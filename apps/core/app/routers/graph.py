"""
CueNote Core - Graph 라우터
AI 기반 노트 클러스터링 및 그래프 뷰 데이터
+ 캐싱 & 증분 업데이트 최적화
"""
import json
import hashlib
import re
import time
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..config import logger, PROJECT_ROOT
from ..schemas import (
    GraphDataPayload, GraphDataResponse,
    ClusterNotesPayload, ClusterNotesResponse,
    GraphNode, GraphEdge, ClusterInfo,
    SaveClusterSettingsPayload, ClusterSettingsResponse,
    UpdateClusterPayload, MoveNoteToClusterPayload,
    ClusterCustomization, NoteClusterOverride
)

router = APIRouter(prefix="/graph", tags=["graph"])

# 환경 설정 파일 경로 (vault.py와 동일)
ENV_CONFIG_PATH = PROJECT_ROOT / "apps" / "core" / "data" / "environments.json"
DEFAULT_VAULT_PATH = PROJECT_ROOT / "data"

# 캐시 파일 경로
CACHE_DIR = PROJECT_ROOT / "apps" / "core" / "data" / ".graph_cache"

# 클러스터 색상 팔레트 (최대 12개)
CLUSTER_COLORS = [
    "#8b5cf6",  # Purple
    "#3b82f6",  # Blue
    "#22c55e",  # Green
    "#f59e0b",  # Amber
    "#ef4444",  # Red
    "#ec4899",  # Pink
    "#06b6d4",  # Cyan
    "#84cc16",  # Lime
    "#f97316",  # Orange
    "#6366f1",  # Indigo
    "#14b8a6",  # Teal
    "#a855f7",  # Violet
]


# ─────────────────────────────────────────────────────────────────────────────
# 캐시 시스템
# ─────────────────────────────────────────────────────────────────────────────

class GraphCache:
    """그래프 데이터 캐싱 관리"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.cache_file = CACHE_DIR / f"{self._get_vault_hash()}.json"
        self.cache_data: dict = {}
        self._load_cache()
    
    def _get_vault_hash(self) -> str:
        """Vault 경로의 해시 (캐시 파일명용)"""
        return hashlib.md5(str(self.vault_path).encode()).hexdigest()[:12]
    
    def _load_cache(self):
        """캐시 파일 로드"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        if self.cache_file.exists():
            try:
                self.cache_data = json.loads(self.cache_file.read_text(encoding="utf-8"))
                logger.info(f"Graph cache loaded: {len(self.cache_data.get('embeddings', {}))} cached notes")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.cache_data = {}
        else:
            self.cache_data = {}
    
    def _save_cache(self):
        """캐시 파일 저장"""
        try:
            self.cache_data["last_updated"] = time.time()
            self.cache_file.write_text(
                json.dumps(self.cache_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def get_content_hash(self, content: str) -> str:
        """콘텐츠 해시 계산"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_cached_embedding(self, note_path: str, content_hash: str) -> Optional[list[float]]:
        """캐시된 임베딩 가져오기"""
        embeddings = self.cache_data.get("embeddings", {})
        cached = embeddings.get(note_path)
        
        if cached and cached.get("hash") == content_hash:
            return cached.get("embedding")
        return None
    
    def set_embedding(self, note_path: str, content_hash: str, embedding: list[float]):
        """임베딩 캐시에 저장"""
        if "embeddings" not in self.cache_data:
            self.cache_data["embeddings"] = {}
        
        self.cache_data["embeddings"][note_path] = {
            "hash": content_hash,
            "embedding": embedding
        }
    
    def get_cached_cluster_label(self, cluster_hash: str) -> Optional[tuple[str, list[str]]]:
        """캐시된 클러스터 라벨 가져오기"""
        labels = self.cache_data.get("cluster_labels", {})
        cached = labels.get(cluster_hash)
        
        if cached:
            return (cached.get("label", ""), cached.get("keywords", []))
        return None
    
    def set_cluster_label(self, cluster_hash: str, label: str, keywords: list[str]):
        """클러스터 라벨 캐시에 저장"""
        if "cluster_labels" not in self.cache_data:
            self.cache_data["cluster_labels"] = {}
        
        self.cache_data["cluster_labels"][cluster_hash] = {
            "label": label,
            "keywords": keywords
        }
    
    def get_cluster_content_hash(self, contents: list[str]) -> str:
        """클러스터 컨텐츠들의 해시 (라벨 캐싱용)"""
        combined = "||".join(sorted([c[:200] for c in contents]))
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def cleanup_old_entries(self, current_paths: set[str]):
        """더 이상 존재하지 않는 노트의 캐시 정리"""
        embeddings = self.cache_data.get("embeddings", {})
        removed = []
        
        for path in list(embeddings.keys()):
            if path not in current_paths:
                del embeddings[path]
                removed.append(path)
        
        if removed:
            logger.info(f"Cleaned up {len(removed)} old cache entries")
    
    # ─────────────────────────────────────────────────────────────────────────
    # 클러스터 커스텀 설정 관리
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_cluster_customizations(self) -> dict[str, dict]:
        """클러스터 커스텀 설정 가져오기 (키는 문자열)"""
        return self.cache_data.get("cluster_customizations", {})
    
    def set_cluster_customization(self, cluster_id: int, label: Optional[str] = None, 
                                   color: Optional[str] = None, keywords: Optional[list[str]] = None):
        """클러스터 커스텀 설정 저장"""
        if "cluster_customizations" not in self.cache_data:
            self.cache_data["cluster_customizations"] = {}
        
        customizations = self.cache_data["cluster_customizations"]
        if str(cluster_id) not in customizations:
            customizations[str(cluster_id)] = {}
        
        if label is not None:
            customizations[str(cluster_id)]["label"] = label
        if color is not None:
            customizations[str(cluster_id)]["color"] = color
        if keywords is not None:
            customizations[str(cluster_id)]["keywords"] = keywords
    
    def get_note_overrides(self) -> dict[str, int]:
        """노트 클러스터 오버라이드 가져오기"""
        return self.cache_data.get("note_overrides", {})
    
    def set_note_override(self, note_path: str, cluster_id: int):
        """노트 클러스터 오버라이드 설정"""
        if "note_overrides" not in self.cache_data:
            self.cache_data["note_overrides"] = {}
        self.cache_data["note_overrides"][note_path] = cluster_id
    
    def remove_note_override(self, note_path: str):
        """노트 클러스터 오버라이드 제거"""
        if "note_overrides" in self.cache_data:
            self.cache_data["note_overrides"].pop(note_path, None)
    
    def clear_customizations(self):
        """모든 커스텀 설정 초기화"""
        self.cache_data["cluster_customizations"] = {}
        self.cache_data["note_overrides"] = {}
    
    def save(self):
        """캐시 저장"""
        self._save_cache()


# ─────────────────────────────────────────────────────────────────────────────
# 유틸리티 함수
# ─────────────────────────────────────────────────────────────────────────────

def get_current_vault_path() -> Path:
    """현재 선택된 환경의 Vault 경로 반환"""
    if not ENV_CONFIG_PATH.exists():
        return DEFAULT_VAULT_PATH
    
    try:
        data = json.loads(ENV_CONFIG_PATH.read_text(encoding="utf-8"))
        current_id = data.get("current_id")
        if not current_id:
            return DEFAULT_VAULT_PATH
        
        for env in data.get("environments", []):
            if env.get("id") == current_id:
                env_path = Path(env.get("path", ""))
                if env_path.exists():
                    return env_path
        
        return DEFAULT_VAULT_PATH
    except Exception as e:
        logger.error("Failed to get current vault path: %s", e)
        return DEFAULT_VAULT_PATH


def get_all_notes() -> list[dict]:
    """모든 노트 파일 읽기"""
    vault_path = get_current_vault_path()
    notes = []
    
    for md_file in vault_path.rglob("*.md"):
        rel_path = md_file.relative_to(vault_path)
        rel_path_str = str(rel_path).replace("\\", "/")
        
        # .trash 폴더 제외
        if rel_path_str.startswith(".trash/") or "/.trash/" in rel_path_str:
            continue
        
        try:
            content = md_file.read_text(encoding="utf-8")
            title = rel_path_str.replace(".md", "")
            
            # 마크다운에서 제목 추출 시도
            first_heading = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if first_heading:
                title = first_heading.group(1).strip()
            
            # 단어 수 계산
            word_count = len(content.split())
            
            notes.append({
                "path": rel_path_str,
                "title": title,
                "content": content[:3000],  # 임베딩용 앞부분만
                "wordCount": word_count
            })
        except Exception as e:
            logger.warning(f"Failed to read note {rel_path_str}: {e}")
    
    return notes


# ─────────────────────────────────────────────────────────────────────────────
# 임베딩 & 클러스터링 (최적화)
# ─────────────────────────────────────────────────────────────────────────────

def get_embeddings_batch_optimized(
    notes: list[dict], 
    cache: GraphCache
) -> tuple[list[list[float]], int, int]:
    """
    캐시를 활용한 배치 임베딩 생성
    Returns: (embeddings, cached_count, computed_count)
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    
    if not notes:
        return [], 0, 0
    
    embeddings: list[Optional[list[float]]] = [None] * len(notes)
    to_compute_indices: list[int] = []
    to_compute_texts: list[str] = []
    cached_count = 0
    
    # 1. 캐시에서 가져올 수 있는 것들 확인
    for i, note in enumerate(notes):
        content_hash = cache.get_content_hash(note["content"])
        cached_emb = cache.get_cached_embedding(note["path"], content_hash)
        
        if cached_emb is not None:
            embeddings[i] = cached_emb
            cached_count += 1
        else:
            to_compute_indices.append(i)
            to_compute_texts.append(note["content"] if note["content"].strip() else "empty")
    
    # 2. 캐시에 없는 것들 계산
    computed_count = len(to_compute_indices)
    
    if to_compute_texts:
        try:
            # 모든 텍스트(캐시 포함)로 TF-IDF 학습해야 일관성 유지
            all_texts = [n["content"] if n["content"].strip() else "empty" for n in notes]
            
            vectorizer = TfidfVectorizer(
                max_features=200,
                stop_words=None,
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            
            # 전체 코퍼스로 fit
            vectorizer.fit(all_texts)
            
            # 필요한 것들만 transform
            transform_result = vectorizer.transform(to_compute_texts)
            new_embeddings_matrix = transform_result.toarray()  # type: ignore
            
            for idx, global_idx in enumerate(to_compute_indices):
                emb = new_embeddings_matrix[idx].tolist()
                embeddings[global_idx] = emb
                
                # 캐시에 저장
                note = notes[global_idx]
                content_hash = cache.get_content_hash(note["content"])
                cache.set_embedding(note["path"], content_hash, emb)
            
            # 캐시된 것들도 새 vectorizer로 재계산 (일관성)
            if cached_count > 0:
                for i, note in enumerate(notes):
                    if i not in to_compute_indices:
                        text = note["content"] if note["content"].strip() else "empty"
                        single_result = vectorizer.transform([text])
                        emb = single_result.toarray()[0].tolist()  # type: ignore
                        embeddings[i] = emb
                        content_hash = cache.get_content_hash(note["content"])
                        cache.set_embedding(note["path"], content_hash, emb)
                        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # 실패 시 0 벡터로 대체
            for idx in to_compute_indices:
                embeddings[idx] = [0.0] * 200
    
    return [e if e else [0.0] * 200 for e in embeddings], cached_count, computed_count


def compute_similarity_matrix(embeddings: list[list[float]]) -> list[list[float]]:
    """코사인 유사도 행렬 계산"""
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    if not embeddings:
        return []
    
    embedding_array = np.array(embeddings)
    similarity_matrix = cosine_similarity(embedding_array)
    return similarity_matrix.tolist()


def perform_clustering(embeddings: list[list[float]], num_clusters: int) -> list[int]:
    """K-Means 클러스터링 수행"""
    from sklearn.cluster import KMeans
    import numpy as np
    
    if not embeddings or len(embeddings) < 2:
        return [0] * len(embeddings) if embeddings else []
    
    # 클러스터 수 조정 (노트 수보다 클 수 없음)
    actual_clusters = min(num_clusters, len(embeddings))
    
    embedding_array = np.array(embeddings)
    
    kmeans = KMeans(
        n_clusters=actual_clusters,
        random_state=42,
        n_init="auto"  # type: ignore
    )
    
    labels = kmeans.fit_predict(embedding_array)
    return labels.tolist()


# ─────────────────────────────────────────────────────────────────────────────
# AI 클러스터 라벨 생성 (캐싱 포함)
# ─────────────────────────────────────────────────────────────────────────────

async def generate_cluster_labels_optimized(
    cluster_contents: dict[int, list[str]],
    provider: str,
    api_key: str,
    model: str,
    cache: GraphCache
) -> tuple[dict[int, tuple[str, list[str]]], int, int]:
    """
    AI를 사용하여 클러스터 라벨 및 키워드 생성 (캐싱 포함)
    Returns: (labels, cached_count, generated_count)
    """
    labels = {}
    cached_count = 0
    generated_count = 0
    
    for cluster_id, contents in cluster_contents.items():
        # 클러스터 컨텐츠 해시로 캐시 확인
        cluster_hash = cache.get_cluster_content_hash(contents)
        cached_label = cache.get_cached_cluster_label(cluster_hash)
        
        if cached_label:
            labels[cluster_id] = cached_label
            cached_count += 1
            continue
        
        # 캐시에 없으면 AI로 생성
        sample_text = "\n---\n".join([c[:500] for c in contents[:5]])
        
        prompt = f"""다음은 같은 주제의 노트들입니다. 이 노트들의 공통 주제를 분석해주세요.

노트 내용:
{sample_text}

다음 JSON 형식으로 응답해주세요:
{{
    "label": "2-3단어의 간결한 주제 라벨",
    "keywords": ["키워드1", "키워드2", "키워드3"]
}}

JSON만 출력하세요:"""

        try:
            if provider == "gemini" and api_key:
                from .. import gemini_client
                result = gemini_client.call_json(prompt, '{"label": "", "keywords": []}', api_key, model or None)
            else:
                from .. import ollama_client
                result = ollama_client.call_json(prompt, '{"label": "", "keywords": []}', model or None)
            
            label = result.get("label", f"주제 {cluster_id + 1}")
            keywords = result.get("keywords", [])
            
            # 캐시에 저장
            cache.set_cluster_label(cluster_hash, label, keywords)
            labels[cluster_id] = (label, keywords)
            generated_count += 1
            
        except Exception as e:
            logger.warning(f"Failed to generate label for cluster {cluster_id}: {e}")
            labels[cluster_id] = (f"주제 {cluster_id + 1}", [])
            generated_count += 1
    
    return labels, cached_count, generated_count


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
    
    # 9. 노트 오버라이드 적용 (사용자가 수동으로 클러스터 변경한 경우)
    final_cluster_labels = cluster_labels.copy()
    for i, note in enumerate(notes):
        if note["path"] in note_overrides:
            override_cluster = note_overrides[note["path"]]
            # 유효한 클러스터 ID인지 확인
            if 0 <= override_cluster < len(set(cluster_labels)):
                final_cluster_labels[i] = override_cluster
    
    # 10. 캐시 저장
    cache.save()
    
    # 11. 클러스터별 최종 노트 수 계산 (오버라이드 반영)
    final_cluster_contents: dict[int, list[str]] = {}
    for i, label in enumerate(final_cluster_labels):
        if label not in final_cluster_contents:
            final_cluster_contents[label] = []
        final_cluster_contents[label].append(notes[i]["content"])
    
    # 12. 노드 생성 (커스텀 설정 적용)
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
    
    # 13. 엣지 생성 (유사도 기반)
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
    
    # 14. 클러스터 정보 생성 (커스텀 설정 적용)
    clusters = []
    for cluster_id, contents in final_cluster_contents.items():
        ai_label, ai_keywords = cluster_label_map.get(cluster_id, (f"주제 {cluster_id + 1}", []))
        
        # 커스텀 설정 적용
        custom = customizations.get(str(cluster_id), {})
        final_label = custom.get("label") or ai_label
        final_color = custom.get("color") or CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
        final_keywords = custom.get("keywords") or ai_keywords
        
        clusters.append(ClusterInfo(
            id=cluster_id,
            label=final_label,
            color=final_color,
            noteCount=len(contents),
            keywords=final_keywords
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
