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
