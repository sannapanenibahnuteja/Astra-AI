from fastapi import APIRouter

from app.services.monitor_service import (
    get_system_status
)


router = APIRouter(
    prefix="/monitor",
    tags=["monitor"]
)



@router.get("/")
def system_monitor():

    return get_system_status()