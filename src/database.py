import sqlite3
import os
from contextlib import contextmanager

# Move DB to a data folder or keep in root relative to the project
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jobs.db')

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
