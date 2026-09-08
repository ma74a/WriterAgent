from functools import lru_cache
from fastapi import Depends
from app.graph import build_graph
from api.job_store import job_store, JobStore
from services.blog_service import BlogService
from services.research_service import ResearchService


@lru_cache()
def get_graph():
    """Return a singleton instance of the compiled LangGraph workflow graph."""
    return build_graph()


def get_job_store() -> JobStore:
    """Return the shared in-memory job store instance."""
    return job_store


def get_blog_service(
    graph=Depends(get_graph),
    store: JobStore = Depends(get_job_store),
) -> BlogService:
    """Return BlogService instance wired with graph and job store dependencies."""
    return BlogService(graph=graph, job_store_instance=store)


def get_research_service() -> ResearchService:
    """Return ResearchService instance."""
    return ResearchService()
