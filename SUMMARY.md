# PaedScale — Summary

For the **paediatrician and clinical pharmacologist** facing a drug with no paediatric label,
PaedScale derives a defensible *starting* dose for a child from published adult pharmacokinetics.
Its thesis: drug clearance does not scale linearly with body size early in life — eliminating
organs are still maturing — so weight-linear scaling over-doses the young. PaedScale models that
gap with allometry × organ maturation (Anderson–Holford) and returns a graded, cited rationale.

The build is genuinely **multi-agent**: an Opus orchestrator drives a cheaper Sonnet retrieval
subagent that gathers adult PK live from PubMed and openFDA, exposed over an **MCP server**, with
lean **skills** loaded on demand. Python does the arithmetic; Claude does the judgment — mapping
each drug to its elimination pathway. Crucially, **cite-or-abstain is enforced in code**: the
engine refuses to invent a maturation curve for an unknown pathway and flags unattributed
clearance. Hard safety stops withhold above-toxic or non-viable doses, and the agent reports where
its own model fails. **Decision support, not prescribing.**
