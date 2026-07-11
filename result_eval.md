# PaedScale validation eval (combined)

**Branch:** `validation-eval` — harness only; **never merge to master.**  
**Data:** [`validation_set/results.csv`](validation_set/results.csv) (60 rows) · raw log: `result.md`  
**Scenarios:** neonate PNA 5d · 2y ♀ eGFR 85 · obese 1y 14 kg  

---

## Executive performance summary

| Metric | Value |
|--------|------:|
| Scenarios | **60** (20 drugs × 3) |
| Numeric dose + ratio | **53** |
| Null dose (no concordance ratio) | **7** |
| **Strict band 0.67×–1.5×** (of dosed) | **32/53 (60%)** |
| **Wide band 0.5×–2×** (of dosed) | **51/53 (96%)** |
| Strict of all 60 | 32/60 (53%) |
| Wide of all 60 | 51/60 (85%) |

### Grade distribution

| Grade | Count | Meaning |
|-------|------:|---------|
| A | 3 | Passes concordance vs real guideline |
| B | 46 | Solid PK / guideline-anchored, caveats |
| C | 7 | Sparse/uncertain, directional |
| D | 4 | Insufficient / safety stop / abstain |

### Tokens (51 instrumented cases; batch 1 of 9 not logged)

| Component | Tokens |
|-----------|--------:|
| Orchestrator output | 209,739 |
| Retrieval output | 79,479 |
| Cache read | 1,551,070 |
| **Generation total** (uncached in + all out) | **310,515** |

### Headline read

- **System-level performance is strong on the wide band (~96% of dosed cases).** The agent usually lands a clinically defensible starting dose when it emits a number.
- **Strict band (~60%) is moderate** — many intentional guideline overrides for aminoglycosides, β-lactams, and high pediatric CL drugs; not pure engine arithmetic failure.
- **Dominant grade is B** — honest about PD assumptions, TDM, and engine vs guideline tension.
- **Null-dose cases** are mostly titration opioids (fentanyl/midazolam) or indication mismatch (caffeine outside AOP).

### Top failure modes (strict band / null dose)

1. **Cmax aminoglycoside under-prediction** then guideline-anchor — gentamicin, amikacin  
2. **time>MIC daily-dose proxy** — ampicillin, meropenem, cefotaxime (ratios often at 1.5–2×)  
3. **Titration drugs, no fixed mg/kg/day** — midazolam, fentanyl  
4. **Michaelis–Menten / null CL** — phenytoin  
5. **Pediatric CL higher than adult allometry** — fluconazole neonate extreme miss  
6. **Off-label age for indication** — caffeine / ondansetron outside neonate → D or weak  

---

## By scenario

| Scenario | n | dosed | strict | wide | grades |
|----------|--:|------:|--------|------|--------|
| `neonate_5d` | 20 | 19 | 11/19 (58%) | 17/19 (89%) | {'B': 17, 'A': 1, 'D': 2} |
| `child_2y_egfr85` | 20 | 17 | 11/17 (65%) | 17/17 (100%) | {'B': 14, 'D': 1, 'A': 1, 'C': 4} |
| `obese_1y_14kg` | 20 | 17 | 10/17 (59%) | 17/17 (100%) | {'B': 15, 'D': 1, 'C': 3, 'A': 1} |

## By pathway group

| Pathway group | n cases | strict (dosed) | wide (dosed) |
|---------------|--------:|----------------|--------------|
| cyp | 30 | 16/23 (70%) | 22/23 (96%) |
| renal_gfr | 27 | 15/27 (56%) | 26/27 (96%) |
| ugt | 3 | 1/3 (33%) | 3/3 (100%) |

---

## Strict-band fails (dosed but outside 0.67–1.5×)

| drug | scenario | ratio | grade |
|------|----------|------:|-------|
| acyclovir | child_2y_egfr85 | 2.0 | B |
| acyclovir | obese_1y_14kg | 2.0 | B |
| ampicillin | child_2y_egfr85 | 1.667 | B |
| ampicillin | neonate_5d | 2.0 | B |
| cefotaxime | obese_1y_14kg | 2.0 | B |
| fluconazole | neonate_5d | 0.083 | B |
| gentamicin | child_2y_egfr85 | 0.545 | C |
| ibuprofen | obese_1y_14kg | 2.0 | B |
| levetiracetam | neonate_5d | 0.5 | B |
| meropenem | child_2y_egfr85 | 2.0 | B |
| meropenem | neonate_5d | 2.0 | B |
| meropenem | obese_1y_14kg | 2.0 | B |
| metronidazole | neonate_5d | 2.0 | B |
| midazolam | neonate_5d | 2.0 | B |
| morphine | neonate_5d | 1.667 | B |
| morphine | obese_1y_14kg | 1.771 | B |
| ondansetron | neonate_5d | 0.133 | D |
| ondansetron | obese_1y_14kg | 0.5 | B |
| phenytoin | child_2y_egfr85 | 0.625 | C |
| theophylline | child_2y_egfr85 | 0.5 | C |
| vancomycin | obese_1y_14kg | 0.667 | B |

## Null dose (no ratio)

| drug | scenario | grade |
|------|----------|-------|
| caffeine | child_2y_egfr85 | D |
| caffeine | obese_1y_14kg | D |
| fentanyl | child_2y_egfr85 | C |
| fentanyl | neonate_5d | B |
| fentanyl | obese_1y_14kg | B |
| midazolam | child_2y_egfr85 | B |
| midazolam | obese_1y_14kg | B |

---

## Full results table

See also CSV: `validation_set/results.csv`.

| drug | scenario | grade | dose | guideline | ratio | strict | wide | pathway | metric |
|------|----------|-------|------|-----------|-------|--------|------|---------|--------|
| acyclovir | child_2y_egfr85 | B | 60.0 | 30.0 | 2.0 | FAIL | PASS | renal_gfr | css |
| acyclovir | neonate_5d | B | 60.0 | 60.0 | 1.0 | PASS | PASS | renal_gfr | css |
| acyclovir | obese_1y_14kg | B | 60.0 | 30.0 | 2.0 | FAIL | PASS | renal_gfr | css |
| amikacin | child_2y_egfr85 | B | 15.0 | 15.0 | 1.0 | PASS | PASS | renal_gfr | cmax |
| amikacin | neonate_5d | B | 15.0 | 15.0 | 1.0 | PASS | PASS | renal_gfr | cmax |
| amikacin | obese_1y_14kg | B | 15.0 | 19.0 | 0.789 | PASS | PASS | renal_gfr | cmax |
| ampicillin | child_2y_egfr85 | B | 200.0 | 120.0 | 1.667 | FAIL | PASS | renal_gfr | time_mic |
| ampicillin | neonate_5d | B | 200.0 | 100.0 | 2.0 | FAIL | PASS | renal_gfr | time_mic |
| ampicillin | obese_1y_14kg | B | 200.0 | 150.0 | 1.333 | PASS | PASS | renal_gfr | time_mic |
| caffeine | child_2y_egfr85 | D | — | 5.0 | — | N/A | N/A | cyp1a2 | css |
| caffeine | neonate_5d | A | 5.0 | 5.0 | 1.0 | PASS | PASS | cyp1a2 | css |
| caffeine | obese_1y_14kg | D | — | 5.0 | — | N/A | N/A | cyp1a2 | css |
| cefotaxime | child_2y_egfr85 | B | 225.0 | 150.0 | 1.5 | PASS | PASS | renal_gfr | time_mic |
| cefotaxime | neonate_5d | B | 100.0 | 100.0 | 1.0 | PASS | PASS | renal_gfr | time_mic |
| cefotaxime | obese_1y_14kg | B | 300.0 | 150.0 | 2.0 | FAIL | PASS | renal_gfr | time_mic |
| clindamycin | child_2y_egfr85 | A | 40.0 | 30.0 | 1.333 | PASS | PASS | cyp3a4 | css |
| clindamycin | neonate_5d | B | 15.0 | 15.0 | 1.0 | PASS | PASS | cyp3a4 | css |
| clindamycin | obese_1y_14kg | B | 30.0 | 30.0 | 1.0 | PASS | PASS | cyp3a4 | css |
| fentanyl | child_2y_egfr85 | C | — | 0.048 | — | N/A | N/A | cyp3a4 | css |
| fentanyl | neonate_5d | B | — | 0.024 | — | N/A | N/A | cyp3a4 | css |
| fentanyl | obese_1y_14kg | B | — | 0.048 | — | N/A | N/A | cyp3a4 | css |
| fluconazole | child_2y_egfr85 | B | 6.0 | 6.0 | 1.0 | PASS | PASS | renal_gfr | css |
| fluconazole | neonate_5d | B | 1.0 | 12.0 | 0.083 | FAIL | FAIL | renal_gfr | css |
| fluconazole | obese_1y_14kg | B | 6.0 | 6.0 | 1.0 | PASS | PASS | renal_gfr | css |
| gentamicin | child_2y_egfr85 | C | 3.0 | 5.5 | 0.545 | FAIL | PASS | renal_gfr | cmax |
| gentamicin | neonate_5d | B | 5.0 | 4.0 | 1.25 | PASS | PASS | renal_gfr | cmax |
| gentamicin | obese_1y_14kg | C | 7.0 | 7.0 | 1.0 | PASS | PASS | renal_gfr | cmax |
| ibuprofen | child_2y_egfr85 | B | 17.0 | 20.0 | 0.85 | PASS | PASS | cyp2c9 | css |
| ibuprofen | neonate_5d | B | 10.0 | 10.0 | 1.0 | PASS | PASS | cyp2c9 | css |
| ibuprofen | obese_1y_14kg | B | 40.0 | 20.0 | 2.0 | FAIL | PASS | cyp2c9 | css |
| levetiracetam | child_2y_egfr85 | B | 55.0 | 40.0 | 1.375 | PASS | PASS | renal_gfr | css |
| levetiracetam | neonate_5d | B | 20.0 | 40.0 | 0.5 | FAIL | PASS | renal_gfr | css |
| levetiracetam | obese_1y_14kg | A | 50.0 | 40.0 | 1.25 | PASS | PASS | renal_gfr | css |
| meropenem | child_2y_egfr85 | B | 120.0 | 60.0 | 2.0 | FAIL | PASS | renal_gfr | time_mic |
| meropenem | neonate_5d | B | 120.0 | 60.0 | 2.0 | FAIL | PASS | renal_gfr | time_mic |
| meropenem | obese_1y_14kg | B | 120.0 | 60.0 | 2.0 | FAIL | PASS | renal_gfr | time_mic |
| metronidazole | child_2y_egfr85 | B | 30.0 | 30.0 | 1.0 | PASS | PASS | cyp2c9,cyp3a4 | css |
| metronidazole | neonate_5d | B | 30.0 | 15.0 | 2.0 | FAIL | PASS | cyp2c9,cyp3a4 | css |
| metronidazole | obese_1y_14kg | B | 30.0 | 30.0 | 1.0 | PASS | PASS | cyp2c9,cyp3a4 | css |
| midazolam | child_2y_egfr85 | B | — | 1.44 | — | N/A | N/A | cyp3a4 | css |
| midazolam | neonate_5d | B | 1.44 | 0.72 | 2.0 | FAIL | PASS | cyp3a4 | css |
| midazolam | obese_1y_14kg | B | — | 1.44 | — | N/A | N/A | cyp3a4 | css |
| morphine | child_2y_egfr85 | B | 0.6 | 0.48 | 1.25 | PASS | PASS | ugt2b7 | css |
| morphine | neonate_5d | B | 0.2 | 0.12 | 1.667 | FAIL | PASS | ugt2b7 | css |
| morphine | obese_1y_14kg | B | 0.85 | 0.48 | 1.771 | FAIL | PASS | ugt2b7 | css |
| ondansetron | child_2y_egfr85 | B | 0.398 | 0.3 | 1.327 | PASS | PASS | cyp3a4,cyp1a2,cyp2d6 | css |
| ondansetron | neonate_5d | D | 0.04 | 0.3 | 0.133 | FAIL | FAIL | cyp3a4,cyp1a2,cyp2d6 | css |
| ondansetron | obese_1y_14kg | B | 0.15 | 0.3 | 0.5 | FAIL | PASS | cyp3a4,cyp1a2,cyp2d6 | css |
| phenobarbital | child_2y_egfr85 | B | 4.0 | 5.0 | 0.8 | PASS | PASS | cyp2c19,cyp2c9 | css |
| phenobarbital | neonate_5d | B | 4.0 | 5.0 | 0.8 | PASS | PASS | cyp2c19,cyp2c9 | css |
| phenobarbital | obese_1y_14kg | B | 4.0 | 5.0 | 0.8 | PASS | PASS | cyp2c19,cyp2c9 | css |
| phenytoin | child_2y_egfr85 | C | 5.0 | 8.0 | 0.625 | FAIL | PASS | cyp2c9 | css |
| phenytoin | neonate_5d | D | 5.0 | 5.0 | 1.0 | PASS | PASS | cyp2c9 | css |
| phenytoin | obese_1y_14kg | C | 8.0 | 8.0 | 1.0 | PASS | PASS | cyp2c9 | css |
| theophylline | child_2y_egfr85 | C | 6.0 | 12.0 | 0.5 | FAIL | PASS | cyp1a2 | css |
| theophylline | neonate_5d | B | 4.0 | 4.0 | 1.0 | PASS | PASS | cyp1a2 | css |
| theophylline | obese_1y_14kg | C | 12.0 | 12.0 | 1.0 | PASS | PASS | cyp1a2 | css |
| vancomycin | child_2y_egfr85 | B | 60.0 | 45.0 | 1.333 | PASS | PASS | renal_gfr | auc |
| vancomycin | neonate_5d | B | 30.0 | 30.0 | 1.0 | PASS | PASS | renal_gfr | auc |
| vancomycin | obese_1y_14kg | B | 40.0 | 60.0 | 0.667 | FAIL | PASS | renal_gfr | auc |

---

## PK engine assessment

### Verdict: **keep the engine — it is good for its design purpose**

The deterministic layer (`pk_engine.py`) does **allometry × maturation exposure matching**. That is the right scientific core for a starting-dose tool. Eval misses are mostly **expected limits of that model**, not broken arithmetic (`test_pk.py` still green).

| Evidence | Interpretation |
|----------|----------------|
| Wide concordance **96%** of dosed | Engine + agent (guideline, flags, grade) is **defensible decision support** |
| Strict concordance **60%** of dosed | Pure exposure-match ≠ pediatric label practice for several archetypes |
| Grade B majority | System correctly refuses false certainty |
| Known AG / time>MIC / MM patterns reappeared | Matches CLAUDE.md known limits — model is self-consistent |

### Keep as-is (do not rewrite core math)

| Piece | Why |
|-------|-----|
| WT^0.75 CL + WT^1 Vd + Hill MF | Textbook; validated on clean archetypes |
| time_mic as css-proxy **with flag** | Honest; fT>MIC is interval/infusion driven |
| Refuse unknown pathways | Cite-or-abstain |
| No silent obesity dose rewrite | Flags/hints only |

### Validated engine limits (agent should compensate — and usually did)

| Limit | Eval signal | Change engine? |
|-------|-------------|----------------|
| **Cmax AG underdose** (adult Vd-scale vs larger pediatric Vd/kg) | gentamicin/amikacin; agent often overrides to guideline | Optional later: pediatric Vd/kg or peak-target helper — **not required if agent flags** |
| **time>MIC daily dose is proxy** | β-lactams at edge of band after guideline | Keep proxy + grade ceiling B |
| **No absolute dose without adult mg/day** | midazolam/fentanyl titration | Engine OK; guideline-anchor |
| **Michaelis–Menten** | phenytoin null CL → C/D | **Do not** force linear CL; document unsupported |
| **Fluconazole under-predict** | neonate extreme ratio | Optional empiric pediatric CL — only with cited source |
| **Obesity** | high wt-for-age | Keep edge-case flags only |

### Recommended changes (product)

1. **Docs (this eval + CLAUDE.md)** — document failure modes; done with this file + CLAUDE update.  
2. **Agent prompt** — when engine ≪ guideline for aminoglycosides / β-lactams, prefer guideline starting dose + flag exposure-target mismatch (strengthen).  
3. **Engine (optional, later)** — pediatric Vd override for `cmax`; explicit “MM kinetics unsupported” refuse for phenytoin-class.  
4. **Do not** invent TM50/Hill or hardcode product-path seed PK.

### Bottom line

> **PK engine: keep.** Improve concordance with agent/guideline discipline and selective future helpers for Cmax Vd and non-linear PK — **not** a rewrite of Anderson–Holford maturation math.

---

## Method notes

- Live agent (`run_case`) vs harness oracles in `validation_set/` (backend never imports them).  
- Concordance vs hand-anchored guideline midpoints in `guideline_data.json` (not always identical to agent’s live web_search guideline).  
- Ratio = recommended_dose / harness_guideline.  
- Batch 1 token usage not in `usage_log.jsonl`.  
- Parallel workers w1–w4 for drugs 7–20.

---

*Generated from combined validation runs on `validation-eval`.*
