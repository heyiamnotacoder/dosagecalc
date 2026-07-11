# Edge cases

Call `assess_edge_cases` after retrieve (and after compute if dose exists). Merge returned flags into `submit_recommendation.flags`.

| Trigger | Action |
|---------|--------|
| Prodrug / active moiety | Flag: parent CL ≠ effect; check metabolite maturation |
| Obesity (high wt for age) | Flag overestimation risk; dosing_weight is a **hint only** |
| High PB (≥90%) + neonate/illness | Flag free-fraction ↑ |
| Renal/hepatic impairment or critical illness | Flag organ OF / PD assumptions |

Do not silently rewrite the engine dose without a flag.
