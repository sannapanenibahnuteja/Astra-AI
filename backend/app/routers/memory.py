from fastapi import APIRouter

from app.memory.memory_service import (
    save_memory,
    search_memory,
    get_recent_memories,
    clear_memories
    
)


router = APIRouter(
    prefix="/memory",
    tags=["memory"]
)



@router.post("/save")
def create_memory(data: dict):

    content = data.get(
        "content",
        ""
    )


    if not content:

        return {

            "success": False,

            "message": "No memory provided"

        }



    result = save_memory(

        "general",

        content

    )



    return {

        "success": True,

        "memory": result

    }




@router.get("/search")
def get_memory(query: str):


    result = search_memory(
        query
    )


    return {

        "results": result

    }

@router.get("/recent")
def recent_memories():

    return get_recent_memories()

@router.get("/clear")
def clear_all_memories():

    return clear_memories()