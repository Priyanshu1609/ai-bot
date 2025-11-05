"""LangChain-based chains wiring: Topic Scout and Blog Writer.

Uses Gemini via langchain-google-genai and Serper for search via
langchain-community utilities.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from ..config import GEMINI_API_KEY, GEMINI_MODEL
from ..prompts import topic_scout_template, blog_writer_template
from .schemas import PostBundle


def _get_llm() -> ChatGoogleGenerativeAI:
    """Return a configured Gemini chat model for LangChain.

    Falls back to a reasonable default model name if not provided.
    """
    model_name = GEMINI_MODEL or "gemini-1.5-flash"
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=GEMINI_API_KEY)


def create_topic_scout_chain():
    """Create the Topic Scout chain: prompt -> LLM -> string output."""
    prompt = ChatPromptTemplate.from_template(topic_scout_template())
    llm = _get_llm()
    return prompt | llm | StrOutputParser()


def create_blog_writer_chain():
    """Create the Blog Writer chain: prompt -> LLM -> JSON dict output."""
    prompt = ChatPromptTemplate.from_template(blog_writer_template())
    llm = _get_llm()
    # Bind server-enforced structured output using Pydantic JSON schema
    schema = PostBundle.model_json_schema()
    llm_json = llm.bind(
        generation_config={
            "response_mime_type": "application/json",
            "response_json_schema": schema,
        }
    )
    return prompt | llm_json | JsonOutputParser()
