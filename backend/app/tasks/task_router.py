from fastapi import APIRouter

from .task_service import *

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.get("/")
def tasks():

    return get_tasks()


@router.post("/")
def create(data: dict):

    create_task(
        data["title"],
        data.get("priority", "normal"),
        data.get("due_date")
    )

    return {
        "success": True
    }


@router.patch("/{task_id}")
def complete(task_id: int):

    complete_task(task_id)

    return {
        "success": True
    }


@router.delete("/{task_id}")
def remove(task_id: int):

    delete_task(task_id)

    return {
        "success": True
    }