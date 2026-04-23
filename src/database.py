import sqlite3
import os
from contextlib import contextmanager

# Database path - using a dedicated folder for Docker volumes
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'jobs.db')

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seen_jobs (
                url TEXT PRIMARY KEY,
                title TEXT,
                platform TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def is_job_seen(url):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM seen_jobs WHERE url = ?', (url,))
        result = cursor.fetchone()
        return result is not None

def mark_job_seen(url, title, platform):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO seen_jobs (url, title, platform) VALUES (?, ?, ?)',
                (url, title, platform)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Already exists

def get_jobs(platform=None, min_rank=0, limit=100):
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM seen_jobs WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
