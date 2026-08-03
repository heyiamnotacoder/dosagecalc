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
