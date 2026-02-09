"""
CueNote Core - Vault 라우터
파일 CRUD 및 휴지통 관리
"""
import hashlib
import uuid
import base64
import json
import re
from typing import Optional
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse

from ..config import VAULT_PATH, TRASH_PATH, TODO_PATTERN, logger, PROJECT_ROOT, DATA_DIR
from ..db import get_conn
from pydantic import BaseModel as PydanticBaseModel

from ..schemas import (
    VaultOpenPayload, VaultFilePayload,
    RenameFilePayload, RestoreFilePayload, PermanentDeletePayload,
    TodoItem, ImageUploadPayload
)

router = APIRouter(prefix="/vault", tags=["vault"])

# 환경 설정 파일 경로
ENV_CONFIG_PATH = DATA_DIR / "environments.json"


def get_git_repos_dir() -> Path:
    """Git 리포지토리 저장 디렉토리 반환 (github.py와 동일)"""
    import os
    import sys
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', '')) / 'cuenote'
    elif os.name == 'posix':
        if 'darwin' in sys.platform:
            base = Path.home() / 'Library' / 'Application Support' / 'cuenote'
        else:
            base = Path.home() / '.local' / 'share' / 'cuenote'
    else:
        base = Path.home() / '.cuenote'
    
    return base / 'git-repos'


def get_current_vault_path() -> Path:
    """현재 선택된 환경의 Vault 경로 반환"""
    if not ENV_CONFIG_PATH.exists():
        return VAULT_PATH
    
    try:
        data = json.loads(ENV_CONFIG_PATH.read_text(encoding="utf-8"))
        current_id = data.get("current_id")
        if not current_id:
            return VAULT_PATH
        
        for env in data.get("environments", []):
            if env.get("id") == current_id:
                env_type = env.get("type", "local")
                
                # GitHub 환경인 경우 실제 클론 경로 반환
                if env_type == "github":
                    github_info = env.get("github", {})
                    owner = github_info.get("owner")
                    repo = github_info.get("repo")
                    if owner and repo:
                        git_path = get_git_repos_dir() / f"{owner}_{repo}"
                        if git_path.exists():
                            return git_path
                    return VAULT_PATH
                
                # 로컬 환경
                env_path = Path(env.get("path", ""))
                if env_path.exists():
                    return env_path
        
        return VAULT_PATH
    except Exception as e:
        logger.error("Failed to get current vault path: %s", e)
        return VAULT_PATH


def get_trash_path() -> Path:
    """현재 Vault의 휴지통 경로 반환"""
    return get_current_vault_path() / ".trash"


def get_img_path() -> Path:
    """현재 Vault의 이미지 저장 경로 반환"""
    return get_current_vault_path() / "img"


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
async def open_vault(payload: Optional[VaultOpenPayload] = None):
    """Vault를 열고 초기화합니다."""
    vault_dir = get_current_vault_path()
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
    vault_path = get_current_vault_path()
    if not vault_path.exists():
        vault_path.mkdir(parents=True, exist_ok=True)
    
    files: list[str] = []
    for md_file in vault_path.rglob("*.md"):
        rel_path = md_file.relative_to(vault_path)
        rel_path_str = str(rel_path).replace("\\", "/")
        
        # .trash 폴더 내의 파일은 제외
        if rel_path_str.startswith(".trash/") or "/.trash/" in rel_path_str:
            continue
        
        files.append(rel_path_str)
    
    files.sort()
    logger.info("Found %d markdown files in vault", len(files))
    return {"files": files}


@router.get("/file")
async def get_vault_file(path: str = Query(..., description="Relative path to file")):
    """Vault 내의 특정 마크다운 파일 내용을 읽습니다."""
    vault_path = get_current_vault_path()
    safe_path = Path(path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = vault_path / safe_path
    
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
    vault_path = get_current_vault_path()
    safe_path = Path(payload.path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = vault_path / safe_path
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
    vault_path = get_current_vault_path()
    base_name = "Untitled"
    counter = 0
    
    while True:
        filename = f"{base_name}.md" if counter == 0 else f"{base_name} {counter}.md"
        file_path = vault_path / filename
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
    vault_path = get_current_vault_path()
    old_safe_path = Path(payload.old_path).as_posix()
    new_safe_path = Path(payload.new_path).as_posix()
    
    if ".." in old_safe_path or old_safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid old path")
    if ".." in new_safe_path or new_safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid new path")
    
    if not new_safe_path.endswith('.md'):
        new_safe_path += '.md'
    
    old_file_path = vault_path / old_safe_path
    new_file_path = vault_path / new_safe_path
    
    if not old_file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if not old_file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")
    if new_file_path.exists():
        raise HTTPException(status_code=409, detail="File with new name already exists")
    
    # 대상 폴더가 없으면 생성
    new_file_path.parent.mkdir(parents=True, exist_ok=True)
    
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


@router.post("/folder/rename")
async def rename_vault_folder(payload: RenameFilePayload):
    """Vault 내의 폴더 이름을 변경합니다."""
    vault_path = get_current_vault_path()
    old_safe_path = Path(payload.old_path).as_posix()
    new_safe_path = Path(payload.new_path).as_posix()
    
    if ".." in old_safe_path or old_safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid old path")
    if ".." in new_safe_path or new_safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid new path")
    
    old_folder_path = vault_path / old_safe_path
    new_folder_path = vault_path / new_safe_path
    
    if not old_folder_path.exists():
        raise HTTPException(status_code=404, detail="Folder not found")
    if not old_folder_path.is_dir():
        raise HTTPException(status_code=400, detail="Not a folder")
    if new_folder_path.exists():
        raise HTTPException(status_code=409, detail="Folder with new name already exists")
    
    # 대상 부모 폴더가 없으면 생성
    new_folder_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # DB의 모든 관련 경로 업데이트
        conn = get_conn()
        try:
            # 해당 폴더 하위의 모든 파일 경로 업데이트
            cursor = conn.execute("SELECT note_path FROM todos WHERE note_path LIKE ?", (old_safe_path + "/%",))
            rows = cursor.fetchall()
            for row in rows:
                old_note_path = row[0]
                new_note_path = new_safe_path + old_note_path[len(old_safe_path):]
                conn.execute("UPDATE todos SET note_path = ? WHERE note_path = ?", (new_note_path, old_note_path))
            conn.commit()
        finally:
            conn.close()
        
        old_folder_path.rename(new_folder_path)
        logger.info("Renamed folder: %s -> %s", old_safe_path, new_safe_path)
        return {"status": "ok", "old_path": old_safe_path, "new_path": new_safe_path}
    except Exception as e:
        logger.error("Failed to rename folder %s: %s", old_safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to rename folder")


@router.delete("/file")
async def delete_vault_file(path: str = Query(..., description="Relative path to file to delete")):
    """Vault 내의 마크다운 파일을 휴지통으로 이동합니다."""
    vault_path = get_current_vault_path()
    trash_path = get_trash_path()
    safe_path = Path(path).as_posix()
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = vault_path / safe_path
    
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
        
        trash_path.mkdir(parents=True, exist_ok=True)
        
        trash_file = trash_path / file_path.name
        counter = 0
        while trash_file.exists():
            counter += 1
            trash_file = trash_path / f"{file_path.stem}_{counter}{file_path.suffix}"
        
        file_path.rename(trash_file)
        logger.info("Moved to trash: %s -> %s", safe_path, trash_file.name)
        return {"status": "ok", "path": safe_path}
    except Exception as e:
        logger.error("Failed to move file to trash %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to delete file")


@router.get("/trash")
async def list_trash_files():
    """휴지통 내의 모든 파일을 조회합니다."""
    trash_path = get_trash_path()
    if not trash_path.exists():
        return {"files": []}
    
    files = [md_file.name for md_file in trash_path.glob("*.md")]
    files.sort()
    logger.info("Found %d files in trash", len(files))
    return {"files": files}


@router.post("/trash/restore")
async def restore_from_trash(payload: RestoreFilePayload):
    """휴지통에서 파일을 복원합니다."""
    vault_path = get_current_vault_path()
    trash_path = get_trash_path()
    filename = payload.filename.strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    trash_file = trash_path / filename
    if not trash_file.exists():
        raise HTTPException(status_code=404, detail="File not found in trash")
    
    restore_name = filename
    restore_path = vault_path / restore_name
    counter = 0
    while restore_path.exists():
        counter += 1
        stem = Path(filename).stem
        if "_" in stem and stem.rsplit("_", 1)[-1].isdigit():
            stem = stem.rsplit("_", 1)[0]
        restore_name = f"{stem}_{counter}.md"
        restore_path = vault_path / restore_name
    
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
    trash_path = get_trash_path()
    filename = payload.filename.strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    trash_file = trash_path / filename
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
    trash_path = get_trash_path()
    if not trash_path.exists():
        return {"status": "ok", "deleted": 0}
    
    deleted_count = 0
    try:
        for md_file in trash_path.glob("*.md"):
            md_file.unlink()
            deleted_count += 1
        logger.info("Emptied trash: %d files deleted", deleted_count)
        return {"status": "ok", "deleted": deleted_count}
    except Exception as e:
        logger.error("Failed to empty trash: %s", e)
        raise HTTPException(status_code=500, detail="Failed to empty trash")


# ─────────────────────────────────────────────────────────────────────────────
# 이미지 관리
# ─────────────────────────────────────────────────────────────────────────────

def sanitize_filename(name: str) -> str:
    """파일명에서 특수문자 제거"""
    # 파일명에 사용할 수 없는 문자 제거
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    # 공백을 언더스코어로 변경
    sanitized = re.sub(r'\s+', '_', sanitized)
    # 연속된 언더스코어 제거
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')


@router.post("/image")
async def upload_image(payload: ImageUploadPayload):
    """Base64 이미지를 파일로 저장합니다."""
    try:
        img_path = get_img_path()
        # img 폴더 생성
        img_path.mkdir(parents=True, exist_ok=True)
        
        # Base64 데이터 파싱
        data = payload.data
        if data.startswith('data:'):
            # data:image/png;base64,xxxxx 형식
            header, encoded = data.split(',', 1)
            # MIME 타입에서 확장자 추출
            mime_type = header.split(':')[1].split(';')[0]
            ext_map = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/svg+xml': '.svg',
            }
            ext = ext_map.get(mime_type, '.png')
        else:
            # 순수 Base64 데이터
            encoded = data
            ext = '.png'
        
        # 파일명 생성: 노트이름_YYYYMMDD_HHMMSS.확장자
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:20]  # 밀리초까지 포함
        
        if payload.note_name:
            # .md 확장자 제거하고 sanitize
            note_base = payload.note_name.replace('.md', '')
            note_base = sanitize_filename(note_base)
            filename = f"{note_base}_{timestamp}{ext}"
        else:
            filename = f"img_{timestamp}{ext}"
        
        # 파일 저장
        file_path = img_path / filename
        image_data = base64.b64decode(encoded)
        file_path.write_bytes(image_data)
        
        logger.info("Image saved: %s (%d bytes)", filename, len(image_data))
        
        # 상대 경로 반환 (마크다운에서 사용)
        return {
            "status": "ok",
            "filename": filename,
            "path": f"img/{filename}",
            "url": f"/vault/image/{filename}"
        }
    except Exception as e:
        logger.error("Failed to save image: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")


@router.get("/image/{filename}")
async def get_image(filename: str):
    """저장된 이미지를 반환합니다."""
    img_path = get_img_path()
    # 경로 탐색 방지
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = img_path / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # MIME 타입 결정
    ext = file_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
    }
    media_type = mime_types.get(ext, 'application/octet-stream')
    
    return FileResponse(file_path, media_type=media_type)


@router.get("/images")
async def list_images():
    """저장된 모든 이미지 목록을 반환합니다."""
    img_path = get_img_path()
    if not img_path.exists():
        return {"images": []}
    
    images = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.svg']:
        for img_file in img_path.glob(ext):
            images.append({
                "filename": img_file.name,
                "path": f"img/{img_file.name}",
                "url": f"/vault/image/{img_file.name}",
                "size": img_file.stat().st_size
            })
    
    images.sort(key=lambda x: x['filename'], reverse=True)
    return {"images": images}


# ─────────────────────────────────────────────────────────────────────────────
# 폴더 관리
# ─────────────────────────────────────────────────────────────────────────────

class CreateFolderPayload(PydanticBaseModel):
    """폴더 생성 요청"""
    path: str


class DeleteFolderPayload(PydanticBaseModel):
    """폴더 삭제 요청"""
    path: str


@router.get("/folders")
async def list_folders():
    """Vault 내의 모든 폴더를 조회합니다."""
    vault_path = get_current_vault_path()
    if not vault_path.exists():
        return {"folders": []}
    
    folders = []
    for item in vault_path.rglob("*"):
        if item.is_dir():
            rel_path = item.relative_to(vault_path)
            rel_path_str = str(rel_path).replace("\\", "/")
            
            # 숨김 폴더, 시스템 폴더 제외
            if rel_path_str.startswith(".") or "/.trash" in rel_path_str or rel_path_str.startswith(".trash"):
                continue
            if rel_path_str.startswith("img"):
                continue
                
            folders.append(rel_path_str)
    
    folders.sort()
    return {"folders": folders}


@router.post("/folder")
async def create_folder(payload: CreateFolderPayload):
    """Vault 내에 새 폴더를 생성합니다."""
    vault_path = get_current_vault_path()
    safe_path = Path(payload.path).as_posix()
    
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # 숨김 폴더 생성 방지
    if safe_path.startswith(".") or "/." in safe_path:
        raise HTTPException(status_code=400, detail="Cannot create hidden folders")
    
    folder_path = vault_path / safe_path
    
    if folder_path.exists():
        raise HTTPException(status_code=409, detail="Folder already exists")
    
    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        logger.info("Created folder: %s", safe_path)
        return {"status": "ok", "path": safe_path}
    except Exception as e:
        logger.error("Failed to create folder %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to create folder")


@router.delete("/folder")
async def delete_folder(path: str = Query(..., description="Relative path to folder to delete")):
    """Vault 내의 폴더를 삭제합니다. 폴더 내 파일도 휴지통으로 이동됩니다."""
    vault_path = get_current_vault_path()
    trash_path = get_trash_path()
    safe_path = Path(path).as_posix()
    
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # 시스템 폴더 삭제 방지
    if safe_path.startswith(".") or safe_path == "img":
        raise HTTPException(status_code=400, detail="Cannot delete system folders")
    
    folder_path = vault_path / safe_path
    
    if not folder_path.exists():
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if not folder_path.is_dir():
        raise HTTPException(status_code=400, detail="Not a folder")
    
    try:
        trash_path.mkdir(parents=True, exist_ok=True)
        
        # 폴더 내 md 파일들을 휴지통으로 이동
        moved_files = []
        for md_file in folder_path.rglob("*.md"):
            trash_file = trash_path / md_file.name
            counter = 0
            while trash_file.exists():
                counter += 1
                trash_file = trash_path / f"{md_file.stem}_{counter}{md_file.suffix}"
            md_file.rename(trash_file)
            moved_files.append(md_file.name)
            
            # TODO 데이터베이스에서 삭제
            rel_md_path = str(md_file.relative_to(vault_path)).replace("\\", "/")
            conn = get_conn()
            try:
                conn.execute("DELETE FROM todos WHERE note_path = ?", (rel_md_path,))
                conn.commit()
            finally:
                conn.close()
        
        # 빈 폴더 삭제 (하위 폴더 포함)
        import shutil
        shutil.rmtree(folder_path)
        
        logger.info("Deleted folder: %s, moved %d files to trash", safe_path, len(moved_files))
        return {"status": "ok", "path": safe_path, "moved_files": moved_files}
    except Exception as e:
        logger.error("Failed to delete folder %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to delete folder")


@router.post("/file/with-folder")
async def create_file_in_folder(path: str = Query(..., description="Relative path including folder")):
    """특정 폴더 내에 새 파일을 생성합니다."""
    vault_path = get_current_vault_path()
    safe_path = Path(path).as_posix()
    
    if ".." in safe_path or safe_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    file_path = vault_path / safe_path
    
    if file_path.exists():
        raise HTTPException(status_code=409, detail="File already exists")
    
    try:
        # 부모 폴더 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 생성
        title = file_path.stem
        default_content = f"# {title}\n\n"
        file_path.write_text(default_content, encoding="utf-8")
        
        logger.info("Created file: %s", safe_path)
        return {"status": "ok", "path": safe_path}
    except Exception as e:
        logger.error("Failed to create file %s: %s", safe_path, e)
        raise HTTPException(status_code=500, detail="Failed to create file")