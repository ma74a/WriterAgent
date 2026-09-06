from typing import TypedDict
from app.schemas import (
    PromptAnalysis,
    BlogPlan
)


class BlogState(TypedDict):
    # user input
    user_prompt: str

    # Prompt analysis
    analysis: PromptAnalysis

    # Planner
    plan: BlogPlan

    # Generated content
    content: dict
    code: dict
    images: dict

    # Final output
    final_output: str

    # Review
    review: str