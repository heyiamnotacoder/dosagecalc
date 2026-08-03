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
