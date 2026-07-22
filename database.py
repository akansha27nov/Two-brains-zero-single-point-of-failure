import sqlite3
from datetime import datetime

class NewsDatabase:
    """Handles SQLite persistence and response caching for processed articles."""
    
    def __init__(self, db_path="news_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
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

    def get_cached_article(self, url: str):
        """Retrieve a processed article from cache by URL."""
        if not url:
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

    def save_article(self, article_data: dict):
        """Save or update a processed article in the local database."""
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