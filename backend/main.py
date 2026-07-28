from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.chat import router as chat_router
from app.routers.system import router as system_router

app = FastAPI(
    title="Astra API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(system_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "assistant": "Astra",
        "version": "1.0.0",
    }