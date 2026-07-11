"""End-to-end agent eval. Needs ANTHROPIC_API_KEY (and, once WS3 lands, network for live
retrieval). Reports per case: graded recommendation, concordance ratio, MECHANISTIC score
(vs mechanism_truth.json), flags, latency, tokens, estimated cost. Then headline aggregates.

Run:  python test_agent.py            # representative subset
      python test_agent.py --full     # every eval drug (costs more)
"""

import json
import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

from agent import ORCHESTRATOR_MODEL, run_case  # noqa: E402
from mechanism_score import DIMENSIONS, load_truth, score_mechanism  # noqa: E402

BAND_HI, BAND_LO = 1.5, 0.67
with open(os.path.join(os.path.dirname(__file__), "eval_data", "guidelines.json")) as _f:
    GUIDELINES = json.load(_f)["drugs"]


def guideline_dose(drug: str, age_years: float):
    """Oracle pediatric guideline dose (mg/kg/day) — the harness scores the agent's LIVE dose
    against this fixed answer key; the agent itself never reads it."""
    d = GUIDELINES.get(drug.lower())
    if not d:
        return None
    pop = next((p for p in d["populations"]
                if p["age_years_min"] <= age_years <= p["age_years_max"]), None)
    return pop["dose_mg_per_kg_per_day"] if pop else None

# List price (USD per 1M tokens): input, output. Web search is $10 / 1000 searches.
PRICE = {"claude-opus-4-8": (5.0, 25.0), "claude-sonnet-5": (3.0, 15.0)}
WEB_SEARCH_USD = 0.04  # ~up to 4 searches/query at $0.01 each

# Representative subset: one per archetype + the edge cases (oral F, time>MIC, impairment).
CASES = [
    {"drug": "midazolam", "indication": "ICU sedation", "age_years": 6, "weight_kg": 20},
    {"drug": "vancomycin", "indication": "sepsis", "age_years": 6, "weight_kg": 20,
     "renal_impairment": True},                                   # edge: renal impairment
    {"drug": "morphine", "indication": "post-op analgesia", "age_years": 6, "weight_kg": 20},
    {"drug": "gentamicin", "indication": "gram-negative sepsis", "age_years": 6, "weight_kg": 20},
    {"drug": "ampicillin", "indication": "neonatal sepsis", "age_years": 6, "weight_kg": 20},  # time>MIC
    {"drug": "clindamycin", "indication": "skin/soft-tissue infection", "age_years": 6,
     "weight_kg": 20, "route": "oral"},                           # edge: oral bioavailability
]
FULL_EXTRA = [
    {"drug": "amikacin", "indication": "resistant gram-negative", "age_years": 6, "weight_kg": 20},
    {"drug": "fentanyl", "indication": "procedural analgesia", "age_years": 6, "weight_kg": 20},
]


def est_cost(usage):
    pin, pout = PRICE.get(usage["model"], (5.0, 25.0))
    cr = usage.get("cache_read_input_tokens", 0)
    cw = usage.get("cache_creation_input_tokens", 0)
    # uncached input at full rate; cache reads ~0.1x; cache writes ~1.25x
    cost = (usage["input_tokens"] / 1e6 * pin
            + cr / 1e6 * pin * 0.1
            + cw / 1e6 * pin * 1.25
            + usage["output_tokens"] / 1e6 * pout)
    # retrieval subagent runs on the cheaper model — roll its tokens into the query cost
    rpin, rpout = PRICE.get(usage.get("retrieval_model", ""), (3.0, 15.0))
    cost += (usage.get("retrieval_input_tokens", 0) / 1e6 * rpin
             + usage.get("retrieval_output_tokens", 0) / 1e6 * rpout)
    return cost


def main():
    cases = CASES + (FULL_EXTRA if "--full" in sys.argv else [])
    truth = load_truth()["drugs"]
    print(f"Model: {ORCHESTRATOR_MODEL}   cases: {len(cases)}\n" + "=" * 72)
    grand_cost = 0.0
    dim_hits = {d: 0 for d in DIMENSIONS}
    mech_scores, n_scored = [], 0
    conc_hits = conc_n = 0
    latencies = []

    for case in cases:
        print(f"\n### {case['drug'].upper()}  (age {case['age_years']}y, {case['weight_kg']}kg"
              f"{', ' + case['route'] if case.get('route') else ''}"
              f"{', renal-impaired' if case.get('renal_impairment') else ''})")
        t0 = time.time()
        out = run_case(case, on_step=lambda s: print("  ·", s[:110]))
        dt = time.time() - t0
        r = out.get("recommendation")
        u = out["usage"]
        cost = est_cost(u) + WEB_SEARCH_USD
        grand_cost += cost
        if not r:
            print("  !! no recommendation:", out.get("error"))
            continue
        latencies.append(dt)
        print(f"\n  DOSE  {r.get('final_dose_mg_per_kg_per_day')} mg/kg/day  "
              f"({r.get('interval','')} {r.get('route','')})   GRADE {r.get('grade')}")

        # ---- concordance vs the ORACLE (harness scores the agent's LIVE dose) --
        gd = guideline_dose(case["drug"], case["age_years"])
        est = r.get("final_dose_mg_per_kg_per_day")
        if gd and est:
            ratio = est / gd
            ok = BAND_LO <= ratio <= BAND_HI
            conc_hits += ok
            conc_n += 1
            print(f"  CONC  est={est} vs oracle guideline={gd} mg/kg/day  "
                  f"ratio={ratio:.2f}  {'PASS' if ok else 'CHECK'}")
        elif gd is None:
            print("  CONC  no oracle guideline for this drug/age")

        # ---- mechanistic reasoning score --------------------------------------
        t = truth.get(case["drug"].lower())
        if t:
            ms = score_mechanism(r.get("mechanism", {}), t)
            n_scored += 1
            mech_scores.append(ms["overall"])
            for d in DIMENSIONS:
                dim_hits[d] += 1 if ms[d] else 0
            missed = [d for d in DIMENSIONS if not ms[d]]
            print(f"  MECH  {ms['overall']*100:.0f}%  "
                  + ("all dimensions correct" if not missed else "missed: " + ", ".join(missed)))
        print(f"  FLAGS {r.get('flags')}")
        print(f"  TIME  {dt:.1f}s   TOKENS in {u['input_tokens']} / out {u['output_tokens']}"
              f"   CACHE read {u.get('cache_read_input_tokens',0)} / write {u.get('cache_creation_input_tokens',0)}"
              f"   ~${cost:.3f}")

    # ---- headline aggregates --------------------------------------------------
    print("\n" + "=" * 72)
    if conc_n:
        print(f"CONCORDANCE (vs oracle, 0.67x-1.5x band) — {conc_hits}/{conc_n} within band")
    if n_scored:
        print(f"MECHANISTIC REASONING — mean {sum(mech_scores)/n_scored*100:.0f}% "
              f"over {n_scored} drugs")
        for d in DIMENSIONS:
            print(f"    {d:20s} {dim_hits[d]}/{n_scored} correct")
    if latencies:
        print(f"LATENCY — mean {sum(latencies)/len(latencies):.0f}s, "
              f"max {max(latencies):.0f}s  (budget <60s each)")
    print(f"COST — total ~${grand_cost:.3f} over {len(cases)} queries "
          f"(~${grand_cost/max(1,len(cases)):.3f}/query; budget <$1 each)")


if __name__ == "__main__":
    main()
