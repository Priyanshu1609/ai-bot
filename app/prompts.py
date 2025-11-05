"""Prompt templates used by the application.

We expose simple helpers that return template strings for LangChain's
ChatPromptTemplate.from_template, keeping content concerns separate
from chain wiring.
"""


def topic_scout_template() -> str:
    """Template for the "Topic Scout" editor step.

    Variables: {search_context}
    """
    return (
        """
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
    ).strip()


def blog_writer_template() -> str:
    """Template for the "Blog Writer" authoring step.

        Variables: {specific_topic}, {search_context}
        The model will output a structured JSON object (server-enforced) matching:
        {
            "post": {
                "slug": string | null,
                "title": string,
                "summary": string | null,
                "contentHtml": string,
                "date": string | null,
                "image": string | null,
                "readingTimeMinutes": integer | null
            },
            "tags": string[],
            "authors": [{ "name": string, "twitter"?: string, "avatarUrl"?: string }]
        }
    """
    return (
        """
You are an expert tech blogger. Your task is to write a short, insightful blog post
(around 300 words) based on the specific topic and context provided.

The blog post should be about: "{specific_topic}"

Use the following recent search results as your primary context to ensure
the post is up-to-date and factual. Synthesize them into a coherent article.

SEARCH CONTEXT:
---
{search_context}
---

Write a cohesive post in semantic HTML under post.contentHtml. Include a clear title under post.title,
and add 3–6 relevant tags. If an author is known, include authors with name and any metadata available.
Return only the JSON object.
"""
    ).strip()