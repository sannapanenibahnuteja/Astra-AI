from fastapi import APIRouter, HTTPException

from .task_service import (
    create_task,
    get_tasks,
    complete_task,
    delete_task,
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.get("/")
def tasks():

    return get_tasks()


@router.post("/")
def create(data: dict):

    print("POST DATA:", data)

    title = data.get("title")

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Task title is required."
        )

    task = create_task(
        title,
        data.get("priority", "normal"),
        data.get("due_date"),
    )

    return {
        "success": True,
        "task": task,
    }


@router.patch("/{task_id}")
def complete(task_id: int):

    complete_task(task_id)

    return {
        "success": True,
    }


@router.delete("/{task_id}")
def remove(task_id: int):

    delete_task(task_id)

    return {
        "success": True,
    }