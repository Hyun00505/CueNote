"""
CueNote Core - Graph 캐시 시스템
노트 임베딩, 클러스터 설정, 잠금 상태 등을 관리
"""
import json
import hashlib
import time
from typing import Optional
from pathlib import Path

from ..config import logger, PROJECT_ROOT

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
    
    # ─────────────────────────────────────────────────────────────────────────
    # 노트 클러스터 잠금 관리
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_locked_notes(self) -> set[str]:
        """잠금된 노트 목록 가져오기"""
        return set(self.cache_data.get("locked_notes", []))
    
    def is_note_locked(self, note_path: str) -> bool:
        """노트가 잠금되어 있는지 확인"""
        return note_path in self.get_locked_notes()
    
    def lock_note(self, note_path: str):
        """노트 클러스터 잠금 (AI 자동 분류 비활성화)"""
        if "locked_notes" not in self.cache_data:
            self.cache_data["locked_notes"] = []
        
        if note_path not in self.cache_data["locked_notes"]:
            self.cache_data["locked_notes"].append(note_path)
    
    def unlock_note(self, note_path: str):
        """노트 클러스터 잠금 해제"""
        if "locked_notes" in self.cache_data:
            if note_path in self.cache_data["locked_notes"]:
                self.cache_data["locked_notes"].remove(note_path)
    
    # ─────────────────────────────────────────────────────────────────────────
    # AI 클러스터 할당 정보 (그래프 생성 시 자동 저장)
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_ai_cluster_assignments(self) -> dict[str, int]:
        """AI가 분류한 노트별 클러스터 ID 가져오기"""
        return self.cache_data.get("ai_cluster_assignments", {})
    
    def set_ai_cluster_assignments(self, assignments: dict[str, int]):
        """AI 클러스터 할당 정보 저장"""
        self.cache_data["ai_cluster_assignments"] = assignments
    
    def get_note_cluster_id(self, note_path: str) -> Optional[int]:
        """노트의 최종 클러스터 ID 가져오기 (오버라이드 > AI 자동)"""
        overrides = self.get_note_overrides()
        if note_path in overrides:
            return overrides[note_path]
        
        assignments = self.get_ai_cluster_assignments()
        return assignments.get(note_path)
    
    # ─────────────────────────────────────────────────────────────────────────
    # AI 클러스터 라벨 정보 (클러스터 ID 기준)
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_ai_cluster_labels(self) -> dict[int, tuple[str, list[str]]]:
        """AI가 생성한 클러스터별 라벨 및 키워드"""
        raw = self.cache_data.get("ai_cluster_label_info", {})
        return {int(k): (v["label"], v["keywords"]) for k, v in raw.items()}
    
    def set_ai_cluster_labels(self, labels: dict[int, tuple[str, list[str]]]):
        """AI 클러스터 라벨 정보 저장 (클러스터 ID -> (라벨, 키워드))"""
        self.cache_data["ai_cluster_label_info"] = {
            str(k): {"label": v[0], "keywords": v[1]} for k, v in labels.items()
        }
    
    def clear_customizations(self):
        """모든 커스텀 설정 초기화"""
        self.cache_data["cluster_customizations"] = {}
        self.cache_data["note_overrides"] = {}
        self.cache_data["locked_notes"] = []
        self.cache_data["custom_edges"] = {"added": [], "removed": []}
    
    # ─────────────────────────────────────────────────────────────────────────
    # 사용자 정의 엣지 관리
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_custom_edges(self) -> dict[str, list[list[str]]]:
        """사용자 정의 엣지 가져오기 (추가/삭제 목록)"""
        return self.cache_data.get("custom_edges", {"added": [], "removed": []})
    
    def add_custom_edge(self, source: str, target: str):
        """사용자 정의 엣지 추가"""
        if "custom_edges" not in self.cache_data:
            self.cache_data["custom_edges"] = {"added": [], "removed": []}
        
        edge = sorted([source, target])
        
        # 삭제 목록에 있으면 제거
        self._remove_from_list(self.cache_data["custom_edges"]["removed"], edge)
        
        # 추가 목록에 없으면 추가
        if edge not in self.cache_data["custom_edges"]["added"]:
            self.cache_data["custom_edges"]["added"].append(edge)
    
    def remove_custom_edge(self, source: str, target: str):
        """사용자 정의 엣지 삭제 (시스템 생성 엣지 숨김)"""
        if "custom_edges" not in self.cache_data:
            self.cache_data["custom_edges"] = {"added": [], "removed": []}
        
        edge = sorted([source, target])
        
        # 추가 목록에 있으면 제거
        self._remove_from_list(self.cache_data["custom_edges"]["added"], edge)
        
        # 삭제 목록에 없으면 추가 (시스템 생성 엣지 숨김)
        if edge not in self.cache_data["custom_edges"]["removed"]:
            self.cache_data["custom_edges"]["removed"].append(edge)
    
    def _remove_from_list(self, lst: list[list[str]], edge: list[str]):
        """리스트에서 엣지 제거"""
        for i, e in enumerate(lst):
            if sorted(e) == edge:
                lst.pop(i)
                return
    
    def is_edge_removed(self, source: str, target: str) -> bool:
        """엣지가 사용자에 의해 삭제되었는지 확인"""
        custom_edges = self.get_custom_edges()
        edge = sorted([source, target])
        return edge in custom_edges["removed"]
    
    def is_edge_custom_added(self, source: str, target: str) -> bool:
        """엣지가 사용자에 의해 추가되었는지 확인"""
        custom_edges = self.get_custom_edges()
        edge = sorted([source, target])
        return edge in custom_edges["added"]
    
    def save(self):
        """캐시 저장"""
        self._save_cache()
