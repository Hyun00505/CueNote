"""
CueNote Core - 설정
"""
import logging
import os
import re
import sys
from pathlib import Path

# 로거 설정
logger = logging.getLogger("cuenote.core")
logging.basicConfig(level=logging.INFO)

# 프로덕션 모드 감지
IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    # 프로덕션 모드: %APPDATA%/cuenote 사용
    if os.name == 'nt':
        _app_data_base = Path(os.environ.get('APPDATA', '')) / 'cuenote'
    elif os.name == 'posix' and 'darwin' in sys.platform:
        _app_data_base = Path.home() / 'Library' / 'Application Support' / 'cuenote'
    else:
        _app_data_base = Path.home() / '.cuenote'

    PROJECT_ROOT = _app_data_base
    DATA_DIR = _app_data_base / "data"
    VAULT_PATH = Path.home() / "Documents" / "CueNote"
else:
    # 개발 모드: 프로젝트 루트의 data 폴더를 기본 vault로 사용
    # apps/core/app/config.py -> 3단계 상위가 프로젝트 루트
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "apps" / "core" / "data"
    VAULT_PATH = PROJECT_ROOT / "data"

TRASH_PATH = VAULT_PATH / ".trash"

# 디렉토리 생성
VAULT_PATH.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# TODO 패턴
TODO_PATTERN = re.compile(r"^\s*-\s*\[(?P<checked>[ xX])\]\s+(?P<text>.+)\s*$")

