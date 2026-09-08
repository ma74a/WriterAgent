from fastapi import APIRouter, Depends, HTTPException, status
from api.dependencies import get_research_service
from api.schemas import ErrorResponse, ResearchRequest, ResearchResponse
from services.research_service import ResearchService

router = APIRouter()


@router.post(
    "/research",
    response_model=ResearchResponse,
    tags=["Research"],
    summary="Perform web research",
    description="Executes direct web research via Tavily without exposing the API key.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameter"},
        500: {"model": ErrorResponse, "description": "Research execution failure"},
    },
)
def search_web(
    request: ResearchRequest,
    research_service: ResearchService = Depends(get_research_service),
):
    """Execute direct web search using Tavily."""
    query = request.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Research query cannot be empty.",
        )

    try:
        result = research_service.search(query=query)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research search failed: {str(e)}",
        )
