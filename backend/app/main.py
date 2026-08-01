from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.chat import router as chat_router
from app.routers.browser import router as browser_router
from app.routers.system import router as system_router
from app.routers.stream import router as stream_router
from app.routers.debug import router as debug_router
from app.routers.monitor import router as monitor_router
from app.routers.commands import router as commands_router
from app.routers.memory import router as memory_router
from app.tasks.task_router import router as task_router


from app.memory.database import (
    init_database as init_memory_database
)

from app.tasks.task_database import (
    init_database as init_task_database
)


app = FastAPI(
    title="Astra API",
    version="1.0.0",
)


# Initialize databases
init_memory_database()
init_task_database()



app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)



# Routers

app.include_router(chat_router)

app.include_router(browser_router)

app.include_router(system_router)

app.include_router(stream_router)

app.include_router(debug_router)

app.include_router(monitor_router)

app.include_router(commands_router)

app.include_router(memory_router)

app.include_router(task_router)



@app.get("/")
def root():

    return {

        "status": "online",

        "assistant": "Astra",

        "version": "1.0.0",

    }