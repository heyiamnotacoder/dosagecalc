# Maturation (TM50 / Hill) extract

Extracted 2026-08-14 from **opened** primary papers and abstracts. Numbers were not filled from memory. Engine form:

```
MF(PMA) = PMA^H / (TM50^H + PMA^H)
```

This is the same sigmoid Holford/Anderson write as `1 / (1 + [PMA/TM50]^(-H))`.

## Include (verified TM50 + Hill)

| proposed_key | TM50 (weeks PMA) | Hill | PMID | Source |
|---|---:|---:|---|---|
| `renal_gfr` | **47.7** | **3.40** | 18846389 | Rhodin 2009 *Pediatr Nephrol* (abstract + Anderson 2009 DMPK restatement) |
| `cyp3a4` | **73.6** | **3.0** | 20704661 | Anderson & Larsson 2010/11 midazolam IV CL |
| `ugt2b7` | **54.2** | **3.92** | 18723857 | Anand 2008 NEOPAIN morphine, Table 1 (PMC2733178) |
| `oat1_3` | **67.3** (converted) | **1.17** | 33948771 | Cristea 2021 in-vivo OAT1/3; raw TM50 = **27.3 weeks PNA** |

### Quotes

- **GFR (Rhodin):** “Half of the adult value is reached at 47.7 post-menstrual weeks (95%CI 45.1–50.5), with a Hill coefficient of 3.40 (95%CI 3.03–3.80).”
- **CYP3A4 (Anderson/Larsson):** “The maturation half-time was 73.6 (95%CI 59.4, 80.0) weeks PMA and the Hill coefficient 3 (95%CI 2.2, 4.1).”
- **UGT2B7 (Anand Table 1):** CLmat50 54.2 weeks (50.3–60.5); HillCL 3.92 (3.25–4.40).
- **OAT1/3 (Cristea):** half-adult CLint at PNA 27.3 weeks (RSE 28%); Hill 1.17 (RSE 36%). Converted with +40 weeks (term).

## Needs review (Hill+TM50 published, but not a clean engine key)

| proposed_key | TM50 | Hill | Why not drop-in |
|---|---:|---:|---|
| `oat1_3_protein` | 70.7 PMA (30.7 PNA) | 0.51 | Cheung 2019 **protein** abundance, not function (PMID 31127606) |
| `paracetamol_mixed_ugt` | 52.2 | 3.43 | Anderson 2009 DMPK Table 1; mixed UGT1A1/1A6/1A9 + SULT |
| `ibuprofen_mixed` | 36.8 | 11.5 | Anderson 2019 (PMID 31472084); drug CL, not CYP2C9 |

## Reject (no verified TM50+Hill, or wrong equation)

**Engine rows that do not match opened primaries**

| Engine key | constants.py | Opened primary |
|---|---|---|
| `cyp3a4` | 55.4 / 1.83 | **73.6 / 3** (Anderson 2010). 55.4/1.83 never seen. |
| `ugt2b7` | 88.3 / 1.90 | **54.2 / 3.92** (Anand 2008). 88.3/1.90 never seen. |
| `cyp1a2` | 94.0 / 1.5 | not found |
| `cyp2d6` | 40.0 / 1.0 | not found; genotype-dominated |
| `cyp2c9` | 50.0 / 1.5 | not found |
| `cyp2c19` | 44.0 / 1.5 | not found; genotype-dominated |
| `ugt1a1` | 70.0 / 1.8 | not found |

`renal_gfr` 47.7 / 3.40 **does** match Rhodin.

**Papers opened that do not yield a Hill pair**

- Anderson & Holford 2008 *Annu Rev Pharmacol Toxicol* (PMID 17914927) — concept only.
- Holford, Heo & Anderson 2013 *J Pharm Sci* (PMID 23650116) — 46-drug **compilation** table (useful pointers; tramadol row is exponential, not Hill).
- Johnson, Rostami-Hodjegan & Tucker 2006 Simcyp (PMID 16928154) — no TM50/Hill in opened abstract.
- Salem 2014 CYP1A2/3A4 (PMID 24671884) — **not** a simple Hill (1A2 rises then falls).
- Upreti & Wahlstrom 2016 (PMID 26139104) — Age50/Hill table almost certainly exists; **paywalled**, not extracted.
- Farhan 2024 UGT ontogeny (PMID 38898531) — table not in abstract.
- Allegaert 2015 tramadol (PMID 25258277) — TM50 39.8 weeks for CYP2D6-mediated M1 formation, **Hill not printed**.
- Potts 2009 dexmedetomidine (PMID 19708909) — Hill mentioned, numbers not in abstract.
- Ince 2013 midazolam — “novel” function, not engine Hill.
- CYP3A7 (declining), CES1, NAT2, SULT1A1, UGT1A6/1A9, P-gp, OCT2, CYP2B6/2C8/2E1/3A5 — no verified pair.

## Conversion caveat

Only convert when the paper uses **years or weeks of PNA**. Formula used: `TM50_weeks_PMA ≈ (years_PNA × 52) + 40`. Cristea/Cheung used **weeks PNA**; Rhodin, Anand, Anderson/Larsson already used **weeks PMA** — do not add 40 again.

## Highest-value unread tables

If a later pass can open full text:

1. **Upreti & Wahlstrom 2016** (DOI 10.1002/jcph.585) — in-vivo vs in-vitro Age50 + Hill for all major hepatic CYPs.
2. **Farhan, Dahal & Wahlstrom 2024** (DOI 10.1002/jcph.2484) — same for UGT1A1/1A4/1A6/1A9/2B7/2B10/2B15/2B17.
3. **Cheung 2019 figures** — exact TM50/Hill for P-gp and OCT2 protein.

## Implication for `constants.py`

Keep Rhodin GFR. Replace CYP3A4 and UGT2B7 with the opened primary pairs. Remove or quarantine CYP1A2, CYP2D6, CYP2C9, CYP2C19, UGT1A1 until a paper that prints both TM50 and Hill is opened. OAT1/3 is the only new key with a verified in-vivo Hill pair.
