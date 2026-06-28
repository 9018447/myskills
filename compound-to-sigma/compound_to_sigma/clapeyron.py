"""Bridge from compound-to-sigma outputs to Clapeyron.jl COSMO-SAC profiles.

The CRSJob SIGMAPROFILE property returns a total sigma profile and a
hydrogen-bond profile.  When the method is a COSMO-SAC variant, the
hydrogen-bond profile is split into total HB, OH, and OT contributions.
This module converts those raw outputs into the ``A/V/Pnhb/POH/POT``
format that :mod:`thermosteam.equilibrium.fast_sigma` (and therefore the
Clapeyron.jl backend) expects.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .utils import Logger

BOHR_TO_ANGSTROM = 0.529177249
NUM_SIGMA_POINTS = 51


def _read_cosmo_area_volume(coskf_path: Path) -> tuple[float, float]:
    """Read COSMO cavity area and volume from a ``.coskf`` file.

    ADF stores ``Area`` in bohr² and ``Volume`` in bohr³ in the
    ``COSMO`` section.  This function converts them to Å² and Å³.
    """
    from scm.plams import KFFile

    kf = KFFile(str(coskf_path))
    area_au = float(kf.read("COSMO", "Area"))
    volume_au = float(kf.read("COSMO", "Volume"))
    bohr = BOHR_TO_ANGSTROM
    area = area_au * bohr * bohr
    volume = volume_au * bohr * bohr * bohr
    return area, volume


def extract_clapeyron_profile(
    coskf_path: str | Path,
    method: str = "COSMOSAC2013",
    verbose: int = 0,
) -> dict[str, Any]:
    """Convert a ``.coskf`` file into a Clapeyron-compatible COSMO-SAC profile.

    Parameters
    ----------
    coskf_path : str | Path
        Path to the ADF ``.coskf`` file.
    method : str, optional
        CRSJob method for sigma-profile extraction.  Must be a COSMO-SAC
        variant that returns split HB profiles (``COSMOSAC2013`` or
        ``COSMOSAC2016``).  Default is ``COSMOSAC2013``.
    verbose : int, optional
        Verbosity level.  ``0`` is silent, ``1`` prints progress,
        ``2`` streams PLAMS stdout.

    Returns
    -------
    dict
        Dictionary with keys:

        * ``A`` — COSMO cavity surface area [Å²]
        * ``V`` — COSMO cavity volume [Å³]
        * ``sigma`` — charge-density grid values [e/Å²]
        * ``Pnhb`` — non-hydrogen-bonding profile (51 points)
        * ``POH`` — OH hydrogen-bonding profile (51 points)
        * ``POT`` — OT hydrogen-bonding profile (51 points)
        * ``method`` — CRSJob method used
        * ``coskf_path`` — absolute path to the source ``.coskf``
    """
    from scm.plams import CRSJob, Settings, config, init, finish

    coskf_path = Path(coskf_path).resolve()
    if not coskf_path.exists():
        raise FileNotFoundError(f"coskf file not found: {coskf_path}")

    logger = Logger(verbose=verbose)
    logger.info(f"Extracting Clapeyron profile from {coskf_path}")

    area, volume = _read_cosmo_area_volume(coskf_path)
    logger.info(f"  COSMO area = {area:.3f} Å², volume = {volume:.3f} Å³")

    init()
    config.log.stdout = 0 if verbose < 2 else 1

    settings = Settings()
    settings.input.property._h = "SIGMAPROFILE"
    settings.input.method = method

    compound = Settings()
    compound._h = str(coskf_path)
    compound.frac1 = 1
    settings.input.compound = [compound]

    job = CRSJob(settings=settings, name=f"{coskf_path.stem}_clapeyron")
    out = job.run()

    if not job.ok():
        finish()
        raise RuntimeError(f"CRSJob SIGMAPROFILE failed for {coskf_path}")

    res = out.get_results()
    finish()

    chdval = np.asarray(res["chdval"]).flatten()
    profil = np.asarray(res["profil"]).flatten()
    hbprofil = np.asarray(res["hbprofil"]).flatten()

    if len(chdval) != NUM_SIGMA_POINTS or len(profil) != NUM_SIGMA_POINTS:
        raise ValueError(
            f"Expected {NUM_SIGMA_POINTS} sigma points, "
            f"got chdval={len(chdval)}, profil={len(profil)}"
        )
    if len(hbprofil) != 3 * NUM_SIGMA_POINTS:
        raise ValueError(
            f"Expected hbprofil length {3 * NUM_SIGMA_POINTS} for {method}, "
            f"got {len(hbprofil)}.  Use a COSMO-SAC variant."
        )

    hb_total = hbprofil[:NUM_SIGMA_POINTS]
    hb_oh = hbprofil[NUM_SIGMA_POINTS : 2 * NUM_SIGMA_POINTS]
    hb_ot = hbprofil[2 * NUM_SIGMA_POINTS :]

    # Pnhb is the total profile minus the total HB contribution.
    # Small negative values from numerical noise are clamped to zero.
    pnhb = profil - hb_total
    pnhb = np.maximum(pnhb, 0.0)

    return {
        "A": float(area),
        "V": float(volume),
        "sigma": chdval.tolist(),
        "Pnhb": pnhb.tolist(),
        "POH": hb_oh.tolist(),
        "POT": hb_ot.tolist(),
        "method": method,
        "coskf_path": str(coskf_path),
    }


def register_in_thermosteam(
    name: str,
    profile: dict[str, Any],
) -> None:
    """Register a Clapeyron profile in the thermosteam fast_sigma user database.

    Parameters
    ----------
    name : str
        Lookup name for the profile.  Must match the chemical's
        ``common_name`` or ``ID`` (case-insensitive).
    profile : dict
        Output of :func:`extract_clapeyron_profile`.
    """
    from thermosteam.equilibrium.fast_sigma import add_cosmo_profile

    add_cosmo_profile(
        name,
        A=profile["A"],
        V=profile["V"],
        Pnhb=profile["Pnhb"],
        POH=profile["POH"],
        POT=profile["POT"],
    )
