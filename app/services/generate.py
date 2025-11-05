"""Deprecated legacy generator (pre-LangChain).

This module is kept as a no-op shim to avoid import errors in older references.
All generation is now handled via LangChain chains in app/services/chains.py.
"""

from __future__ import annotations

from typing import Optional, TypedDict, List


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


def generate_blog_post(*args, **kwargs) -> Optional[PostBundle]:  # pragma: no cover
    """Legacy API stub maintained for backward-compat.

    This function is deprecated. Use the LangChain-based writer chain instead.
    Returns None to indicate no generation was performed.
    """
    print("[deprecated] app.services.generate.generate_blog_post is no longer used."
          " Use the LangChain Blog Writer chain instead.")
    return None
