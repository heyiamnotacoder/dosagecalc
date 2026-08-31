"""Adult HI facade — issue #6. Label lookup, no allometry, no A–D."""

from __future__ import annotations

import inspect
from unittest.mock import patch

from engine.adult_hi import (
    ABSTAIN,
    CONTRAINDICATED,
    GUIDELINE_CONFLICT_FLAG,
    LABEL_DOSE,
    NO_ALLOMETRY_FLAG,
    NO_LABELED_ADJUSTMENT,
    adult_hi_should_run,
    merge_adult_hi_into_recommendation,
    recommendation_from_adult_hi,
    run_adult_hi_facade,
)
from engine.child_pugh import CHILD_PUGH_ON_CHILD_FLAG
from engine.hi_table import extract_hi_table, oral_high_extraction_abstain, table_is_for_oral_product
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


def _adult_case(**kw):
    case = {
        "drug": "atomoxetine",
        "age_years": 45,
        "weight_kg": 70,
        "calculator_mode": "adult_hi",
        "hepatic_impairment": True,
        "child_pugh": "B",
        "route": "oral",
        "adult_dose_mg_per_day": 80,
    }
    case.update(kw)
    return case


def _dossier(table=None, **kw):
    d = {
        "typical_adult_dose_mg_per_day": 80.0,
        "oral_bioavailability": 0.63,
        "hi_table": table if table is not None else _adult_table(),
        "cl_adult_l_h": 20.0,
        "vd_adult_l": 70.0,
        "fm": {"cyp3a4": 0.9},
    }
    d.update(kw)
    return d


def _state(dossier):
    return {
        "pk_ok": False,
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
        "age_years": n["age_years"],
        "route": n.get("route") or "iv",
    }
    if extra_args:
        args.update(extra_args)
    out = _build_compute(n, state)(args)
    return out, state, n


def test_adult_hi_emits_three_outcomes():
    result = run_adult_hi_facade(_adult_case(), _dossier())
    assert result["entered"] and not result["blocked"], result
    assert result["outcome"] == LABEL_DOSE
    assert result["outcome_label"] == "Label dose"
    assert result["adult_dose_mg_per_day"] == 40.0
    assert result["grade"] is None

    mild = extract_hi_table(
        text=(
            "No dosage adjustment is necessary in mild hepatic impairment "
            "(Child-Pugh A). Typical adult dose is 80 mg per day."
        ),
        citation=ATOMOXETINE_CITE,
    )
    none = run_adult_hi_facade(_adult_case(child_pugh="A"), _dossier(mild))
    assert none["outcome"] == NO_LABELED_ADJUSTMENT, none
    assert none["adult_dose_mg_per_day"] == 80.0
    assert not none["blocked"]

    contra = extract_hi_table(
        text=(
            "Do not use in severe hepatic impairment (Child-Pugh C). "
            "Typical adult dose is 80 mg per day."
        ),
        citation=ATOMOXETINE_CITE,
    )
    stop = run_adult_hi_facade(_adult_case(child_pugh="C"), _dossier(contra))
    assert stop["outcome"] == CONTRAINDICATED, stop
    assert stop["blocked"] is True
    assert stop["adult_dose_mg_per_day"] is None
    print("  adult HI: Label dose / No labeled adjustment / Contraindicated  OK")


def test_no_allometry_and_no_ad_grade():
    out, state, n = _compute(_adult_case(age_years=10, weight_kg=30), _dossier())
    assert not out.get("error"), out
    assert not out.get("blocked"), out
    assert out["recommended_dose_mg_per_day"] == 40.0
    assert out.get("allometry_applied") is False
    assert "pathways" not in out
    assert out.get("grade") is None
    assert out.get("hi_outcome") == LABEL_DOSE
    assert state["last_adult_hi"]["entered"] is True
    assert state["last_adult_hi"]["grade"] is None

    allo = compute_pediatric_dose(
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
    assert round(allo.recommended_dose_mg_per_day, 2) != 40.0

    rec = recommendation_from_adult_hi(n, state["last_adult_hi"], _dossier())
    assert rec["grade"] is None
    assert rec["hi_outcome"] == LABEL_DOSE
    assert rec["final_dose_mg_per_day"] == 40.0
    assert rec["allometry_applied"] is False
    print("  adult HI: no allometry, no A–D  OK")


def test_same_hi_module_no_second_parser():
    import engine.adult_hi as mod
    src = inspect.getsource(mod)
    assert "def resolve_hi_dose" not in src
    assert "def extract_hi_table" not in src
    assert adult_hi_should_run(_adult_case()) is True
    assert adult_hi_should_run({"calculator_mode": "pediatric", "hepatic_impairment": True}) is False
    print("  adult HI: same HI module, no second parser  OK")


def test_oral_high_e_same_rule():
    iv_ish = extract_hi_table(
        text=(
            "Hepatic Impairment: In moderate hepatic impairment (Child-Pugh B) "
            "reduce to 50% of the usual adult dose of 80 mg per day."
        ),
        citation="Injectable product US PI, hepatic-impairment dosing.",
    )
    case = _adult_case(route="oral")
    dossier = _dossier(iv_ish, oral_bioavailability=0.2)
    assert oral_high_extraction_abstain(case, iv_ish, dossier)
    out, state, n = _compute(case, dossier, extra_args={"oral_bioavailability": 0.2})
    assert out.get("blocked") is True, out
    assert out.get("hi_outcome") == ABSTAIN

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
    assert ok["recommended_dose_mg_per_day"] == 40.0
    print("  adult HI: oral high-E same rule  OK")


def test_adult_label_beats_pediatric_guideline():
    adult = _adult_table()
    pediatric = extract_hi_table(
        text=(
            "Pediatric hepatic-impairment dosing: in moderate hepatic impairment "
            "(Child-Pugh B) reduce to 25% of the usual adult dose of 80 mg per day."
        ),
        citation="BNFC pediatric HI dosing guideline, atomoxetine.",
    )
    dossier = _dossier(adult, hi_table_pediatric=pediatric)
    result = run_adult_hi_facade(_adult_case(), dossier)
    assert result["entered"] and not result["blocked"], result
    assert result["source"] == "adult_label"
    assert result["adult_dose_mg_per_day"] == 40.0
    assert any(GUIDELINE_CONFLICT_FLAG in f for f in result["flags"])
    print("  adult HI: adult label wins + conflict flag  OK")


def test_fold_only_no_adult_dose_abstains():
    table = extract_hi_table(text=ATOMOXETINE_HI, citation=ATOMOXETINE_CITE)
    dossier = _dossier(table, typical_adult_dose_mg_per_day=None)
    case = _adult_case()
    case.pop("adult_dose_mg_per_day")
    result = run_adult_hi_facade(case, dossier)
    assert result["blocked"] is True, result
    assert result["outcome"] == ABSTAIN
    assert result["adult_dose_mg_per_day"] is None
    rec = recommendation_from_adult_hi(case, result, dossier)
    assert rec["final_dose_mg_per_day"] is None
    assert rec["grade"] is None
    print("  adult HI: fold-only no adult dose → abstain  OK")


def test_contraindicated_blocked_no_dose():
    contra = extract_hi_table(
        text=(
            "Atomoxetine is contraindicated in severe hepatic impairment "
            "(Child-Pugh C). Typical adult dose is 80 mg per day."
        ),
        citation=ATOMOXETINE_CITE,
    )
    out, state, n = _compute(_adult_case(child_pugh="C"), _dossier(contra))
    assert out.get("blocked") is True, out
    assert out.get("recommended_dose_mg_per_day") is None
    rec = recommendation_from_adult_hi(n, state["last_adult_hi"], _dossier(contra))
    merge_adult_hi_into_recommendation(rec, state["last_adult_hi"])
    assert rec["blocked"] is True
    assert rec["final_dose_mg_per_day"] is None
    assert rec["hi_outcome"] == CONTRAINDICATED
    assert rec["grade"] is None
    print("  adult HI: contraindicated → blocked, no dose  OK")


def test_age_under_18_still_adult_facade():
    from agents.agent import _apply_organ_function_flags, _normalize_case

    case = _normalize_case(_adult_case(age_years=10, weight_kg=30))
    result = run_adult_hi_facade(case, _dossier())
    rec = recommendation_from_adult_hi(case, result, _dossier())
    _apply_organ_function_flags(rec, case)
    merge_adult_hi_into_recommendation(rec, result)
    assert rec["final_dose_mg_per_day"] == 40.0
    assert rec["grade"] is None
    assert any(CHILD_PUGH_ON_CHILD_FLAG in f for f in rec["flags"])
    assert any(NO_ALLOMETRY_FLAG in f for f in rec["flags"])
    print("  adult HI: age < 18 still label lookup + Child-Pugh-on-child flag  OK")


def test_run_case_short_circuits_orchestrator():
    from agents.agent import _normalize_case, _run_adult_hi_case

    case = _normalize_case(_adult_case())
    with patch(
        "agents.agent._load_adult_hi_dossier",
        return_value=(_dossier(), "test", {"input_tokens": 0, "output_tokens": 0}),
    ):
        wrap = _run_adult_hi_case(case)
    rec = wrap["recommendation"]
    assert wrap["usage"]["model"] == "adult_hi_facade"
    assert rec["grade"] is None
    assert rec["hi_outcome"] == LABEL_DOSE
    assert rec["final_dose_mg_per_day"] == 40.0
    assert rec["allometry_applied"] is False
    print("  adult HI: run_case short-circuit, no orchestrator  OK")


if __name__ == "__main__":
    print("Adult HI facade (issue #6):")
    test_adult_hi_emits_three_outcomes()
    test_no_allometry_and_no_ad_grade()
    test_same_hi_module_no_second_parser()
    test_oral_high_e_same_rule()
    test_adult_label_beats_pediatric_guideline()
    test_fold_only_no_adult_dose_abstains()
    test_contraindicated_blocked_no_dose()
    test_age_under_18_still_adult_facade()
    test_run_case_short_circuits_orchestrator()
    print("All adult-HI tests passed.")
