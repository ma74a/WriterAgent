import os
from typing import Any
from app.web_search import TavilyWebSearch


class ResearchService:
    """Service layer wrapping Tavily search for direct web research."""

    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 5) -> dict[str, Any]:
        """Perform a web search using Tavily without exposing credentials."""
        searcher = TavilyWebSearch()
        raw_response = searcher.search(query=query, max_results=max_results)
        
        # Format results cleanly
        results = raw_response.get("results", []) if isinstance(raw_response, dict) else []
        
        return {
            "query": query,
            "results": results,
        }
