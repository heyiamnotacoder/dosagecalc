"""
PaedScale — FastAPI backend.

Serves the lightweight frontend and a /calculate endpoint that runs a case through the
Claude orchestration layer. Also exposes /pk for the deterministic engine alone (no key).

Run:  uvicorn main:app --reload --port 8000
Then open http://localhost:8000
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()  # pulls ANTHROPIC_API_KEY from backend/.env

from agent import run_case  # noqa: E402  (after load_dotenv)
from pk_engine import compute_pediatric_dose, result_to_dict  # noqa: E402

app = FastAPI(title="PaedScale", version="0.2-mvp")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

HERE = os.path.dirname(__file__)
FRONTEND = os.path.join(HERE, "..", "frontend", "index.html")
EVAL_PK = os.path.join(HERE, "eval_data", "drug_pk.json")


def _oracle_pk() -> dict:
    """Reviewed adult-PK oracle — DEV/EVAL ONLY. The product path (/calculate) never reads it;
    it exists so the no-key /pk engine check can run against known drugs."""
    with open(EVAL_PK) as f:
        return json.load(f)["drugs"]


class Case(BaseModel):
    drug: str
    indication: str | None = None
    age_years: float
    weight_kg: float
    pma_weeks: float | None = None
    gestational_age_weeks: float | None = None
    postnatal_age_weeks: float | None = None
    renal_impairment: bool = False
    hepatic_impairment: bool = False
    route: str = "iv"  # "iv" | "oral" — governs the oral-bioavailability correction


@app.get("/")
def index():
    return FileResponse(FRONTEND)


@app.get("/health")
def health():
    return {"ok": True, "has_api_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "model": os.environ.get("ORCHESTRATOR_MODEL", "claude-opus-4-8"),
            "eval_drugs": sorted(_oracle_pk())}  # scored drug set (oracle), not a runtime source


@app.post("/calculate")
def calculate(case: Case):
    """Full agentic pipeline — needs ANTHROPIC_API_KEY."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(400, "ANTHROPIC_API_KEY not set. Add it to backend/.env")
    result = run_case(case.model_dump())
    if result.get("recommendation") is None:
        raise HTTPException(502, result.get("error", "no recommendation produced"))
    return result


@app.post("/pk")
def pk(case: Case):
    """DEV/EVAL ONLY — deterministic engine on the reviewed PK oracle, no API key required.
    This is a bench check for the math; the PRODUCT path is /calculate (live retrieval)."""
    oracle = _oracle_pk()
    seed = oracle.get(case.drug.strip().lower())
    if not seed:
        raise HTTPException(404, f"'{case.drug}' not in eval oracle {sorted(oracle)}")
    r = compute_pediatric_dose(
        drug=case.drug, weight_kg=case.weight_kg,
        cl_adult_l_h=seed["cl_adult_l_h"], vd_adult_l=seed["vd_adult_l"],
        fm=seed["fm"], target_metric=seed["target_metric"],
        age_years=case.age_years, pma_weeks=case.pma_weeks,
        gestational_age_weeks=case.gestational_age_weeks,
        postnatal_age_weeks=case.postnatal_age_weeks,
        adult_dose_mg_per_day=seed.get("typical_adult_dose_mg_per_day"),
        renal_function_fraction=0.5 if case.renal_impairment else 1.0,
        hepatic_function_fraction=0.5 if case.hepatic_impairment else 1.0,
        route=case.route,
        oral_bioavailability=seed.get("oral_bioavailability", 1.0),
        toxic_dose_mg_per_kg_per_day=seed.get("toxic_dose_mg_per_kg_per_day"),
        effective_dose_mg_per_kg_per_day=seed.get("effective_dose_mg_per_kg_per_day"),
    )
    return result_to_dict(r)
