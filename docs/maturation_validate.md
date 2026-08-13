# Maturation TM50/Hill — validator report

Validated 2026-08-14. Numbers accepted only when they were read on an opened page.

Engine form `MF = PMA^H / (TM50^H + PMA^H)` is the same Hill sigmoid printed by Rhodin, Anand, Anderson & Larsson, Anderson & Holford (DMPK 2009), and Cristea (as `COV^H / (COV^H + TM50^H)`).

## ACCEPT (use these)

| key | TM50 (weeks PMA) | Hill | PMID | action |
|---|---|---|---|---|
| renal_gfr | 47.7 | 3.40 | 18846389 | **keep_current** |
| cyp3a4 | 73.6 | 3.0 | 20704661 | **replace_current** (engine is 55.4 / 1.83) |
| ugt2b7 | 54.2 | 3.92 | 18723857 | **replace_current** (engine is 88.3 / 1.90) |

- **renal_gfr** — PubMed 18846389: “Half of the adult value is reached at 47.7 post-menstrual weeks (95%CI 45.1-50.5), with a Hill coefficient of 3.40 (95%CI 3.03-3.80).” Same pair in the opened Anderson & Holford DMPK 2009 PDF.
- **cyp3a4** — PubMed 20704661: “The maturation half-time was 73.6 (95%CI 59.4, 80.0) weeks PMA and the Hill coefficient 3 (95%CI 2.2, 4.1).” Hill equation, PMA weeks.
- **ugt2b7** — Anand PMC2733178 Table 1: CLmat50 54.2 weeks, HillCL 3.92. Same quote on Mahmood PMC3018029. Anderson DMPK 2009 Table 3 reprints 54.2 / 3.92 (separate) and 54.6 / 3.83 (simultaneous re-fit).

## NEEDS_REVIEW (numbers real; do not put in engine as isoform keys)

| key | printed pair | why not ACCEPT for engine |
|---|---|---|
| oat1_3 | 27.3 weeks **PNA**, Hill 1.17 (Cristea PMC8096729) | PNA Hill, not PMA. `+40` conversion is not written in the paper. |
| oat1_3_protein | 30.7 weeks PNA, Hill 0.51 (Cheung, quoted by Cristea) | Protein abundance, not clearance; PNA. |
| paracetamol_mixed_ugt | 52.2 weeks PMA, Hill 3.43 (DMPK 2009 Table 1, opened PDF) | Mixed UGT1A1/1A6/1A9 + SULT. Do not map to `ugt1a1`. |
| ibuprofen_mixed | 36.8 weeks PMA, Hill 11.5 (PubMed 31472084) | Drug CL, not CYP2C9 isoform. |
| cyp2d6 | TM50 39.8 weeks PMA (Allegaert abstract); Hill 9 on Healy Table 5 quoting Allegaert | Primary full text not opened. Genotype-dominated. Engine 40 / 1.0 is unsourced. |

## REJECT (extract reject reasons are fair)

Current `constants.py` rows **cyp1a2 94/1.5**, **cyp2d6 40/1.0**, **cyp2c9 50/1.5**, **cyp2c19 44/1.5**, **ugt1a1 70/1.8** were not printed as TM50+Hill on any opened page. Comments already call them approximate / Anderson–Holford style.

No opened source printed both TM50 and Hill for **CYP1A2, CYP2C9, CYP2C19, UGT1A1, CYP2B6, CES1**. Upreti 2016 (PMID 26139104) is the likely CYP table; Wiley full text was not retrieved — not accepted from memory.

Engine **cyp3a4 55.4/1.83** and **ugt2b7 88.3/1.90** do not match the opened primaries. Anand Tvol is 88.8 **days** (volume), not CL TM50.

## Engine action if constants are updated

Keep `renal_gfr` 47.7 / 3.40. Replace `cyp3a4` with 73.6 / 3.0 (Anderson & Larsson 2011). Replace `ugt2b7` with 54.2 / 3.92 (Anand 2008). Leave the other isoform keys out (or mark unverified) until a page that prints both TM50 and Hill is opened.
