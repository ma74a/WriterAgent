from fastapi import APIRouter
from api.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
    description="Returns system operational status and API version.",
)
def health_check():
    """Returns application health status and version."""
    return HealthResponse(status="ok", version="0.1.0")
