# PaedScale — CLAUDE.md

Pediatric dose-extrapolation agent. Derives a defensible **starting** dose for a child
from adult pharmacokinetics using allometry × organ maturation (Anderson–Holford), with a
cited, auditable rationale. **Decision support, not prescribing.**

The concept brief is `concept.html`; the product spec is `PRD.md`. This file is the
engineering source of truth. `AGENT.md` holds the short version and routes here.

## RULES:
1. If you want to check browser use browser harness first. if allow external debugging is not enabled ask user to do it. It is more token efficient.
  If browser harness cant solve the problem and you must have to use browser then use claude in chrome.
2. read handoff saved at /private/tmp/
3. Read Checklist.md for any task remaining and ask user if he want to continue remaining tasks. Also if the work is too long rather than saving work in plan.md use checklist.md for it.
4. **NEVER merge branch `demo` into `master`.** Root `demo/` is offline curated PK for demos only.
5. **NEVER merge branch `validation-eval` into `master`.** Harness oracles stay off the product path.

## Demo branch (this branch)
Root `demo/pk.json` + `demo/guidelines.json` + `backend/demo_pack.py`: when a listed drug is
requested, `retrieval.fetch` returns `source_mode="demo"` and **skips live PubMed/openFDA**.
Disable with `PAEDSCALE_DEMO=0`. Other drugs still use the live path.

## Core thesis
Drug clearance does not scale linearly with body size in early life — the organs that
eliminate the drug are still maturing. Scaling an adult dose by weight over-doses the young.
PaedScale encodes the gap between the naive linear line and the true maturation curve.

## Architecture
```
frontend/index.html         self-contained UI (form → /calculate/stream → graded result + chat)
backend/                    (run all commands from here; backend/ is the package root)
  engine/                   deterministic backbone (no I/O, no LLM)
    constants.py            MATURATION params (TM50/Hill) ONLY — engine backbone. NO per-drug PK.
    pk_engine.py            DETERMINISTIC math: allometry × maturation, dose solve, oral-F, safety,
                            renal eGFR (bedside Schwartz) → organ-function modifier
    edge_cases.py           deterministic flags: prodrug / obesity / protein-binding / illness
    pk_cache.py             bounded in-process LRU for live dossiers (Render single-dyno shared pool)
    mechanism_score.py      mechanistic-reasoning scorer (6 PRD dimensions)
  retrieval/                retrieval subagent + tools (package; `import retrieval` → __init__.py)
    __init__.py             RETRIEVAL SUBAGENT → demo pack | live | cache | abstain
    retrieval_tools.py      httpx: PubMed E-utilities + openFDA + web_fetch
  agents/
    agent.py                Opus ORCHESTRATOR: load_skill → retrieve → compute → edge_cases → grade
  api/
    main.py                 FastAPI: /, /calculate, /calculate/stream, /chat, /pk, /health
    mcp_server.py           MCP server for the same retrieval tools (FastMCP, stdio)
  tests/                    test_pk.py / test_agent.py
  skills/                   lean markdown skills (mechanism, pubmed, openfda, webfetch, edge_cases)
  demo_pack.py              DEMO ONLY: load root demo/ JSON (skip live retrieval); top-level module
  eval_data/                ANSWER KEYS ONLY — harness never product path
demo/                       DEMO BRANCH ONLY: curated pk.json + guidelines.json
```

**On master:** no hardcoded per-drug PK in the product path — live retrieve or abstain.
**On `demo`:** curated `demo/` pack short-circuits retrieval for 8 drugs (`source_mode=demo`).
`eval_data/` remains harness/dev only.

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

Known pathway keys: `renal_gfr`, `cyp3a4`, `ugt2b7`, `cyp1a2`, `cyp2d6`, `cyp2c9`,
`cyp2c19`, `ugt1a1`. Extend MATURATION only with **published** TM50/Hill — never invent.

**Skills:** lean files in `backend/skills/` loaded via `load_skill` — keep agent SYSTEM short.
**Edge cases:** `assess_edge_cases` flags prodrug/obesity/high-PB/illness when evidence exists.
**PK cache:** `pk_cache.py` — max entries/bytes/TTL (env); single dyno shared; no multi-dyno Redis yet.

## The seeded drugs
Stage 1 = three archetypes. Stage 2 adds five more. Demo drugs primarily use
`renal_gfr` / `cyp3a4` / `ugt2b7`; extra pathways support broader drug space without inventing curves.

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
cd backend                         # backend/ is the package root — run everything from here
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m tests.test_pk           # deterministic core + scorers — NO key needed
cp .env.example .env               # ANTHROPIC_API_KEY (+ optional OPENFDA_API_KEY / NCBI_API_KEY)
uvicorn api.main:app --reload --port 8000
# open http://localhost:8000
python3 -m tests.test_agent        # end-to-end eval (needs key + network); --full for all drugs
python3 -m api.mcp_server          # optional: run the retrieval MCP server (stdio)
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
