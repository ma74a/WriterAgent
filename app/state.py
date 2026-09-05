from typing import TypedDict


class BlogState(TypedDict):
    # user input
    user_prompt: str

    # Prompt analysis
    topic: str
    audience: str
    tone: str
    needs_code: bool
    needs_images: bool
    word_count: int