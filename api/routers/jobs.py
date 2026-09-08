import markdown
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse

from api.dependencies import get_job_store
from api.job_store import JobStore
from api.schemas import BlogListItem, BlogResponse, ErrorResponse, ImageMetadataItem

router = APIRouter()


@router.get(
    "/blogs",
    response_model=List[BlogListItem],
    tags=["Blogs"],
    summary="List all generated blog posts",
    description="Returns a list of all in-memory blog posts sorted newest first.",
)
def list_blogs(store: JobStore = Depends(get_job_store)):
    """List all blogs (newest first)."""
    return store.list_blogs()


@router.get(
    "/blog/{blog_id}",
    response_model=BlogResponse,
    tags=["Blogs"],
    summary="Get a single blog post by ID",
    description="Retrieves full structured data for a specific blog post by UUID.",
    responses={
        404: {"model": ErrorResponse, "description": "Blog post not found"},
    },
)
def get_blog(blog_id: str, store: JobStore = Depends(get_job_store)):
    """Retrieve a single blog post."""
    blog = store.get_blog(blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID '{blog_id}' not found.",
        )
    return blog


@router.delete(
    "/blog/{blog_id}",
    tags=["Blogs"],
    summary="Delete a blog post",
    description="Deletes a blog post from the in-memory store by UUID.",
    responses={
        404: {"model": ErrorResponse, "description": "Blog post not found"},
    },
)
def delete_blog(blog_id: str, store: JobStore = Depends(get_job_store)):
    """Delete a blog post by ID."""
    deleted = store.delete_blog(blog_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID '{blog_id}' not found.",
        )
    return {"message": "Blog deleted successfully", "id": blog_id}


@router.get(
    "/blog/{blog_id}/markdown",
    response_class=PlainTextResponse,
    tags=["Blogs"],
    summary="Get raw blog markdown",
    description="Returns the raw generated Markdown text of a blog post.",
    responses={
        404: {"model": ErrorResponse, "description": "Blog post not found"},
    },
)
def get_blog_markdown(blog_id: str, store: JobStore = Depends(get_job_store)):
    """Return raw markdown string for a blog post."""
    blog = store.get_blog(blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID '{blog_id}' not found.",
        )
    return PlainTextResponse(content=blog.get("blog", ""), media_type="text/plain")


@router.get(
    "/blog/{blog_id}/html",
    response_class=HTMLResponse,
    tags=["Blogs"],
    summary="Get rendered HTML blog post",
    description="Renders the blog post Markdown content into full HTML without saving to disk.",
    responses={
        404: {"model": ErrorResponse, "description": "Blog post not found"},
    },
)
def get_blog_html(blog_id: str, store: JobStore = Depends(get_job_store)):
    """Render and return HTML content for a blog post."""
    blog = store.get_blog(blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID '{blog_id}' not found.",
        )
    
    content = blog.get("blog", "")
    html_body = markdown.markdown(
        content,
        extensions=[
            "fenced_code",
            "tables",
        ],
    )

    html_document = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AI Generated Blog</title>
</head>

<body>

{html_body}

</body>

</html>
"""
    return HTMLResponse(content=html_document, media_type="text/html")


@router.get(
    "/blog/{blog_id}/images",
    response_model=List[ImageMetadataItem],
    tags=["Blogs"],
    summary="Get blog image metadata list",
    description="Returns metadata for all images associated with the blog post without exposing internal file paths.",
    responses={
        404: {"model": ErrorResponse, "description": "Blog post not found"},
    },
)
def get_blog_images(blog_id: str, store: JobStore = Depends(get_job_store)):
    """Return image metadata list for a blog post."""
    blog = store.get_blog(blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID '{blog_id}' not found.",
        )
    
    images_dict = blog.get("images", {}) or {}
    metadata_list: List[ImageMetadataItem] = []

    for section_title, img_info in images_dict.items():
        if isinstance(img_info, dict) and img_info.get("filename"):
            metadata_list.append(
                ImageMetadataItem(
                    filename=img_info.get("filename", ""),
                    source=img_info.get("source"),
                    creator=img_info.get("creator"),
                    license=img_info.get("license"),
                    source_url=img_info.get("source_url"),
                )
            )

    return metadata_list
