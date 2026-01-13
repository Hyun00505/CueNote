"""
CueNote Core - Graph API 라우터
AI 기반 노트 클러스터링 및 그래프 뷰 데이터
"""
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..config import logger
from ..schemas import (
    GraphDataPayload, GraphDataResponse,
    ClusterNotesPayload, ClusterNotesResponse,
    GraphNode, GraphEdge, ClusterInfo,
    SaveClusterSettingsPayload, ClusterSettingsResponse,
    UpdateClusterPayload, MoveNoteToClusterPayload,
    ClusterCustomization, NoteClusterOverride,
    LockNoteClusterPayload
)

# 분리된 모듈에서 import
from .graph_cache import GraphCache, CLUSTER_COLORS
from .graph_utils import (
    get_current_vault_path,
    get_all_notes,
    get_embeddings_batch_optimized,
    compute_similarity_matrix,
    perform_clustering,
    generate_cluster_labels_optimized
)

router = APIRouter(prefix="/graph", tags=["graph"])


# ─────────────────────────────────────────────────────────────────────────────
# API 엔드포인트
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/data", response_model=GraphDataResponse)
async def get_graph_data(payload: GraphDataPayload):
    """
    그래프 뷰 데이터 생성 (최적화 버전)
    - 캐싱을 통한 증분 업데이트
    - 변경된 노트만 재계산
    - 클러스터 라벨 캐싱
    """
    start_time = time.time()
    
    # 1. 모든 노트 읽기
    vault_path = get_current_vault_path()
    notes = get_all_notes()
    
    if not notes:
        return GraphDataResponse(
            nodes=[],
            edges=[],
            clusters=[],
            totalNotes=0
        )
    
    logger.info(f"Processing {len(notes)} notes for graph view")
    
    # 2. 캐시 초기화
    cache = GraphCache(vault_path)
    
    # 오래된 캐시 정리
    current_paths = {n["path"] for n in notes}
    cache.cleanup_old_entries(current_paths)
    
    # 3. 임베딩 생성 (캐시 활용)
    embeddings, emb_cached, emb_computed = get_embeddings_batch_optimized(notes, cache)
    
    # 4. 클러스터링
    num_clusters = min(payload.maxClusters, max(2, len(notes) // 3))
    cluster_labels = perform_clustering(embeddings, num_clusters)
    
    # 5. 유사도 행렬 계산
    similarity_matrix = compute_similarity_matrix(embeddings)
    
    # 6. 클러스터별 컨텐츠 수집 (라벨 생성용)
    cluster_contents: dict[int, list[str]] = {}
    for i, label in enumerate(cluster_labels):
        if label not in cluster_contents:
            cluster_contents[label] = []
        cluster_contents[label].append(notes[i]["content"])
    
    # 7. AI로 클러스터 라벨 생성 (캐싱 포함)
    cluster_label_map, label_cached, label_generated = await generate_cluster_labels_optimized(
        cluster_contents,
        payload.provider,
        payload.api_key,
        payload.model,
        cache
    )
    
    # 8. 커스텀 설정 로드
    customizations = cache.get_cluster_customizations()
    note_overrides = cache.get_note_overrides()
    locked_notes = cache.get_locked_notes()
    
    # 9. 노트 오버라이드 적용 (사용자가 수동으로 클러스터 변경한 경우)
    # 잠금된 노트: AI 클러스터링 결과 무시, 기존 오버라이드 유지
    # 오버라이드된 노트: AI 클러스터링보다 우선
    final_cluster_labels = cluster_labels.copy()
    max_cluster_id = max(cluster_labels) if cluster_labels else 0
    
    for i, note in enumerate(notes):
        note_path = note["path"]
        
        if note_path in note_overrides:
            override_cluster = note_overrides[note_path]
            final_cluster_labels[i] = override_cluster
            # 오버라이드된 클러스터 ID가 현재 범위를 벗어나면 최대값 업데이트
            if override_cluster > max_cluster_id:
                max_cluster_id = override_cluster
        elif note_path in locked_notes:
            # 잠금되어 있지만 오버라이드가 없는 경우: 현재 AI 클러스터 유지하고 오버라이드로 저장
            cache.set_note_override(note_path, cluster_labels[i])
    
    # 10. AI 클러스터 할당 정보 저장 (노트별 클러스터 ID)
    ai_assignments = {}
    for i, note in enumerate(notes):
        ai_assignments[note["path"]] = cluster_labels[i]  # AI가 분류한 원본 클러스터
    cache.set_ai_cluster_assignments(ai_assignments)
    
    # AI 클러스터 라벨 정보 저장 (클러스터 ID -> (라벨, 키워드))
    ai_cluster_labels_info: dict[int, tuple[str, list[str]]] = {}
    for cluster_id, (label, keywords) in cluster_label_map.items():
        ai_cluster_labels_info[cluster_id] = (label, keywords)
    cache.set_ai_cluster_labels(ai_cluster_labels_info)
    
    # 11. 캐시 저장
    cache.save()
    
    # 12. 클러스터별 최종 노트 수 계산 (오버라이드 반영)
    final_cluster_contents: dict[int, list[str]] = {}
    for i, label in enumerate(final_cluster_labels):
        if label not in final_cluster_contents:
            final_cluster_contents[label] = []
        final_cluster_contents[label].append(notes[i]["content"])
    
    # 13. 노드 생성 (커스텀 설정 적용)
    nodes = []
    for i, note in enumerate(notes):
        cluster_id = final_cluster_labels[i]
        ai_label, _ = cluster_label_map.get(cluster_id, (f"주제 {cluster_id + 1}", []))
        
        # 커스텀 설정 적용
        custom = customizations.get(str(cluster_id), {})
        final_label = custom.get("label") or ai_label
        final_color = custom.get("color") or CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
        
        nodes.append(GraphNode(
            id=note["path"],
            label=note["title"],
            cluster=cluster_id,
            clusterLabel=final_label,
            size=max(1, note["wordCount"] // 100),
            color=final_color
        ))
    
    # 14. 엣지 생성 (유사도 기반)
    edges = []
    for i in range(len(notes)):
        for j in range(i + 1, len(notes)):
            similarity = similarity_matrix[i][j]
            if similarity >= payload.minSimilarity:
                edges.append(GraphEdge(
                    source=notes[i]["path"],
                    target=notes[j]["path"],
                    weight=similarity,
                    type="similarity"
                ))
    
    # 15. 클러스터 정보 생성 (커스텀 설정 적용)
    clusters = []
    
    # 15-1. 노트가 있는 클러스터
    for cluster_id, contents in final_cluster_contents.items():
        ai_label, ai_keywords = cluster_label_map.get(cluster_id, (f"주제 {cluster_id + 1}", []))
        
        # 커스텀 설정 적용
        custom = customizations.get(str(cluster_id), {})
        final_label = custom.get("label") or ai_label
        final_color = custom.get("color") or CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
        # 빈 배열 []도 유효한 사용자 설정으로 처리 (키워드를 지운 경우)
        custom_keywords = custom.get("keywords")
        final_keywords = custom_keywords if custom_keywords is not None else ai_keywords
        
        clusters.append(ClusterInfo(
            id=cluster_id,
            label=final_label,
            color=final_color,
            noteCount=len(contents),
            keywords=final_keywords or []
        ))
    
    # 15-2. 사용자가 만든 빈 클러스터 (노트가 없는 커스텀 클러스터)
    existing_cluster_ids = set(final_cluster_contents.keys())
    for cluster_id_str, custom in customizations.items():
        try:
            cluster_id = int(cluster_id_str)
        except ValueError:
            continue
        
        # 이미 추가된 클러스터는 스킵
        if cluster_id in existing_cluster_ids:
            continue
        
        # 사용자가 만든 빈 클러스터 추가
        clusters.append(ClusterInfo(
            id=cluster_id,
            label=custom.get("label", f"클러스터 {cluster_id + 1}"),
            color=custom.get("color", CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]),
            noteCount=0,
            keywords=custom.get("keywords", [])
        ))
    
    elapsed = time.time() - start_time
    logger.info(
        f"Graph generated in {elapsed:.2f}s: "
        f"{len(nodes)} nodes, {len(edges)} edges, {len(clusters)} clusters | "
        f"Embeddings: {emb_cached} cached, {emb_computed} computed | "
        f"Labels: {label_cached} cached, {label_generated} generated"
    )
    
    return GraphDataResponse(
        nodes=nodes,
        edges=edges,
        clusters=clusters,
        totalNotes=len(notes)
    )


@router.post("/cluster", response_model=ClusterNotesResponse)
async def cluster_notes(payload: ClusterNotesPayload):
    """특정 노트들을 클러스터링"""
    vault_path = get_current_vault_path()
    all_notes = get_all_notes()
    
    if payload.notePaths:
        notes = [n for n in all_notes if n["path"] in payload.notePaths]
    else:
        notes = all_notes
    
    if not notes:
        return ClusterNotesResponse(clusters=[], noteAssignments={})
    
    # 캐시 사용
    cache = GraphCache(vault_path)
    
    # 임베딩 및 클러스터링
    embeddings, _, _ = get_embeddings_batch_optimized(notes, cache)
    
    num_clusters = min(payload.numClusters, len(notes))
    cluster_labels = perform_clustering(embeddings, num_clusters)
    
    # 클러스터별 컨텐츠 수집
    cluster_contents: dict[int, list[str]] = {}
    for i, label in enumerate(cluster_labels):
        if label not in cluster_contents:
            cluster_contents[label] = []
        cluster_contents[label].append(notes[i]["content"])
    
    # AI로 라벨 생성 (캐싱)
    cluster_label_map, _, _ = await generate_cluster_labels_optimized(
        cluster_contents,
        payload.provider,
        payload.api_key,
        payload.model,
        cache
    )
    
    cache.save()
    
    # 응답 생성
    clusters = []
    for cluster_id, contents in cluster_contents.items():
        label, keywords = cluster_label_map.get(cluster_id, (f"주제 {cluster_id + 1}", []))
        clusters.append(ClusterInfo(
            id=cluster_id,
            label=label,
            color=CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)],
            noteCount=len(contents),
            keywords=keywords
        ))
    
    note_assignments = {
        notes[i]["path"]: cluster_labels[i]
        for i in range(len(notes))
    }
    
    return ClusterNotesResponse(
        clusters=clusters,
        noteAssignments=note_assignments
    )


@router.get("/stats")
async def get_graph_stats():
    """그래프 통계 조회"""
    notes = get_all_notes()
    
    total_words = sum(n["wordCount"] for n in notes)
    avg_words = total_words // len(notes) if notes else 0
    
    # 캐시 상태도 반환
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    cached_embeddings = len(cache.cache_data.get("embeddings", {}))
    cached_labels = len(cache.cache_data.get("cluster_labels", {}))
    
    return {
        "totalNotes": len(notes),
        "totalWords": total_words,
        "averageWords": avg_words,
        "cache": {
            "cachedEmbeddings": cached_embeddings,
            "cachedLabels": cached_labels,
            "lastUpdated": cache.cache_data.get("last_updated")
        }
    }


@router.delete("/cache")
async def clear_cache():
    """캐시 초기화"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    try:
        if cache.cache_file.exists():
            cache.cache_file.unlink()
        
        cache.cache_data = {}
        logger.info("Graph cache cleared")
        
        return {"status": "ok", "message": "캐시가 초기화되었습니다"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 클러스터 커스텀 설정 API
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/settings", response_model=ClusterSettingsResponse)
async def get_cluster_settings():
    """클러스터 커스텀 설정 조회"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    customizations = cache.get_cluster_customizations()
    note_overrides = cache.get_note_overrides()
    
    # 응답 형식으로 변환
    custom_list = [
        ClusterCustomization(
            id=int(cluster_id),
            label=data.get("label"),
            color=data.get("color"),
            keywords=data.get("keywords")
        )
        for cluster_id, data in customizations.items()
    ]
    
    override_list = [
        NoteClusterOverride(notePath=path, clusterId=cluster_id)
        for path, cluster_id in note_overrides.items()
    ]
    
    return ClusterSettingsResponse(
        customizations=custom_list,
        noteOverrides=override_list
    )


@router.post("/settings", response_model=ClusterSettingsResponse)
async def save_cluster_settings(payload: SaveClusterSettingsPayload):
    """클러스터 커스텀 설정 저장"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    # 커스텀 설정 저장
    for custom in payload.customizations:
        cache.set_cluster_customization(
            custom.id,
            label=custom.label,
            color=custom.color,
            keywords=custom.keywords
        )
    
    # 노트 오버라이드 저장
    for override in payload.noteOverrides:
        cache.set_note_override(override.notePath, override.clusterId)
    
    cache.save()
    logger.info(f"Saved cluster settings: {len(payload.customizations)} customizations, {len(payload.noteOverrides)} overrides")
    
    return await get_cluster_settings()


@router.put("/cluster/{cluster_id}")
async def update_cluster(cluster_id: int, payload: UpdateClusterPayload):
    """단일 클러스터 설정 업데이트"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    cache.set_cluster_customization(
        cluster_id,
        label=payload.label,
        color=payload.color,
        keywords=payload.keywords
    )
    cache.save()
    
    logger.info(f"Updated cluster {cluster_id}: label={payload.label}, color={payload.color}")
    
    return {
        "status": "ok",
        "clusterId": cluster_id,
        "label": payload.label,
        "color": payload.color,
        "keywords": payload.keywords
    }


@router.post("/move-note")
async def move_note_to_cluster(payload: MoveNoteToClusterPayload):
    """노트를 다른 클러스터로 이동 (수동 오버라이드)"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    cache.set_note_override(payload.notePath, payload.targetClusterId)
    cache.save()
    
    logger.info(f"Moved note '{payload.notePath}' to cluster {payload.targetClusterId}")
    
    return {
        "status": "ok",
        "notePath": payload.notePath,
        "clusterId": payload.targetClusterId
    }


@router.delete("/move-note/{note_path:path}")
async def reset_note_cluster(note_path: str):
    """노트의 클러스터 오버라이드 제거 (AI 클러스터링으로 복원)"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    cache.remove_note_override(note_path)
    cache.save()
    
    logger.info(f"Reset cluster override for note '{note_path}'")
    
    return {"status": "ok", "notePath": note_path}


@router.delete("/settings/customizations")
async def clear_all_customizations():
    """모든 클러스터 커스텀 설정 초기화"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    cache.clear_customizations()
    cache.save()
    
    logger.info("Cleared all cluster customizations")
    
    return {"status": "ok", "message": "모든 클러스터 설정이 초기화되었습니다"}


# ─────────────────────────────────────────────────────────────────────────────
# 노트 클러스터 잠금 API
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/lock-note")
async def lock_note_cluster(payload: LockNoteClusterPayload):
    """노트 클러스터 잠금/해제
    
    잠금된 노트는 AI가 자동으로 클러스터를 변경하지 않습니다.
    """
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    if payload.locked:
        cache.lock_note(payload.notePath)
        # 잠금 시 현재 클러스터를 오버라이드로 저장 (없는 경우)
        if payload.notePath not in cache.get_note_overrides():
            # 현재 노트의 클러스터 ID를 찾아서 저장해야 함
            # 일단 오버라이드가 없으면 다음 새로고침 시 자동으로 저장됨
            pass
        logger.info(f"Locked note cluster: {payload.notePath}")
    else:
        cache.unlock_note(payload.notePath)
        logger.info(f"Unlocked note cluster: {payload.notePath}")
    
    cache.save()
    
    return {
        "status": "ok",
        "notePath": payload.notePath,
        "locked": payload.locked
    }


@router.post("/lock-notes-batch")
async def lock_notes_batch(payload: dict):
    """여러 노트 일괄 잠금/해제
    
    payload: { "notePaths": ["path1", "path2", ...], "locked": true/false }
    """
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    note_paths: list[str] = payload.get("notePaths", [])
    locked: bool = payload.get("locked", True)
    
    for note_path in note_paths:
        if locked:
            cache.lock_note(note_path)
        else:
            cache.unlock_note(note_path)
    
    cache.save()
    
    action = "locked" if locked else "unlocked"
    logger.info(f"Batch {action} {len(note_paths)} notes")
    
    return {
        "status": "ok",
        "count": len(note_paths),
        "locked": locked
    }


@router.get("/locked-notes")
async def get_locked_notes():
    """잠금된 노트 목록 조회"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    locked = list(cache.get_locked_notes())
    
    return {
        "lockedNotes": locked,
        "count": len(locked)
    }


@router.get("/note-info/{note_path:path}")
async def get_note_cluster_info(note_path: str):
    """단일 노트의 클러스터 정보 조회
    
    에디터에서 현재 노트의 클러스터 정보를 표시하기 위한 API
    """
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    # 캐시에서 정보 로드
    customizations = cache.get_cluster_customizations()
    locked_notes = cache.get_locked_notes()
    
    # 노트 경로 정규화
    normalized_path = note_path.replace("\\", "/")
    if not normalized_path.endswith(".md"):
        normalized_path += ".md"
    
    # 노트의 클러스터 ID 확인 (오버라이드 > AI 자동 분류)
    cluster_id = cache.get_note_cluster_id(normalized_path)
    
    if cluster_id is None:
        # 아직 그래프가 생성되지 않았거나 노트가 없는 경우
        return {
            "notePath": normalized_path,
            "hasCluster": False,
            "cluster": None,
            "isLocked": normalized_path in locked_notes
        }
    
    # 커스텀 설정 확인
    custom = customizations.get(str(cluster_id), {})
    
    # AI 라벨 정보 가져오기
    ai_cluster_labels = cache.get_ai_cluster_labels()
    ai_label, ai_keywords = ai_cluster_labels.get(cluster_id, (f"주제 {cluster_id + 1}", []))
    
    # 기본 색상
    default_color = CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
    
    return {
        "notePath": normalized_path,
        "hasCluster": True,
        "cluster": {
            "id": cluster_id,
            "label": custom.get("label") or ai_label,
            "color": custom.get("color") or default_color,
            "keywords": custom.get("keywords") if "keywords" in custom else ai_keywords
        },
        "isLocked": normalized_path in locked_notes
    }


# ─────────────────────────────────────────────────────────────────────────────
# 사용자 정의 클러스터 관리 API
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/cluster/create")
async def create_custom_cluster(payload: dict):
    """새 사용자 정의 클러스터 생성
    
    payload: { "label": string, "color": string, "keywords": list[string] }
    """
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    label = payload.get("label", "새 클러스터")
    color = payload.get("color", "#8b5cf6")
    keywords = payload.get("keywords", [])
    
    # 새 클러스터 ID 할당 (기존 최대 ID + 1)
    customizations = cache.get_cluster_customizations()
    ai_labels = cache.get_ai_cluster_labels()
    
    existing_ids = set()
    for key in customizations.keys():
        try:
            existing_ids.add(int(key))
        except ValueError:
            pass
    for key in ai_labels.keys():
        existing_ids.add(key)
    
    new_cluster_id = max(existing_ids, default=-1) + 1
    
    # 클러스터 설정 저장
    cache.set_cluster_customization(
        new_cluster_id,
        label=label,
        color=color,
        keywords=keywords
    )
    cache.save()
    
    logger.info(f"Created custom cluster {new_cluster_id}: {label}")
    
    return {
        "status": "ok",
        "cluster": {
            "id": new_cluster_id,
            "label": label,
            "color": color,
            "keywords": keywords,
            "noteCount": 0
        }
    }


@router.delete("/cluster/{cluster_id}")
async def delete_custom_cluster(cluster_id: int):
    """사용자 정의 클러스터 삭제
    
    해당 클러스터에 있는 노트들은 오버라이드가 제거됨
    """
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    # 클러스터 커스텀 설정 제거
    customizations = cache.get_cluster_customizations()
    if str(cluster_id) in customizations:
        del customizations[str(cluster_id)]
        cache.cache_data["cluster_customizations"] = customizations
    
    # 해당 클러스터에 있는 노트들의 오버라이드 제거
    note_overrides = cache.get_note_overrides()
    notes_to_remove = [
        note_path for note_path, cid in note_overrides.items() 
        if cid == cluster_id
    ]
    for note_path in notes_to_remove:
        cache.remove_note_override(note_path)
    
    cache.save()
    
    logger.info(f"Deleted cluster {cluster_id}, removed {len(notes_to_remove)} note overrides")
    
    return {
        "status": "ok",
        "clusterId": cluster_id,
        "removedOverrides": len(notes_to_remove)
    }


@router.get("/clusters")
async def get_all_clusters():
    """현재 존재하는 모든 클러스터 목록 조회"""
    vault_path = get_current_vault_path()
    cache = GraphCache(vault_path)
    
    customizations = cache.get_cluster_customizations()
    ai_labels = cache.get_ai_cluster_labels()
    note_overrides = cache.get_note_overrides()
    ai_assignments = cache.get_ai_cluster_assignments()
    
    # 클러스터별 노트 수 계산
    cluster_note_counts: dict[int, int] = {}
    
    # AI 자동 분류 노트 카운트
    for note_path, cluster_id in ai_assignments.items():
        if note_path not in note_overrides:  # 오버라이드되지 않은 경우만
            cluster_note_counts[cluster_id] = cluster_note_counts.get(cluster_id, 0) + 1
    
    # 오버라이드 노트 카운트
    for note_path, cluster_id in note_overrides.items():
        cluster_note_counts[cluster_id] = cluster_note_counts.get(cluster_id, 0) + 1
    
    # 클러스터 목록 생성
    clusters = []
    all_cluster_ids = set(cluster_note_counts.keys()) | set(int(k) for k in customizations.keys())
    
    for cluster_id in sorted(all_cluster_ids):
        custom = customizations.get(str(cluster_id), {})
        ai_label, ai_keywords = ai_labels.get(cluster_id, (f"주제 {cluster_id + 1}", []))
        
        clusters.append({
            "id": cluster_id,
            "label": custom.get("label") or ai_label,
            "color": custom.get("color") or CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)],
            "keywords": custom.get("keywords") if "keywords" in custom else ai_keywords,
            "noteCount": cluster_note_counts.get(cluster_id, 0),
            "isCustom": str(cluster_id) in customizations and not ai_labels.get(cluster_id)
        })
    
    return {
        "clusters": clusters,
        "totalClusters": len(clusters)
    }