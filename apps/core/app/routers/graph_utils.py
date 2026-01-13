"""
CueNote Core - Graph 유틸리티 함수
임베딩, 클러스터링, AI 라벨 생성 등
"""
import json
import re
from typing import Optional
from pathlib import Path

from ..config import logger, PROJECT_ROOT
from .graph_cache import GraphCache

# 환경 설정 파일 경로 (vault.py와 동일)
ENV_CONFIG_PATH = PROJECT_ROOT / "apps" / "core" / "data" / "environments.json"
DEFAULT_VAULT_PATH = PROJECT_ROOT / "data"


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
