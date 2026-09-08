from datetime import datetime, timezone
import threading
from typing import Any, Optional


class JobStore:
    """Thread-safe in-memory store for generated blogs and streaming jobs."""

    def __init__(self):
        self._blogs: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def save_blog(
        self,
        blog_id: str,
        prompt: str,
        blog: str = "",
        analysis: Optional[dict[str, Any]] = None,
        plan: Optional[dict[str, Any]] = None,
        research: Optional[dict[str, Any]] = None,
        code: Optional[dict[str, Any]] = None,
        images: Optional[dict[str, Any]] = None,
        created_at: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create or update a blog record in memory."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self._lock:
            existing = self._blogs.get(blog_id)
            if existing:
                record = existing
                record["prompt"] = prompt or record.get("prompt", "")
                record["blog"] = blog if blog != "" else record.get("blog", "")
                if analysis is not None:
                    record["analysis"] = analysis
                if plan is not None:
                    record["plan"] = plan
                if research is not None:
                    record["research"] = research
                if code is not None:
                    record["code"] = code
                if images is not None:
                    record["images"] = images
                record["updated_at"] = now
            else:
                record = {
                    "id": blog_id,
                    "prompt": prompt,
                    "blog": blog,
                    "analysis": analysis or {},
                    "plan": plan or {},
                    "research": research or {},
                    "code": code or {},
                    "images": images or {},
                    "created_at": created_at or now,
                    "updated_at": now,
                }
                self._blogs[blog_id] = record
            
            return dict(record)

    def get_blog(self, blog_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a single blog post by UUID."""
        with self._lock:
            blog = self._blogs.get(blog_id)
            return dict(blog) if blog else None

    def list_blogs(self) -> list[dict[str, Any]]:
        """Return all blog posts sorted newest first."""
        with self._lock:
            blogs = list(self._blogs.values())
        
        # Sort by created_at timestamp descending (newest first)
        blogs.sort(key=lambda b: b.get("created_at", ""), reverse=True)
        return [dict(b) for b in blogs]

    def delete_blog(self, blog_id: str) -> bool:
        """Delete a blog post by UUID."""
        with self._lock:
            if blog_id in self._blogs:
                del self._blogs[blog_id]
                return True
            return False


# Global singleton instance
job_store = JobStore()
