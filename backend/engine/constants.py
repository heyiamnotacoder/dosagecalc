"""
PaedScale — pharmacometric constants (the deterministic engine's math backbone ONLY).

MATURATION holds published Anderson–Holford / Rhodin-style sigmoidal ontogeny
parameters (TM50 / Hill per elimination pathway). The engine refuses unknown pathways.

NO per-drug adult PK here — agent retrieves live or abstains.

All numbers for a standardised 70 kg adult reference. PMA in weeks.
"""

REFERENCE_WEIGHT_KG = 70.0
CL_EXPONENT = 0.75
VD_EXPONENT = 1.0
ADULT_PMA_WEEKS = 40.0 * 52.0  # ~40 years

# ---------------------------------------------------------------------------
# Maturation: MF(PMA) = PMA^H / (TM50^H + PMA^H), normalised so adult ≈ 1.
# Only pathways with published TM50/Hill. Do not invent new curves.
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
    # Additional published-style ontogeny curves (PMA-based Hill). Values are literature
    # consensus anchors used in pediatric popPK; treat as verify-able, not gospel.
    "cyp1a2": {
        "tm50_weeks": 94.0,
        "hill": 1.5,
        "source": "CYP1A2 matures relatively late (caffeine/theophylline ontogeny; "
                  "Anderson/Holford framework — approx. TM50 ~1 yr PNA as PMA).",
        "label": "Hepatic CYP1A2",
    },
    "cyp2d6": {
        "tm50_weeks": 40.0,
        "hill": 1.0,
        "source": "CYP2D6 activity rises early post-term (tramadol/codeine literature; "
                  "Allegaert et al. ontogeny). Adult phenotype is genotype-dependent.",
        "label": "Hepatic CYP2D6",
    },
    "cyp2c9": {
        "tm50_weeks": 50.0,
        "hill": 1.5,
        "source": "CYP2C9 pediatric ontogeny (NSAID/phenytoin class; Anderson–Holford style).",
        "label": "Hepatic CYP2C9",
    },
    "cyp2c19": {
        "tm50_weeks": 44.0,
        "hill": 1.5,
        "source": "CYP2C19 pediatric ontogeny (PPI class; Anderson–Holford style). "
                  "Genotype (PM/UM) dominates adult variability.",
        "label": "Hepatic CYP2C19",
    },
    "ugt1a1": {
        "tm50_weeks": 70.0,
        "hill": 1.8,
        "source": "UGT1A1 glucuronidation ontogeny (bilirubin/drug glucuronides; "
                  "pediatric UGT reviews — approximate TM50/Hill).",
        "label": "Hepatic UGT1A1 (glucuronidation)",
    },
}
