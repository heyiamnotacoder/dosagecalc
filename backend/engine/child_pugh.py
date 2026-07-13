"""
Child-Pugh class from lab/clinical components (deterministic).

Used only as a *note* for hepatic impairment — never invents a clearance
modifier (hepatic OF stays drug-specific). Standard adult cirrhosis scoring;
pediatric use is uncommon and should be flagged as such by the agent.
"""

from __future__ import annotations

from typing import Any, Optional


def _bilirubin_points(bilirubin_mg_dl: float) -> int:
    if bilirubin_mg_dl < 2.0:
        return 1
    if bilirubin_mg_dl <= 3.0:
        return 2
    return 3


def _albumin_points(albumin_g_dl: float) -> int:
    if albumin_g_dl > 3.5:
        return 1
    if albumin_g_dl >= 2.8:
        return 2
    return 3


def _inr_points(inr: float) -> int:
    if inr < 1.7:
        return 1
    if inr <= 2.3:
        return 2
    return 3


def _ascites_points(ascites: str) -> int:
    a = (ascites or "none").strip().lower()
    if a in ("none", "absent", "no", ""):
        return 1
    if a in ("mild", "slight", "1", "grade1"):
        return 2
    if a in ("moderate", "severe", "marked", "2", "3", "mod"):
        return 3
    raise ValueError(f"Unknown ascites value: {ascites!r} (use none|mild|moderate)")


def _encephalopathy_points(encephalopathy: str) -> int:
    e = (encephalopathy or "none").strip().lower().replace(" ", "")
    if e in ("none", "absent", "no", "0", ""):
        return 1
    if e in ("1-2", "1to2", "grade1-2", "grade1", "grade2", "1", "2", "mild"):
        return 2
    if e in ("3-4", "3to4", "grade3-4", "grade3", "grade4", "3", "4", "severe"):
        return 3
    raise ValueError(
        f"Unknown encephalopathy value: {encephalopathy!r} (use none|1-2|3-4)"
    )


def class_from_score(score: int) -> str:
    """Map total Child-Pugh points to class A/B/C."""
    if score < 5 or score > 15:
        raise ValueError(f"Child-Pugh score {score} out of range 5–15")
    if score <= 6:
        return "A"
    if score <= 9:
        return "B"
    return "C"


def compute_child_pugh(
    bilirubin_mg_dl: float,
    albumin_g_dl: float,
    inr: float,
    ascites: str = "none",
    encephalopathy: str = "none",
) -> dict[str, Any]:
    """
    Compute Child-Pugh score and class from components.

    Returns dict: score, class (A|B|C), component_points.
    Raises ValueError on missing/invalid inputs.
    """
    try:
        bili = float(bilirubin_mg_dl)
        alb = float(albumin_g_dl)
        inr_f = float(inr)
    except (TypeError, ValueError) as e:
        raise ValueError("bilirubin_mg_dl, albumin_g_dl, and inr must be numbers") from e
    if bili < 0 or alb < 0 or inr_f <= 0:
        raise ValueError("bilirubin/albumin must be ≥0 and INR must be >0")

    pts = {
        "bilirubin": _bilirubin_points(bili),
        "albumin": _albumin_points(alb),
        "inr": _inr_points(inr_f),
        "ascites": _ascites_points(ascites),
        "encephalopathy": _encephalopathy_points(encephalopathy),
    }
    score = sum(pts.values())
    return {
        "score": score,
        "class": class_from_score(score),
        "component_points": pts,
    }


def resolve_child_pugh(case: dict) -> dict[str, Any]:
    """
    From a case dict, resolve Child-Pugh class.

    Priority:
      1. If all calc labs present → compute (source=calculated), may override blank class
      2. Else if child_pugh A/B/C entered → source=entered
      3. Else no class

    Mutates a *copy* is caller's job; this returns patch fields only.
    """
    out: dict[str, Any] = {}
    bili = case.get("bilirubin_mg_dl")
    alb = case.get("albumin_g_dl")
    inr = case.get("inr")
    has_labs = all(v is not None and v != "" for v in (bili, alb, inr))

    if has_labs:
        try:
            r = compute_child_pugh(
                bili,
                alb,
                inr,
                ascites=case.get("ascites") or "none",
                encephalopathy=case.get("encephalopathy") or "none",
            )
            out["child_pugh"] = r["class"]
            out["child_pugh_score"] = r["score"]
            out["child_pugh_source"] = "calculated"
            out["child_pugh_components"] = r["component_points"]
            return out
        except (TypeError, ValueError):
            pass  # fall through to entered class

    cp = case.get("child_pugh")
    if cp:
        cp_u = str(cp).strip().upper()
        if cp_u in ("A", "B", "C"):
            out["child_pugh"] = cp_u
            out["child_pugh_source"] = "entered"
    return out


def allergy_tokens_overlap(allergies: Optional[list], drug: str) -> list[str]:
    """
    Lightweight token overlap between allergy strings and drug name.
    Not a clinical decision — surfaces candidates for the agent hard-stop path.
    """
    if not allergies or not drug:
        return []
    drug_l = drug.strip().lower()
    hits: list[str] = []
    for a in allergies:
        if not a:
            continue
        t = str(a).strip().lower()
        if not t:
            continue
        if t in drug_l or drug_l in t:
            hits.append(str(a).strip())
    return hits
