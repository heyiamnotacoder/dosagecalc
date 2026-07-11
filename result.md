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

## gentamicin · `neonate_5d`
- **Grade:** B · **Dose:** 5 mg/kg/day · **105.4s**
- **Concordance:** guideline 4 · ratio 1.25 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4478 cache_read=19332 | retr in=8 out=2701
- **Flags:**
  - NTI aminoglycoside -> mandatory TDM (peak and trough after first dose); adjust interval to keep trough <1-2 mg/L
  - Cmax:MIC-driven (target peak ~8-12 mg/L neonate) -> peak-optimized extended-interval dosing
  - ENGINE UNDERESTIMATE OVERRIDDEN: engine 3 mg/kg/day q8h scaled Vd by adult size only (0.25 L/kg); neonatal Vd ~0.4-0.5 L/kg -> raw engine dose sub-therapeutic peak; dose raised to guideline 5 mg/kg/day and interval extended to q24h
  - Immature neonatal GFR (maturation factor ~0.37, t1/2 ~3.2 h) -> extended q24h interval for adequate trough clearance
  - 10% of clearance non-renal/unattributed to a maturing pathway (scaled by size only) - minor source of error
  - Assumed term (GA 40w) with normal renal function per case
  - Nephrotoxicity/ototoxicity risk -> monitor renal function and troughs
  - Exposure/PD matching assumption: neonatal peak target (~8-12 mg/L) not identical to adult
- **Grade rationale:** n/a

## gentamicin · `child_2y_egfr85`
- **Grade:** C · **Dose:** 3.0 mg/kg/day · **52.7s**
- **Concordance:** guideline 5.5 · ratio 0.545 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=8 out=3965 cache_read=19114 | retr in=0 out=0
- **Flags:**
  - NTI drug — mandatory TDM: measure peak (Cmax:MIC >=10) and trough; adjust dose and interval to levels.
  - RENAL impairment flagged — organ-function modifier applied to renal pathway; LENGTHEN interval and monitor renal function, auditory/vestibular function.
  - Sub-therapeutic risk: engine dose (3 mg/kg/day divided) is below the modern once-daily guideline band (~0.43×); consider up-titration toward 5-7 mg/kg once daily per PD (Cmax:MIC) target, guided by TDM.
  - Peak-driven (Cmax) drug — extended-interval (once-daily) dosing preferred over divided dosing.
  - Exposure/PD assumption: dose matched on adult exposure surrogate (Vd ratio); assumes pediatric Cmax:MIC target equals adult.
  - Toxic dose threshold not quantifiable in mg/kg/day — nephro-/ototoxicity monitored via trough levels, not a fixed daily cap.
- **Grade rationale:** PK from cache (not live), core renal PK is high-confidence. Engine dose (3 mg/kg/day) is anchored to the conservative divided-dose reference and falls BELOW the guideline concordance band (~0.43× of a ~7 mg/kg/day once-daily guideline midpoint), so it is potentially sub-therapeutic by peak-driven (Cmax:MIC) standards. NTI drug in a renally-impaired child mandates TDM. Discordance + cache source + 

## gentamicin · `obese_1y_14kg`
- **Grade:** C · **Dose:** 7 mg/kg/day · **57.8s**
- **Concordance:** guideline 7 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4212 cache_read=35276 | retr in=0 out=0
- **Flags:**
  - NARROW THERAPEUTIC INDEX aminoglycoside — TDM MANDATORY (peak for efficacy, trough <1–2 mg/L for nephro/ototoxicity avoidance).
  - ENGINE-GUIDELINE DISCORDANCE: engine 3 mg/kg/day is subtherapeutic; final dose overridden to guideline range (~7 mg/kg/day).
  - Vd underestimation risk: infants have larger weight-normalized Vd than adults; peak-driven dosing requires higher mg/kg than size-scaling predicts.
  - HIGH WEIGHT-FOR-AGE (14 kg at 1 yr vs ~10 kg ideal) — consider adjusted/ideal body weight for dosing to avoid overexposure; confirm with TDM.
  - Assumed TERM gestation — PMA not supplied.
  - Nephro-/ototoxicity monitoring required; ensure adequate hydration and avoid concomitant nephrotoxins.
- **Grade rationale:** Core PK is high-confidence (renal elimination, GFR maturation well-characterized), but the deterministic engine dose (3 mg/kg/day, matched on adult Vd ratio) is discordant with and ~2.4x below well-established pediatric guidelines. The engine under-predicts because it scales the peak-driving Vd by size, whereas infants have a LARGER weight-normalized Vd than adults — the exact failure mode documen

## ampicillin · `neonate_5d`
- **Grade:** B · **Dose:** 200 mg/kg/day · **99.5s**
- **Concordance:** guideline 100 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4198 cache_read=20337 | retr in=4 out=3678
- **Flags:**
  - fT>MIC β-lactam: efficacy depends on fraction of interval above MIC — dose frequently (q8h at this PMA/PNA), NOT total-exposure matched; engine value is directional only
  - Engine exposure-matched dose (119.6 mg/kg/day) is SUB-THERAPEUTIC vs effective/guideline 200 mg/kg/day — overridden to guideline
  - Critical illness / sepsis indication: neonatal Vd is expanded and CL immature — PK may diverge from healthy-adult exposure matching; treat as starting point
  - Assumed term (GA 40w provided, consistent with case); interval is PMA/PNA-dependent — escalate frequency (q6h) after PNA 7 days
  - Neurotoxicity/seizure risk at very high CNS exposures, chiefly with renal impairment — none here, but monitor
  - Combine with aminoglycoside per standard empiric neonatal sepsis regimens (clinician decision); flush line — ampicillin inactivates aminoglycosides in-line
- **Grade rationale:** Live PK retrieved, but ampicillin is a time>MIC β-lactam: the allometry×maturation engine matches total daily exposure only, which is a directional proxy (grade ceiling B) that here underdoses vs guideline (0.60× band). Final dose adopts well-established neonatal guideline concordance rather than the engine number.

## ampicillin · `child_2y_egfr85`
- **Grade:** B · **Dose:** 200 mg/kg/day · **54.9s**
- **Concordance:** guideline 120 · ratio 1.667 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 4 · rationale: True
- **Tokens:** orch in=10 out=4068 cache_read=35557 | retr in=0 out=0
- **Flags:**
  - OVERRIDE: engine TIME>MIC proxy (~154 mg/kg/day) was sub-therapeutic (<200 mg/kg/day floor); final dose anchored to guideline 200 mg/kg/day.
  - TIME>MIC (fT>MIC) beta-lactam: efficacy driven by fraction of interval above MIC, not total exposure — give frequently (q4-6h) or extended infusion; total-daily-dose match is DIRECTIONAL only.
  - RENAL impairment (eGFR 85, fraction 0.85) — mild; no dose reduction from floor, but reassess interval and monitor renal trend (CNS penetration/seizure risk with accumulation in renal impairment).
  - Indication label says 'neonatal' but covariates are a 2-year-old (12 kg) — dosed as toddler, not neonate. Confirm patient identity/indication.
  - 20% of adult clearance unattributed to a maturing pathway (scaled by size only) — minor error source, low impact at age 2.
  - Exposure/PD matching assumption: adult effective target assumed applicable to child.
  - Wide guideline range (50-400 mg/kg/day); 200 chosen for Listeria/enterococcal coverage. Max 12 g/day.
- **Grade rationale:** PK from cache (moderate confidence; adult CL/Vd derived, not directly measured). Ampicillin is a TIME>MIC beta-lactam, so the allometry total-daily-dose match is a directional PROXY only (grade ceiling B). Guideline concordance is strong and used as the primary anchor. No live source and PD exposure-matching assumption prevent grade A.

## ampicillin · `obese_1y_14kg`
- **Grade:** B · **Dose:** 200 mg/kg/day · **56.1s**
- **Concordance:** guideline 150 · ratio 1.333 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4166 cache_read=35643 | retr in=0 out=0
- **Flags:**
  - INDICATION/AGE MISMATCH: labeled 'neonatal' but patient is 1 y / 14 kg — dosed as a 1-year-old child, NOT a neonate. Verify intended patient.
  - SUB-THERAPEUTIC ENGINE ESTIMATE: allometric exposure-match (158 mg/kg/day) fell below the 200 mg/kg/day effective threshold; guideline dose adopted instead.
  - TIME>MIC β-LACTAM: total-daily-dose match is a PROXY only — dose frequently (q4-6h) or by extended/continuous infusion; efficacy = fT>MIC.
  - ASSUMED-TERM: PMA not supplied for child <2 y — assumed 40 wk gestation. (Low impact at age 1 y.)
  - EXPOSURE-MATCHING PD ASSUMPTION: healthy-adult exposure equivalence assumed.
  - PK source = shared cache, not live retrieval.
  - OBESITY / high weight-for-age (14 kg vs ~10 kg ideal at 1 y): weight-linear dosing may overestimate exposure; consider adjusted body weight.
  - CRITICAL ILLNESS/sepsis: Vd and CL may diverge from healthy-adult PK — starting point only.
  - LISTERIA/CNS: consider aminoglycoside combination and possibly higher dose per local guideline; separate ampicillin from aminoglycoside in the line (inactivation).
- **Grade rationale:** PK from shared cache (not live), moderate confidence with derived adult CL/Vd. Guideline-concordant for the indication. Ceiling of B because ampicillin is a time>MIC β-lactam: total-daily-dose exposure matching is a proxy only, so the allometric estimate is directional. Grade not lowered to C/D because robust pediatric guideline dosing (200 mg/kg/day for Listeria) anchors the recommendation.

## caffeine · `neonate_5d`
- **Grade:** A · **Dose:** 5 mg/kg/day · **118.2s**
- **Concordance:** guideline 5 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4503 cache_read=36829 | retr in=8 out=4235
- **Flags:**
  - EXPOSURE-MATCHING ASSUMPTION FAILED: engine scaled to adult steady-state Css, but the neonatal AOP therapeutic target (~5-25 mg/L caffeine) is higher and better tolerated than adult exposure; allometric dose (~1.5 mg/kg/day) is markedly SUB-THERAPEUTIC and must NOT be used.
  - SALT FORM: doses are caffeine CITRATE; caffeine base is ~50% of these values — verify product labeling to avoid 2x dosing error.
  - IMMATURE CLEARANCE / LONG HALF-LIFE: CYP1A2 markedly immature in neonates; real neonatal caffeine t1/2 ~50-100 h (engine estimated ~7.7 h, likely underestimate). Justifies once-daily maintenance and the large loading dose; accumulation risk if renal/hepatic maturation is delayed.
  - ACTIVE METABOLITES: paraxanthine/theobromine/theophylline; in neonates interconversion of caffeine<->theophylline occurs and metabolite maturation differs from parent.
  - TDM: routine serum caffeine monitoring generally not required per AAP, but consider levels for persistent apnea, tachycardia, or signs of toxicity.
  - COVARIATE NOTE: GA 40 wk + PNA 5 d = TERM infant (3.5 kg); AOP and this regimen are validated in PRETERM neonates. Confirm indication is genuine apnea of prematurity vs. apnea from another cause before treating.
  - PRESCRIBER VERIFICATION REQUIRED: decision support only.
- **Grade rationale:** Live PK retrieved; a robust, FDA-labeled and CAP-trial-validated neonatal weight-based regimen exists with strong guideline concordance. Grade A reflects the guideline dose (which I adopt), NOT the allometric engine output — the latter is invalid here because adult-CSS exposure-matching does not represent the neonatal PD target.

## caffeine · `child_2y_egfr85`
- **Grade:** D · **Dose:** None mg/kg/day · **112.0s**
- **Concordance:** guideline 5 · ratio None · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 3 · rationale: True
- **Tokens:** orch in=8 out=3954 cache_read=19586 | retr in=6 out=4573
- **Flags:**
  - INDICATION–AGE MISMATCH: 'apnea of prematurity' entered for a 2-year-old — AOP is a preterm-neonatal diagnosis only. Verify true age/indication before dosing.
  - ABSTAIN: no numeric starting dose issued (grade D).
  - ACTIVE METABOLITES: theophylline (itself pharmacologically active) plus paraxanthine/theobromine — parent CL underestimates total methylxanthine effect; consider metabolite contribution.
  - MATURATION MISMATCH: neonatal 5 mg/kg/day regimen relies on immature CYP1A2/long t1/2; at 2 yr CYP1A2 is ~66% mature and t1/2 ~4.3 h — once-daily dosing assumptions do not transfer.
  - NARROW-THERAPEUTIC-INDEX methylxanthine (toxic ~20 mg/kg/day vs effective ~5): if any caffeine use is truly intended, obtain serum caffeine TDM.
  - RENAL impairment flagged, but caffeine is <5% renally cleared — organ modifier has negligible effect; not dose-limiting.
  - CSS drug with no adult daily dose supplied — engine cannot solve an absolute dose regardless of age.
- **Grade rationale:** Indication–patient mismatch invalidates the dosing request: 'apnea of prematurity' is definitionally a preterm-neonatal disorder, but this patient is a 2-year-old (12 kg, PMA 144 wk). No guideline maintenance dose exists for AOP at this age, and the neonatal 5 mg/kg/day regimen depends on immature CYP1A2 ontogeny that no longer applies (engine CYP1A2 maturation factor 0.66 at 2 yr vs near-zero in 

## caffeine · `obese_1y_14kg`
- **Grade:** D · **Dose:** None mg/kg/day · **55.8s**
- **Concordance:** guideline 5 · ratio None · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 3 · rationale: True
- **Tokens:** orch in=12 out=3949 cache_read=35795 | retr in=0 out=0
- **Flags:**
  - INDICATION–POPULATION MISMATCH: apnea of prematurity is a neonatal diagnosis; patient covariates describe a 1-year-old 14 kg child — indication does not apply; NO DOSE ISSUED.
  - NO ABSOLUTE DOSE FROM ENGINE: CSS drug with no adult daily-dose anchor; caffeine for AOP is dosed by fixed neonatal mg/kg, not adult-PK extrapolation.
  - NARROW THERAPEUTIC INDEX → TDM: effective ~5 vs toxic ~20 mg/kg/day; monitor serum caffeine and for tachycardia if ever used.
  - ACTIVE METABOLITES: paraxanthine, theobromine, theophylline — parent clearance ≠ full pharmacologic effect; metabolite maturation not separately modeled.
  - ASSUMED-TERM GESTATION: no gestational age supplied; PMA assumed 40 wk — if truly preterm this understates immaturity and overestimates clearance.
  - EXPOSURE-MATCHING PD ASSUMPTION: allometry×maturation matches drug exposure, not necessarily neonatal respiratory-stimulant effect.
  - OBESITY / high weight-for-age (14.0 kg at 1.0 y; ideal ≈10 kg) — total-body-weight dosing may overestimate exposure; dosing-weight hint advisory only.
- **Grade rationale:** Critical indication–population mismatch: apnea of prematurity is a neonatal condition, but the case describes a 1-year-old 14 kg term-equivalent child (PMA ~92 weeks). The allometry×maturation engine could not solve an absolute dose (caffeine for AOP is a CSS drug dosed by fixed mg/kg, with no adult daily-dose anchor). A weight-based extrapolation of the neonatal regimen to a 1-year-old is not cli

### Batch summary (gentamicin, ampicillin, caffeine)
- n=9 · within 0.67–1.5×: 4/9 · within 0.5–2×: 7/9
- **Tokens this batch:** orch in/out 84/37493 (cache_read 257469) · retrieval in/out 26/15187 · **total 52,790**
- finished 2026-07-11T16:40:46.888664+00:00

---

## Token usage ledger

### Batch 1 (vancomycin, midazolam, morphine × 3)
- **Not instrumented** — usage fields were returned by the API but not written to `usage_log.jsonl`.
- Rough scale: ~9 cases × ~50–110 s; similar order of magnitude to batch 2 if re-run.

### Batch 2 (gentamicin, ampicillin, caffeine × 3) — measured
| Component | Tokens |
|-----------|--------|
| Orchestrator uncached input | 84 |
| Orchestrator output | 37,493 |
| Orchestrator cache **read** | 257,469 |
| Orchestrator cache **write** | 156,860 |
| Retrieval uncached input | 26 |
| Retrieval output | 15,187 |
| **Generation total** (uncached in + all out) | **52,790** |
| **All reported fields sum** (incl. cache r/w) | **467,119** |

Notes:
- Prompt caching makes uncached `input_tokens` tiny; most prompt mass is cache_read/cache_write.
- Generation total = tokens the models *produced* + uncached input (matches per-case `tok=` lines).
- Cache fields dominate “throughput” but are billed at cache rates, not full input rates.

### Cumulative (logged only = batch 2)
- Cases logged: **9**
- Generation total: **52,790**
- With cache r/w: **467,119**
