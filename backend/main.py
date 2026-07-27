from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/")
def root():
    return {"status": "online", "assistant": "ASTRA"}


@app.get("/system")
def system_info():
    return {
        "cpu": round(psutil.cpu_percent(interval=0.1), 1),
        "ram": round(psutil.virtual_memory().percent, 1),
        "time": datetime.now().strftime("%I:%M %p"),
    }