"""
CueNote Core - MCP (Model Context Protocol) 클라이언트 매니저

MCP 서버들을 관리하고, 도구를 검색/실행하는 기능을 제공합니다.
설정은 로컬 JSON 파일에 저장됩니다.
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from .config import logger, PROJECT_ROOT

# MCP 설정 파일 경로
MCP_CONFIG_PATH = PROJECT_ROOT / "mcp_servers.json"


# ─────────────────────────────────────────────────────────────────────────────
# 설정 관리
# ─────────────────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    """MCP 서버 설정을 로드합니다."""
    if MCP_CONFIG_PATH.exists():
        try:
            with open(MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load MCP config: %s", e)
    return {"servers": {}}


def _save_config(config: dict) -> None:
    """MCP 서버 설정을 저장합니다."""
    try:
        with open(MCP_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logger.error("Failed to save MCP config: %s", e)


def get_servers() -> dict:
    """등록된 모든 MCP 서버 목록을 반환합니다."""
    config = _load_config()
    return config.get("servers", {})


def add_server(
    server_id: str,
    command: str,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    enabled: bool = True,
    description: str = "",
) -> dict:
    """MCP 서버를 추가합니다."""
    config = _load_config()
    config.setdefault("servers", {})
    config["servers"][server_id] = {
        "command": command,
        "args": args or [],
        "env": env or {},
        "enabled": enabled,
        "description": description,
    }
    _save_config(config)
    return config["servers"][server_id]


def update_server(server_id: str, updates: dict) -> dict | None:
    """MCP 서버 설정을 업데이트합니다."""
    config = _load_config()
    servers = config.get("servers", {})
    if server_id not in servers:
        return None
    servers[server_id].update(updates)
    _save_config(config)
    return servers[server_id]


def remove_server(server_id: str) -> bool:
    """MCP 서버를 삭제합니다."""
    config = _load_config()
    servers = config.get("servers", {})
    if server_id in servers:
        del servers[server_id]
        _save_config(config)
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# MCP 서버 실행 & 도구 관리
# ─────────────────────────────────────────────────────────────────────────────

# 실행 중인 프로세스 캐시
_running_processes: dict[str, subprocess.Popen] = {}
_server_tools: dict[str, list[dict]] = {}


async def _communicate_jsonrpc(
    process: subprocess.Popen,
    method: str,
    params: dict | None = None,
    request_id: int = 1,
    timeout: float = 30.0,
) -> dict | None:
    """MCP 서버에 JSON-RPC 메시지를 전송하고 응답을 받습니다. (newline-delimited JSON)"""
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params:
        request["params"] = params

    message = json.dumps(request) + "\n"

    try:
        if process.stdin is None or process.stdout is None:
            return None

        loop = asyncio.get_event_loop()

        # 비동기로 stdin에 쓰기
        await loop.run_in_executor(
            None,
            lambda: (process.stdin.write(message.encode("utf-8")), process.stdin.flush()),
        )

        # 비동기로 응답 읽기 (한 줄 읽기)
        response_data = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: _read_jsonrpc_response(process)),
            timeout=timeout,
        )
        return response_data

    except asyncio.TimeoutError:
        logger.warning("MCP server communication timed out")
        return None
    except Exception as e:
        logger.error("MCP communication error: %s", e)
        return None


def _read_jsonrpc_response(process: subprocess.Popen) -> dict | None:
    """JSON-RPC 응답을 읽습니다 (newline-delimited JSON)."""
    if process.stdout is None:
        return None

    try:
        line = process.stdout.readline().decode("utf-8").strip()
        if not line:
            return None
        return json.loads(line)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse MCP response: %s", e)
        return None


async def start_server(server_id: str) -> bool:
    """MCP 서버 프로세스를 시작합니다."""
    servers = get_servers()
    server_config = servers.get(server_id)
    if not server_config or not server_config.get("enabled", True):
        return False

    # 이미 실행 중이면 중지 후 재시작
    if server_id in _running_processes:
        await stop_server(server_id)

    command = server_config["command"]
    args = server_config.get("args", [])
    env_vars = server_config.get("env", {})

    # 환경 변수 설정
    env = os.environ.copy()
    env.update(env_vars)

    try:
        # Windows에서 npx, uvx 등은 .cmd 파일이므로 shutil.which로 전체 경로 검색
        resolved_command = shutil.which(command)
        if resolved_command is None:
            logger.error("MCP server command not found in PATH: %s", command)
            return False

        cmd = [resolved_command] + args

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        _running_processes[server_id] = process

        # 초기화 (MCP initialize 핸드셰이크)
        init_response = await _communicate_jsonrpc(
            process,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "CueNote", "version": "1.0.0"},
            },
        )

        if init_response and "result" in init_response:
            # initialized 알림 (newline-delimited)
            notify_msg = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            process.stdin.write(notify_msg.encode("utf-8"))
            process.stdin.flush()

            # 도구 목록 가져오기
            tools_response = await _communicate_jsonrpc(process, "tools/list", request_id=2)
            if tools_response and "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                _server_tools[server_id] = [
                    {
                        "name": t.get("name", ""),
                        "description": t.get("description", ""),
                        "inputSchema": t.get("inputSchema", {}),
                    }
                    for t in tools
                ]
                logger.info(
                    "MCP server '%s' started with %d tools", server_id, len(tools)
                )
                return True

        # 초기화 실패
        logger.error("MCP server '%s' failed to initialize", server_id)
        await stop_server(server_id)
        return False

    except FileNotFoundError:
        logger.error("MCP server command not found: %s", command)
        return False
    except Exception as e:
        logger.error("Failed to start MCP server '%s': %s", server_id, e)
        return False


async def stop_server(server_id: str) -> None:
    """MCP 서버 프로세스를 중지합니다."""
    process = _running_processes.pop(server_id, None)
    _server_tools.pop(server_id, None)
    if process:
        try:
            process.terminate()
            process.wait(timeout=5)
        except Exception:
            process.kill()
        logger.info("MCP server '%s' stopped", server_id)


async def stop_all() -> None:
    """모든 MCP 서버를 중지합니다."""
    server_ids = list(_running_processes.keys())
    for sid in server_ids:
        await stop_server(sid)


def get_running_servers() -> list[str]:
    """실행 중인 서버 ID 목록을 반환합니다."""
    # 종료된 프로세스 정리
    dead = [
        sid for sid, proc in _running_processes.items() if proc.poll() is not None
    ]
    for sid in dead:
        _running_processes.pop(sid, None)
        _server_tools.pop(sid, None)
    return list(_running_processes.keys())


def get_all_tools() -> list[dict]:
    """실행 중인 모든 MCP 서버의 도구를 반환합니다."""
    all_tools = []
    for server_id, tools in _server_tools.items():
        if server_id in _running_processes:
            for tool in tools:
                all_tools.append({**tool, "server_id": server_id})
    return all_tools


def get_server_tools(server_id: str) -> list[dict]:
    """특정 MCP 서버의 도구를 반환합니다."""
    return _server_tools.get(server_id, [])


async def call_tool(server_id: str, tool_name: str, arguments: dict) -> Any:
    """MCP 서버의 도구를 호출합니다."""
    process = _running_processes.get(server_id)
    if not process:
        raise RuntimeError(f"MCP server '{server_id}' is not running")

    response = await _communicate_jsonrpc(
        process,
        "tools/call",
        {"name": tool_name, "arguments": arguments},
        request_id=100,
        timeout=30.0,
    )

    if response is None:
        raise RuntimeError(f"No response from MCP server '{server_id}'")

    if "error" in response:
        error = response["error"]
        raise RuntimeError(
            f"MCP tool error: {error.get('message', 'Unknown error')}"
        )

    result = response.get("result", {})
    # content 배열에서 텍스트 추출
    content_items = result.get("content", [])
    texts = []
    for item in content_items:
        if item.get("type") == "text":
            texts.append(item.get("text", ""))
    return "\n".join(texts) if texts else json.dumps(result)
