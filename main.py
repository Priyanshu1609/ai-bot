import os
import json
import psycopg2

# LangChain components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# 1. --- Get Secrets & Initialize Components ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
DB_CONN_STRING = os.environ.get("SUPABASE_CONN_STRING")

# Initialize our LLM (Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

# Initialize our Search Tool (Serper)
search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)


# 2. --- Define Our Two Chains ---

def create_topic_scout_chain():
    """
    This chain acts as a "News Editor."
    It searches a broad topic and decides on a single, specific story to write about.
    """
    print("...Initializing Topic Scout chain...")
    
    # This prompt instructs the LLM to act as an editor
    scout_prompt_template = """
    You are an expert news editor. Your goal is to find one specific, interesting story.
    Based on the following search results for a broad topic, identify the
    SINGLE most interesting, specific, and timely news story or development.
    
    Return ONLY a new, concise Google search query for that specific story.
    Do not add any preamble, explanation, or extra text.
    
    Broad Topic Search Results:
    ---
    {search_context}
    ---
    
    New, Specific Search Query:
    """
    
    prompt = ChatPromptTemplate.from_template(scout_prompt_template)
    
    # The chain:
    # 1. Takes "search_context" as input
    # 2. Formats the prompt
    # 3. Sends it to the LLM
    # 4. Parses the string output
    chain = prompt | llm | StrOutputParser()
    return chain


def create_blog_writer_chain():
    """
    This chain acts as a "Blog Author."
    It takes a specific topic, researches it, and writes the final blog post.
    """
    print("...Initializing Blog Writer chain...")

    # This prompt instructs the LLM to write the blog post in JSON format
    writer_prompt_template = """
    You are an expert tech blogger. Your task is to write a short, insightful blog post
    (around 300 words) based on the specific topic and context provided.
    
    The blog post should be about: "{specific_topic}"
    
    Use the following recent search results as your primary context to ensure
    the post is up-to-date and factual. Synthesize them into a coherent article.
    
    SEARCH CONTEXT:
    ---
    {search_context}
    ---
    
    The output must be a single, valid JSON object with two keys: "title" and "content".
    
    Example:
    {{
      "title": "The Future of AI: New Developments",
      "content": "The world of AI is moving at breakneck speed..."
    }}
    """
    
    prompt = ChatPromptTemplate.from_template(writer_prompt_template)
    
    # The chain:
    # 1. Takes "specific_topic" and "search_context" as input
    # 2. Formats the prompt
    # 3. Sends it to the LLM
    # 4. Parses the output as JSON
    chain = prompt | llm | JsonOutputParser()
    return chain


# 3. --- Database Function (Unchanged) ---

def write_to_postgres(title, content):
    """Writes the generated blog post to the Supabase Postgres DB."""
    if not title or not content:
        print("Skipping database insert due to missing title or content.")
        return

    print(f"Writing to database: {title}")
    sql = "INSERT INTO posts (title, content) VALUES (%s, %s)"
    
    try:
        conn = psycopg2.connect(DB_CONN_STRING)
        cursor = conn.cursor()
        cursor.execute(sql, (title, content))
        conn.commit()
        cursor.close()
        conn.close()
        print("Successfully written to database.")
    except Exception as e:
        print(f"Error writing to database: {e}")


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
    
    # Create our reusable chains
    topic_scout = create_topic_scout_chain()
    blog_writer = create_blog_writer_chain()

    for broad_keyword in keywords:
        print(f"\n--- Processing Broad Keyword: {broad_keyword} ---")
        
        # --- STAGE 1: The Topic Scout ---
        print(f"Scouting for specific topics...")
        # 1. Search for the broad topic
        try:
            broad_search_results = search.run(broad_keyword)
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
            specific_search_results = search.run(specific_topic_query)
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