#!/usr/bin/env python3
"""Run live agent cases against validation_set oracles. Harness-only — not imported by backend."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")

from mechanism_score import score_mechanism  # noqa: E402
from agent import run_case  # noqa: E402

VSET = Path(__file__).resolve().parent
DRUGS = json.loads((VSET / "drug_data.json").read_text())["drugs"]
GUIDE = json.loads((VSET / "guideline_data.json").read_text())
SCENARIOS = GUIDE["scenarios"]
RESULT = ROOT / "result.md"

BAND_STRICT = (0.67, 1.5)
BAND_WIDE = (0.5, 2.0)


def _case(drug: str, scenario_key: str) -> dict:
    meta = SCENARIOS[scenario_key]["case"]
    c = {"drug": drug, "indication": DRUGS[drug].get("indication"), **meta}
    return c


def _score_mech(drug: str, rec: dict) -> dict:
    truth = {
        "elimination": DRUGS[drug]["elimination"],
        "pathways": DRUGS[drug]["pathways"],
        "enzymes": DRUGS[drug]["enzymes"],
        "transporters": DRUGS[drug]["transporters"],
        "active_metabolites": DRUGS[drug]["active_metabolites"],
        "protein_binding_percent": DRUGS[drug]["protein_binding_percent"],
    }
    mech = (rec or {}).get("mechanism") or {}
    return score_mechanism(mech, truth)


def _concordance(drug: str, scenario_key: str, dose: float | None) -> dict:
    g = GUIDE["drugs"][drug]["scenario_doses_mg_per_kg_per_day"][scenario_key]
    if dose is None or not g:
        return {"guideline": g, "ratio": None, "in_0.67_1.5": False, "in_0.5_2": False}
    ratio = dose / g
    return {
        "guideline": g,
        "ratio": round(ratio, 3),
        "in_0.67_1.5": BAND_STRICT[0] <= ratio <= BAND_STRICT[1],
        "in_0.5_2": BAND_WIDE[0] <= ratio <= BAND_WIDE[1],
    }


def run_one(drug: str, scenario_key: str) -> dict:
    case = _case(drug, scenario_key)
    t0 = time.time()
    out = run_case(case, on_step=lambda s: print(f"    · {s[:100]}", flush=True))
    dt = time.time() - t0
    rec = out.get("recommendation") or {}
    dose = rec.get("final_dose_mg_per_kg_per_day")
    conc = _concordance(drug, scenario_key, dose)
    mech = _score_mech(drug, rec) if rec else {}
    flags = rec.get("flags") or []
    return {
        "drug": drug,
        "scenario": scenario_key,
        "seconds": round(dt, 1),
        "grade": rec.get("grade"),
        "dose_mg_per_kg_per_day": dose,
        "concordance": conc,
        "mechanism_score": mech,
        "flags": flags,
        "citations_n": len(rec.get("citations") or []),
        "has_rationale": bool(rec.get("rationale")),
        "error": out.get("error"),
        "usage": out.get("usage"),
        "case": case,
        "recommendation": rec,
    }


def append_result(rows: list[dict]) -> None:
    lines: list[str] = []
    if not RESULT.exists():
        lines.append("# PaedScale validation results\n")
        lines.append(f"Branch: `validation-eval`. Started {datetime.now(timezone.utc).isoformat()}\n")
        lines.append("Harness-only. Never merge this branch to master.\n")
    for r in rows:
        lines.append(f"\n## {r['drug']} · `{r['scenario']}`\n")
        if r.get("error"):
            lines.append(f"- **ERROR:** {r['error']}\n")
        lines.append(
            f"- **Grade:** {r.get('grade')} · **Dose:** {r.get('dose_mg_per_kg_per_day')} "
            f"mg/kg/day · **{r['seconds']}s**\n"
        )
        c = r["concordance"]
        lines.append(
            f"- **Concordance:** guideline {c['guideline']} · ratio {c['ratio']} · "
            f"0.67–1.5×: {'PASS' if c['in_0.67_1.5'] else 'FAIL'} · "
            f"0.5–2×: {'PASS' if c['in_0.5_2'] else 'FAIL'}\n"
        )
        ms = r.get("mechanism_score") or {}
        if ms:
            dims = {k: v for k, v in ms.items() if k != "overall"}
            lines.append(f"- **Mechanism score:** {ms.get('overall')} · dims: `{dims}`\n")
        lines.append(f"- **Citations:** {r.get('citations_n')} · rationale: {r.get('has_rationale')}\n")
        if r.get("flags"):
            lines.append("- **Flags:**\n")
            for f in r["flags"][:12]:
                lines.append(f"  - {f}\n")
        g = r.get("recommendation") or {}
        if g.get("grade_rationale"):
            lines.append(f"- **Grade rationale:** {g['grade_rationale'][:400]}\n")
    prev = RESULT.read_text() if RESULT.exists() else ""
    RESULT.write_text(prev + "".join(lines))


def main():
    drugs = sys.argv[1:] or ["vancomycin", "midazolam", "morphine"]
    scenario_keys = list(SCENARIOS.keys())
    all_rows = []
    for drug in drugs:
        if drug not in DRUGS:
            print(f"skip unknown drug {drug}")
            continue
        for sk in scenario_keys:
            print(f"\n=== {drug} / {sk} ===", flush=True)
            try:
                row = run_one(drug, sk)
            except Exception as e:
                row = {
                    "drug": drug, "scenario": sk, "seconds": 0, "grade": None,
                    "dose_mg_per_kg_per_day": None,
                    "concordance": _concordance(drug, sk, None),
                    "mechanism_score": {}, "flags": [], "citations_n": 0,
                    "has_rationale": False, "error": str(e), "usage": {},
                    "recommendation": {},
                }
            all_rows.append(row)
            print(
                f"  → grade={row.get('grade')} dose={row.get('dose_mg_per_kg_per_day')} "
                f"ratio={row['concordance'].get('ratio')} t={row['seconds']}s",
                flush=True,
            )
            append_result([row])
    # summary block
    with RESULT.open("a") as f:
        f.write("\n### Batch summary\n")
        n = len(all_rows)
        s = sum(1 for r in all_rows if r["concordance"].get("in_0.67_1.5"))
        w = sum(1 for r in all_rows if r["concordance"].get("in_0.5_2"))
        f.write(f"- n={n} · within 0.67–1.5×: {s}/{n} · within 0.5–2×: {w}/{n}\n")
        f.write(f"- finished {datetime.now(timezone.utc).isoformat()}\n")
    print("\nWrote", RESULT)


if __name__ == "__main__":
    main()
