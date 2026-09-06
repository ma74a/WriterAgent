from pathlib import Path
import markdown


def save_markdown(
    content: str,
    filename: str = "blog.md",
):
    output_dir = Path("output")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_dir / filename

    output_file.write_text(
        content,
        encoding="utf-8"
    )

    print(
        f"\nMarkdown saved to: {output_file}"
    )

    return output_file


def save_html(
    content: str,
    filename: str = "blog.html",
):
    output_dir = Path("output")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    html_body = markdown.markdown(
        content,
        extensions=[
            "fenced_code",
            "tables",
        ],
    )

    html_document = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AI Generated Blog</title>
</head>

<body>

{html_body}

</body>

</html>
"""

    output_file = output_dir / filename

    output_file.write_text(
        html_document,
        encoding="utf-8"
    )

    print(
        f"HTML saved to: {output_file}"
    )

    return output_file