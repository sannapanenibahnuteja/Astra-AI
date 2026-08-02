from .task_database import get_connection


def create_task(title, priority="normal", due_date=None):

    print("CREATING TASK:", title)

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
            due_date,
        ),
    )

    connection.commit()

    task_id = cursor.lastrowid

    print("INSERTED ID:", task_id)

    connection.close()

    return {
        "id": task_id,
        "title": title,
        "priority": priority,
        "completed": 0,
        "due_date": due_date,
    }


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

    tasks = [dict(row) for row in rows]

    print("TASKS:", tasks)

    return tasks


def complete_task(task_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        """,
        (task_id,),
    )

    connection.commit()

    connection.close()


def delete_task(task_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,),
    )

    connection.commit()

    connection.close()