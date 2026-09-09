from typing import TypedDict, Annotated
import operator
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
    # content: dict
    # code: dict
    # images: dict
    # Generated content — reducers act as the fan-in barrier
    content: Annotated[list[dict], operator.add]
    code: Annotated[list[dict], operator.add]
    images: Annotated[list[dict], operator.add]

    # Final output
    final_blog: str

    # Review
    review: str