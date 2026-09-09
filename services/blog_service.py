import json
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional
from app.graph import build_graph
from api.job_store import JobStore, job_store as default_job_store


def to_dict(val: Any) -> Any:
    """Recursively convert Pydantic models or containers to JSON-serializable dicts."""
    if hasattr(val, "model_dump"):
        return val.model_dump()
    if hasattr(val, "dict"):
        return val.dict()
    if isinstance(val, dict):
        return {k: to_dict(v) for k, v in val.items()}
    if isinstance(val, list):
        return [to_dict(v) for v in val]
    return val


def extract_dict(val: Any) -> dict:
    """Extract a dictionary from state, unwrapping list reducer structures if present."""
    d = to_dict(val)
    if isinstance(d, list) and len(d) > 0:
        return d[0] if isinstance(d[0], dict) else {}
    if isinstance(d, dict):
        return d
    return {}


class BlogService:
    """Service wrapping LangGraph execution and streaming for blog generation."""

    def __init__(self, graph=None, job_store_instance: Optional[JobStore] = None):
        self.graph = graph if graph is not None else build_graph()
        self.job_store = job_store_instance if job_store_instance is not None else default_job_store

    def generate(self, prompt: str) -> dict[str, Any]:
        """Synchronously execute the LangGraph blog generation agent."""
        blog_id = str(uuid.uuid4())
        
        # Invoke LangGraph
        result = self.graph.invoke({"user_prompt": prompt})

        # Process and serialize node outputs
        analysis = to_dict(result.get("analysis", {}))
        plan = to_dict(result.get("plan", {}))
        research = to_dict(result.get("research", {}))
        code = extract_dict(result.get("code", {}))
        images = extract_dict(result.get("images", {}))
        blog = result.get("final_blog", "")

        # Save into in-memory store
        saved = self.job_store.save_blog(
            blog_id=blog_id,
            prompt=prompt,
            blog=blog,
            analysis=analysis,
            plan=plan,
            research=research,
            code=code,
            images=images,
        )

        return {
            "id": blog_id,
            "success": True,
            "prompt": prompt,
            "blog": blog,
            "analysis": analysis,
            "plan": plan,
            "research": research,
            "code": code,
            "images": images,
            "created_at": saved["created_at"],
        }

    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Asynchronously stream node execution events via Server-Sent Events (SSE)."""
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        accumulated_state: Dict[str, Any] = {
            "user_prompt": prompt,
            "analysis": {},
            "plan": {},
            "research": {},
            "code": {},
            "images": {},
            "final_blog": "",
        }

        # Save initial job placeholder in store
        self.job_store.save_blog(
            blog_id=job_id,
            prompt=prompt,
            created_at=created_at,
        )

        try:
            # Stream node updates from LangGraph
            async for node_update in self.graph.astream({"user_prompt": prompt}, stream_mode="updates"):
                for node_name, node_output in node_update.items():
                    serialized_output = to_dict(node_output)
                    
                    # Update accumulated state
                    if isinstance(serialized_output, dict):
                        for k, v in serialized_output.items():
                            if k in accumulated_state:
                                accumulated_state[k] = v

                    event_payload = {
                        "event": "node_complete",
                        "job_id": job_id,
                        "node": node_name,
                        "data": serialized_output,
                    }
                    yield f"data: {json.dumps(event_payload)}\n\n"

            # Workflow completed - extract final serialized elements
            analysis = to_dict(accumulated_state.get("analysis", {}))
            plan = to_dict(accumulated_state.get("plan", {}))
            research = to_dict(accumulated_state.get("research", {}))
            code = extract_dict(accumulated_state.get("code", {}))
            images = extract_dict(accumulated_state.get("images", {}))
            blog = accumulated_state.get("final_blog", "")

            # Update final record in in-memory job store
            self.job_store.save_blog(
                blog_id=job_id,
                prompt=prompt,
                blog=blog,
                analysis=analysis,
                plan=plan,
                research=research,
                code=code,
                images=images,
                created_at=created_at,
            )

            done_payload = {
                "event": "done",
                "job_id": job_id,
                "done": True,
                "prompt": prompt,
                "blog": blog,
                "analysis": analysis,
                "plan": plan,
                "research": research,
                "code": code,
                "images": images,
                "created_at": created_at,
            }
            yield f"data: {json.dumps(done_payload)}\n\n"

        except Exception as e:
            error_payload = {
                "event": "error",
                "job_id": job_id,
                "done": True,
                "detail": str(e),
            }
            yield f"data: {json.dumps(error_payload)}\n\n"
