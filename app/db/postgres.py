"""Postgres persistence utilities (PrismaDB Postgres).

Implements inserts/upserts for the Prisma-style schema:
Post, Tag, Author, PostTag, PostAuthor.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import uuid
from urllib.parse import urlparse, urlunparse, parse_qs

import psycopg2
from psycopg2.extensions import connection as PGConnection

from ..config import DB_CONN_STRING


def _normalize_dsn(dsn: str) -> tuple[str, Optional[str]]:
    """Remove unsupported query params from DSN and extract schema if present.

    PrismaDB often provides a DSN like:
      postgresql://user:pass@host:5432/db?schema=public
    psycopg2 may reject unknown params like `schema`. We strip the query
    and return (dsn_without_query, schema_name or None).
    """
    try:
        parts = urlparse(dsn)
        schema = None
        if parts.query:
            qs = parse_qs(parts.query)
            schema = (qs.get("schema") or [None])[0]
        dsn_no_query = urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, "", parts.fragment))
        return dsn_no_query, schema
    except Exception:
        return dsn, None


def _connect() -> PGConnection:
    if not DB_CONN_STRING:
        raise ValueError("DB_CONN_STRING is not set in the environment")
    dsn, schema = _normalize_dsn(DB_CONN_STRING)
    conn = psycopg2.connect(dsn)
    if schema:
        with conn.cursor() as cur:
            try:
                cur.execute("SET search_path TO %s", (schema,))
                conn.commit()
            except Exception:
                # Don't fail connection if setting search_path fails
                conn.rollback()
    return conn


def _ensure_slug(text: str) -> str:
    """Create a simple kebab-case slug from a title."""
    text = text.lower().strip()
    # Replace non-alphanumeric with hyphen
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def write_post_bundle(bundle: dict) -> bool:
    """Insert/update a Post with related Tags and Authors using upserts.

    bundle shape:
      { "post": {...}, "tags": [str], "authors": [{"name":..., ...}] }
    Returns True on success, False otherwise.
    """
    post = (bundle or {}).get("post") or {}
    tags: List[str] = (bundle or {}).get("tags") or []
    authors: List[Dict[str, Any]] = (bundle or {}).get("authors") or []

    title = post.get("title")
    content_html = post.get("contentHtml")
    if not title or not content_html:
        print("Skipping database insert: missing required fields 'title' or 'contentHtml'.")
        return False

    slug = post.get("slug") or _ensure_slug(title)
    summary = post.get("summary")
    date = post.get("date")
    image = post.get("image")
    reading_time = post.get("readingTimeMinutes")

    try:
        conn = _connect()
        cur = conn.cursor()
        # Upsert Post (use unique slug). Provide explicit UUID to avoid NULL id if DB has no default.
        post_uuid = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO "Post" (id, slug, title, summary, "contentHtml", date, image, "readingTimeMinutes", "updatedAt")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (slug) DO UPDATE SET
                title = EXCLUDED.title,
                summary = EXCLUDED.summary,
                "contentHtml" = EXCLUDED."contentHtml",
                date = EXCLUDED.date,
                image = EXCLUDED.image,
                "readingTimeMinutes" = EXCLUDED."readingTimeMinutes",
                "updatedAt" = NOW()
            RETURNING id
            """,
            (post_uuid, slug, title, summary, content_html, date, image, reading_time),
        )
        row = cur.fetchone()
        if not row:
            raise RuntimeError("Failed to insert or fetch Post id")
        post_id = row[0]

        # Upsert Tags and link
        tag_ids: List[str] = []
        for t in tags:
            tname = (t or "").strip()
            if not tname:
                continue
            # Provide explicit UUID for Tag as well to avoid NULL id on DBs without default
            tag_uuid = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO "Tag" (id, name) VALUES (%s, %s)
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
                """,
                (tag_uuid, tname),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("Failed to insert or fetch Tag id")
            tag_id = row[0]
            tag_ids.append(tag_id)
            cur.execute(
                """
                INSERT INTO "PostTag" ("postId", "tagId") VALUES (%s, %s)
                ON CONFLICT ("postId", "tagId") DO NOTHING
                """,
                (post_id, tag_id),
            )

        # Upsert Authors and link
        for a in authors:
            name = (a.get("name") or "").strip()
            if not name:
                continue
            twitter = a.get("twitter")
            avatar = a.get("avatarUrl")
            # Provide explicit UUID for Author as well
            author_uuid = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO "Author" (id, name, twitter, "avatarUrl") VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    twitter = COALESCE(EXCLUDED.twitter, "Author".twitter),
                    "avatarUrl" = COALESCE(EXCLUDED."avatarUrl", "Author"."avatarUrl")
                RETURNING id
                """,
                (author_uuid, name, twitter, avatar),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("Failed to insert or fetch Author id")
            author_id = row[0]
            cur.execute(
                """
                INSERT INTO "PostAuthor" ("postId", "authorId") VALUES (%s, %s)
                ON CONFLICT ("postId", "authorId") DO NOTHING
                """,
                (post_id, author_id),
            )

        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully written to database: {title}")
        return True
    except Exception as e:
        print(f"Error writing to database: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        return False


# Backward-compatible minimal insert (older table 'posts')
def write_to_postgres(title: str | None, content: str | None) -> None:
    if not title or not content:
        print("Skipping database insert due to missing title or content.")
        return
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)", (title, content))
        conn.commit()
        cur.close()
        conn.close()
        print("Successfully written to database.")
    except Exception as e:
        print(f"Error writing to database (legacy 'posts' table): {e}")
