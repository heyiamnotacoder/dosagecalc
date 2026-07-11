"""
PaedScale — Claude orchestration layer.

Maps drug → pathways, retrieves adult PK (subagent), runs deterministic engine,
concordance + grade. Decision support, not prescribing.

Requires ANTHROPIC_API_KEY. Engine (pk_engine.py) needs no key.
Detail lives in lean skills (backend/skills/) via load_skill — keep SYSTEM short.
"""

from __future__ import annotations

import json
import os

from anthropic import Anthropic

import retrieval
from pk_engine import compute_pediatric_dose, result_to_dict
from skills import load_skill, list_skills

ORCHESTRATOR_MODEL = os.environ.get("ORCHESTRATOR_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.environ.get("PAEDSCALE_MAX_TOKENS", "4000"))

SYSTEM = """You are PaedScale: pediatric STARTING dose from adult PK via allometry × maturation.
Decision support for a clinician — NOT a prescriber.

Pipeline (lean):
1. load_skill('mechanism') if needed → map elimination / fm / target_metric / mechanism fields.
   Empty lists for absent transporters/metabolites. Cite-or-abstain.
2. retrieve_drug_data FIRST — only PK source. Null/unavailable → grade D, no invented numbers.
3. compute_pediatric_dose with retrieved PK + child covariates (use case renal/hepatic fractions).
4. load_skill('edge_cases') + assess_edge_cases when relevant; merge flags.
5. web_search pediatric guideline → concordance 0.67×–1.5× (none → grade B).
6. Grade A/B/C/D; flag NTI→TDM, metabolites, oral-F, assumed-term, exposure-matching PD assumption.
7. submit_recommendation once, last. Lean reasoning. Flag toxic/sub-therapeutic doses."""

TOOLS = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 2,
    },
    {
        "name": "load_skill",
        "description": f"Load a lean skill. Names: {', '.join(list_skills())}.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "retrieve_drug_data",
        "description": "LIVE retrieval subagent (PubMed + openFDA). ONLY source of drug PK. "
                       "Returns source_mode live|unavailable.",
        "input_schema": {
            "type": "object",
            "properties": {"drug": {"type": "string"}, "indication": {"type": "string"}},
            "required": ["drug"],
        },
    },
    {
        "name": "compute_pediatric_dose",
        "description": "Deterministic allometry × maturation engine. fm keys must exist in MATURATION.",
        "input_schema": {
            "type": "object",
            "properties": {
                "drug": {"type": "string"},
                "weight_kg": {"type": "number"},
                "cl_adult_l_h": {"type": "number"},
                "vd_adult_l": {"type": "number"},
                "fm": {
                    "type": "object",
                    "description": "pathway -> fraction, e.g. {\"renal_gfr\": 0.9}",
                    "additionalProperties": {"type": "number"},
                },
                "target_metric": {"type": "string", "enum": ["css", "auc", "cmax", "time_mic"]},
                "age_years": {"type": "number"},
                "pma_weeks": {"type": "number"},
                "gestational_age_weeks": {"type": "number"},
                "postnatal_age_weeks": {"type": "number"},
                "adult_dose_mg_per_day": {"type": "number"},
                "adult_interval_h": {"type": "number"},
                "renal_function_fraction": {"type": "number"},
                "hepatic_function_fraction": {"type": "number"},
                "toxic_dose_mg_per_kg_per_day": {"type": "number"},
                "effective_dose_mg_per_kg_per_day": {"type": "number"},
                "route": {"type": "string", "enum": ["iv", "oral"]},
                "oral_bioavailability": {"type": "number"},
            },
            "required": ["drug", "weight_kg", "cl_adult_l_h", "vd_adult_l", "fm"],
        },
    },
    {
        "name": "assess_edge_cases",
        "description": "Deterministic flags for prodrug/obesity/protein-binding/illness. "
                       "Call after retrieve (and after compute if dose set). Merge flags.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case": {"type": "object"},
                "dossier": {"type": "object"},
                "engine_result": {"type": "object"},
            },
            "required": ["case"],
        },
    },
    {
        "name": "submit_recommendation",
        "description": "Final structured recommendation. Call exactly once, last.",
        "input_schema": {
            "type": "object",
            "properties": {
                "final_dose_mg_per_kg_per_day": {"type": ["number", "null"]},
                "final_dose_mg_per_day": {"type": ["number", "null"]},
                "route": {"type": "string"},
                "interval": {"type": "string"},
                "mechanism": {
                    "type": "object",
                    "properties": {
                        "elimination": {"type": "string", "enum": ["renal", "hepatic", "mixed"]},
                        "pathways": {"type": "array", "items": {"type": "string"}},
                        "enzymes": {"type": "array", "items": {"type": "string"}},
                        "transporters": {"type": "array", "items": {"type": "string"}},
                        "active_metabolites": {"type": "array", "items": {"type": "string"}},
                        "protein_binding_percent": {"type": ["number", "null"]},
                    },
                    "required": ["elimination", "pathways", "enzymes",
                                 "transporters", "active_metabolites"],
                },
                "grade": {"type": "string", "enum": ["A", "B", "C", "D"]},
                "grade_rationale": {"type": "string"},
                "concordance": {
                    "type": "object",
                    "properties": {
                        "guideline_dose_mg_per_kg_per_day": {"type": ["number", "null"]},
                        "ratio": {"type": ["number", "null"]},
                        "verdict": {"type": "string"},
                        "source": {"type": "string"},
                    },
                },
                "rationale": {"type": "string"},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "uncertainty": {"type": "string"},
                "flags": {"type": "array", "items": {"type": "string"}},
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"claim": {"type": "string"}, "source": {"type": "string"}},
                    },
                },
            },
            "required": ["mechanism", "grade", "grade_rationale", "rationale", "flags"],
        },
    },
]


def _compute(args: dict) -> dict:
    try:
        r = compute_pediatric_dose(**args)
        return result_to_dict(r)
    except Exception as e:
        return {"error": str(e)}


def _assess_edge_cases(args: dict) -> dict:
    try:
        from edge_cases import assess_edge_cases
        return assess_edge_cases(
            args.get("case") or {},
            args.get("dossier"),
            args.get("engine_result"),
        )
    except Exception as e:
        return {"flags": [], "adjustments": {}, "notes": [], "error": str(e)}


LOCAL_TOOLS = {
    "compute_pediatric_dose": _compute,
    "load_skill": lambda a: load_skill(a.get("name", "")),
    "assess_edge_cases": _assess_edge_cases,
}


def _normalize_case(case: dict) -> dict:
    """Map UI bools to engine organ fractions; copy so we do not mutate caller."""
    c = dict(case)
    if "renal_function_fraction" not in c:
        c["renal_function_fraction"] = 0.5 if c.get("renal_impairment") else 1.0
    if "hepatic_function_fraction" not in c:
        c["hepatic_function_fraction"] = 0.5 if c.get("hepatic_impairment") else 1.0
    # postnatal days → weeks for engine if provided
    if c.get("postnatal_age_days") is not None and c.get("postnatal_age_weeks") is None:
        try:
            c["postnatal_age_weeks"] = float(c["postnatal_age_days"]) / 7.0
        except (TypeError, ValueError):
            pass
    return c


def run_case(case: dict, on_step=None, max_turns: int = 12) -> dict:
    """Run one dosing case end-to-end."""
    case = _normalize_case(case)
    client = Anthropic()
    user_msg = (
        "Dose this case. Follow your pipeline and finish with submit_recommendation.\n\n"
        f"Case: {json.dumps(case)}"
    )
    messages = [{"role": "user", "content": user_msg}]
    trace: list[str] = []
    in_tok = out_tok = cache_read = cache_write = 0
    retr_in = retr_out = 0

    for _ in range(max_turns):
        resp = client.messages.create(
            model=ORCHESTRATOR_MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
            cache_control={"type": "ephemeral"},
        )
        in_tok += resp.usage.input_tokens
        out_tok += resp.usage.output_tokens
        cache_read += getattr(resp.usage, "cache_read_input_tokens", 0) or 0
        cache_write += getattr(resp.usage, "cache_creation_input_tokens", 0) or 0

        tool_uses = []
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                trace.append(block.text.strip())
                if on_step:
                    on_step(block.text.strip())
            elif block.type == "tool_use":
                tool_uses.append(block)
            elif block.type == "server_tool_use" and getattr(block, "name", "") == "web_search":
                q = ""
                if isinstance(getattr(block, "input", None), dict):
                    q = block.input.get("query", "")
                if on_step:
                    on_step(f"→ web_search — finding pediatric guideline{(': ' + q) if q else ' …'}")

        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            break

        tool_results = []
        for tu in tool_uses:
            if tu.name == "submit_recommendation":
                return {
                    "recommendation": tu.input,
                    "trace": trace,
                    "usage": {"input_tokens": in_tok, "output_tokens": out_tok,
                              "cache_read_input_tokens": cache_read,
                              "cache_creation_input_tokens": cache_write,
                              "retrieval_input_tokens": retr_in,
                              "retrieval_output_tokens": retr_out,
                              "retrieval_model": retrieval.RETRIEVAL_MODEL,
                              "model": ORCHESTRATOR_MODEL},
                }
            if tu.name == "retrieve_drug_data":
                if on_step:
                    on_step(f"→ retrieve_drug_data({tu.input.get('drug')}) — live PubMed/openFDA …")
                rout = retrieval.fetch(tu.input["drug"], tu.input.get("indication"))
                retr_in += rout["usage"].get("input_tokens", 0)
                retr_out += rout["usage"].get("output_tokens", 0)
                payload = {
                    "source_mode": rout["source_mode"],
                    "dossier": rout["dossier"],
                }
                tool_results.append({
                    "type": "tool_result", "tool_use_id": tu.id,
                    "content": json.dumps(payload),
                })
            elif tu.name in LOCAL_TOOLS:
                if on_step:
                    on_step(f"→ {tu.name} …")
                out = LOCAL_TOOLS[tu.name](tu.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(out),
                })
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return {
        "recommendation": None,
        "trace": trace,
        "error": "Agent did not submit a recommendation within the turn budget.",
        "usage": {"input_tokens": in_tok, "output_tokens": out_tok,
                  "cache_read_input_tokens": cache_read,
                  "cache_creation_input_tokens": cache_write,
                  "retrieval_input_tokens": retr_in,
                  "retrieval_output_tokens": retr_out,
                  "retrieval_model": retrieval.RETRIEVAL_MODEL,
                  "model": ORCHESTRATOR_MODEL},
    }


if __name__ == "__main__":
    import sys
    demo = {"drug": "vancomycin", "indication": "sepsis", "age_years": 6,
            "weight_kg": 20, "renal_impairment": False, "hepatic_impairment": False}
    if len(sys.argv) > 1:
        demo["drug"] = sys.argv[1]
    out = run_case(demo, on_step=lambda s: print("  ·", s[:120]))
    print("\n=== RECOMMENDATION ===")
    print(json.dumps(out["recommendation"], indent=2))
    print("usage:", out["usage"])
