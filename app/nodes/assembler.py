from app.state import BlogState


def blog_assembler(state: BlogState):

    print("\nAssembling blog...")

    plan = state["plan"]
    content = state["content"]
    code = state["code"]
    images = state["images"]

    parts = []

    # Title
    parts.append(f"# {plan.title}")

    # Introduction
    if "Introduction" in content:
        parts.append("## Introduction")
        parts.append(content["Introduction"])

    # Main sections
    for section in plan.sections:

        title = section.title

        # Section heading
        parts.append(f"## {title}")

        # Section content
        if title in content:
            parts.append(content[title])


        # Code
        if title in code:

            generated_code = code[title]

            parts.append(
                f"### Example: {title}"
            )

            parts.append(
                generated_code.explanation
            )

            if generated_code.dependencies:

                dependencies = "\n".join(
                    f"- `{dependency}`"
                    for dependency in generated_code.dependencies
                )

                parts.append(
                    "### Dependencies\n\n"
                    + dependencies
                )

            parts.append(
                f"```{generated_code.language}\n"
                f"{generated_code.code}\n"
                f"```"
            )

        # Images
        if title in images:
            image = images[title]
            parts.append(
                "### Diagram"
            )
            parts.append(
                f"<!-- Image: {image['description']} -->"
            )

    # Conclusion
    if "Conclusion" in content:
        parts.append("## Conclusion")
        parts.append(content["Conclusion"])

    final_blog = "\n\n".join(parts)

    return {
        "final_blog": final_blog
    }