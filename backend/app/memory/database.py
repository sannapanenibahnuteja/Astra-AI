import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "astra_memory.db"



def get_connection():

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection



def init_database():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            key TEXT NOT NULL,

            value TEXT NOT NULL

        )
        """
    )


    connection.commit()

    connection.close()