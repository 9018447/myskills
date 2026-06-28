"""Compound-name resolution to SMILES via PubChem and CIR."""

from __future__ import annotations

import re
import time
from typing import Any

import requests


PUBCHEM_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/IsomericSMILES,CanonicalSMILES,MolecularFormula/JSON"
CIR_URL = "https://cactus.nci.nih.gov/chemical/structure/{name}/smiles"


def _normalize_name(name: str) -> str:
    """Lowercase and remove common separators."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _heuristic_filter(candidates: list[dict], name: str) -> dict | None:
    """Apply simple heuristics to disambiguate multiple candidates."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    norm_name = _normalize_name(name)

    # Prefer exact synonym match if available (PubChem may not provide synonyms in this endpoint).
    # Fallback: prefer candidates whose molecular formula is simplest (fewest heavy atoms).
    def heaviness(record: dict) -> int:
        formula = record.get("MolecularFormula", "")
        # Very rough atom count from formula; sufficient for tie-breaking.
        nums = re.findall(r"[A-Z][a-z]?(\d*)", formula)
        total = 0
        for n in nums:
            total += int(n) if n else 1
        return total

    sorted_by_size = sorted(candidates, key=heaviness)
    return sorted_by_size[0]


def _resolve_pubchem(name: str) -> list[dict]:
    """Query PubChem PUG-REST and return a list of candidate records."""
    url = PUBCHEM_URL.format(name=name)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    properties = data.get("PropertyTable", {}).get("Properties", [])
    candidates = []
    for prop in properties:
        smiles = prop.get("CanonicalSMILES") or prop.get("IsomericSMILES")
        if smiles:
            candidates.append({
                "smiles": smiles,
                "MolecularFormula": prop.get("MolecularFormula", ""),
                "source": "pubchem",
            })
    return candidates


def _resolve_cir(name: str) -> list[dict]:
    """Query NCI/CADD Chemical Identifier Resolver and return a list of candidates."""
    url = CIR_URL.format(name=name)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return []

    text = response.text.strip()
    if not text:
        return []

    # CIR returns one SMILES per line when multiple exist.
    smiles_list = [line.strip() for line in text.split("\n") if line.strip()]
    return [{"smiles": s, "MolecularFormula": "", "source": "cir"} for s in smiles_list]


def resolve_name(name: str) -> str:
    """Resolve a compound name to a single SMILES string.

    Raises ValueError if the name cannot be resolved unambiguously.
    """
    candidates = _resolve_pubchem(name)
    if not candidates:
        time.sleep(0.2)  # be polite to free APIs
        candidates = _resolve_cir(name)

    if not candidates:
        raise ValueError(f"Could not resolve name to SMILES: {name}")

    chosen = _heuristic_filter(candidates, name)
    if not chosen:
        raise ValueError(f"Could not disambiguate name: {name}")

    return chosen["smiles"]
