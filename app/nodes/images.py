from app.state import BlogState


def image_handler(state: BlogState):

    plan = state["plan"]

    images = {}

    for section in plan.sections:

        if not section.needs_image:
            continue

        print(f"\nPreparing image: {section.title}")

        images[section.title] = {
            "type": "diagram",
            "description": section.description,
            "status": "pending",
        }

    return {
        "images": images
    }