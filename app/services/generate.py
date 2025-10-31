"""Content generation service using Google Gemini via the official SDK.

Updated to use Gemini structured output (response_schema) instead of prompt-based JSON.
"""

import json
from typing import Any, Dict, List, Optional, TypedDict

from typing import TypedDict as _TypedDictAlias  # avoid name clash in hints

from ..config import GEMINI_API_KEY, GEMINI_MODEL, gemini_client
from ..prompts import blog_post_prompt


class AuthorIn(TypedDict, total=False):
    name: str
    twitter: Optional[str]
    avatarUrl: Optional[str]


class PostIn(TypedDict, total=False):
    slug: Optional[str]
    title: str
    summary: Optional[str]
    contentHtml: str
    date: Optional[str]
    image: Optional[str]
    readingTimeMinutes: Optional[int]


class PostBundle(TypedDict, total=False):
    post: PostIn
    tags: List[str]
    authors: List[AuthorIn]


def _post_bundle_schema() -> Dict[str, Any]:
    """Build a dict schema compatible with response_schema (OpenAPI-like)."""
    return {
        "type": "OBJECT",
        "properties": {
            "post": {
                "type": "OBJECT",
                "properties": {
                    "slug": {"type": "STRING"},
                    "title": {"type": "STRING"},
                    "summary": {"type": "STRING"},
                    "contentHtml": {"type": "STRING"},
                    "date": {"type": "STRING", "format": "date-time"},
                    "image": {"type": "STRING"},
                    "readingTimeMinutes": {"type": "INTEGER"},
                },
                "required": ["title", "contentHtml"],
            },
            "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
            "authors": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING"},
                        "twitter": {"type": "STRING"},
                        "avatarUrl": {"type": "STRING"},
                    },
                    "required": ["name"],
                },
            },
        },
        "required": ["post"],
    }


def generate_blog_post(search_context: str, keyword: str) -> Optional[PostBundle]:
    """Generate a structured post bundle using Gemini structured output.

    Returns a PostBundle dict or None on failure.
    """
    print(f"Generating blog post for: {keyword}")

    prompt = blog_post_prompt(search_context, keyword)

    try:
        if not GEMINI_API_KEY:
            print("Missing GEMINI_API_KEY. Ensure it's set in your environment or .env file.")
            return None

        schema = _post_bundle_schema()
        resp = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )

        # With structured output, response.text is guaranteed to be JSON.
        raw_text = getattr(resp, "text", None) or "{}"
        data: Dict[str, Any] = json.loads(raw_text)

        # Basic shape normalization
        post: Dict[str, Any] = data.get("post") or {}
        tags: List[str] = data.get("tags") or []
        authors: List[Dict[str, Any]] = data.get("authors") or []

        # Backward compatibility if model emitted flat {title, content}
        if not post and ("title" in data or "contentHtml" in data or "content" in data):
            post = {
                "title": data.get("title"),
                "contentHtml": data.get("contentHtml") or data.get("content"),
            }

        if not post.get("title") or not post.get("contentHtml"):
            print("Model response missing required fields 'title' or 'contentHtml'.")
            return None

        bundle: PostBundle = {
            "post": post,  # type: ignore
            "tags": tags,
            "authors": authors,  # type: ignore
        }
        return bundle

    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        try:
            print(f"Raw response text: {raw_text[:500] if raw_text else ''}")
        except Exception:
            pass
        return None
