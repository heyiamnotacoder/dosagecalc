# Demo pack (branch `demo` only)

**Never merge this branch into `master`.** This folder is for offline / low-latency demos.

## What it is
Curated adult PK + pediatric guideline midpoints for **all 20 validation drugs**:

| Drug | Pathway | Metric | Notes |
|------|---------|--------|-------|
| vancomycin | renal_gfr | auc | NTI → TDM |
| gentamicin | renal_gfr | cmax | Cmax/MIC; TDM |
| amikacin | renal_gfr | cmax | Cmax/MIC; TDM |
| ampicillin | renal_gfr | time_mic | time>MIC proxy |
| meropenem | renal_gfr | time_mic | time>MIC proxy |
| cefotaxime | renal_gfr | time_mic | time>MIC proxy |
| acyclovir | renal_gfr | css | renal |
| levetiracetam | renal_gfr | css | mostly renal unchanged |
| fluconazole | renal_gfr | css | pediatric CL may exceed allometry |
| midazolam | cyp3a4 | css | titration; high first-pass |
| fentanyl | cyp3a4 | css | titration; mcg dosing |
| clindamycin | cyp3a4 | css | hepatic CYP3A4 |
| morphine | ugt2b7 | css | active M6G |
| caffeine | cyp1a2 | css | AOP indication-sensitive |
| theophylline | cyp1a2 | css | NTI; TDM |
| phenytoin | cyp2c9 | css | Michaelis–Menten — care |
| ibuprofen | cyp2c9 | css | very high PB |
| phenobarbital | cyp2c19/cyp2c9 | css | long half-life; TDM |
| metronidazole | cyp2c9/cyp3a4 | css | active metabolite |
| ondansetron | multi-CYP | css | multi-enzyme |

## Files
- `pk.json` — adult PK dossiers (engine-ready: CL, Vd, fm, metric, …)
- `guidelines.json` — pediatric mg/kg/day midpoints + source notes

## Runtime behaviour
On branch `demo`, `retrieval.fetch()` checks this pack **before** live PubMed/openFDA:

- Hit → `source_mode: "demo"`, dossier + guideline attached (no live retrieval)
- Miss → normal live path (or cache / abstain)

All 20 drugs above are hits → demos stay offline for PK + guidelines.

## Run
```bash
cd backend
source .venv/bin/activate   # or create venv + pip install -r requirements.txt
cp .env.example .env        # ANTHROPIC_API_KEY still needed for orchestrator
uvicorn main:app --reload --port 8000
# open http://localhost:8000 — pick any of the 20 demo drugs
```

Quick no-server smoke test:
```bash
cd backend && python3 -c "import retrieval; print(retrieval.fetch('vancomycin')['source_mode'])"
# → demo
```
