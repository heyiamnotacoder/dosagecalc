# Demo pack (branch `demo` only)

**Never merge this branch into `master`.** This folder is for offline / low-latency demos.

## What it is
Curated adult PK + pediatric guideline midpoints for **8 validation-best drugs**:

| Drug | Pathway | Metric | Why demo-worthy |
|------|---------|--------|-----------------|
| clindamycin | CYP3A4 | css | 3/3 strict; grade A |
| amikacin | renal_gfr | cmax | 3/3 strict; NTI→TDM |
| phenobarbital | CYP2C19/2C9 | css | 3/3 strict; TDM |
| vancomycin | renal_gfr | auc | Classic NTI AUC archetype |
| levetiracetam | renal_gfr | css | Grade A case |
| ibuprofen | CYP2C9 | css | Hepatic high-PB |
| metronidazole | CYP2C9/3A4 | css | Mixed hepatic + metabolite |
| gentamicin | renal_gfr | cmax | Stage-1 aminoglycoside |

## Files
- `pk.json` — adult PK dossiers (engine-ready: CL, Vd, fm, metric, …)
- `guidelines.json` — pediatric mg/kg/day midpoints + source notes

## Runtime behaviour
On branch `demo`, `retrieval.fetch()` checks this pack **before** live PubMed/openFDA:

- Hit → `source_mode: "demo"`, dossier + optional guideline (no live retrieval)
- Miss → normal live path (or cache / abstain)

## Run
```bash
cd backend
source .venv/bin/activate   # or create venv + pip install -r requirements.txt
cp .env.example .env        # ANTHROPIC_API_KEY still needed for orchestrator
uvicorn main:app --reload --port 8000
# open http://localhost:8000 — pick a demo drug (e.g. vancomycin, 6 yr, 20 kg)
```

Quick no-server smoke test:
```bash
cd backend && python3 -c "import retrieval; print(retrieval.fetch('vancomycin')['source_mode'])"
# → demo
```
