"""
Deterministic edge-case flags: prodrug, obesity, protein binding, illness.

Only flags when evidence is present in case/dossier. Does not invent dose math.
Hints (e.g. dosing_weight_kg) are suggestions for the agent — never silent rewrites.
"""

from __future__ import annotations

from typing import Any, Optional

# Known prodrugs (parent name → active moiety note). Extend carefully.
_PRODRUGS = {
    "codeine": "morphine (CYP2D6); parent CL does not equal analgesic effect",
    "tramadol": "O-desmethyltramadol / M1 (CYP2D6)",
    "oseltamivir": "oseltamivir carboxylate (esterases)",
    "clopidogrel": "active thiol metabolite (CYP2C19)",
    "enalapril": "enalaprilat (esterases)",
    "prednisone": "prednisolone (11β-HSD)",
    "levodopa": "dopamine (aromatic L-amino acid decarboxylase)",
    "fosphenytoin": "phenytoin (phosphatases)",
    "cefuroxime axetil": "cefuroxime (esterases)",
    "valacyclovir": "acyclovir (esterases)",
}

_CRITICAL_ILLNESS_HINTS = (
    "sepsis", "septic", "shock", "icu", "critical", "ards", "ecmo",
    "multi-organ", "mof", "hypoalbumin", "burns", "trauma",
)


def _ideal_weight_kg(age_years: float) -> Optional[float]:
    """Rough pediatric ideal body weight (kg). Not for clinical use alone."""
    if age_years is None or age_years < 0:
        return None
    if age_years < 1:
        # ~ expected wt at age months (simple linear from 3.5 kg term)
        months = age_years * 12
        return 3.5 + months * 0.6  # ~10.7 kg at 12 mo
    if age_years <= 5:
        return 2 * (age_years + 4)  # classic APLS-style approx for 1–5 y
    if age_years <= 12:
        return 3 * age_years + 7
    return None  # adolescent: skip auto obesity flag without height


def assess_edge_cases(
    case: dict,
    dossier: Optional[dict] = None,
    engine_result: Optional[dict] = None,
) -> dict[str, Any]:
    """Return flags / adjustment hints when evidence supports them."""
    flags: list[str] = []
    notes: list[str] = []
    adjustments: dict[str, Any] = {}
    dossier = dossier or {}
    case = case or {}

    drug = (case.get("drug") or dossier.get("drug") or "").strip().lower()
    age = case.get("age_years")
    try:
        age_f = float(age) if age is not None else None
    except (TypeError, ValueError):
        age_f = None
    try:
        wt = float(case["weight_kg"]) if case.get("weight_kg") is not None else None
    except (TypeError, ValueError):
        wt = None

    # ---- prodrug ----
    prodrug_note = _PRODRUGS.get(drug)
    enzymes = [str(e).upper() for e in (dossier.get("enzymes") or [])]
    actives = [str(a).lower() for a in (dossier.get("active_metabolites") or [])]
    conf = (dossier.get("confidence") or "").lower()
    if prodrug_note:
        flags.append(
            f"PRODRUG: {drug} → {prodrug_note}. Matching parent clearance may mis-predict "
            "effect; consider active-moiety maturation and (if relevant) genotype."
        )
    elif "prodrug" in conf or any("prodrug" in a for a in actives):
        flags.append(
            "PRODRUG signal in dossier — parent CL may not drive effect; verify active moiety."
        )

    # ---- obesity ----
    if age_f is not None and wt is not None:
        ideal = _ideal_weight_kg(age_f)
        obese = False
        if ideal and ideal > 0 and wt / ideal >= 1.2:
            obese = True
        # Explicit demo threshold: ~1 y and ≥14 kg
        if age_f <= 1.5 and wt >= 14.0:
            obese = True
        if obese:
            dosing_wt = min(wt, ideal) if ideal else wt
            flags.append(
                f"OBESITY / high weight-for-age ({wt:.1f} kg at {age_f:.2f} y"
                + (f"; rough ideal ≈ {ideal:.1f} kg" if ideal else "")
                + "). Weight-linear or allometric dose on total body weight may overestimate "
                "exposure for some drugs — consider adjusted body weight and TDM where used."
            )
            if ideal:
                adjustments["dosing_weight_kg_hint"] = round(dosing_wt, 2)
                adjustments["ideal_weight_kg"] = round(ideal, 2)
                notes.append(
                    "dosing_weight_kg_hint is advisory only; do not silently replace weight_kg."
                )

    # ---- protein binding ----
    pb = dossier.get("protein_binding_percent")
    if pb is None and engine_result:
        pb = engine_result.get("protein_binding_percent")
    try:
        pb_f = float(pb) if pb is not None else None
    except (TypeError, ValueError):
        pb_f = None

    neonate = False
    if age_f is not None and age_f < 0.25:  # ~3 months
        neonate = True
    pma = case.get("pma_weeks")
    try:
        if pma is not None and float(pma) < 50:
            neonate = True
    except (TypeError, ValueError):
        pass

    indication = (case.get("indication") or "").lower()
    illness = any(h in indication for h in _CRITICAL_ILLNESS_HINTS)

    def _frac_impaired(key: str) -> bool:
        """True when organ-function fraction is present and < 0.99. Bad values → not impaired."""
        raw = case.get(key)
        if raw is None or raw == "":
            return False
        try:
            return float(raw) < 0.99
        except (TypeError, ValueError):
            return False

    renal = bool(case.get("renal_impairment")) or _frac_impaired("renal_function_fraction")
    hepatic = bool(case.get("hepatic_impairment")) or _frac_impaired("hepatic_function_fraction")

    if pb_f is not None and pb_f >= 90 and (neonate or illness or hepatic):
        flags.append(
            f"PROTEIN BINDING {pb_f:.0f}% is high and patient is neonate and/or ill/hepatic — "
            "free (unbound) fraction may rise (low albumin); total-concentration targets can mislead."
        )

    # ---- illness / organ impairment ----
    if renal:
        flags.append(
            "RENAL impairment flagged — organ-function modifier applied to renal pathways; "
            "reassess interval and TDM for renally cleared / NTI drugs."
        )
    if hepatic:
        flags.append(
            "HEPATIC impairment flagged — adjustment is drug-specific (hepatic extraction ratio / "
            "metabolic pathway); NO automatic clearance reduction is applied. First-pass and "
            "high-extraction drugs especially uncertain — consult a drug-specific reference."
        )
    if illness and not (renal or hepatic):
        flags.append(
            "CRITICAL ILLNESS / sepsis-class indication — PK/PD may diverge from healthy-adult "
            "exposure matching (Vd shifts, augmented/impaired CL). Treat estimate as starting point only."
        )

    # Engine safety warnings already produced — surface as notes, not duplicate
    if engine_result and engine_result.get("warnings"):
        notes.append(f"engine_warnings_count={len(engine_result['warnings'])}")

    return {"flags": flags, "adjustments": adjustments, "notes": notes}
