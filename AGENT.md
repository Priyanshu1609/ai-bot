# AI Blog Bot - Project Knowledge Base

Project Owner: You (the user)
Last Updated: 2025-11-06

---

## Overview

This project generates high-quality, focused tech blog posts using a two-stage agentic workflow powered by LangChain and Gemini. It reads broad keywords, scouts a specific timely topic, writes a post grounded in fresh search results, and persists it to a normalized Postgres schema (Post/Tag/Author).

Key trade-off: We spend more API calls (2x Serper + 2x LLM per keyword) for a big jump in quality and specificity.

---

## Architecture (Two-stage Agent)

1. Topic Scout

- Input: Broad keyword (e.g., "latest AI developments")
- Action: Serper search → Gemini prompt selects a single specific topic
- Output: A new, concise Google search query (string)

2. Blog Writer

- Input: Specific topic query (e.g., "OpenAI's Sora model performance")
- Actions: Serper search for focused results → Gemini writes a PostBundle
- Output: Structured JSON matching Post/Tag/Author (server-side enforced)

Implementation highlights

- LangChain LCEL chains in `app/services/chains.py`
- Server-side structured output bound via Gemini `response_json_schema`
- Upserts to normalized tables in `app/db/postgres.py`

---

## Folder structure

```
.
├── AGENT.md
├── keywords.json
├── main.py
├── requirements.txt
└── app/
        ├── __init__.py
        ├── config.py
        ├── prompts.py
        ├── db/
        │   ├── __init__.py
        │   └── postgres.py
        └── services/
                ├── __init__.py
                ├── chains.py           # Topic Scout + Blog Writer chains (LangChain)
                ├── schemas.py          # Pydantic PostBundle (server-side schema)
                └── search.py           # Serper wrapper via LangChain
```

---

## Data model and structured output

We use provider-enforced structured output for predictable JSON. The Blog Writer chain binds a JSON schema generated from these Pydantic models:

```
class AuthorIn(BaseModel):
    name: str
    twitter: Optional[str]
    avatarUrl: Optional[str]

class PostIn(BaseModel):
    slug: Optional[str]
    title: str
    summary: Optional[str]
    contentHtml: str
    date: Optional[str]
    image: Optional[str]
    readingTimeMinutes: Optional[int]

class PostBundle(BaseModel):
    post: PostIn
    tags: List[str] = []
    authors: List[AuthorIn] = []
```

Gemini is instructed with `generation_config`:

- `response_mime_type: application/json`
- `response_json_schema: PostBundle.model_json_schema()`

---

## Key files

- `main.py` – Orchestrator with small helpers: loads keywords, runs Scout → Writer, persists bundle.
- `app/services/chains.py` – LCEL wiring for Topic Scout and Blog Writer; binds server-side schema.
- `app/services/search.py` – Serper search via LangChain’s `GoogleSerperAPIWrapper`.
- `app/services/schemas.py` – Pydantic models used to generate the response JSON schema.
- `app/db/postgres.py` – Upserts Post/Tag/Author (+ join tables) with a generated slug if missing.
- `app/prompts.py` – Prompt templates for Scout/Writer.
- `.github/workflows/blog-bot.yml` – GH Actions workflow (uses requirements.txt to install deps, then `python main.py`).

---

## Setup

Requirements

- Python 3.10+
- Postgres-compatible DSN
- API keys for Gemini and Serper

Environment variables

- `GEMINI_API_KEY` – Google Generative AI API key
- `SERPER_API_KEY` – Serper API key
- `DB_CONN_STRING` – Postgres connection string (supports `?schema=public`)
- `GEMINI_MODEL` – optional, defaults to `gemini-1.5-flash`

Install dependencies

- `requirements.txt` includes:
  - `langchain`
  - `langchain-google-genai`
  - `langchain-community`
  - `psycopg2-binary`

Local run (example)

1. Create/activate a venv
2. `pip install -r requirements.txt`
3. Set env vars (or add a `.env` file)
4. `python main.py`

---

## GitHub Actions

Workflow: `.github/workflows/blog-bot.yml`

- Triggers: manual `workflow_dispatch` and/or `schedule` (cron)
- Steps: checkout → setup Python → install from requirements.txt → run main.py
- Secrets: set `GEMINI_API_KEY`, `SERPER_API_KEY`, `DB_CONN_STRING` (and optional `GEMINI_MODEL`)

### Pause/Resume ("pause button")

- The workflow is gated by repository variable `BLOG_BOT_PAUSED`.
- When `BLOG_BOT_PAUSED == 'true'`, the main job is skipped and a small `paused-note` job explains why.
- To toggle:
  1. Go to Actions → "Toggle AI Blog Bot" → Run workflow
  2. Choose `pause` or `resume` and run

Files involved:

- `.github/workflows/blog-bot.yml` – uses `if: ${{ vars.BLOG_BOT_PAUSED != 'true' }}`
- `.github/workflows/toggle-blog-bot.yml` – sets the repository variable via `actions/github-script`

---

## Cost note (“Broke CTO” trade-off)

- Old: 1× Serper + 1× LLM per keyword
- New: 2× Serper + 2× LLM per keyword

Result: roughly 2× API usage, but much better post quality and topical specificity.

---

## Troubleshooting

- Empty or malformed JSON
  - We bind a JSON schema via `response_json_schema`, so structure is enforced. If failures persist, log the raw response and validate with the Pydantic models.
- DB insert errors
  - Verify `DB_CONN_STRING` and that tables exist (Post, Tag, Author, PostTag, PostAuthor). Ensure the `slug` unique index exists on Post.
- Search returns nothing
  - Check `SERPER_API_KEY` and query patterns; Topic Scout may produce a too-narrow query. Adjust the Scout prompt if needed.
- Rate limits or quota
  - Reduce keywords, cache broad search, or switch to cheaper/lower-latency models temporarily.

---

## Current ask

Keep the agent stable and improve post quality incrementally. Potential enhancements:

- Add retry/backoff around API calls
- Include source links in `contentHtml`
- Add author defaults and image generation hooks
- Add minimal unit tests for chain wiring and DB upsert helpers
