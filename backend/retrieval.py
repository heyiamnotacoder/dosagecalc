"""
PaedScale — retrieval subagent (the cheap/fast leg of the multi-agent split).

A SEPARATE Anthropic loop on a cheaper model (default claude-sonnet-5) whose only job is to
return a structured, CITED adult-PK + mechanism dossier for one drug. It uses real retrieval
tools (PubMed E-utilities + openFDA, from retrieval_tools.py) plus web_search. The Opus
orchestrator (agent.py) calls this via the `retrieve_drug_data` tool and does the judgment.

Design:
- cite-or-abstain: the subagent nulls any value it cannot source rather than inventing one.
- lean + capped: few turns, small max_tokens, on a cheap model, to hold the <60s / <$1 budget.
- graceful fallback: on any failure/timeout it returns a seed-derived dossier (from
  constants.DRUG_SEED + mechanism_truth.json) tagged source_mode="seed_fallback", so the
  dosing request degrades instead of crashing. "Force live everywhere" holds on the happy
  path; seed is used ONLY when live retrieval genuinely fails.

The identical retrieval tools are also exposed over MCP by mcp_server.py.
"""

from __future__ import annotations

import json
import os

from anthropic import Anthropic

from retrieval_tools import TOOL_FUNCS, TOOL_SCHEMAS, openfda_label

RETRIEVAL_MODEL = os.environ.get("RETRIEVAL_MODEL", "claude-sonnet-5")
RETRIEVAL_MAX_TOKENS = int(os.environ.get("RETRIEVAL_MAX_TOKENS", "4000"))

SYSTEM = """You are a pediatric pharmacokinetics RETRIEVAL specialist. For the given drug you
find and CITE the adult PK and elimination mechanism, then call submit_dossier exactly once.

TIGHT BUDGET (latency-critical): make AT MOST 3 retrieval tool calls total, then submit.
Recommended path: (1) openfda_label once for label text / clinical pharmacology / safety, then
(2) ONE pubmed_search + (3) ONE pubmed_fetch of the top 1-2 PMIDs only if a specific PK number
(clearance, Vd, fm-split, protein binding) is still missing. Reserve web_search for a single
named gap. Do NOT keep searching once you can fill the dossier — submit immediately.

CITE-OR-ABSTAIN is absolute: every numeric value you report must be traceable to a source you
retrieved. If you cannot source a value, set it to null — NEVER invent a number to look
complete. Empty lists (no transporter / no active metabolite) are valid and expected.

Report adult values for a standard 70 kg adult. fm must use engine pathway keys where they
apply: renal_gfr, cyp3a4, ugt2b7 (map the drug's real enzymes onto these; if the true pathway
has no engine key, still name the enzyme in `enzymes` and leave fm for that fraction out)."""

DOSSIER_TOOL = {
    "name": "submit_dossier",
    "description": "Emit the structured, cited PK + mechanism dossier. Call exactly once, last.",
    "input_schema": {
        "type": "object",
        "properties": {
            "cl_adult_l_h": {"type": ["number", "null"]},
            "vd_adult_l": {"type": ["number", "null"]},
            "fm": {"type": "object", "additionalProperties": {"type": "number"},
                   "description": "engine pathway key -> fraction of clearance"},
            "target_metric": {"type": "string", "enum": ["css", "auc", "cmax", "time_mic"]},
            "typical_adult_dose_mg_per_day": {"type": ["number", "null"]},
            "oral_bioavailability": {"type": ["number", "null"]},
            "elimination": {"type": "string", "enum": ["renal", "hepatic", "mixed"]},
            "enzymes": {"type": "array", "items": {"type": "string"}},
            "transporters": {"type": "array", "items": {"type": "string"}},
            "active_metabolites": {"type": "array", "items": {"type": "string"}},
            "protein_binding_percent": {"type": ["number", "null"]},
            "toxic_dose_mg_per_kg_per_day": {"type": ["number", "null"]},
            "effective_dose_mg_per_kg_per_day": {"type": ["number", "null"]},
            "citations": {
                "type": "array",
                "items": {"type": "object",
                          "properties": {"claim": {"type": "string"}, "source": {"type": "string"}}},
            },
            "confidence": {"type": "string", "description": "brief note on data quality / gaps"},
        },
        "required": ["fm", "elimination", "enzymes", "transporters", "active_metabolites",
                     "citations"],
    },
}

TOOLS = [
    {"type": "web_search_20250305", "name": "web_search", "max_uses": 1},
    *TOOL_SCHEMAS,
    DOSSIER_TOOL,
]


def _abstention(reason: str) -> dict:
    """A null dossier — retrieval failed, so we ABSTAIN. There is deliberately NO seed
    fallback: the agent must not dose off fabricated numbers. Everything is null so the
    orchestrator grades D / declines a point estimate."""
    return {
        "cl_adult_l_h": None, "vd_adult_l": None, "fm": {}, "target_metric": "css",
        "typical_adult_dose_mg_per_day": None, "oral_bioavailability": None,
        "elimination": "mixed", "enzymes": [], "transporters": [], "active_metabolites": [],
        "protein_binding_percent": None, "toxic_dose_mg_per_kg_per_day": None,
        "effective_dose_mg_per_kg_per_day": None, "citations": [],
        "confidence": f"RETRIEVAL UNAVAILABLE ({reason}) — no values retrieved; abstain, do not dose.",
    }


def fetch(drug: str, indication: str | None = None, *, max_turns: int = 5) -> dict:
    """Retrieve a cited PK+mechanism dossier for `drug`.

    Latency/reliability design: the openFDA label is PRE-FETCHED deterministically and injected
    into the first message (so the model can often submit on turn 1), and submit_dossier is
    FORCED on the final turn (so budget exhaustion yields a real cited dossier, not a seed
    fallback). Seed fallback is reserved for genuine exceptions (e.g. network/API down).

    Returns {"dossier": {...}, "source_mode": "live"|"seed_fallback", "trace": [...],
             "usage": {...}}. Never raises.
    """
    trace: list[str] = []
    usage = {"input_tokens": 0, "output_tokens": 0, "model": RETRIEVAL_MODEL}
    try:
        client = Anthropic()
        label = openfda_label(drug)  # deterministic pre-fetch — cuts a model turn
        hint = ""
        if label.get("found"):
            keep = {k: v for k, v in label.items() if k not in ("drug", "found")}
            hint = "\n\nopenFDA label (pre-fetched — use it, search only for gaps):\n" + \
                   json.dumps(keep)[:2500]
        user = (f"Drug: {drug}\nIndication: {indication or 'unspecified'}\n"
                "Retrieve/confirm the adult PK + mechanism, then call submit_dossier." + hint)
        messages = [{"role": "user", "content": user}]

        for i in range(max_turns):
            kwargs = {}
            if i == max_turns - 1:  # final turn: force a structured dossier from what we have
                kwargs["tool_choice"] = {"type": "tool", "name": "submit_dossier"}
            resp = client.messages.create(
                model=RETRIEVAL_MODEL, max_tokens=RETRIEVAL_MAX_TOKENS,
                system=SYSTEM, tools=TOOLS, messages=messages,
                cache_control={"type": "ephemeral"}, **kwargs,
            )
            usage["input_tokens"] += resp.usage.input_tokens
            usage["output_tokens"] += resp.usage.output_tokens

            tool_uses = []
            for block in resp.content:
                if block.type == "text" and block.text.strip():
                    trace.append(block.text.strip())
                elif block.type == "tool_use":
                    tool_uses.append(block)
            messages.append({"role": "assistant", "content": resp.content})

            # Return the dossier if the model submitted one — checked BEFORE the stop_reason
            # break, because a large dossier can end with stop_reason="max_tokens", not "tool_use".
            for tu in tool_uses:
                if tu.name == "submit_dossier" and tu.input:
                    return {"dossier": tu.input, "source_mode": "live",
                            "trace": trace, "usage": usage}

            if resp.stop_reason != "tool_use":
                break

            results = []
            for tu in tool_uses:
                if tu.name in TOOL_FUNCS:
                    try:
                        out = TOOL_FUNCS[tu.name](tu.input)
                    except Exception as te:  # a bad tool call must not sink the whole retrieval
                        out = {"error": f"{tu.name} failed: {te}"}
                    results.append({"type": "tool_result", "tool_use_id": tu.id,
                                    "content": json.dumps(out)})
                # web_search is a server tool — handled by the API.
            if results:
                messages.append({"role": "user", "content": results})

        # Should be unreachable (final turn forces submit); abstain if it truly didn't.
        return {"dossier": _abstention("no dossier submitted in budget"),
                "source_mode": "unavailable",
                "trace": trace + ["retrieval did not submit a dossier in budget"], "usage": usage}
    except Exception as e:
        return {"dossier": _abstention(str(e)), "source_mode": "unavailable",
                "trace": trace + [f"retrieval error: {e}"], "usage": usage}


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "gentamicin"
    out = fetch(d, "sepsis")
    print(f"source_mode = {out['source_mode']}   (model {out['usage']['model']})")
    print(json.dumps(out["dossier"], indent=2)[:1600])
