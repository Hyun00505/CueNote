"""
CueNote Core - MCP Integration Helper
AI 기능에서 MCP 도구를 자동 활용하는 헬퍼 모듈
"""
from typing import Optional
from ..config import logger
from .. import mcp_client


def get_available_mcp_tools() -> list[dict]:
    """실행 중인 MCP 서버의 모든 도구 목록을 반환"""
    return mcp_client.get_all_tools()


def is_server_running(server_id: str) -> bool:
    """특정 MCP 서버가 실행 중인지 확인"""
    return server_id in mcp_client.get_running_servers()


async def enhance_with_sequential_thinking(
    content: str,
    task_description: str = "Analyze and structure the following content",
) -> Optional[dict]:
    """
    Sequential Thinking MCP 서버를 사용하여 콘텐츠 분석 강화.
    서버가 실행 중이지 않으면 None 반환.
    """
    if not is_server_running("sequential-thinking"):
        return None

    try:
        result = await mcp_client.call_tool(
            "sequential-thinking",
            "sequentialthinking",
            {
                "thought": f"{task_description}: {content[:500]}",
                "nextThoughtNeeded": False,
                "thoughtNumber": 1,
                "totalThoughts": 1,
            },
        )
        logger.info("Sequential thinking MCP tool used successfully")
        return result
    except Exception as e:
        logger.warning("Sequential thinking MCP call failed: %s", e)
        return None


async def store_to_memory(
    entities: list[dict],
) -> Optional[dict]:
    """
    Memory MCP 서버에 엔티티를 저장.
    entities: [{"name": "...", "entityType": "...", "observations": ["..."]}]
    """
    if not is_server_running("memory"):
        return None

    try:
        result = await mcp_client.call_tool(
            "memory",
            "create_entities",
            {"entities": entities},
        )
        logger.info("Memory MCP tool used: stored %d entities", len(entities))
        return result
    except Exception as e:
        logger.warning("Memory MCP call failed: %s", e)
        return None


async def search_memory(query: str) -> Optional[dict]:
    """Memory MCP 서버에서 관련 정보 검색"""
    if not is_server_running("memory"):
        return None

    try:
        result = await mcp_client.call_tool(
            "memory",
            "search_nodes",
            {"query": query},
        )
        logger.info("Memory MCP search used for: %s", query[:50])
        return result
    except Exception as e:
        logger.warning("Memory MCP search failed: %s", e)
        return None


async def try_mcp_enhance(content: str, action: str) -> dict:
    """
    AI 기능 호출 시 MCP 도구 활용을 시도.
    Returns: {"mcp_used": [...], "context": "추가 컨텍스트", "memory_stored": bool}
    """
    mcp_used: list[dict] = []
    extra_context = ""
    memory_stored = False

    # 1) sequential-thinking으로 분석 강화 (요약, 확장 시)
    if action in ("summarize", "expand", "custom"):
        thinking_result = await enhance_with_sequential_thinking(
            content,
            f"Analyze this content for {action}",
        )
        if thinking_result:
            mcp_used.append({
                "server": "sequential-thinking",
                "tool": "sequentialthinking",
                "status": "success",
            })
            # thinking 결과에서 유용한 컨텍스트 추출
            if isinstance(thinking_result, dict):
                extra_context = str(thinking_result.get("content", [{}]))

    # 2) memory에서 관련 정보 검색 (요약, 번역 시)
    if action in ("summarize", "custom"):
        memory_result = await search_memory(content[:200])
        if memory_result:
            mcp_used.append({
                "server": "memory",
                "tool": "search_nodes",
                "status": "success",
            })

    # 3) 요약 결과를 memory에 저장
    if action == "summarize":
        store_result = await store_to_memory([{
            "name": f"Note Summary ({content[:30].strip()}...)",
            "entityType": "NoteSummary",
            "observations": [f"Content preview: {content[:200]}"],
        }])
        if store_result:
            memory_stored = True
            mcp_used.append({
                "server": "memory",
                "tool": "create_entities",
                "status": "success",
            })

    return {
        "mcp_used": mcp_used,
        "context": extra_context,
        "memory_stored": memory_stored,
    }
