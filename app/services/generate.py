"""Content generation service using Google Gemini via the official SDK."""

import json

from ..config import GEMINI_API_KEY, GEMINI_MODEL, gemini_client
from ..prompts import blog_post_prompt


def generate_blog_post(search_context: str, keyword: str) -> tuple[str | None, str | None]:
    """Generate a blog post title and content based on search context and a keyword.

    Returns (title, content) or (None, None) on failure.
    """
    print(f"Generating blog post for: {keyword}")

    prompt = blog_post_prompt(search_context, keyword)

    try:
        if not GEMINI_API_KEY:
            print("Missing GEMINI_API_KEY. Ensure it's set in your environment or .env file.")
            return None, None

        resp = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        raw_text = getattr(resp, "text", None) or ""

        cleaned = raw_text.strip()
        if cleaned.startswith("```json") and cleaned.endswith("```"):
            cleaned = cleaned[7:-3].strip()
        elif cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned = cleaned[3:-3].strip()

        blog_data = json.loads(cleaned)
        return blog_data.get("title"), blog_data.get("content")

    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        try:
            print(f"Raw response text: {raw_text[:500] if raw_text else ''}")
        except Exception:
            pass
        return None, None
