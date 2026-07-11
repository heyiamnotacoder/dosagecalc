"""
Deterministic PK-engine tests + concordance check against guidelines.json.

Runs with NO API key — this exercises the scientific core (the math that must be exactly
right) and scores it against the hand-reviewed guideline doses. The Claude reasoning layer
is tested separately in test_agent.py (which does need a key).

Run:  python test_pk.py
"""

import json
import os

from pk_engine import compute_pediatric_dose, maturation_factor

HERE = os.path.dirname(__file__)
EVAL = os.path.join(HERE, "eval_data")
BAND_HI, BAND_LO = 1.5, 0.67  # concordance band

# The reviewed adult-PK oracle (moved out of production code) — the harness reads it to feed
# the deterministic engine and score it. The product agent never touches this.
with open(os.path.join(EVAL, "drug_pk.json")) as _f:
    DRUG_SEED = json.load(_f)["drugs"]


def _seed_dose(drug: str, weight_kg: float, age_years: float, adult_dose_mg_per_day):
    s = DRUG_SEED[drug]
    return compute_pediatric_dose(
        drug=drug,
        weight_kg=weight_kg,
        cl_adult_l_h=s["cl_adult_l_h"],
        vd_adult_l=s["vd_adult_l"],
        fm=s["fm"],
        target_metric=s["target_metric"],
        age_years=age_years,
        adult_dose_mg_per_day=adult_dose_mg_per_day,
    )


def test_maturation_monotonic():
    """Maturation must rise with PMA and approach 1 in adulthood."""
    mf_neo = maturation_factor(40, 47.7, 3.40)      # term neonate, renal
    mf_1yr = maturation_factor(40 + 52, 47.7, 3.40)
    mf_adult = maturation_factor(40 * 52, 47.7, 3.40)
    assert mf_neo < mf_1yr < mf_adult, (mf_neo, mf_1yr, mf_adult)
    assert 0.95 <= mf_adult <= 1.001, mf_adult
    assert mf_neo < 0.6, mf_neo  # a term neonate clears renally well below adult/kg
    print(f"  maturation renal: neonate={mf_neo:.2f} 1yr={mf_1yr:.2f} adult={mf_adult:.2f}  OK")


def test_neonate_clears_below_linear():
    """A neonate's clearance fraction of adult must sit well below the naive mg/kg line."""
    # 3.5 kg term neonate on vancomycin (renal)
    r = _seed_dose("vancomycin", weight_kg=3.5, age_years=0.02, adult_dose_mg_per_day=2000)
    # naive linear mg/kg would give child CL fraction = (3.5/70) = 0.05 of adult;
    # allometry+maturation must give LESS (immature GFR) per-kg, i.e. lower mg/kg than adult.
    adult_mg_per_kg = 2000 / 70
    assert r.recommended_dose_mg_per_kg_per_day < adult_mg_per_kg, (
        r.recommended_dose_mg_per_kg_per_day, adult_mg_per_kg
    )
    print(f"  neonate vancomycin: {r.recommended_dose_mg_per_kg_per_day:.1f} mg/kg/day "
          f"(CL {r.cl_fraction_of_adult:.1%} of adult, t1/2 {r.half_life_h:.1f} h)  OK")


def test_refuses_unknown_pathway():
    try:
        compute_pediatric_dose(
            drug="mystery", weight_kg=10, cl_adult_l_h=10, vd_adult_l=50,
            fm={"not_a_real_pathway": 1.0}, age_years=1,
        )
    except ValueError as e:
        assert "maturation curve" in str(e)
        print("  refuses to invent a maturation curve for unknown pathway  OK")
        return
    raise AssertionError("should have refused unknown pathway")


def test_new_pathways_accepted():
    """Expanded MATURATION keys must be callable (cyp1a2, cyp2d6, …)."""
    from constants import MATURATION
    for key in ("cyp1a2", "cyp2d6", "cyp2c9", "cyp2c19", "ugt1a1"):
        assert key in MATURATION, key
        r = compute_pediatric_dose(
            drug="probe", weight_kg=10, cl_adult_l_h=20, vd_adult_l=50,
            fm={key: 1.0}, age_years=1, adult_dose_mg_per_day=100,
        )
        assert r.cl_child_l_h > 0 and r.pathways[0].pathway == key
    print(f"  new pathways accepted: cyp1a2/2d6/2c9/2c19, ugt1a1  OK")


def test_pk_cache():
    from pk_cache import PkCache
    c = PkCache(max_entries=2, max_bytes=50_000, ttl_seconds=3600)
    d = {"cl_adult_l_h": 5.0, "vd_adult_l": 20.0, "fm": {"renal_gfr": 1.0}}
    assert c.set("gentamicin", "sepsis", d, "live")
    hit = c.get("gentamicin", "sepsis")
    assert hit and hit["dossier"]["cl_adult_l_h"] == 5.0
    assert c.set("vanco", None, d, "live")
    assert c.set("amikacin", None, d, "live")  # evicts oldest
    assert c.get("gentamicin", "sepsis") is None  # LRU evicted
    assert not c.set("x", None, d, "unavailable")
    print("  pk_cache: LRU + reject unavailable  OK")


def test_edge_cases():
    from edge_cases import assess_edge_cases
    # prodrug
    r = assess_edge_cases({"drug": "codeine", "age_years": 6, "weight_kg": 20}, {})
    assert any("PRODRUG" in f for f in r["flags"]), r
    # obesity
    r2 = assess_edge_cases({"drug": "midazolam", "age_years": 1.0, "weight_kg": 14}, {})
    assert any("OBESITY" in f for f in r2["flags"]), r2
    assert "dosing_weight_kg_hint" in r2["adjustments"]
    # high PB + neonate
    r3 = assess_edge_cases(
        {"drug": "midazolam", "age_years": 0.05, "weight_kg": 3.5},
        {"protein_binding_percent": 97},
    )
    assert any("PROTEIN BINDING" in f for f in r3["flags"]), r3
    # renal
    r4 = assess_edge_cases(
        {"drug": "vanco", "age_years": 6, "weight_kg": 20, "renal_impairment": True}, {}
    )
    assert any("RENAL" in f for f in r4["flags"]), r4
    # no false positive on lean child
    r5 = assess_edge_cases({"drug": "vancomycin", "age_years": 6, "weight_kg": 20},
                           {"protein_binding_percent": 50})
    assert not any("OBESITY" in f for f in r5["flags"])
    print("  edge_cases: prodrug/obesity/PB/renal  OK")


def test_oral_bioavailability():
    """Oral route must inflate the administered dose by 1/F vs the IV-equivalent."""
    s = DRUG_SEED["ampicillin"]  # F ~ 0.40
    common = dict(
        drug="ampicillin", weight_kg=20, cl_adult_l_h=s["cl_adult_l_h"],
        vd_adult_l=s["vd_adult_l"], fm=s["fm"], target_metric=s["target_metric"],
        age_years=6, adult_dose_mg_per_day=s["typical_adult_dose_mg_per_day"],
    )
    iv = compute_pediatric_dose(route="iv", **common)
    po = compute_pediatric_dose(route="oral", oral_bioavailability=0.40, **common)
    ratio = po.recommended_dose_mg_per_kg_per_day / iv.recommended_dose_mg_per_kg_per_day
    assert abs(ratio - 1 / 0.40) < 1e-6, ratio
    assert any("Oral bioavailability F applied" in w for w in po.warnings), po.warnings
    print(f"  oral F: IV={iv.recommended_dose_mg_per_kg_per_day:.1f} → "
          f"PO={po.recommended_dose_mg_per_kg_per_day:.1f} mg/kg/day (×{ratio:.2f} = 1/F)  OK")


def test_time_mic_flag():
    """A time>MIC drug must emit the fT>MIC proxy warning + a half-life-anchored interval."""
    s = DRUG_SEED["ampicillin"]
    r = compute_pediatric_dose(
        drug="ampicillin", weight_kg=20, cl_adult_l_h=s["cl_adult_l_h"],
        vd_adult_l=s["vd_adult_l"], fm=s["fm"], target_metric="time_mic",
        age_years=6, adult_dose_mg_per_day=s["typical_adult_dose_mg_per_day"],
    )
    assert any("TIME>MIC" in w for w in r.warnings), r.warnings
    assert r.suggested_interval_h is not None and r.suggested_interval_h > 0
    print(f"  time>MIC: flag present, interval anchored to t1/2 "
          f"(~{r.suggested_interval_h:.1f} h)  OK")


def test_safety_bounds_fire():
    """Passing toxic/effective thresholds must trigger the safety warnings when breached."""
    s = DRUG_SEED["amikacin"]  # cmax → child mg/kg ≈ adult mg/kg
    # Feed an absurdly high adult dose so the child mg/kg blows past the toxic bound.
    r = compute_pediatric_dose(
        drug="amikacin", weight_kg=20, cl_adult_l_h=s["cl_adult_l_h"],
        vd_adult_l=s["vd_adult_l"], fm=s["fm"], target_metric="cmax",
        age_years=6, adult_dose_mg_per_day=100.0 * 70,  # 100 mg/kg adult → child ~100
        toxic_dose_mg_per_kg_per_day=s["toxic_dose_mg_per_kg_per_day"],
        effective_dose_mg_per_kg_per_day=s["effective_dose_mg_per_kg_per_day"],
    )
    assert any("EXCEEDS the stated toxic threshold" in w for w in r.warnings), r.warnings
    print("  safety bounds: toxic-threshold breach flagged  OK")


def test_mechanism_scorer():
    """The mechanism scorer must reward a perfect answer and catch a targeted miss (no key)."""
    from mechanism_score import load_truth, score_mechanism
    truth = load_truth()["drugs"]
    assert score_mechanism(truth["vancomycin"], truth["vancomycin"])["overall"] == 1.0
    miss = score_mechanism(
        {"elimination": "renal", "pathways": ["renal_gfr"], "enzymes": ["CYP3A4"],
         "transporters": [], "active_metabolites": [], "protein_binding_percent": 50},
        truth["vancomycin"],
    )
    assert miss["enzymes"] is False and miss["elimination"] is True, miss
    print("  mechanism scorer: perfect=1.0, invented-enzyme miss caught  OK")


def concordance_check():
    """Score seed-based estimates against the guideline JSON."""
    with open(os.path.join(EVAL, "guidelines.json")) as f:
        gl = json.load(f)

    # representative test children per drug (weight_kg, age_years, adult_dose_mg_per_day)
    cases = {
        "midazolam": [(20, 6, 1.44 * 70)],   # child; adult ~0.06 mg/kg/h*70kg*24h
        "vancomycin": [(20, 6, 2000)],
        "morphine": [(20, 6, 0.48 * 70)],
        # Stage-2 drugs (adult daily dose = adult mg/kg midpoint * 70 kg):
        "gentamicin": [(20, 6, 5.0 * 70)],    # cmax-driven aminoglycoside, ~5 mg/kg adult
        "amikacin":   [(20, 6, 15.0 * 70)],   # cmax-driven aminoglycoside, ~15 mg/kg adult
        "fentanyl":   [(20, 6, 0.036 * 70)],  # css infusion, ~1.5 mcg/kg/h adult
        "ampicillin": [(20, 6, 8000)],        # css (time>MIC proxy), 2 g q6h adult
        "clindamycin":[(20, 6, 1800)],        # css, 600 mg q8h adult
    }
    print("\nConcordance vs guidelines (band 0.67x-1.5x):")
    passed = 0
    total = 0
    for drug, drug_cases in cases.items():
        pops = gl["drugs"][drug]["populations"]
        for (wt, age, adult_dose) in drug_cases:
            # find matching guideline population
            gpop = next(
                (p for p in pops if p["age_years_min"] <= age <= p["age_years_max"]), None
            )
            if not gpop:
                continue
            r = _seed_dose(drug, wt, age, adult_dose)
            est = r.recommended_dose_mg_per_kg_per_day
            ref = gpop["dose_mg_per_kg_per_day"]
            ratio = est / ref if ref else float("nan")
            ok = BAND_LO <= ratio <= BAND_HI
            passed += ok
            total += 1
            print(f"  {drug:12s} est={est:6.2f}  guideline={ref:6.2f} mg/kg/day  "
                  f"ratio={ratio:.2f}  {'PASS' if ok else 'CHECK'}")
    print(f"\n  {passed}/{total} within band "
          f"(seed PK — expect some misses; this validates the pipeline, not final numbers)")


if __name__ == "__main__":
    print("Deterministic PK-engine tests (no API key):")
    test_maturation_monotonic()
    test_neonate_clears_below_linear()
    test_refuses_unknown_pathway()
    test_new_pathways_accepted()
    test_edge_cases()
    test_pk_cache()
    test_oral_bioavailability()
    test_time_mic_flag()
    test_safety_bounds_fire()
    test_mechanism_scorer()
    concordance_check()
    print("\nAll structural tests passed.")
