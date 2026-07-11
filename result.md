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
