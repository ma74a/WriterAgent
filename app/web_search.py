import os

from tavily import TavilyClient

class TavilyWebSearch:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY is not set in the environment."
            )

        self.client = TavilyClient(api_key)

    def search(
            self,
            query,
            max_results=5
    ):
        response = self.client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,

        )

        return response
