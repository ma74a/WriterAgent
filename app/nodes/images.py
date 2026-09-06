import re

from app.state import BlogState
from app.image_search import OpenverseImageSearch


image_search = OpenverseImageSearch()


def create_image_query(
    topic: str,
    section_title: str,
    description: str,
):
    """
    Create a concise search query for the image.
    """

    return (
        f"{topic} "
        f"{section_title} "
        f"{description}"
    )


def create_filename(section_title: str):
    """
    Convert section title into a safe filename.
    """

    filename = section_title.lower()

    filename = re.sub(
        r"[^a-z0-9]+",
        "-",
        filename,
    )

    filename = filename.strip("-")

    return filename


def image_handler(state: BlogState):

    analysis = state["analysis"]
    plan = state["plan"]

    images = {}

    for section in plan.sections:

        if not section.needs_image:
            continue

        print(
            f"\nSearching image: {section.title}"
        )

        query = create_image_query(
            topic=analysis.topic,
            section_title=section.title,
            description=section.description,
        )

        try:

            results = image_search.search(
                query=query,
                page_size=5,
            )

            if not results:
                print(
                    f"No images found for: "
                    f"{section.title}"
                )

                images[section.title] = {
                    "status": "not_found",
                    "query": query,
                    "description": section.description,
                }

                continue

            # For now, use the first result.
            selected = results[0]

            filename = create_filename(
                section.title
            )

            output_path = (
                f"output/images/"
                f"{filename}.jpg"
            )

            local_file = image_search.download(
                image=selected,
                output_path=output_path,
            )

            images[section.title] = {
                "status": "downloaded",

                "query": query,

                "title": selected.get(
                    "title"
                ),

                "url": selected.get(
                    "url"
                ),

                "source": selected.get(
                    "source"
                ),

                "provider": selected.get(
                    "provider"
                ),

                "license": selected.get(
                    "license"
                ),

                "license_version": selected.get(
                    "license_version"
                ),

                "license_url": selected.get(
                    "license_url"
                ),

                "creator": selected.get(
                    "creator"
                ),

                "creator_url": selected.get(
                    "creator_url"
                ),

                "source_url": selected.get(
                    "foreign_landing_url"
                ),

                "filename": local_file.name,

                "path": (
                    f"images/"
                    f"{local_file.name}"
                ),
            }

            print(
                f"Downloaded: {local_file}"
            )

        except Exception as e:

            print(
                f"Image search failed for "
                f"{section.title}: {e}"
            )

            images[section.title] = {
                "status": "error",
                "query": query,
                "description": section.description,
                "error": str(e),
            }

    return {
        "images": images
    }