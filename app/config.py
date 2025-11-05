"""Application configuration and environment variables.

Loads env vars (optionally from .env when available) and exposes constants.
We avoid importing heavy SDKs here to keep dependencies minimal in the
LangChain-based architecture.
"""

import os

try:
	from dotenv import load_dotenv  # type: ignore
except Exception:
	# Graceful fallback if python-dotenv isn't installed
	def load_dotenv() -> None:  # type: ignore
		return None

# Load from .env when running locally. In CI, environment variables should be set directly.
load_dotenv()

# --- Environment variables ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
# Support both names for compatibility with previous versions
DB_CONN_STRING = os.environ.get("DB_CONN_STRING")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
