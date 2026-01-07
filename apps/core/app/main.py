import hashlib
import logging
import re
from typing import Optional

import json

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .db import get_conn, init_db
    from .ollama_client import call_json
except ImportError:
    from db import get_conn, init_db
    from ollama_client import call_json

app = FastAPI(title="CueNote Core")
logger = logging.getLogger("cuenote.core")

TODO_PATTERN = re.compile(r"^\s*-\s*\[(?P<checked>[ xX])\]\s+(?P<text>.+)\s*$")


class VaultFilePayload(BaseModel):
    note_path: str = Field(alias="notePath")
    content: str

    class Config:
        allow_population_by_field_name = True


class TodoItem(BaseModel):
    id: str
    text: str
    checked: bool
    notePath: str
    lineNo: int


class TodayPlan(BaseModel):
    tldr: str
    overdue: list[TodoItem]
    dueSoon: list[TodoItem]
    nextActions: list[str]
    quickWins: list[str]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    logger.info("CueNote core started")


@app.get("/health")
async def health():
    return {"status": "ok"}


def parse_todos(note_path: str, content: str) -> list[TodoItem]:
    todos: list[TodoItem] = []
    for index, line in enumerate(content.splitlines(), start=1):
        match = TODO_PATTERN.match(line)
        if not match:
            continue
        checked = match.group("checked").lower() == "x"
        text = match.group("text").strip()
        raw_id = f"{note_path}:{index}:{text}"
        todo_id = hashlib.sha1(raw_id.encode("utf-8")).hexdigest()
        todos.append(
            TodoItem(
                id=todo_id,
                text=text,
                checked=checked,
                notePath=note_path,
                lineNo=index,
            )
        )
    return todos


@app.put("/vault/file")
async def put_vault_file(payload: VaultFilePayload):
    todos = parse_todos(payload.note_path, payload.content)
    conn = get_conn()
    try:
        conn.execute("DELETE FROM todos WHERE note_path = ?", (payload.note_path,))
        conn.executemany(
            """
            INSERT INTO todos (id, note_path, line_no, text, checked, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            [
                (
                    todo.id,
                    todo.notePath,
                    todo.lineNo,
                    todo.text,
                    1 if todo.checked else 0,
                )
                for todo in todos
            ],
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Indexed %s todos for %s", len(todos), payload.note_path)
    return {"status": "ok", "todoCount": len(todos)}


@app.get("/todos")
async def get_todos(checked: Optional[bool] = Query(default=None)):
    conn = get_conn()
    try:
        if checked is None:
            rows = conn.execute(
                """
                SELECT id, note_path, line_no, text, checked
                FROM todos
                ORDER BY updated_at DESC
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, note_path, line_no, text, checked
                FROM todos
                WHERE checked = ?
                ORDER BY updated_at DESC
                """,
                (1 if checked else 0,),
            ).fetchall()
    finally:
        conn.close()

    todos = [
        TodoItem(
            id=row[0],
            notePath=row[1],
            lineNo=row[2],
            text=row[3],
            checked=bool(row[4]),
        )
        for row in rows
    ]
    return {"todos": [todo.dict() for todo in todos]}


@app.post("/ai/today-plan")
async def today_plan():
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, note_path, line_no, text, checked
            FROM todos
            WHERE checked = 0
            ORDER BY updated_at DESC
            LIMIT 50
            """
        ).fetchall()
    finally:
        conn.close()

    todos = [
        {
            "id": row[0],
            "notePath": row[1],
            "lineNo": row[2],
            "text": row[3],
            "checked": bool(row[4]),
        }
        for row in rows
    ]

    prompt = (
        "You are generating a daily plan. Output MUST be JSON only and match the schema.\n"
        "Rules:\n"
        "- overdue: up to 5 most important items\n"
        "- dueSoon: next 5 items\n"
        "- nextActions and quickWins are strings informed by remaining items\n\n"
        f"Todos JSON:\n{json.dumps(todos, ensure_ascii=True)}\n\n"
        "Schema:\n"
        "{\n"
        '  "tldr": "string",\n'
        '  "overdue": [TodoItem],\n'
        '  "dueSoon": [TodoItem],\n'
        '  "nextActions": ["string"],\n'
        '  "quickWins": ["string"]\n'
        "}\n"
        "TodoItem:\n"
        "{\n"
        '  "id": "string",\n'
        '  "text": "string",\n'
        '  "checked": boolean,\n'
        '  "notePath": "string",\n'
        '  "lineNo": number\n'
        "}\n"
        "Return JSON only."
    )
    schema_hint = "TodayPlan with fields tldr, overdue, dueSoon, nextActions, quickWins"
    plan = call_json(prompt, schema_hint)
    return plan
