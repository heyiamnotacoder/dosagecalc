# I want to build the paedia-scale which is a ai callibarated dosage calculator.

## this is PRD file explaining how everything will be made.

## Framework:
It will be mainly based on Next.JS frontend with Fast API as backend.

## How will it work:
It work as ai assisted dosage calculator, not scaling linearly with dosage.

## Governing scope (sequential rollout):
This is the decision that overrides the more ambitious "any drug" language elsewhere. We
build in stages and only widen once the previous stage passes on cost, accuracy, and
mechanistic reasoning:
- **Stage 1 (MVP):** 3 linear-PK (dose-proportional, non-saturable) drugs, end to end,
  one per elimination archetype:
  - **Midazolam** — CYP3A4 (cleanest, best-characterized ontogeny).
  - **Vancomycin** — renal (GFR). NOTE: AUC/MIC-driven + narrow-TI → output must recommend TDM, not stand alone.
  - **Morphine** — UGT2B7 glucuronidation. NOTE: active renally-cleared metabolite (M6G) → must be flagged.
- **Stage 2:** 5-10 drugs commonly dose-calculated by paediatricians.
- **Stage 3:** 20-drug eval set.
At each stage measure: cost/query (must stay < $1), latency (< 60s), concordance accuracy,
and mechanistic-reasoning score before expanding.

## Pipeline:
1. User gives drug name, age, indication, weight, and problem (hepatic impairment or renal impairment). For a child under 2 yr, also collect postmenstrual age (gestational + postnatal age) or preterm/gestational date; if the user answers "unknown", assume term/normal development AND surface that assumption in the output.
2. an LLM loop is fired which takes this information.
3. It gets the drug data from openFDA and web search/ pubmed/ scholarly which includes adult clearance, volume, bioavailability, protein binding, and the fraction cleared by each route, toxic dosage and minimum effective dosage from the label and literature. NOTE: openFDA is reliable for label *text*, not for structured numeric PK — clearance, Vd, fraction metabolised (fm) split, and protein binding usually come from literature / PubMed / DrugBank-style sources, so budget retrieval for those rather than expecting openFDA fields.
3.1 another subagent fired for getting guideline dosage.
4. It applies Anderson–Holford maturation model to clearance of all pathway using pre determined python script.
5. the final dosage is given with cited rationale, explicit assumptions, uncertainty, data-gap flags, narrow-therapeutic-index warnings, and — where one exists — a concordance check against the published guideline.

this is how a usual happy case should look like. there are 2-3 sub agents fired who have skills for data retrival and have API access of openFDA, webFetch, webSearch, PubMED mcp, scholarly MCP. they retrieve drug data and guidelines (if present) and then main orchastror do the reasoning.

6. In case of patient with hepatic and renal impairement the dose would be calculate after correcting clearance. this will be cited by LLM.

## things that i must need in backend:
1. constants:
a. Maturation function for all major enzymes and proteins tm50, Hill constants. NOTE: published TM50/Hill exist only for a handful of pathways (CYP3A4, CYP1A2, CYP2D6, UGT1A1, renal GFR). For any pathway with no published constants, do NOT invent them — emit a data-gap flag and widen the uncertainty band instead of returning a false-confident number.
b. constant tables for eGFR and other needed to execute this. NOTE: pediatric eGFR (bedside Schwartz) needs height + serum creatinine — a bare hepatic/renal toggle cannot quantify the organ-function modifier. Either collect height + creatinine, or scope renal/hepatic impairment out of the Stage-1 MVP.
c. adult data constants.

### cite-or-abstain rule (applies to all PK values)
Every fm-split / TM50 / Hill / Vd / protein-binding value used in a calculation must carry a source. Unsourced values widen the uncertainty band or block a point estimate — they are never silently invented. This is the credibility guardrail for the whole pathway-decomposition step.

2. logic/functions:
a. logic to find clearance for each pathway.
b. there must be function that calculate new clearance based on Hepatic impairement or renal impairement. The decision should be taken purely by llm based on data it has (for ex. calculating hepatic impaired dose is totally illogical for 100% renally cleared drug.)

3. common sense:
there should be a method in which if the calculated dose is > toxic dose OR calculated dose < effective dose then llm gives the reason that the dose that was calculated can not be recommended.

4. Edge cases and Test eval.
## Edge cases:

1. some drugs are optimised for diffrent exposure matric for ex time>MIC (β-lactams) vs Cmax/MIC (aminoglycosides) vs AUC (vancomycin). LLM should be able to flag this and tell weather dose calculation will stand or not.
2. obesity 
3. Protein binding 
4. Oral bioavailibility
5. active metabolites
6. pro-drugs

## Guideline / concordance source:
Guideline doses are retrieved live via web/PubMed at query time for the open-ended
"any drug" path. CAVEAT: the concordance check is the whole credibility move, and a
subagent fetching the wrong formulation/indication silently corrupts it. So for the
**eval set specifically**, cache the retrieved guideline doses into a small reviewed JSON
so headline accuracy numbers are reproducible and not at the mercy of a flaky fetch on
demo day. Keep live retrieval only for the open-ended path.

## Test eval: never shown in production 

I want to run a complete test eval for the drug set (built up 2-3 → 5-10 → 20 per the sequential rollout above) which can be judged on following evals:
1. concordance band: fraction of estimates within **1.5× / 0.67×** of the guideline dose (the old "within 10%" bar is too strict — legitimate mechanistic extrapolation lands 1.5-2× off and is still clinically defensible). Report % within 1.5×/0.67× AND % within 50% as a stratified headline number.
2. weighted kappa — flavor only; n≈20 is statistically thin, do not lead with it.
3. ICC — flavor only, same caveat.
4. mechanistic reasoning:
    Did the model correctly identify:
    * Clearance pathway
    * Hepatic vs renal elimination
    * CYP enzymes
    * Transporters
    * Active metabolites
    * Protein binding

## the API key will be given in .env file.

## Frontend:
1. initially drug, indication, age, weight, and toggle based hepatic and renal impairement will be asked.
2. then one line reasoning like chat bots (chatgpt, gemini and anthropic) will be shown.
3. a final output will have final dose recommendation, guidelines suggestions, cited rationale, grading the dosage recommendation (from A - strong evidence, passes the concordance test. B, C - parse PK data, no guidelines). The output must also carry: (a) the exposure-matching assumption flag — matching adult exposure assumes pediatric PD target = adult, which is not always true (e.g. neonatal receptor sensitivity); (b) the "assumed term development" flag when PMA was unknown.
4. further questioning with chat bar at the bottom with preloaded Q&A.
5. [post-MVP] round the raw mg output to available formulations/concentrations so the dose is bedside-actionable (a raw "3.7 mg" for a neonate is not directly usable).



## things that we should build:
1. caching system 
2. a db for storing those quaries
3. a landing page for concept and how and why to use it.
4. auth system.

## Optimise for:
1. i have anthropic api keys we can use it for work, but cost of one quary should never touch more than 1$.
2. also this whole thing must not take more than 1 min.
3. optimise code for performance, dont bloat up prompts keep it lean.
4. this is hackathon projects which values claude use soo try to include multiagent system, mcps, skills, skills with agent.
5. architecture to hold <$1 / <60s: lean multi-agent — Opus orchestrator + 1-2 retrieval subagents on Haiku/Sonnet, PubMed MCP, a deterministic Python PK tool, one data-retrieval skill. Reserve Opus for pathway decomposition + synthesis; put retrieval on the cheaper/faster models. This still shows multiagent + MCP + skills for judging without blowing the latency/cost budget.

## current deliverable:
built frontend and backend run on local host run test. i dont think caching, db and auth will be needed for now.

also if you are any llm maintain a CLAUDE.md and agent.MD and write most of details in CLAUDE.md and key details in AGENT.md and route agent.md to claude.md for all the details. 
