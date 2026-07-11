# PaedScale validation results

Branch: `validation-eval`. Harness-only. **Never merge this branch to master.**

## Setup
- `validation_set/drug_data.json` — 20 drugs (PK + mechanism truth)
- `validation_set/guideline_data.json` — 3 scenarios × 20 drugs
- Backend has **zero** references to `validation_set`
- CLAUDE.md rule 4: never merge `validation-eval` → master

### Scenarios
| Key | Description |
|-----|-------------|
| `neonate_5d` | Term neonate, PNA 5 days, 3.5 kg |
| `child_2y_egfr85` | 2 yo female, eGFR 85, 12 kg (mild renal flag) |
| `obese_1y_14kg` | 1 yo, 14 kg (obesity edge) |

### Drug list (20)
vancomycin, gentamicin, amikacin, ampicillin, meropenem, cefotaxime, acyclovir, levetiracetam, midazolam, fentanyl, clindamycin, morphine, caffeine, theophylline, phenytoin, ibuprofen, phenobarbital, fluconazole, metronidazole, ondansetron

---

## Live runs (append below)

Starting batch: **vancomycin, midazolam, morphine** × 3 scenarios (9 cases).

## vancomycin · `neonate_5d`
- **Grade:** B · **Dose:** 30 mg/kg/day · **85.6s**
- **Concordance:** guideline 30 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 1.0 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 4 · rationale: True
- **Flags:**
  - NEONATE: term, PNA 5 days — PMA/PNA-stratified dosing applied
  - AUC-guided TDM MANDATORY (target AUC24/MIC >= 400); check level and adjust
  - Engine AUC dose-rate (26.08 mg/kg/day) below effective-dose floor (30) — final anchored to guideline
  - STARTING dose only — not a prescription; confirm renal function / serum creatinine
  - Serum creatinine not provided; renal function assumed normal
  - Exposure-matching PD assumption (adult AUC target applied to neonate)
  - 10% of clearance unattributed to maturing pathway (size-scaled, assumed adult-like)
  - Protein binding controversial (0-98%); ~50% assumed
- **Grade rationale:** Live FDA-label PK retrieved and allometry×GFR-maturation engine ran successfully (grade A conditions), but final dose was anchored to external neonatal guideline rather than the raw engine output because the engine's AUC dose-rate matching (26.08 mg/kg/day) fell below the effective-dose floor and does not capture the neonate's elevated weight-normalized Vd and standard AUC24/MIC>=400 target. Downg

## vancomycin · `child_2y_egfr85`
- **Grade:** B · **Dose:** 60 mg/kg/day · **59.5s**
- **Concordance:** guideline 45 · ratio 1.333 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 1.0 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Flags:**
  - SUB-THERAPEUTIC ENGINE OUTPUT: adult-AUC-matching gave 37.6 mg/kg/day, ~0.5–0.6x pediatric guideline of 60–80 mg/kg/day; engine dose NOT recommended — overridden to guideline.
  - EXPOSURE-MATCHING PD ASSUMPTION invalid for vancomycin pediatrics: children clear vancomycin faster per kg than adult scaling predicts.
  - MANDATORY AUC-GUIDED TDM: target AUC24/MIC 400–600; trough-only monitoring no longer recommended; individualize via Bayesian software.
  - RENAL IMPAIRMENT (eGFR 85, fraction 0.85): dose anchored to LOWER end (60 not 80 mg/kg/day); reassess interval per renal function and AUC.
  - NEPHROTOXICITY RISK: avoid concomitant nephrotoxins (aminoglycosides, amphotericin, calcineurin inhibitors); monitor renal function.
  - PROTEIN BINDING controversial in literature (0–98% reported; ~50% used); minor impact for renally cleared drug but noted.
  - STARTING DOSE ONLY — decision support, not a prescription; confirm max dose typically ≤3000 mg/day.
- **Grade rationale:** Core PK is high-confidence (FDA label, renal elimination, no metabolites) and a strong pediatric guideline concordance base exists (multiple 2020-consensus-aligned sources). Downgraded from A because: (1) the allometry engine and pediatric guidelines diverge nearly 2-fold — adult-AUC-matching materially under-doses children for vancomycin, so I deviated from the engine toward the guideline; (2) re

## vancomycin · `obese_1y_14kg`
- **Grade:** B · **Dose:** 40 mg/kg/day · **48.6s**
- **Concordance:** guideline 60 · ratio 0.667 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 1.0 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Flags:**
  - NARROW THERAPEUTIC INDEX — mandatory TDM: monitor AUC24 (target 400–600 mg·h/L); do not use as a fixed regimen.
  - STARTING dose only — escalate toward 60 mg/kg/day for confirmed/suspected invasive MRSA, CNS infection, endocarditis, or febrile neutropenia per guidelines.
  - PD exposure-matching assumption: pediatric AUC24/MIC target assumed transferable from adult PK.
  - ASSUMED TERM gestation — PMA not supplied for child <2 yr; verify preterm history.
  - High weight-for-age (14 kg vs ~10 kg ideal at 1 y); vancomycin conventionally dosed on total body weight in children — verify weight and refine by TDM.
  - Nephrotoxicity risk rises with high AUC exposure; avoid concomitant nephrotoxins and monitor renal function.
  - Infuse no faster than 10 mg/min (over ≥60 min) to reduce infusion-related reactions.
- **Grade rationale:** Core PK is high-confidence FDA-label data but delivered from cache rather than a live source; deterministic allometry×GFR-maturation engine output (39 mg/kg/day) is strongly concordant with published pediatric guidelines (40–60 mg/kg/day), so recommendation is well-supported but not grade A (cache PK + PD exposure-matching assumption + no live retrieval).

## midazolam · `neonate_5d`
- **Grade:** B · **Dose:** 1.44 mg/kg/day · **108.9s**
- **Concordance:** guideline 0.72 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Flags:**
  - PROTEIN BINDING 97% is high and patient is a neonate — free (unbound) fraction may rise with low neonatal albumin/illness; total-concentration targets can mislead.
  - ACTIVE METABOLITE: 1'-hydroxymidazolam is active and RENALLY cleared — parent CL does not equal effect; risk of sedative accumulation, magnified in any renal impairment. Monitor for prolonged sedation.
  - NO IV LOADING/BOLUS in neonates — rapid IV administration linked to severe hypotension and seizures, especially with concomitant fentanyl.
  - ACCUMULATION RISK: immature CYP3A4 -> low clearance; reassess rate after 24 h and titrate down to lowest effective dose.
  - PD/EXPOSURE-MATCHING ASSUMPTION: dose is titrated to clinical sedation score (e.g., COMFORT/N-PASS), not to a plasma target — TDM not routine; titrate to effect with continuous respiratory/BP monitoring.
  - BENZYL ALCOHOL: some IV midazolam formulations contain benzyl alcohol — use a preservative-free product in neonates where possible.
  - RESPIRATORY DEPRESSION: additive with opioids/other CNS depressants — continuous monitoring required, ideally intubated/ventilated setting.
- **Grade rationale:** Live PK retrieved (CYP3A4-anchored maturation is the reference midazolam model), and a strong neonatal guideline anchor exists (FDA label + PICU/Cochrane sources). Downgraded from A because the engine could not return an absolute dose (sedation is titration-based, no fixed adult mg/kg/day), so the final number is guideline-anchored rather than fully engine-derived, and free-fraction/metabolite unc

## midazolam · `child_2y_egfr85`
- **Grade:** B · **Dose:** None mg/kg/day · **55.3s**
- **Concordance:** guideline 1.44 · ratio None · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 7 · rationale: True
- **Flags:**
  - RENAL impairment: parent CL is hepatic (CYP3A4) and unaffected, BUT active metabolite 1'-hydroxymidazolam glucuronide is renally cleared and may accumulate — risk of prolonged/deepened sedation with repeated dosing or infusion; extend intervals and monitor.
  - ACTIVE METABOLITE: parent clearance ≠ pharmacologic effect; effect may outlast parent-drug PK.
  - HIGH PROTEIN BINDING (97%): free-fraction shifts possible in critical illness/hypoalbuminemia — not a neonate here, lower concern.
  - TITRATED ENDPOINT: dose is bolus-and-titrate, not a fixed daily dose; exposure–response PD assumption applies.
  - RESPIRATORY DEPRESSION: continuous pulse oximetry; have flumazenil and airway equipment available; reduce dose if combined with opioids/other CNS depressants.
- **Grade rationale:** PK from cache (not live retrieval) with moderate-high confidence on core parameters, but no adult mg/kg/day target exists because IV sedation is titrated, not a fixed daily regimen. Dose is anchored to a well-established pediatric IV guideline rather than an allometric absolute; concordance is qualitative. Held at B (not A) due to cache source, wide inter-individual PK variability, and the exposur

## midazolam · `obese_1y_14kg`
- **Grade:** B · **Dose:** None mg/kg/day · **54.5s**
- **Concordance:** guideline 1.44 · ratio None · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 3 · rationale: True
- **Flags:**
  - TITRATED DOSE - not a fixed mg/kg/day; titrate to clinical effect with continuous monitoring
  - ACTIVE METABOLITE: alpha-hydroxymidazolam is renally cleared and accumulates in renal failure - watch with prolonged infusion or if renal function declines
  - HIGH PROTEIN BINDING (97%) - free fraction may rise in hypoalbuminemia/critical illness/neonatal states
  - HIGH-EXTRACTION HEPATIC DRUG - clearance depends on hepatic perfusion; reduced by cirrhosis, low CO, CYP3A4 inhibitors
  - OBESITY/high weight-for-age (14 kg vs ideal ~10 kg) - consider ideal/adjusted body weight to avoid overexposure
  - ASSUMED TERM gestation (PMA not supplied)
  - RESPIRATORY DEPRESSION/airway risk - reduce dose and titrate cautiously if combined with opioids; ensure monitoring and airway rescue capability
  - Cache-mode PK, not live retrieval
- **Grade rationale:** Core PK from cache (Vd, CL, CYP3A4 metabolism, 97% PB, active metabolite) is moderate-high confidence, and an explicit age-matched pediatric guideline exists for the 6mo-5yr band. Downgraded from A because midazolam sedation is titration-based with no fixed mg/kg/day target, so the allometry engine could not solve an absolute dose; the recommendation rests on the guideline per-dose range rather th

## morphine · `neonate_5d`
- **Grade:** B · **Dose:** 0.2 mg/kg/day · **98.1s**
- **Concordance:** guideline 0.12 · ratio 1.667 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.0 · dims: `{'elimination': False, 'pathways': False, 'enzymes': False, 'transporters': False, 'active_metabolites': False, 'protein_binding': False}`
- **Citations:** 6 · rationale: True
- **Flags:**
  - NTI opioid — respiratory depression risk; monitor closely, naloxone available
  - Neonate <1 month — immature UGT2B7 glucuronidation; use lowest dose + extended interval to prevent metabolite accumulation
  - Active metabolite M6G (potent mu-agonist) is renally cleared; immature neonatal GFR may prolong effect — clinical monitoring/TDM as available
  - M3G neuroexcitatory metabolite may accumulate
  - Engine could not solve absolute dose (AUC-driven, no adult daily anchor) — dose is guideline-anchored
  - 21% of clearance size-scaled only (assumed adult-like) — accumulation-risk direction
  - Term status assumed from GA 40 wk
  - Exposure-matching PD assumption
  - Opioid-naive assumption — doses not valid if tolerant
- **Grade rationale:** Live high-confidence adult PK retrieved; engine PK (CL 4% of adult, t½ ~2h) coheres with neonate-specific guidelines that converge tightly on 50–100 mcg/kg IV intermittent / 10 mcg/kg/hr infusion. Not grade A because the AUC-driven engine could not solve an absolute dose (no adult daily anchor), so final dose is guideline-anchored rather than model-derived; neonatal UGT2B7 immaturity + active rena

## morphine · `child_2y_egfr85`
- **Grade:** B · **Dose:** 0.6 mg/kg/day · **54.2s**
- **Concordance:** guideline 0.48 · ratio 1.25 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.0 · dims: `{'elimination': False, 'pathways': False, 'enzymes': False, 'transporters': False, 'active_metabolites': False, 'protein_binding': False}`
- **Citations:** 5 · rationale: True
- **Flags:**
  - RENAL impairment: active metabolite M6G accumulates → start at LOW end (0.05 mg/kg), consider extended interval, monitor for delayed respiratory depression
  - ACTIVE METABOLITE (M6G) not modeled by parent-drug engine — parent CL ≠ effect
  - EXPOSURE-MATCHING PD ASSUMPTION invalid for titrated opioid — do not administer engine AUC-rate as a fixed dose
  - MANDATORY MONITORING: continuous SpO2/respiratory rate, naloxone available; respiratory-depression risk highest first 24-72 h
  - ~21% adult clearance unattributed, size-scaled only — error source in young child
  - Protein binding null — not modeled
  - Decision support only — not a prescription; titrate to effect
- **Grade rationale:** Core PK is high-confidence from a cited human study and the engine applied validated UGT2B7 + GFR maturation curves. Downgraded from A because: (1) morphine is dose-titrated to a PD endpoint, so the engine's AUC-exposure-matching is a weaker basis than for a css/therapeutic-window drug; (2) the active metabolite M6G — the main effector in renal impairment — has its own maturation/renal clearance n

## morphine · `obese_1y_14kg`
- **Grade:** B · **Dose:** 0.85 mg/kg/day · **56.2s**
- **Concordance:** guideline 0.48 · ratio 1.771 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.0 · dims: `{'elimination': False, 'pathways': False, 'enzymes': False, 'transporters': False, 'active_metabolites': False, 'protein_binding': False}`
- **Citations:** 4 · rationale: True
- **Flags:**
  - ACTIVE METABOLITE: M6G is a potent mu-agonist, renally cleared — accumulates in renal impairment; M3G is neuroexcitatory. Monitor even though renal function is normal here.
  - ASSUMED TERM: no PMA supplied for child <2 yr; assumed 40 wk gestation — if preterm, immaturity is understated and dose OVER-estimated.
  - UNATTRIBUTED CLEARANCE: ~21% of adult CL not mapped to a maturing pathway, scaled by size only — error risk in the young.
  - EXPOSURE-MATCHING PD ASSUMPTION: dose derived by matching adult AUC; assumes equal concentration-effect relationship in child.
  - OBESITY/HIGH WEIGHT-FOR-AGE: 14 kg at 1 yr (ideal ~10 kg) — total-body-weight-linear dosing may overestimate exposure; consider adjusted weight and clinical titration.
  - TITRATE-TO-EFFECT: opioid analgesia is titrated to response with respiratory/sedation monitoring; computed value is a STARTING anchor, not a fixed regimen. No fixed mg/kg toxic threshold (tolerance-dependent).
- **Grade rationale:** Core PK (CL, Vd, F, fm) from a well-cited human study (cache, Hasselström & Rane 1993) and applied via validated UGT2B7 (Anderson) and GFR (Rhodin) maturation curves. AUC-matched engine dose (0.85 mg/kg/day) falls squarely within published pediatric guideline ranges (concordance ratio ~1.0). Not grade A because PK was cache- rather than live-retrieved, protein binding was null, and ~21% of clearan

### Batch summary (first 3 drugs × 3 scenarios)
- **n=9** completed (~10 min total; PK cache hit after first retrieve per drug)
- **Concordance (all 9 rows, null dose = fail):** 0.67–1.5× **3/9** · 0.5–2× **7/9**
- **Among 7 with a numeric dose:** 0.67–1.5× **3/7** · 0.5–2× **7/7**
- **Grades:** all **B** (guidelines found but engine often overridden / titration drugs)
- **Mechanism score:** vancomycin **1.0** all scenarios; midazolam **0.5** (pathways/transporters/metabolites miss on synonym/extra keys); morphine **0.0** (agent reported mixed elimination / incomplete structured mechanism vs hepatic+UGT2B7 truth — **bug to watch**)
- **Reasoning quality:** strong flags (TDM, M6G, obesity, high PB, renal OF); citations present; edge_cases + skills used
- **Midazolam gap:** no fixed mg/kg/day when adult daily dose null → agent correctly titrate-flags but concordance metric fails
- finished 2026-07-11T16:25:14+00:00

### After ≥3 drugs — pause for user
Next drugs candidates: gentamicin, ampicillin, caffeine (diverse pathways).  
Subagents only after user OK (~5–6 drugs).
