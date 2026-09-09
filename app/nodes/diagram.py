from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import llm


diagram_llm = llm  # plain LLM — we want raw SVG, not structured output


def generate_diagram(topic: str, section_title: str, description: str) -> str | None:
    """
    Ask the LLM to generate a clean SVG diagram for a blog section.
    Returns a raw SVG string, or None if generation fails validation.
    """

    system_prompt = """
    You are a technical diagram generator for blog posts.

    Generate a clean, minimal SVG diagram that visually explains a concept.

    Strict rules:
    - Return ONLY the raw SVG. No markdown, no backticks, no explanation, no preamble.
    - Start with <svg and end with </svg>.
    - Always include: xmlns="http://www.w3.org/2000/svg" and viewBox="0 0 800 450".
    - Add a white background: <rect width="800" height="450" fill="#ffffff"/>.
    - Font: font-family="Arial, sans-serif" throughout.
    - Use only these colors:
        #2563eb  — blue (primary, arrows, highlights)
        #1e293b  — dark slate (text, borders)
        #f1f5f9  — light gray (node backgrounds)
        #ffffff  — white (card backgrounds)
        #10b981  — green (success / output nodes)
        #f59e0b  — amber (decision / branching nodes)
    - Prefer boxes, arrows, and labels over complex illustrations.
    - Every node must have a text label inside it.
    - Arrow markers must use a proper <defs> block with a markerEnd.
    - Make it fully self-explanatory — no legend needed.
    - No external images, no JavaScript, no <script>, no <image> tags.
    """

    user_prompt = f"""
    Blog topic: {topic}
    Section title: {section_title}
    Section description: {description}

    Generate an SVG diagram that visually explains this section's concept.
    Keep it clear and minimal — this will be embedded in a blog post.
    """

    response = diagram_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    svg = response.content.strip()

    # Strip accidental markdown fences the LLM sometimes adds
    if svg.startswith("```"):
        lines = svg.splitlines()
        svg = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

    # Validate it looks like an SVG
    if not (svg.startswith("<svg") and "</svg>" in svg):
        return None

    return svg


def save_diagram(svg: str, filename: str, output_dir: str | Path) -> Path:
    """
    Save an SVG string to disk.
    Returns the Path of the saved file.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{filename}.svg"
    path.write_text(svg, encoding="utf-8")

    return path
