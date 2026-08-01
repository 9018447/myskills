"""Configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from .utils import expand_env_vars


INPUT_FIELDS = {"name", "smiles", "xyz_path", "coskf_path"}
REQUIRED_FIELDS = {"charge", "multiplicity"}


def load_yaml(path: str | Path) -> dict:
    """Load a YAML configuration file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_compound(compound: dict, index: int) -> dict:
    """Validate a single compound entry and normalize it."""
    provided = {k for k in compound if k in INPUT_FIELDS and compound[k]}
    if len(provided) != 1:
        raise ValueError(
            f"Compound {index}: exactly one of {INPUT_FIELDS} must be provided, got {provided}"
        )

    missing = REQUIRED_FIELDS - set(compound.keys())
    if missing:
        raise ValueError(
            f"Compound {index}: missing required fields {missing}"
        )

    return compound


def validate_config(raw: dict) -> dict:
    """Validate and normalize the full configuration."""
    config = {
        "output_dir": expand_env_vars(raw.get("output_dir", "./compound-to-sigma-outputs")),
        "database_path": expand_env_vars(raw.get("database_path", os.environ.get("SCM_PKG_ADFCRSDIR", ""))),
        "n_jobs": int(raw.get("n_jobs", 1)),
        "method": raw.get("method", "COSMO-RS"),
        "verbose": int(raw.get("verbose", 1)),
    }

    # If database_path is just the root env var, append ADFCRS-2018
    if config["database_path"] and not config["database_path"].endswith("ADFCRS-2018"):
        candidate = os.path.join(config["database_path"], "ADFCRS-2018")
        if os.path.isdir(candidate):
            config["database_path"] = candidate

    compounds = raw.get("compounds", [])
    if not compounds:
        raise ValueError("Config must contain at least one compound")

    config["compounds"] = [validate_compound(c, i) for i, c in enumerate(compounds)]
    return config


def load_config(path: str | Path) -> dict:
    """Load and validate a YAML config file."""
    raw = load_yaml(path)
    return validate_config(raw)
