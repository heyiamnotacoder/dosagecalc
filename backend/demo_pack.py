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
    # Env is re-read every call so PAEDSCALE_DEMO=0 toggles at runtime; only the
    # filesystem stat is memoised (see _pack_present) — it was on the per-query hot path.
    flag = os.environ.get("PAEDSCALE_DEMO", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return _pack_present()


def _demo_dir() -> Path:
    override = os.environ.get("PAEDSCALE_DEMO_DIR")
    return Path(override) if override else _DEFAULT_DEMO_DIR


@lru_cache(maxsize=1)
def _pack_present() -> bool:
    d = _demo_dir()
    return d.is_dir() and (d / "pk.json").is_file()


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


# Keys inside an indication variant that are control metadata, not dossier fields.
_CONTROL_KEYS = {"match"}


def _match_indication(variants: dict, indication: str | None) -> str | None:
    """Return the key of the indication variant best matching `indication`, or None.

    Matching is deterministic and case-insensitive: a variant matches if its key or
    any string in its optional `match` list is a substring of the caller's indication
    (or vice-versa). First variant declared wins on ties.
    """
    if not indication or not variants:
        return None
    q = indication.strip().lower()
    if not q:
        return None
    for key, variant in variants.items():
        needles = [key.lower()] + [str(m).lower() for m in (variant.get("match") or [])]
        if any(n and (n in q or q in n) for n in needles):
            return key
    return None


def _resolve_indication(entry: dict, indication: str | None) -> tuple[dict, str | None]:
    """Merge the matching indication override onto a fresh copy of the base entry.

    Returns (resolved_entry_without_the_`indications`_map, matched_variant_key_or_None).
    Falling back to the base preserves today's behaviour when no indication is given
    or nothing matches. Always returns a new dict so the lru_cached pack is never mutated.
    """
    base = {k: v for k, v in entry.items() if k != "indications"}
    variants = entry.get("indications") or {}
    key = _match_indication(variants, indication)
    if key is None:
        return base, None
    override = {k: v for k, v in variants[key].items() if k not in _CONTROL_KEYS}
    base.update(override)
    return base, key


def lookup(drug: str, indication: str | None = None) -> dict | None:
    """Return {dossier, guideline} for a demo drug, resolved for `indication`, or None.

    Indication-sensitive drugs carry an `indications` override map; the caller's
    indication selects the variant (falling back to the base entry). The returned
    dossier/guideline are fresh dicts, so callers cannot mutate the cached pack.
    """
    if not demo_enabled() or not drug:
        return None
    key = drug.strip().lower()
    entry = _load_pk().get(key)
    if entry is None:
        return None
    dossier, resolved = _resolve_indication(entry, indication)
    guideline, g_resolved = _resolve_indication(_load_guidelines().get(key) or {}, indication)
    label = resolved or g_resolved
    if label:
        dossier["indication_resolved"] = label
        if guideline:
            guideline["indication_resolved"] = label
    return {
        "dossier": dossier,
        "guideline": guideline,
    }
