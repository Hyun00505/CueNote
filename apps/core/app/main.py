import asyncio
import sqlite3
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"
DB_PATH = DATA_PATH / "cuenote.db"

app = FastAPI(title="CueNote Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_database():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        );
        """
    )
    connection.commit()
    connection.close()


@app.on_event("startup")
async def on_startup() -> None:
    ensure_database()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/events")
async def events(request: Request):
    async def event_generator():
        yield {"event": "message", "data": "core ready"}
        while True:
            if await request.is_disconnected():
                break
            yield {"event": "message", "data": "tick"}
            await asyncio.sleep(5)

    return EventSourceResponse(event_generator())
