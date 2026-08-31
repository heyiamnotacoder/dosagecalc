"""Adult HI facade: cited label lookup. No allometry, no maturation, no A–D.

Issue #6. Uses the single HI resolver in hi_table.py — never a second parser,
never an invented hepatic_function_fraction.
"""

from __future__ import annotations

from typing import Any, Optional

from engine.child_pugh import resolve_calculator_mode, resolve_child_pugh
from engine.hi_table import (
    apply_hi_resolution,
    oral_high_extraction_abstain,
    pick_facade_table,
)

LABEL_DOSE = "label_dose"
NO_LABELED_ADJUSTMENT = "no_labeled_adjustment"
CONTRAINDICATED = "contraindicated"
ABSTAIN = "abstain"

OUTCOME_LABELS = {
    LABEL_DOSE: "Label dose",
    NO_LABELED_ADJUSTMENT: "No labeled adjustment",
    CONTRAINDICATED: "Contraindicated",
    ABSTAIN: "Abstain",
}

GUIDELINE_CONFLICT_FLAG = (
    "Pediatric HI dosing guideline disagrees with the adult label; "
    "adult label used on this facade."
)
NO_ALLOMETRY_FLAG = (
    "Adult HI facade: cited label lookup only — no allometry, no maturation, no A–D grade."
)
NO_CITED_ROW = (
    "SAFETY STOP — no cited applicable hepatic-impairment adjustment; "
    "abstain (adult HI facade)."
)
FOLD_ONLY_NO_DOSE = (
    "SAFETY STOP — fold-only hepatic-impairment instruction with no usual or "
    "override adult dose; abstain (adult HI facade)."
)


def adult_hi_should_run(case: dict) -> bool:
    try:
        return resolve_calculator_mode(case) == "adult_hi"
    except ValueError:
        return False


def pick_adult_facade_table(
    case: dict,
    adult_table: Optional[dict],
    pediatric_table: Optional[dict],
) -> tuple[Optional[dict], str, list[str]]:
    """Adult label wins when it has an applicable row; flag pediatric conflict."""
    table, source, conflict = pick_facade_table(
        case, adult_table, pediatric_table, prefer="adult_label"
    )
    flags = [GUIDELINE_CONFLICT_FLAG] if conflict else []
    return table, source, flags


def _hepatic_note(case: dict, source: str, res: dict, outcome: str) -> str:
    cp = resolve_child_pugh(case).get("child_pugh") or case.get("child_pugh") or "?"
    kind = res.get("kind") or "cited"
    dose = res.get("adult_dose_mg_per_day")
    dose_txt = f"{dose:g} mg/day" if isinstance(dose, (int, float)) else "no numeric dose"
    src_txt = (
        "pediatric HI dosing guideline" if source == "pediatric_guideline" else "adult HI label"
    )
    label = OUTCOME_LABELS.get(outcome, outcome)
    return (
        f"HEPATIC impairment: Child-Pugh {cp} — {label} from cited {src_txt} "
        f"({kind} → {dose_txt}). No allometry, no maturation, no A–D grade."
    )


def _outcome_from_resolution(res: dict) -> str:
    if res.get("status") != "ok":
        return ABSTAIN
    if res.get("kind") == "contraindicated":
        return CONTRAINDICATED
    if res.get("kind") == "fold":
        try:
            if res.get("fold") is not None and abs(float(res["fold"]) - 1.0) < 1e-9:
                return NO_LABELED_ADJUSTMENT
        except (TypeError, ValueError):
            pass
    if res.get("adult_dose_mg_per_day") is None:
        return ABSTAIN
    return LABEL_DOSE


def run_adult_hi_facade(
    case: dict,
    dossier: Optional[dict] = None,
    *,
    route: Optional[str] = None,
) -> dict[str, Any]:
    """Deterministic adult HI decision. No I/O, no allometry, no A–D.

    Returns entered, outcome, adult_dose, blocked/reason, flags, source, resolution.
    """
    dossier = dossier or {}
    work = dict(case)
    if route:
        work["route"] = route
    if dossier.get("typical_adult_dose_mg_per_day") is not None and work.get(
        "adult_dose_mg_per_day"
    ) is None and work.get("user_adult_dose_mg_per_day") is None:
        work["adult_dose_mg_per_day"] = dossier["typical_adult_dose_mg_per_day"]

    out: dict[str, Any] = {
        "entered": False,
        "outcome": None,
        "outcome_label": None,
        "adult_dose_mg_per_day": None,
        "blocked": False,
        "block_reason": None,
        "flags": [NO_ALLOMETRY_FLAG],
        "source": None,
        "resolution": None,
        "hepatic_note": None,
        "grade": None,
        "allometry_applied": False,
    }

    try:
        mode = resolve_calculator_mode(work)
    except ValueError:
        return out
    if mode != "adult_hi":
        out["flags"] = []
        return out

    out["entered"] = True
    adult_table = dossier.get("hi_table")
    pediatric_table = dossier.get("hi_table_pediatric")
    table, source, pick_flags = pick_adult_facade_table(
        work, adult_table, pediatric_table
    )
    out["source"] = source
    out["flags"].extend(pick_flags)

    high_e = oral_high_extraction_abstain(work, table, dossier)
    if high_e:
        out["outcome"] = ABSTAIN
        out["outcome_label"] = OUTCOME_LABELS[ABSTAIN]
        out["blocked"] = True
        out["block_reason"] = high_e
        out["flags"].append(high_e)
        return out

    if not table:
        out["outcome"] = ABSTAIN
        out["outcome_label"] = OUTCOME_LABELS[ABSTAIN]
        out["blocked"] = True
        out["block_reason"] = NO_CITED_ROW
        out["flags"].append(NO_CITED_ROW)
        return out

    res = apply_hi_resolution(work, table)
    out["resolution"] = res
    if res.get("status") != "ok":
        reason = res.get("reason") or "resolver abstained"
        if "fold-only" in str(reason).lower() or "no adult dose" in str(reason).lower():
            block = FOLD_ONLY_NO_DOSE
        else:
            block = (
                "SAFETY STOP — no cited applicable hepatic-impairment adjustment "
                f"({reason}). Abstain (adult HI facade)."
            )
        out["outcome"] = ABSTAIN
        out["outcome_label"] = OUTCOME_LABELS[ABSTAIN]
        out["blocked"] = True
        out["block_reason"] = block
        out["flags"].append(block)
        return out

    outcome = _outcome_from_resolution(res)
    out["outcome"] = outcome
    out["outcome_label"] = OUTCOME_LABELS[outcome]
    if outcome == CONTRAINDICATED:
        cp = work.get("child_pugh") or "?"
        reason = (
            "SAFETY STOP — label contraindicated in this hepatic-impairment class "
            f"(Child-Pugh {cp})."
        )
        out["blocked"] = True
        out["block_reason"] = reason
        out["flags"].append(reason)
        out["hepatic_note"] = _hepatic_note(work, source, res, outcome)
        return out
    if res.get("adult_dose_mg_per_day") is None:
        out["outcome"] = ABSTAIN
        out["outcome_label"] = OUTCOME_LABELS[ABSTAIN]
        out["blocked"] = True
        out["block_reason"] = NO_CITED_ROW
        out["flags"].append(NO_CITED_ROW)
        return out

    out["adult_dose_mg_per_day"] = res["adult_dose_mg_per_day"]
    out["hepatic_note"] = _hepatic_note(work, source, res, outcome)
    out["flags"].append(out["hepatic_note"])
    return out


def recommendation_from_adult_hi(
    case: dict,
    result: dict,
    dossier: Optional[dict] = None,
) -> dict[str, Any]:
    """Submit-shaped rec: Label dose / No labeled adjustment / Contraindicated. No A–D."""
    dossier = dossier or {}
    blocked = bool(result.get("blocked"))
    dose = None if blocked else result.get("adult_dose_mg_per_day")
    dpk = None
    wt = case.get("weight_kg")
    if dose is not None and wt not in (None, ""):
        try:
            dpk = round(float(dose) / float(wt), 3)
        except (TypeError, ValueError, ZeroDivisionError):
            dpk = None
    outcome = result.get("outcome")
    rec: dict[str, Any] = {
        "final_dose_mg_per_day": None if blocked or dose is None else round(float(dose), 2),
        "final_dose_mg_per_kg_per_day": None if blocked else dpk,
        "grade": None,
        "grade_rationale": "Adult HI facade does not use A–D grades.",
        "hi_outcome": outcome,
        "hi_outcome_label": result.get("outcome_label") or OUTCOME_LABELS.get(outcome or "", outcome),
        "blocked": blocked,
        "block_reason": result.get("block_reason"),
        "flags": list(result.get("flags") or []),
        "rationale": result.get("hepatic_note") or result.get("block_reason") or NO_ALLOMETRY_FLAG,
        "assumptions": [
            "Cited hepatic-impairment row from the adult label "
            "(pediatric guideline only if no adult row applies).",
            "No allometry and no maturation on this facade.",
        ],
        "uncertainty": (
            "This is a labeled adult hepatic-impairment lookup, not a pediatric "
            "starting-dose extrapolation."
        ),
        "citations": [],
        "contraindications_avoid": [],
        "calculator_mode": "adult_hi",
        "allometry_applied": False,
        "route": case.get("route") or "iv",
    }
    table = None
    if result.get("source") == "pediatric_guideline":
        table = dossier.get("hi_table_pediatric")
    else:
        table = dossier.get("hi_table")
    cite = (table or {}).get("citation")
    excerpt = (table or {}).get("excerpt")
    if cite:
        rec["citations"] = [{
            "claim": excerpt or "Hepatic-impairment dosing from cited label/guideline",
            "source": cite,
        }]
    return rec


def merge_adult_hi_into_recommendation(rec: dict, result: dict) -> None:
    """Strip A–D, attach outcome + flags. Never invents a grade."""
    rec["grade"] = None
    rec["allometry_applied"] = False
    rec["hi_outcome"] = result.get("outcome")
    rec["hi_outcome_label"] = result.get("outcome_label") or rec.get("hi_outcome_label")
    rec["grade_rationale"] = "Adult HI facade does not use A–D grades."
    flags = list(rec.get("flags") or [])
    if result.get("entered") and result.get("hepatic_note"):
        flags = [f for f in flags if not str(f).startswith("HEPATIC impairment")]
    for f in result.get("flags") or []:
        if f not in flags:
            flags.append(f)
    rec["flags"] = flags
    if result.get("blocked"):
        rec["blocked"] = True
        rec["block_reason"] = result.get("block_reason") or rec.get("block_reason")
        rec["final_dose_mg_per_day"] = None
        rec["final_dose_mg_per_kg_per_day"] = None
