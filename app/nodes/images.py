import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.state import BlogState
from app.nodes.diagram import generate_diagram, save_diagram


# Absolute output dir — safe regardless of where the process is launched from
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output" / "images"


def create_filename(section_title: str) -> str:
    """
    Convert a section title into a safe, slug-style filename (no extension).
    """

    filename = section_title.lower()
    filename = re.sub(r"[^a-z0-9]+", "-", filename)
    return filename.strip("-")


def fetch_diagram_for_section(section, topic: str) -> tuple[str, dict]:
    """
    Generate and save an LLM SVG diagram for a single section.
    Returns (section_title, image_result_dict).
    Designed to run inside a thread pool.
    """

    print(f"\nGenerating diagram: {section.title!r}")

    filename = create_filename(section.title)

    svg = generate_diagram(
        topic=topic,
        section_title=section.title,
        description=section.description,
    )

    if not svg:
        print(f"Diagram generation failed for: {section.title!r}")
        return section.title, {
            "status":      "error",
            "type":        "diagram",
            "description": section.description,
            "error":       "LLM returned invalid or empty SVG.",
        }

    saved_path = save_diagram(svg, filename, OUTPUT_DIR)

    print(f"Diagram saved: {saved_path}")

    return section.title, {
        "status":   "downloaded",
        "type":     "diagram",
        "filename": saved_path.name,
        "path":     f"images/{saved_path.name}",
        "source":   "AI-generated diagram",
    }


def image_handler(state: BlogState):

    analysis = state["analysis"]
    plan     = state["plan"]

    # Only process sections that need an image
    sections_needing_images = [s for s in plan.sections if s.needs_image]

    images: dict[str, dict] = {}

    if not sections_needing_images:
        return {"images": [images]}

    # Generate all diagrams in parallel — one thread per section
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_diagram_for_section, section, analysis.topic): section
            for section in sections_needing_images
        }

        for future in as_completed(futures):
            section = futures[future]
            try:
                title, result = future.result()
                images[title] = result
            except Exception as e:
                print(f"Diagram generation failed for {section.title!r}: {e}")
                images[section.title] = {
                    "status":      "error",
                    "type":        "diagram",
                    "description": section.description,
                    "error":       str(e),
                }

    # Wrap in list to satisfy the Annotated[list[dict], operator.add] reducer
    return {"images": [images]}