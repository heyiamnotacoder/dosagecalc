# PubMed retrieval

1. `pubmed_search`: `"{drug} pharmacokinetics clearance volume adult"` (add enzyme/renal if known).
2. `pubmed_fetch` top 1–2 PMIDs only.
3. Extract CL (L/h or mL/min → convert), Vd (L), fm-split, PB% — cite PMID.
4. Null any number you cannot source. Max one search + one fetch unless a critical gap remains.
