"""Application configuration and SDK client initialization.

Loads environment variables (supports .env for local dev) and exposes
constants and shared clients to be used across the app.
"""

import os
from dotenv import load_dotenv
from google import genai

# Load from .env when running locally. In CI, environment variables should be set directly.
load_dotenv()

# --- Environment variables ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
DB_CONN_STRING = os.environ.get("SUPABASE_CONN_STRING")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# --- SDK Clients ---
# The official Google Generative AI SDK reads the API key from environment.
gemini_client = genai.Client()
