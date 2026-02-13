"""
CueNote Core - Graph 캐시 시스템 (간소화)
노트 임베딩 및 클러스터 라벨 캐싱만 관리
"""
import json
import hashlib
import time
from typing import Optional
from pathlib import Path

from ..config import logger, DATA_DIR

# 캐시 파일 경로
CACHE_DIR = DATA_DIR / ".graph_cache"

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


class GraphCache:
    """그래프 데이터 캐싱 관리 (간소화)"""
    
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
    
    # ─────────────────────────────────────────────────────────────────────────
    # 임베딩 캐시
    # ─────────────────────────────────────────────────────────────────────────
    
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
    
    # ─────────────────────────────────────────────────────────────────────────
    # 클러스터 라벨 캐시
    # ─────────────────────────────────────────────────────────────────────────
    
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
    
    # ─────────────────────────────────────────────────────────────────────────
    # 캐시 관리
    # ─────────────────────────────────────────────────────────────────────────
    
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
    
    def save(self):
        """캐시 저장"""
        self._save_cache()
