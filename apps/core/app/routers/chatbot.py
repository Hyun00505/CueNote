"""
CueNote Core - AI 챗봇 라우터
사용자 자연어 명령을 분석하여 앱 기능(도구)을 자동 실행하는 대화형 인터페이스
"""
import json
import re
import shutil
from datetime import datetime, date
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from ..config import logger
from .. import ollama_client, gemini_client, openai_client, anthropic_client

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False
    logger.warning("duckduckgo-search not installed, web_search tool disabled")

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


# ─────────────────────────────────────────────────────────────────────────────
# 스키마
# ─────────────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="메시지 역할 (user, assistant, tool_call, tool_result)")
    content: str = Field(..., description="메시지 내용")

class ChatPayload(BaseModel):
    message: str = Field(..., description="사용자 메시지")
    provider: str = Field(default="ollama", description="LLM 제공자")
    api_key: str = Field(default="", description="API 키")
    model: str = Field(default="", description="모델명")
    history: list[ChatMessage] = Field(default_factory=list, description="대화 히스토리")
    active_note_path: str = Field(default="", description="현재 열려있는 노트 경로")
    active_note_content: str = Field(default="", description="현재 열려있는 노트 내용")


# ─────────────────────────────────────────────────────────────────────────────
# CueNote 내장 도구 정의
# ─────────────────────────────────────────────────────────────────────────────

CUENOTE_TOOLS = [
    {
        "name": "create_note",
        "description": "새 노트(마크다운 파일)를 생성합니다. 제목을 지정하면 해당 이름으로 파일이 생성됩니다.",
        "parameters": {
            "title": {"type": "string", "description": "노트 제목 (파일명, .md 제외)", "required": False},
            "content": {"type": "string", "description": "노트 초기 내용 (마크다운)", "required": False},
            "folder": {"type": "string", "description": "폴더 경로 (예: 'projects/ideas')", "required": False}
        }
    },
    {
        "name": "list_notes",
        "description": "현재 볼트의 모든 노트 파일 목록을 조회합니다.",
        "parameters": {}
    },
    {
        "name": "read_note",
        "description": "특정 노트의 내용을 읽어옵니다.",
        "parameters": {
            "path": {"type": "string", "description": "노트 파일 경로 (예: 'meeting-notes.md')", "required": True}
        }
    },
    {
        "name": "save_note",
        "description": "노트의 내용을 저장합니다.",
        "parameters": {
            "path": {"type": "string", "description": "노트 파일 경로", "required": True},
            "content": {"type": "string", "description": "저장할 내용", "required": True}
        }
    },
    {
        "name": "delete_note",
        "description": "노트를 휴지통으로 이동합니다.",
        "parameters": {
            "path": {"type": "string", "description": "삭제할 노트 경로", "required": True}
        }
    },
    {
        "name": "search_notes",
        "description": "노트 제목이나 내용에서 키워드를 검색합니다.",
        "parameters": {
            "query": {"type": "string", "description": "검색 키워드", "required": True}
        }
    },
    {
        "name": "create_schedule",
        "description": "새 일정을 생성합니다.",
        "parameters": {
            "title": {"type": "string", "description": "일정 제목", "required": True},
            "date": {"type": "string", "description": "일정 날짜 (YYYY-MM-DD)", "required": True},
            "startTime": {"type": "string", "description": "시작 시간 (HH:MM)", "required": False},
            "endTime": {"type": "string", "description": "종료 시간 (HH:MM)", "required": False},
            "description": {"type": "string", "description": "일정 설명", "required": False}
        }
    },
    {
        "name": "list_schedules",
        "description": "일정 목록을 조회합니다. 특정 날짜나 월별로 필터링 가능합니다.",
        "parameters": {
            "date": {"type": "string", "description": "특정 날짜 (YYYY-MM-DD)", "required": False},
            "month": {"type": "string", "description": "월별 조회 (YYYY-MM)", "required": False}
        }
    },
    {
        "name": "delete_schedule",
        "description": "일정을 삭제합니다.",
        "parameters": {
            "schedule_id": {"type": "string", "description": "삭제할 일정 ID", "required": True}
        }
    },
    {
        "name": "list_todos",
        "description": "모든 노트에서 TODO 항목(체크리스트)을 조회합니다.",
        "parameters": {}
    },
    {
        "name": "summarize_text",
        "description": "주어진 텍스트를 요약합니다.",
        "parameters": {
            "content": {"type": "string", "description": "요약할 텍스트", "required": True}
        }
    },
    {
        "name": "translate_text",
        "description": "텍스트를 다른 언어로 번역합니다.",
        "parameters": {
            "content": {"type": "string", "description": "번역할 텍스트", "required": True},
            "target_language": {"type": "string", "description": "대상 언어 코드 (ko, en, ja, zh 등)", "required": True}
        }
    },
    {
        "name": "create_folder",
        "description": "새 폴더를 생성합니다.",
        "parameters": {
            "path": {"type": "string", "description": "폴더 경로 (예: 'projects/new-project')", "required": True}
        }
    },
    {
        "name": "web_search",
        "description": "웹에서 정보를 검색합니다. 최신 뉴스, 기사, 정보 등을 찾을 수 있습니다.",
        "parameters": {
            "query": {"type": "string", "description": "검색할 키워드 또는 문장", "required": True},
            "max_results": {"type": "integer", "description": "최대 결과 수 (기본: 5)", "required": False}
        }
    },
    {
        "name": "smart_search_notes",
        "description": "노트 내용을 AI로 분석하여 특정 정보가 포함된 노트를 찾습니다. 단순 키워드가 아닌 의미 기반 검색입니다.",
        "parameters": {
            "query": {"type": "string", "description": "찾고 싶은 정보 (자연어로 설명)", "required": True}
        }
    },
    {
        "name": "organize_notes",
        "description": "모든 노트를 AI가 분석하여 주제별 폴더로 자동 정리합니다.",
        "parameters": {}
    },
    {
        "name": "move_note",
        "description": "노트를 다른 폴더로 이동합니다.",
        "parameters": {
            "path": {"type": "string", "description": "이동할 노트 경로", "required": True},
            "destination": {"type": "string", "description": "대상 폴더 경로", "required": True}
        }
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 도구 실행 함수
# ─────────────────────────────────────────────────────────────────────────────

async def execute_tool(tool_name: str, args: dict, provider: str = "", api_key: str = "", model: str = "") -> dict:
    """CueNote 내장 도구를 실행합니다."""
    try:
        if tool_name == "create_note":
            return await _create_note(args)
        elif tool_name == "list_notes":
            return await _list_notes()
        elif tool_name == "read_note":
            return await _read_note(args)
        elif tool_name == "save_note":
            return await _save_note(args)
        elif tool_name == "delete_note":
            return await _delete_note(args)
        elif tool_name == "search_notes":
            return await _search_notes(args)
        elif tool_name == "create_schedule":
            return await _create_schedule(args)
        elif tool_name == "list_schedules":
            return await _list_schedules(args)
        elif tool_name == "delete_schedule":
            return await _delete_schedule(args)
        elif tool_name == "list_todos":
            return await _list_todos()
        elif tool_name == "summarize_text":
            return await _summarize_text(args)
        elif tool_name == "translate_text":
            return await _translate_text(args)
        elif tool_name == "create_folder":
            return await _create_folder(args)
        elif tool_name == "web_search":
            return await _web_search(args)
        elif tool_name == "smart_search_notes":
            return await _smart_search_notes(args, provider, api_key, model)
        elif tool_name == "organize_notes":
            return await _organize_notes(args, provider, api_key, model)
        elif tool_name == "move_note":
            return await _move_note(args)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error(f"Tool execution failed [{tool_name}]: {e}")
        return {"error": str(e)}


async def _create_note(args: dict) -> dict:
    """노트 생성"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    title = args.get("title", "")
    content = args.get("content", "")
    folder = args.get("folder", "")
    
    if not title:
        # 자동 생성: 현재 시간 기반
        title = f"새 노트 {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 파일 경로 생성
    filename = f"{title}.md"
    if folder:
        file_path = vault_path / folder / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        file_path = vault_path / filename
    
    if file_path.exists():
        return {"error": f"'{title}.md' 파일이 이미 존재합니다."}
    
    # 기본 내용 생성
    if not content:
        content = f"# {title}\n\n"
    
    file_path.write_text(content, encoding="utf-8")
    rel_path = str(file_path.relative_to(vault_path)).replace("\\", "/")
    
    return {
        "success": True,
        "path": rel_path,
        "message": f"노트 '{title}' 생성 완료"
    }


async def _list_notes() -> dict:
    """노트 목록 조회"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    notes = []
    
    for md_file in sorted(vault_path.rglob("*.md")):
        rel_path = str(md_file.relative_to(vault_path)).replace("\\", "/")
        if rel_path.startswith(".trash/") or "/.trash/" in rel_path:
            continue
        
        stat = md_file.stat()
        notes.append({
            "path": rel_path,
            "title": rel_path.replace(".md", ""),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        })
    
    return {
        "notes": notes,
        "count": len(notes),
        "message": f"총 {len(notes)}개의 노트"
    }


async def _read_note(args: dict) -> dict:
    """노트 읽기"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    path = args.get("path", "")
    if not path:
        return {"error": "노트 경로가 필요합니다."}
    
    file_path = vault_path / path
    if not file_path.exists():
        return {"error": f"'{path}' 파일을 찾을 수 없습니다."}
    
    content = file_path.read_text(encoding="utf-8")
    return {
        "path": path,
        "content": content[:5000],  # 챗봇용으로 앞부분만
        "full_length": len(content),
        "truncated": len(content) > 5000
    }


async def _save_note(args: dict) -> dict:
    """노트 저장"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    path = args.get("path", "")
    content = args.get("content", "")
    
    if not path:
        return {"error": "노트 경로가 필요합니다."}
    
    file_path = vault_path / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    
    return {
        "success": True,
        "path": path,
        "message": f"'{path}' 저장 완료"
    }


async def _delete_note(args: dict) -> dict:
    """노트 삭제 (휴지통으로)"""
    from .vault import get_current_vault_path, get_trash_path
    import shutil
    
    vault_path = get_current_vault_path()
    trash_path = get_trash_path()
    path = args.get("path", "")
    
    if not path:
        return {"error": "삭제할 노트 경로가 필요합니다."}
    
    file_path = vault_path / path
    if not file_path.exists():
        return {"error": f"'{path}' 파일을 찾을 수 없습니다."}
    
    trash_path.mkdir(parents=True, exist_ok=True)
    dest = trash_path / file_path.name
    shutil.move(str(file_path), str(dest))
    
    return {
        "success": True,
        "path": path,
        "message": f"'{path}' 파일이 휴지통으로 이동됨"
    }


async def _search_notes(args: dict) -> dict:
    """노트 검색"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    query = args.get("query", "").lower()
    if not query:
        return {"error": "검색어가 필요합니다."}
    
    results = []
    for md_file in vault_path.rglob("*.md"):
        rel_path = str(md_file.relative_to(vault_path)).replace("\\", "/")
        if rel_path.startswith(".trash/") or "/.trash/" in rel_path:
            continue
        
        title = rel_path.replace(".md", "")
        title_match = query in title.lower()
        
        content_match = False
        snippet = ""
        try:
            content = md_file.read_text(encoding="utf-8")
            idx = content.lower().find(query)
            if idx >= 0:
                content_match = True
                start = max(0, idx - 50)
                end = min(len(content), idx + len(query) + 50)
                snippet = "..." + content[start:end] + "..."
        except Exception:
            pass
        
        if title_match or content_match:
            results.append({
                "path": rel_path,
                "title": title,
                "match": "title" if title_match else "content",
                "snippet": snippet if content_match else ""
            })
    
    return {
        "results": results[:20],
        "count": len(results),
        "query": query,
        "message": f"'{query}' 검색 결과: {len(results)}건"
    }


async def _create_schedule(args: dict) -> dict:
    """일정 생성"""
    import uuid
    from ..db import get_conn
    
    title = args.get("title", "")
    schedule_date = args.get("date", "")
    
    if not title:
        return {"error": "일정 제목이 필요합니다."}
    if not schedule_date:
        schedule_date = date.today().isoformat()
    
    schedule_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    start_time = args.get("startTime", "")
    end_time = args.get("endTime", "")
    description = args.get("description", "")
    
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO schedules (id, title, description, date, start_time, end_time, color, completed, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (schedule_id, title, description, schedule_date, start_time, end_time, "#c9a76c", 0, now, now)
        )
        conn.commit()
    finally:
        conn.close()
    
    return {
        "success": True,
        "schedule_id": schedule_id,
        "title": title,
        "date": schedule_date,
        "startTime": start_time,
        "endTime": end_time,
        "message": f"일정 '{title}' ({schedule_date}) 생성 완료"
    }


async def _list_schedules(args: dict) -> dict:
    """일정 목록 조회"""
    from ..db import get_conn
    
    schedule_date = args.get("date", "")
    month = args.get("month", "")
    
    conn = get_conn()
    try:
        if schedule_date:
            rows = conn.execute(
                "SELECT * FROM schedules WHERE date = ? ORDER BY start_time", (schedule_date,)
            ).fetchall()
        elif month:
            rows = conn.execute(
                "SELECT * FROM schedules WHERE date LIKE ? ORDER BY date, start_time", (f"{month}%",)
            ).fetchall()
        else:
            today = date.today().isoformat()
            rows = conn.execute(
                "SELECT * FROM schedules WHERE date >= ? ORDER BY date, start_time LIMIT 50", (today,)
            ).fetchall()
    finally:
        conn.close()
    
    schedules = []
    for row in rows:
        schedules.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "date": row[3],
            "startTime": row[4],
            "endTime": row[5],
            "color": row[6],
            "completed": bool(row[7])
        })
    
    return {
        "schedules": schedules,
        "count": len(schedules),
        "message": f"{len(schedules)}건의 일정"
    }


async def _delete_schedule(args: dict) -> dict:
    """일정 삭제"""
    from ..db import get_conn
    
    schedule_id = args.get("schedule_id", "")
    if not schedule_id:
        return {"error": "삭제할 일정 ID가 필요합니다."}
    
    conn = get_conn()
    try:
        cursor = conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
        conn.commit()
    finally:
        conn.close()
    
    if cursor.rowcount == 0:
        return {"error": f"일정 '{schedule_id}'를 찾을 수 없습니다."}
    
    return {
        "success": True,
        "schedule_id": schedule_id,
        "message": "일정 삭제 완료"
    }


async def _list_todos() -> dict:
    """TODO 목록 조회"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    todo_pattern = re.compile(r"^\s*-\s*\[(?P<checked>[ xX])\]\s+(?P<text>.+)\s*$")
    
    todos = []
    for md_file in vault_path.rglob("*.md"):
        rel_path = str(md_file.relative_to(vault_path)).replace("\\", "/")
        if rel_path.startswith(".trash/") or "/.trash/" in rel_path:
            continue
        
        try:
            content = md_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.split("\n"), 1):
                m = todo_pattern.match(line)
                if m:
                    todos.append({
                        "text": m.group("text").strip(),
                        "checked": m.group("checked").strip().lower() == "x",
                        "notePath": rel_path,
                        "lineNo": i
                    })
        except Exception:
            pass
    
    unchecked = [t for t in todos if not t["checked"]]
    checked = [t for t in todos if t["checked"]]
    
    return {
        "todos": todos[:50],
        "total": len(todos),
        "unchecked": len(unchecked),
        "checked": len(checked),
        "message": f"TODO {len(todos)}개 (미완료: {len(unchecked)}, 완료: {len(checked)})"
    }


async def _summarize_text(args: dict) -> dict:
    """텍스트 요약 (동기 호출)"""
    content = args.get("content", "")
    if not content:
        return {"error": "요약할 텍스트가 필요합니다."}
    
    return {
        "content": content[:3000],
        "action": "summarize",
        "message": "텍스트를 요약합니다."
    }


async def _translate_text(args: dict) -> dict:
    """텍스트 번역 (동기 호출)"""
    content = args.get("content", "")
    target = args.get("target_language", "en")
    if not content:
        return {"error": "번역할 텍스트가 필요합니다."}
    
    return {
        "content": content[:3000],
        "target_language": target,
        "action": "translate",
        "message": f"텍스트를 {target}로 번역합니다."
    }


async def _create_folder(args: dict) -> dict:
    """폴더 생성"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    path = args.get("path", "")
    if not path:
        return {"error": "폴더 경로가 필요합니다."}
    
    folder_path = vault_path / path
    if folder_path.exists():
        return {"error": f"'{path}' 폴더가 이미 존재합니다."}
    
    folder_path.mkdir(parents=True, exist_ok=True)
    
    return {
        "success": True,
        "path": path,
        "message": f"폴더 '{path}' 생성 완료"
    }


async def _web_search(args: dict) -> dict:
    """웹 검색 (DuckDuckGo)"""
    if not HAS_DDGS:
        return {"error": "웹 검색 기능이 설치되지 않았습니다. (pip install duckduckgo-search)"}
    
    query = args.get("query", "")
    max_results = args.get("max_results", 5)
    if not query:
        return {"error": "검색어가 필요합니다."}
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")
            })
        
        # 검색 결과를 텍스트로도 정리
        text_summary = f"'{query}' 검색 결과:\n\n"
        for i, r in enumerate(formatted, 1):
            text_summary += f"{i}. **{r['title']}**\n   {r['snippet']}\n   🔗 {r['url']}\n\n"
        
        return {
            "results": formatted,
            "count": len(formatted),
            "query": query,
            "text_summary": text_summary,
            "message": f"'{query}' 검색 결과: {len(formatted)}건"
        }
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return {"error": f"검색 중 오류 발생: {str(e)}"}


async def _smart_search_notes(args: dict, provider: str = "", api_key: str = "", model: str = "") -> dict:
    """AI 기반 스마트 노트 검색"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    query = args.get("query", "")
    if not query:
        return {"error": "검색할 정보를 입력해주세요."}
    
    # 모든 노트 수집 (제목 + 내용 앞부분)
    notes_info = []
    for md_file in sorted(vault_path.rglob("*.md")):
        rel_path = str(md_file.relative_to(vault_path)).replace("\\", "/")
        if rel_path.startswith(".trash/") or "/.trash/" in rel_path:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")[:1000]
            notes_info.append({
                "path": rel_path,
                "title": rel_path.replace(".md", ""),
                "preview": content
            })
        except Exception:
            pass
    
    if not notes_info:
        return {"results": [], "count": 0, "message": "노트가 없습니다."}
    
    # LLM으로 관련 노트 찾기
    notes_text = ""
    for i, n in enumerate(notes_info[:30]):  # 최대 30개
        notes_text += f"\n[{i}] 경로: {n['path']}\n내용 미리보기: {n['preview'][:300]}\n---\n"
    
    search_prompt = f"""다음 노트 목록에서 \"{query}\" 정보가 포함된 노트를 찾아주세요.

{notes_text}

관련된 노트의 인덱스 번호를 JSON 배열로 응답하세요. 예: [0, 3, 5]
관련 노트가 없으면 빈 배열 []을 응답하세요.
인덱스 번호만 포함된 JSON 배열만 출력하세요."""
    
    try:
        llm_result = call_llm_text(search_prompt, provider, api_key, model)
        # JSON 배열 파싱
        match = re.search(r'\[([\d,\s]*)\]', llm_result)
        if match:
            indices = json.loads(f"[{match.group(1)}]")
            matched = []
            for idx in indices:
                if 0 <= idx < len(notes_info):
                    matched.append(notes_info[idx])
            return {
                "results": matched,
                "count": len(matched),
                "query": query,
                "message": f"'{query}' 관련 노트: {len(matched)}건"
            }
        else:
            return {"results": [], "count": 0, "query": query, "message": "관련 노트를 찾지 못했습니다."}
    except Exception as e:
        logger.error(f"Smart search failed: {e}")
        return {"error": f"스마트 검색 오류: {str(e)}"}


async def _organize_notes(args: dict, provider: str = "", api_key: str = "", model: str = "") -> dict:
    """AI 기반 노트 자동 정리"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    
    # 루트 레벨 노트만 수집 (이미 폴더에 있는 건 제외)
    root_notes = []
    for md_file in sorted(vault_path.glob("*.md")):
        rel_path = md_file.name
        try:
            content = md_file.read_text(encoding="utf-8")[:500]
            root_notes.append({
                "path": rel_path,
                "title": rel_path.replace(".md", ""),
                "preview": content
            })
        except Exception:
            pass
    
    if not root_notes:
        return {"message": "정리할 루트 레벨 노트가 없습니다.", "moved": []}
    
    # LLM으로 카테고리 분류
    notes_text = ""
    for i, n in enumerate(root_notes):
        notes_text += f"[{i}] {n['title']}: {n['preview'][:200]}\n"
    
    organize_prompt = f"""다음 노트들을 주제별 폴더로 분류해주세요.

{notes_text}

아래 JSON 형식으로만 응답하세요:
{{
  "categories": [
    {{
      "folder": "폴더명 (영문 kebab-case, 예: project-ideas)",
      "label": "폴더 한국어 이름",
      "notes": [0, 2, 5]
    }}
  ]
}}

규칙:
- 폴더명은 영문 kebab-case
- 분류하기 애매한 노트는 "misc" 폴더에
- JSON만 출력하세요"""
    
    try:
        llm_result = call_llm_text(organize_prompt, provider, api_key, model)
        
        # JSON 파싱
        json_match = re.search(r'\{.*"categories".*\}', llm_result, re.DOTALL)
        if not json_match:
            return {"error": "분류 결과를 파싱할 수 없습니다.", "raw": llm_result[:300]}
        
        parsed = json.loads(json_match.group(0))
        categories = parsed.get("categories", [])
        
        moved = []
        for cat in categories:
            folder = cat.get("folder", "misc")
            label = cat.get("label", folder)
            note_indices = cat.get("notes", [])
            
            folder_path = vault_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            for idx in note_indices:
                if 0 <= idx < len(root_notes):
                    note = root_notes[idx]
                    src = vault_path / note["path"]
                    dst = folder_path / note["path"]
                    if src.exists() and not dst.exists():
                        shutil.move(str(src), str(dst))
                        moved.append({"note": note["title"], "folder": folder, "label": label})
        
        return {
            "success": True,
            "moved": moved,
            "count": len(moved),
            "message": f"{len(moved)}개 노트를 폴더별로 정리했습니다."
        }
    except json.JSONDecodeError:
        return {"error": "LLM 분류 결과 파싱 실패"}
    except Exception as e:
        logger.error(f"Organize notes failed: {e}")
        return {"error": f"정리 오류: {str(e)}"}


async def _move_note(args: dict) -> dict:
    """노트 이동"""
    from .vault import get_current_vault_path
    
    vault_path = get_current_vault_path()
    path = args.get("path", "")
    destination = args.get("destination", "")
    
    if not path:
        return {"error": "이동할 노트 경로가 필요합니다."}
    if not destination:
        return {"error": "대상 폴더 경로가 필요합니다."}
    
    src = vault_path / path
    if not src.exists():
        return {"error": f"'{path}' 파일을 찾을 수 없습니다."}
    
    dest_folder = vault_path / destination
    dest_folder.mkdir(parents=True, exist_ok=True)
    dst = dest_folder / src.name
    
    if dst.exists():
        return {"error": f"대상 위치에 '{src.name}' 파일이 이미 존재합니다."}
    
    shutil.move(str(src), str(dst))
    new_path = str(dst.relative_to(vault_path)).replace("\\", "/")
    
    return {
        "success": True,
        "original_path": path,
        "new_path": new_path,
        "message": f"'{path}' → '{new_path}' 이동 완료"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 프롬프트 생성
# ─────────────────────────────────────────────────────────────────────────────

def build_tool_descriptions() -> str:
    """도구 설명을 문자열로 변환"""
    lines = []
    for tool in CUENOTE_TOOLS:
        params = tool.get("parameters", {})
        param_desc = ""
        if params:
            param_parts = []
            for pname, pinfo in params.items():
                req = " (필수)" if pinfo.get("required") else " (선택)"
                param_parts.append(f"    - {pname}: {pinfo['description']}{req}")
            param_desc = "\n" + "\n".join(param_parts)
        lines.append(f"  - {tool['name']}: {tool['description']}{param_desc}")
    return "\n".join(lines)


def build_chat_prompt(
    user_message: str,
    history: list[ChatMessage],
    today: str,
    active_note_path: str = "",
    active_note_content: str = "",
) -> str:
    """챗봇 시스템 프롬프트 생성"""
    tools_desc = build_tool_descriptions()
    
    # 대화 히스토리 포맷 (더 명확하게)
    history_block = ""
    last_assistant_content = ""
    if history:
        hist_lines = []
        for msg in history[-10:]:
            if msg.role == "user":
                hist_lines.append(f"[사용자]: {msg.content}")
            elif msg.role == "assistant":
                content = msg.content
                if len(content) > 2000:
                    content = content[:2000] + "\n... (이하 생략)"
                hist_lines.append(f"[어시스턴트]: {content}")
                last_assistant_content = msg.content
        history_block = "\n\n".join(hist_lines)
    
    # 마지막 어시스턴트 응답이 있으면 명시적으로 표시
    context_hint = ""
    if last_assistant_content:
        truncated = last_assistant_content[:3000]
        if len(last_assistant_content) > 3000:
            truncated += "\n... (이하 생략)"
        context_hint = f"""

## 직전 어시스턴트 응답 (가장 최근에 내가 답변한 내용):
\"\"\"
{truncated}
\"\"\"
"""
    
    # 현재 노트 컨텍스트
    active_note_section = ""
    if active_note_path:
        note_title = active_note_path.replace(".md", "")
        note_preview = ""
        if active_note_content:
            note_preview = active_note_content[:3000]
            if len(active_note_content) > 3000:
                note_preview += "\n... (이하 생략)"
        active_note_section = f"""

## 현재 사용자가 보고 있는 노트:
파일경로: {active_note_path}
제목: {note_title}
내용:
\"\"\"
{note_preview}
\"\"\"
"""
    
    return f"""당신은 CueNote 노트 앱의 AI 어시스턴트입니다.
사용자의 요청에 따라 앱 기능을 실행하고, 친절하게 결과를 안내합니다.

오늘 날짜: {today}

사용 가능한 도구:
{tools_desc}

## 매우 중요한 응답 규칙:

### 도구 호출 규칙:
1. 도구를 실행해야 하면 반드시 아래 JSON 형식 **만** 출력하세요 (다른 텍스트 없이):
   {{"tool_call": {{"name": "도구이름", "arguments": {{"param": "value"}}}}}}
2. 도구가 필요 없는 일반 대화라면, 자연어로 직접 응답하세요.
3. 하나의 요청에 하나의 tool_call만 사용하세요.

### 현재 노트 관련 규칙 (매우 중요!):
4. 사용자가 "이 글", "이 노트", "현재 노트", "지금 보고 있는 글" 등으로 현재 노트를 참조하면,
   반드시 "현재 사용자가 보고 있는 노트" 섹션의 내용을 사용하세요.
5. "이 글이 무슨 내용이야?" → read_note를 호출하지 말고, 프롬프트에 이미 포함된 노트 내용을 읽고 자연어로 직접 설명하세요.
6. "이 글 요약해줘" → 프롬프트에 포함된 노트의 **실제 텍스트 전체**를 summarize_text의 content에 넣으세요. 절대 "[현재 노트 내용]" 같은 플레이스홀더를 쓰지 마세요.
7. "이 글 번역해줘" → 프롬프트에 포함된 노트의 **실제 텍스트 전체**를 translate_text의 content에 넣으세요.
8. "이 글 개선해줘 / 수정해줘" → 노트 내용을 개선하여 save_note(path=현재경로, content=개선된내용)로 저장
9. 중요: read_note 도구를 사용하지 마세요 — 현재 노트 내용은 이미 프롬프트에 포함되어 있습니다!

### 대화 맥락 규칙:
9. 사용자가 "이 내용", "위 내용", "이걸", "그거", "방금 말한 것" 등으로 이전 대화를 참조하면,
   "직전 어시스턴트 응답"의 내용을 사용하세요.

### 기타 규칙:
10. 한국어로 응답하세요 (사용자가 영어로 말하면 영어로).
11. 날짜가 필요한 경우, 오늘 날짜({today}) 기준으로 판단하세요.
12. 사용자가 도구 실행을 요청하면 절대 되묻지 말고 바로 tool_call JSON을 출력하세요.
{active_note_section}{context_hint}
{f"## 이전 대화 기록:{chr(10)}{history_block}" if history_block else ""}

[사용자]: {user_message}

[어시스턴트]:"""



def build_result_prompt(
    user_message: str,
    tool_name: str,
    tool_result: dict,
    history: list[ChatMessage],
) -> str:
    """도구 실행 결과를 바탕으로 자연어 응답 생성"""
    result_json = json.dumps(tool_result, ensure_ascii=False, indent=2)
    
    return f"""당신은 CueNote 노트 앱의 AI 어시스턴트입니다.
사용자의 요청에 대해 도구를 실행한 결과입니다. 이 결과를 바탕으로 친절하고 자연스러운 응답을 생성하세요.

사용자 요청: {user_message}
실행된 도구: {tool_name}
실행 결과:
{result_json}

## 응답 규칙:
1. 도구 실행 결과를 사용자가 이해하기 쉽게 자연어로 설명하세요.
2. 한국어로 응답하세요.
3. 결과가 목록이면 보기 좋게 정리해 주세요.
4. 에러가 발생한 경우, 원인과 해결 방법을 안내하세요.
5. 간결하고 친절하게 응답하세요.
6. 마크다운 포맷을 사용하면 더 보기 좋습니다.

응답:"""


def build_continuation_prompt(
    user_message: str,
    tool_history: list[dict],
    today: str
) -> str:
    """멀티스텝 도구 호출을 위한 연속 프롬프트"""
    tools_desc = build_tool_descriptions()
    
    history_text = ""
    for i, th in enumerate(tool_history, 1):
        result_str = json.dumps(th["result"], ensure_ascii=False)
        if len(result_str) > 1000:
            result_str = result_str[:1000] + "..."
        history_text += f"\n단계 {i}: {th['name']}({json.dumps(th['args'], ensure_ascii=False)})\n결과: {result_str}\n"
    
    return f"""당신은 CueNote 노트 앱의 AI 어시스턴트입니다.
사용자의 원래 요청을 완전히 수행하기 위해, 추가 도구 호출이 필요한지 판단하세요.

오늘 날짜: {today}

사용 가능한 도구:
{tools_desc}

## 사용자 원래 요청:
{user_message}

## 이미 실행된 도구:
{history_text}

## 판단 규칙:
1. 사용자의 요청이 아직 완전히 수행되지 않았다면, 다음에 실행할 도구를 JSON 형식으로 응답하세요:
   {{"tool_call": {{"name": "도구이름", "arguments": {{"param": "value"}}}}}}
2. 사용자의 요청이 이미 완전히 수행되었다면, "완료" 라고만 응답하세요.
3. 예시: "XX를 검색해서 노트를 만들어줘" → web_search 후 → 그 결과로 create_note 도구 호출
4. 이전 단계의 결과 데이터를 활용하여 다음 도구의 arguments를 채우세요.

응답:"""


def build_multistep_result_prompt(
    user_message: str,
    tool_history: list[dict],
    history: list[ChatMessage],
) -> str:
    """멀티스텝 도구 실행 결과를 바탕으로 자연어 응답 생성"""
    steps_text = ""
    for i, th in enumerate(tool_history, 1):
        result_str = json.dumps(th["result"], ensure_ascii=False, indent=2)
        if len(result_str) > 2000:
            result_str = result_str[:2000] + "\n... (truncated)"
        steps_text += f"\n### 단계 {i}: {th['name']}\n인자: {json.dumps(th['args'], ensure_ascii=False)}\n결과:\n{result_str}\n"
    
    return f"""당신은 CueNote 노트 앱의 AI 어시스턴트입니다.
사용자의 요청에 대해 도구를 실행한 결과입니다. 이 결과를 바탕으로 친절하고 자연스러운 응답을 생성하세요.

사용자 요청: {user_message}

## 실행된 도구들:
{steps_text}

## 응답 규칙:
1. 모든 도구 실행 결과를 종합하여 사용자가 이해하기 쉽게 자연어로 설명하세요.
2. 한국어로 응답하세요.
3. 결과가 목록이면 보기 좋게 정리해 주세요.
4. 에러가 발생한 경우, 원인과 해결 방법을 안내하세요.
5. 간결하고 친절하게 응답하세요.
6. 마크다운 포맷을 사용하면 더 보기 좋습니다.

응답:"""


# ─────────────────────────────────────────────────────────────────────────────
# LLM 호출
# ─────────────────────────────────────────────────────────────────────────────

def call_llm_text(prompt: str, provider: str, api_key: str, model: str) -> str:
    """LLM으로 텍스트 생성 (동기)"""
    model_or_none = model if model else None
    
    if provider == "gemini" and api_key:
        return gemini_client.generate(prompt, api_key, model_or_none)
    elif provider == "openai" and api_key:
        return openai_client.generate(prompt, api_key, model_or_none)
    elif provider == "anthropic" and api_key:
        return anthropic_client.generate(prompt, api_key, model_or_none)
    else:
        return ollama_client.generate(prompt, model=model_or_none)


def get_stream_func(prompt: str, provider: str, api_key: str, model: str):
    """LLM 스트리밍 함수 반환"""
    model_or_none = model if model else None
    
    if provider == "gemini" and api_key:
        return gemini_client.stream_generate(prompt, api_key, model_or_none)
    elif provider == "openai" and api_key:
        return openai_client.stream_generate(prompt, api_key, model_or_none)
    elif provider == "anthropic" and api_key:
        return anthropic_client.stream_generate(prompt, api_key, model_or_none)
    else:
        return ollama_client.stream_generate(prompt, model_or_none)


def parse_tool_call(text: str) -> Optional[dict]:
    """LLM 응답에서 tool_call JSON을 파싱 (강건한 버전)"""
    if "tool_call" not in text:
        return None
    
    try:
        # 1) 전체 텍스트가 JSON인 경우
        stripped = text.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            parsed = json.loads(stripped)
            if "tool_call" in parsed:
                return parsed["tool_call"]
        
        # 2) ```json ... ``` 패턴
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                if "tool_call" in parsed:
                    return parsed["tool_call"]
            except json.JSONDecodeError:
                pass
        
        # 3) 중첩 괄호 처리 — "tool_call" 키워드를 포함하는 최외곽 { } 추출
        #    다양한 시작 패턴 매칭 (공백, 줄바꿈 허용)
        for pattern in [r'\{\s*"tool_call"', r"\{\s*'tool_call'"]:
            match = re.search(pattern, text)
            if match:
                brace_start = match.start()
                depth = 0
                for i in range(brace_start, len(text)):
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                        if depth == 0:
                            candidate = text[brace_start:i+1]
                            try:
                                parsed = json.loads(candidate)
                                if "tool_call" in parsed:
                                    return parsed["tool_call"]
                            except json.JSONDecodeError:
                                # 작은따옴표를 큰따옴표로 치환 후 재시도
                                try:
                                    fixed = candidate.replace("'", '"')
                                    parsed = json.loads(fixed)
                                    if "tool_call" in parsed:
                                        return parsed["tool_call"]
                                except json.JSONDecodeError:
                                    pass
                            break
        
        # 4) 마지막 수단: 텍스트에서 JSON-like 블록 추출 시도
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace >= 0 and last_brace > first_brace:
            candidate = text[first_brace:last_brace+1]
            try:
                parsed = json.loads(candidate)
                if "tool_call" in parsed:
                    return parsed["tool_call"]
            except json.JSONDecodeError:
                pass
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.debug(f"parse_tool_call error: {e}")
    
    return None


# ─────────────────────────────────────────────────────────────────────────────
# API 엔드포인트
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(payload: ChatPayload):
    """
    AI 챗봇 대화 (SSE 스트리밍)
    
    Flow:
    1. 사용자 메시지 분석 → 도구 호출 여부 판단
    2. 도구 실행이 필요하면 → 도구 실행 → 결과 기반 응답 스트리밍
    3. 일반 대화면 → 직접 응답 스트리밍
    """
    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
    
    provider = payload.provider
    api_key = payload.api_key
    model = payload.model
    history = payload.history
    today = date.today().isoformat()
    
    async def event_generator():
        try:
            # 1단계: LLM에게 도구 사용 여부 판단
            chat_prompt = build_chat_prompt(
                user_message, history, today,
                active_note_path=payload.active_note_path,
                active_note_content=payload.active_note_content,
            )
            
            yield {"event": "thinking", "data": "메시지를 분석하고 있습니다..."}
            
            # 동기 호출로 도구 판단
            llm_response = call_llm_text(chat_prompt, provider, api_key, model)
            logger.info(f"Chatbot LLM response: {llm_response[:200]}")
            
            # 2단계: tool_call 파싱
            tool_call_data = parse_tool_call(llm_response)
            
            if tool_call_data:
                # ─── 멀티스텝 도구 실행 루프 (최대 3단계) ───
                tool_history = []  # 실행된 도구들의 기록
                MAX_STEPS = 3
                
                for step in range(MAX_STEPS):
                    tool_name = tool_call_data.get("name", "")
                    tool_args = tool_call_data.get("arguments", {})
                    
                    logger.info(f"Chatbot tool call [{step+1}]: {tool_name}({tool_args})")
                    
                    # 도구 호출 정보 전송
                    yield {
                        "event": "tool_call",
                        "data": json.dumps({
                            "name": tool_name,
                            "arguments": tool_args
                        }, ensure_ascii=False)
                    }
                    
                    # 도구 실행
                    tool_result = await execute_tool(
                        tool_name, tool_args, provider, api_key, model
                    )
                    
                    yield {
                        "event": "tool_result",
                        "data": json.dumps(tool_result, ensure_ascii=False)
                    }
                    
                    tool_history.append({
                        "name": tool_name,
                        "args": tool_args,
                        "result": tool_result
                    })
                    
                    # 다음 단계 판단: LLM에게 추가 도구 호출이 필요한지 확인
                    if step < MAX_STEPS - 1:
                        continuation_prompt = build_continuation_prompt(
                            user_message, tool_history, today
                        )
                        cont_response = call_llm_text(continuation_prompt, provider, api_key, model)
                        logger.info(f"Chatbot continuation [{step+1}]: {cont_response[:150]}")
                        
                        next_tool = parse_tool_call(cont_response)
                        if next_tool:
                            tool_call_data = next_tool
                            yield {"event": "thinking", "data": "추가 작업을 수행합니다..."}
                        else:
                            break
                    else:
                        break
                
                # 최종 결과 기반 자연어 응답 (스트리밍)
                result_prompt = build_multistep_result_prompt(
                    user_message, tool_history, history
                )
                
                stream_func = get_stream_func(result_prompt, provider, api_key, model)
                async for chunk in stream_func:
                    escaped_chunk = chunk.replace('\n', '\\n')
                    yield {"event": "message", "data": escaped_chunk}
            else:
                # 도구 호출 없이 직접 응답 — 이미 생성된 텍스트를 그대로 스트리밍
                logger.info("Chatbot: no tool call, streaming existing response")
                
                chunk_size = 8
                for i in range(0, len(llm_response), chunk_size):
                    chunk = llm_response[i:i + chunk_size]
                    escaped_chunk = chunk.replace('\n', '\\n')
                    yield {"event": "message", "data": escaped_chunk}
            
            yield {"event": "done", "data": ""}
            
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            yield {"event": "error", "data": str(e)}
    
    return EventSourceResponse(event_generator())
