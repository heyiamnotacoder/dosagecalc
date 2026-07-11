"""Lean skill loader — focused markdown modules for agent/retrieval prompts."""

from __future__ import annotations

from pathlib import Path

_DIR = Path(__file__).resolve().parent

# name -> filename (no .md)
SKILL_NAMES = ("mechanism", "pubmed", "openfda", "webfetch", "edge_cases")


def list_skills() -> list[str]:
    return list(SKILL_NAMES)


def load_skill(name: str) -> dict:
    """Return {"name", "content"} or {"error"}."""
    key = (name or "").strip().lower().replace(".md", "")
    if key not in SKILL_NAMES:
        return {"error": f"unknown skill '{name}'. known: {list(SKILL_NAMES)}"}
    path = _DIR / f"{key}.md"
    if not path.is_file():
        return {"error": f"skill file missing: {path.name}"}
    return {"name": key, "content": path.read_text(encoding="utf-8").strip()}
