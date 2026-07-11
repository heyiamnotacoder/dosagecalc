"""
PaedScale — real retrieval tool layer (single source of truth).

Pure httpx functions that hit FREE public endpoints — NCBI E-utilities (PubMed) and openFDA
drug labels. No Anthropic key needed; these are the actual network calls behind both the
retrieval subagent (retrieval.py) and the MCP server (mcp_server.py).

Every function is defensive: it returns a dict with an "error" key on failure and never
raises, so a flaky fetch degrades gracefully instead of crashing the dosing request.
"""

from __future__ import annotations

import os

import httpx

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OPENFDA_LABEL = "https://api.fda.gov/drug/label.json"
_TOOL = "paedscale"
_EMAIL = os.environ.get("NCBI_EMAIL", "paedscale@example.com")
_TIMEOUT = float(os.environ.get("RETRIEVAL_HTTP_TIMEOUT", "12"))


def _ncbi_params(extra: dict) -> dict:
    p = {"tool": _TOOL, "email": _EMAIL}
    key = os.environ.get("NCBI_API_KEY")
    if key:
        p["api_key"] = key
    p.update(extra)
    return p


def pubmed_search(query: str, retmax: int = 5) -> dict:
    """Search PubMed; return a list of PMIDs for `query` (most relevant first)."""
    try:
        r = httpx.get(
            f"{NCBI_BASE}/esearch.fcgi",
            params=_ncbi_params({"db": "pubmed", "term": query,
                                 "retmax": retmax, "retmode": "json", "sort": "relevance"}),
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        return {"query": query, "pmids": ids}
    except Exception as e:
        return {"query": query, "pmids": [], "error": f"pubmed_search failed: {e}"}


def pubmed_fetch(pmids: list[str] | str, max_chars: int = 6000) -> dict:
    """Fetch abstract text for one or more PMIDs (truncated for token budget)."""
    if isinstance(pmids, str):
        pmids = [p.strip() for p in pmids.split(",") if p.strip()]
    if not pmids:
        return {"pmids": [], "text": "", "error": "no PMIDs supplied"}
    try:
        r = httpx.get(
            f"{NCBI_BASE}/efetch.fcgi",
            params=_ncbi_params({"db": "pubmed", "id": ",".join(pmids),
                                 "rettype": "abstract", "retmode": "text"}),
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        text = r.text.strip()
        return {"pmids": pmids, "text": text[:max_chars],
                "truncated": len(text) > max_chars}
    except Exception as e:
        return {"pmids": pmids, "text": "", "error": f"pubmed_fetch failed: {e}"}


# Label sections most useful for PK / safety extraction (kept short for token budget).
_LABEL_FIELDS = [
    "indications_and_usage", "dosage_and_administration", "clinical_pharmacology",
    "pharmacokinetics", "warnings", "warnings_and_cautions", "boxed_warning",
]


def openfda_label(drug: str, max_field_chars: int = 1500) -> dict:
    """Fetch key sections of the openFDA drug label for `drug` (generic-name search)."""
    try:
        params = {"search": f'openfda.generic_name:"{drug}"', "limit": 1}
        fda_key = os.environ.get("OPENFDA_API_KEY")
        if fda_key:
            params["api_key"] = fda_key  # raises the openFDA rate limit
        r = httpx.get(OPENFDA_LABEL, params=params, timeout=_TIMEOUT)
        if r.status_code == 404:
            return {"drug": drug, "found": False, "note": "no openFDA label match"}
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return {"drug": drug, "found": False}
        label = results[0]
        out = {"drug": drug, "found": True}
        for f in _LABEL_FIELDS:
            if f in label:
                val = label[f]
                text = " ".join(val) if isinstance(val, list) else str(val)
                out[f] = text[:max_field_chars]
        return out
    except Exception as e:
        return {"drug": drug, "found": False, "error": f"openfda_label failed: {e}"}


# Registry so retrieval.py and mcp_server.py wrap the exact same callables.
TOOL_FUNCS = {
    "pubmed_search": lambda a: pubmed_search(a["query"], a.get("retmax", 5)),
    "pubmed_fetch": lambda a: pubmed_fetch(a["pmids"], a.get("max_chars", 3500)),
    "openfda_label": lambda a: openfda_label(a["drug"], a.get("max_field_chars", 1500)),
}

TOOL_SCHEMAS = [
    {
        "name": "pubmed_search",
        "description": "Search PubMed for a query; returns the most relevant PMIDs. Use to find "
                       "primary literature for adult PK (clearance, Vd, fm-split, protein binding).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "retmax": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "pubmed_fetch",
        "description": "Fetch abstract text for one or more PMIDs (comma-separated string or list).",
        "input_schema": {
            "type": "object",
            "properties": {"pmids": {"type": "string"}},
            "required": ["pmids"],
        },
    },
    {
        "name": "openfda_label",
        "description": "Fetch key sections (indications, dosing, clinical pharmacology, warnings) "
                       "of the FDA drug label. Reliable for label TEXT and safety, not structured PK.",
        "input_schema": {
            "type": "object",
            "properties": {"drug": {"type": "string"}},
            "required": ["drug"],
        },
    },
]


if __name__ == "__main__":
    import json
    print("pubmed_search('gentamicin pediatric clearance pharmacokinetics'):")
    s = pubmed_search("gentamicin pediatric clearance pharmacokinetics", retmax=3)
    print(" ", s)
    if s.get("pmids"):
        f = pubmed_fetch(s["pmids"][:1], max_chars=400)
        print("  fetch[0] excerpt:", (f.get("text") or f.get("error"))[:200].replace("\n", " "))
    lbl = openfda_label("gentamicin")
    print("  openfda_label found:", lbl.get("found"),
          "| sections:", [k for k in lbl if k not in ("drug", "found")][:4])
