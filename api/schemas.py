from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str = Field(..., description="System status indicator", example="ok")
    version: str = Field(..., description="Application version", example="0.1.0")


class BlogGenerateRequest(BaseModel):
    """Request payload for blog generation."""
    prompt: str = Field(..., description="The user prompt describing the desired blog post", min_length=1)


class ImageMetadataItem(BaseModel):
    """Metadata for an image associated with a blog post section."""
    filename: str = Field(..., description="Local image filename without path")
    source: Optional[str] = Field(None, description="Image source or platform")
    creator: Optional[str] = Field(None, description="Creator or author of the image")
    license: Optional[str] = Field(None, description="License name or type")
    source_url: Optional[str] = Field(None, description="Web landing page URL for the image")


class BlogResponse(BaseModel):
    """Detailed response model for a generated blog entry."""
    id: str = Field(..., description="Unique UUID identifier of the blog post")
    success: bool = Field(True, description="Generation status flag")
    prompt: str = Field(..., description="The user prompt used for generation")
    blog: str = Field(..., description="Final generated markdown content")
    analysis: Optional[dict[str, Any]] = Field(default_factory=dict, description="Prompt analysis output")
    plan: Optional[dict[str, Any]] = Field(default_factory=dict, description="Blog structure plan")
    research: Optional[dict[str, Any]] = Field(default_factory=dict, description="Web research context")
    code: Optional[dict[str, Any]] = Field(default_factory=dict, description="Generated code examples")
    images: Optional[dict[str, Any]] = Field(default_factory=dict, description="Generated image metadata mapping")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: Optional[str] = Field(None, description="ISO 8601 last updated timestamp")


class BlogListItem(BaseModel):
    """Summary/full entry model for blog post list endpoint."""
    id: str = Field(..., description="Unique UUID identifier of the blog post")
    prompt: str = Field(..., description="The user prompt used for generation")
    blog: str = Field(..., description="Final generated markdown content")
    analysis: Optional[dict[str, Any]] = Field(default_factory=dict, description="Prompt analysis output")
    plan: Optional[dict[str, Any]] = Field(default_factory=dict, description="Blog structure plan")
    research: Optional[dict[str, Any]] = Field(default_factory=dict, description="Web research context")
    code: Optional[dict[str, Any]] = Field(default_factory=dict, description="Generated code examples")
    images: Optional[dict[str, Any]] = Field(default_factory=dict, description="Generated image metadata mapping")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last updated timestamp")


class ResearchRequest(BaseModel):
    """Request payload for direct web research."""
    query: str = Field(..., description="Search query string", min_length=1)


class ResearchResponse(BaseModel):
    """Response model for direct web research."""
    query: str = Field(..., description="Original search query")
    results: list[dict[str, Any]] = Field(default_factory=list, description="Search result items")


class ErrorResponse(BaseModel):
    """Standardized API error response model."""
    detail: str = Field(..., description="Human-readable error explanation")
