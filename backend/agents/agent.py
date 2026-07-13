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
from engine.pk_engine import (
    compute_pediatric_dose,
    estimate_gfr_bedside_schwartz,
    renal_function_fraction_from_labs,
    result_to_dict,
)
from skills import load_skill, list_skills

ORCHESTRATOR_MODEL = os.environ.get("ORCHESTRATOR_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.environ.get("PAEDSCALE_MAX_TOKENS", "4000"))

SYSTEM = """You are PaedScale: pediatric STARTING dose from adult PK via allometry × maturation.
Decision support for a clinician — NOT a prescriber.

Pipeline (lean):
1. load_skill('mechanism') if needed → map elimination / fm / target_metric / mechanism fields.
   Empty lists for absent transporters/metabolites. Cite-or-abstain.
2. retrieve_drug_data FIRST — only PK source (live or shared cache). Null/unavailable → grade D, no invented numbers.
3. CONTRAINDICATIONS (before or with dosing): from the label/dossier + clinical knowledge, list
   situations where this drug should be AVOIDED in contraindications_avoid (allergy/class
   cross-reactivity, absolute contraindications, major condition warnings). Compare to case
   allergies[] and conditions[]. If the patient MATCHES a true contraindication (e.g. allergy
   to this drug or class, absolute contraindication present), HARD STOP: final_dose_* = null,
   grade = D, blocked=true, block_reason = "SAFETY STOP — CONTRAINDICATED: …", and put that
   string as the FIRST flag. Never invent a dose for a contraindicated patient. Always still
   fill contraindications_avoid so the clinician sees the full avoid-list.
4. compute_pediatric_dose with retrieved PK + child covariates (use case renal/hepatic fractions).
   Pass oral_bioavailability from the dossier; if a route is clinically non-viable (e.g. an oral
   route for a drug not systemically absorbed orally, F=0), pass routes_allowed (e.g. ["iv"]).
   If compute returns blocked=true the case is NOT prescribable: submit_recommendation with
   final_dose_mg_per_kg_per_day AND final_dose_mg_per_day = null, grade = D, and block_reason
   verbatim as the FIRST flag. Never fabricate or carry forward a dose for a blocked case.
5. load_skill('edge_cases') + assess_edge_cases when relevant; merge flags.
6. web_search pediatric guideline → concordance 0.67×–1.5× (none → grade B).
7. Grade A/B/C/D; flag NTI→TDM, metabolites, oral-F, assumed-term, exposure-matching PD assumption.
8. submit_recommendation once, last. Lean reasoning. Flag toxic/sub-therapeutic doses."""

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
                       "Returns source_mode live|cache|unavailable.",
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
                "routes_allowed": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Optional clinically viable routes, e.g. [\"iv\"] for a drug "
                                   "not systemically absorbed orally. Non-viable route → hard stop.",
                },
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
                "contraindications_avoid": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Conditions / situations where this drug should be avoided "
                                   "(allergy class, absolute CIs, major warnings). Always fill.",
                },
                "contraindication_matched": {
                    "type": ["string", "null"],
                    "description": "If patient allergies/conditions match a true CI, the "
                                   "matched reason; else null.",
                },
                "blocked": {
                    "type": "boolean",
                    "description": "true when not prescribable (contraindication, route, toxic).",
                },
                "block_reason": {
                    "type": ["string", "null"],
                    "description": "SAFETY STOP reason when blocked.",
                },
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"claim": {"type": "string"}, "source": {"type": "string"}},
                    },
                },
            },
            "required": ["mechanism", "grade", "grade_rationale", "rationale", "flags",
                         "contraindications_avoid"],
        },
    },
]


# Keyword args accepted by compute_pediatric_dose (filter model junk).
_COMPUTE_KEYS = frozenset({
    "drug", "weight_kg", "cl_adult_l_h", "vd_adult_l", "fm", "target_metric",
    "age_years", "pma_weeks", "gestational_age_weeks", "postnatal_age_weeks",
    "adult_dose_mg_per_day", "adult_interval_h", "renal_function_fraction",
    "hepatic_function_fraction", "toxic_dose_mg_per_kg_per_day",
    "effective_dose_mg_per_kg_per_day", "route", "oral_bioavailability",
    "routes_allowed", "assume_term",
})


def _assess_edge_cases(args: dict) -> dict:
    try:
        from engine.edge_cases import assess_edge_cases
        return assess_edge_cases(
            args.get("case") or {},
            args.get("dossier"),
            args.get("engine_result"),
        )
    except Exception as e:
        return {"flags": [], "adjustments": {}, "notes": [], "error": str(e)}


def _dossier_core_pk_ok(dossier: dict | None) -> bool:
    """True when both adult CL and Vd are present (usable for the engine)."""
    if not dossier:
        return False
    return dossier.get("cl_adult_l_h") is not None and dossier.get("vd_adult_l") is not None


def _force_safety_block(rec: dict, reason: str, *, flag_token: str = "SAFETY STOP") -> None:
    """Null doses, grade D, blocked — deterministic submit override."""
    rec["final_dose_mg_per_kg_per_day"] = None
    rec["final_dose_mg_per_day"] = None
    rec["grade"] = "D"
    rec["blocked"] = True
    rec["block_reason"] = reason
    flags = list(rec.get("flags") or [])
    if not any(flag_token in str(f).upper() or reason in str(f) for f in flags):
        flags.insert(0, reason if reason.upper().startswith("SAFETY") else f"SAFETY STOP: {reason}")
    rec["flags"] = flags


def _build_compute(case: dict, state: dict):
    """Return a compute_pediatric_dose tool handler closed over case + retrieval state.

    Injects authoritative organ fractions / route / safety bounds from the case and
    last dossier so the model cannot omit renal OF or invent PK after abstention.
    """
    def _compute(args: dict) -> dict:
        # Live-or-abstain: refuse compute without a successful retrieval of core PK.
        if state.get("pk_block_reason") or not state.get("pk_ok"):
            reason = state.get("pk_block_reason") or (
                "SAFETY STOP — no cited adult PK retrieved; call retrieve_drug_data "
                "successfully before compute (cite-or-abstain)."
            )
            state["blocked_reason"] = reason
            return {
                "error": reason,
                "blocked": True,
                "block_reason": reason,
                "recommended_dose_mg_per_day": None,
                "recommended_dose_mg_per_kg_per_day": None,
            }
        try:
            merged = {k: v for k, v in (args or {}).items() if k in _COMPUTE_KEYS and v is not None}
            # Authoritative organ function from normalized case (not model defaults).
            if case.get("renal_function_fraction") is not None:
                merged["renal_function_fraction"] = case["renal_function_fraction"]
            if case.get("hepatic_function_fraction") is not None:
                merged["hepatic_function_fraction"] = case["hepatic_function_fraction"]
            # Prefer case route when model omits it.
            if "route" not in merged and case.get("route"):
                merged["route"] = case["route"]
            # Child covariates from case if model omitted them.
            for k in ("weight_kg", "age_years", "pma_weeks", "gestational_age_weeks",
                      "postnatal_age_weeks"):
                if k not in merged and case.get(k) is not None:
                    merged[k] = case[k]
            if "drug" not in merged and case.get("drug"):
                merged["drug"] = case["drug"]
            # Wire dossier toxic/effective/F when model omits them.
            dossier = state.get("last_dossier") or {}
            for k in ("toxic_dose_mg_per_kg_per_day", "effective_dose_mg_per_kg_per_day",
                      "oral_bioavailability"):
                if k not in merged and dossier.get(k) is not None:
                    merged[k] = dossier[k]
            # Prefer retrieved adult dose when model omits it.
            if "adult_dose_mg_per_day" not in merged and dossier.get("typical_adult_dose_mg_per_day") is not None:
                merged["adult_dose_mg_per_day"] = dossier["typical_adult_dose_mg_per_day"]
            # Prefer retrieved CL/Vd/fm/metric over model invention when dossier has them.
            if dossier.get("cl_adult_l_h") is not None:
                merged["cl_adult_l_h"] = dossier["cl_adult_l_h"]
            if dossier.get("vd_adult_l") is not None:
                merged["vd_adult_l"] = dossier["vd_adult_l"]
            if dossier.get("fm"):
                merged["fm"] = dossier["fm"]
            if dossier.get("target_metric") and "target_metric" not in (args or {}):
                merged["target_metric"] = dossier["target_metric"]

            state["last_compute_renal_frac"] = merged.get(
                "renal_function_fraction", case.get("renal_function_fraction", 1.0)
            )
            r = compute_pediatric_dose(**merged)
            out = result_to_dict(r)
            if out.get("blocked"):
                state["blocked_reason"] = out.get("block_reason") or "not prescribable"
            return out
        except Exception as e:
            return {"error": str(e)}

    return _compute


def _normalize_case(case: dict) -> dict:
    """Map UI inputs to engine organ fractions; copy so we do not mutate caller.

    Renal: derive the organ-function modifier from labs (bedside Schwartz eGFR from
    serum creatinine + height). If labs are absent we apply NO reduction (fraction
    1.0) and rely on a data-gap flag — never a silent flat 0.5.
    Hepatic: no automatic clearance reduction; adjustment is drug-specific and is
    surfaced as a note (see _organ_function_flags). Child-Pugh class may be entered
    or calculated from labs (bilirubin, albumin, INR ± ascites/encephalopathy).
    """
    c = dict(case)
    if "renal_function_fraction" not in c:
        frac = None
        if c.get("renal_impairment"):
            frac = renal_function_fraction_from_labs(
                c.get("height_cm"), c.get("serum_creatinine_mg_dl")
            )
            c["estimated_gfr_ml_min_1_73m2"] = estimate_gfr_bedside_schwartz(
                c.get("height_cm"), c.get("serum_creatinine_mg_dl")
            )
        c["renal_function_fraction"] = frac if frac is not None else 1.0
    if "hepatic_function_fraction" not in c:
        c["hepatic_function_fraction"] = 1.0  # drug-specific; note instead of flat modifier
    # Child-Pugh: calculate from labs when present, else keep entered A/B/C
    try:
        from engine.child_pugh import resolve_child_pugh
        cp_patch = resolve_child_pugh(c)
        c.update(cp_patch)
    except Exception:
        pass
    # Normalize allergies/conditions to clean string lists
    for key in ("allergies", "conditions"):
        raw = c.get(key)
        if raw is None:
            c[key] = []
        elif isinstance(raw, str):
            c[key] = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
        elif isinstance(raw, list):
            c[key] = [str(x).strip() for x in raw if str(x).strip()]
        else:
            c[key] = []
    # Light deterministic allergy↔drug name overlap hint (agent still decides hard-stop)
    try:
        from engine.child_pugh import allergy_tokens_overlap
        hits = allergy_tokens_overlap(c.get("allergies"), c.get("drug") or "")
        if hits:
            c["allergy_name_overlap_hint"] = hits
    except Exception:
        pass
    # postnatal days → weeks for engine if provided
    if c.get("postnatal_age_days") is not None and c.get("postnatal_age_weeks") is None:
        try:
            c["postnatal_age_weeks"] = float(c["postnatal_age_days"]) / 7.0
        except (TypeError, ValueError):
            pass
    return c


def _organ_function_flags(case: dict, applied_renal_frac: float | None = None) -> list[str]:
    """Deterministic renal/hepatic-impairment flags built from the normalized case.

    Authoritative and model-independent: run_case injects these at submit time so the
    graded output always reflects what the engine actually did with organ function.
    `applied_renal_frac` is the fraction actually passed into the last compute (if any).
    """
    flags: list[str] = []
    if case.get("renal_impairment"):
        egfr = case.get("estimated_gfr_ml_min_1_73m2")
        frac = applied_renal_frac if applied_renal_frac is not None else case.get("renal_function_fraction")
        if egfr is not None and frac is not None:
            flags.append(
                f"RENAL impairment: estimated GFR ~{egfr:.0f} mL/min/1.73m^2 (bedside Schwartz "
                f"from serum creatinine + height) → renal clearance scaled to ~{float(frac):.2f}x normal. "
                "NOTE: Schwartz is the pediatric standard; Cockcroft-Gault (adult) is not used. "
                "Reassess interval and TDM for renally-cleared / narrow-TI drugs."
            )
        else:
            flags.append(
                "RENAL impairment flagged but serum creatinine and/or height were not provided — "
                "GFR was NOT estimated and NO clearance reduction was applied. Provide height + "
                "serum creatinine for a Schwartz-based estimate; reassess interval and TDM."
            )
    if case.get("hepatic_impairment"):
        cp = case.get("child_pugh")
        src = case.get("child_pugh_source")
        score = case.get("child_pugh_score")
        if cp:
            src_txt = ""
            if src == "calculated" and score is not None:
                src_txt = f" (calculated score {score})"
            elif src == "entered":
                src_txt = " (entered)"
            cp_txt = f"Child-Pugh {str(cp).upper()}{src_txt} noted; "
        else:
            cp_txt = ""
        flags.append(
            f"HEPATIC impairment: {cp_txt}dose adjustment is DRUG-SPECIFIC (depends on the drug's "
            "hepatic extraction ratio and metabolic pathway). No automatic clearance reduction was "
            "applied — consult a drug-specific hepatic-impairment reference; further research required."
        )
    return flags


def _apply_organ_function_flags(
    rec: dict, case: dict, applied_renal_frac: float | None = None,
) -> None:
    """Replace any renal/hepatic-impairment flags with the authoritative deterministic ones."""
    kept = [
        f for f in (rec.get("flags") or [])
        if not str(f).startswith(("RENAL impairment", "HEPATIC impairment"))
    ]
    kept.extend(_organ_function_flags(case, applied_renal_frac=applied_renal_frac))
    rec["flags"] = kept


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
    # Deterministic safety state shared with tool handlers (not model-trust).
    state: dict = {
        "blocked_reason": None,   # engine / route / toxic hard-stop
        "pk_ok": False,           # True after live/cache dossier with CL+Vd
        "pk_block_reason": None,  # sticky when retrieval unavailable / null PK
        "last_dossier": None,
        "last_compute_renal_frac": case.get("renal_function_fraction"),
    }
    local_tools = {
        "compute_pediatric_dose": _build_compute(case, state),
        "load_skill": lambda a: load_skill(a.get("name", "")),
        "assess_edge_cases": _assess_edge_cases,
    }

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
                rec = dict(tu.input) if tu.input else {}
                # 1) PK cite-or-abstain: never allow a dose without successful retrieval.
                if state.get("pk_block_reason") or not state.get("pk_ok"):
                    reason = state.get("pk_block_reason") or (
                        "SAFETY STOP — adult PK was not retrieved (or was null); "
                        "abstain, do not invent numbers (grade D)."
                    )
                    _force_safety_block(rec, reason)
                # 2) Engine hard stop (route / toxic / empty fm / …).
                if state.get("blocked_reason"):
                    _force_safety_block(rec, state["blocked_reason"])
                # 3) Deterministic same-drug allergy hard-stop (token overlap).
                allergy_hits = case.get("allergy_name_overlap_hint") or []
                if allergy_hits:
                    hits_txt = ", ".join(str(h) for h in allergy_hits)
                    reason = (
                        f"SAFETY STOP — CONTRAINDICATED: allergy matches drug name "
                        f"({hits_txt})."
                    )
                    _force_safety_block(rec, reason, flag_token="CONTRAINDICATED")
                    rec["contraindication_matched"] = rec.get("contraindication_matched") or hits_txt
                # 4) Model-reported contraindication hard-stop.
                matched = rec.get("contraindication_matched")
                matched_s = str(matched).strip() if matched is not None else ""
                br = str(rec.get("block_reason") or "")
                ci_hit = bool(matched_s) or "CONTRAINDICATED" in br.upper()
                if ci_hit:
                    reason = br if "CONTRAINDICATED" in br.upper() else (
                        f"SAFETY STOP — CONTRAINDICATED: {matched_s or br or 'patient matches a listed contraindication'}"
                    )
                    if not reason.upper().startswith("SAFETY"):
                        reason = f"SAFETY STOP — CONTRAINDICATED: {reason}"
                    _force_safety_block(rec, reason, flag_token="CONTRAINDICATED")
                # Ensure avoid-list is always a list (even if model omitted)
                avoid = rec.get("contraindications_avoid")
                if not isinstance(avoid, list):
                    rec["contraindications_avoid"] = []
                # Authoritative renal/hepatic-impairment flags (model-independent).
                _apply_organ_function_flags(
                    rec, case, applied_renal_frac=state.get("last_compute_renal_frac"),
                )
                return {
                    "recommendation": rec,
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
                dossier = rout.get("dossier") or {}
                mode = rout.get("source_mode") or "unavailable"
                # Latch retrieval outcome — product path never invents PK after fail/null.
                if mode == "unavailable" or not _dossier_core_pk_ok(dossier):
                    state["pk_ok"] = False
                    state["last_dossier"] = dossier
                    conf = (dossier.get("confidence") or "").strip()
                    state["pk_block_reason"] = (
                        "SAFETY STOP — PK retrieval unavailable or core adult PK (CL/Vd) "
                        f"null (source_mode={mode}"
                        + (f"; {conf}" if conf else "")
                        + "). Abstain — do not invent numbers (grade D)."
                    )
                    if on_step:
                        on_step(f"→ retrieval {mode} — PK abstain latched")
                else:
                    state["pk_ok"] = True
                    state["pk_block_reason"] = None
                    state["last_dossier"] = dossier
                payload = {
                    "source_mode": mode,
                    "dossier": dossier,
                }
                tool_results.append({
                    "type": "tool_result", "tool_use_id": tu.id,
                    "content": json.dumps(payload),
                })
            elif tu.name in local_tools:
                if on_step:
                    on_step(f"→ {tu.name} …")
                out = local_tools[tu.name](tu.input)
                if tu.name == "compute_pediatric_dose" and isinstance(out, dict) and out.get("blocked"):
                    state["blocked_reason"] = out.get("block_reason") or state.get("blocked_reason") or "not prescribable"
                    if on_step:
                        on_step(f"→ SAFETY STOP — {state['blocked_reason']}")
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
