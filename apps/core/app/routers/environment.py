"""
CueNote Core - Environment 라우터
여러 Vault(작업 환경) 관리
"""
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import PROJECT_ROOT, DATA_DIR, VAULT_PATH, logger

router = APIRouter(prefix="/environment", tags=["environment"])

# 환경 설정 파일 경로 (앱 데이터 폴더에 저장)
ENV_CONFIG_PATH = DATA_DIR / "environments.json"


class Environment(BaseModel):
    """환경 정보"""
    id: str
    name: str
    path: str
    type: str = "local"  # 'local' | 'github'
    github: Optional[dict] = None  # GitHub 정보 (owner, repo, private 등)


class EnvironmentConfig(BaseModel):
    """환경 설정"""
    environments: list[Environment] = []
    current_id: Optional[str] = None


class AddEnvironmentPayload(BaseModel):
    """환경 추가 요청"""
    name: str
    path: str
    type: str = "local"
    github: Optional[dict] = None


class SetCurrentPayload(BaseModel):
    """현재 환경 설정 요청"""
    id: str


class RemoveEnvironmentPayload(BaseModel):
    """환경 제거 요청"""
    id: str


def load_config() -> EnvironmentConfig:
    """환경 설정 로드"""
    if not ENV_CONFIG_PATH.exists():
        return EnvironmentConfig()
    
    try:
        data = json.loads(ENV_CONFIG_PATH.read_text(encoding="utf-8"))
        return EnvironmentConfig(**data)
    except Exception as e:
        logger.error("Failed to load environment config: %s", e)
        return EnvironmentConfig()


def save_config(config: EnvironmentConfig):
    """환경 설정 저장"""
    ENV_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENV_CONFIG_PATH.write_text(
        json.dumps(config.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def generate_env_id(name: str) -> str:
    """환경 ID 생성"""
    import hashlib
    from datetime import datetime
    raw = f"{name}_{datetime.now().isoformat()}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


@router.get("/list")
async def list_environments():
    """모든 환경 목록 조회"""
    config = load_config()
    
    # 각 환경의 유효성 확인
    valid_envs = []
    for env in config.environments:
        exists = True
        if env.type == "local":
            env_path = Path(env.path)
            exists = env_path.exists()
            
        valid_envs.append({
            **env.model_dump(),
            "exists": exists,
            "is_current": env.id == config.current_id
        })
    
    return {
        "environments": valid_envs,
        "current_id": config.current_id
    }


@router.post("/add")
async def add_environment(payload: AddEnvironmentPayload):
    """새 환경 추가"""
    env_path = Path(payload.path)
    
    # 로컬 환경인 경우에만 경로 유효성 검사
    if payload.type == "local":
        if not env_path.exists():
            raise HTTPException(status_code=400, detail="경로가 존재하지 않습니다")
        
        if not env_path.is_dir():
            raise HTTPException(status_code=400, detail="유효한 폴더가 아닙니다")
    
    config = load_config()
    
    # 중복 확인
    for env in config.environments:
        # 로컬 환경: 경로 중복 확인
        if payload.type == "local" and env.type == "local":
             if Path(env.path).resolve() == env_path.resolve():
                raise HTTPException(status_code=409, detail="이미 등록된 환경입니다")
        # GitHub 환경: owner/repo 중복 확인
        elif payload.type == "github" and env.type == "github":
            if (env.github and payload.github and 
                env.github.get("owner") == payload.github.get("owner") and 
                env.github.get("repo") == payload.github.get("repo")):
                raise HTTPException(status_code=409, detail="이미 등록된 리포지토리입니다")
    
    # 새 환경 추가
    new_env = Environment(
        id=generate_env_id(payload.name),
        name=payload.name,
        path=payload.path if payload.type == "local" else f"github://{payload.github['owner']}/{payload.github['repo']}" if payload.github else "",
        type=payload.type,
        github=payload.github
    )
    config.environments.append(new_env)
    
    # 첫 번째 환경이면 현재 환경으로 설정
    if len(config.environments) == 1:
        config.current_id = new_env.id
    
    save_config(config)
    logger.info("Environment added: %s (%s)", new_env.name, new_env.path)
    
    return {
        "status": "ok",
        "environment": new_env.model_dump(),
        "is_current": new_env.id == config.current_id
    }


@router.post("/set-current")
async def set_current_environment(payload: SetCurrentPayload):
    """현재 환경 설정"""
    config = load_config()
    
    # 환경 존재 확인
    env = next((e for e in config.environments if e.id == payload.id), None)
    if not env:
        raise HTTPException(status_code=404, detail="환경을 찾을 수 없습니다")
    
    config.current_id = payload.id
    save_config(config)
    
    logger.info("Current environment set to: %s", env.name)
    
    return {
        "status": "ok",
        "current": env.model_dump()
    }


@router.get("/current")
async def get_current_environment():
    """현재 환경 조회"""
    config = load_config()
    
    if not config.current_id:
        return {"current": None}
    
    env = next((e for e in config.environments if e.id == config.current_id), None)
    if not env:
        return {"current": None}
    
    exists = True
    if env.type == "local":
        exists = Path(env.path).exists()

    return {
        "current": {
            **env.model_dump(),
            "exists": exists
        }
    }


@router.delete("/remove")
async def remove_environment(payload: RemoveEnvironmentPayload):
    """환경 제거 (실제 폴더는 삭제하지 않음)"""
    config = load_config()
    
    # 환경 찾기
    env_index = next(
        (i for i, e in enumerate(config.environments) if e.id == payload.id),
        None
    )
    
    if env_index is None:
        raise HTTPException(status_code=404, detail="환경을 찾을 수 없습니다")
    
    removed_env = config.environments.pop(env_index)
    
    # 현재 환경이 삭제되면 다른 환경으로 변경
    if config.current_id == payload.id:
        config.current_id = config.environments[0].id if config.environments else None
    
    save_config(config)
    logger.info("Environment removed: %s", removed_env.name)
    
    return {
        "status": "ok",
        "removed": removed_env.model_dump(),
        "new_current_id": config.current_id
    }


@router.post("/init-default")
async def init_default_environment():
    """기본 환경 초기화 (data 폴더)"""
    config = load_config()
    
    # 기본 환경이 이미 있는지 확인
    default_path = VAULT_PATH
    for env in config.environments:
        if Path(env.path).resolve() == default_path.resolve():
            # 이미 있으면 현재 환경으로 설정
            config.current_id = env.id
            save_config(config)
            return {
                "status": "ok",
                "environment": env.model_dump(),
                "message": "기존 환경을 현재 환경으로 설정했습니다"
            }
    
    # 기본 환경 추가
    default_path.mkdir(parents=True, exist_ok=True)
    default_env = Environment(
        id=generate_env_id("Default"),
        name="기본 노트",
        path=str(default_path.resolve())
    )
    config.environments.append(default_env)
    config.current_id = default_env.id
    save_config(config)
    
    logger.info("Default environment initialized: %s", default_path)
    
    return {
        "status": "ok",
        "environment": default_env.model_dump(),
        "message": "기본 환경이 생성되었습니다"
    }
