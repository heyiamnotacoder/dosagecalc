# PaedScale — AGENT.md

Pediatric dose-extrapolation agent: adult PK → pediatric starting dose via
**allometry × organ maturation (Anderson–Holford)**, with cited rationale.
Decision support, not prescribing.

**Full engineering detail lives in [CLAUDE.md](./CLAUDE.md) — read it for anything beyond
this summary.** Concept: `concept.html`. Product spec: `PRD.md`.

## Key facts
- **Python does the math, Claude does the judgment** (drug → pathway → maturation mapping).
- Core equation: `CL_child = CL_adult × (WT/70)^0.75 × MF(PMA) × OF`,
  `MF = PMA^H / (TM50^H + PMA^H)`.
- Drugs: Stage 1 — **midazolam** (CYP3A4), **vancomycin** (renal, NTI→TDM), **morphine** (UGT2B7, M6G).
  Stage 2 adds **gentamicin**/**amikacin** (renal, Cmax/MIC, NTI→TDM), **ampicillin** (renal, time>MIC),
  **fentanyl** & **clindamycin** (CYP3A4) — all reuse the 3 existing maturation curves (no new constants).
- **Cite-or-abstain**: no unsourced PK value drives a confident number.
- **Concordance band 1.5× / 0.67×**. Grades A/B/C/D.
- PMA required for under-2s; unknown → assume term + flag.

## Layout
`backend/constants.py` (MATURATION only — no per-drug PK) · `backend/pk_engine.py`
(deterministic, no key) · `backend/retrieval.py` (Sonnet retrieval subagent, live PubMed/openFDA)
· `backend/retrieval_tools.py` + `backend/mcp_server.py` (MCP) · `backend/agent.py` (Opus
orchestrator) · `backend/mechanism_score.py` (mechanistic eval) · `backend/main.py` (FastAPI) ·
`backend/eval_data/` (answer keys — harness only, NEVER read by the agent) · `frontend/index.html`.

**No hardcoded drug PK in the product path** — the agent retrieves live or abstains (grade D).
Multi-agent: Opus orchestrator + Sonnet retrieval subagent + MCP retrieval tools + mechanistic eval.

## Run
```bash
cd backend && pip install -r requirements.txt
python3 test_pk.py                       # no key
cp .env.example .env                     # add ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000    # open http://localhost:8000
```
See CLAUDE.md → "Rules that must not regress" before changing engine or agent behaviour.
