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


# Merged parallel worker outputs

## Worker w1
# PaedScale validation results
Branch: `validation-eval`. Started 2026-07-11T16:44:41.060005+00:00
Harness-only. Never merge this branch to master.

## amikacin · `neonate_5d`
- **Grade:** B · **Dose:** 15 mg/kg/day · **88.1s**
- **Concordance:** guideline 15 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=10 out=4185 cache_read=35052 | retr in=6 out=2238
- **Flags:**
  - NTI aminoglycoside → mandatory TDM: target peak 24–35 mg/L, trough <5 mg/L (avoid peak >35, trough >10 µg/mL per label)
  - Cmax/concentration-target driven: dose set by peak/trough goals, NOT exposure-matching; PD assumption of exposure-matching does NOT apply
  - Neonate: extended-interval dosing (q24h) preferred to reduce trough accumulation/nephro-ototoxicity
  - Assumed term (GA 40 wk, PMA ~40.7 wk) — dosing category is ≥35 wk term
  - Engine did not output a dose (Cmax drug, no matched adult dose); final dose derived from neonatal guidelines
  - Renal function assumed normal; any renal impairment or perinatal asphyxia/hypothermia markedly lowers CL (~40%) → lengthen interval
  - Ototoxicity/nephrotoxicity monitoring; co-administration of nephrotoxins or ibuprofen prolongs interval
- **Grade rationale:** Live PK dossier retrieved (High-confidence class PK) and multiple concordant neonatal guidelines/pop-PK studies support the dose. Not grade A because the allometry×maturation engine cannot directly generate an aminoglycoside dose (Cmax/concentration-target driven, not exposure-matched) and no single adult reference dose was matched — the number rests on external neonatal guidelines plus mandatory 

## amikacin · `child_2y_egfr85`
- **Grade:** B · **Dose:** 15 mg/kg/day · **55.4s**
- **Concordance:** guideline 15 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=8 out=4244 cache_read=18581 | retr in=0 out=0
- **Flags:**
  - NTI aminoglycoside — MANDATORY TDM: target peak 20–40 mcg/mL (or peak/MIC ≥8–10 for resistant organism), trough <5 mcg/mL; avoid peak >35 and trough >10 mcg/mL per label
  - RENAL impairment flagged — organ-function modifier (0.85) applied to renal clearance; reassess interval and monitor renal function with serial troughs
  - Nephrotoxicity/ototoxicity risk — monitor renal function and audiometry, especially with concurrent nephrotoxins (vancomycin, loop diuretics, amphotericin)
  - Exposure-matching PD assumption: dose matched to adult Cmax exposure via Vd ratio; assumes equivalent peak/MIC target applies in child
  - RESISTANT organism — confirm MIC; low-end dose may be sub-therapeutic if MIC high — consider up to 20 mg/kg/day guided by peak/MIC
  - PK source_mode = cache (not live retrieval)
  - Term birth assumed (no gestational age provided); at age 2y renal maturation essentially complete so impact negligible
- **Grade rationale:** PK from shared cache (not live retrieval), but core aminoglycoside PK is well-established and high-confidence. Engine allometry×maturation dose (15 mg/kg/day) is concordant with multiple pediatric guidelines (15–20 mg/kg/day). Cmax target-matching on Vd ratio is appropriate for an aminoglycoside. Downgraded from A because source_mode was cache rather than live, toxic mg/kg/day threshold is null (t

## amikacin · `obese_1y_14kg`
- **Grade:** B · **Dose:** 15 mg/kg/day · **46.9s**
- **Concordance:** guideline 19 · ratio 0.789 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.8333333333333334 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=3481 cache_read=18588 | retr in=0 out=0
- **Flags:**
  - NTI aminoglycoside → TDM MANDATORY: target peak 20-40 µg/mL, trough <5 µg/mL; avoid peak >35-40 and trough >10 µg/mL
  - Cmax-driven: once-daily dosing preferred over divided q8h for efficacy and reduced toxicity
  - Engine dose (15 mg/kg/day) is at the LOW end; for resistant gram-negative infection consider 20 mg/kg/day once-daily for better Cmax/MIC target attainment (PTA >90% at 20 vs 63.5% at 15 mg/kg/day)
  - OBESITY / high weight-for-age (14 kg at 1 y; ideal ~10 kg): amikacin distributes into extracellular/lean water, not fat — dosing on total body weight may overestimate; consider adjusted body weight and confirm with TDM
  - PMA not supplied; assumed TERM (40 wk) — appropriate for a 1-year-old but verify no prematurity affecting renal maturation
  - Exposure/PD-matching assumption: dose matched on adult Vd ratio assuming equivalent Cmax/MIC target
- **Grade rationale:** Core PK from cache (not live retrieval), but amikacin class PK is well-established and highly concordant with published pediatric guidelines. Engine dose (15 mg/kg/day) matches the low end of the guideline range; graded B rather than A because PK was cache-sourced and current pediatric evidence favors the upper end (20 mg/kg/day) for this resistant gram-negative indication.

## meropenem · `neonate_5d`
- **Grade:** B · **Dose:** 120 mg/kg/day · **89.8s**
- **Concordance:** guideline 60 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': True, 'enzymes': False, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=3763 cache_read=20337 | retr in=4 out=3486
- **Flags:**
  - fT>MIC β-lactam: total-daily-dose match is a PROXY only — efficacy depends on fraction of interval above MIC; give q8h and prefer prolonged/extended infusion (3–4 h)
  - Engine-calculated dose (66.8 mg/kg/day) fell below the effective threshold and was overridden by the guideline dose (120 mg/kg/day)
  - Neonate: renal clearance is GFR-maturation-dependent; monitor renal function and adjust interval if creatinine clearance changes
  - Exposure-matching PD assumption does not hold for time>MIC drugs — guideline-anchored
  - Not first-line for neonatal meningitis: reserve for confirmed/suspected multidrug-resistant gram-negatives or first-line failure
  - Assumed term (GA 40 wk) — dosing category is GA ≥32 wk, all ages, 40 mg/kg q8h
- **Grade rationale:** Live PK retrieved and a consistent neonatal meningitis guideline dose exists (40 mg/kg q8h). Grade capped at B (not A) because meropenem is a time>MIC β-lactam: the deterministic engine matches total daily exposure only, which is a directional proxy and undershoots the fT>MIC-driven guideline dose (engine 66.8 vs guideline 120 mg/kg/day). Recommendation is anchored to the guideline, not the engine

## meropenem · `child_2y_egfr85`
- **Grade:** B · **Dose:** 120 mg/kg/day · **55.1s**
- **Concordance:** guideline 60 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': True, 'enzymes': False, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=8 out=4155 cache_read=20218 | retr in=0 out=0
- **Flags:**
  - TIME>MIC (fT>MIC) drug — total-daily-dose match is a PROXY only; give q8h and consider extended/continuous infusion to optimize target attainment.
  - RENAL impairment flagged — eGFR 85 is mild; no interval extension indicated at this level (adult adjustment begins <50 mL/min), but monitor renal function and reassess with any decline.
  - Exposure/PD-matching assumption: allometric scaling assumes equivalent PK/PD target between adult and child; CSF penetration and inflamed-meninges permeability add variability.
  - Engine 'toxic-dose exceeded' warning is a false positive here — threshold (85.7 mg/kg/day) derived from continuous-infusion neurotoxicity in renally-impaired adults, not applicable to intermittent pediatric meningitis dosing.
  - Watch drug interactions: meropenem markedly lowers valproic acid levels; probenecid raises meropenem levels.
  - Augmented renal clearance (common in pediatric meningitis/critical illness) can make even 40 mg/kg q8h subtherapeutic — consider TDM/extended infusion if clinical response inadequate.
- **Grade rationale:** PK from shared cache (not live retrieval), and target is time>MIC — so the allometric total-daily-dose match is only a directional proxy (grade ceiling B). However, an established, well-validated pediatric meningitis guideline dose exists (IDSA/FDA label) and the engine proxy (110.6 mg/kg/day) is highly concordant (0.92×) with it, supporting confidence.

## meropenem · `obese_1y_14kg`
- **Grade:** B · **Dose:** 120 mg/kg/day · **60.9s**
- **Concordance:** guideline 60 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': True, 'enzymes': False, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=3895 cache_read=36969 | retr in=0 out=0
- **Flags:**
  - TIME>MIC β-lactam: efficacy = fraction of interval above MIC, not total exposure — dose q8h (or extended/continuous infusion for high-MIC/critically ill); daily-total concordance is directional only.
  - MENINGITIS requires the higher 40 mg/kg q8h dose for adequate CSF penetration; do NOT use the 20 mg/kg non-CNS dose if CNS involvement is present.
  - Assumed TERM gestation (PMA 92 wk) — no gestational/postnatal age supplied; if preterm history, immaturity is understated and dose may be over-estimated.
  - High weight-for-age advisory flag (14 kg at 1 yr vs ~10 kg ideal): pediatric meropenem is conventionally dosed on ACTUAL body weight, but watch for overexposure in true obesity; per-dose cap 2 g/dose applies.
  - Neurotoxicity/seizure risk with β-lactams, especially at high doses or with renal impairment — monitor; augmented renal clearance can render standard dosing subtherapeutic.
  - Drug interaction: meropenem markedly lowers valproic acid levels (avoid co-administration).
  - Exposure/PD-matching assumption: extrapolation assumes pediatric PK/PD target (fT>MIC) equivalent to adults.
  - PK source_mode = cache (not live retrieval).
- **Grade rationale:** Core PK from cache (not live) with high confidence; engine allometry×GFR-maturation dose (~116 mg/kg/day) is within 0.67–1.5× of the established pediatric meningitis guideline (120 mg/kg/day), giving strong concordance. Ceiling held at B (not A) because meropenem is a time>MIC β-lactam: total-daily-dose matching is only a DIRECTIONAL proxy — efficacy depends on fT>MIC (fraction of interval above M

## cefotaxime · `neonate_5d`
- **Grade:** B · **Dose:** 100 mg/kg/day · **104.7s**
- **Concordance:** guideline 100 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': True, 'enzymes': False, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4166 cache_read=37097 | retr in=8 out=3412
- **Flags:**
  - TIME>MIC β-lactam: engine total-daily-dose match is a PROXY only — efficacy is fT>MIC. Dose frequently (q8–12h) or by extended infusion; do NOT reduce to the ~90 mg/kg/day engine number.
  - Engine calculated 89.7 mg/kg/day is BELOW the effective 200 mg/kg/day figure — sub-therapeutic if used literally; final dose anchored to guideline instead.
  - Active metabolite desacetylcefotaxime is renally cleared and contributes to activity; accumulates if renal function declines (none here, renal_function_fraction 1.0).
  - 20% of clearance was unattributed to a maturing pathway and scaled by size only (assumed adult-like) — source of error in the neonate.
  - Critical illness / neonatal sepsis: Vd and CL may diverge from healthy-adult PK; treat as a STARTING dose and adjust to clinical response.
  - Assumed term (GA 40w, PMA ~40.7w) — interval widens for lower PMA/preterm.
  - Ceftriaxone is NOT interchangeable in neonates (bilirubin displacement/Ca precipitation); cefotaxime preferred.
  - Decision support only — not a prescription; confirm against local neonatal formulary.
- **Grade rationale:** Live adult PK retrieved and a maturing renal (GFR) pathway is mapped, but cefotaxime is a time>MIC β-lactam: the engine's total-exposure match (~90 mg/kg/day) is a directional proxy only, not a valid basis for a fraction-of-interval PD target. Final dose is therefore anchored to concordant pediatric guidelines/formulary + a model-based neonatal PK/PD study rather than the raw engine output, cappin

## cefotaxime · `child_2y_egfr85`
- **Grade:** B · **Dose:** 225 mg/kg/day · **59.3s**
- **Concordance:** guideline 150 · ratio 1.5 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': True, 'enzymes': False, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4349 cache_read=19794 | retr in=0 out=0
- **Flags:**
  - INDICATION MISMATCH: labeled 'neonatal' but patient is 2 y / 12 kg — used pediatric (>1 month) meningitis dosing, not neonatal PMA-based dosing.
  - TIME-DEPENDENT β-LACTAM (fT>MIC): engine total-daily-dose match is a proxy only; dose frequently (q4–6h) or by extended/continuous infusion. Concordance is DIRECTIONAL (grade ceiling B).
  - ENGINE SUB-THERAPEUTIC: computed 115 mg/kg/day is below both the minimum effective (200 mg/kg/day) and guideline meningitis dose — do NOT use the engine number; deferred to guideline.
  - ACTIVE METABOLITE: desacetylcefotaxime contributes antibacterial activity and CSF penetration; parent clearance ≠ total effect.
  - RENAL IMPAIRMENT (eGFR 85, fraction 0.85): mild; adjust INTERVAL and monitor renal function rather than cut total daily dose at meningitis initiation. Accumulation of renally-cleared active metabolite possible.
  - MENINGITIS: requires high-dose regimen for adequate CSF exposure; verify against local formulary and pathogen MIC before prescribing.
  - EXPOSURE-MATCHING PD ASSUMPTION: allometry×maturation assumes adult-like target; CSF target attainment is pathogen/MIC-specific.
  - 20% of clearance unattributed to a maturing pathway — scaled by size only (minor error source at 2 y, less than in neonates).
- **Grade rationale:** Grade ceiling B: cefotaxime is a time-dependent (fT>MIC) β-lactam, so the allometry×maturation engine's total-daily-dose match (115 mg/kg/day) is only a DIRECTIONAL proxy and cannot set the true dose. The engine result fell below its own minimum effective threshold and below the guideline concordance floor (ratio ~0.51). Robust, consistent pediatric/neonatal formulary and trial data anchor the men

## cefotaxime · `obese_1y_14kg`
- **Grade:** B · **Dose:** 300 mg/kg/day · **56.3s**
- **Concordance:** guideline 150 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=3968 cache_read=19902 | retr in=0 out=0
- **Flags:**
  - NON-NEONATE: case labeled 'neonatal' but covariates are a 1-yr-old (14 kg); dosed to actual covariates — verify intended patient.
  - ASSUMED TERM: PMA not supplied; engine assumed 40-wk term gestation (irrelevant at 1 yr but noted).
  - TIME>MIC β-LACTAM: efficacy governed by fT>MIC, not total exposure — engine AUC-match is DIRECTIONAL only; give q6h / extended or continuous infusion.
  - ENGINE DOSE SUB-THERAPEUTIC: computed 118 mg/kg/day < effective minimum (200) — NOT used; guideline dose adopted.
  - ACTIVE METABOLITE: desacetylcefotaxime is active and renally cleared — contributes to efficacy and accumulates in renal impairment (none here).
  - MENINGITIS: high dose (300 mg/kg/day) selected for CSF target attainment; cap at 12 g/day max.
  - OBESITY/HIGH WEIGHT-FOR-AGE: 14 kg at 1 yr (~ideal 10 kg) — total-body-weight dosing may overestimate; consider clinical judgment / adjusted weight.
  - CRITICAL ILLNESS/SEPSIS: augmented renal clearance and Vd shifts possible — starting point only; consider TDM/target attainment monitoring where available.
  - PD ASSUMPTION: exposure-matching from adult PK assumes similar target; confirm MIC and local susceptibility.
  - DECISION SUPPORT ONLY — clinician to confirm dose, companion agents, and formulary.
- **Grade rationale:** Cached (not live) adult PK; robust concordant pediatric guideline data exist, but the drug is a time>MIC β-lactam so the allometric exposure-matching engine dose is only DIRECTIONAL (grade ceiling B). Final dose is guideline-driven, not engine-driven.

## acyclovir · `neonate_5d`
- **Grade:** B · **Dose:** 60 mg/kg/day · **105.2s**
- **Concordance:** guideline 60 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': False, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 4 · rationale: True
- **Tokens:** orch in=8 out=4498 cache_read=20414 | retr in=4 out=3722
- **Flags:**
  - ENGINE DISCORDANT / OVERRIDDEN: allometry×maturation AUC-match = 29.4 mg/kg/day is ~half the guideline dose and would be SUB-THERAPEUTIC — guideline (60 mg/kg/day) used instead.
  - EXPOSURE-MATCHING PD ASSUMPTION DOES NOT HOLD: neonatal HSV dosing is target-attainment/empiric (CNS + disseminated disease, ~50% CSF penetration), deliberately higher than adult-AUC extrapolation.
  - RENAL SAFETY: infuse over ≥1 hour and ensure adequate hydration to avoid crystalluria / renal tubular injury; acyclovir CL is GFR-dependent — monitor renal function and adjust interval if it deteriorates.
  - TERM vs PRETERM INTERVAL: q8h assumed for this TERM neonate; premature infants may require q12h due to lower renal clearance — verify GA (assumed term, GA 40 wk given).
  - 15% of adult clearance (hepatic/other) is not attributed to a mapped maturation pathway and was size-scaled only — minor source of PK uncertainty in the neonate.
  - ACTIVE MOIETY: acyclovir triphosphate is an intracellular anabolite, not a circulating metabolite — systemic parent PK drives dosing.
  - NEONATAL HSV is life-threatening; empiric treatment should not be delayed. Manage with pediatric infectious disease consultation. Duration 14–21 days per disease form; CSF HSV PCR to guide CNS therapy endpoint.
- **Grade rationale:** Live adult PK retrieved and a strong, well-established pediatric guideline exists (Red Book / AAP: 20 mg/kg/dose q8h = 60 mg/kg/day for neonatal HSV). Grade B rather than A because guideline and allometry×maturation engine are DISCORDANT: the engine's AUC-matched dose (29.4 mg/kg/day) is ~0.49× the guideline. The guideline governs — neonatal HSV dosing is deliberately supratherapeutic vs adult-AUC

## acyclovir · `child_2y_egfr85`
- **Grade:** B · **Dose:** 60 mg/kg/day · **105.9s**
- **Concordance:** guideline 30 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': True, 'enzymes': False, 'transporters': False, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=8 out=4108 cache_read=18793 | retr in=9659 out=4396
- **Flags:**
  - Indication labeled 'neonatal HSV' but patient is 2 y / 12 kg — neonatal 60 mg/kg/day high-dose protocol is for <3 months; verify intended indication.
  - RENAL impairment (eGFR 85, fraction 0.85): reassess interval if function declines; extend to q12h for worsening renal function.
  - Nephrotoxicity/crystalluria risk is dose- & hydration-dependent — ensure adequate IV hydration; infuse over ≥1 h. No fixed toxic mg/kg/day threshold.
  - Prodrug/active-moiety caveat: effect driven by intracellular acyclovir triphosphate, not plasma parent — exposure-matching PD assumption.
  - Consider TDM in impaired renal function or neurotoxicity signs (renally cleared drug with CNS toxicity potential).
- **Grade rationale:** Live adult PK retrieved (high confidence on renal CL/Vd/PB); robust concordant pediatric IV guidelines for severe HSV in 1–12 y (20 mg/kg q8h). Engine AUC-match (76 mg/kg/day) is concordant with guideline (60 mg/kg/day) at ratio 1.27× (within 0.67–1.5×). Downgraded from A because of renal impairment adding uncertainty and no defined toxic mg/kg/day threshold; not D because PK is live and guideline

## acyclovir · `obese_1y_14kg`
- **Grade:** B · **Dose:** 60 mg/kg/day · **193.1s**
- **Concordance:** guideline 30 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': True, 'enzymes': False, 'transporters': False, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=10 out=4551 cache_read=37905 | retr in=4 out=3263
- **Flags:**
  - [
  - "
  - T
  - I
  - M
  - E
  - >
  - M
  - I
  - C
  -  
  - d
- **Grade rationale:** Live PK retrieved and a strong, convergent pediatric guideline exists for HSV/VZV in infants ≥3 months (20 mg/kg IV q8h = 60 mg/kg/day). Ceiling held at B (not A) because acyclovir is a TIME>MIC drug with an intracellular active moiety (acyclovir triphosphate) — the engine's total-daily-dose match is a PD proxy only, and efficacy depends on fraction of interval above MIC rather than total exposure

### Batch summary (amikacin, meropenem, cefotaxime, acyclovir)
- n=12 · within 0.67–1.5×: 6/12 · within 0.5–2×: 12/12
- **Tokens this batch:** orch in/out 104/49363 (cache_read 303650) · retrieval in/out 9685/20517 · **total 79,669**
- finished 2026-07-11T17:00:13.657584+00:00

## Worker w2
# PaedScale validation results
Branch: `validation-eval`. Started 2026-07-11T16:44:39.362126+00:00
Harness-only. Never merge this branch to master.

## levetiracetam · `neonate_5d`
- **Grade:** B · **Dose:** 20 mg/kg/day · **86.4s**
- **Concordance:** guideline 40 · ratio 0.5 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4417 cache_read=20354 | retr in=4 out=2059
- **Flags:**
  - EXPOSURE-MATCHING PD ASSUMPTION: engine matches adult CSS; neonatal dosing is PD/seizure-driven, so guideline dose (20 mg/kg/day) preferred over engine output (35 mg/kg/day).
  - ENGINE/GUIDELINE DISCORDANCE: ratio 1.76 outside concordance band; deferred to neonatal guideline.
  - NEONATE (PNA 5 d): renal function immature and rapidly changing over first weeks — clearance rises quickly, so maintenance dose typically titrated upward; reassess dosing as PMA advances.
  - LOADING DOSE required for acute seizure control: 40 mg/kg IV (140 mg) over 15 min, optionally +20 mg/kg if seizures persist.
  - 10% of adult clearance unattributed to a maturing pathway (scaled by size only) — added uncertainty in the neonate.
  - 1:1 IV-to-oral conversion (F~0.95) when transitioning route.
  - Decision support only — not a prescription; confirm with local neonatal formulary and clinical status.
- **Grade rationale:** Live PK dossier available and multiple neonatal-specific guidelines/trials exist, but the engine's CSS-matched output (35 mg/kg/day) diverges from the established neonatal guideline maintenance dose (~20 mg/kg/day; ratio 1.76, outside 0.67–1.5×). Divergence is expected because the engine matches ADULT steady-state exposure while neonatal dosing is driven by a PD (seizure-suppression) target and im

## levetiracetam · `child_2y_egfr85`
- **Grade:** B · **Dose:** 55 mg/kg/day · **52.3s**
- **Concordance:** guideline 40 · ratio 1.375 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=3430 cache_read=36488 | retr in=0 out=0
- **Flags:**
  - RENAL impairment flagged — organ-function modifier applied to renal pathway; eGFR 85 is only mildly reduced (CrCl>80 needs no label adjustment), reassess interval/TDM if function declines.
  - CSS exposure-matching PD assumption: dose matched to adult steady-state exposure, not directly to pediatric efficacy endpoint.
  - Engine CSS-matched dose (~55 mg/kg/day) is at UPPER end of guideline range — start lower (~20 mg/kg/day) and titrate to avoid behavioral AEs.
  - 10% of clearance unattributed to a maturing pathway, scaled by size only — source of error in young children.
  - This is a MAINTENANCE dose only — acute seizure/status requires a separate IV loading dose (~40 mg/kg).
- **Grade rationale:** Cache PK (not live retrieval), but robust label-anchored parameters. Engine output (54.7 mg/kg/day) falls squarely within the established pediatric guideline range of 20–60 mg/kg/day for 6mo–4yr, giving concordance. Downgraded from A due to cache source, 10% unattributed clearance scaled by size only, and CSS exposure-matching PD assumption.

## levetiracetam · `obese_1y_14kg`
- **Grade:** A · **Dose:** 50 mg/kg/day · **52.3s**
- **Concordance:** guideline 40 · ratio 1.25 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=10 out=3786 cache_read=36433 | retr in=0 out=0
- **Flags:**
  - Engine-derived 52.6 mg/kg/day rounded to labeled maintenance target ~50 mg/kg/day (700 mg/day, 350 mg q12h).
  - ASSUMED TERM gestation — PMA not supplied for child <2 yr; if preterm, maturation is overstated and dose may be too high (esp. renal GFR immaturity).
  - High weight-for-age (14 kg vs ~10 kg expected at 1 y): total-body-weight dosing may overestimate exposure — verify weight is accurate and not edema/obesity; consider adjusted body weight if applicable.
  - Exposure-matching (CSS) PD assumption: adult target concentration assumed appropriate in infants.
  - MAINTENANCE dose only — acute status epilepticus requires a separate loading dose (40–60 mg/kg IV) not computed here.
  - IV formulation is off-label in young children in some regions though widely used; mg-for-mg oral↔IV substitution supported by F≈0.95.
  - 10% of clearance unattributed to a maturing pathway (size-scaled only) — minor error source in infants.
  - Renally eliminated: confirm normal renal function (assumed 1.0); reduce dose if impaired.
- **Grade rationale:** High-confidence PK dossier (FDA label/DailyMed + population PK), clean mechanism (66% renal unchanged, 24% non-CYP esterase hydrolysis, no active metabolites, negligible protein binding), and engine output (52.6 mg/kg/day) concords tightly with the FDA-labeled pediatric maintenance target (~50 mg/kg/day; ratio ≈1.05). Wide therapeutic index and F≈0.95 make oral→IV extrapolation robust.

## fentanyl · `neonate_5d`
- **Grade:** B · **Dose:** None mg/kg/day · **84.9s**
- **Concordance:** guideline 0.024 · ratio None · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=8 out=4380 cache_read=20232 | retr in=4 out=2032
- **Flags:**
  - Potent opioid — narrow therapeutic index; use lowest effective starting dose with full cardiorespiratory monitoring
  - Neonatal reduced clearance (engine CL ~3.8% adult, t½ ~5h) — accumulation risk with repeated boluses/infusion; monitor for delayed respiratory depression
  - Chest wall rigidity risk (reported 2.2-6.5 mcg/kg, occasionally with laryngospasm) — administer slowly, have naloxone available
  - High protein binding (~82.5%, mainly alpha-1-acid glycoprotein) — free fraction may be increased in neonates/illness (low AAG); potentiates effect
  - Tolerance/withdrawal with infusions >5 days — plan weaning
  - Exposure-matching PD assumption: not applicable — dose is titrated to validated pain score, not to a matched adult exposure target
  - Engine returned no absolute dose (fentanyl is titrated/procedural, not fixed mg/day) — recommendation is guideline-anchored
  - Not a prescription — clinician decision support only
- **Grade rationale:** Live PK retrieved and mechanism well-corroborated (CYP3A4 N-dealkylation to inactive norfentanyl, hepatic elimination). Multiple concordant neonatal guidelines support the dose range. Downgraded from A because fentanyl is not a fixed mg/day CSS drug — the allometry×maturation engine cannot solve an absolute dose (no meaningful adult daily dose for an acute/procedural titrated opioid), so the recom

## fentanyl · `child_2y_egfr85`
- **Grade:** C · **Dose:** None mg/kg/day · **61.1s**
- **Concordance:** guideline 0.048 · ratio None · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4209 cache_read=37232 | retr in=0 out=0
- **Flags:**
  - NTI / high-potency opioid — titrate to effect; risk of respiratory depression and chest-wall rigidity with rapid IV push; naloxone available.
  - Engine CSS daily-dose output NOT clinically applicable — fentanyl dosed per-bolus/per-rate; adult reference (0.1 mg) is a single bolus, not a daily dose.
  - RENAL impairment flagged — organ-function modifier applied, but renal pathway is only ~10% of clearance (hepatic CYP3A4-dominant); minimal impact on fentanyl handling. Parent drug not renally dependent; norfentanyl inactive.
  - High protein binding (~82.5%, alpha-1-acid glycoprotein) — free fraction may rise in critical illness/hypoalbuminemia; monitor clinically.
  - Exposure-matching PD assumption: extrapolation assumes child effect-site sensitivity comparable to adult once CL/Vd corrected — titrate to clinical endpoint.
  - Prolonged/repeated dosing or infusion → accumulation in fat/muscle with context-sensitive half-time increase; reassess.
- **Grade rationale:** Duplicate — see grade_rationale field.

## fentanyl · `obese_1y_14kg`
- **Grade:** B · **Dose:** None mg/kg/day · **57.9s**
- **Concordance:** guideline 0.048 · ratio None · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4055 cache_read=37219 | retr in=0 out=0
- **Flags:**
  - HIGH-POTENCY OPIOID / narrow safety margin: titrate to effect, continuous pulse oximetry + capnography, naloxone and airway equipment immediately available; risk of respiratory depression and chest-wall rigidity (rapid bolus).
  - TITRATED AGENT — not fixed daily dosing: engine daily-rate is confirmatory only; use per-dose guideline (1–2 mcg/kg/dose, up to 4 in tolerant patients).
  - PD ASSUMPTION: exposure-matching to adult CSS assumes equivalent adult/pediatric concentration–effect relationship — not established for opioid sedation; titrate clinically.
  - ASSUMED TERM gestation (PMA not supplied, age <2 y): if ex-preterm, immaturity is understated and dose may be overestimated.
  - HIGH WEIGHT-FOR-AGE (14 kg vs ~10 kg ideal at 1 y): weight-linear per-kg dosing on total body weight may overestimate — consider lean/ideal weight and titrate.
  - HIGH PROTEIN BINDING (~82.5%, mainly α1-acid glycoprotein): free fraction rises with acute illness/altered AAG — effect may exceed total-concentration prediction.
  - PK from shared cache (not fresh live retrieval); large inter-individual variability in Vd and CL.
- **Grade rationale:** PK sourced from shared cache (not a fresh live pull) with wide inter-individual variability (Vd 3–8 L/kg, CL 27–75 L/h), and the drug is titrated-to-effect rather than fixed-daily-dosed, so the allometric daily-rate engine output is confirmatory rather than the actionable number. Multiple concordant pediatric guidelines exist and support the recommended per-dose range, precluding grade C/D; but re

## clindamycin · `neonate_5d`
- **Grade:** B · **Dose:** 15 mg/kg/day · **101.4s**
- **Concordance:** guideline 15 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.3333333333333333 · dims: `{'elimination': False, 'pathways': False, 'enzymes': True, 'transporters': True, 'active_metabolites': False, 'protein_binding': False}`
- **Citations:** 7 · rationale: True
- **Tokens:** orch in=12 out=4846 cache_read=88420 | retr in=9718 out=2632
- **Flags:**
  - NEONATE: first-week-of-life immature CYP3A4 markedly reduces clearance (engine CL ~4% of adult); prolonged half-life reported (~6 h in some newborn series) — monitor for accumulation
  - PRODRUG: IV clindamycin phosphate is an inactive prodrug hydrolyzed to active clindamycin; hydrolysis capacity in neonates adds uncertainty
  - ACTIVE METABOLITES present (clindamycin sulfoxide, N-desmethylclindamycin, minor) — parent-based exposure matching is approximate
  - EXPOSURE-MATCHING PD ASSUMPTION: dose derived by matching adult AUC; assumes equivalent PK/PD target across ages
  - ADULT PK Vd/CL not directly retrieved — sourced from literature pop-PK and F-adjusted; absolute Vd and protein binding unconfirmed
  - ADMINISTRATION SAFETY: never give undiluted IV push; max 18 mg/mL, max infusion rate 30 mg/min
  - STARTING dose only — decision support, not a prescription; monitor clinically
- **Grade rationale:** Live PK retrieved, but adult Vd/CL were null in the dossier and had to be sourced from published pop-PK literature (CL/F ~23 L/h, V/F ~100 L; healthy-subject IV values comparable), then F-adjusted — introducing parameter uncertainty. Offsetting this, the allometry × CYP3A4/GFR-maturation engine output (14.3 mg/kg/day) is in excellent concordance with multiple independent neonatal guidelines conver

## clindamycin · `child_2y_egfr85`
- **Grade:** A · **Dose:** 40 mg/kg/day · **125.6s**
- **Concordance:** guideline 30 · ratio 1.333 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 1.0 · dims: `{'elimination': True, 'pathways': True, 'enzymes': True, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=12 out=3973 cache_read=83108 | retr in=8 out=5151
- **Flags:**
  - Renal impairment flagged by engine but NOT clinically actionable: clindamycin is hepatically (CYP3A4) cleared; label states no renal dose adjustment needed.
  - Exposure-matching (AUC) assumes adult PK/PD target is valid in a 2-year-old — reasonable for a time/AUC-dependent bacteriostatic protein-synthesis inhibitor.
  - ~10% of clearance was size-scaled only (not attributed to a maturing pathway) — minor source of error, negligible at age 2 (CYP3A4 near-mature).
  - Adult CL (13 L/h) and Vd (66 L) were literature-standard values, not returned by retrieval — verify against local reference.
  - Not an NTI drug; routine TDM not required. Monitor for C. difficile-associated diarrhea.
  - Max pediatric IV dose 2.7 g/day; recommended 480 mg/day is well within limits.
- **Grade rationale:** Live PK retrieval + well-established CYP3A4 maturation model produced an AUC-matched dose (34.7 mg/kg/day) that is highly concordant (ratio ~0.87) with the robust pediatric guideline standard of 40 mg/kg/day. Mechanism, guideline, and engine agree; no NTI or metabolite complications.

## clindamycin · `obese_1y_14kg`
- **Grade:** B · **Dose:** 30 mg/kg/day · **90.5s**
- **Concordance:** guideline 30 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4232 cache_read=20769 | retr in=4 out=2874
- **Flags:**
  - SUB-THERAPEUTIC ENGINE OUTPUT: AUC-matched engine dose 19.2 mg/kg/day is below the pediatric guideline minimum (20 mg/kg/day); final dose aligned upward to guideline 30 mg/kg/day.
  - EXPOSURE-MATCHING PD ASSUMPTION: engine assumes adult AUC target is appropriate; clindamycin PD is time>MIC/exposure-driven for bacteriostatic effect and guidelines dose higher.
  - PRODRUG: IV clindamycin phosphate is an inactive prodrug rapidly hydrolyzed to active clindamycin — parent-drug CL scaling may not fully capture active-moiety exposure; hydrolysis maturation in young infants adds uncertainty.
  - ASSUMED-TERM: PMA not supplied for child <2 yr — term (40 wk) gestation assumed; a preterm history would warrant lower dosing.
  - HIGH PROTEIN BINDING (~90%): free-fraction shifts possible in illness/hypoalbuminemia, though less critical at age 1 yr than neonate.
  - OBESITY FLAG = FALSE POSITIVE: 14 kg at 12 mo is ~90th percentile, not obese; clindamycin dosed on total body weight per label — do not use adjusted weight.
  - C. difficile / pseudomembranous colitis risk; neuromuscular-blocker potentiation — monitor.
  - Decision support only — not a prescription; confirm indication-specific dose and susceptibility.
- **Grade rationale:** Live PK + deterministic engine, but engine AUC-match under-doses vs validated guidelines which drive final dose.

## theophylline · `neonate_5d`
- **Grade:** B · **Dose:** 4 mg/kg/day · **125.3s**
- **Concordance:** guideline 4 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4521 cache_read=21018 | retr in=1350 out=4970
- **Flags:**
  - NTI drug → mandatory TDM: target theophylline ~5-10 mcg/mL in neonates; draw pre-dose trough at steady state
  - Active metabolite caffeine accumulates in neonates (immature CYP1A2 N-methylation) → monitor total methylxanthine load; consider measuring caffeine level
  - Neonatal clearance immature and rapidly maturing → dose requirement will increase over coming weeks; re-titrate
  - Engine dose (3.34 mg/kg/day) flagged sub-therapeutic vs 4 mg/kg/day threshold; guideline dose adopted instead
  - Reduced protein binding in neonates (~lower than adult ~58%) → higher free fraction; interpret total levels with caution
  - Salt correction required if aminophylline used (aminophylline ≈ 79-86% theophylline)
  - Modern practice favors caffeine over theophylline for apnea of prematurity (wider therapeutic index); indication noted as historical
- **Grade rationale:** Live PK retrieved and multiple converging neonatal pediatric guidelines/PK studies found (concordant). Downgraded from A because the engine's adult-anchored allometry×maturation is a poor model here: neonatal theophylline shows a distinct renal-dominant + caffeine-forming metabolism the maturation curves don't capture, and this is an NTI drug requiring TDM. The chosen dose relies on guideline data

## theophylline · `child_2y_egfr85`
- **Grade:** C · **Dose:** 6.0 mg/kg/day · **102.3s**
- **Concordance:** guideline 12 · ratio 0.5 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.3333333333333333 · dims: `{'elimination': False, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 7 · rationale: True
- **Tokens:** orch in=8 out=4750 cache_read=20218 | retr in=4 out=3510
- **Flags:**
  - NTI drug → mandatory TDM, target serum 10–20 mcg/mL (toxicity regularly >20).
  - SUB-THERAPEUTIC RISK: engine dose ~0.5× pediatric guideline; toddlers have higher weight-normalized CL than adults — engine maturation curve likely underestimates clearance at age 2.
  - Active metabolite 3-methylxanthine weakly active — minor contributor, monitor by level not by dose.
  - RENAL impairment flagged, but renal handles only ~10% of clearance so impact on total CL is small; CYP1A2 (hepatic, ~90%) dominates.
  - Exposure-matching PD assumption: dose derived by matching adult Css; assumes equivalent concentration-effect in child.
  - Use IDEAL body weight — theophylline distributes poorly into fat (12 kg appears appropriate for a 2-yr-old, low obesity risk).
  - Do NOT give loading dose if patient already on oral theophylline (common cause of iatrogenic toxicity).
  - Reduce dose during intercurrent viral illness (clearance impaired).
  - CL_adult is an estimate (Vd×t½ derived), not pooled — widens uncertainty.
  - Indication is historical (apnea/bronchospasm); caffeine now preferred for neonatal apnea — confirm clinical indication.
- **Grade rationale:** Live PK retrieved (grade A/B foundation), but CL was an estimate (derived from Vd × t½, not a pooled value) and the engine's late-CYP1A2 maturation curve conflicts materially with pediatric guideline infusion rates for toddlers, which imply ~2× higher clearance/dose. This unresolved discordance plus NTI status downgrades confidence to C. This is a STARTING estimate only; drug is titrated to serum 

## theophylline · `obese_1y_14kg`
- **Grade:** C · **Dose:** 12 mg/kg/day · **54.1s**
- **Concordance:** guideline 12 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.3333333333333333 · dims: `{'elimination': False, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4015 cache_read=20215 | retr in=0 out=0
- **Flags:**
  - NTI — narrow therapeutic index: MANDATORY TDM, target serum 10–15 mcg/mL in older infants (toxicity >20 mcg/mL); titrate to level, not weight formula
  - ENGINE DISCORDANT: allometry×maturation output (4.6 mg/kg/day) rejected — CYP1A2 TM50 ~1yr under-predicts; per-kg pediatric clearance meets/exceeds adult. Final dose is guideline-anchored (12 mg/kg/day)
  - OBESITY / high weight-for-age (14 kg at 1 yr, ~95th+ pct); total-body-weight dosing may overestimate — consider adjusted/ideal weight (~10 kg) and TDM
  - Assumed TERM gestation (PMA not supplied); if preterm/neonatal history, clearance is far lower — use neonatal regimen (~1.5 mg/kg q12h) instead
  - Clearance-reducing risk factors (febrile illness, URTI, hepatic impairment, CHD) markedly lower CL — reduce dose and monitor if present
  - Active metabolite 3-methylxanthine weakly active; in young infants methylation to caffeine occurs — additional CNS stimulant exposure
  - Loading dose (5–6 mg/kg) only if NOT already on theophylline; omit if on maintenance to avoid toxicity
  - Historical indication — theophylline largely superseded by caffeine (apnea) and inhaled therapy (bronchospasm); confirm clinical appropriateness
  - Cache (non-live) PK; adult CL is a derived estimate
- **Grade rationale:** PK from cache (not live); adult CL was derived from Vd×t½ rather than a directly pooled value (dossier flags it as an estimate). More importantly, the allometry×maturation engine output (4.6 mg/kg/day) is materially DISCORDANT with a robust FDA-label pediatric benchmark (12–14 mg/kg/day initial). The CYP1A2 late-maturation TM50 (~1 yr) drives child CL to only 16% of adult, but empirically theophyl

### Batch summary (levetiracetam, fentanyl, clindamycin, theophylline)
- n=12 · within 0.67–1.5×: 7/12 · within 0.5–2×: 9/12
- **Tokens this batch:** orch in/out 112/50614 (cache_read 441706) · retrieval in/out 11092/23228 · **total 85,046**
- finished 2026-07-11T16:59:47.097850+00:00

## Worker w3
# PaedScale validation results
Branch: `validation-eval`. Started 2026-07-11T16:44:33.949778+00:00
Harness-only. Never merge this branch to master.

## phenytoin · `neonate_5d`
- **Grade:** D · **Dose:** 5 mg/kg/day · **81.0s**
- **Concordance:** guideline 5 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=8 out=3783 cache_read=27853 | retr in=6 out=2382
- **Flags:**
  - MODEL INAPPLICABLE: saturable Michaelis-Menten kinetics — no fixed adult CL; allometric engine not run.
  - NARROW THERAPEUTIC INDEX: mandatory TDM; small dose changes near Km cause disproportionate level rises.
  - PROTEIN BINDING 90% + neonate: free (unbound) fraction may rise with low neonatal albumin — total-concentration targets can mislead; prefer free phenytoin monitoring.
  - FIRST WEEK OF LIFE: half-life highly variable, no fixed regimen reliably predicts levels — reassess with levels, expect slow time-to-steady-state (7–10 days).
  - EXPOSURE-MATCHING PD ASSUMPTION: neonatal target free level ~3 mg/L (total ~40–80 micromol/L) assumed equivalent to adult efficacy target.
  - IV FORMULATION: contains propylene glycol/ethanol; infuse slowly (≤1 mg/kg/min neonate) with continuous ECG/BP monitoring.
  - ROUTE: oral phenytoin absorption is unreliable in neonates — IV preferred; do not simply convert.
- **Grade rationale:** Allometric engine could NOT be run: phenytoin follows saturable Michaelis-Menten kinetics, so no fixed adult clearance (cl_adult_l_h) exists to scale — the core PaedScale assumption (first-order allometric CL scaling) is invalid for this drug. Guidelines explicitly state that in the first week of life phenytoin half-life is so variable that no fixed dosage regimen can be derived. Dose is therefore

## phenytoin · `child_2y_egfr85`
- **Grade:** C · **Dose:** 5 mg/kg/day · **48.5s**
- **Concordance:** guideline 8 · ratio 0.625 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=3408 cache_read=28929 | retr in=0 out=0
- **Flags:**
  - NONLINEAR (Michaelis-Menten) kinetics — allometric CL scaling invalid; engine bypassed, dose is guideline-derived.
  - NARROW THERAPEUTIC INDEX — mandatory TDM; target total 10–20 mcg/mL (free 1–2 mcg/mL); adjust doses no sooner than every 7–10 days for maintenance.
  - HIGH PROTEIN BINDING (90%) + renal impairment — free-fraction may be elevated (binding displacement/uremia); monitor FREE phenytoin, not just total, or correct total for albumin.
  - RENAL impairment flagged — but elimination is hepatic/negligible renal; no elimination-based dose reduction, relevance is protein-binding/free-fraction only.
  - IV administration — infuse slowly (≤1 mg/kg/min pediatric), continuous ECG/BP monitoring; risk of hypotension, arrhythmia, purple glove syndrome.
  - EXPOSURE-MATCHING PD ASSUMPTION — dose assumes adult/pediatric target serum concentration range applies.
- **Grade rationale:** Adult clearance is null because phenytoin exhibits saturable Michaelis-Menten (nonlinear, capacity-limited) kinetics, so the linear allometry × maturation engine cannot be validly run. Dose is therefore taken directly from concordant pediatric labeling/guidelines rather than computed, and TDM is mandatory. This precludes grade A/B; not D because PK mechanism and a robust weight-based pediatric gui

## phenytoin · `obese_1y_14kg`
- **Grade:** C · **Dose:** 8 mg/kg/day · **51.6s**
- **Concordance:** guideline 8 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=3678 cache_read=28239 | retr in=0 out=0
- **Flags:**
  - NARROW THERAPEUTIC INDEX → mandatory TDM: target total phenytoin 10–20 mcg/mL, unbound 1–2 mcg/mL; adjust in small increments.
  - NONLINEAR (Michaelis-Menten) kinetics → no first-order CL available; dose–concentration relationship is disproportionate near saturation; do not extrapolate linearly.
  - HIGH weight-for-age (14 kg at 1 y; typical ≈10 kg) → weight-linear IV dose on total body weight may overestimate exposure; consider lower effective weight and confirm with levels.
  - HIGH protein binding (90%) → free-fraction rises with hypoalbuminemia/critical illness; interpret unbound (or corrected) levels, not total alone.
  - EXPOSURE-MATCHING PD ASSUMPTION: guideline weight-based dosing assumed to reproduce effective exposure; not derived from mechanistic scaling here.
  - No active metabolites (p-HPPH inactive).
  - Separate loading dose (15–20 mg/kg IV) required for acute/status indications; infusion rate/cardiac monitoring cautions apply.
- **Grade rationale:** Adult clearance is null because phenytoin follows saturable Michaelis-Menten (nonlinear) kinetics, so the allometry × maturation engine cannot generate a valid first-order CL-based extrapolation. Dose therefore rests on guideline weight-based data (well-concordant across multiple sources) rather than mechanistic scaling. Downgraded from B by narrow therapeutic index, nonlinear kinetics, and a high

## ibuprofen · `neonate_5d`
- **Grade:** B · **Dose:** 10 mg/kg/day · **108.7s**
- **Concordance:** guideline 10 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4705 cache_read=19719 | retr in=6 out=3743
- **Flags:**
  - NTI-adjacent / neonatal narrow safety window — this is DECISION SUPPORT, not a prescription; confirm against local NICU PDA protocol and neonatology
  - PROTEIN BINDING >99% in a neonate — free (unbound) fraction may rise with low neonatal albumin; BILIRUBIN DISPLACEMENT RISK. Ibuprofen contraindicated in severe hyperbilirubinemia; check bilirubin before dosing
  - Engine dose (~17 mg/kg/day) DISCORDANT with guideline loading (10 mg/kg) — adult-PK exposure-matching does not capture AUC-targeted neonatal PDA regimen; guideline used instead
  - TERM neonate (40wk GA) — PDA evidence base is almost entirely PRETERM; efficacy/PK extrapolation to term infants is uncertain
  - PNA ~120h places patient in range where PNA-adjusted higher dosing (up to 18-9-9 mg/kg) has been proposed; consider per local protocol
  - Renal safety: monitor urine output/creatinine — ibuprofen reduces renal blood flow; contraindicated with renal impairment, active bleeding, thrombocytopenia, NEC
  - Exposure-matching PD assumption: neonatal PDA target is AUC-driven, not adult Cmax equivalence
  - Toxic dose threshold null in retrieval — upper safety bound not quantifiable from cited source
- **Grade rationale:** Live PK retrieved and a well-established, class-specific neonatal PDA guideline regimen exists (10-5-5 mg/kg IV ibuprofen-lysine). Not grade A because: (1) the allometry×maturation engine (adult CYP2C9 PK) gives ~17 mg/kg/day, which is discordant (ratio ~1.7 vs day-1 loading of 10 mg/kg) — adult-PK exposure-matching does not capture the AUC-targeted neonatal taper; (2) the entire evidence base is 

## ibuprofen · `child_2y_egfr85`
- **Grade:** B · **Dose:** 17 mg/kg/day · **51.0s**
- **Concordance:** guideline 20 · ratio 0.85 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 4 · rationale: True
- **Tokens:** orch in=10 out=3681 cache_read=36956 | retr in=0 out=0
- **Flags:**
  - INDICATION MISMATCH: PDA closure is a neonatal indication (ibuprofen lysine 10-5-5 mg/kg) — NOT applicable to a 2-year-old; dosed here for ANALGESIA only.
  - RENAL impairment flagged — NSAIDs reduce renal prostaglandin-mediated perfusion; with eGFR 85 / renal_function 0.85, monitor renal function, urine output, and hydration; avoid in dehydration/hypovolemia.
  - High protein binding (>99%) — free fraction may rise with hypoalbuminemia/critical illness or uremia; interpret exposure with caution.
  - NSAID class cautions: GI and CV risk; verify no concurrent nephrotoxins.
  - Exposure-matching PD assumption (pediatric target = adult).
  - Engine dose is Cmax-matched and conservative vs guideline per-dose; use guideline 10 mg/kg/dose as starting regimen.
- **Grade rationale:** PK sourced from cache (label-derived; adult CL is calculated not directly reported, CYP2C8 folded into CYP2C9 key). Cmax-matched allometric/maturation estimate (~17 mg/kg/day) is concordant with well-established pediatric IV analgesia guidelines (10 mg/kg/dose q6–8h). Downgraded from A due to derived adult CL, the fm approximation, and the exposure-matching PD assumption.

## ibuprofen · `obese_1y_14kg`
- **Grade:** B · **Dose:** 40 mg/kg/day · **51.0s**
- **Concordance:** guideline 20 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 4 · rationale: True
- **Tokens:** orch in=8 out=3731 cache_read=19580 | retr in=0 out=0
- **Flags:**
  - [
  - "
  - I
  - N
  - D
  - I
  - C
  - A
  - T
  - I
  - O
  - N
- **Grade rationale:** PK from shared cache (not live), derived clearance, and fm approximation (CYP2C8 folded into CYP2C9). However a strong FDA-approved IV pediatric guideline (Caldolor, 6 mo–<12 y) directly covers this patient, so the actionable dose is guideline-anchored rather than allometry-derived. Not grade A because the engine PK is oral-adult, cache-sourced, and the allometric estimate structurally disagrees w

## phenobarbital · `neonate_5d`
- **Grade:** B · **Dose:** 4 mg/kg/day · **95.8s**
- **Concordance:** guideline 5 · ratio 0.8 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': False, 'pathways': False, 'enzymes': True, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=8 out=3904 cache_read=29572 | retr in=6 out=3105
- **Flags:**
  - NTI drug — mandatory TDM: target trough 15–40 mcg/mL; obtain level at steady state (5 half-lives ≈ 7–10 days in neonate) and earlier if sedation/respiratory depression
  - Slow neonatal clearance (engine t½ ~158 h; CL ~4% of adult) → accumulation risk, especially at age <1 week; 5 mg/kg/day may push levels >30 mcg/mL in neonates <1 week
  - Loading dose (20 mg/kg IV) required separately to reach therapeutic level rapidly — maintenance alone will not
  - Engine could not compute absolute dose (no adult daily dose in dossier); dose is guideline-anchored
  - Exposure/PD-matching assumption: dose targets adult therapeutic serum range, assuming similar concentration-effect relationship in neonates
  - Watch respiratory depression/sedation, particularly with concurrent benzodiazepines and at serum concentrations >40 mg/L
- **Grade rationale:** Live adult PK retrieved, but the dossier lacked an adult daily/effective dose, so the allometry×maturation engine could not solve an absolute dose (it returned CL_child 0.009 L/h, t½ ~158 h, CL only ~4% of adult — confirming markedly slow neonatal clearance). The final dose is therefore anchored to convergent, high-quality neonatal-specific guideline literature rather than the engine. Multiple ind

## phenobarbital · `child_2y_egfr85`
- **Grade:** B · **Dose:** 4 mg/kg/day · **60.5s**
- **Concordance:** guideline 5 · ratio 0.8 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': False, 'pathways': False, 'enzymes': True, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 6 · rationale: True
- **Tokens:** orch in=10 out=4406 cache_read=37719 | retr in=0 out=0
- **Flags:**
  - INDICATION/AGE MISMATCH: indication 'neonatal seizures' but patient is 2 years old — do NOT use neonatal doses; pediatric dosing applied
  - NTI drug — mandatory TDM; target serum ~15–40 mcg/mL, draw trough at steady state (note long t1/2 ~1 week to steady state without loading)
  - AUTOINDUCER — clearance may increase over 1–2 weeks; anticipate dose uptitration (e.g., to 5 mg/kg/day) and monitor levels
  - Loading dose (20 mg/kg IV, ~240 mg, rate ≤1–2 mg/kg/min) required for acute seizure control before maintenance; risk of respiratory depression/hypotension
  - Mild renal impairment (fraction 0.85) minor here — only ~27% renal clearance; no starting dose reduction, covered by TDM
  - Engine returned null absolute dose (no adult dose in dossier); recommendation is guideline-based extrapolation
  - Exposure-matching PD assumption: adult therapeutic serum target assumed valid in child
- **Grade rationale:** Adult dossier from cache lacked any adult daily/effective/toxic dose, so the allometry×maturation engine could not solve an absolute CSS-driven dose (returned null; child CL 0.047 L/h, Vd 7.2 L, t1/2 ~107 h computed for downstream use). The recommended dose is therefore anchored to concordant, well-sourced pediatric weight-based guidelines rather than the engine — dose grade capped below A. Multip

## phenobarbital · `obese_1y_14kg`
- **Grade:** B · **Dose:** 4 mg/kg/day · **55.9s**
- **Concordance:** guideline 5 · ratio 0.8 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': False, 'pathways': False, 'enzymes': True, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=3805 cache_read=36663 | retr in=0 out=0
- **Flags:**
  - NTI drug + very long half-life (~120 h computed; 69–165 h reported in young infants) → mandatory TDM; steady state ~7–10 days; small day-to-day fluctuation.
  - Do NOT exceed 5 mg/kg/day maintenance — accumulation risk from long half-life.
  - AGE/INDICATION MISMATCH: indication labeled 'neonatal seizures' but patient is 1 year old (14 kg); neonatal-specific dosing/PK do NOT apply — used infant/child guideline band.
  - ASSUMED TERM: PMA not supplied for child <2y; engine assumed 40 wk gestation.
  - OBESITY / high weight-for-age (14 kg at 1y; ideal ≈10 kg): weight-based dose on total body weight may overexpose — consider adjusted body weight and lean on TDM.
  - EXPOSURE-MATCHING PD ASSUMPTION: dose anchored to guideline target serum concentration, not a computed adult-exposure match (engine could not solve dose).
  - Respiratory depression / hypotension risk, especially with concurrent sedatives.
  - PK sourced from shared cache (source_mode=cache), not a live retrieval this session.
- **Grade rationale:** Adult PK retrieved from shared cache (not live), and it lacked an adult daily/effective dose, so the allometry engine could not solve an absolute dose (returned CL/Vd only). Final dose is therefore anchored to convergent, high-quality pediatric guidelines rather than the engine. Multiple independent sources agree on 3–5 mg/kg/day for this age band, so concordance is strong — but reliance on guidel

## fluconazole · `neonate_5d`
- **Grade:** B · **Dose:** 1.0 mg/kg/day · **93.1s**
- **Concordance:** guideline 12 · ratio 0.083 · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 3 · rationale: True
- **Tokens:** orch in=8 out=4294 cache_read=19612 | retr in=4 out=3038
- **Flags:**
  - EXPOSURE-MATCHING PD ASSUMPTION: engine matches adult AUC; neonatal prophylaxis actually targets AUC/MIC — reconciled via extended (q72h) interval, not reduced daily rate.
  - ENGINE AUC-RATE (2.26 mg/kg/day) SELF-FLAGGED SUB-THERAPEUTIC vs 4 mg/kg/day threshold — resolved by extended-interval delivery; do NOT give as low daily dose without interval extension.
  - INDICATION AMBIGUITY: prophylaxis (3 mg/kg q72h) vs treatment of invasive candidiasis (12 mg/kg/day + optional load) — confirm before dosing.
  - NEONATE: rapidly changing GFR in first weeks — reassess/monitor renal function; consider loading dose given long t1/2 (~37 h).
  - CYP INHIBITOR: fluconazole inhibits CYP2C9/2C19/3A4 — screen co-meds (e.g. midazolam, phenytoin, phenobarbital); QTc caution.
  - ASSUMED TERM (GA 40 wk provided).
- **Grade rationale:** Live, high-confidence PK (Vd, PB, renal fm ~80%, CL) from FDA label + peer-reviewed reviews. Neonatal guideline exists (multiple RCTs + IDSA) supporting a dose that concords with the engine once dosing interval is extended. Not grade A because (1) the pure allometric AUC-rate under-doses vs the PD (AUC/MIC) target and required manual interval-extension to reconcile, and (2) the non-renal fm split 

## fluconazole · `child_2y_egfr85`
- **Grade:** B · **Dose:** 6 mg/kg/day · **56.2s**
- **Concordance:** guideline 6 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 4 · rationale: True
- **Tokens:** orch in=10 out=3841 cache_read=36340 | retr in=0 out=0
- **Flags:**
  - Guideline-anchored dose (6 mg/kg/day): engine allometric maintenance calc was sub-therapeutic (~3.7 mg/kg/day), a known fluconazole scaling limitation due to faster pediatric clearance/shorter half-life.
  - RENAL impairment flagged — organ-function modifier applied to renal pathways; predominantly renal elimination (~80% unchanged), so monitor renal function and reassess interval/dose if eGFR declines further.
  - Loading dose recommended (12 mg/kg day 1) to reach steady-state by day 2, per label — otherwise ~5 half-lives (>4 days) to steady state.
  - Exposure-matching (AUC) PD assumption: adult efficacy exposure assumed to translate to child; target AUC24 ≥400 mg·h/L for invasive candidiasis is the pediatric PD anchor.
  - CYP inhibitor (2C9/3A4/2C19) — strong drug-interaction potential; review concomitant meds even though fluconazole itself is a minor CYP substrate.
  - Starting-dose decision support only — not a prescription; verify indication severity (prophylaxis vs invasive treatment) as treatment may require up to 12 mg/kg/day.
- **Grade rationale:** Core PK from cache (not live retrieval) but high-confidence and consistent across FDA label and PK reviews; strong pediatric guideline concordance available. Allometry maintenance calc conflicted with guideline (engine ratio 0.62, below 0.67× band) so dose is anchored on guideline rather than the engine — hence B, not A.

## fluconazole · `obese_1y_14kg`
- **Grade:** B · **Dose:** 6 mg/kg/day · **56.5s**
- **Concordance:** guideline 6 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4418 cache_read=35980 | retr in=0 out=0
- **Flags:**
  - ENGINE SUB-THERAPEUTIC: allometry×maturation gave 3.7 mg/kg/day (<4 mg/kg/day MEC) and <0.67× guideline — DEFERRED to guideline 6 mg/kg/day.
  - EXPOSURE-MATCHING PD ASSUMPTION: dose selection assumes fAUC/MIC ≥100 target; verify against local Candida MIC (avoid fluconazole for C. krusei / C. glabrata).
  - ASSUMED-TERM: PMA not supplied for child <2 y; engine assumed 40-wk term gestation.
  - HIGH WEIGHT-FOR-AGE: 14 kg at 1 y (ideal ≈10 kg) — total-body-weight dosing may overestimate exposure; consider adjusted body weight.
  - LOADING DOSE: consider 12 mg/kg on day 1 (IDSA) to reach steady state faster given long t½ (~22 h child).
  - QT/DDI: fluconazole is a CYP2C9/2C19/3A4 inhibitor — review interacting drugs (QT-prolonging agents, etc.).
- **Grade rationale:** High-confidence core PK from FDA label + peer-reviewed reviews (cache), and a clear pediatric guideline consensus exists. Downgraded from A because the deterministic allometry×maturation engine under-predicts (3.7 mg/kg/day) relative to the established pediatric guideline dose (6 mg/kg/day) — engine/guideline discordant (ratio 0.62, outside 0.67–1.5×) — so the recommendation defers to the guidelin

### Batch summary (phenytoin, ibuprofen, phenobarbital, fluconazole)
- n=12 · within 0.67–1.5×: 9/12 · within 0.5–2×: 11/12
- **Tokens this batch:** orch in/out 106/47654 (cache_read 357162) · retrieval in/out 22/12268 · **total 60,050**
- finished 2026-07-11T16:56:42.891938+00:00

## Worker w4
# PaedScale validation results
Branch: `validation-eval`. Started 2026-07-11T16:45:16.311375+00:00
Harness-only. Never merge this branch to master.

## metronidazole · `neonate_5d`
- **Grade:** B · **Dose:** 30 mg/kg/day · **123.4s**
- **Concordance:** guideline 15 · ratio 2.0 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 3 · rationale: True
- **Tokens:** orch in=8 out=4190 cache_read=21024 | retr in=6 out=5773
- **Flags:**
  - ACTIVE METABOLITE: hydroxymetronidazole (30-65% activity, longer t1/2) accumulates in neonates — parent CL underestimates total active exposure
  - LONG NEONATAL HALF-LIFE (~20-23 h published) → risk of accumulation; loading dose needed, maintenance spaced by PMA
  - EXPOSURE-MATCHING PD ASSUMPTION: engine assumes adult AUC target is appropriate; guideline defers to empirical neonatal regimen instead
  - PMA AT INTERVAL BOUNDARY (40.7 wk): q6h vs q8h — confirm with local protocol
  - DERIVED ADULT CLEARANCE — engine scaling approximate
  - DURATION: limit to ~7 days in NEC per neonatal guidance; monitor for neurotoxicity/seizures with prolonged/high cumulative dose
  - DECISION SUPPORT ONLY — not a prescription; verify against institutional neonatal formulary
- **Grade rationale:** Live PK retrieved and multiple concordant published neonatal guidelines/PK studies (SCAMP/Cohen-Wolkowiez, Queensland, Iowa NICU, MOH-Malaysia) define a PMA-based regimen — strong external validation. Not grade A because the allometric engine dose-rate (15.45 mg/kg/day maintenance) does NOT concord with the guideline schedule (ratio ~0.52, below 0.67-1.5x band); guideline is deferred to over the n

## metronidazole · `child_2y_egfr85`
- **Grade:** B · **Dose:** 30 mg/kg/day · **52.8s**
- **Concordance:** guideline 30 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=3927 cache_read=38398 | retr in=0 out=0
- **Flags:**
  - ACTIVE METABOLITE: hydroxymetronidazole retains 30-65% antimicrobial activity, has a longer half-life, and is renally cleared — may accumulate with renal impairment/prolonged therapy; parent-drug clearance underestimates total active exposure.
  - RENAL impairment (function 0.85) — minimal effect on predominantly hepatic parent clearance, but monitor for hydroxy-metabolite accumulation; reassess interval on prolonged courses.
  - PD EXPOSURE-MATCHING ASSUMPTION: dose derived by matching adult AUC; assumes adult exposure-response applies to this child.
  - INDICATION LABEL MISMATCH: 'NEC-related' regimens are PMA-based neonatal protocols and do NOT apply to this 2-year-old; adult-like q8h dosing used.
  - Do not exceed 500 mg/dose or 4 g/day caps.
- **Grade rationale:** PK from cache (not live), but adult disposition parameters are well-supported (Lamp et al. review); allometry×maturation output (27.7 mg/kg/day) is concordant with an independent pediatric guideline range (30-40 mg/kg/day, ratio ~0.79-0.92). Clearance was derived rather than directly reported, and this is a STARTING dose only.

## metronidazole · `obese_1y_14kg`
- **Grade:** B · **Dose:** 30 mg/kg/day · **55.3s**
- **Concordance:** guideline 30 · ratio 1.0 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.5 · dims: `{'elimination': True, 'pathways': False, 'enzymes': False, 'transporters': True, 'active_metabolites': False, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4141 cache_read=37810 | retr in=0 out=0
- **Flags:**
  - ACTIVE METABOLITE: hydroxymetronidazole retains 30-65% activity with longer half-life — accumulates on repeated dosing; may augment effect beyond parent AUC.
  - PRODRUG/ACTIVATION: nitroimidazole requires intracellular reductive activation — parent CL ≠ effect site.
  - HIGH WEIGHT-FOR-AGE: 14 kg at 12 months (~>97th pct, ideal ≈10 kg); total-body-weight dosing may overestimate exposure — consider adjusted body weight; ideal wt hint ≈10 kg.
  - ASSUMED TERM gestation (no PMA supplied).
  - EXPOSURE-MATCHING PD ASSUMPTION used for engine dose.
  - MAX-DOSE CAP: do not exceed 500 mg/dose.
  - Consider 15 mg/kg IV loading dose for serious anaerobic infection.
  - Avoid prolonged/repeated courses — cumulative neurotoxicity risk; TDM not routine but consider in hepatic impairment.
- **Grade rationale:** PK from shared cache (not live retrieval) with derived (not directly reported) adult clearance; engine dose (22.9 mg/kg/day) is concordant with a robust published pediatric guideline (30 mg/kg/day, ratio 0.76, within 0.67–1.5×). Guideline-anchored final dose chosen. Not grade A because PK source is cached/derived and gestational age was assumed term.

## ondansetron · `neonate_5d`
- **Grade:** D · **Dose:** 0.04 mg/kg/day · **92.1s**
- **Concordance:** guideline 0.3 · ratio 0.133 · 0.67–1.5×: FAIL · 0.5–2×: FAIL
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=8 out=4399 cache_read=20567 | retr in=4 out=2506
- **Flags:**
  - OFF_LABEL_NEONATE: use restricted to >=6 months; no FDA/validated neonatal dose
  - CYP1A2_IMMATURITY: latest-maturing pathway dominates elimination (fm 0.5); neonatal clearance ~3% of adult -> overdose risk with weight-scaled dosing
  - QT_PROLONGATION_RISK: dose-independent QT effect reported; consider ECG/electrolyte monitoring in neonate
  - NO_TOXIC_THRESHOLD: mg/kg toxic dose not established in sources
  - EXPOSURE_MATCHING_PD_ASSUMPTION: efficacy target extrapolated from older children, unvalidated in neonates
  - FM_APPROXIMATE: CYP1A2/3A4/2D6 fractional split qualitative
  - ENGINE_SUBTHERAPEUTIC_WARNING vs older-child target does not credit neonatal CL immaturity; anchored to conservative neonatal literature instead
  - ASSUMED_TERM: GA 40 wk confirmed term
- **Grade rationale:** PK retrieved live (grade-A inputs), but the patient is a 5-day-old term neonate (PMA ~40.7 wk) — outside the studied/approved population. No FDA-approved or validated neonatal ondansetron dose exists; guidance restricts use to ≥6 months. Dominant elimination is via CYP1A2 (fm 0.5), the latest-maturing CYP pathway, giving a maturation factor of only 0.22 and total clearance ~3% of adult — a high-un

## ondansetron · `child_2y_egfr85`
- **Grade:** B · **Dose:** 0.398 mg/kg/day · **53.5s**
- **Concordance:** guideline 0.3 · ratio 1.327 · 0.67–1.5×: PASS · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=4010 cache_read=36502 | retr in=0 out=0
- **Flags:**
  - RENAL impairment flagged by case but clinically negligible: only ~5% renal clearance, guidelines state no renal dose adjustment needed
  - QT PROLONGATION: ondansetron prolongs QTc; single IV dose max 16 mg; screen for cardiac history/congenital QT and avoid co-administered QT-prolonging drugs
  - PD exposure-matching assumption: engine matches adult AUC; ondansetron efficacy in children is established at 0.15 mg/kg/dose empirically, supporting this target
  - Dose expressed as PRN per-dose (clinical norm) rather than continuous daily maintenance rate
  - No active metabolites; inactive metabolites do not contribute to effect
- **Grade rationale:** PK from cache (not live), concordant across Springer PK review, StatPearls and DailyMed. Engine allometry×maturation output (0.40 mg/kg/day) falls within the established pediatric guideline range when expressed as 2-3 PRN doses/day (0.15 mg/kg/dose). Downgraded from A because PK is cached and fm CYP split is qualitative/approximate; not downgraded further because guideline concordance is strong.

## ondansetron · `obese_1y_14kg`
- **Grade:** B · **Dose:** 0.15 mg/kg/day · **61.1s**
- **Concordance:** guideline 0.3 · ratio 0.5 · 0.67–1.5×: FAIL · 0.5–2×: PASS
- **Mechanism score:** 0.6666666666666666 · dims: `{'elimination': True, 'pathways': False, 'enzymes': True, 'transporters': False, 'active_metabolites': True, 'protein_binding': True}`
- **Citations:** 5 · rationale: True
- **Tokens:** orch in=10 out=3948 cache_read=36782 | retr in=0 out=0
- **Flags:**
  - [
  - "
  - E
  - N
  - G
  - I
  - N
  - E
  - /
  - G
  - U
  - I
- **Grade rationale:** PK from cache (not live retrieval). A robust, well-established pediatric guideline dose exists (0.15 mg/kg/dose IV, approved ≥6 months) and is used as the primary anchor. The allometry×maturation engine dose is DISCORDANT (grade-lowering) because its CYP1A2-anchored late-maturation curve understates infant clearance, whereas real-world pediatric PK shows HIGHER weight-normalized clearance than adu

### Batch summary (metronidazole, ondansetron)
- n=6 · within 0.67–1.5×: 3/6 · within 0.5–2×: 5/6
- **Tokens this batch:** orch in/out 56/24615 (cache_read 191083) · retrieval in/out 10/8279 · **total 32,960**
- finished 2026-07-11T16:50:31.176434+00:00


---

## Parallel subagent batch (remaining 14 drugs × 3 = 42 cases)

Workers: w1 amikacin/meropenem/cefotaxime/acyclovir · w2 levetiracetam/fentanyl/clindamycin/theophylline · w3 phenytoin/ibuprofen/phenobarbital/fluconazole · w4 metronidazole/ondansetron

### Concordance (this parallel batch)
- n=**42** · with numeric ratio **39**
- **0.67–1.5×:** 25/39 of dosed · 25/42 of all
- **0.5–2×:** 37/39 of dosed · 37/42 of all
- Grades: {'D': 2, 'C': 5, 'B': 33, 'A': 2}

### Full validation set (batches 1+2+parallel ≈ 60 scenarios)
- n=**60**
- **0.67–1.5×:** 32/53 of dosed
- **0.5–2×:** 51/53 of dosed
- Grades: {'B': 46, 'C': 7, 'A': 3, 'D': 4}

### Token usage (all logged usage_log*.jsonl — batch 2 + parallel; batch 1 not logged)
| Component | Tokens |
|-----------|--------:|
| Orch uncached in | 462 |
| Orch out | 209,739 |
| Cache read | 1,551,070 |
| Cache write | 921,351 |
| Retrieval in | 20,835 |
| Retrieval out | 79,479 |
| **Generation total** | **310,515** |
| **All fields sum** | **2,782,936** |
| Logged cases | 51 |

### Case table (parallel batch)
| Drug | Scenario | Grade | Dose | Ratio | Strict | Wide |
|------|----------|-------|------|-------|--------|------|
| acyclovir | child_2y_egfr85 | B | 60.0 | 2.0 | N | Y |
| acyclovir | neonate_5d | B | 60.0 | 1.0 | Y | Y |
| acyclovir | obese_1y_14kg | B | 60.0 | 2.0 | N | Y |
| amikacin | child_2y_egfr85 | B | 15.0 | 1.0 | Y | Y |
| amikacin | neonate_5d | B | 15.0 | 1.0 | Y | Y |
| amikacin | obese_1y_14kg | B | 15.0 | 0.789 | Y | Y |
| cefotaxime | child_2y_egfr85 | B | 225.0 | 1.5 | Y | Y |
| cefotaxime | neonate_5d | B | 100.0 | 1.0 | Y | Y |
| cefotaxime | obese_1y_14kg | B | 300.0 | 2.0 | N | Y |
| clindamycin | child_2y_egfr85 | A | 40.0 | 1.333 | Y | Y |
| clindamycin | neonate_5d | B | 15.0 | 1.0 | Y | Y |
| clindamycin | obese_1y_14kg | B | 30.0 | 1.0 | Y | Y |
| fentanyl | child_2y_egfr85 | C | None | None | N | N |
| fentanyl | neonate_5d | B | None | None | N | N |
| fentanyl | obese_1y_14kg | B | None | None | N | N |
| fluconazole | child_2y_egfr85 | B | 6.0 | 1.0 | Y | Y |
| fluconazole | neonate_5d | B | 1.0 | 0.083 | N | N |
| fluconazole | obese_1y_14kg | B | 6.0 | 1.0 | Y | Y |
| ibuprofen | child_2y_egfr85 | B | 17.0 | 0.85 | Y | Y |
| ibuprofen | neonate_5d | B | 10.0 | 1.0 | Y | Y |
| ibuprofen | obese_1y_14kg | B | 40.0 | 2.0 | N | Y |
| levetiracetam | child_2y_egfr85 | B | 55.0 | 1.375 | Y | Y |
| levetiracetam | neonate_5d | B | 20.0 | 0.5 | N | Y |
| levetiracetam | obese_1y_14kg | A | 50.0 | 1.25 | Y | Y |
| meropenem | child_2y_egfr85 | B | 120.0 | 2.0 | N | Y |
| meropenem | neonate_5d | B | 120.0 | 2.0 | N | Y |
| meropenem | obese_1y_14kg | B | 120.0 | 2.0 | N | Y |
| metronidazole | child_2y_egfr85 | B | 30.0 | 1.0 | Y | Y |
| metronidazole | neonate_5d | B | 30.0 | 2.0 | N | Y |
| metronidazole | obese_1y_14kg | B | 30.0 | 1.0 | Y | Y |
| ondansetron | child_2y_egfr85 | B | 0.398 | 1.327 | Y | Y |
| ondansetron | neonate_5d | D | 0.04 | 0.133 | N | N |
| ondansetron | obese_1y_14kg | B | 0.15 | 0.5 | N | Y |
| phenobarbital | child_2y_egfr85 | B | 4.0 | 0.8 | Y | Y |
| phenobarbital | neonate_5d | B | 4.0 | 0.8 | Y | Y |
| phenobarbital | obese_1y_14kg | B | 4.0 | 0.8 | Y | Y |
| phenytoin | child_2y_egfr85 | C | 5.0 | 0.625 | N | Y |
| phenytoin | neonate_5d | D | 5.0 | 1.0 | Y | Y |
| phenytoin | obese_1y_14kg | C | 8.0 | 1.0 | Y | Y |
| theophylline | child_2y_egfr85 | C | 6.0 | 0.5 | N | Y |
| theophylline | neonate_5d | B | 4.0 | 1.0 | Y | Y |
| theophylline | obese_1y_14kg | C | 12.0 | 1.0 | Y | Y |
