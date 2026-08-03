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


def _strip_indications(entry: dict) -> dict:
    """Fresh copy of the entry without its `indications` override map."""
    return {k: v for k, v in entry.items() if k != "indications"}


def _apply_variant(entry: dict, key: str | None) -> tuple[dict, bool]:
    """Merge the named indication variant onto a fresh base copy of `entry`.

    Returns (resolved_entry, applied). `applied` is True only when `key` is set AND
    this entry actually carries that variant — so a caller never labels an entry with
    a variant it does not have. Always a new dict, so the lru_cached pack is untouched.
    """
    base = _strip_indications(entry)
    if not key:
        return base, False
    variant = (entry.get("indications") or {}).get(key)
    if not variant:
        return base, False
    base.update({k: v for k, v in variant.items() if k not in _CONTROL_KEYS})
    return base, True


def _resolve_indication(entry: dict, indication: str | None) -> tuple[dict, str | None]:
    """Resolve `indication` against the entry's own variants → (resolved_entry, matched_key)."""
    key = _match_indication(entry.get("indications") or {}, indication)
    resolved, _ = _apply_variant(entry, key)
    return resolved, key


def lookup(drug: str, indication: str | None = None) -> dict | None:
    """Return {dossier, guideline} for a demo drug, resolved for `indication`, or None.

    The dossier is AUTHORITATIVE: the indication is matched once against the dossier's
    variants, and that same key is applied to the guideline. This prevents a parser-
    differential where the guideline resolves to a variant (e.g. meningitis) the dossier
    does not — which would serve a high-dose guideline against standard PK yet stamp both
    with the same `indication_resolved` label. An entry is labeled only when the variant
    actually applied to it. Returned dicts are fresh, so callers cannot mutate the cache.
    """
    if not demo_enabled() or not drug:
        return None
    key = drug.strip().lower()
    entry = _load_pk().get(key)
    if entry is None:
        return None
    dossier, resolved = _resolve_indication(entry, indication)
    guideline, g_applied = _apply_variant(_load_guidelines().get(key) or {}, resolved)
    if resolved:
        dossier["indication_resolved"] = resolved
        if g_applied:
            guideline["indication_resolved"] = resolved
    return {
        "dossier": dossier,
        "guideline": guideline,
    }
