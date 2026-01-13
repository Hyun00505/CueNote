/**
 * CueNote - 그래프 뷰 Composable
 * AI 기반 노트 클러스터링 및 그래프 시각화
 */
import { ref, computed, onUnmounted, type Ref } from 'vue';
import type { GraphNode, GraphEdge, ClusterInfo, GraphData } from '../types';
import { useSettings } from './useSettings';

const BASE_URL = 'http://127.0.0.1:8787';

// 상태
const graphData = ref<GraphData | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const selectedNode = ref<GraphNode | null>(null);
const selectedCluster = ref<ClusterInfo | null>(null);
const hoveredNode = ref<GraphNode | null>(null);

// 필터 상태
const minSimilarity = ref(0.3);
const showOnlyCluster = ref<number | null>(null);

export function useGraph() {
  const { settings } = useSettings();

  /**
   * 그래프 데이터 로드
   */
  const loadGraphData = async () => {
    isLoading.value = true;
    error.value = null;

    try {
      const payload = {
        provider: settings.value.llmProvider || 'ollama',
        api_key: settings.value.geminiApiKey || '',
        model: settings.value.selectedModel || '',
        minSimilarity: minSimilarity.value,
        maxClusters: 8
      };

      const response = await fetch(`${BASE_URL}/graph/data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      graphData.value = data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '그래프 로드 실패';
      console.error('Graph load error:', err);
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 필터링된 노드
   */
  const filteredNodes = computed(() => {
    if (!graphData.value) return [];
    if (showOnlyCluster.value === null) return graphData.value.nodes;
    return graphData.value.nodes.filter(n => n.cluster === showOnlyCluster.value);
  });

  /**
   * 필터링된 엣지
   */
  const filteredEdges = computed(() => {
    if (!graphData.value) return [];
    const nodeIds = new Set(filteredNodes.value.map(n => n.id));
    return graphData.value.edges.filter(e => {
      const sourceId = typeof e.source === 'string' ? e.source : e.source.id;
      const targetId = typeof e.target === 'string' ? e.target : e.target.id;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });
  });

  /**
   * 클러스터 목록
   */
  const clusters = computed(() => graphData.value?.clusters || []);

  /**
   * 노트 통계
   */
  const stats = computed(() => ({
    totalNotes: graphData.value?.totalNotes || 0,
    totalClusters: clusters.value.length,
    totalEdges: graphData.value?.edges.length || 0
  }));

  /**
   * 노드 선택
   */
  const selectNode = (node: GraphNode | null) => {
    selectedNode.value = node;
    if (node) {
      // 해당 클러스터 찾기
      const cluster = clusters.value.find(c => c.id === node.cluster);
      selectedCluster.value = cluster || null;
    }
  };

  /**
   * 클러스터 필터링
   */
  const filterByCluster = (clusterId: number | null) => {
    showOnlyCluster.value = clusterId;
  };

  /**
   * 유사도 임계값 변경
   */
  const setMinSimilarity = (value: number) => {
    minSimilarity.value = value;
  };

  /**
   * 새로고침
   */
  const refresh = async () => {
    await loadGraphData();
  };

  /**
   * 그래프 데이터 초기화 (환경 변경 시)
   */
  const clearGraphData = () => {
    graphData.value = null;
    selectedNode.value = null;
    selectedCluster.value = null;
    hoveredNode.value = null;
    showOnlyCluster.value = null;
    error.value = null;
    lockedNotes.value = new Set();
  };

  /**
   * 클러스터 색상 가져오기
   */
  const getClusterColor = (clusterId: number) => {
    const cluster = clusters.value.find(c => c.id === clusterId);
    return cluster?.color || '#888888';
  };

  /**
   * 노드와 연결된 노드들 찾기
   */
  const getConnectedNodes = (nodeId: string) => {
    if (!graphData.value) return [];
    
    const connectedIds = new Set<string>();
    graphData.value.edges.forEach(e => {
      const sourceId = typeof e.source === 'string' ? e.source : e.source.id;
      const targetId = typeof e.target === 'string' ? e.target : e.target.id;
      
      if (sourceId === nodeId) connectedIds.add(targetId);
      if (targetId === nodeId) connectedIds.add(sourceId);
    });

    return graphData.value.nodes.filter(n => connectedIds.has(n.id));
  };

  // ─────────────────────────────────────────────────────────────────────────
  // 클러스터 커스텀 설정 API
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * 클러스터 설정 업데이트
   */
  const updateCluster = async (clusterId: number, data: { label?: string; color?: string; keywords?: string[] }) => {
    try {
      const response = await fetch(`${BASE_URL}/graph/cluster/${clusterId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: clusterId,
          label: data.label,
          color: data.color,
          keywords: data.keywords
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 로컬 상태 즉시 업데이트 (새로고침 없이)
      if (graphData.value) {
        // 클러스터 목록 업데이트
        const clusterIndex = graphData.value.clusters.findIndex(c => c.id === clusterId);
        if (clusterIndex !== -1) {
          if (data.label) graphData.value.clusters[clusterIndex].label = data.label;
          if (data.color) graphData.value.clusters[clusterIndex].color = data.color;
          if (data.keywords) graphData.value.clusters[clusterIndex].keywords = data.keywords;
        }
        
        // 해당 클러스터의 노드들 색상 업데이트
        if (data.color) {
          graphData.value.nodes.forEach(node => {
            if (node.cluster === clusterId) {
              node.color = data.color!;
            }
          });
        }
      }

      return true;
    } catch (err) {
      console.error('Failed to update cluster:', err);
      return false;
    }
  };

  /**
   * 노트를 다른 클러스터로 이동
   */
  const moveNoteToCluster = async (notePath: string, targetClusterId: number) => {
    try {
      const response = await fetch(`${BASE_URL}/graph/move-note`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notePath,
          targetClusterId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 로컬 상태 즉시 업데이트 (새로고침 없이)
      if (graphData.value) {
        const nodeIndex = graphData.value.nodes.findIndex(n => n.id === notePath);
        if (nodeIndex !== -1) {
          const oldClusterId = graphData.value.nodes[nodeIndex].cluster;
          
          // 노드의 클러스터 및 색상 업데이트
          const targetCluster = graphData.value.clusters.find(c => c.id === targetClusterId);
          graphData.value.nodes[nodeIndex].cluster = targetClusterId;
          if (targetCluster) {
            graphData.value.nodes[nodeIndex].color = targetCluster.color;
            graphData.value.nodes[nodeIndex].clusterLabel = targetCluster.label;
          }
          
          // 클러스터 노트 수 업데이트
          const oldCluster = graphData.value.clusters.find(c => c.id === oldClusterId);
          if (oldCluster && oldCluster.noteCount > 0) {
            oldCluster.noteCount--;
          }
          if (targetCluster) {
            targetCluster.noteCount++;
          }
          
          // selectedNode도 함께 업데이트 (같은 노드라면)
          if (selectedNode.value && selectedNode.value.id === notePath) {
            selectedNode.value.cluster = targetClusterId;
            if (targetCluster) {
              selectedNode.value.color = targetCluster.color;
              selectedNode.value.clusterLabel = targetCluster.label;
            }
            // selectedCluster도 업데이트
            selectedCluster.value = targetCluster || null;
          }
        }
      }

      return true;
    } catch (err) {
      console.error('Failed to move note:', err);
      return false;
    }
  };

  /**
   * 노트의 클러스터 오버라이드 제거 (AI 클러스터링으로 복원)
   */
  const resetNoteCluster = async (notePath: string) => {
    try {
      const encodedPath = encodeURIComponent(notePath);
      const response = await fetch(`${BASE_URL}/graph/move-note/${encodedPath}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await loadGraphData();
      return true;
    } catch (err) {
      console.error('Failed to reset note cluster:', err);
      return false;
    }
  };

  /**
   * 클러스터 설정 초기화 (AI 설정으로 복원)
   */
  const resetClusterSettings = async () => {
    try {
      const response = await fetch(`${BASE_URL}/graph/settings/customizations`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await loadGraphData();
      return true;
    } catch (err) {
      console.error('Failed to reset cluster settings:', err);
      return false;
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  // 노트 클러스터 잠금 API
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * 잠금된 노트 목록
   */
  const lockedNotes = ref<Set<string>>(new Set());

  /**
   * 잠금된 노트 목록 로드
   */
  const loadLockedNotes = async () => {
    try {
      const response = await fetch(`${BASE_URL}/graph/locked-notes`);
      if (response.ok) {
        const data = await response.json();
        lockedNotes.value = new Set(data.lockedNotes || []);
      }
    } catch (err) {
      console.error('Failed to load locked notes:', err);
    }
  };

  /**
   * 노트 클러스터 잠금/해제
   */
  const toggleNoteLock = async (notePath: string, lock: boolean) => {
    try {
      const response = await fetch(`${BASE_URL}/graph/lock-note`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notePath, locked: lock })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 로컬 상태 업데이트 (새 Set 생성으로 reactivity 보장)
      const newSet = new Set(lockedNotes.value);
      if (lock) {
        newSet.add(notePath);
      } else {
        newSet.delete(notePath);
      }
      lockedNotes.value = newSet;

      return true;
    } catch (err) {
      console.error('Failed to toggle note lock:', err);
      return false;
    }
  };

  /**
   * 노트가 잠금되어 있는지 확인
   */
  const isNoteLocked = (notePath: string) => {
    return lockedNotes.value.has(notePath);
  };

  /**
   * 여러 노트 일괄 잠금/해제
   */
  const lockNotesBatch = async (notePaths: string[], lock: boolean) => {
    try {
      const response = await fetch(`${BASE_URL}/graph/lock-notes-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notePaths, locked: lock })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 로컬 상태 업데이트 (새 Set 생성으로 reactivity 보장)
      const newSet = new Set(lockedNotes.value);
      notePaths.forEach(path => {
        if (lock) {
          newSet.add(path);
        } else {
          newSet.delete(path);
        }
      });
      lockedNotes.value = newSet;

      return true;
    } catch (err) {
      console.error('Failed to batch lock notes:', err);
      return false;
    }
  };

  /**
   * 현재 필터된 노트들의 잠금 상태 확인
   */
  const areAllFilteredNodesLocked = computed(() => {
    const nodes = filteredNodes.value;
    if (nodes.length === 0) return false;
    return nodes.every(n => lockedNotes.value.has(n.id));
  });

  /**
   * 새 클러스터 생성
   */
  const createCluster = async (label: string, color: string, keywords: string[] = []) => {
    try {
      const response = await fetch(`${BASE_URL}/graph/cluster/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label, color, keywords })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      
      // 로컬 상태 업데이트 (새 클러스터 추가)
      if (graphData.value && result.cluster) {
        graphData.value.clusters.push(result.cluster);
      }

      return result.cluster;
    } catch (err) {
      console.error('Failed to create cluster:', err);
      return null;
    }
  };

  /**
   * 클러스터 삭제
   */
  const deleteCluster = async (clusterId: number) => {
    try {
      const response = await fetch(`${BASE_URL}/graph/cluster/${clusterId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // 로컬 상태 업데이트 (클러스터 제거)
      if (graphData.value) {
        graphData.value.clusters = graphData.value.clusters.filter(c => c.id !== clusterId);
        // 해당 클러스터의 노트들 업데이트
        graphData.value.nodes = graphData.value.nodes.filter(n => n.cluster !== clusterId);
      }

      return true;
    } catch (err) {
      console.error('Failed to delete cluster:', err);
      return false;
    }
  };

  return {
    // 상태
    graphData,
    isLoading,
    error,
    selectedNode,
    selectedCluster,
    hoveredNode,
    minSimilarity,
    showOnlyCluster,

    // Computed
    filteredNodes,
    filteredEdges,
    clusters,
    stats,

    // 메서드
    loadGraphData,
    selectNode,
    filterByCluster,
    setMinSimilarity,
    refresh,
    clearGraphData,
    getClusterColor,
    getConnectedNodes,

    // 클러스터 커스텀 설정
    updateCluster,
    moveNoteToCluster,
    resetNoteCluster,
    resetClusterSettings,

    // 클러스터 생성/삭제
    createCluster,
    deleteCluster,

    // 노트 클러스터 잠금
    lockedNotes,
    loadLockedNotes,
    toggleNoteLock,
    isNoteLocked,
    lockNotesBatch,
    areAllFilteredNodesLocked
  };
}
