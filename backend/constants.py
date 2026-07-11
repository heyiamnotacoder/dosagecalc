"""
PaedScale — pharmacometric constants (the deterministic engine's math backbone ONLY).

This file holds MATURATION — the *stable* Anderson–Holford / Rhodin sigmoidal ontogeny
parameters (TM50 / Hill per elimination pathway). These are the textbook constants the
engine needs to scale clearance by age; the engine refuses to invent a curve for an unknown
pathway, so they live in code.

There is deliberately NO per-drug adult PK here. Adult clearance / Vd / fm-split / protein
binding / etc. are drug-specific values the agent must RETRIEVE LIVE (retrieval.py → PubMed +
openFDA) or abstain on — never a hardcoded fallback. The reviewed adult-PK values used to
SCORE the live agent live in eval_data/drug_pk.json and are read only by the test harness /
dev endpoints, never by the production agent path.

ALL numbers are reference values for a standardised 70 kg adult. PMA is in *weeks*.

NOTE ON RIGOUR: the maturation TM50/Hill values are widely-cited literature figures; treat
them as verify-able, not gospel.
"""

# ---------------------------------------------------------------------------
# Allometric scaling (West/Anderson standardised framework)
# ---------------------------------------------------------------------------
REFERENCE_WEIGHT_KG = 70.0
CL_EXPONENT = 0.75          # clearance scales with WT^0.75
VD_EXPONENT = 1.0           # volume scales ~ linearly with WT

# Adult postmenstrual age used to normalise the maturation function to ~1.
# (An adult is far past every TM50, so MF(adult) ≈ 1 already; we keep this explicit.)
ADULT_PMA_WEEKS = 40.0 * 52.0  # ~40 years

# ---------------------------------------------------------------------------
# Maturation functions — MF(PMA) = PMA^H / (TM50^H + PMA^H)
# Keyed by elimination pathway. tm50 in weeks PMA, hill dimensionless.
# ---------------------------------------------------------------------------
MATURATION = {
    "renal_gfr": {
        "tm50_weeks": 47.7,
        "hill": 3.40,
        "source": "Rhodin MM et al., Pediatr Nephrol 2009 — GFR maturation model.",
        "label": "Renal (glomerular filtration)",
    },
    "cyp3a4": {
        "tm50_weeks": 55.4,
        "hill": 1.83,
        "source": "Anderson BJ & Holford NHG — CYP3A4 clearance ontogeny "
                  "(midazolam-anchored maturation).",
        "label": "Hepatic CYP3A4",
    },
    "ugt2b7": {
        "tm50_weeks": 88.3,
        "hill": 1.90,
        "source": "Anderson BJ et al. — morphine (UGT2B7) glucuronidation maturation.",
        "label": "Hepatic UGT2B7 (glucuronidation)",
    },
}
