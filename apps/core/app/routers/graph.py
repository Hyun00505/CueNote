"""
CueNote Core - Graph API 라우터 (간소화)
AI 기반 노트 클러스터링 및 관련 노트 탐색
"""
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from ..config import logger
from ..schemas import (
    GraphDataPayload, GraphDataResponse,
    GraphNode, GraphEdge, ClusterInfo, RelatedNoteItem
)

# 분리된 모듈에서 import
from .graph_cache import GraphCache, CLUSTER_COLORS
from .graph_utils import (
    get_current_vault_path,
    get_all_notes,
    get_embeddings_batch_optimized,
    compute_similarity_matrix,
    perform_clustering,
    generate_cluster_labels_optimized,
    get_note_preview,
    search_notes_in_graph
)

router = APIRouter(prefix="/graph", tags=["graph"])


# ─────────────────────────────────────────────────────────────────────────────
# API 엔드포인트 (5개)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/data", response_model=GraphDataResponse)
async def get_graph_data(payload: GraphDataPayload):
    """
    그래프 뷰 데이터 생성
    - 캐싱을 통한 증분 업데이트
    - 변경된 노트만 재계산
    - 클러스터 라벨 캐싱
    """
    try:
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
        try:
            cluster_label_map, label_cached, label_generated = await generate_cluster_labels_optimized(
                cluster_contents,
                payload.provider,
                payload.api_key,
                payload.model,
                cache
            )
        except Exception as e:
            logger.warning(f"Failed to generate AI labels, using defaults: {e}")
            cluster_label_map = {
                cluster_id: (f"주제 {cluster_id + 1}", [])
                for cluster_id in cluster_contents.keys()
            }
            label_cached, label_generated = 0, 0
    
        # 8. 캐시 저장
        cache.save()
    
        # 9. 노드 생성
        nodes = []
        for i, note in enumerate(notes):
            cluster_id = cluster_labels[i]
            label, _ = cluster_label_map.get(cluster_id, (f"주제 {cluster_id + 1}", []))
            color = CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
        
            nodes.append(GraphNode(
                id=note["path"],
                label=note["title"],
                cluster=cluster_id,
                clusterLabel=label,
                size=max(1, note["wordCount"] // 100),
                color=color,
                preview=get_note_preview(note["content"])
            ))
    
        # 10. 엣지 생성 (유사도 기반)
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
    
        # 11. 클러스터 정보 생성
        clusters = []
        for cluster_id, contents in cluster_contents.items():
            label, keywords = cluster_label_map.get(cluster_id, (f"주제 {cluster_id + 1}", []))
            color = CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
        
            clusters.append(ClusterInfo(
                id=cluster_id,
                label=label,
                color=color,
                noteCount=len(contents),
                keywords=keywords or []
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
    except Exception as e:
        logger.error(f"Failed to generate graph data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"그래프 데이터 생성 중 오류 발생: {str(e)}")


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


@router.get("/related/{note_path:path}")
async def get_related_notes(note_path: str, top_n: int = Query(default=8, ge=1, le=20)):
    """
    특정 노트와 관련된 노트 추천 (유사도 기반 Top N)
    """
    try:
        vault_path = get_current_vault_path()
        notes = get_all_notes()
        
        if not notes:
            return {"relatedNotes": [], "notePath": note_path}
        
        # 대상 노트 인덱스 찾기
        target_idx = None
        normalized_path = note_path.replace("\\", "/")
        if not normalized_path.endswith(".md"):
            normalized_path += ".md"
        
        for i, note in enumerate(notes):
            if note["path"] == normalized_path or note["path"] == note_path:
                target_idx = i
                break
        
        if target_idx is None:
            return {"relatedNotes": [], "notePath": note_path}
        
        # 캐시 활용 임베딩
        cache = GraphCache(vault_path)
        embeddings, _, _ = get_embeddings_batch_optimized(notes, cache)
        cache.save()
        
        # 유사도 계산
        similarity_matrix = compute_similarity_matrix(embeddings)
        
        # 자기 자신 제외하고 유사도 순 정렬
        similarities = []
        for i, note in enumerate(notes):
            if i == target_idx:
                continue
            sim = similarity_matrix[target_idx][i]
            if sim > 0.05:  # 최소 유사도 임계값
                similarities.append((i, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 클러스터 정보가 필요하므로 클러스터링 수행
        num_clusters = min(8, max(2, len(notes) // 3))
        cluster_labels = perform_clustering(embeddings, num_clusters)
        
        # 클러스터 라벨 생성은 캐시에서 가져오기 시도
        cluster_contents: dict[int, list[str]] = {}
        for i, label in enumerate(cluster_labels):
            if label not in cluster_contents:
                cluster_contents[label] = []
            cluster_contents[label].append(notes[i]["content"])
        
        # 기본 라벨 (AI 호출 없이 빠르게 응답)
        cluster_label_map = {}
        for cluster_id, contents in cluster_contents.items():
            cluster_hash = cache.get_cluster_content_hash(contents)
            cached = cache.get_cached_cluster_label(cluster_hash)
            if cached:
                cluster_label_map[cluster_id] = cached
            else:
                cluster_label_map[cluster_id] = (f"주제 {cluster_id + 1}", [])
        
        # Top N 관련 노트 반환
        related = []
        for idx, sim in similarities[:top_n]:
            note = notes[idx]
            cluster_id = cluster_labels[idx]
            cluster_label, _ = cluster_label_map.get(cluster_id, (f"주제 {cluster_id + 1}", []))
            
            related.append(RelatedNoteItem(
                path=note["path"],
                title=note["title"],
                similarity=round(sim, 3),
                clusterLabel=cluster_label,
                color=CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)],
                preview=get_note_preview(note["content"])
            ))
        
        return {"relatedNotes": related, "notePath": note_path}
        
    except Exception as e:
        logger.error(f"Failed to get related notes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_graph_notes(q: str = Query(default="", min_length=0)):
    """
    그래프 내 노트 검색 (제목/내용/경로 매칭)
    매칭된 노트 ID 목록을 반환하여 프론트엔드에서 하이라이트
    """
    try:
        if not q.strip():
            return {"matches": [], "query": q}
        
        notes = get_all_notes()
        results = search_notes_in_graph(notes, q)
        
        matches = [
            {
                "path": note["path"],
                "title": note["title"],
                "preview": get_note_preview(note["content"])
            }
            for note in results[:20]  # 최대 20개
        ]
        
        return {"matches": matches, "query": q, "totalMatches": len(results)}
        
    except Exception as e:
        logger.error(f"Failed to search notes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))