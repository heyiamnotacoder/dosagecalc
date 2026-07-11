# PaedScale — CLAUDE.md

Pediatric dose-extrapolation agent. Derives a defensible **starting** dose for a child
from adult pharmacokinetics using allometry × organ maturation (Anderson–Holford), with a
cited, auditable rationale. **Decision support, not prescribing.**

The concept brief is `concept.html`; the product spec is `PRD.md`. This file is the
engineering source of truth. `AGENT.md` holds the short version and routes here.

## Core thesis
Drug clearance does not scale linearly with body size in early life — the organs that
eliminate the drug are still maturing. Scaling an adult dose by weight over-doses the young.
PaedScale encodes the gap between the naive linear line and the true maturation curve.

## Architecture
```
frontend/index.html         self-contained UI (form → /calculate → graded result)
backend/
  constants.py              MATURATION params (TM50/Hill) ONLY — the engine math backbone. NO per-drug PK.
  pk_engine.py              DETERMINISTIC math: allometry × maturation, dose solve, oral-F, safety  (no key)
  retrieval_tools.py        real httpx retrieval: NCBI E-utilities (PubMed) + openFDA  (no key)
  retrieval.py              RETRIEVAL SUBAGENT (cheap model) → cited PK+mechanism dossier, or abstains
  mcp_server.py             MCP server exposing the retrieval tools (FastMCP, stdio)
  agent.py                  Opus ORCHESTRATOR: retrieve_drug_data → compute → concordance → grade
  mechanism_score.py        mechanistic-reasoning scorer (6 PRD dimensions)  (no key)
  main.py                   FastAPI: / (frontend), /calculate (agent), /pk (DEV/EVAL engine), /health
  test_pk.py                deterministic engine + scorer tests + concordance  (no key)
  test_agent.py             end-to-end eval: dose, concordance, mechanistic score, latency, cost
  eval_data/                ANSWER KEYS ONLY — read by the harness, NEVER by the agent:
    drug_pk.json              reviewed adult PK oracle (scores the live agent)
    guidelines.json           pediatric guideline doses for the concordance band
    mechanism_truth.json      correct mechanism per drug (the 6 dimensions)
```

**No hardcoded per-drug PK in the product path.** The agent RETRIEVES adult PK live
(`retrieval.py` → PubMed + openFDA) or ABSTAINS (grade D) — there is no seed fallback. The
reviewed PK/guideline/mechanism data lives in `eval_data/` and is read only by the test harness
(and the no-key `/pk` dev endpoint) to *score* the live agent. This keeps the eval honest.

Split of labour: **Python does the arithmetic; Claude does the judgment** (drug → pathway
→ maturation-curve mapping and the written justification). This is the whole point — the
mapping across the drug space is what a hardcoded calculator cannot do.

## The math (pk_engine.py)
Per elimination pathway:
```
CL_child = CL_adult × (WT/70)^0.75 × MF(PMA) × OF
MF(PMA)  = PMA^H / (TM50^H + PMA^H)      # normalised so adult ≈ 1
```
- `WT` weight (kg), `PMA` postmenstrual age (weeks), `TM50` age at 50% maturation,
  `H` Hill coefficient, `OF` organ-function modifier (renal/hepatic impairment).
- Vd scales linearly (WT^1.0). Half-life = ln2 · Vd/CL.
- Dose solve by effect-driving metric:
  - `css`/`auc` (maintenance): `dose_rate_child = adult_dose_rate × CL_child/CL_adult`
  - `cmax` (peak): `dose_child = adult_dose × Vd_child/Vd_adult`
  - `time_mic` (β-lactams): solved like `css` but **flagged as a proxy** — efficacy is fT>MIC,
    so the interval/infusion governs; grade ceiling B, half-life-anchored interval forced.
- **Oral bioavailability**: `route="oral"` divides the systemic-matched dose by `F` (pediatric
  F assumed = adult → data-gap flag). **Safety bounds**: toxic/effective thresholds, when
  supplied, fire a prominent warning.
- The engine **refuses to invent a maturation curve** for an unknown pathway (raises) and
  **flags** unattributed clearance rather than hiding it. This is cite-or-abstain in code.

Known pathway keys: `renal_gfr`, `cyp3a4`, `ugt2b7` (extend MATURATION to add more).

## The seeded drugs
Stage 1 = three archetypes. Stage 2 adds five more, all of which **reuse the three
already-sourced maturation curves** (renal_gfr / cyp3a4) — no new ontogeny constant is
invented, so cite-or-abstain holds. What Stage 2 adds is drug breadth plus two new
exposure-metric archetypes (Cmax/MIC and time>MIC).

| Stage | Drug | Pathway | Metric | Edge to flag |
|-------|------|---------|--------|--------------|
| 1 | Midazolam | CYP3A4 | css | cleanest; high oral first-pass |
| 1 | Vancomycin | renal (GFR) | auc | AUC/MIC-driven + **narrow TI → recommend TDM** |
| 1 | Morphine | UGT2B7 | css | **active renally-cleared metabolite (M6G)** |
| 2 | Gentamicin | renal (GFR) | cmax | **Cmax/MIC** aminoglycoside; **NTI → TDM**; extend interval in the young |
| 2 | Amikacin | renal (GFR) | cmax | same Cmax/MIC aminoglycoside archetype |
| 2 | Fentanyl | CYP3A4 | css | extreme potency (mcg dosing); CYP3A4-interaction-prone |
| 2 | Ampicillin | renal (GFR) | css | **time>MIC** β-lactam — daily-dose match is only a proxy for fT>MIC |
| 2 | Clindamycin | CYP3A4 | css | hepatic CYP3A4 antibiotic |

Deliberately **excluded** (bad fit for the "match adult exposure" engine): digoxin,
sildenafil, acetaminophen — their paediatric dosing is empirically de-linked from adult
PK (or is multi-route with sulfation compensation), so a single-pathway extrapolation
mis-predicts and would fail concordance.

## The agents (multi-agent)
**Orchestrator** (`agent.py`, Opus) tools: `retrieve_drug_data` (→ retrieval subagent),
`compute_pediatric_dose` (engine), `web_search` (guideline only), `submit_recommendation`
(structured, includes the scored `mechanism` object). Steps: 1. record mechanism (elimination,
pathways, enzymes, transporters, active metabolites, protein binding) → 2. retrieve PK LIVE or
abstain → 3. call the engine → 4. web_search the guideline + concordance (0.67×–1.5×) →
5. grade (A/B/C/D) → 6. flags (NTI/TDM, active metabolite, time>MIC, oral-F, data gaps,
"assumed term", PD-target assumption).

**Retrieval subagent** (`retrieval.py`, Sonnet): tight-budget loop over `pubmed_search` /
`pubmed_fetch` (NCBI E-utilities) + `openfda_label` → cited PK+mechanism dossier. openFDA label
is pre-fetched; `submit_dossier` is forced on the final turn. On failure it returns a **null
dossier** (`source_mode="unavailable"`) — never a fabricated fallback. Same tools are exposed
over MCP by `mcp_server.py`.

Grades: **A** passes concordance vs a real guideline · **B** solid PK, no guideline ·
**C** sparse/uncertain, directional only · **D** insufficient data / safety stop.

## Rules that must not regress
- **Live retrieval or abstain.** Product path never reads `eval_data/`; unretrievable PK → grade D.
- **Cite-or-abstain.** No unsourced PK value drives a confident point estimate (null it instead).
- **Concordance band is 1.5× / 0.67×** (not the old 10%). Report the ratio.
- **Mechanism is scored.** 6 dimensions vs `eval_data/mechanism_truth.json`; empty lists are
  correct-negatives — the model must not invent transporters/metabolites.
- **PMA for under-2s.** If unknown, assume term AND surface that assumption.
- **Safety bounds.** Never present a dose above toxic / below effective without a prominent flag.
- **NTI drugs (vancomycin, aminoglycosides) recommend TDM**; **active metabolites (M6G) flagged.**
- **Known engine limit:** allometry×Cmax **underdoses concentration-dependent aminoglycosides** —
  the agent must guideline-anchor and flag the exposure-target mismatch (verified on gentamicin).

## Run
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 test_pk.py                 # deterministic core + scorers — NO key needed
cp .env.example .env               # ANTHROPIC_API_KEY (+ optional OPENFDA_API_KEY / NCBI_API_KEY)
uvicorn main:app --reload --port 8000
# open http://localhost:8000
python3 test_agent.py              # end-to-end eval (needs key + network); --full for all drugs
python3 mcp_server.py              # optional: run the retrieval MCP server (stdio)
```
`/pk` and `test_pk.py` run without a key (they read the `eval_data/` oracle). `/calculate`,
`agent.py`, `retrieval.py` need the key **and network** (live PubMed/openFDA).
**Budget note:** live retrieval on every query is real — expect ~60–95 s/query (retrieval
subagent + orchestrator + guideline search). The <60 s target is the tuning goal, not yet met.

## Budget / scope
Target < $1 and < 60 s per query. Default model `claude-opus-4-8` (override via
`ORCHESTRATOR_MODEL`; `claude-sonnet-5` is the cheaper option). Sequential rollout:
**3 drugs → 5–10 → 20**, gating on cost, concordance, and mechanistic-reasoning score.
Not built yet (deferred per PRD): caching, DB, auth, Next.js migration, dose rounding to
available formulations.
