import os
import mimetypes
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
import requests

load_dotenv()


class PexelsImageSearch:
    """
    Image search and download using the Pexels API.

    Free tier:
        - 200 requests/hour
        - 20,000 requests/month
        - No attribution required but appreciated

    Get a free API key at: https://www.pexels.com/api/
    Set it as PEXELS_API_KEY environment variable.
    """

    BASE_URL = "https://api.pexels.com/v1/search"

    def __init__(self, api_key: str = "", timeout: int = 20):
        self.timeout = timeout
        self.api_key = api_key or os.getenv("PEXELS_API_KEY", "")

        if not self.api_key:
            raise ValueError(
                "Pexels API key is required. "
                "Set PEXELS_API_KEY environment variable "
                "or pass it to the constructor."
            )

        self.headers = {
            "Authorization": self.api_key,
            "User-Agent": "WriterAgent/1.0",
        }

    def search(self, query: str, page_size: int = 5) -> list[dict]:
        """
        Search Pexels for high-quality images.

        Returns a list of image dicts, each containing:
            - url: direct image URL (original size)
            - large2x / large / medium / small: resized variants
            - photographer, photographer_url
            - avg_color
            - width, height
        """

        params = {
            "query": query,
            "per_page": min(page_size, 80),   # Pexels max is 80
            "orientation": "landscape",        # better for blog sections
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()
        photos = data.get("photos", [])

        # Normalize to a flat dict matching the shape images.py expects
        return [self._normalize(photo) for photo in photos]

    def _normalize(self, photo: dict) -> dict:
        """
        Flatten Pexels photo dict into a consistent shape.
        """
        src = photo.get("src", {})

        return {
            # Direct URLs
            "url":    src.get("large2x") or src.get("original"),
            "thumb":  src.get("medium"),

            # Dimensions (for quality scoring)
            "width":  photo.get("width", 0),
            "height": photo.get("height", 0),

            # Attribution
            "title":       photo.get("alt", ""),
            "creator":     photo.get("photographer", ""),
            "creator_url": photo.get("photographer_url", ""),
            "source":      "Pexels",
            "source_url":  photo.get("url", ""),   # Pexels page for the photo
            "license":     "Pexels License",
            "license_url": "https://www.pexels.com/license/",
            "provider":    "pexels",
        }

    def download(self, image: dict, output_path: str) -> Path:
        """
        Download an image from a Pexels search result.

        Detects the real file extension from the URL or Content-Type
        header — does not assume .jpg.
        """

        image_url = image.get("url")

        if not image_url:
            raise ValueError("Image result does not contain a URL.")

        response = requests.get(
            image_url,
            timeout=self.timeout,
            stream=True,
            headers={"User-Agent": "WriterAgent/1.0"},
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if not content_type.startswith("image/"):
            raise ValueError(
                f"URL did not return an image. "
                f"Content-Type: {content_type}"
            )

        # Detect the real extension; fall back to .jpg
        output_file = Path(output_path)
        if not output_file.suffix:
            ext = self._detect_extension(image_url, content_type)
            output_file = output_file.with_suffix(ext)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return output_file

    @staticmethod
    def _detect_extension(url: str, content_type: str) -> str:
        """
        Try URL path first, then Content-Type header.
        """

        VALID = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

        # 1. Try URL path
        ext = Path(urlparse(url).path).suffix.lower()
        if ext in VALID:
            return ext

        # 2. Try Content-Type
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ""
        if ext in VALID:
            return ext

        return ".jpg"
