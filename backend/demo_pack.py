"""
Demo-branch curated PK + guidelines loader.

DEMO BRANCH ONLY — never merge to master as a product assumption.
When a drug is present under ../demo/pk.json, the retrieval layer serves it
with source_mode="demo" and skips live PubMed/openFDA.

Env:
  PAEDSCALE_DEMO=0|false|off  — disable the pack even if files exist
  PAEDSCALE_DEMO_DIR          — override path to the demo/ directory
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_DEMO_DIR = _HERE.parent / "demo"


def demo_enabled() -> bool:
    flag = os.environ.get("PAEDSCALE_DEMO", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return _demo_dir().is_dir() and (_demo_dir() / "pk.json").is_file()


def _demo_dir() -> Path:
    override = os.environ.get("PAEDSCALE_DEMO_DIR")
    return Path(override) if override else _DEFAULT_DEMO_DIR


@lru_cache(maxsize=1)
def _load_pk() -> dict:
    path = _demo_dir() / "pk.json"
    if not path.is_file():
        return {}
    with path.open() as f:
        data = json.load(f)
    return {k.lower(): v for k, v in (data.get("drugs") or {}).items()}


@lru_cache(maxsize=1)
def _load_guidelines() -> dict:
    path = _demo_dir() / "guidelines.json"
    if not path.is_file():
        return {}
    with path.open() as f:
        data = json.load(f)
    return {k.lower(): v for k, v in (data.get("drugs") or {}).items()}


def list_demo_drugs() -> list[str]:
    if not demo_enabled():
        return []
    return sorted(_load_pk().keys())


def lookup(drug: str) -> dict | None:
    """Return {dossier, guideline} for a demo drug, or None if not in the pack."""
    if not demo_enabled() or not drug:
        return None
    key = drug.strip().lower()
    dossier = _load_pk().get(key)
    if dossier is None:
        return None
    # Shallow copy so callers cannot mutate the cached pack
    return {
        "dossier": dict(dossier),
        "guideline": dict(_load_guidelines().get(key) or {}),
    }
