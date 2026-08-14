"""HI table extract + resolve — issue #3.

Seams: extract_hi_table (label/guideline text → cited table),
resolve_hi_dose (one resolver for both facades).
"""

from __future__ import annotations

import inspect

from engine.hi_table import extract_hi_table, resolve_hi_dose


# Verbatim FDA atomoxetine (Strattera) hepatic-impairment dosing language.
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


def test_extract_fills_per_class_contract_with_excerpt_and_citation():
    table = extract_hi_table(text=ATOMOXETINE_HI, citation=ATOMOXETINE_CITE)
    assert table["excerpt"], table
    assert "50%" in table["excerpt"] or "Child-Pugh Class B" in table["excerpt"]
    assert table["citation"] == ATOMOXETINE_CITE
    for cls in ("A", "B", "C"):
        row = table["classes"][cls]
        assert row["kind"] in ("absolute_mg_per_day", "fold", "contraindicated", "absent"), row
        assert "value" in row
    assert table["classes"]["B"]["kind"] == "fold"
    assert table["classes"]["B"]["value"] == 0.5
    assert table["classes"]["C"]["kind"] == "fold"
    assert table["classes"]["C"]["value"] == 0.25
    print("  hi extract: per-class contract + excerpt/citation  OK")


def test_caution_only_or_missing_excerpt_is_not_a_citation():
    try:
        extract_hi_table(
            text="Use with caution in patients with hepatic impairment.",
            citation="Some label.",
        )
    except ValueError as e:
        assert "not a citation" in str(e).lower()
    else:
        raise AssertionError("caution-only text should not be a citation")
    try:
        extract_hi_table(text=ATOMOXETINE_HI, citation="")
    except ValueError as e:
        assert "not a citation" in str(e).lower()
    else:
        raise AssertionError("empty citation should be rejected")
    print("  hi extract: caution-only / empty citation rejected  OK")


def test_mild_moderate_severe_maps_to_abc_and_is_flagged():
    table = extract_hi_table(text=ATOMOXETINE_HI, citation=ATOMOXETINE_CITE)
    assert table["classes"]["B"]["label_term"] == "moderate"
    assert table["classes"]["C"]["label_term"] == "severe"
    assert table["classes"]["B"]["mapped"] is True
    assert table["mapping_flagged"] is True
    print("  hi extract: A↔mild / B↔moderate / C↔severe flagged  OK")


def test_no_adjustment_necessary_is_fold_one():
    text = (
        "Hepatic Impairment: No dosage adjustment is necessary in patients "
        "with mild, moderate, or severe hepatic impairment (Child-Pugh A, B, or C)."
    )
    table = extract_hi_table(text=text, citation="Example SmPC hepatic dosing.")
    for cls in ("A", "B", "C"):
        assert table["classes"][cls]["kind"] == "fold", table["classes"][cls]
        assert table["classes"][cls]["value"] == 1.0
    print("  hi extract: no-adjustment → fold 1.0  OK")


def test_missing_a_is_fold_one_missing_b_uses_c_else_abstain():
    only_c = extract_hi_table(
        text=(
            "In severe hepatic impairment (Child-Pugh C) the dose is 25 mg once daily. "
            "Typical adult dose is 100 mg per day."
        ),
        citation="Label HI dosing table.",
    )
    a = resolve_hi_dose(only_c, "A")
    assert a["status"] == "ok" and a["fold"] == 1.0, a
    assert a["adult_dose_mg_per_day"] == 100.0, a

    b = resolve_hi_dose(only_c, "B")
    assert b["status"] == "ok" and b["kind"] == "absolute_mg_per_day", b
    assert b["adult_dose_mg_per_day"] == 25.0, b

    only_a = extract_hi_table(
        text=(
            "Mild hepatic impairment (Child-Pugh A): no adjustment necessary. "
            "Typical adult dose is 80 mg per day."
        ),
        citation="Label HI dosing.",
    )
    assert resolve_hi_dose(only_a, "B")["status"] == "abstain"
    assert resolve_hi_dose(only_a, "C")["status"] == "abstain"
    print("  hi resolve: missing A → 1.0; missing B → C else abstain  OK")


def test_missing_c_uses_moderate_else_abstain():
    only_b = extract_hi_table(
        text=(
            "Moderate hepatic impairment (Child-Pugh Class B): reduce to 50% of "
            "the usual adult dose of 80 mg per day."
        ),
        citation="Label HI dosing.",
    )
    c = resolve_hi_dose(only_b, "C")
    assert c["status"] == "ok" and c["fold"] == 0.5, c
    assert c["adult_dose_mg_per_day"] == 40.0, c
    print("  hi resolve: missing C → moderate/B  OK")


def test_user_adult_dose_overrides_label_fold_only_without_dose_abstains():
    table = extract_hi_table(text=ATOMOXETINE_HI, citation=ATOMOXETINE_CITE)
    assert resolve_hi_dose(table, "B")["status"] == "abstain"

    from_label = resolve_hi_dose(
        extract_hi_table(
            text=ATOMOXETINE_HI + " " + ATOMOXETINE_ADULT,
            citation=ATOMOXETINE_CITE,
        ),
        "B",
    )
    assert from_label["status"] == "ok", from_label
    assert from_label["adult_dose_mg_per_day"] == 40.0, from_label  # 50% of 80 mg target

    user = resolve_hi_dose(table, "B", user_adult_dose_mg_per_day=60)
    assert user["status"] == "ok" and user["adult_dose_mg_per_day"] == 30.0, user
    print("  hi resolve: label dose / user override / fold-only abstain  OK")


def test_indication_stratified_rows_must_match_or_abstain():
    text = (
        "For pulmonary arterial hypertension: in moderate hepatic impairment "
        "(Child-Pugh B) the recommended dose is 62.5 mg per day. "
        "For digital ulcers: do not use in hepatic impairment."
    )
    table = extract_hi_table(
        text=text,
        citation="Bosentan-style SmPC HI table.",
        indication="pulmonary arterial hypertension",
    )
    ok = resolve_hi_dose(table, "B", indication="pulmonary arterial hypertension")
    assert ok["status"] == "ok" and ok["adult_dose_mg_per_day"] == 62.5, ok

    miss = resolve_hi_dose(table, "B", indication="digital ulcers")
    assert miss["status"] == "abstain", miss

    none = resolve_hi_dose(table, "B", indication=None)
    assert none["status"] == "abstain", none

    try:
        extract_hi_table(
            text=text,
            citation="Bosentan-style SmPC HI table.",
            indication="community acquired pneumonia",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("unmatched stratified indication must not yield a table")
    print("  hi resolve: indication-stratified match or abstain  OK")


def test_resolver_is_single_implementation():
    import engine.hi_table as mod
    src = inspect.getsource(mod)
    assert src.count("def resolve_hi_dose") == 1
    assert "hepatic_function_fraction" not in src
    from engine import child_pugh
    assert not hasattr(child_pugh, "resolve_hi_dose")
    print("  hi resolve: single implementation, no invented OF  OK")


def test_live_extract_from_openfda_style_label():
    from engine.hi_table import maybe_extract_hi_table

    table = maybe_extract_hi_table(
        {
            "drug": "atomoxetine",
            "dosage_and_administration": ATOMOXETINE_HI + " " + ATOMOXETINE_ADULT,
            "warnings": "See hepatic impairment dosing.",
        },
        drug="atomoxetine",
    )
    assert table is not None
    assert table["excerpt"]
    assert "openFDA" in table["citation"]
    assert table["classes"]["B"]["kind"] == "fold"
    assert table["classes"]["B"]["value"] == 0.5

    none = maybe_extract_hi_table(
        {"dosage_and_administration": "Use with caution in hepatic impairment."},
        drug="x",
    )
    assert none is None
    print("  hi extract: live label fill / caution-only None  OK")


def test_non_hepatic_severity_is_not_a_citation():
    from engine.hi_table import maybe_extract_hi_table

    try:
        extract_hi_table(
            text="Do not use in severe renal impairment. Typical adult dose is 100 mg per day.",
            citation="Label renal warning.",
        )
    except ValueError as e:
        assert "not a citation" in str(e).lower()
    else:
        raise AssertionError("renal-only severity must not become an HI table")

    mixed = maybe_extract_hi_table(
        {
            "warnings": "Do not use in severe renal impairment.",
            "dosage_and_administration": ATOMOXETINE_HI,
        },
        drug="atomoxetine",
    )
    assert mixed is not None
    assert mixed["classes"]["C"]["kind"] == "fold"
    assert mixed["classes"]["C"]["value"] == 0.25
    print("  hi extract: non-hepatic severity ignored  OK")


def test_both_facades_share_resolve_hi_dose():
    from engine.hi_table import apply_hi_resolution

    table = extract_hi_table(
        text=ATOMOXETINE_HI + " " + ATOMOXETINE_ADULT,
        citation=ATOMOXETINE_CITE,
    )
    ped = apply_hi_resolution(
        {"calculator_mode": "pediatric", "child_pugh": "B"}, table
    )
    adult = apply_hi_resolution(
        {"calculator_mode": "adult_hi", "child_pugh": "B"}, table
    )
    assert ped["status"] == adult["status"] == "ok"
    assert ped["adult_dose_mg_per_day"] == adult["adult_dose_mg_per_day"] == 40.0
    print("  hi resolve: both facades share one resolver  OK")


def test_retrieval_attaches_live_hi_table():
    from retrieval import _attach_live_hi_table

    dossier = {"cl_adult_l_h": 1.0, "vd_adult_l": 2.0}
    out = _attach_live_hi_table(
        dossier,
        {"dosage_and_administration": ATOMOXETINE_HI + " " + ATOMOXETINE_ADULT},
        "atomoxetine",
        None,
    )
    assert out["hi_table"]["classes"]["C"]["value"] == 0.25
    assert dossier.get("hi_table") is None  # original not mutated

    invented = _attach_live_hi_table(
        {"hi_table": {"classes": {"B": {"kind": "fold", "value": 0.1}}}},
        {"dosage_and_administration": "Use with caution in hepatic impairment."},
        "x",
        None,
    )
    assert invented["hi_table"] is None
    print("  hi extract: retrieval attach live table  OK")


def test_compute_uses_shared_hi_resolver():
    from agents.agent import _build_compute, _normalize_case

    table = extract_hi_table(
        text=ATOMOXETINE_HI + " " + ATOMOXETINE_ADULT,
        citation=ATOMOXETINE_CITE,
    )
    case = _normalize_case({
        "drug": "atomoxetine", "age_years": 10, "weight_kg": 30,
        "hepatic_impairment": True, "child_pugh": "B",
    })
    state = {
        "pk_ok": True, "pk_block_reason": None, "blocked_reason": None,
        "last_compute_renal_frac": None,
        "last_dossier": {
            "cl_adult_l_h": 20.0, "vd_adult_l": 70.0, "fm": {"cyp3a4": 0.9},
            "typical_adult_dose_mg_per_day": 80.0,
            "hi_table": table,
        },
    }
    out = _build_compute(case, state)({
        "drug": "atomoxetine", "weight_kg": 30, "cl_adult_l_h": 20,
        "vd_adult_l": 70, "fm": {"cyp3a4": 0.9}, "age_years": 10,
        "adult_dose_mg_per_day": 80,
    })
    assert not out.get("error"), out
    assert state["last_hi_resolution"]["adult_dose_mg_per_day"] == 40.0
    print("  hi resolve: compute path uses shared resolver  OK")

if __name__ == "__main__":
    print("HI table extract + resolve (issue #3):")
    test_extract_fills_per_class_contract_with_excerpt_and_citation()
    test_caution_only_or_missing_excerpt_is_not_a_citation()
    test_mild_moderate_severe_maps_to_abc_and_is_flagged()
    test_no_adjustment_necessary_is_fold_one()
    test_missing_a_is_fold_one_missing_b_uses_c_else_abstain()
    test_missing_c_uses_moderate_else_abstain()
    test_user_adult_dose_overrides_label_fold_only_without_dose_abstains()
    test_indication_stratified_rows_must_match_or_abstain()
    test_resolver_is_single_implementation()
    test_live_extract_from_openfda_style_label()
    test_non_hepatic_severity_is_not_a_citation()
    test_both_facades_share_resolve_hi_dose()
    test_retrieval_attaches_live_hi_table()
    test_compute_uses_shared_hi_resolver()
    print("All HI-table tests passed.")
