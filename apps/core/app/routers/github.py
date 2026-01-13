"""
CueNote Core - GitHub 라우터
GitHub 연동 기능 (Git Clone 기반 로컬 파일 관리)
"""
import httpx
import subprocess
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import logger

router = APIRouter(prefix="/github", tags=["github"])

GITHUB_API_BASE = "https://api.github.com"

# Git 클론 저장 경로 (앱 데이터 폴더)
def get_git_repos_dir() -> Path:
    """Git 리포지토리 저장 디렉토리 반환"""
    # Windows: %APPDATA%/cuenote/git-repos
    # macOS: ~/Library/Application Support/cuenote/git-repos
    # Linux: ~/.local/share/cuenote/git-repos
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', '')) / 'cuenote'
    elif os.name == 'posix':
        if 'darwin' in os.sys.platform:
            base = Path.home() / 'Library' / 'Application Support' / 'cuenote'
        else:
            base = Path.home() / '.local' / 'share' / 'cuenote'
    else:
        base = Path.home() / '.cuenote'
    
    repos_dir = base / 'git-repos'
    repos_dir.mkdir(parents=True, exist_ok=True)
    return repos_dir


def get_repo_local_path(owner: str, repo: str) -> Path:
    """특정 리포지토리의 로컬 경로 반환"""
    return get_git_repos_dir() / f"{owner}_{repo}"


def check_git_installed() -> bool:
    """Git 설치 여부 확인"""
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_git_command(args: list[str], cwd: Path, env: dict = None) -> tuple[bool, str, str]:
    """Git 명령 실행"""
    try:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        
        result = subprocess.run(
            ['git'] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,  # 2분 타임아웃 (대용량 클론 대비)
            env=full_env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, '', 'Git 명령 시간 초과'
    except Exception as e:
        return False, '', str(e)


class GitHubTokenPayload(BaseModel):
    """GitHub 토큰 검증 요청"""
    token: str


class GitHubRepo(BaseModel):
    """GitHub 리포지토리 정보"""
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    private: bool
    html_url: str
    default_branch: str


class GitHubFile(BaseModel):
    """GitHub 파일 정보"""
    name: str
    path: str
    type: str  # 'file' or 'dir'
    size: Optional[int] = None


class CloneRepoPayload(BaseModel):
    """리포지토리 클론 요청"""
    token: str
    owner: str
    repo: str
    branch: Optional[str] = None


class FetchRepoFilesPayload(BaseModel):
    """리포지토리 파일 조회 요청"""
    token: str
    owner: str
    repo: str
    path: str = ""


class FetchFileContentPayload(BaseModel):
    """파일 내용 조회 요청"""
    token: str
    owner: str
    repo: str
    path: str


class SaveFilePayload(BaseModel):
    """파일 저장 요청"""
    token: str
    owner: str
    repo: str
    path: str
    content: str


class CreateRepoPayload(BaseModel):
    """리포지토리 생성 요청"""
    token: str
    name: str
    description: Optional[str] = ""
    private: bool = False
    auto_init: bool = True


class CommitPayload(BaseModel):
    """커밋 요청"""
    token: str
    owner: str
    repo: str
    message: str


class DeleteFilePayload(BaseModel):
    """파일 삭제 요청"""
    token: str
    owner: str
    repo: str
    path: str


class CreateFilePayload(BaseModel):
    """새 파일 생성 요청"""
    token: str
    owner: str
    repo: str
    path: str
    content: str = ""


class RenamePayload(BaseModel):
    """파일/폴더 이름 변경 요청"""
    token: str
    owner: str
    repo: str
    old_path: str
    new_path: str


def get_github_headers(token: str) -> dict:
    """GitHub API 요청 헤더 생성"""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


@router.get("/check-git")
async def check_git():
    """Git 설치 여부 확인"""
    installed = check_git_installed()
    return {"installed": installed}


@router.post("/validate-token")
async def validate_github_token(payload: GitHubTokenPayload):
    """GitHub Personal Access Token 검증"""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{GITHUB_API_BASE}/user",
                headers=get_github_headers(payload.token),
                timeout=10.0
            )
            
            if res.status_code == 200:
                user_data = res.json()
                return {
                    "valid": True,
                    "user": {
                        "login": user_data.get("login"),
                        "name": user_data.get("name"),
                        "avatar_url": user_data.get("avatar_url"),
                        "html_url": user_data.get("html_url")
                    }
                }
            elif res.status_code == 401:
                return {"valid": False, "error": "유효하지 않은 토큰입니다"}
            else:
                return {"valid": False, "error": f"GitHub API 오류: {res.status_code}"}
                
    except httpx.TimeoutException:
        return {"valid": False, "error": "GitHub 서버 응답 시간 초과"}
    except Exception as e:
        logger.error("GitHub token validation error: %s", e)
        return {"valid": False, "error": str(e)}


@router.post("/repos")
async def get_user_repos(payload: GitHubTokenPayload):
    """사용자의 리포지토리 목록 조회"""
    try:
        async with httpx.AsyncClient() as client:
            # 페이지네이션으로 모든 리포 가져오기
            all_repos = []
            page = 1
            per_page = 100
            
            while True:
                res = await client.get(
                    f"{GITHUB_API_BASE}/user/repos",
                    headers=get_github_headers(payload.token),
                    params={
                        "per_page": per_page,
                        "page": page,
                        "sort": "updated",
                        "direction": "desc",
                        "type": "all"  # owner, collaborator 포함
                    },
                    timeout=15.0
                )
                
                if res.status_code != 200:
                    raise HTTPException(status_code=res.status_code, detail="GitHub API 오류")
                
                repos = res.json()
                if not repos:
                    break
                    
                all_repos.extend(repos)
                
                if len(repos) < per_page:
                    break
                    
                page += 1
            
            # 필요한 정보만 추출
            result = []
            for repo in all_repos:
                result.append({
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description"),
                    "private": repo["private"],
                    "html_url": repo["html_url"],
                    "default_branch": repo.get("default_branch", "main"),
                    "owner": repo["owner"]["login"]
                })
            
            return {"repos": result}
            
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GitHub 서버 응답 시간 초과")
    except Exception as e:
        logger.error("Failed to fetch repos: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Git Clone 기반 로컬 파일 관리
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/clone")
async def clone_repo(payload: CloneRepoPayload):
    """리포지토리 클론 (shallow clone)"""
    if not check_git_installed():
        raise HTTPException(status_code=500, detail="Git이 설치되어 있지 않습니다")
    
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    # 이미 클론된 경우 pull로 업데이트
    if repo_path.exists() and (repo_path / '.git').exists():
        return await pull_repo(payload)
    
    # 기존 폴더 삭제 (불완전한 클론인 경우)
    if repo_path.exists():
        shutil.rmtree(repo_path)
    
    try:
        # HTTPS URL with token for authentication
        clone_url = f"https://{payload.token}@github.com/{payload.owner}/{payload.repo}.git"
        
        # Shallow clone (depth=1) for faster cloning
        args = ['clone', '--depth', '1']
        if payload.branch:
            args.extend(['--branch', payload.branch])
        args.extend([clone_url, str(repo_path)])
        
        success, stdout, stderr = run_git_command(
            args[1:],  # 'clone' is added by run_git_command
            cwd=get_git_repos_dir(),
            env={'GIT_TERMINAL_PROMPT': '0'}
        )
        
        # clone은 git 명령어에 이미 포함되어야 함
        result = subprocess.run(
            ['git'] + args,
            cwd=str(get_git_repos_dir()),
            capture_output=True,
            text=True,
            timeout=300,  # 5분 타임아웃
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        )
        
        if result.returncode != 0:
            logger.error("Clone failed: %s", result.stderr)
            raise HTTPException(status_code=500, detail=f"클론 실패: {result.stderr}")
        
        # 파일 목록 가져오기
        files = get_local_md_files(repo_path)
        
        return {
            "success": True,
            "local_path": str(repo_path),
            "files": files
        }
        
    except subprocess.TimeoutExpired:
        if repo_path.exists():
            shutil.rmtree(repo_path)
        raise HTTPException(status_code=504, detail="클론 시간 초과")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Clone error: %s", e)
        if repo_path.exists():
            shutil.rmtree(repo_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pull")
async def pull_repo(payload: CloneRepoPayload):
    """최신 변경사항 가져오기 (git pull)"""
    if not check_git_installed():
        raise HTTPException(status_code=500, detail="Git이 설치되어 있지 않습니다")
    
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists() or not (repo_path / '.git').exists():
        # 클론되지 않은 경우 클론 먼저
        return await clone_repo(payload)
    
    try:
        # Git credential 설정
        env = {
            **os.environ,
            'GIT_TERMINAL_PROMPT': '0'
        }
        
        # remote URL 업데이트 (토큰 갱신)
        remote_url = f"https://{payload.token}@github.com/{payload.owner}/{payload.repo}.git"
        subprocess.run(
            ['git', 'remote', 'set-url', 'origin', remote_url],
            cwd=str(repo_path),
            capture_output=True,
            timeout=10,
            env=env
        )
        
        # Pull
        result = subprocess.run(
            ['git', 'pull', '--rebase'],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )
        
        if result.returncode != 0:
            # conflict 발생 시
            if 'CONFLICT' in result.stdout or 'CONFLICT' in result.stderr:
                # rebase 취소
                subprocess.run(['git', 'rebase', '--abort'], cwd=str(repo_path), capture_output=True)
                raise HTTPException(status_code=409, detail="충돌이 발생했습니다. 로컬 변경사항을 먼저 커밋하거나 취소해주세요.")
            raise HTTPException(status_code=500, detail=f"Pull 실패: {result.stderr}")
        
        files = get_local_md_files(repo_path)
        
        return {
            "success": True,
            "local_path": str(repo_path),
            "files": files,
            "message": "최신 상태로 업데이트되었습니다"
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Pull error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push")
async def push_repo(payload: CommitPayload):
    """변경사항 푸시 (git push)"""
    if not check_git_installed():
        raise HTTPException(status_code=500, detail="Git이 설치되어 있지 않습니다")
    
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="클론된 리포지토리가 없습니다")
    
    try:
        env = {
            **os.environ,
            'GIT_TERMINAL_PROMPT': '0'
        }
        
        # remote URL 업데이트 (토큰 갱신)
        remote_url = f"https://{payload.token}@github.com/{payload.owner}/{payload.repo}.git"
        subprocess.run(
            ['git', 'remote', 'set-url', 'origin', remote_url],
            cwd=str(repo_path),
            capture_output=True,
            timeout=10,
            env=env
        )
        
        # Stage all changes
        subprocess.run(
            ['git', 'add', '-A'],
            cwd=str(repo_path),
            capture_output=True,
            timeout=30,
            env=env
        )
        
        # Commit
        commit_result = subprocess.run(
            ['git', 'commit', '-m', payload.message],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        # nothing to commit인 경우
        if commit_result.returncode != 0 and 'nothing to commit' in commit_result.stdout:
            return {
                "success": True,
                "message": "변경사항이 없습니다"
            }
        
        # Push
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'HEAD'],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )
        
        if push_result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Push 실패: {push_result.stderr}")
        
        return {
            "success": True,
            "message": "푸시 완료"
        }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Push error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/status")
async def get_repo_status(payload: FetchRepoFilesPayload):
    """Git 상태 확인 (변경된 파일 목록)"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        return {"cloned": False, "changes": []}
    
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        changes = []
        for line in result.stdout.strip().split('\n'):
            if line:
                status = line[:2].strip()
                path = line[3:].strip()
                if path.endswith('.md'):
                    changes.append({
                        "path": path,
                        "status": status,
                        "status_text": get_status_text(status)
                    })
        
            return {
            "cloned": True,
            "changes": changes,
            "has_changes": len(changes) > 0
        }
        
    except Exception as e:
        logger.error("Status error: %s", e)
        return {"cloned": True, "changes": [], "error": str(e)}


def get_status_text(status: str) -> str:
    """Git 상태 코드를 텍스트로 변환"""
    status_map = {
        'M': '수정됨',
        'A': '추가됨',
        'D': '삭제됨',
        'R': '이름변경',
        '??': '새 파일',
        'MM': '수정됨',
        'AM': '추가 후 수정됨'
    }
    return status_map.get(status, status)


def get_local_md_files(repo_path: Path) -> list[dict]:
    """로컬 리포지토리에서 md 파일과 폴더만 가져오기"""
    files = []
    
    # 제외할 폴더
    exclude_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.vscode', '.idea'}
    
    def scan_dir(dir_path: Path, relative_path: str = ""):
        items = []
        try:
            for item in sorted(dir_path.iterdir()):
                name = item.name
                
                # 숨김 파일/폴더 제외
                if name.startswith('.'):
                    continue
                
                # 제외 폴더 스킵
                if name in exclude_dirs:
                    continue
                
                item_relative = f"{relative_path}/{name}" if relative_path else name
                
                if item.is_dir():
                    # 폴더인 경우 재귀적으로 탐색
                    sub_items = scan_dir(item, item_relative)
                    # .gitkeep이 있는지 확인 (빈 폴더도 표시하기 위해)
                    has_gitkeep = (item / ".gitkeep").exists()
                    # 빈 폴더도 표시 (md 파일이 없어도 폴더는 보여줌)
                    items.append({
                        "name": name,
                        "path": item_relative,
                        "type": "dir",
                        "children": sub_items,
                        "empty": len(sub_items) == 0 and has_gitkeep
                    })
                elif item.is_file() and name.lower().endswith('.md'):
                    items.append({
                        "name": name,
                        "path": item_relative,
                        "type": "file",
                        "size": item.stat().st_size
                    })
        except PermissionError:
            pass
        
        return items
    
    return scan_dir(repo_path)


@router.post("/repo/files")
async def get_repo_files(payload: FetchRepoFilesPayload):
    """리포지토리 내 파일 목록 조회 (로컬 기반)"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        # 클론되지 않은 경우 빈 목록 반환
        return {"files": [], "cloned": False}
    
    files = get_local_md_files(repo_path)
    return {"files": files, "cloned": True}


@router.post("/repo/file-content")
async def get_file_content(payload: FetchFileContentPayload):
    """파일 내용 조회 (로컬 파일)"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    file_path = repo_path / payload.path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="파일이 아닙니다")
    
    try:
        content = file_path.read_text(encoding='utf-8')
        return {
            "content": content,
            "path": payload.path
        }
    except Exception as e:
        logger.error("Failed to read file: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repo/save-file")
async def save_file(payload: SaveFilePayload):
    """파일 저장 (로컬에 저장)"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="클론된 리포지토리가 없습니다")
    
    file_path = repo_path / payload.path
    
    # 상위 디렉토리 생성
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        file_path.write_text(payload.content, encoding='utf-8')
        return {
            "success": True,
            "path": payload.path
        }
    except Exception as e:
        logger.error("Failed to save file: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repo/create-file")
async def create_file(payload: CreateFilePayload):
    """새 파일 생성"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="클론된 리포지토리가 없습니다")
    
    # .md 확장자 자동 추가
    path = payload.path
    if not path.lower().endswith('.md'):
        path = path + '.md'
    
    file_path = repo_path / path
    
    if file_path.exists():
        raise HTTPException(status_code=409, detail="파일이 이미 존재합니다")
    
    # 상위 디렉토리 생성
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        file_path.write_text(payload.content, encoding='utf-8')
        return {
            "success": True,
            "path": path
        }
    except Exception as e:
        logger.error("Failed to create file: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repo/create-folder")
async def create_folder(payload: CreateFilePayload):
    """새 폴더 생성 (빈 .gitkeep 파일 포함)"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="클론된 리포지토리가 없습니다")
    
    folder_path = repo_path / payload.path
    
    if folder_path.exists():
        raise HTTPException(status_code=409, detail="폴더가 이미 존재합니다")
    
    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        # Git은 빈 폴더를 추적하지 않으므로 .gitkeep 파일 생성
        gitkeep_path = folder_path / ".gitkeep"
        gitkeep_path.write_text("", encoding='utf-8')
        return {
            "success": True,
            "path": payload.path
        }
    except Exception as e:
        logger.error("Failed to create folder: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repo/rename-file")
async def rename_file(payload: RenamePayload):
    """파일 이름 변경"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="클론된 리포지토리가 없습니다")
    
    old_file_path = repo_path / payload.old_path
    new_file_path = repo_path / payload.new_path
    
    if not old_file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    if new_file_path.exists():
        raise HTTPException(status_code=409, detail="같은 이름의 파일이 이미 존재합니다")
    
    # 상위 디렉토리 생성
    new_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        old_file_path.rename(new_file_path)
        return {
            "success": True,
            "old_path": payload.old_path,
            "new_path": payload.new_path
        }
    except Exception as e:
        logger.error("Failed to rename file: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repo/rename-folder")
async def rename_folder(payload: RenamePayload):
    """폴더 이름 변경"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="클론된 리포지토리가 없습니다")
    
    old_folder_path = repo_path / payload.old_path
    new_folder_path = repo_path / payload.new_path
    
    if not old_folder_path.exists():
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다")
    
    if not old_folder_path.is_dir():
        raise HTTPException(status_code=400, detail="폴더가 아닙니다")
    
    if new_folder_path.exists():
        raise HTTPException(status_code=409, detail="같은 이름의 폴더가 이미 존재합니다")
    
    # 상위 디렉토리 생성
    new_folder_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        old_folder_path.rename(new_folder_path)
        return {
            "success": True,
            "old_path": payload.old_path,
            "new_path": payload.new_path
        }
    except Exception as e:
        logger.error("Failed to rename folder: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


def get_repo_trash_path(owner: str, repo: str) -> Path:
    """GitHub 리포지토리의 휴지통 경로 반환"""
    return get_repo_local_path(owner, repo) / ".trash"


@router.post("/repo/delete-file")
async def delete_file(payload: DeleteFilePayload):
    """파일을 휴지통으로 이동"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="클론된 리포지토리가 없습니다")
    
    file_path = repo_path / payload.path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    trash_path = get_repo_trash_path(payload.owner, payload.repo)
    
    try:
        trash_path.mkdir(parents=True, exist_ok=True)
        
        if file_path.is_file():
            # 파일을 휴지통으로 이동
            trash_file = trash_path / file_path.name
            counter = 0
            while trash_file.exists():
                counter += 1
                trash_file = trash_path / f"{file_path.stem}_{counter}{file_path.suffix}"
            file_path.rename(trash_file)
        else:
            # 폴더의 경우 내부 md 파일들을 휴지통으로 이동
            for md_file in file_path.rglob("*.md"):
                trash_file = trash_path / md_file.name
                counter = 0
                while trash_file.exists():
                    counter += 1
                    trash_file = trash_path / f"{md_file.stem}_{counter}{md_file.suffix}"
                md_file.rename(trash_file)
            # 폴더 삭제
            shutil.rmtree(file_path)
        
        return {
            "success": True,
            "path": payload.path
        }
    except Exception as e:
        logger.error("Failed to delete file: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repo/trash")
async def list_trash_files(token: str, owner: str, repo: str):
    """GitHub 리포지토리의 휴지통 파일 목록"""
    trash_path = get_repo_trash_path(owner, repo)
    
    if not trash_path.exists():
        return {"files": []}
    
    files = [md_file.name for md_file in trash_path.glob("*.md")]
    files.sort()
    return {"files": files}


@router.post("/repo/trash/restore")
async def restore_from_trash(payload: DeleteFilePayload):
    """휴지통에서 파일 복원"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    trash_path = get_repo_trash_path(payload.owner, payload.repo)
    
    filename = payload.path.strip()
    if not filename:
        raise HTTPException(status_code=400, detail="파일명이 필요합니다")
    
    trash_file = trash_path / filename
    if not trash_file.exists():
        raise HTTPException(status_code=404, detail="휴지통에서 파일을 찾을 수 없습니다")
    
    restore_name = filename
    restore_path = repo_path / restore_name
    counter = 0
    while restore_path.exists():
        counter += 1
        restore_path = repo_path / f"{Path(filename).stem}_{counter}{Path(filename).suffix}"
        restore_name = restore_path.name
    
    try:
        trash_file.rename(restore_path)
        return {"success": True, "path": restore_name}
    except Exception as e:
        logger.error("Failed to restore file: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repo/trash")
async def permanent_delete_from_trash(token: str, owner: str, repo: str, filename: str):
    """휴지통에서 파일 영구 삭제"""
    trash_path = get_repo_trash_path(owner, repo)
    
    if not filename:
        raise HTTPException(status_code=400, detail="파일명이 필요합니다")
    
    trash_file = trash_path / filename
    if not trash_file.exists():
        raise HTTPException(status_code=404, detail="휴지통에서 파일을 찾을 수 없습니다")
    
    try:
        trash_file.unlink()
        return {"success": True, "filename": filename}
    except Exception as e:
        logger.error("Failed to permanently delete: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repo/trash/empty")
async def empty_trash(token: str, owner: str, repo: str):
    """휴지통 비우기"""
    trash_path = get_repo_trash_path(owner, repo)
    
    if not trash_path.exists():
        return {"success": True, "deleted": 0}
    
    deleted_count = 0
    try:
        for md_file in trash_path.glob("*.md"):
            md_file.unlink()
            deleted_count += 1
        return {"success": True, "deleted": deleted_count}
    except Exception as e:
        logger.error("Failed to empty trash: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect")
async def disconnect_repo(payload: FetchRepoFilesPayload):
    """리포지토리 연결 해제 (로컬 클론 삭제)"""
    repo_path = get_repo_local_path(payload.owner, payload.repo)
    
    if repo_path.exists():
        try:
            shutil.rmtree(repo_path)
        except Exception as e:
            logger.error("Failed to remove repo: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    return {"success": True}


@router.post("/create-repo")
async def create_repository(payload: CreateRepoPayload):
    """새 GitHub 리포지토리 생성"""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{GITHUB_API_BASE}/user/repos",
                headers=get_github_headers(payload.token),
                json={
                    "name": payload.name,
                    "description": payload.description,
                    "private": payload.private,
                    "auto_init": payload.auto_init
                },
                timeout=15.0
            )
            
            if res.status_code == 201:
                repo_data = res.json()
                return {
                    "success": True,
                    "repo": {
                        "id": repo_data["id"],
                        "name": repo_data["name"],
                        "full_name": repo_data["full_name"],
                        "description": repo_data.get("description"),
                        "private": repo_data["private"],
                        "html_url": repo_data["html_url"],
                        "default_branch": repo_data.get("default_branch", "main"),
                        "owner": repo_data["owner"]["login"]
                    }
                }
            elif res.status_code == 422:
                # 이미 존재하는 리포지토리 이름
                error_data = res.json()
                error_msg = "리포지토리 이름이 이미 존재합니다"
                if error_data.get("errors"):
                    for err in error_data["errors"]:
                        if err.get("message"):
                            error_msg = err["message"]
                raise HTTPException(status_code=422, detail=error_msg)
            elif res.status_code == 401:
                raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
            else:
                raise HTTPException(status_code=res.status_code, detail=f"GitHub API 오류: {res.status_code}")
            
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GitHub 서버 응답 시간 초과")
    except Exception as e:
        logger.error("Failed to create repo: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
