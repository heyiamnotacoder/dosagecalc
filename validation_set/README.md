# Validation set (harness only)

**Do not merge the `validation-eval` branch into master.**  
**Backend product code must never import this folder.**

| File | Purpose |
|------|---------|
| `drug_data.json` | Adult PK + mechanism truth for scoring |
| `guideline_data.json` | Guideline midpoints for 3 case scenarios × each drug |
| `run_batch.py` | Offline runner: live agent vs this oracle → appends `../result.md` |

Scenarios: `neonate_5d`, `child_2y_egfr85`, `obese_1y_14kg`.
