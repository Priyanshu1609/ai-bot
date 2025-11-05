"""Search service using Serper API (Google Search) via LangChain wrapper."""

from __future__ import annotations

from typing import Optional

from langchain_community.utilities import GoogleSerperAPIWrapper

from ..config import SERPER_API_KEY


def _serper() -> GoogleSerperAPIWrapper:
    return GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)


def get_google_search_results(query: str) -> Optional[str]:
    """Run a Serper search and return a synthesized string context.

    Uses LangChain's GoogleSerperAPIWrapper to format results.
    Returns None on failure.
    """
    print(f"Searching for: {query}")
    try:
        if not SERPER_API_KEY:
            print("Missing SERPER_API_KEY. Ensure it's set in your environment or .env file.")
            return None

        res = _serper().run(query)
        return res
    except Exception as e:
        print(f"Error in Serper search: {e}")
        return None
