from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psutil
from datetime import datetime

app = FastAPI(title="Astra API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "online"}

@app.get("/system")
def system():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "time": datetime.now().strftime("%I:%M %p"),
    }

@app.post("/chat")
def chat(data: ChatRequest):
    return {
        "reply": f"You said: {data.message}"
    }