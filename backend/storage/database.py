import os
import sqlite3
import json
from typing import List, Dict, Any, Optional
from core.config import settings
from core.logging_config import logger

def get_db_connection() -> sqlite3.Connection:
    # Ensure the parent directory for SQLite file exists
    db_path = settings.sqlite_db_path
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(db_path)
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    logger.info("Initializing SQLite database schema...")
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                key_rights TEXT,
                penalties TEXT,
                card_description TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e
    finally:
        conn.close()

def clear_db():
    logger.info("Clearing SQLite topics table...")
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM topics")
        conn.commit()
        logger.info("Database records cleared successfully.")
    except Exception as e:
        logger.error(f"Failed to clear database records: {e}")
    finally:
        conn.close()

def save_topic_metadata(
    topic_id: str,
    title: str,
    summary: str,
    key_rights: List[str],
    penalties: List[str],
    card_description: str,
    source_url: str
):
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO topics (id, title, summary, key_rights, penalties, card_description, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                title,
                summary,
                json.dumps(key_rights),
                json.dumps(penalties),
                card_description,
                source_url
            )
        )
        conn.commit()
        logger.info(f"Metadata for topic '{topic_id}' cached in database.")
    except Exception as e:
        logger.error(f"Failed to save metadata for topic '{topic_id}': {e}")
        raise e
    finally:
        conn.close()

def get_topic_metadata(topic_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            # Deserialize JSON columns
            data["key_rights"] = json.loads(data["key_rights"]) if data.get("key_rights") else []
            data["penalties"] = json.loads(data["penalties"]) if data.get("penalties") else []
            return data
        return None
    finally:
        conn.close()

def get_all_topics() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, card_description, source_url FROM topics")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
