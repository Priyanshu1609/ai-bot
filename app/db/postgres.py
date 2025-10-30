"""Postgres persistence utilities (Supabase Postgres)."""

import psycopg2

from ..config import DB_CONN_STRING


def write_to_postgres(title: str | None, content: str | None) -> None:
    """Writes the generated blog post to the database, if both fields are present."""
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
