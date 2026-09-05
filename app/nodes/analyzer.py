from app.state import BlogState


def prompt_analyzer(state: BlogState):
    prompt = state["user_prompt"]

    print(f"prompt: {prompt}")

    # Temporary result
    analysis = {
        "topic": "Retrieval-Augmented Generation",
        "audience": "beginners",
        "tone": "educational",
        "needs_code": True,
        "needs_images": True,
        "word_count": 1500,
    }

    return analysis