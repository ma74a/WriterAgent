from app.state import BlogState
from app.schemas import (
    ResearchSource,
    ResearchResult,
    ResearchContext
)
from app.web_search import TavilyWebSearch

taivly_search = TavilyWebSearch()

def create_search_query(topic):
    return [
        f"{topic} overview",
        f"{topic} best practices",
        f"{topic} examples",
    ]

def web_searcher(state: BlogState):
    analysis = state["analysis"]
    topic = analysis.topic

    print("\nStarting web research...")
    print(f"Topic: {topic}")

    search_queries = create_search_query(topic=topic)
    # search_results = taivly_search.search(query=search_query)

    research_results = []
    for query in search_queries:
        response = taivly_search.search(query=query)

        sources = []
        for result in response.get("results", []):
            source = ResearchSource(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", ""),
                score=result.get("score", 0.0)
            )

            sources.append(source)

        research_results.append(
            ResearchResult(
                query=query,
                sources=sources,
            )
        )
        print(f"Found {len(sources)} sources.")

    research = ResearchContext(
        results=research_results
    )

    print("\nWeb research completed.")

    return {
        "research": research
    }    