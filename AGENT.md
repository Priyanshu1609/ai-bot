# AI Blog Bot - Project Knowledge Base

**Project Owner:** You (the user)
**Last Updated:** 2025-10-31

---

## 1. Project Core ("The Aim")

The primary objective of this project is to create a **fully autonomous, zero-cost AI agentic workflow** for content creation.

**Core Constraint:** The entire system **must run for $0** by exclusively leveraging the "always free" tiers of various cloud and API services.

**The Workflow:**

1.  **Input:** Read a list of keywords from a JSON file (e.g., "latest AI developments").
2.  **Research:** For each keyword, perform a Google search to find the latest, relevant news and blogs.
3.  **Create:** Feed the search results as context to an LLM (Gemini) and prompt it to write an original, high-quality blog post.
4.  **Store:** Save the final blog post (title and content) to a cloud-hosted PostgreSQL database.

---

## 2. Current State ("Progress")

We have successfully implemented **Path 1** of this project.

**"Path 1" is a serverless script** that runs on a schedule. It is _not_ a persistent agent, but a triggered, stateless workflow.

**Current Status: Implemented & Functional.**

- The system can be triggered manually or run on a `cron` schedule.
- It successfully reads keywords, searches, generates content, and saves to the database.

---

## 3. System Architecture (Path 1)

This implementation is a Python script orchestrated by GitHub Actions.

- **Runner:** **GitHub Actions** (using `schedule` and `workflow_dispatch` triggers).
- **Code:** **Python 3.10+** with a small modular package and a thin `main.py` entrypoint.
- **Search API:** **Serper** (free tier, via `requests`).
- **LLM API:** **Google Gemini** (free tier, via the official `google-genai` SDK).
- **Database:** **PrismaDB** (free tier Postgres, via `psycopg2-binary`).
- **Secrets:** All API keys and connection strings are stored as **GitHub Actions Secrets**.

### Key Files in Repository

1.  **`.github/workflows/blog-bot.yml`**:

    - The orchestrator.
    - Sets up the Python environment.
    - Installs dependencies from `requirements.txt`.
    - Injects secrets as environment variables.
    - Runs `python main.py`.

2.  **`main.py`**:

    - The thin entrypoint that orchestrates the workflow.
    - Loads keywords and calls service-layer functions for search, generation, and persistence.

3.  **`ai_agent_gactions/`** (package):

    - `config.py` – loads environment (supports `.env`), exposes constants and a shared Gemini client.
    - `prompts.py` – prompt templates (e.g., blog post prompt).
    - `services/search.py` – Serper search integration.
    - `services/generate.py` – Gemini content generation.
    - `db/postgres.py` – Postgres insert utility.

4.  **`requirements.txt`**:

    - `requests` (for Serper and Gemini APIs)
    - `psycopg2-binary` (for Postgres connection)

5.  **`keywords.json`**:

    - A simple JSON file containing a list of keywords for the bot to process.

6.  **`AGENT.md`**:
    - This file. The project's "memory."

---

## 4. Next Steps ("The Ask")

This section defines the current task. When providing this file to an AI, the "Ask" is the primary problem to be solved.

**Current Ask: [Your next question or goal goes here]**

_Example Asks:_

- "My `main.py` script is failing with a 500 error from Gemini. Analyze the `generate_blog_post` function and help me debug it."
- "The blog posts are too generic. Help me refine the prompt in `main.py` to produce more insightful, opinionated articles."
- "I want to move to 'Path 2'. Help me refactor this Python logic into a visual n8n workflow."
- "How can I add error handling to `main.py` so that if one keyword fails, the whole script doesn't stop?"
- "Help me add a new step to the Python script that also generates a DALL-E image for the blog post and saves the URL to the database."
