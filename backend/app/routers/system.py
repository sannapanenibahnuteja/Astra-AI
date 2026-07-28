from fastapi import APIRouter
import psutil
from datetime import datetime

router = APIRouter()


@router.get("/system")
def system_info():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "time": datetime.now().strftime("%I:%M %p"),
    }