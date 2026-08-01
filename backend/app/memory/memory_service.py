from .database import get_connection



def save_memory(key, value):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO memories
        (key, value)

        VALUES (?, ?)
        """,
        (
            key,
            value
        )
    )


    connection.commit()

    connection.close()


    return {
        "key": key,
        "value": value
    }




def get_memories():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT key, value
        FROM memories
        """
    )


    rows = cursor.fetchall()


    connection.close()


    return [

        {
            "key": row["key"],
            "value": row["value"]
        }

        for row in rows

    ]




def search_memory(query):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT key, value
        FROM memories
        WHERE key LIKE ?
        OR value LIKE ?
        """,
        (
            f"%{query}%",
            f"%{query}%"
        )
    )


    rows = cursor.fetchall()


    connection.close()



    return [

        {
            "key": row["key"],
            "value": row["value"]
        }

        for row in rows

    ]




def delete_memory(key):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM memories
        WHERE key = ?
        """,
        (key,)
    )


    connection.commit()

    connection.close()

def get_recent_memories(limit=5):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, key, value
        FROM memories
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) as total FROM memories"
    )

    total = cursor.fetchone()["total"]

    connection.close()

    return {

        "count": total,

        "recent":[

            {

                "id":row["id"],

                "key":row["key"],

                "value":row["value"]

            }

            for row in rows

        ]

    }

def clear_memories():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        """
    )

    connection.commit()

    connection.close()

    return {
        "success": True
    }