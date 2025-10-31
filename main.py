import json
from typing import cast

from app.services.search import get_google_search_results
from app.services.generate import generate_blog_post
from app.db.postgres import write_post_bundle


# 4. --- Main Execution ---

def load_keywords(file_path: str = "keywords.json") -> list:
    """Load a list of keywords from a JSON file.

    The file is expected to contain an object with a top-level key "keywords"
    whose value is a list of strings.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("keywords", [])
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
        return []


def process_keyword(keyword: str) -> bool:
    """Process a single keyword end-to-end: search -> generate -> persist.

    Returns True if a post was successfully written to the database; otherwise False.
    """
    print(f"\n--- Processing Keyword: {keyword} ---")

    context = get_google_search_results(keyword)
    if not context:
        print("Skipping blog generation due to failed search.")
        return False

    bundle = generate_blog_post(context, keyword)
    if not bundle:
        print("Skipping database write due to failed blog generation.")
        return False

    if write_post_bundle(cast(dict, bundle)):
        print("------------------------------------------")
        return True
    else:
        return False
    


def main() -> None:
    """Entrypoint that orchestrates reading keywords and processing them."""
    keywords = load_keywords("keywords.json")
    if not keywords:
        print("No keywords found. Ensure 'keywords.json' contains a 'keywords' array.")
        return

    print(f"Found {len(keywords)} keywords. Starting workflow...")

    successes = 0
    for kw in keywords:
        try:
            if process_keyword(kw):
                successes += 1
        except Exception as e:
            # Never let one keyword kill the whole batch
            print(f"Unexpected error while processing '{kw}': {e}")

    print(f"Completed. Successfully processed {successes}/{len(keywords)} keywords.")


if __name__ == "__main__":
    main()