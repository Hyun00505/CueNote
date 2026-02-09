"""
CueNote Core - MCP 라우터
MCP 서버 관리 및 도구 실행 API
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import mcp_client

router = APIRouter(prefix="/mcp", tags=["mcp"])


# ─────────────────────────────────────────────────────────────────────────────
# 스키마
# ─────────────────────────────────────────────────────────────────────────────

class MCPServerConfig(BaseModel):
    """MCP 서버 추가/수정 페이로드"""
    command: str = Field(..., description="실행 명령어 (예: npx, uvx, node)")
    args: list[str] = Field(default_factory=list, description="명령어 인수")
    env: dict[str, str] = Field(default_factory=dict, description="환경 변수")
    enabled: bool = Field(default=True, description="활성화 여부")
    description: str = Field(default="", description="서버 설명")


class MCPToolCallPayload(BaseModel):
    """MCP 도구 호출 페이로드"""
    server_id: str = Field(..., description="서버 ID")
    tool_name: str = Field(..., description="도구 이름")
    arguments: dict = Field(default_factory=dict, description="도구 인수")


# ─────────────────────────────────────────────────────────────────────────────
# 서버 관리 API
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/servers")
async def list_servers():
    """등록된 모든 MCP 서버 목록을 반환합니다."""
    servers = mcp_client.get_servers()
    running = mcp_client.get_running_servers()
    result = {}
    for sid, config in servers.items():
        result[sid] = {
            **config,
            "status": "running" if sid in running else "stopped",
            "tools": mcp_client.get_server_tools(sid) if sid in running else [],
        }
    return {"servers": result}


@router.post("/servers/{server_id}")
async def add_or_update_server(server_id: str, config: MCPServerConfig):
    """MCP 서버를 추가 또는 업데이트합니다."""
    existing = mcp_client.get_servers()
    if server_id in existing:
        updated = mcp_client.update_server(server_id, config.model_dump())
        return {"message": f"Server '{server_id}' updated", "server": updated}
    else:
        server = mcp_client.add_server(
            server_id=server_id,
            command=config.command,
            args=config.args,
            env=config.env,
            enabled=config.enabled,
            description=config.description,
        )
        return {"message": f"Server '{server_id}' added", "server": server}


@router.delete("/servers/{server_id}")
async def delete_server(server_id: str):
    """MCP 서버를 삭제합니다."""
    # 실행 중이면 먼저 중지
    if server_id in mcp_client.get_running_servers():
        await mcp_client.stop_server(server_id)

    if mcp_client.remove_server(server_id):
        return {"message": f"Server '{server_id}' deleted"}
    raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found")


# ─────────────────────────────────────────────────────────────────────────────
# 서버 시작/중지
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/servers/{server_id}/start")
async def start_server(server_id: str):
    """MCP 서버를 시작합니다."""
    servers = mcp_client.get_servers()
    if server_id not in servers:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found")

    success = await mcp_client.start_server(server_id)
    if success:
        tools = mcp_client.get_server_tools(server_id)
        return {
            "message": f"Server '{server_id}' started",
            "tools": tools,
        }
    raise HTTPException(
        status_code=500,
        detail=f"Failed to start server '{server_id}'. Check command and configuration.",
    )


@router.post("/servers/{server_id}/stop")
async def stop_server(server_id: str):
    """MCP 서버를 중지합니다."""
    if server_id not in mcp_client.get_running_servers():
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' is not running")

    await mcp_client.stop_server(server_id)
    return {"message": f"Server '{server_id}' stopped"}


# ─────────────────────────────────────────────────────────────────────────────
# 도구 관리 & 실행
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/tools")
async def list_all_tools():
    """실행 중인 모든 MCP 서버의 도구를 반환합니다."""
    tools = mcp_client.get_all_tools()
    return {"tools": tools, "count": len(tools)}


@router.post("/tools/call")
async def call_tool(payload: MCPToolCallPayload):
    """MCP 도구를 호출합니다."""
    try:
        result = await mcp_client.call_tool(
            payload.server_id, payload.tool_name, payload.arguments
        )
        return {"result": result}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool call failed: {str(e)}")
