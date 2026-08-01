from .task_database import get_connection


def create_task(title, priority="normal", due_date=None):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (
            title,
            priority,
            due_date
        )
        VALUES
        (?, ?, ?)
        """,
        (
            title,
            priority,
            due_date
        )
    )

    connection.commit()
    connection.close()


def get_tasks():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        ORDER BY completed ASC,
                 created_at DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def complete_task(task_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed=1
        WHERE id=?
        """,
        (task_id,)
    )

    connection.commit()

    connection.close()


def delete_task(task_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id=?
        """,
        (task_id,)
    )

    connection.commit()

    connection.close()