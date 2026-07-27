"""
Astra Backend
"""

from fastapi import FastAPI

from config import APP_NAME, APP_VERSION

from core.engine import AstraAssistant
from core.memory import MemoryManager
from core.skills import SkillManager
from core.router import CommandRouter

assistant = AstraAssistant()
memory = MemoryManager()
skills = SkillManager()
router = CommandRouter()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)


@app.get("/")
def home():

    return {

        "message": "Welcome to Astra",

        "assistant": assistant.get_info()

    }


@app.get("/assistant")
def assistant_info():

    return assistant.get_info()


@app.get("/memory")
def memory_info():

    return memory.all()


@app.post("/remember/{key}/{value}")
def remember(key: str, value: str):

    memory.remember(key, value)

    return {

        "saved": True

    }


@app.get("/recall/{key}")
def recall(key: str):

    return {

        "value": memory.recall(key)

    }


@app.get("/skills")
def list_skills():

    return skills.list()


@app.get("/skills/{name}")
def execute_skill(name: str):

    return skills.execute(name)

@app.get("/command/{text}")
def command(text: str):

    return router.execute(text)


@app.get("/health")
def health():

    return {

        "status": "healthy"

    }