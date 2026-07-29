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