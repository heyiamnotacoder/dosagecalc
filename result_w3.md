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
