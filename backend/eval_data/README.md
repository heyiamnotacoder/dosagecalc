# eval_data — the answer keys (NOT used by the product)

These files are **evaluation oracles**. The test harness reads them to score the live agent.
The production agent path (`/calculate` → `agent.py` → `retrieval.py`) **never** reads them —
it retrieves drug PK live (PubMed + openFDA) or abstains. Keeping the oracle out of the agent
is deliberate: if the model had a hardcoded fallback it could return canned numbers instead of
genuinely retrieving, and the eval would be scoring itself.

| File | Role | Read by |
|------|------|---------|
| `drug_pk.json` | Reviewed adult PK + mechanism per drug | `test_pk.py` (deterministic engine check), `/pk` dev endpoint |
| `guidelines.json` | Pediatric guideline doses for the concordance band | `test_pk.py`, `test_agent.py` (scores agent's live dose) |
| `mechanism_truth.json` | Correct mechanism per drug (6 PRD dimensions) | `mechanism_score.py` / `test_agent.py` |

All values are reviewed seeds — verify against BNFc/Lexicomp/label before any real use.
Empty lists in `mechanism_truth.json` are meaningful (correct-negatives, e.g. "no transporter").
