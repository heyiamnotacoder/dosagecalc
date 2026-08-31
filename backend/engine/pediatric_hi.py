"""Pediatric HI facade: bake a cited HI adjustment into the adult dose, then allometry.

Issue #5. Uses the single HI resolver in hi_table.py. Never invents
hepatic_function_fraction — that stays 1.0; HI is already in the adult number.
"""

from __future__ import annotations

from typing import Any, Optional

from engine.child_pugh import resolve_calculator_mode, resolve_child_pugh
from engine.hi_table import (
    apply_hi_resolution,
    oral_high_extraction_abstain,
    pick_facade_table,
)

HEPATIC_FM_THRESHOLD = 0.3

_GRADE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}

LOW_FM_FLAG = (
    f"Hepatic fm share < {HEPATIC_FM_THRESHOLD}; pediatric HI facade not applied "
    "(adult reference dose was not rewritten from an HI table)."
)
STACKED_MODIFIERS_FLAG = (
    "STACKED modifiers: renal organ-function (Schwartz) applied after the "
    "hepatic-impairment adult-dose rewrite; treat as extra uncertainty (grade ceiling C)."
)
ADULT_LABEL_CAP_FLAG = (
    "Cited adult HI label × allometry is not pediatric-HI concordance (grade ceiling B)."
)
GUIDELINE_CONFLICT_FLAG = (
    "Pediatric HI dosing guideline disagrees with the adult label; "
    "pediatric guideline used on this facade."
)
NO_CITED_ROW = (
    "SAFETY STOP — no cited applicable hepatic-impairment adjustment; "
    "abstain (pediatric HI facade)."
)


def hepatic_fm_share(fm: Optional[dict]) -> float:
    """Hepatic share of clearance: non-renal pathway fractions."""
    if not fm:
        return 0.0
    total = 0.0
    for key, val in fm.items():
        if str(key).startswith("renal"):
            continue
        try:
            total += float(val)
        except (TypeError, ValueError):
            continue
    return total


def pediatric_hi_should_run(case: dict, fm: Optional[dict] = None) -> bool:
    """Pediatric path + hepatic on + hepatic fm ≥ 0.3."""
    try:
        if resolve_calculator_mode(case) != "pediatric":
            return False
    except ValueError:
        return False
    if not case.get("hepatic_impairment"):
        return False
    return hepatic_fm_share(fm if fm is not None else case.get("fm")) >= HEPATIC_FM_THRESHOLD


def _renal_stacked(case: dict) -> bool:
    if case.get("renal_impairment"):
        return True
    try:
        frac = case.get("renal_function_fraction")
        if frac is not None and float(frac) < 0.999:
            return True
    except (TypeError, ValueError):
        pass
    return False


def pick_pediatric_facade_table(
    case: dict,
    adult_table: Optional[dict],
    pediatric_table: Optional[dict],
) -> tuple[Optional[dict], str, list[str]]:
    """Pediatric guideline wins when it has an applicable row; flag adult conflict."""
    table, source, conflict = pick_facade_table(
        case, adult_table, pediatric_table, prefer="pediatric_guideline"
    )
    flags = [GUIDELINE_CONFLICT_FLAG] if conflict else []
    return table, source, flags


def _hepatic_note(case: dict, source: str, res: dict) -> str:
    cp = resolve_child_pugh(case).get("child_pugh") or case.get("child_pugh") or "?"
    kind = res.get("kind") or "cited"
    dose = res.get("adult_dose_mg_per_day")
    dose_txt = f"{dose:g} mg/day" if isinstance(dose, (int, float)) else "cited adult HI dose"
    src_txt = (
        "pediatric HI dosing guideline" if source == "pediatric_guideline" else "adult HI label"
    )
    return (
        f"HEPATIC impairment: Child-Pugh {cp} — adult reference dose rewritten from cited "
        f"{src_txt} ({kind} → {dose_txt}), then allometry × maturation. "
        "hepatic_function_fraction remains 1.0 (HI is already in the adult number)."
    )


def run_pediatric_hi_facade(
    case: dict,
    dossier: Optional[dict] = None,
    *,
    fm: Optional[dict] = None,
    route: Optional[str] = None,
) -> dict[str, Any]:
    """Deterministic pediatric HI decision. No I/O, no invented OF.

    Returns entered, adult_dose rewrite, blocked/reason, flags, grade_cap,
    source, resolution. hepatic_function_fraction is always 1.0 when entered.
    """
    dossier = dossier or {}
    work = dict(case)
    if route:
        work["route"] = route
    fm_use = fm if fm is not None else (dossier.get("fm") or work.get("fm") or {})

    out: dict[str, Any] = {
        "entered": False,
        "hepatic_function_fraction": 1.0,
        "adult_dose_mg_per_day": None,
        "blocked": False,
        "block_reason": None,
        "flags": [],
        "grade_cap": None,
        "source": None,
        "resolution": None,
        "hepatic_note": None,
    }

    try:
        mode = resolve_calculator_mode(work)
    except ValueError:
        return out
    if mode != "pediatric" or not work.get("hepatic_impairment"):
        return out

    if hepatic_fm_share(fm_use) < HEPATIC_FM_THRESHOLD:
        out["flags"] = [LOW_FM_FLAG]
        out["source"] = "skipped_low_fm"
        return out

    out["entered"] = True
    adult_table = dossier.get("hi_table")
    pediatric_table = dossier.get("hi_table_pediatric")
    table, source, pick_flags = pick_pediatric_facade_table(
        work, adult_table, pediatric_table
    )
    out["source"] = source
    out["flags"].extend(pick_flags)

    high_e = oral_high_extraction_abstain(work, table, dossier)
    if high_e:
        out["blocked"] = True
        out["block_reason"] = high_e
        out["flags"].append(high_e)
        return out

    if not table:
        out["blocked"] = True
        out["block_reason"] = NO_CITED_ROW
        out["flags"].append(NO_CITED_ROW)
        return out

    res = apply_hi_resolution(work, table)
    out["resolution"] = res
    if res.get("status") != "ok":
        reason = (
            "SAFETY STOP — no cited applicable hepatic-impairment adjustment "
            f"({res.get('reason') or 'resolver abstained'}). Abstain (pediatric HI facade)."
        )
        out["blocked"] = True
        out["block_reason"] = reason
        out["flags"].append(reason)
        return out
    if res.get("kind") == "contraindicated":
        cp = work.get("child_pugh") or "?"
        reason = (
            "SAFETY STOP — label contraindicated in this hepatic-impairment class "
            f"(Child-Pugh {cp})."
        )
        out["blocked"] = True
        out["block_reason"] = reason
        out["flags"].append(reason)
        return out
    if res.get("adult_dose_mg_per_day") is None:
        out["blocked"] = True
        out["block_reason"] = NO_CITED_ROW
        out["flags"].append(NO_CITED_ROW)
        return out

    out["adult_dose_mg_per_day"] = res["adult_dose_mg_per_day"]
    out["hepatic_note"] = _hepatic_note(work, source, res)
    out["flags"].append(out["hepatic_note"])
    if source == "adult_label":
        out["grade_cap"] = "B"
        out["flags"].append(ADULT_LABEL_CAP_FLAG)
    if _renal_stacked(work):
        out["grade_cap"] = "C"
        out["flags"].append(STACKED_MODIFIERS_FLAG)
    return out


def cap_grade(rec: dict, cap: str) -> None:
    """Never raise a grade; only lower toward D. D stays D."""
    if rec.get("blocked"):
        return
    want = _GRADE_ORDER.get(cap)
    if want is None:
        return
    have = _GRADE_ORDER.get(str(rec.get("grade") or ""), 0)
    if have < want:
        rec["grade"] = cap
        extra = f"Grade capped at {cap} (pediatric HI facade)."
        prev = (rec.get("grade_rationale") or "").strip()
        rec["grade_rationale"] = f"{prev} {extra}".strip() if prev else extra


def merge_pediatric_hi_into_recommendation(rec: dict, result: dict) -> None:
    """Flags + grade cap after any safety-block the caller already applied."""
    flags = list(rec.get("flags") or [])
    if result.get("entered") and result.get("hepatic_note"):
        flags = [f for f in flags if not str(f).startswith("HEPATIC impairment")]
    for f in result.get("flags") or []:
        if f not in flags:
            flags.append(f)
    rec["flags"] = flags
    cap = result.get("grade_cap")
    if cap:
        cap_grade(rec, cap)
