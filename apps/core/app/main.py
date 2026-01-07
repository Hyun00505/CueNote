import hashlib
import logging
import re
from pathlib import Path
from typing import Optional

import json

from fastapi import FastAPI, HTTPException, Query
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
logging.basicConfig(level=logging.INFO)

# 프로젝트 루트의 data 폴더를 기본 vault로 사용
# apps/core/app/main.py -> 3단계 상위가 프로젝트 루트
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "data"

# vault 디렉토리 생성
VAULT_PATH.mkdir(parents=True, exist_ok=True)

TODO_PATTERN = re.compile(r"^\s*-\s*\[(?P<checked>[ xX])\]\s+(?P<text>.+)\s*$")


class VaultFilePayload(BaseModel):
    path: str  # relative path in vault
    content: str


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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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


# ─────────────────────────────────────────────────────────────────────────────
# Vault Endpoints
# ─────────────────────────────────────────────────────────────────────────────


class VaultOpenPayload(BaseModel):
    path: Optional[str] = None  # 경로가 없으면 기본 data 폴더 사용


@app.post("/vault/open")
async def open_vault(payload: VaultOpenPayload = None):
    """
    Vault를 열고 초기화합니다.
    payload.path가 없으면 프로젝트 루트의 data 폴더를 사용합니다.
    """
    vault_dir = VAULT_PATH
    if payload and payload.path:
        vault_dir = Path(payload.path)
    
    if not vault_dir.exists():
        vault_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created vault directory: %s", vault_dir)
    
    if not vault_dir.is_dir():
        raise HTTPException(status_code=400, detail="Invalid vault path")
    
    logger.info("Vault opened: %s", vault_dir)
    return {"status": "ok", "path": str(vault_dir)}


@app.get("/vault/files")
async def list_vault_files():
    """
    Vault 내의 모든 마크다운 파일을 재귀적으로 조회합니다.
    """
    if not VAULT_PATH.exists():
        VAULT_PATH.mkdir(parents=True, exist_ok=True)
    
    files: list[str] = []
    for md_file in VAULT_PATH.rglob("*.md"):
        # 상대 경로로 변환
        rel_path = md_file.relative_to(VAULT_PATH)
        files.append(str(rel_path).replace("\\", "/"))
    
    files.sort()
    logger.info("Found %d markdown files in vault", len(files))
    return {"files": files}


@app.get("/vault/file")
async def get_vault_file(path: str = Query(..., description="Relative path to file")):
    """
    Vault 내의 특정 마크다운 파일 내용을 읽습니다.
    """
    # 경로 순회 공격 방지
    safe_path = Path(path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = VAULT_PATH / safe_path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")
    
    try:
        content = file_path.read_text(encoding="utf-8")
        logger.info("Read file: %s", safe_path)
        return {"path": safe_path, "content": content}
    except Exception as e:
        logger.error("Failed to read file %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to read file")


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
    """
    Vault 내의 마크다운 파일을 저장하고, TODO를 인덱싱합니다.
    파일이 없으면 새로 생성합니다.
    """
    # 경로 순회 공격 방지
    safe_path = Path(payload.path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = VAULT_PATH / safe_path
    
    # 상위 디렉토리 생성
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # 파일 저장
        file_path.write_text(payload.content, encoding="utf-8")
        logger.info("Saved file: %s", safe_path)
    except Exception as e:
        logger.error("Failed to save file %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # TODO 파싱 및 인덱싱
    todos = parse_todos(safe_path, payload.content)
    conn = get_conn()
    try:
        conn.execute("DELETE FROM todos WHERE note_path = ?", (safe_path,))
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
    
    logger.info("Indexed %s todos for %s", len(todos), safe_path)
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
