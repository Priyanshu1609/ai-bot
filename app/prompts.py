"""Prompt templates used by the application."""

def blog_post_prompt(search_context: str, keyword: str) -> str:
    """Return a JSON-oriented prompt instructing the model to produce title and content.

    The model is asked to return a JSON object with keys "title" and "content".
    """
    return f"""
You are an expert tech blogger.
Your task is to write a short, insightful blog post (around 300 words).
The blog post should be about: "{keyword}".

Use the following recent search results as your primary context to ensure the post is up-to-date and factual.
Do NOT just list the search results. Synthesize them into a coherent article.

SEARCH CONTEXT:
---
{search_context}
---

The output must be a JSON object with two keys: "title" and "content".

Example:
{{
  "title": "The Future of AI: New Developments",
  "content": "The world of AI is moving at breakneck speed..."
}}

Now, write the blog post.
"""
