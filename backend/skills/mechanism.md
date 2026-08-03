# Mechanism selection

Map drug → engine `fm` keys only when a maturation curve exists.

**Keys:** `renal_gfr`, `cyp3a4`, `ugt2b7`, `cyp1a2`, `cyp2d6`, `cyp2c9`, `cyp2c19`, `ugt1a1`.

**Rules**
- `fm` fractions ≈ 1.0 for the cleared share; unmapped fraction → leave out (engine flags it).
- Empty lists for transporters/metabolites when none — never invent.
- **target_metric:** `auc` (vanco), `cmax` (aminoglycosides), `time_mic` (β-lactams), else `css`.
- Unknown pathway with no key → do not invent TM50; data-gap / grade C–D.
- **cmax AG:** engine may underdose vs pediatric practice → guideline-anchor + TDM flag.
- **time_mic:** daily dose is proxy only → frequent/extended dosing + grade ≤ B.
- **MM kinetics / null CL:** no linear invent → guideline or grade D.
