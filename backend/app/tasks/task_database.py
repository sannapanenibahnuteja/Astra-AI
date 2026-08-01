import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "astra_tasks.db"


def get_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            completed INTEGER DEFAULT 0,

            priority TEXT DEFAULT 'normal',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            due_date TEXT
        )
        """
    )

    connection.commit()
    connection.close()