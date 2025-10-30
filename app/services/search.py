"""Search service using Serper API (Google Search)."""

import requests

from ..config import SERPER_API_KEY


def get_google_search_results(query: str) -> str | None:
    """Hits the Serper API for search results and returns synthesized context.

    Returns a string with top results' titles/snippets/links or None on failure.
    """
    print(f"Searching for: {query}")
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        if not SERPER_API_KEY:
            print("Missing SERPER_API_KEY. Ensure it's set in your environment or .env file.")
            return None

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        search_data = response.json()

        snippets = [
            f"Title: {item.get('title', '')}\nSnippet: {item.get('snippet', '')}\nURL: {item.get('link', '')}"
            for item in search_data.get("organic", [])[:5]
        ]
        return "\n\n".join(snippets)
    except Exception as e:
        try:
            print(f"Error in Serper search: {e}. Response: {response.text}")
        except Exception:
            print(f"Error in Serper search: {e}")
        return None
