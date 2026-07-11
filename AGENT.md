# PaedScale — AGENT.md

Pediatric dose-extrapolation agent: adult PK → pediatric starting dose via
**allometry × organ maturation (Anderson–Holford)**, with cited rationale.
Decision support, not prescribing.

**Full engineering detail lives in [CLAUDE.md](./CLAUDE.md).** Concept: `concept.html`. Spec: `PRD.md`.

## Key facts
- **Python does the math, Claude does the judgment** (pathway mapping + justification).
- `CL_child = CL_adult × (WT/70)^0.75 × MF(PMA) × OF`
- Pathways: `renal_gfr`, `cyp3a4`, `ugt2b7`, `cyp1a2`, `cyp2d6`, `cyp2c9`, `cyp2c19`, `ugt1a1`
- **Lean skills** in `backend/skills/` (mechanism, pubmed, openfda, webfetch, edge_cases)
- **Cite-or-abstain**; live retrieve → optional **shared PK cache** → or grade D
- **Edge flags**: prodrug, obesity, high protein binding, illness/organ impairment
- Concordance **0.67×–1.5×**. Grades A/B/C/D (hover legend in UI)

## Layout
`constants.py` · `pk_engine.py` · `edge_cases.py` · `pk_cache.py` · `skills/` ·
`retrieval.py` + `retrieval_tools.py` + `mcp_server.py` · `agent.py` · `main.py` ·
`eval_data/` (harness only) · `frontend/index.html`

## Run
```bash
cd backend && pip install -r requirements.txt
python3 test_pk.py
cp .env.example .env   # ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```
