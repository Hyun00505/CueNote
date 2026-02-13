/**
 * CueNote - 그래프 뷰 Composable (간소화)
 * AI 기반 노트 클러스터링 및 그래프 시각화
 */
import { ref, computed } from 'vue';
import type { GraphNode, GraphEdge, ClusterInfo, GraphData, RelatedNote } from '../types';
import { API_BASE_URL } from '../config/api';

// 전역 상태
const graphData = ref<GraphData | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const selectedNode = ref<GraphNode | null>(null);
const hoveredNode = ref<GraphNode | null>(null);
const relatedNotes = ref<RelatedNote[]>([]);
const searchQuery = ref('');
const searchResults = ref<{ path: string; title: string; preview: string }[]>([]);

// 필터 상태
const minSimilarity = ref(0.1);
const showOnlyCluster = ref<number | null | 'unclustered'>(null);

export function useGraph() {
  // 그래프 데이터 로드
  async function loadGraphData() {
    isLoading.value = true;
    error.value = null;
    
    try {
      // LLM 설정 가져오기
      const settingsRes = await fetch(`${API_BASE_URL}/llm/settings`);
      const settings = settingsRes.ok ? await settingsRes.json() : {};
      
      const response = await fetch(`${API_BASE_URL}/graph/data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: settings.provider || 'ollama',
          api_key: settings.api_key || '',
          model: settings.model || '',
          minSimilarity: minSimilarity.value,
          maxClusters: 8
        })
      });
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data: GraphData = await response.json();
      graphData.value = data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : '알 수 없는 오류';
      console.error('Graph data load failed:', e);
    } finally {
      isLoading.value = false;
    }
  }

  // 노드 필터링
  const filteredNodes = computed(() => {
    if (!graphData.value) return [];
    
    const nodes = graphData.value.nodes;
    let result = nodes;
    
    // 클러스터 필터
    if (showOnlyCluster.value !== null) {
      if (showOnlyCluster.value === 'unclustered') {
        result = result.filter(n => n.cluster === -1);
      } else {
        result = result.filter(n => n.cluster === showOnlyCluster.value);
      }
    }
    
    return result;
  });

  // 엣지 필터링
  const filteredEdges = computed<GraphEdge[]>(() => {
    if (!graphData.value) return [];
    
    const nodeIds = new Set(filteredNodes.value.map(n => n.id));
    
    return graphData.value.edges.filter(e => {
      const sourceId = typeof e.source === 'string' ? e.source : e.source.id;
      const targetId = typeof e.target === 'string' ? e.target : e.target.id;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });
  });

  // 클러스터 목록
  const clusters = computed<ClusterInfo[]>(() => {
    return graphData.value?.clusters || [];
  });

  // 미분류 노트 수
  const unclusteredCount = computed(() => {
    if (!graphData.value) return 0;
    return graphData.value.nodes.filter(n => n.cluster === -1).length;
  });

  // 통계
  const stats = computed(() => {
    if (!graphData.value) return null;
    return {
      totalNotes: graphData.value.totalNotes,
      totalClusters: graphData.value.clusters.length,
      totalEdges: graphData.value.edges.length
    };
  });

  // 노드 선택
  function selectNode(node: GraphNode | null) {
    selectedNode.value = node;
    // 노드 선택 시 관련 노트 자동 로드
    if (node) {
      fetchRelatedNotes(node.id);
    } else {
      relatedNotes.value = [];
    }
  }

  // 클러스터 필터링
  function filterByCluster(clusterId: number | null | 'unclustered') {
    showOnlyCluster.value = clusterId;
    selectedNode.value = null;
    relatedNotes.value = [];
  }

  // 유사도 임계값 변경
  function setMinSimilarity(value: number) {
    minSimilarity.value = value;
    loadGraphData();
  }

  // 새로고침
  function refresh() {
    loadGraphData();
  }

  // 그래프 데이터 초기화 (환경 변경 시)
  function clearGraphData() {
    graphData.value = null;
    selectedNode.value = null;
    hoveredNode.value = null;
    relatedNotes.value = [];
    searchQuery.value = '';
    searchResults.value = [];
    error.value = null;
    showOnlyCluster.value = null;
  }

  // 클러스터 색상 가져오기
  function getClusterColor(clusterId: number): string {
    const cluster = clusters.value.find(c => c.id === clusterId);
    return cluster?.color || '#888888';
  }

  // 노드와 연결된 노트 찾기
  function getConnectedNodes(nodeId: string): GraphNode[] {
    if (!graphData.value) return [];
    
    const connectedIds = new Set<string>();
    for (const edge of graphData.value.edges) {
      const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
      const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
      
      if (sourceId === nodeId) connectedIds.add(targetId);
      if (targetId === nodeId) connectedIds.add(sourceId);
    }
    
    return graphData.value.nodes.filter(n => connectedIds.has(n.id));
  }

  // 관련 노트 추천 가져오기
  async function fetchRelatedNotes(notePath: string) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/graph/related/${encodeURIComponent(notePath)}?top_n=8`
      );
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      relatedNotes.value = data.relatedNotes || [];
    } catch (e) {
      console.error('Related notes fetch failed:', e);
      relatedNotes.value = [];
    }
  }

  // 그래프 내 검색
  async function searchInGraph(query: string) {
    searchQuery.value = query;
    
    if (!query.trim()) {
      searchResults.value = [];
      return;
    }
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/graph/search?q=${encodeURIComponent(query)}`
      );
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      searchResults.value = data.matches || [];
    } catch (e) {
      console.error('Graph search failed:', e);
      searchResults.value = [];
    }
  }

  return {
    // State
    graphData,
    isLoading,
    error,
    selectedNode,
    hoveredNode,
    filteredNodes,
    filteredEdges,
    clusters,
    stats,
    showOnlyCluster,
    unclusteredCount,
    relatedNotes,
    searchQuery,
    searchResults,
    
    // Actions
    loadGraphData,
    selectNode,
    filterByCluster,
    setMinSimilarity,
    refresh,
    clearGraphData,
    getClusterColor,
    getConnectedNodes,
    fetchRelatedNotes,
    searchInGraph
  };
}
