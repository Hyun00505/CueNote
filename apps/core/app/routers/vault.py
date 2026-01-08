"""
CueNote Core - Vault 라우터
파일 CRUD 및 휴지통 관리
"""
import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from ..config import VAULT_PATH, TRASH_PATH, TODO_PATTERN, logger
from ..db import get_conn
from ..schemas import (
    VaultOpenPayload, VaultFilePayload, DeleteFilePayload,
    RenameFilePayload, RestoreFilePayload, PermanentDeletePayload,
    TodoItem
)

router = APIRouter(prefix="/vault", tags=["vault"])


def parse_todos(note_path: str, content: str) -> list[TodoItem]:
    """노트에서 TODO 항목을 파싱"""
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


@router.post("/open")
async def open_vault(payload: VaultOpenPayload = None):
    """Vault를 열고 초기화합니다."""
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


@router.get("/files")
async def list_vault_files():
    """Vault 내의 모든 마크다운 파일을 재귀적으로 조회합니다."""
    if not VAULT_PATH.exists():
        VAULT_PATH.mkdir(parents=True, exist_ok=True)
    
    files: list[str] = []
    for md_file in VAULT_PATH.rglob("*.md"):
        rel_path = md_file.relative_to(VAULT_PATH)
        files.append(str(rel_path).replace("\\", "/"))
    
    files.sort()
    logger.info("Found %d markdown files in vault", len(files))
    return {"files": files}


@router.get("/file")
async def get_vault_file(path: str = Query(..., description="Relative path to file")):
    """Vault 내의 특정 마크다운 파일 내용을 읽습니다."""
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


@router.put("/file")
async def put_vault_file(payload: VaultFilePayload):
    """Vault 내의 마크다운 파일을 저장하고, TODO를 인덱싱합니다."""
    safe_path = Path(payload.path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = VAULT_PATH / safe_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
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
            [(todo.id, todo.notePath, todo.lineNo, todo.text, 1 if todo.checked else 0) for todo in todos],
        )
        conn.commit()
    finally:
        conn.close()
    
    logger.info("Indexed %s todos for %s", len(todos), safe_path)
    return {"status": "ok", "todoCount": len(todos)}


@router.post("/file")
async def create_vault_file():
    """Vault 내에 새로운 마크다운 파일을 자동 생성합니다."""
    base_name = "Untitled"
    counter = 0
    
    while True:
        filename = f"{base_name}.md" if counter == 0 else f"{base_name} {counter}.md"
        file_path = VAULT_PATH / filename
        if not file_path.exists():
            break
        counter += 1
    
    try:
        title = filename.replace('.md', '')
        default_content = f"# {title}\n\n"
        file_path.write_text(default_content, encoding="utf-8")
        logger.info("Created file: %s", filename)
        return {"status": "ok", "path": filename}
    except Exception as e:
        logger.error("Failed to create file %s: %s", filename, e)
        raise HTTPException(status_code=500, detail="Failed to create file")


@router.post("/file/rename")
async def rename_vault_file(payload: RenameFilePayload):
    """Vault 내의 마크다운 파일 이름을 변경합니다."""
    old_safe_path = Path(payload.old_path).as_posix()
    new_safe_path = Path(payload.new_path).as_posix()
    
    if ".." in old_safe_path or old_safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid old path")
    if ".." in new_safe_path or new_safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid new path")
    
    if not new_safe_path.endswith('.md'):
        new_safe_path += '.md'
    
    old_file_path = VAULT_PATH / old_safe_path
    new_file_path = VAULT_PATH / new_safe_path
    
    if not old_file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if not old_file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")
    if new_file_path.exists():
        raise HTTPException(status_code=409, detail="File with new name already exists")
    
    try:
        conn = get_conn()
        try:
            conn.execute("UPDATE todos SET note_path = ? WHERE note_path = ?", (new_safe_path, old_safe_path))
            conn.commit()
        finally:
            conn.close()
        
        old_file_path.rename(new_file_path)
        logger.info("Renamed file: %s -> %s", old_safe_path, new_safe_path)
        return {"status": "ok", "old_path": old_safe_path, "new_path": new_safe_path}
    except Exception as e:
        logger.error("Failed to rename file %s: %s", old_safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to rename file")


@router.delete("/file")
async def delete_vault_file(payload: DeleteFilePayload):
    """Vault 내의 마크다운 파일을 휴지통으로 이동합니다."""
    safe_path = Path(payload.path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = VAULT_PATH / safe_path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")
    
    try:
        conn = get_conn()
        try:
            conn.execute("DELETE FROM todos WHERE note_path = ?", (safe_path,))
            conn.commit()
        finally:
            conn.close()
        
        TRASH_PATH.mkdir(parents=True, exist_ok=True)
        
        trash_file = TRASH_PATH / file_path.name
        counter = 0
        while trash_file.exists():
            counter += 1
            trash_file = TRASH_PATH / f"{file_path.stem}_{counter}{file_path.suffix}"
        
        file_path.rename(trash_file)
        logger.info("Moved to trash: %s -> %s", safe_path, trash_file.name)
        return {"status": "ok", "path": safe_path}
    except Exception as e:
        logger.error("Failed to move file to trash %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to delete file")


@router.get("/trash")
async def list_trash_files():
    """휴지통 내의 모든 파일을 조회합니다."""
    if not TRASH_PATH.exists():
        return {"files": []}
    
    files = [md_file.name for md_file in TRASH_PATH.glob("*.md")]
    files.sort()
    logger.info("Found %d files in trash", len(files))
    return {"files": files}


@router.post("/trash/restore")
async def restore_from_trash(payload: RestoreFilePayload):
    """휴지통에서 파일을 복원합니다."""
    filename = payload.filename.strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    trash_file = TRASH_PATH / filename
    if not trash_file.exists():
        raise HTTPException(status_code=404, detail="File not found in trash")
    
    restore_name = filename
    restore_path = VAULT_PATH / restore_name
    counter = 0
    while restore_path.exists():
        counter += 1
        stem = Path(filename).stem
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


@router.delete("/trash")
async def permanent_delete(payload: PermanentDeletePayload):
    """휴지통에서 파일을 영구 삭제합니다."""
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


@router.delete("/trash/empty")
async def empty_trash():
    """휴지통을 비웁니다."""
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
