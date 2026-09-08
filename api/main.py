import logging
import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.routers import generate, health, jobs, research

# Set up logger
logger = logging.getLogger("writeragent.api")
logging.basicConfig(level=logging.INFO)

# Define OpenAPI Tags
tags_metadata = [
    {
        "name": "System",
        "description": "System health and operational status endpoints.",
    },
    {
        "name": "Blogs",
        "description": "Blog generation, streaming, and storage management endpoints.",
    },
    {
        "name": "Research",
        "description": "Direct web search and context retrieval endpoints.",
    },
]

app = FastAPI(
    title="WriterAgent API",
    description="Backend API powering the WriterAgent AI blog writing platform.",
    version="0.1.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware using environment-based settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(research.router, prefix="/api")

# Mount static files directory if present
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        """Serve the black-themed web UI at root URL."""
        return FileResponse("static/index.html")


# Global Exception Handler for unexpected server errors (500)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."},
    )
