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

      // 그래프 데이터 새로고침
      await loadGraphData();
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

      // 그래프 데이터 새로고침
      await loadGraphData();
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
    getClusterColor,
    getConnectedNodes,

    // 클러스터 커스텀 설정
    updateCluster,
    moveNoteToCluster,
    resetNoteCluster,
    resetClusterSettings
  };
}
