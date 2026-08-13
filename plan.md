# Part 1 — Usable starting dose

**Branch:** `usable-starting-dose` (from `master`)  
**Out of scope:** TDM / Bayesian update (deferred). DDI Explorer (not building).

PaedScale already emits a cited, graded starting dose. This plan makes that number something a clinician can take to a consultant: rounded to an administerable amount, printed as a one-page case card, faster on a repeat drug, and using only published maturation curves.

---

## Current state

| Piece | Today |
|---|---|
| Engine dose | Raw `recommended_dose_mg_per_day` (e.g. 47.32). No rounding, no mL. |
| Result UI | Hero shows `mg/kg/day` + `mg/day`. No print/export. |
| PK cache | In-process LRU, keyed `drug\|indication`. Retrieval skips PubMed on hit; orchestrator still always calls `retrieve_drug_data` (one extra Opus round). |
| MATURATION | 8 keys in `engine/constants.py`. Three are well-cited (GFR, CYP3A4, UGT2B7). Five (`cyp1a2`, `cyp2d6`, `cyp2c9`, `cyp2c19`, `ugt1a1`) are marked approximate / “Anderson–Holford style” and are **not** yet validated as published TM50/Hill. |

TDM is **not** in this plan.

---

## What we will ship

### A. Formulation rounding (deterministic, post-engine)

Python does the arithmetic. The model must not invent a rounded dose.

- New module: `backend/engine/formulation.py` (no I/O, no LLM).
- After `submit_recommendation`, `attach_administration(rec, case)` fills `recommendation.administration`.
- Engine fields `final_dose_*` stay the **unrounded** estimate. Rounding is a separate, labelled layer.
- Rules (not per-drug PK tables):
  - Practical increment from dose size: `<1 mg → 0.05`, `<5 → 0.1`, `<20 → 0.5`, `<100 → 1`, `<500 → 5`, else `10`.
  - If an interval is parseable (`q8h`, `every 8 hours`, BID/TID/QID) or the engine suggested an interval in hours → also round **per dose**.
  - Optional clinician-entered `formulation_mg_per_ml` → volume in mL per dose. No invented vial strengths.
  - If `|rounded − engine| / engine > 10%`, set `administration.flag` (shown, does not change the grade).
- Blocked / grade-D / null dose → `administration: null`.

### B. One-page case card

- Same result view. Button: **Print case card**.
- Print CSS: hide nav, chat, loader chrome; keep case identity, dose (engine + give), grade, concordance, flags, citations, disclaimer.
- `window.print()` — no new backend, no PDF library.
- Disclaimer stays visible: decision support, not a prescription.

### C. Latency on repeat drugs

Cache already stores live cited dossiers. The remaining waste is (1) keying by indication so `vancomycin` ≠ `vancomycin|sepsis`, and (2) the orchestrator still paying a retrieve turn.

- Cache **primary key = generic drug name** (adult CL/Vd is not indication-specific). `get(drug, indication)` still works; indication is ignored for lookup.
- On `run_case` start: if a valid cached dossier exists, latch `pk_ok`, inject the dossier into the user message, and tell the orchestrator **not** to call `retrieve_drug_data` unless core PK is missing.
- Stream step: `pk_cache hit — skipped live retrieval`.
- If the model calls retrieve anyway, `retrieval.fetch` still returns the cache hit in milliseconds.
- First-ever drug on a dyno is unchanged (live PubMed + openFDA). Cite-or-abstain unchanged: uncited / partial dossiers still cannot enter the cache.

### D. TM50 / Hill — extract, validate, then maybe expand

**Do not add a curve from memory.**

1. Extractor subagent writes `docs/maturation_extract.json` from papers it actually opened.
2. Validator subagent scores each row (PMID/DOI exists, numbers match, equation is the engine Hill, PMA vs PNA conversion is explicit).
3. Parent (this session) re-checks every **include** against the opened source.
4. Decision rule:
   - **Keep** only rows both validators accept, with a real citation, Hill sigmoid, TM50 in PMA weeks (or a documented conversion).
   - **Remove or leave unused** any existing key whose TM50/Hill cannot be sourced (the five approximate curves). Removing a key is allowed: the engine already refuses unknown pathways (cite-or-abstain). Tests that require those keys will be updated.
   - **Add** new keys only if a primary paper publishes TM50 + Hill. Candidates to search (not promises): CYP2B6, CYP2C8, CES1, UGT1A9, tubular secretion. Reject piecewise Simcyp / age-bin / linear models that do not publish Hill parameters.
5. After a key change: update `skills/mechanism.md` and the retrieval system `fm` key list. Never invent TM50 to “fill” a gap.

**D is done (2026-08-14).** Extractor + validator + parent all opened the same primaries.

- **Keep** `renal_gfr` 47.7 / 3.40 (Rhodin PMID 18846389).
- **Replace** `cyp3a4` → 73.6 / 3.0 (Anderson/Larsson PMID 20704661). Old 55.4 / 1.83 was unsourced.
- **Replace** `ugt2b7` → 54.2 / 3.92 (Anand PMID 18723857). Old 88.3 / 1.90 was unsourced (88.8 days is Anand *volume*, not CL).
- **Remove** `cyp1a2`, `cyp2d6`, `cyp2c9`, `cyp2c19`, `ugt1a1` — no opened paper printed both TM50 and Hill.
- **Do not add** `oat1_3` — Cristea TM50 is weeks **PNA**; `+40` is not in the paper (validator: needs_review).

Parent audit matches validator `docs/maturation_validate.md`. These edits are in `backend/engine/constants.py`.

---

## File plan

| File | Change |
|---|---|
| `backend/engine/formulation.py` | **New.** Increment, interval parse, `attach_administration`. |
| `backend/engine/pk_cache.py` | Drug-only key; `get`/`set` keep the indication arg for API stability. |
| `backend/agents/agent.py` | Prefetch cache → inject dossier; attach administration on submit. |
| `backend/api/main.py` | Optional `formulation_mg_per_ml` on `Case`. |
| `frontend/index.html` | Strength field; give-line on result; print button + `@media print`. |
| `backend/tests/test_pk.py` | Rounding, interval parse, cache key, administration-on-submit. |
| `backend/engine/constants.py` | 3 published keys only (Rhodin / Anderson-Larsson / Anand). |
| `backend/skills/mechanism.md` | Pathway key list after D. |
| `docs/maturation_extract.json` + `_validate.json` | Harness notes, not product path. |

Product code still must not import `validation_set/` or `eval_data/` on `/calculate`.

---

## Tests (must pass before claiming done)

- Increment table + 10% flag.
- `q8h` / BID / engine `suggested_interval_h` → per-dose.
- Volume only when `formulation_mg_per_ml` is set and > 0.
- Blocked rec → `administration is None`.
- Cache: `get("vanco", "sepsis")` hits a `set("vanco", None, …)` entry; uncited still rejected.
- Existing engine tests still pass (`python3 -m tests.test_pk` from `backend/`).
- Unknown pathway still raises.
- After TM50 edits: monotonic MF; no approximate source strings left in `MATURATION`.

## UI check

Use `playwright-web-check` on the local result view: rounding line, optional mL, print button, print CSS does not hide the dose, mobile viewport still readable.

---

## Order of work

1. `formulation.py` + tests.  
2. Wire `attach_administration` + optional form field + result “give” line.  
3. Printable case card.  
4. Cache key + orchestrator prefetch.  
5. TM50: wait for extract → validate subagent → parent audit → edit `constants.py` only if accepted.  
6. Browser check.

No TDM in this branch.
