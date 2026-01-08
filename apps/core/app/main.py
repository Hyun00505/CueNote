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
    allow_origins=["*"],  # Allow all origins for Electron app
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


@app.post("/vault/file")
async def create_vault_file():
    """
    Vault 내에 새로운 마크다운 파일을 자동 생성합니다.
    파일명은 'Untitled', 'Untitled 1', 'Untitled 2' 등으로 자동 생성됩니다.
    """
    # 고유한 파일명 생성
    base_name = "Untitled"
    counter = 0
    
    while True:
        if counter == 0:
            filename = f"{base_name}.md"
        else:
            filename = f"{base_name} {counter}.md"
        
        file_path = VAULT_PATH / filename
        if not file_path.exists():
            break
        counter += 1
    
    try:
        # 기본 템플릿으로 파일 생성
        title = filename.replace('.md', '')
        default_content = f"# {title}\n\n"
        file_path.write_text(default_content, encoding="utf-8")
        logger.info("Created file: %s", filename)
        return {"status": "ok", "path": filename}
    except Exception as e:
        logger.error("Failed to create file %s: %s", filename, e)
        raise HTTPException(status_code=500, detail="Failed to create file")


class DeleteFilePayload(BaseModel):
    path: str


# 휴지통 디렉토리
TRASH_PATH = VAULT_PATH / ".trash"


@app.delete("/vault/file")
async def delete_vault_file(payload: DeleteFilePayload):
    """
    Vault 내의 마크다운 파일을 휴지통으로 이동합니다.
    """
    # 경로 순회 공격 방지
    safe_path = Path(payload.path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = VAULT_PATH / safe_path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")
    
    try:
        # DB에서 해당 파일의 TODO 삭제
        conn = get_conn()
        try:
            conn.execute("DELETE FROM todos WHERE note_path = ?", (safe_path,))
            conn.commit()
        finally:
            conn.close()
        
        # 휴지통 디렉토리 생성
        TRASH_PATH.mkdir(parents=True, exist_ok=True)
        
        # 휴지통에 동일한 이름이 있으면 고유한 이름 생성
        trash_file = TRASH_PATH / file_path.name
        counter = 0
        while trash_file.exists():
            counter += 1
            stem = file_path.stem
            suffix = file_path.suffix
            trash_file = TRASH_PATH / f"{stem}_{counter}{suffix}"
        
        # 파일을 휴지통으로 이동
        file_path.rename(trash_file)
        logger.info("Moved to trash: %s -> %s", safe_path, trash_file.name)
        return {"status": "ok", "path": safe_path}
    except Exception as e:
        logger.error("Failed to move file to trash %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to delete file")


@app.get("/vault/trash")
async def list_trash_files():
    """
    휴지통 내의 모든 파일을 조회합니다.
    """
    if not TRASH_PATH.exists():
        return {"files": []}
    
    files: list[str] = []
    for md_file in TRASH_PATH.glob("*.md"):
        files.append(md_file.name)
    
    files.sort()
    logger.info("Found %d files in trash", len(files))
    return {"files": files}


class RestoreFilePayload(BaseModel):
    filename: str


@app.post("/vault/trash/restore")
async def restore_from_trash(payload: RestoreFilePayload):
    """
    휴지통에서 파일을 복원합니다.
    """
    filename = payload.filename.strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    trash_file = TRASH_PATH / filename
    
    if not trash_file.exists():
        raise HTTPException(status_code=404, detail="File not found in trash")
    
    # 복원할 파일명 결정 (중복 시 번호 추가)
    restore_name = filename
    restore_path = VAULT_PATH / restore_name
    counter = 0
    while restore_path.exists():
        counter += 1
        stem = Path(filename).stem
        # 기존 번호 제거 (예: Untitled_1 -> Untitled)
        if "_" in stem and stem.rsplit("_", 1)[-1].isdigit():
            stem = stem.rsplit("_", 1)[0]
        restore_name = f"{stem}_{counter}.md"
        restore_path = VAULT_PATH / restore_name
    
    try:
        trash_file.rename(restore_path)
        logger.info("Restored from trash: %s -> %s", filename, restore_name)
        return {"status": "ok", "path": restore_name}
    except Exception as e:
        logger.error("Failed to restore file %s: %s", filename, e)
        raise HTTPException(status_code=500, detail="Failed to restore file")


class PermanentDeletePayload(BaseModel):
    filename: str


@app.delete("/vault/trash")
async def permanent_delete(payload: PermanentDeletePayload):
    """
    휴지통에서 파일을 영구 삭제합니다.
    """
    filename = payload.filename.strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    trash_file = TRASH_PATH / filename
    
    if not trash_file.exists():
        raise HTTPException(status_code=404, detail="File not found in trash")
    
    try:
        trash_file.unlink()
        logger.info("Permanently deleted: %s", filename)
        return {"status": "ok", "filename": filename}
    except Exception as e:
        logger.error("Failed to permanently delete %s: %s", filename, e)
        raise HTTPException(status_code=500, detail="Failed to delete file")


@app.delete("/vault/trash/empty")
async def empty_trash():
    """
    휴지통을 비웁니다.
    """
    if not TRASH_PATH.exists():
        return {"status": "ok", "deleted": 0}
    
    deleted_count = 0
    try:
        for md_file in TRASH_PATH.glob("*.md"):
            md_file.unlink()
            deleted_count += 1
        logger.info("Emptied trash: %d files deleted", deleted_count)
        return {"status": "ok", "deleted": deleted_count}
    except Exception as e:
        logger.error("Failed to empty trash: %s", e)
        raise HTTPException(status_code=500, detail="Failed to empty trash")


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
