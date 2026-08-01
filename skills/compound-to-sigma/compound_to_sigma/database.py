"""ADFCRS-2018 database lookup for existing coskf files."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any

from .utils import Logger


def _normalize_filename(name: str) -> str:
    """Normalize a name for fuzzy filename matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _read_coskf_smiles(coskf_path: Path, logger: Logger) -> str | None:
    """Try to read SMILES metadata from a coskf file using scm.plams.KFFile."""
    try:
        from scm.plams import KFFile
    except ImportError:
        logger.debug("scm.plams not available; cannot read coskf SMILES metadata")
        return None

    try:
        kf = KFFile(str(coskf_path))
        # Common sections/keys for molecule metadata in ADF coskf files.
        for section in ["General", "Molecule", "Compound"]:
            for key in ["SMILES", "smiles", "Smiles"]:
                value = kf.read(section, key)
                if value:
                    return str(value)
    except Exception as e:
        logger.debug(f"Could not read SMILES from {coskf_path}: {e}")
    return None


def _list_coskf_files(database_path: Path) -> list[Path]:
    """Return all .coskf files under the database directory."""
    if not database_path.is_dir():
        return []
    return sorted(database_path.rglob("*.coskf"))


def find_database_match(
    smiles: str | None,
    name: str | None,
    database_path: str | Path | None,
    logger: Logger,
) -> Path | None:
    """Search the ADFCRS-2018 database for a matching coskf file.

    Returns the path to the matching coskf, or None if no match is found.
    """
    if not database_path:
        logger.debug("No database_path configured; skipping database lookup")
        return None

    db_path = Path(database_path)
    if not db_path.is_dir():
        logger.debug(f"Database path does not exist: {db_path}")
        return None

    logger.debug(f"Searching database: {db_path}")
    coskf_files = _list_coskf_files(db_path)
    if not coskf_files:
        logger.debug("No .coskf files found in database")
        return None

    # Strategy 1: normalized filename match (fast, no file reading).
    if name:
        norm_name = _normalize_filename(name)
        for coskf in coskf_files:
            norm_file = _normalize_filename(coskf.stem)
            if norm_file == norm_name:
                logger.debug(f"Filename match: {coskf}")
                return coskf
            # Also allow the name to appear at the start of the filename.
            if norm_file.startswith(norm_name) or norm_name.startswith(norm_file):
                logger.debug(f"Partial filename match: {coskf}")
                return coskf

    # Strategy 2: SMILES metadata match (slower, reads each coskf).
    if smiles:
        norm_smiles = smiles.strip()
        for coskf in coskf_files:
            coskf_smiles = _read_coskf_smiles(coskf, logger)
            if coskf_smiles and coskf_smiles.strip() == norm_smiles:
                logger.debug(f"SMILES match: {coskf}")
                return coskf

    logger.debug("No database match found")
    return None


def copy_database_coskf(
    source: Path,
    output_dir: Path,
    compound_name: str,
    logger: Logger,
) -> Path:
    """Copy a database coskf into the compound output directory."""
    dest = output_dir / f"{compound_name}.coskf"
    shutil.copy2(source, dest)
    logger.info(f"Copied database coskf to {dest}")
    return dest
