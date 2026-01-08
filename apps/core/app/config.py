"""
CueNote Core - 설정
"""
import logging
import re
from pathlib import Path

# 로거 설정
logger = logging.getLogger("cuenote.core")
logging.basicConfig(level=logging.INFO)

# 프로젝트 루트의 data 폴더를 기본 vault로 사용
# apps/core/app/config.py -> 3단계 상위가 프로젝트 루트
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "data"
TRASH_PATH = VAULT_PATH / ".trash"

# vault 디렉토리 생성
VAULT_PATH.mkdir(parents=True, exist_ok=True)

# TODO 패턴
TODO_PATTERN = re.compile(r"^\s*-\s*\[(?P<checked>[ xX])\]\s+(?P<text>.+)\s*$")
