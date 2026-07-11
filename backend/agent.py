"""
PaedScale — Claude orchestration layer.

Claude sits in the pharmacometric-expert seat: it maps the drug to its elimination
pathways and fm-split (cite-or-abstain), assembles adult PK, calls the deterministic PK
engine, retrieves the guideline dose for a concordance check, and emits a graded, cited
recommendation with explicit assumptions, uncertainty, and safety flags.

Requires ANTHROPIC_API_KEY. The deterministic engine (pk_engine.py) needs no key and is
tested separately in test_pk.py.
"""

from __future__ import annotations

import json
import os

from anthropic import Anthropic

import retrieval
from pk_engine import compute_pediatric_dose, result_to_dict

ORCHESTRATOR_MODEL = os.environ.get("ORCHESTRATOR_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.environ.get("PAEDSCALE_MAX_TOKENS", "4000"))

SYSTEM = """You are PaedScale, a pediatric dose-extrapolation agent. You derive a defensible
STARTING dose for a child from adult pharmacokinetics using allometry × organ maturation
(Anderson–Holford). You are decision support for a qualified clinician, NOT a prescriber.

Your job, in order:
1. Identify the MECHANISM and record it in submit_recommendation.mechanism (this is scored):
   - elimination: renal / hepatic / mixed
   - pathways: the fm-split over engine keys renal_gfr, cyp3a4, ugt2b7
   - enzymes (e.g. CYP3A4, UGT2B7), transporters (e.g. P-gp), active_metabolites (e.g. M6G),
     and protein_binding_percent.
   Correct-negatives count: if the drug has no transporter or no active metabolite, return an
   EMPTY list — do NOT invent one to look thorough. Every claim still obeys cite-or-abstain.
2. RETRIEVE LIVE, then CITE-OR-ABSTAIN: call retrieve_drug_data(drug, indication) FIRST — it
   runs a retrieval subagent over PubMed + openFDA and returns a CITED adult-PK + mechanism
   dossier. This is your ONLY source of drug PK — there is no hardcoded fallback. Use its
   values for the compute step and to fill the mechanism object. If a required value (clearance,
   Vd, fm) came back null, do NOT invent it: you cannot compute a defensible dose — grade D and
   abstain from a point estimate. If source_mode is "unavailable", retrieval failed — grade D.
3. Call compute_pediatric_dose with the retrieved adult PK, the child's covariates, and the
   fm-split. The Python engine does the deterministic math — you do the judgment.
4. Retrieve the pediatric GUIDELINE dose with web_search and run a CONCORDANCE check: is your
   estimate within 0.67x–1.5x of the guideline? Report the ratio. (No guideline found → grade B.)
5. Grade the recommendation:
   A = mechanistic estimate passes concordance against a real guideline.
   B = solid retrieved PK, plausible estimate, but no guideline to check against.
   C = sparse/uncertain PK; estimate is directional only.
   D = insufficient data or a safety stop — do not recommend a number.
6. Flag: narrow-therapeutic-index drugs (recommend TDM), active metabolites, data gaps,
   the "assumed term" caveat if PMA was unknown, and the exposure-matching assumption
   (matching adult exposure assumes pediatric PD target = adult).

Finish by calling submit_recommendation exactly once with the structured result. Keep
reasoning lean — do not pad. Never exceed the toxic dose or drop below the effective dose
without flagging it prominently."""


# --------------------------------------------------------------------------- tools
TOOLS = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        # The orchestrator's own search is reserved for the pediatric GUIDELINE dose (for the
        # concordance check). Drug PK comes from retrieve_drug_data, not from here.
        "max_uses": 2,
    },
    {
        "name": "retrieve_drug_data",
        "description": "Run the LIVE retrieval subagent (PubMed E-utilities + openFDA on a "
                       "cheaper model) to get a CITED adult-PK + mechanism dossier. Call this "
                       "FIRST and base the compute + mechanism on it — it is the ONLY source of "
                       "drug PK (no hardcoded fallback). Returns source_mode='live' or "
                       "'unavailable' (retrieval failed → abstain).",
        "input_schema": {
            "type": "object",
            "properties": {"drug": {"type": "string"}, "indication": {"type": "string"}},
            "required": ["drug"],
        },
    },
    {
        "name": "compute_pediatric_dose",
        "description": "Deterministic PK engine. Applies allometry (WT^0.75) × Anderson–Holford "
                       "maturation per pathway to adult PK, returns child clearance/volume/half-life "
                       "and the solved dose. Pathway keys must be renal_gfr, cyp3a4, or ugt2b7.",
        "input_schema": {
            "type": "object",
            "properties": {
                "drug": {"type": "string"},
                "weight_kg": {"type": "number"},
                "cl_adult_l_h": {"type": "number", "description": "adult total clearance, L/h, 70kg ref"},
                "vd_adult_l": {"type": "number", "description": "adult volume of distribution, L"},
                "fm": {
                    "type": "object",
                    "description": "pathway key -> fraction of clearance, e.g. {\"renal_gfr\": 0.9}",
                    "additionalProperties": {"type": "number"},
                },
                "target_metric": {"type": "string", "enum": ["css", "auc", "cmax", "time_mic"]},
                "age_years": {"type": "number"},
                "pma_weeks": {"type": "number", "description": "postmenstrual age in weeks, if known"},
                "gestational_age_weeks": {"type": "number"},
                "postnatal_age_weeks": {"type": "number"},
                "adult_dose_mg_per_day": {"type": "number"},
                "adult_interval_h": {"type": "number"},
                "renal_function_fraction": {"type": "number", "description": "1.0 normal; <1 impaired"},
                "hepatic_function_fraction": {"type": "number"},
                "toxic_dose_mg_per_kg_per_day": {"type": "number"},
                "effective_dose_mg_per_kg_per_day": {"type": "number"},
                "route": {"type": "string", "enum": ["iv", "oral"],
                          "description": "child route; oral applies the bioavailability correction"},
                "oral_bioavailability": {"type": "number", "description": "F for oral route (0,1]"},
            },
            "required": ["drug", "weight_kg", "cl_adult_l_h", "vd_adult_l", "fm"],
        },
    },
    {
        "name": "submit_recommendation",
        "description": "Emit the final structured recommendation. Call exactly once, last.",
        "input_schema": {
            "type": "object",
            "properties": {
                "final_dose_mg_per_kg_per_day": {"type": ["number", "null"]},
                "final_dose_mg_per_day": {"type": ["number", "null"]},
                "route": {"type": "string"},
                "interval": {"type": "string"},
                "mechanism": {
                    "type": "object",
                    "description": "Structured mechanism identification — scored against the "
                                   "answer key. Empty lists mean a deliberate correct-negative "
                                   "(e.g. no transporter); do NOT invent entries to look thorough.",
                    "properties": {
                        "elimination": {"type": "string", "enum": ["renal", "hepatic", "mixed"]},
                        "pathways": {"type": "array", "items": {"type": "string"},
                                     "description": "engine fm keys: renal_gfr, cyp3a4, ugt2b7"},
                        "enzymes": {"type": "array", "items": {"type": "string"},
                                    "description": "e.g. CYP3A4, UGT2B7; [] if none"},
                        "transporters": {"type": "array", "items": {"type": "string"},
                                         "description": "e.g. P-gp; [] if none"},
                        "active_metabolites": {"type": "array", "items": {"type": "string"},
                                               "description": "e.g. M6G; [] if none"},
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
                "rationale": {"type": "string", "description": "markdown, cited, concise"},
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


# --------------------------------------------------------------------------- tool impls
def _compute(args: dict) -> dict:
    try:
        r = compute_pediatric_dose(**args)
        return result_to_dict(r)
    except Exception as e:  # surface engine refusals (e.g. unknown pathway) to the model
        return {"error": str(e)}


LOCAL_TOOLS = {
    "compute_pediatric_dose": _compute,
}


# --------------------------------------------------------------------------- run loop
def run_case(case: dict, on_step=None, max_turns: int = 12) -> dict:
    """Run one dosing case end-to-end. `case` is a dict of user inputs.

    on_step(text) is an optional callback for streaming one-line reasoning to the UI.
    Returns {"recommendation": {...}, "trace": [...], "usage": {...}}.
    """
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    user_msg = (
        "Dose this case. Follow your pipeline and finish with submit_recommendation.\n\n"
        f"Case: {json.dumps(case)}"
    )
    messages = [{"role": "user", "content": user_msg}]
    trace: list[str] = []
    in_tok = out_tok = cache_read = cache_write = 0
    retr_in = retr_out = 0  # retrieval-subagent tokens, rolled up for cost accounting

    for _ in range(max_turns):
        resp = client.messages.create(
            model=ORCHESTRATOR_MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
            # Prompt caching: auto-places one breakpoint on the last cacheable block, so the
            # static tools+system prefix AND the growing tool/web-search history are read from
            # cache (~0.1x) on every tool-loop turn after the first, instead of re-billed in full.
            cache_control={"type": "ephemeral"},
        )
        in_tok += resp.usage.input_tokens
        out_tok += resp.usage.output_tokens
        cache_read += getattr(resp.usage, "cache_read_input_tokens", 0) or 0
        cache_write += getattr(resp.usage, "cache_creation_input_tokens", 0) or 0

        # collect assistant text (the "one-line reasoning") + tool calls
        tool_uses = []
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                trace.append(block.text.strip())
                if on_step:
                    on_step(block.text.strip())
            elif block.type == "tool_use":
                tool_uses.append(block)
            elif block.type == "server_tool_use" and getattr(block, "name", "") == "web_search":
                # web_search runs API-side (no local handler), so surface it here for the UI:
                # this is the pediatric-guideline lookup for the concordance check.
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
                    on_step(f"→ {tu.name}({', '.join(f'{k}={v}' for k, v in list(tu.input.items())[:3])} …)")
                out = LOCAL_TOOLS[tu.name](tu.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(out),
                })
            # web_search is a server tool: executed by the API, no local handling needed.
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
