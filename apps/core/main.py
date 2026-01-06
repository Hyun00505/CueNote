import hashlib
import json
import logging
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib import request as urlrequest

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "cuenote.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("cuenote.core")

app = FastAPI(title="CueNote Core")

OPEN_VAULT: Path | None = None
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_TODAY_PLAN_MODEL = os.getenv(
    "OLLAMA_TODAY_PLAN_MODEL", "HuggingFaceTB/SmolLM2-1.7B-Instruct"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            note_path TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            text TEXT NOT NULL,
            checked INTEGER NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )
    connection.close()


def get_vault_root() -> Path:
    if OPEN_VAULT is None:
        raise HTTPException(status_code=400, detail="No vault open")
    return OPEN_VAULT


def resolve_vault_path(relative_path: str) -> Path:
    if Path(relative_path).is_absolute():
        raise HTTPException(status_code=400, detail="Absolute paths are not allowed")
    vault_root = get_vault_root()
    resolved = (vault_root / relative_path).resolve()
    if vault_root not in resolved.parents and resolved != vault_root:
        raise HTTPException(status_code=400, detail="Path escapes vault")
    return resolved


def parse_todos(note_path: str, content: str) -> list[dict]:
    todos: list[dict] = []
    pattern = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.*)$")
    for index, line in enumerate(content.splitlines(), start=1):
        match = pattern.match(line)
        if not match:
            continue
        checked = match.group(1).lower() == "x"
        text = match.group(2).strip()
        if not text:
            continue
        raw_id = f"{note_path}:{index}:{text}".encode("utf-8")
        todo_id = hashlib.sha1(raw_id).hexdigest()
        todos.append(
            {
                "id": todo_id,
                "note_path": note_path,
                "line_no": index,
                "text": text,
                "checked": 1 if checked else 0,
            }
        )
    return todos


def upsert_todos(note_path: str, content: str) -> None:
    todos = parse_todos(note_path, content)
    now = datetime.now(timezone.utc).isoformat()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("BEGIN")
    if todos:
        todo_ids = [todo["id"] for todo in todos]
        placeholders = ",".join("?" for _ in todo_ids)
        cursor.execute(
            f"DELETE FROM todos WHERE note_path = ? AND id NOT IN ({placeholders})",
            [note_path, *todo_ids],
        )
    else:
        cursor.execute("DELETE FROM todos WHERE note_path = ?", (note_path,))
    for todo in todos:
        cursor.execute(
            """
            INSERT INTO todos (id, note_path, line_no, text, checked, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                note_path = excluded.note_path,
                line_no = excluded.line_no,
                text = excluded.text,
                checked = excluded.checked,
                updated_at = excluded.updated_at
            """,
            (
                todo["id"],
                todo["note_path"],
                todo["line_no"],
                todo["text"],
                todo["checked"],
                now,
            ),
        )
    connection.commit()
    connection.close()


def fetch_unchecked_todos() -> list[dict]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, note_path, line_no, text, checked
        FROM todos
        WHERE checked = 0
        ORDER BY note_path, line_no
        """
    )
    rows = cursor.fetchall()
    connection.close()
    return [
        {
            "id": row["id"],
            "notePath": row["note_path"],
            "lineNo": row["line_no"],
            "text": row["text"],
            "checked": bool(row["checked"]),
        }
        for row in rows
    ]


def is_todo_item(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    return (
        isinstance(value.get("id"), str)
        and isinstance(value.get("text"), str)
        and isinstance(value.get("checked"), bool)
        and isinstance(value.get("notePath"), str)
        and isinstance(value.get("lineNo"), int)
    )


def is_today_plan_response(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if not isinstance(value.get("tldr"), str):
        return False
    overdue = value.get("overdue")
    due_soon = value.get("dueSoon")
    next_actions = value.get("nextActions")
    quick_wins = value.get("quickWins")
    if not isinstance(overdue, list) or not all(is_todo_item(item) for item in overdue):
        return False
    if not isinstance(due_soon, list) or not all(
        is_todo_item(item) for item in due_soon
    ):
        return False
    if not isinstance(next_actions, list) or not all(
        isinstance(item, str) for item in next_actions
    ):
        return False
    if not isinstance(quick_wins, list) or not all(
        isinstance(item, str) for item in quick_wins
    ):
        return False
    return True


def call_ollama_chat(model: str, system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        f"{OLLAMA_BASE_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    message = parsed.get("message", {})
    return str(message.get("content", "")).strip()


@app.on_event("startup")
async def on_startup() -> None:
    ensure_database()
    logger.info("Core startup complete")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/vault/open")
async def open_vault(payload: dict):
    global OPEN_VAULT
    path = payload.get("path")
    if not isinstance(path, str) or not path.strip():
        raise HTTPException(status_code=400, detail="Path is required")
    vault_path = Path(path).expanduser().resolve()
    if not vault_path.exists() or not vault_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")
    OPEN_VAULT = vault_path
    logger.info("Vault opened: %s", vault_path)
    return {"ok": True}


@app.get("/vault/files")
async def list_vault_files():
    vault_root = get_vault_root()
    files: list[str] = []
    for file_path in vault_root.rglob("*.md"):
        if file_path.is_file():
            files.append(file_path.relative_to(vault_root).as_posix())
    return {"files": sorted(files)}


@app.get("/vault/file")
async def read_vault_file(path: str):
    file_path = resolve_vault_path(path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    content = file_path.read_text(encoding="utf-8")
    return {"content": content}


@app.put("/vault/file")
async def write_vault_file(payload: dict):
    path = payload.get("path")
    content = payload.get("content")
    if not isinstance(path, str) or not path.strip():
        raise HTTPException(status_code=400, detail="Path is required")
    if not isinstance(content, str):
        raise HTTPException(status_code=400, detail="Content must be a string")
    file_path = resolve_vault_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    upsert_todos(path, content)
    return {"ok": True}


@app.get("/todos")
async def list_todos(checked: bool | None = None):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if checked is None:
        cursor.execute(
            "SELECT id, note_path, line_no, text, checked FROM todos ORDER BY note_path, line_no"
        )
    else:
        cursor.execute(
            """
            SELECT id, note_path, line_no, text, checked
            FROM todos
            WHERE checked = ?
            ORDER BY note_path, line_no
            """,
            (1 if checked else 0,),
        )
    rows = cursor.fetchall()
    connection.close()
    todos = [
        {
            "id": row["id"],
            "notePath": row["note_path"],
            "lineNo": row["line_no"],
            "text": row["text"],
            "checked": bool(row["checked"]),
        }
        for row in rows
    ]
    return {"todos": todos}


@app.post("/ai/today-plan")
async def today_plan():
    todos = fetch_unchecked_todos()
    request_payload = {
        "nowISO": datetime.now(timezone.utc).isoformat(),
        "todos": todos,
    }
    system_prompt = (
        "You are a planning assistant. Return ONLY valid JSON matching the "
        "TodayPlanResponse schema. Do not include extra keys, comments, or "
        "markdown. The JSON keys must be: tldr, overdue, dueSoon, nextActions, quickWins."
    )
    user_prompt = (
        "Using the following TodayPlanRequest JSON, produce a TodayPlanResponse JSON.\n"
        f"{json.dumps(request_payload)}"
    )
    strict_system_prompt = (
        "Output only raw JSON. No prose, no markdown, no code fences. "
        "The JSON must validate as TodayPlanResponse with keys: "
        "tldr (string), overdue (TodoItem[]), dueSoon (TodoItem[]), "
        "nextActions (string[]), quickWins (string[])."
    )

    for attempt in range(2):
        response_text = call_ollama_chat(
            OLLAMA_TODAY_PLAN_MODEL,
            strict_system_prompt if attempt == 1 else system_prompt,
            user_prompt,
        )
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            if attempt == 1:
                raise HTTPException(status_code=502, detail="AI response not JSON")
            continue
        if is_today_plan_response(parsed):
            return parsed
        if attempt == 1:
            raise HTTPException(status_code=502, detail="AI response invalid")

    raise HTTPException(status_code=502, detail="AI response invalid")


@app.post("/ai/deep-summary")
async def deep_summary():
    return {"ok": True, "status": "stub"}
