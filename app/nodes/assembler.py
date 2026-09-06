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

            if image["status"] == "downloaded":

                parts.append(
                    f"![{title}]({image['path']})"
                )

                creator = image.get("creator")
                source = image.get("source")
                license_name = image.get("license")
                source_url = image.get("source_url")

                attribution = []

                if creator:
                    attribution.append(
                        f"Creator: {creator}"
                    )

                if source:
                    attribution.append(
                        f"Source: {source}"
                    )

                if license_name:
                    attribution.append(
                        f"License: {license_name}"
                    )

                if source_url:
                    attribution.append(
                        f"[View original]({source_url})"
                    )

                if attribution:
                    parts.append(
                        "*"
                        + " · ".join(attribution)
                        + "*"
                    )

    else:

        parts.append(
            f"<!-- Image unavailable: "
            f"{image.get('description', '')} -->"
        )

    # Conclusion
    if "Conclusion" in content:
        parts.append("## Conclusion")
        parts.append(content["Conclusion"])

    final_blog = "\n\n".join(parts)

    return {
        "final_blog": final_blog
    }