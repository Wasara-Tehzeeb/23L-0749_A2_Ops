import os
import sqlite3
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

DB_PATH = Path(os.getenv("DATABASE_PATH", "visionguard.db"))

if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH


def init_db():
    if DATABASE_URL:
        import psycopg

        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    filename TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    model_name TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    model_name TEXT,
                    timestamp TEXT NOT NULL
                )
            """)


def save_prediction(filename, prediction, confidence, model_name):
    values = (
        filename,
        prediction,
        confidence,
        model_name,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    if DATABASE_URL:
        import psycopg

        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute("""
                INSERT INTO predictions
                (filename, prediction, confidence, model_name, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, values)
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO predictions
                (filename, prediction, confidence, model_name, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, values)


def get_predictions():
    if DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(
            DATABASE_URL, row_factory=dict_row
        ) as conn:
            records = conn.execute(
                "SELECT * FROM predictions ORDER BY id DESC"
            ).fetchall()

        return records

    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            records = conn.execute(
                "SELECT * FROM predictions ORDER BY id DESC"
            ).fetchall()

        return [dict(record) for record in records]
