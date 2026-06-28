"""Core pipeline runner: from compound input to sigma profile."""

from __future__ import annotations

import os
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from .config import validate_compound
from .database import copy_database_coskf, find_database_match
from .resolver import resolve_name
from .utils import Logger, ensure_dir, expand_env_vars, run_command, which


def _check_environment(logger: Logger) -> None:
    """Verify that required external tools are available."""
    missing = []
    for tool in ["amspython", "xtb", "obabel"]:
        if not which(tool):
            missing.append(tool)
    if missing:
        raise RuntimeError(
            f"Missing required tools: {missing}. "
            "Please source $AMSHOME/amsbashrc.sh and ensure xtb and obabel are in PATH."
        )
    logger.debug("Environment check passed")


def _smiles_to_xyz(smiles: str, output_xyz: Path, logger: Logger) -> None:
    """Convert a SMILES string to a 3D xyz file using Open Babel."""
    cmd = ["obabel", f"-:{smiles}", "--gen3d", "-O", str(output_xyz)]
    run_command(cmd, verbose=logger.verbose)
    if not output_xyz.exists():
        raise RuntimeError(f"obabel failed to produce {output_xyz}")


def _run_xtb(
    input_xyz: Path,
    charge: int,
    multiplicity: int,
    output_dir: Path,
    logger: Logger,
) -> Path:
    """Run gas-phase GFN2-xTB optimization."""
    output_xyz = output_dir / f"{input_xyz.stem}_xtbopt.xyz"
    uhf = multiplicity - 1
    cmd = [
        "xtb",
        str(input_xyz.resolve()),
        "--opt",
        "--gfn",
        "2",
        "--chrg",
        str(charge),
        "--uhf",
        str(uhf),
    ]
    run_command(cmd, cwd=output_dir, verbose=logger.verbose)

    # xtb writes the optimized geometry to xtbopt.xyz by default.
    candidate = output_dir / "xtbopt.xyz"
    if not candidate.exists():
        raise RuntimeError("xtb optimization did not produce xtbopt.xyz")
    shutil.move(candidate, output_xyz)
    return output_xyz


def _run_adf_cosmo(
    input_xyz: Path,
    output_dir: Path,
    compound_name: str,
    logger: Logger,
) -> Path:
    """Run ADF COSMO single point using the ADFCOSMORSCompound recipe.

    Uses the official SCM recipe settings (BP86/TZP + COSMO) and returns
    the generated coskf path.
    """
    from scm.plams import Molecule, config, init, finish
    from scm.plams.recipes.adfcosmorscompound import ADFCOSMORSCompoundJob

    init()
    config.log.stdout = 0 if logger.verbose < 2 else 1

    mol = Molecule(str(input_xyz.resolve()))
    job = ADFCOSMORSCompoundJob(
        molecule=mol,
        name=compound_name,
        singlepoint=False,  # perform geometry optimization + COSMO single point
    )
    out = job.run()

    if not job.ok():
        finish()
        raise RuntimeError(f"ADF COSMO job failed for {compound_name}")

    coskf_path = output_dir / f"{compound_name}.coskf"
    source_coskf = Path(job.results.coskfpath())
    if not source_coskf.exists():
        finish()
        raise RuntimeError(f"ADF COSMO coskf not found at {source_coskf}")

    shutil.copy2(source_coskf, coskf_path)
    finish()
    return coskf_path


def _extract_sigma_profile(
    coskf_path: Path,
    method: str,
    logger: Logger,
) -> pd.DataFrame:
    """Run CRSJob SIGMAPROFILE and return a DataFrame."""
    from scm.plams import CRSJob, Settings, config, init, finish

    init()
    config.log.stdout = 0 if logger.verbose < 2 else 1

    settings = Settings()
    settings.input.property._h = "SIGMAPROFILE"
    settings.input.method = method

    compound = Settings()
    compound._h = str(coskf_path.resolve())
    compound.frac1 = 1
    settings.input.compound = [compound]

    job = CRSJob(settings=settings, name=f"{coskf_path.stem}_sigma")
    out = job.run()

    if not job.ok():
        finish()
        raise RuntimeError(f"CRSJob SIGMAPROFILE failed for {coskf_path}")

    res = out.get_results()
    finish()

    import numpy as np

    chdval = np.asarray(res.get("chdval")).flatten()
    profil = np.asarray(res.get("profil")).flatten()
    hbprofil_raw = res.get("hbprofil")
    hbprofil = np.asarray(hbprofil_raw).flatten() if hbprofil_raw is not None else None

    if chdval is None or profil is None:
        raise RuntimeError("CRSJob result missing chdval or profil")

    data: dict[str, Any] = {"sigma": chdval, "total_profile": profil}
    if hbprofil is not None:
        prof_len = len(profil)
        hb_len = len(hbprofil)
        if hb_len == prof_len:
            data["hb_profile"] = hbprofil
        elif hb_len == 3 * prof_len:
            # COSMO-SAC2013: split into HB, HB-OH, HB-OT
            data["hb_profile"] = hbprofil[:prof_len]
            data["hb_oh_profile"] = hbprofil[prof_len:2 * prof_len]
            data["hb_ot_profile"] = hbprofil[2 * prof_len:]
        else:
            # Fallback: store as a single column even if lengths differ
            data["hb_profile"] = hbprofil

    return pd.DataFrame(data)


def _run_single_compound(
    compound: dict,
    output_dir: Path,
    database_path: str | Path | None,
    method: str,
    verbose: int,
) -> dict:
    """Run the full pipeline for one compound and return a result dict."""
    logger = Logger(verbose)
    # Determine input type and base name.
    if "name" in compound and compound["name"]:
        base_name = compound["name"]
        input_type = "name"
    elif "smiles" in compound and compound["smiles"]:
        base_name = compound["smiles"].replace("/", "_").replace("\\", "_")
        input_type = "smiles"
    elif "xyz_path" in compound and compound["xyz_path"]:
        base_name = Path(compound["xyz_path"]).stem
        input_type = "xyz_path"
    elif "coskf_path" in compound and compound["coskf_path"]:
        base_name = Path(compound["coskf_path"]).stem
        input_type = "coskf_path"
    else:
        raise ValueError("No valid input field found in compound")

    compound_dir = ensure_dir(output_dir / base_name)
    coskf_path = compound_dir / f"{base_name}.coskf"
    csv_path = compound_dir / f"{base_name}_sigma_profile.csv"

    # Resume: if local coskf exists, skip to extraction.
    if coskf_path.exists():
        logger.info(f"{base_name}: found existing local coskf; extracting sigma profile")
        df = _extract_sigma_profile(coskf_path, method, logger)
        df.to_csv(csv_path, index=False)
        return {
            "name": base_name,
            "smiles": compound.get("smiles"),
            "coskf_path": str(coskf_path),
            "csv_path": str(csv_path),
            "source": "existing_local",
            "sigma_profile": df,
        }

    # Handle user-provided coskf directly: skip DB lookup and DFT.
    if input_type == "coskf_path":
        source_coskf = Path(expand_env_vars(compound["coskf_path"]))
        shutil.copy2(source_coskf, coskf_path)
        logger.info(f"{base_name}: extracting sigma profile from provided coskf")
        df = _extract_sigma_profile(coskf_path, method, logger)
        df.to_csv(csv_path, index=False)
        return {
            "name": base_name,
            "smiles": None,
            "coskf_path": str(coskf_path),
            "csv_path": str(csv_path),
            "source": "user_provided",
            "sigma_profile": df,
        }

    # Resolve name to SMILES if needed.
    smiles = compound.get("smiles")
    if input_type == "name":
        logger.info(f"{base_name}: resolving name to SMILES")
        smiles = resolve_name(compound["name"])
        logger.info(f"{base_name}: resolved to {smiles}")

    # Try database lookup if we have a SMILES or name.
    db_match = find_database_match(
        smiles=smiles,
        name=compound.get("name") or base_name,
        database_path=database_path,
        logger=logger,
    )
    if db_match:
        coskf_path = copy_database_coskf(db_match, compound_dir, base_name, logger)
        df = _extract_sigma_profile(coskf_path, method, logger)
        df.to_csv(csv_path, index=False)
        return {
            "name": base_name,
            "smiles": smiles,
            "coskf_path": str(coskf_path),
            "csv_path": str(csv_path),
            "source": "database",
            "sigma_profile": df,
        }

    # Generate xyz if needed.
    if input_type == "xyz_path":
        xyz_path = Path(expand_env_vars(compound["xyz_path"]))
        input_xyz = compound_dir / f"{base_name}.xyz"
        shutil.copy2(xyz_path, input_xyz)
    elif input_type in ("name", "smiles"):
        input_xyz = compound_dir / f"{base_name}.xyz"
        logger.info(f"{base_name}: generating 3D xyz from SMILES")
        _smiles_to_xyz(smiles, input_xyz, logger)
    else:
        # input_type == "coskf_path"
        input_xyz = None

    # Run xtb + ADF, or directly extract if coskf_path input.
    if input_type == "coskf_path":
        source_coskf = Path(expand_env_vars(compound["coskf_path"]))
        shutil.copy2(source_coskf, coskf_path)
    else:
        logger.info(f"{base_name}: running xtb optimization")
        opt_xyz = _run_xtb(
            input_xyz,
            charge=compound["charge"],
            multiplicity=compound["multiplicity"],
            output_dir=compound_dir,
            logger=logger,
        )
        logger.info(f"{base_name}: running ADF COSMO")
        coskf_path = _run_adf_cosmo(opt_xyz, compound_dir, base_name, logger)

    logger.info(f"{base_name}: extracting sigma profile")
    df = _extract_sigma_profile(coskf_path, method, logger)
    df.to_csv(csv_path, index=False)

    return {
        "name": base_name,
        "smiles": smiles,
        "coskf_path": str(coskf_path),
        "csv_path": str(csv_path),
        "source": "calculated",
        "sigma_profile": df,
    }


def from_name(
    name: str,
    charge: int,
    multiplicity: int,
    output_dir: str | Path = "./compound-to-sigma-outputs",
    database_path: str | Path | None = None,
    method: str = "COSMO-RS",
    verbose: int = 1,
) -> dict:
    """Compute sigma profile for a single compound by name."""
    _check_environment(Logger(verbose))
    compound = {
        "name": name,
        "charge": charge,
        "multiplicity": multiplicity,
    }
    validate_compound(compound, 0)
    logger = Logger(verbose)
    if database_path is None:
        database_path = os.environ.get("SCM_PKG_ADFCRSDIR", "")
        if database_path and not database_path.endswith("ADFCRS-2018"):
            candidate = os.path.join(database_path, "ADFCRS-2018")
            if os.path.isdir(candidate):
                database_path = candidate
    return _run_single_compound(
        compound,
        Path(output_dir),
        database_path,
        method,
        verbose,
    )


def from_coskf(
    coskf_path: str | Path,
    output_dir: str | Path = "./compound-to-sigma-outputs",
    method: str = "COSMO-RS",
    verbose: int = 1,
) -> dict:
    """Extract sigma profile from an existing coskf file."""
    logger = Logger(verbose)
    compound = {
        "coskf_path": str(coskf_path),
        "charge": 0,
        "multiplicity": 1,
    }
    validate_compound(compound, 0)
    return _run_single_compound(
        compound,
        Path(output_dir),
        None,
        method,
        verbose,
    )


def _compound_display_name(compound: dict) -> str:
    """Return a human-readable name for a compound dict."""
    return (
        compound.get("name")
        or compound.get("smiles")
        or Path(compound.get("xyz_path", "")).stem
        or Path(compound.get("coskf_path", "")).stem
        or "unknown"
    )


def _validation_failure(compound: dict, error: Exception) -> dict:
    """Build a failure record for a compound that failed validation."""
    return {
        "name": _compound_display_name(compound),
        "input": compound,
        "error": str(error),
    }


def from_names(
    compounds: list[dict],
    output_dir: str | Path = "./compound-to-sigma-outputs",
    database_path: str | Path | None = None,
    n_jobs: int = 1,
    method: str = "COSMO-RS",
    verbose: int = 1,
) -> dict:
    """Compute sigma profiles for a list of compounds.

    Returns {"successes": [...], "failures": [...]}.
    """
    logger = Logger(verbose)
    _check_environment(logger)

    output_path = Path(output_dir)
    ensure_dir(output_path)

    # Set up file logging.
    log_path = output_path / "log.txt"
    logger.info(f"Logging to {log_path}")

    if database_path is None:
        database_path = os.environ.get("SCM_PKG_ADFCRSDIR", "")
        if database_path and not database_path.endswith("ADFCRS-2018"):
            candidate = os.path.join(database_path, "ADFCRS-2018")
            if os.path.isdir(candidate):
                database_path = candidate

    successes: list[dict] = []
    failures: list[dict] = []

    # Validate all compounds up front so failures are captured clearly.
    validated = []
    for i, compound in enumerate(compounds):
        try:
            validate_compound(compound, i)
            validated.append(compound)
        except Exception as e:
            failures.append(_validation_failure(compound, e))
            logger.error(f"{_compound_display_name(compound)}: {e}")

    if n_jobs == 1:
        iterator = tqdm(validated, disable=verbose == 0)
        for compound in iterator:
            name = _compound_display_name(compound)
            iterator.set_description(f"Processing {name}")
            try:
                result = _run_single_compound(
                    compound,
                    output_path,
                    database_path,
                    method,
                    verbose,
                )
                successes.append(result)
            except Exception as e:
                failures.append({
                    "name": name,
                    "input": compound,
                    "error": str(e),
                })
                logger.error(f"{name}: {e}")
    else:
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            futures = {}
            for compound in validated:
                future = executor.submit(
                    _run_single_compound,
                    compound,
                    output_path,
                    database_path,
                    method,
                    verbose,
                )
                futures[future] = compound

            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                disable=verbose == 0,
            ):
                compound = futures[future]
                name = _compound_display_name(compound)
                try:
                    result = future.result()
                    successes.append(result)
                except Exception as e:
                    failures.append({
                        "name": name,
                        "input": compound,
                        "error": str(e),
                    })
                    logger.error(f"{name}: {e}")

    return {"successes": successes, "failures": failures}
