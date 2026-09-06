from pathlib import Path
from urllib.parse import urlparse
import mimetypes

import requests


class OpenverseImageSearch:
    BASE_URL = "https://api.openverse.org/v1/images/"

    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def search(self, query: str, page_size: int = 5):
        """
        Search Openverse for openly licensed images.
        """

        params = {
            "q": query,
            "page_size": page_size,
            "mature": "false",
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])

    def download(
        self,
        image: dict,
        output_path: str,
    ):
        """
        Download an image from an Openverse search result.
        """

        image_url = image.get("url")

        if not image_url:
            raise ValueError("Image result does not contain a URL.")

        response = requests.get(
            image_url,
            timeout=self.timeout,
            stream=True,
            headers={
                "User-Agent": "WriterAgent/1.0"
            },
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if not content_type.startswith("image/"):
            raise ValueError(
                f"URL did not return an image. "
                f"Content-Type: {content_type}"
            )

        output_file = Path(output_path)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(output_file, "wb") as file:
            for chunk in response.iter_content(
                chunk_size=8192
            ):
                if chunk:
                    file.write(chunk)

        return output_file