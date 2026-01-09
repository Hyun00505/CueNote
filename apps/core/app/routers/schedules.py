"""
CueNote Core - 일정(Schedule) 라우터
일정 CRUD 및 AI 일정 추출 기능
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..config import logger
from ..db import get_conn
from ..ollama_client import call_json as ollama_call_json
from ..gemini_client import call_json as gemini_call_json
from ..schemas import (
    ScheduleItem,
    ScheduleCreatePayload,
    ScheduleUpdatePayload,
    ScheduleCountByDate,
    AIExtractSchedulePayload,
    AIExtractScheduleResponse,
)

router = APIRouter(tags=["schedules"])


def _row_to_schedule(row: tuple) -> dict:
    """DB 행을 일정 딕셔너리로 변환"""
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2] or "",
        "date": row[3],
        "startTime": row[4] or "",
        "endTime": row[5] or "",
        "color": row[6] or "#c9a76c",
        "completed": bool(row[7]),
        "createdAt": row[8] or "",
        "updatedAt": row[9] or "",
    }


@router.get("/schedules")
async def get_schedules(
    date: Optional[str] = Query(default=None, description="특정 날짜 (YYYY-MM-DD)"),
    month: Optional[str] = Query(default=None, description="월별 조회 (YYYY-MM)"),
):
    """일정 목록을 조회합니다."""
    conn = get_conn()
    try:
        if date:
            # 특정 날짜의 일정
            rows = conn.execute(
                """
                SELECT id, title, description, date, start_time, end_time, 
                       color, completed, created_at, updated_at
                FROM schedules
                WHERE date = ?
                ORDER BY start_time ASC, created_at ASC
                """,
                (date,),
            ).fetchall()
        elif month:
            # 월별 일정
            rows = conn.execute(
                """
                SELECT id, title, description, date, start_time, end_time,
                       color, completed, created_at, updated_at
                FROM schedules
                WHERE date LIKE ?
                ORDER BY date ASC, start_time ASC
                """,
                (f"{month}%",),
            ).fetchall()
        else:
            # 전체 일정
            rows = conn.execute(
                """
                SELECT id, title, description, date, start_time, end_time,
                       color, completed, created_at, updated_at
                FROM schedules
                ORDER BY date DESC, start_time ASC
                LIMIT 100
                """
            ).fetchall()
    finally:
        conn.close()

    schedules = [_row_to_schedule(row) for row in rows]
    return {"schedules": schedules}


@router.get("/schedules/counts")
async def get_schedule_counts(
    month: str = Query(..., description="월별 조회 (YYYY-MM)"),
):
    """월별 날짜별 일정 개수를 조회합니다."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT date, 
                   COUNT(*) as total,
                   SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed
            FROM schedules
            WHERE date LIKE ?
            GROUP BY date
            ORDER BY date ASC
            """,
            (f"{month}%",),
        ).fetchall()
    finally:
        conn.close()

    counts = [
        {"date": row[0], "count": row[1], "completedCount": row[2]}
        for row in rows
    ]
    return {"counts": counts}


@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: str):
    """특정 일정을 조회합니다."""
    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT id, title, description, date, start_time, end_time,
                   color, completed, created_at, updated_at
            FROM schedules
            WHERE id = ?
            """,
            (schedule_id,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다")

    return {"schedule": _row_to_schedule(row)}


@router.post("/schedules")
async def create_schedule(payload: ScheduleCreatePayload):
    """새 일정을 생성합니다."""
    schedule_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO schedules (id, title, description, date, start_time, end_time, color, completed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                schedule_id,
                payload.title,
                payload.description,
                payload.date,
                payload.startTime,
                payload.endTime,
                payload.color,
                now,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    logger.info(f"일정 생성: {schedule_id} - {payload.title}")

    return {
        "schedule": {
            "id": schedule_id,
            "title": payload.title,
            "description": payload.description,
            "date": payload.date,
            "startTime": payload.startTime,
            "endTime": payload.endTime,
            "color": payload.color,
            "completed": False,
            "createdAt": now,
            "updatedAt": now,
        }
    }


@router.put("/schedules/{schedule_id}")
async def update_schedule(schedule_id: str, payload: ScheduleUpdatePayload):
    """일정을 수정합니다."""
    conn = get_conn()
    try:
        # 기존 일정 확인
        existing = conn.execute(
            "SELECT id FROM schedules WHERE id = ?", (schedule_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다")

        # 업데이트할 필드만 설정
        updates = []
        values = []
        
        if payload.title is not None:
            updates.append("title = ?")
            values.append(payload.title)
        if payload.description is not None:
            updates.append("description = ?")
            values.append(payload.description)
        if payload.date is not None:
            updates.append("date = ?")
            values.append(payload.date)
        if payload.startTime is not None:
            updates.append("start_time = ?")
            values.append(payload.startTime)
        if payload.endTime is not None:
            updates.append("end_time = ?")
            values.append(payload.endTime)
        if payload.color is not None:
            updates.append("color = ?")
            values.append(payload.color)
        if payload.completed is not None:
            updates.append("completed = ?")
            values.append(1 if payload.completed else 0)

        if updates:
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(schedule_id)

            conn.execute(
                f"UPDATE schedules SET {', '.join(updates)} WHERE id = ?",
                tuple(values),
            )
            conn.commit()

        # 업데이트된 일정 조회
        row = conn.execute(
            """
            SELECT id, title, description, date, start_time, end_time,
                   color, completed, created_at, updated_at
            FROM schedules
            WHERE id = ?
            """,
            (schedule_id,),
        ).fetchone()
    finally:
        conn.close()

    return {"schedule": _row_to_schedule(row)}


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """일정을 삭제합니다."""
    conn = get_conn()
    try:
        result = conn.execute(
            "DELETE FROM schedules WHERE id = ?", (schedule_id,)
        )
        conn.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다")
    finally:
        conn.close()

    logger.info(f"일정 삭제: {schedule_id}")
    return {"success": True, "message": "일정이 삭제되었습니다"}


@router.post("/ai/extract-schedules")
async def extract_schedules_from_note(payload: AIExtractSchedulePayload):
    """노트 내용에서 AI로 일정을 추출합니다."""
    
    # 현재 날짜/요일 정보 계산
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    today_weekday = weekday_names[now.weekday()]
    
    # 이번주/다음주 날짜 계산
    days_until_monday = now.weekday()  # 0=월요일
    this_week_start = now - timedelta(days=days_until_monday)
    next_week_start = this_week_start + timedelta(days=7)
    
    week_dates = {}
    for i, day_name in enumerate(weekday_names):
        # 이번주
        this_week_date = this_week_start + timedelta(days=i)
        week_dates[f"이번주 {day_name}"] = this_week_date.strftime('%Y-%m-%d')
        week_dates[f"이번 주 {day_name}"] = this_week_date.strftime('%Y-%m-%d')
        # 다음주
        next_week_date = next_week_start + timedelta(days=i)
        week_dates[f"다음주 {day_name}"] = next_week_date.strftime('%Y-%m-%d')
        week_dates[f"다음 주 {day_name}"] = next_week_date.strftime('%Y-%m-%d')
        # 요일만 언급된 경우 (이번주로 간주, 오늘 이후)
        if this_week_date >= now:
            week_dates[day_name] = this_week_date.strftime('%Y-%m-%d')
        else:
            week_dates[day_name] = next_week_date.strftime('%Y-%m-%d')
    
    prompt = f"""당신은 일정 추출 전문가입니다. 아래 텍스트에서 모든 일정, 약속, 할 일, 마감일을 찾아 추출하세요.

## 분석할 텍스트:
{payload.content}

## 현재 날짜 정보:
- 오늘: {today_str} ({today_weekday})
- 내일: {(now + timedelta(days=1)).strftime('%Y-%m-%d')}
- 모레: {(now + timedelta(days=2)).strftime('%Y-%m-%d')}
- 이번주 월요일: {week_dates.get('이번주 월요일')}
- 다음주 월요일: {week_dates.get('다음주 월요일')}

## 요일별 실제 날짜:
{json.dumps(week_dates, ensure_ascii=False, indent=2)}

## 추출 규칙:
1. "- [ ]" 체크박스 형식은 할 일/일정으로 인식
2. "오늘", "내일", "다음주" 등의 상대적 표현은 위의 날짜 정보로 변환
3. "목요일에" → 가장 가까운 다음 목요일 날짜로 변환
4. 시간이 명시되면 (예: "오후 8시", "20:00") startTime에 HH:MM 형식으로 기록
5. 시간이 없으면 startTime, endTime은 빈 문자열 ""
6. 모든 일정 항목을 빠짐없이 추출

## 출력 형식 (JSON만 출력, 설명 없이):
{{
  "schedules": [
    {{
      "title": "일정 제목",
      "description": "",
      "date": "YYYY-MM-DD",
      "startTime": "HH:MM 또는 빈문자열",
      "endTime": ""
    }}
  ],
  "confidence": 0.0~1.0
}}

JSON만 출력하세요:"""

    schema_hint = "ExtractedSchedules with fields schedules (array of schedule objects) and confidence (float)"

    # ===== 디버깅 로그 =====
    print("\n" + "="*60)
    print("🔍 [AI 일정 추출] 디버깅 시작")
    print("="*60)
    print(f"📅 오늘 날짜: {today_str} ({today_weekday})")
    print(f"🤖 Provider: {payload.provider}")
    print(f"🧠 Model: {payload.model or '기본값'}")
    print(f"🔑 API Key: {'있음' if payload.api_key else '없음'}")
    print("-"*60)
    print("📝 입력 텍스트:")
    print(payload.content[:500] + ("..." if len(payload.content) > 500 else ""))
    print("-"*60)
    print("📤 AI에 보내는 프롬프트 (앞부분):")
    print(prompt[:800] + "...")
    print("="*60)

    try:
        if payload.provider == "gemini" and payload.api_key:
            print("🚀 Gemini API 호출 중...")
            result = gemini_call_json(
                prompt, 
                schema_hint, 
                api_key=payload.api_key, 
                model=payload.model or None
            )
        else:
            print("🚀 Ollama API 호출 중...")
            result = ollama_call_json(prompt, schema_hint, model=payload.model or None)

        # ===== 결과 디버깅 =====
        print("\n" + "="*60)
        print("✅ AI 응답 받음!")
        print("-"*60)
        print("📥 Raw 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("="*60 + "\n")

        # 추출된 일정에 ID 부여
        schedules = result.get("schedules", [])
        print(f"📊 추출된 일정 개수: {len(schedules)}개")
        
        for i, schedule in enumerate(schedules):
            schedule["id"] = str(uuid.uuid4())
            schedule["color"] = "#c9a76c"
            schedule["completed"] = False
            schedule["createdAt"] = ""
            schedule["updatedAt"] = ""
            # 필드명 정규화
            if "startTime" not in schedule:
                schedule["startTime"] = schedule.pop("start_time", "")
            if "endTime" not in schedule:
                schedule["endTime"] = schedule.pop("end_time", "")
            
            print(f"  [{i+1}] {schedule.get('title', '?')} - {schedule.get('date', '?')} {schedule.get('startTime', '')}")

        final_result = {
            "schedules": schedules,
            "confidence": result.get("confidence", 0.5)
        }
        
        print(f"\n🎯 최종 신뢰도: {final_result['confidence']}")
        print("="*60 + "\n")
        
        return final_result

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ 일정 추출 실패!")
        print(f"🔴 에러 타입: {type(e).__name__}")
        print(f"🔴 에러 메시지: {e}")
        import traceback
        print("🔴 스택 트레이스:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        logger.error(f"일정 추출 실패: {e}")
        return {"schedules": [], "confidence": 0.0, "error": str(e)}


@router.post("/schedules/batch")
async def create_schedules_batch(schedules: list[ScheduleCreatePayload]):
    """여러 일정을 한 번에 생성합니다."""
    created = []
    now = datetime.now().isoformat()

    conn = get_conn()
    try:
        for payload in schedules:
            schedule_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO schedules (id, title, description, date, start_time, end_time, color, completed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    schedule_id,
                    payload.title,
                    payload.description,
                    payload.date,
                    payload.startTime,
                    payload.endTime,
                    payload.color,
                    now,
                    now,
                ),
            )
            created.append({
                "id": schedule_id,
                "title": payload.title,
                "description": payload.description,
                "date": payload.date,
                "startTime": payload.startTime,
                "endTime": payload.endTime,
                "color": payload.color,
                "completed": False,
                "createdAt": now,
                "updatedAt": now,
            })
        conn.commit()
    finally:
        conn.close()

    logger.info(f"{len(created)}개 일정 일괄 생성")
    return {"schedules": created}
