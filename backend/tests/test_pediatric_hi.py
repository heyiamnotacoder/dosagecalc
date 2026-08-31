"""Pediatric HI facade — issue #5. Bake cited HI into adult dose, then allometry."""

from __future__ import annotations

from engine.hi_table import extract_hi_table, oral_high_extraction_abstain, table_is_for_oral_product
from engine.pediatric_hi import (
    ADULT_LABEL_CAP_FLAG,
    GUIDELINE_CONFLICT_FLAG,
    HEPATIC_FM_THRESHOLD,
    LOW_FM_FLAG,
    STACKED_MODIFIERS_FLAG,
    cap_grade,
    hepatic_fm_share,
    merge_pediatric_hi_into_recommendation,
    pediatric_hi_should_run,
    run_pediatric_hi_facade,
)
from engine.pk_engine import compute_pediatric_dose


ATOMOXETINE_HI = (
    "Hepatic Impairment: Atomoxetine exposure is increased in patients with "
    "hepatic impairment. In patients with moderate hepatic impairment "
    "(Child-Pugh Class B), initial and target doses should be reduced to 50% "
    "of the normal dose. In patients with severe hepatic impairment "
    "(Child-Pugh Class C), initial and target doses should be reduced to 25% "
    "of the normal dose."
)
ATOMOXETINE_CITE = (
    "Strattera (atomoxetine) US Prescribing Information, section 2.4 / 8.7, "
    "Eli Lilly; FDA label."
)
ATOMOXETINE_ADULT = (
    "The recommended starting daily dose is 40 mg. The target daily dose is "
    "80 mg. The maximum recommended total daily dose is 100 mg."
)


def _adult_table():
    return extract_hi_table(
        text=ATOMOXETINE_HI + " " + ATOMOXETINE_ADULT,
        citation=ATOMOXETINE_CITE,
    )


def _ped_case(**kw):
    case = {
        "drug": "atomoxetine",
        "age_years": 10,
        "weight_kg": 30,
        "calculator_mode": "pediatric",
        "hepatic_impairment": True,
        "child_pugh": "B",
        "route": "oral",
        "adult_dose_mg_per_day": 80,
    }
    case.update(kw)
    return case


def _dossier(table=None, **kw):
    d = {
        "cl_adult_l_h": 20.0,
        "vd_adult_l": 70.0,
        "fm": {"cyp3a4": 0.9},
        "typical_adult_dose_mg_per_day": 80.0,
        "oral_bioavailability": 0.63,
        "hi_table": table if table is not None else _adult_table(),
    }
    d.update(kw)
    return d


def _state(dossier):
    return {
        "pk_ok": True,
        "pk_block_reason": None,
        "blocked_reason": None,
        "last_compute_renal_frac": None,
        "last_dossier": dossier,
    }


def _compute(case, dossier, extra_args=None):
    from agents.agent import _build_compute, _normalize_case

    n = _normalize_case(case)
    state = _state(dossier)
    args = {
        "drug": n["drug"],
        "weight_kg": n["weight_kg"],
        "cl_adult_l_h": dossier["cl_adult_l_h"],
        "vd_adult_l": dossier["vd_adult_l"],
        "fm": dossier["fm"],
        "age_years": n["age_years"],
        "adult_dose_mg_per_day": dossier["typical_adult_dose_mg_per_day"],
        "route": n.get("route") or "iv",
        "hepatic_function_fraction": 0.5,  # model must not win
    }
    if extra_args:
        args.update(extra_args)
    out = _build_compute(n, state)(args)
    return out, state, n


def test_hepatic_fm_share_and_gate():
    assert hepatic_fm_share({"cyp3a4": 0.9}) == 0.9
    assert hepatic_fm_share({"renal_gfr": 0.9}) == 0.0
    assert hepatic_fm_share({"renal_gfr": 0.6, "cyp3a4": 0.3}) == 0.3
    assert hepatic_fm_share({"renal_gfr": 0.8, "cyp3a4": 0.2}) < HEPATIC_FM_THRESHOLD
    case = _ped_case()
    assert pediatric_hi_should_run(case, {"cyp3a4": 0.9}) is True
    assert pediatric_hi_should_run(case, {"renal_gfr": 0.9}) is False
    adult = _ped_case(calculator_mode="adult_hi")
    assert pediatric_hi_should_run(adult, {"cyp3a4": 0.9}) is False
    print("  pediatric HI: fm gate  OK")


def test_bake_then_allometry_keeps_hepatic_of_one():
    table = _adult_table()
    dossier = _dossier(table)
    case = _ped_case()
    out, state, n = _compute(case, dossier)
    assert not out.get("error"), out
    assert not out.get("blocked"), out
    assert state["last_pediatric_hi"]["entered"] is True
    assert state["last_pediatric_hi"]["adult_dose_mg_per_day"] == 40.0
    assert state["last_hi_resolution"]["adult_dose_mg_per_day"] == 40.0
    for p in out["pathways"]:
        if not str(p["pathway"]).startswith("renal"):
            assert p["organ_function_modifier"] == 1.0, p

    healthy = compute_pediatric_dose(
        drug="atomoxetine",
        weight_kg=30,
        cl_adult_l_h=20.0,
        vd_adult_l=70.0,
        fm={"cyp3a4": 0.9},
        age_years=10,
        adult_dose_mg_per_day=80.0,
        hepatic_function_fraction=1.0,
        route="oral",
        oral_bioavailability=0.63,
    )
    baked = compute_pediatric_dose(
        drug="atomoxetine",
        weight_kg=30,
        cl_adult_l_h=20.0,
        vd_adult_l=70.0,
        fm={"cyp3a4": 0.9},
        age_years=10,
        adult_dose_mg_per_day=40.0,
        hepatic_function_fraction=1.0,
        route="oral",
        oral_bioavailability=0.63,
    )
    assert round(baked.recommended_dose_mg_per_day, 2) == out["recommended_dose_mg_per_day"]
    assert abs(baked.recommended_dose_mg_per_day * 2 - healthy.recommended_dose_mg_per_day) < 0.05
    print("  pediatric HI: bake then allometry, OF=1.0  OK")


def test_low_hepatic_fm_does_not_enter():
    dossier = _dossier(fm={"renal_gfr": 0.9})
    out, state, n = _compute(_ped_case(), dossier)
    assert not out.get("blocked"), out
    assert state["last_pediatric_hi"]["entered"] is False
    assert state["last_pediatric_hi"]["source"] == "skipped_low_fm"
    healthy = compute_pediatric_dose(
        drug="atomoxetine",
        weight_kg=30,
        cl_adult_l_h=20.0,
        vd_adult_l=70.0,
        fm={"renal_gfr": 0.9},
        age_years=10,
        adult_dose_mg_per_day=80.0,
        hepatic_function_fraction=1.0,
        route="oral",
        oral_bioavailability=0.63,
    )
    assert out["recommended_dose_mg_per_day"] == round(healthy.recommended_dose_mg_per_day, 2)
    rec = {"grade": "A", "flags": ["HEPATIC impairment: consult reference."]}
    merge_pediatric_hi_into_recommendation(rec, state["last_pediatric_hi"])
    assert rec["grade"] == "A"
    assert any(LOW_FM_FLAG in f for f in rec["flags"])
    print("  pediatric HI: fm < 0.3 does not enter  OK")


def test_no_cited_row_abstains():
    dossier = _dossier(table=None, hi_table=None)
    out, state, n = _compute(_ped_case(), dossier)
    assert out.get("blocked") is True, out
    assert out.get("recommended_dose_mg_per_day") is None
    rec = {
        "grade": "B",
        "final_dose_mg_per_day": 12.0,
        "final_dose_mg_per_kg_per_day": 0.4,
        "flags": [],
    }
    from agents.agent import _force_safety_block

    if state["last_pediatric_hi"].get("blocked"):
        _force_safety_block(rec, state["last_pediatric_hi"]["block_reason"])
    merge_pediatric_hi_into_recommendation(rec, state["last_pediatric_hi"])
    assert rec["grade"] == "D"
    assert rec["final_dose_mg_per_day"] is None
    print("  pediatric HI: no cited row → abstain  OK")


def test_adult_label_grade_cap_b():
    result = run_pediatric_hi_facade(_ped_case(), _dossier(), fm={"cyp3a4": 0.9})
    assert result["entered"] and not result["blocked"], result
    assert result["grade_cap"] == "B"
    rec = {"grade": "A", "grade_rationale": "concordant", "flags": []}
    merge_pediatric_hi_into_recommendation(rec, result)
    assert rec["grade"] == "B"
    assert any(ADULT_LABEL_CAP_FLAG in f for f in rec["flags"])
    print("  pediatric HI: adult label grade cap B  OK")


def test_renal_plus_hi_stacked_cap_c():
    case = _ped_case(renal_impairment=True, renal_function_fraction=0.5)
    dossier = _dossier(fm={"renal_gfr": 0.5, "cyp3a4": 0.5})
    out, state, n = _compute(case, dossier)
    assert not out.get("blocked"), out
    assert state["last_pediatric_hi"]["grade_cap"] == "C"
    rec = {"grade": "A", "flags": []}
    merge_pediatric_hi_into_recommendation(rec, state["last_pediatric_hi"])
    assert rec["grade"] == "C"
    assert any(STACKED_MODIFIERS_FLAG in f for f in rec["flags"])
    renal_ofs = [
        p["organ_function_modifier"]
        for p in out["pathways"]
        if str(p["pathway"]).startswith("renal")
    ]
    hep_ofs = [
        p["organ_function_modifier"]
        for p in out["pathways"]
        if not str(p["pathway"]).startswith("renal")
    ]
    assert renal_ofs and renal_ofs[0] == 0.5
    assert hep_ofs and hep_ofs[0] == 1.0
    print("  pediatric HI: stacked renal+HI grade cap C  OK")


def test_oral_high_e_requires_oral_product_row():
    iv_ish = extract_hi_table(
        text=(
            "Hepatic Impairment: In moderate hepatic impairment (Child-Pugh B) "
            "reduce to 50% of the usual adult dose of 80 mg per day."
        ),
        citation="Injectable product US PI, hepatic-impairment dosing.",
    )
    case = _ped_case(route="oral")
    dossier = _dossier(iv_ish, oral_bioavailability=0.2)
    assert oral_high_extraction_abstain(case, iv_ish, dossier)
    out, state, n = _compute(case, dossier, extra_args={"oral_bioavailability": 0.2})
    assert out.get("blocked") is True, out
    assert "oral" in (out.get("block_reason") or "").lower()

    oral_row = extract_hi_table(
        text=(
            "For the oral product: in moderate hepatic impairment (Child-Pugh B) "
            "reduce to 50% of the usual adult dose of 80 mg per day."
        ),
        citation="Oral capsules US PI, hepatic-impairment dosing.",
    )
    assert table_is_for_oral_product(oral_row)
    ok, state2, _ = _compute(
        case, _dossier(oral_row, oral_bioavailability=0.2),
        extra_args={"oral_bioavailability": 0.2},
    )
    assert not ok.get("blocked"), ok
    assert state2["last_pediatric_hi"]["adult_dose_mg_per_day"] == 40.0

    iv_case = _ped_case(route="iv")
    iv_out, _, _ = _compute(
        iv_case, _dossier(iv_ish, oral_bioavailability=0.2),
        extra_args={"route": "iv", "oral_bioavailability": 0.2},
    )
    assert not iv_out.get("blocked"), iv_out
    print("  pediatric HI: oral high-E oral-product rule  OK")


def test_pediatric_guideline_beats_adult_label():
    adult = _adult_table()
    pediatric = extract_hi_table(
        text=(
            "Pediatric hepatic-impairment dosing: in moderate hepatic impairment "
            "(Child-Pugh B) reduce to 25% of the usual adult dose of 80 mg per day."
        ),
        citation="BNFC pediatric HI dosing guideline, atomoxetine.",
    )
    dossier = _dossier(adult, hi_table_pediatric=pediatric)
    result = run_pediatric_hi_facade(_ped_case(), dossier, fm={"cyp3a4": 0.9})
    assert result["entered"] and not result["blocked"], result
    assert result["source"] == "pediatric_guideline"
    assert result["adult_dose_mg_per_day"] == 20.0
    assert any(GUIDELINE_CONFLICT_FLAG in f for f in result["flags"])
    # Pediatric guideline is not the adult-label cap-B rule.
    assert result["grade_cap"] is None
    print("  pediatric HI: pediatric guideline wins + conflict flag  OK")


def test_cap_grade_never_raises():
    rec = {"grade": "C", "flags": []}
    cap_grade(rec, "B")
    assert rec["grade"] == "C"
    rec_d = {"grade": "D", "blocked": True, "flags": []}
    cap_grade(rec_d, "B")
    assert rec_d["grade"] == "D"
    print("  pediatric HI: cap_grade never raises  OK")


if __name__ == "__main__":
    print("Pediatric HI facade (issue #5):")
    test_hepatic_fm_share_and_gate()
    test_bake_then_allometry_keeps_hepatic_of_one()
    test_low_hepatic_fm_does_not_enter()
    test_no_cited_row_abstains()
    test_adult_label_grade_cap_b()
    test_renal_plus_hi_stacked_cap_c()
    test_oral_high_e_requires_oral_product_row()
    test_pediatric_guideline_beats_adult_label()
    test_cap_grade_never_raises()
    print("All pediatric-HI tests passed.")
