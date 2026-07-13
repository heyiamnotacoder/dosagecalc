"""
PaedScale — real retrieval tool layer (single source of truth).

Pure httpx functions that hit FREE public endpoints — NCBI E-utilities (PubMed) and openFDA
drug labels. No Anthropic key needed; these are the actual network calls behind both the
retrieval subagent (retrieval.py) and the MCP server (mcp_server.py).

Every function is defensive: it returns a dict with an "error" key on failure and never
raises, so a flaky fetch degrades gracefully instead of crashing the dosing request.
"""

from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import urlparse

import httpx

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OPENFDA_LABEL = "https://api.fda.gov/drug/label.json"
_TOOL = "paedscale"
_EMAIL = os.environ.get("NCBI_EMAIL", "paedscale@example.com")
_TIMEOUT = float(os.environ.get("RETRIEVAL_HTTP_TIMEOUT", "12"))

# Hostnames that must never be fetched (SSRF).
_BLOCKED_HOSTS = frozenset({
    "localhost", "localhost.localdomain", "metadata", "metadata.google.internal",
    "metadata.goog", "instance-data",
})


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


def _is_blocked_ip(ip_str: str) -> bool:
    """True for private, loopback, link-local, multicast, reserved, or unspecified addresses."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_reserved
        or addr.is_unspecified
    )


def _ssrf_guard(url: str) -> str | None:
    """Return an error message if URL is not safe to fetch; else None."""
    try:
        parsed = urlparse(url)
    except Exception:
        return "invalid URL"
    if parsed.scheme not in ("http", "https"):
        return "url must start with http:// or https://"
    host = (parsed.hostname or "").strip().lower()
    if not host:
        return "url missing hostname"
    if host in _BLOCKED_HOSTS or host.endswith(".local") or host.endswith(".internal"):
        return f"SSRF blocked: hostname '{host}' is not allowed"
    # Literal IP in the URL
    try:
        if _is_blocked_ip(host):
            return f"SSRF blocked: address '{host}' is not a public IP"
    except Exception:
        pass
    # DNS resolve and reject any non-public A/AAAA
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        return f"SSRF blocked: cannot resolve host '{host}': {e}"
    if not infos:
        return f"SSRF blocked: no addresses for '{host}'"
    for info in infos:
        ip = info[4][0]
        if _is_blocked_ip(ip):
            return f"SSRF blocked: '{host}' resolves to non-public address {ip}"
    return None


def web_fetch(url: str, max_chars: int = 10000) -> dict:
    """Fetch plain text from a public URL (size-capped). SSRF-guarded; no redirects."""
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        return {"url": url, "text": "", "error": "url must start with http:// or https://"}
    ssrf_err = _ssrf_guard(url)
    if ssrf_err:
        return {"url": url, "text": "", "error": ssrf_err}
    try:
        # No redirects: a 30x to 169.254.169.254 or an internal host would bypass the pre-check.
        r = httpx.get(
            url,
            timeout=_TIMEOUT,
            follow_redirects=False,
            headers={"User-Agent": "PaedScale/0.2 (pediatric-dosing-research; educational)"},
        )
        if r.status_code in (301, 302, 303, 307, 308):
            loc = r.headers.get("location", "")
            return {
                "url": url, "text": "",
                "error": f"redirects disabled (SSRF guard); got {r.status_code} → {loc[:200]}",
            }
        r.raise_for_status()
        ctype = (r.headers.get("content-type") or "").lower()
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            return {"url": url, "text": "", "error": "PDF binary not extracted; use HTML or abstract sources"}
        text = r.text.strip()
        # strip coarse tags if HTML
        if "html" in ctype or text[:200].lower().lstrip().startswith("<!doctype") or "<html" in text[:500].lower():
            import re
            text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", text)
            text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
            text = re.sub(r"(?s)<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
        return {"url": url, "text": text[:max_chars], "truncated": len(text) > max_chars,
                "status_code": r.status_code}
    except Exception as e:
        return {"url": url, "text": "", "error": f"web_fetch failed: {e}"}


# Registry so retrieval.py and mcp_server.py wrap the exact same callables.
TOOL_FUNCS = {
    "pubmed_search": lambda a: pubmed_search(a["query"], a.get("retmax", 5)),
    "pubmed_fetch": lambda a: pubmed_fetch(a["pmids"], a.get("max_chars", 3500)),
    "openfda_label": lambda a: openfda_label(a["drug"], a.get("max_field_chars", 1500)),
    "web_fetch": lambda a: web_fetch(a["url"], a.get("max_chars", 10000)),
}

TOOL_SCHEMAS = [
    {
        "name": "pubmed_search",
        "description": "Search PubMed; returns PMIDs. Load skill 'pubmed' first if unsure how to query.",
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
        "description": "FDA label text (dosing/safety). Load skill 'openfda' if unsure. Not structured PK.",
        "input_schema": {
            "type": "object",
            "properties": {"drug": {"type": "string"}},
            "required": ["drug"],
        },
    },
    {
        "name": "web_fetch",
        "description": "Fetch text from a specific URL. Load skill 'webfetch' first. Size-capped.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "max_chars": {"type": "integer", "default": 10000},
            },
            "required": ["url"],
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
