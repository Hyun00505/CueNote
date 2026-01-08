"""
CueNote Core - TODO 라우터
TODO 조회 및 오늘의 계획 생성
"""
import json
from typing import Optional

from fastapi import APIRouter, Query

from ..config import logger
from ..db import get_conn
from ..ollama_client import call_json, OLLAMA_MODEL_PLAN
from ..schemas import TodoItem

router = APIRouter(tags=["todos"])


@router.get("/todos")
async def get_todos(checked: Optional[bool] = Query(default=None)):
    """TODO 항목을 조회합니다."""
    conn = get_conn()
    try:
        if checked is None:
            rows = conn.execute(
                """
                SELECT id, note_path, line_no, text, checked
                FROM todos
                ORDER BY updated_at DESC
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, note_path, line_no, text, checked
                FROM todos
                WHERE checked = ?
                ORDER BY updated_at DESC
                """,
                (1 if checked else 0,),
            ).fetchall()
    finally:
        conn.close()

    todos = [
        TodoItem(
            id=row[0],
            notePath=row[1],
            lineNo=row[2],
            text=row[3],
            checked=bool(row[4]),
        )
        for row in rows
    ]
    return {"todos": [todo.dict() for todo in todos]}


@router.post("/ai/today-plan")
async def today_plan():
    """AI를 사용하여 오늘의 계획을 생성합니다."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, note_path, line_no, text, checked
            FROM todos
            WHERE checked = 0
            ORDER BY updated_at DESC
            LIMIT 50
            """
        ).fetchall()
    finally:
        conn.close()

    todos = [
        {
            "id": row[0],
            "notePath": row[1],
            "lineNo": row[2],
            "text": row[3],
            "checked": bool(row[4]),
        }
        for row in rows
    ]

    prompt = (
        "You are generating a daily plan. Output MUST be JSON only and match the schema.\n"
        "Rules:\n"
        "- overdue: up to 5 most important items\n"
        "- dueSoon: next 5 items\n"
        "- nextActions and quickWins are strings informed by remaining items\n\n"
        f"Todos JSON:\n{json.dumps(todos, ensure_ascii=True)}\n\n"
        "Schema:\n"
        "{\n"
        '  "tldr": "string",\n'
        '  "overdue": [TodoItem],\n'
        '  "dueSoon": [TodoItem],\n'
        '  "nextActions": ["string"],\n'
        '  "quickWins": ["string"]\n'
        "}\n"
        "TodoItem:\n"
        "{\n"
        '  "id": "string",\n'
        '  "text": "string",\n'
        '  "checked": boolean,\n'
        '  "notePath": "string",\n'
        '  "lineNo": number\n'
        "}\n"
        "Return JSON only."
    )
    schema_hint = "TodayPlan with fields tldr, overdue, dueSoon, nextActions, quickWins"
    plan = call_json(prompt, schema_hint, model=OLLAMA_MODEL_PLAN)
    return plan
