from typing import TypedDict
from app.schemas import (
    PromptAnalysis,
    BlogPlan,
    ResearchContext
)


class BlogState(TypedDict):
    # user input
    user_prompt: str

    # Analysis
    analysis: PromptAnalysis

    # Research
    research: ResearchContext

    # Planner
    plan: BlogPlan

    # Generated content
    content: dict
    code: dict
    images: dict

    # Final output
    final_blog: str

    # Review
    review: str