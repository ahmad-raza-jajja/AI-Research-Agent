# database.py
import sqlite3
import os
from datetime import datetime

DB_NAME = "research_data.db"

def get_db_connection():
    """Create and return a connection to the database"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables if not exists"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        results_count INTEGER,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER,
        title TEXT,
        url TEXT,
        text TEXT,
        word_count INTEGER,
        scraped_at TEXT,
        FOREIGN KEY (search_id) REFERENCES searches (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER,
        summary TEXT,
        created_at TEXT,
        FOREIGN KEY (search_id) REFERENCES searches (id)
    )
    """)

    conn.commit()
    conn.close()

def save_search(query, results_count):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO searches (query, results_count, created_at) VALUES (?, ?, ?)",
        (query, results_count, datetime.now().isoformat())
    )
    search_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return search_id

def save_scraped_content(search_id, title, url, text, word_count):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO scraped_content 
        (search_id, title, url, text, word_count, scraped_at) 
        VALUES (?, ?, ?, ?, ?, ?)""",
        (search_id, title, url, text, word_count, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def save_summary(search_id, summary):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO summaries (search_id, summary, created_at) VALUES (?, ?, ?)",
        (search_id, summary, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_recent_searches(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM searches ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    searches = cursor.fetchall()
    conn.close()
    return searches

def get_scraped_content_by_search(search_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM scraped_content WHERE search_id = ?",
        (search_id,)
    )
    contents = cursor.fetchall()
    conn.close()
    return contents

def get_summary_by_search(search_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT summary FROM summaries WHERE search_id = ? ORDER BY created_at DESC LIMIT 1",
        (search_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row["summary"] if row else None

# Initialize database on first run
if not os.path.exists(DB_NAME):
    init_db()
