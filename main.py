import json

from app.services.search import get_google_search_results
from app.services.chains import create_topic_scout_chain, create_blog_writer_chain
from app.db.postgres import write_to_postgres


# 4. --- Main Execution (Orchestrator) ---

def main():
    try:
        with open('keywords.json', 'r') as f:
            data = json.load(f)
            keywords = data.get("keywords", [])
    except Exception as e:
        print(f"Could not read keywords.json: {e}")
        return

    print(f"Found {len(keywords)} broad keywords. Initializing chains...")

    # Create our reusable chains via services
    topic_scout = create_topic_scout_chain()
    blog_writer = create_blog_writer_chain()

    for broad_keyword in keywords:
        print(f"\n--- Processing Broad Keyword: {broad_keyword} ---")
        
        # --- STAGE 1: The Topic Scout ---
        print(f"Scouting for specific topics...")
        # 1. Search for the broad topic
        try:
            broad_search_results = get_google_search_results(broad_keyword)
            if not broad_search_results:
                raise RuntimeError("No broad search results returned")
            print(f"Broad search context (first 100 chars): {broad_search_results[:100]}...")
            
            # 2. Invoke the "Scout" chain to decide on a specific topic
            specific_topic_query = topic_scout.invoke({
                "search_context": broad_search_results
            })
            print(f"Scout decided on new topic: {specific_topic_query}")
        except Exception as e:
            print(f"Error in Topic Scout stage: {e}")
            continue # Skip to the next keyword

        # --- STAGE 2: The Blog Writer ---
        print(f"Researching and writing blog for: {specific_topic_query}")
        try:
            # 3. Search for the *new, specific* topic
            specific_search_results = get_google_search_results(specific_topic_query)
            if not specific_search_results:
                raise RuntimeError("No specific search results returned")
            print(f"Specific search context (first 100 chars): {specific_search_results[:100]}...")

            # 4. Invoke the "Writer" chain to generate the blog post
            blog_post_json = blog_writer.invoke({
                "specific_topic": specific_topic_query,
                "search_context": specific_search_results
            })
            
            # 5. Write the result to the database
            write_to_postgres(
                blog_post_json.get("title"),
                blog_post_json.get("content")
            )
        except Exception as e:
            print(f"Error in Blog Writer stage: {e}")
            continue # Skip to the next keyword
            
        print("------------------------------------------")


if __name__ == "__main__":
    main()