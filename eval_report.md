# PaedScale — Eval report (tasks 0–2)

**Branch:** `eval` (created from `master` @ `07b13cb`)  
**Method:** full code read of agent/engine/frontend + `python3 test_pk.py` (deterministic).  
**Live agent runs:** not required for structural answers; deferred (budget ≤5 if needed later).

---

## Task 1 — Judgement eval

### 1. Single-run architecture inventory

| Question | Answer |
|----------|--------|
| **Claude agent tool calls** | Orchestrator (`agent.py`): `retrieve_drug_data`, `compute_pediatric_dose`, `web_search` (server tool, max 2), `submit_recommendation`. Retrieval subagent (`retrieval.py`): `pubmed_search`, `pubmed_fetch`, `openfda_label`, `web_search` (max 1), `submit_dossier`. |
| **Claude skill used** | **No.** There is no Claude Skill / SKILL.md registered for this product path. PRD mentions skills aspirationally; implementation uses plain Anthropic Messages API + Python tools. |
| **Claude MCP used** | **MCP server exists but is optional / off the hot path.** `mcp_server.py` exposes PubMed + openFDA via FastMCP (stdio). Production retrieval calls the same functions **in-process** via `retrieval_tools.py`, not over MCP. |
| **Claude Agent SDK used** | **No.** Uses `anthropic` Python SDK (`Anthropic().messages.create` tool loop), not the Claude Agent SDK. |
| **Multi-agentic?** | **Yes.** Two Anthropic loops: (1) Opus orchestrator (`ORCHESTRATOR_MODEL`, default `claude-opus-4-8`) with judgment + tools; (2) Sonnet retrieval subagent (`RETRIEVAL_MODEL`, default `claude-sonnet-5`) that returns a cited PK dossier. Split of labour: cheap model retrieves, expensive model maps pathway / grades / writes rationale; Python does the arithmetic. |

### 2. Real-world impact — will clinicians use this?

**Potential impact: real; clinical adoption today: not yet.**

- **Why it matters:** Pediatric off-label / off-guideline dosing is a genuine gap. Weight-linear adult scaling over-doses young children; allometry × maturation is textbook pharmacometrics that few bedside tools expose with citations.
- **Why a clinician would not trust it in production yet:** no regulatory CDS validation, live PubMed/openFDA values can be wrong or sparse, ~60–95 s latency, no formulation rounding, binary organ-function toggles, obesity/protein-binding shift not modeled, and the product correctly disclaims “decision support, not prescribing.”
- **Likely near-term users:** clinical pharmacology fellows, pediatric pharmacy teams, educators, hackathon/demo judges — not autonomous ward dosing.

### 3. Is this a sound project? Craft vs hack?

**Yes — thoughtfully refined for a hackathon MVP, not a one-shot demo.**

Evidence of iteration:
- Cite-or-abstain encoded in **code** (engine refuses unknown pathways; retrieval nulls unsourced numbers; no seed fallback on product path).
- Multi-agent cost split (Opus + Sonnet), prompt caching, turn caps, forced `submit_dossier` on last retrieval turn.
- Scored mechanism dimensions with correct-negatives; concordance band 0.67×–1.5×; grades A–D.
- Stage-2 drugs reuse only three published maturation curves (no invented ontogeny).
- Frontend overhaul: landing, SSE live loader, full result + floating follow-up chat.
- Honest known limits (aminoglycoside Cmax underdose, time>MIC as proxy) documented in CLAUDE.md / flags.

Gaps that still feel unfinished: only 3 ontogeny curves for a claimed path to 50 drugs; obesity/prodrug/protein-binding shift absent; PRD “skills + Agent SDK” not fully realized; latency over target.

### 4. Does it work? Trustworthy? Cool to watch?

| Layer | Status |
|-------|--------|
| Deterministic engine | **Works** — `test_pk.py` all pass; 7/8 seed concordance within band |
| Live agent path | **Wired** (`/calculate`, `/calculate/stream`, `/chat`); needs key + network; not re-run this session |
| UI “cool factor” | **High** — live stage UI, maturation-curve viz, console stream of reasoning, graded result + preloaded Q&A chips |

As software you could demo: yes. As findings you fully trust for dosing: only with clinician oversight and after validation (task 3 territory).

---

## Task 2 — Internal eval

### 1. Mechanisms for predicting dose

**Exposure / solve metrics (how dose is computed)** — decided by the **orchestrator model** via `target_metric` passed into `compute_pediatric_dose`:

| Metric | Solve rule | Use case |
|--------|------------|----------|
| `css` | daily dose × CL_child/CL_adult | maintenance / steady state |
| `auc` | same as css | AUC/MIC (e.g. vancomycin) |
| `cmax` | dose × Vd_child/Vd_adult | peak-driven (aminoglycosides) |
| `time_mic` | css-like + **proxy flag** + half-life interval | β-lactams (fT>MIC) |

**Maturation pathways (engine keys in `constants.MATURATION`)** — only three:

1. `renal_gfr` (TM50 47.7 wk, Hill 3.40)
2. `cyp3a4` (TM50 55.4 wk, Hill 1.83)
3. `ugt2b7` (TM50 88.3 wk, Hill 1.90)

**Who decides which to use?** Claude (orchestrator) maps drug → `fm` dict over those keys after reading the retrieval dossier. The engine never invents a fourth pathway.

**Multiple routes of elimination?** Yes — `fm` can split across pathways (e.g. mixed renal + hepatic). Unattributed fraction is allometry-only and **flagged**.

**Enough mechanisms?** For 8 demo drugs: **yes**. For next-phase ~50 drugs: **no** — need more published TM50/Hill (e.g. CYP2D6, CYP1A2, CYP2C9/19, UGT1A1, tubular secretion, plasma esterases) or explicit data-gap abstention when no curve exists.

### 2. Reasoning traces during loading?

**Yes, shown to the end user.**

- Backend: `on_step` callback streams model text + tool labels.
- `/calculate/stream` SSE events: `step` / `done` / `error`.
- Frontend: stage checklist + console lines (`handleStep`) + rotating reassurance copy.
- Not a full token stream of every thought — one-line reasoning + tool markers.

### 3. Evidence grading?

**Yes — grades A / B / C / D** with `grade_rationale`.

| Grade | Meaning (system prompt / product) |
|-------|-----------------------------------|
| A | Mechanistic estimate passes concordance vs real guideline |
| B | Solid PK, no guideline |
| C | Sparse/uncertain, directional only |
| D | Insufficient data / safety stop |

**Does the user know what grades mean?** **Partially.** Landing chips say “Grades A → D”; result shows letter + model-written rationale. There is **no permanent legend** (A=… B=…) on the result card itself — a UX gap.

### 4. Flags for edge cases

| Edge case | Handled? | How |
|-----------|----------|-----|
| a. Prodrug | **No dedicated logic** | Model *could* free-text flag if retrieved; not in engine or prompt checklist |
| b. Toxic / active metabolites | **Yes (prompted + scored)** | e.g. M6G for morphine; `active_metabolites` + flags |
| c. Obesity | **No** | Weight-only; no LBW/ABW/BMI |
| d. Renal & hepatic impairment | **Partial** | Binary UI toggles → model must pass `renal_function_fraction` / `hepatic_function_fraction` (dev `/pk` hardcodes 0.5; product path relies on LLM mapping) |
| e. Protein binding shift in illness | **No** | % binding reported; no free-fraction correction |
| f. Illness changing assumptions | **Weak** | Free-text flags/assumptions only |
| g. Oral bioavailability | **Yes** | `route=oral` divides by F; always flags adult-F assumption |
| h. Above toxic / below effective | **Yes (engine)** | When thresholds supplied; red “stop” styling in UI for matching keywords |

### 5. Final reasoning for dosage vs guideline?

**Yes.** Result includes: `rationale` (markdown), concordance (guideline dose, ratio, verdict, source), `assumptions`, `uncertainty`, `dose_basis` (inside engine output used by agent), mechanism cards, citations. Preloaded chat also answers “How does this compare to the guideline?”

### 6. Follow-up questions / preloaded Q&A?

**Yes.**
- Preloaded Q&A built from grade_rationale, concordance, flags, assumptions (no extra API cost).
- Suggestion chips + free-text `/chat` grounded in case + recommendation (no tools on chat path).

### 7. Cache retrieval system?

**Not a drug/PK result cache.**  
What exists:
- Anthropic **prompt caching** (`cache_control: ephemeral`) on orchestrator + retrieval loops.
- No Redis/DB/file cache of dossiers or prior doses (explicitly deferred in CLAUDE.md).

### 8. Max turns agent ↔ subagents?

| Loop | Default `max_turns` |
|------|---------------------|
| Orchestrator `run_case` | **12** |
| Retrieval `fetch` | **5** (tight budget; force submit on last turn) |
| Retrieval tool-call budget (prompt) | ≤3 retrieval tools then submit |
| Orchestrator `web_search` | max_uses **2** |

### 9. Only 3 constants — enough for 50 drugs?

**Not enough for breadth.** Phase-2 plan of reusing 3 curves works only for drugs that truly clear by GFR / CYP3A4 / UGT2B7. Expanding to 50 drugs needs either more published ontogeny constants or systematic grade-C/D abstention for unmapped enzymes. **Do not invent TM50/Hill.**

Priority adds if literature supports: CYP2D6, CYP1A2, CYP2C9, CYP2C19, UGT1A1, renal tubular secretion, maybe plasma esterases.

### 10. Curated drug list for demo?

**Good demo set** — eight drugs, three pathways, four exposure archetypes, deliberate edges (NTI→TDM, M6G, time>MIC proxy, oral F, Cmax aminoglycoside underdose).

| Stage | Drugs |
|-------|-------|
| 1 | midazolam, vancomycin, morphine |
| 2 | gentamicin, amikacin, fentanyl, ampicillin, clindamycin |

**Keep for demo.** Optional polish: drop one of the near-duplicate aminoglycosides if time is tight; do not add digoxin/sildenafil/acetaminophen (explicitly excluded — empirical dosing not exposure-matched).

### 11. Frontend bugs / issues found

| Severity | Issue |
|----------|--------|
| Medium | **Grade legend missing** on result — letter alone is opaque without hover/help |
| Medium | **Impairment is binary**; eGFR 85 / obesity weight scenarios cannot be expressed accurately |
| Medium | **Neonate UX**: age in years only (0.014 yr for day 5 is clumsy); GA field only, no postnatal age days field |
| Medium | **Renal/hepatic on product path** depend on LLM to map bool → 0.5 fraction (unlike explicit `/pk` mapping) — inconsistent |
| Low | Form can submit with empty/NaN age or weight (no client-side validation) |
| Low | Free-text drug not allowed (dropdown only) — fine for demo, limits exploration |
| Low | Console is `overflow:hidden` (capped lines) — older steps disappear rather than scroll |
| Low | `mdToHtml` is minimal (bold + newlines only); list-heavy rationales render flat |
| Low | Preloaded Q&A renders as assistant bubbles without interactive expand/collapse |
| Info | Loading stages are **heuristic** (regex on step text), not true backend stage IDs — can desync if wording changes |
| Info | No obesity / BSA / ideal body weight controls |

No show-stopping JS syntax errors found in static review; structure is coherent (landing → calc → SSE load → result + chat).

---

## Verification commands used

```bash
git checkout -b eval   # from master
cd backend && python3 test_pk.py   # all structural tests passed
```

---

## Satisfaction gate (checklist)

**Ask user:** Are you satisfied with tasks 0–2 results? If yes, proceed toward task 3 (validation set) only after explicit go-ahead. Task 3 says never merge validation branch to master.
