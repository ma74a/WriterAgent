from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from api.dependencies import get_blog_service
from api.schemas import BlogGenerateRequest, BlogResponse, ErrorResponse
from services.blog_service import BlogService

router = APIRouter()


@router.post(
    "/blog/generate",
    response_model=BlogResponse,
    tags=["Blogs"],
    summary="Generate a complete blog post",
    description="Invokes the WriterAgent workflow synchronously to generate a full blog post from a user prompt.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid prompt or request"},
        500: {"model": ErrorResponse, "description": "Generation execution error"},
    },
)
def generate_blog(
    request: BlogGenerateRequest,
    blog_service: BlogService = Depends(get_blog_service),
):
    """Synchronously generate a blog post."""
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty.",
        )

    try:
        result = blog_service.generate(prompt=request.prompt)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate blog: {str(e)}",
        )


@router.post(
    "/blog/generate/stream",
    tags=["Blogs"],
    summary="Stream blog post generation",
    description="Streams Server-Sent Events (SSE) as each LangGraph node completes during generation.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid prompt or request"},
    },
)
async def generate_blog_stream(
    request: BlogGenerateRequest,
    blog_service: BlogService = Depends(get_blog_service),
):
    """Stream blog post generation node-by-node via SSE."""
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty.",
        )

    event_generator = blog_service.generate_stream(prompt=request.prompt)
    return StreamingResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
