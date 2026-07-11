"""
PaedScale — MCP server exposing the live retrieval tools.

Wraps the SAME callables used by the retrieval subagent (retrieval_tools.py) as MCP tools,
so PubMed + openFDA retrieval is available to any MCP client (Claude Desktop, Claude Code,
the MCP inspector, or an Agent-SDK subagent), not just our in-process loop.

Run as a stdio MCP server:
    python mcp_server.py

Register it (e.g. in an .mcp.json / Claude Desktop config):
    {"mcpServers": {"paedscale-retrieval": {"command": "python",
      "args": ["backend/mcp_server.py"]}}}

The retrieval subagent (retrieval.py) calls these functions in-process by default for latency;
this server is the MCP surface for the identical capability.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from retrieval_tools import openfda_label as _openfda_label
from retrieval_tools import pubmed_fetch as _pubmed_fetch
from retrieval_tools import pubmed_search as _pubmed_search

mcp = FastMCP("paedscale-retrieval")


@mcp.tool()
def pubmed_search(query: str, retmax: int = 5) -> dict:
    """Search PubMed; return the most relevant PMIDs for adult-PK literature."""
    return _pubmed_search(query, retmax)


@mcp.tool()
def pubmed_fetch(pmids: str) -> dict:
    """Fetch abstract text for one or more PMIDs (comma-separated string)."""
    return _pubmed_fetch(pmids)


@mcp.tool()
def openfda_label(drug: str) -> dict:
    """Fetch key sections (indications, dosing, clinical pharmacology, warnings) of the FDA label."""
    return _openfda_label(drug)


if __name__ == "__main__":
    mcp.run()
