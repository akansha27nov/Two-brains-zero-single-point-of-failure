# SQLite cache for processed news articles.
# Stores summaries and sentiment by article URL.
# Falls back to temp storage if the workspace is read-only.
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

class NewsDatabase:
    """Handles SQLite persistence and response caching for processed articles."""
    
    # Set the database path and initialize the cache schema.
    def __init__(self, db_path="news_cache.db"):
        self.db_path = db_path
        self.enabled = True
        self._init_db()

    # Create the schema, with a temp-directory fallback if needed.
    def _init_db(self):
        try:
            self._create_schema(self.db_path)
        except sqlite3.OperationalError:
            # Fall back to a writable temp location when the working directory is read-only.
            fallback_path = Path(tempfile.gettempdir()) / "news_cache.db"
            if str(fallback_path) != self.db_path:
                try:
                    self.db_path = str(fallback_path)
                    self._create_schema(self.db_path)
                    return
                except sqlite3.OperationalError:
                    pass

            self.enabled = False

    # Create the articles table if it does not already exist.
    def _create_schema(self, path):
        with sqlite3.connect(path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    summary TEXT,
                    sentiment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    # Read a cached article by URL when caching is enabled.
    def get_cached_article(self, url: str):
        """Retrieve a processed article from cache by URL."""
        if not url or not self.enabled:
            return None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, summary, sentiment FROM articles WHERE url = ?", (url,))
            row = cursor.fetchone()
            if row:
                return {
                    "title": row[0],
                    "summary": row[1],
                    "sentiment": row[2],
                    "url": url,
                    "cached": True
                }
        return None

    # Save a processed article so future runs can reuse it.
    def save_article(self, article_data: dict):
        """Save or update a processed article in the local database."""
        if not self.enabled:
            return

        url = article_data.get("url")
        if not url:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO articles (url, title, summary, sentiment)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    summary = excluded.summary,
                    sentiment = excluded.sentiment
            """, (
                url,
                article_data.get("title"),
                article_data.get("summary"),
                article_data.get("sentiment")
            ))
            conn.commit()
