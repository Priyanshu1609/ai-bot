import json
from typing import List, Optional

from app.services.search import get_google_search_results
from app.services.chains import create_topic_scout_chain, create_blog_writer_chain
from app.db.postgres import write_to_postgres


# 4. --- Main Execution (Orchestrator) ---

def load_keywords(path: str = "keywords.json") -> List[str]:
    """Load the list of broad keywords from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("keywords", [])
    except Exception as e:
        print(f"Could not read {path}: {e}")
        return []


def scout_specific_query(broad_keyword, topic_scout) -> Optional[str]:
    """Run the Topic Scout stage: search broadly, then pick a specific query."""
    print(f"\n--- Processing Broad Keyword: {broad_keyword} ---")
    print("Scouting for specific topics…")

    broad_search_results = get_google_search_results(broad_keyword)
    if not broad_search_results:
        print("No broad search results returned; skipping.")
        return None
    print(f"Broad search context (first 100 chars): {broad_search_results[:100]}...")

    try:
        specific_topic_query = topic_scout.invoke({"search_context": broad_search_results})
        if not specific_topic_query:
            print("Scout produced empty topic; skipping.")
            return None
        print(f"Scout decided on new topic: {specific_topic_query}")
        return str(specific_topic_query).strip()
    except Exception as e:
        print(f"Error invoking Topic Scout: {e}")
        return None


def write_blog_for_topic(specific_topic_query: str, blog_writer) -> bool:
    """Run the Blog Writer stage: focused search, then generate and persist."""
    print(f"Researching and writing blog for: {specific_topic_query}")

    specific_search_results = get_google_search_results(specific_topic_query)
    if not specific_search_results:
        print("No specific search results returned; skipping.")
        return False
    print(f"Specific search context (first 100 chars): {specific_search_results[:100]}...")

    try:
        blog_post_json = blog_writer.invoke({
            "specific_topic": specific_topic_query,
            "search_context": specific_search_results,
        })
        title = (blog_post_json or {}).get("title")
        content = (blog_post_json or {}).get("content")
        write_to_postgres(title, content)
        print("------------------------------------------")
        return bool(title and content)
    except Exception as e:
        print(f"Error invoking Blog Writer: {e}")
        return False


def build_chains():
    """Create and return the reusable chains for the run."""
    return create_topic_scout_chain(), create_blog_writer_chain()


def main():
    keywords = load_keywords()
    if not keywords:
        print("No keywords found. Ensure 'keywords.json' contains a 'keywords' array.")
        return

    print(f"Found {len(keywords)} broad keywords. Initializing chains…")
    topic_scout, blog_writer = build_chains()

    successes = 0
    for kw in keywords:
        specific = scout_specific_query(kw, topic_scout)
        if not specific:
            continue
        if write_blog_for_topic(specific, blog_writer):
            successes += 1

    print(f"Completed. Successfully processed {successes}/{len(keywords)} keywords.")


if __name__ == "__main__":
    main()