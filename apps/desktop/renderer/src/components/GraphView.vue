<template>
  <div class="graph-view">
    <GraphVisualizer
      ref="visualizerRef"
      :nodes="renderedNodes"
      :edges="renderedEdges"
      :width="dimensions.width"
      :height="dimensions.height"
      :selected-node="selectedNode"
      :hovered-node="hoveredNode"
      :search-matches="searchMatchIds"
      @node-click="handleNodeClick"
      @node-dblclick="handleNodeDblClick"
      @node-hover="handleNodeHover"
      @node-contextmenu="handleNodeContextMenu"
    >
      <template #loading-error-empty>
        <GraphEmptyState
          :loading="isLoading"
          :error="error"
          :is-empty="!graphData || graphData.totalNotes === 0"
          :cluster-empty="filteredNodes.length === 0"
          @refresh="handleRefresh"
        />
      </template>

      <template #overlays>
        <GraphControls
          @zoom-in="visualizerRef?.zoomIn()"
          @zoom-out="visualizerRef?.zoomOut()"
          @reset-zoom="visualizerRef?.resetZoom()"
        />
      </template>
    </GraphVisualizer>

    <GraphContextMenu
      :show="showContextMenu"
      :pos="contextMenuPos"
      :node="contextMenuNode"
      @open-note="handleOpenNote"
      @show-related="handleShowRelated"
    />

    <GraphDetailPanel
      :selected-node="selectedNode"
      :connected-notes="connectedNotes"
      :related-notes="relatedNotes"
      :clusters="clusters"
      @close="selectNode(null)"
      @open-node="handleNodeClick"
      @open-file="handleOpenNote"
      @focus-node="handleFocusNode"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useGraph } from '../composables/useGraph';
import { useEnvironment } from '../composables/useEnvironment';
import type { GraphNode } from '../types';

import GraphVisualizer from './graph/GraphVisualizer.vue';
import GraphEmptyState from './graph/GraphEmptyState.vue';
import GraphControls from './graph/GraphControls.vue';
import GraphContextMenu from './graph/GraphContextMenu.vue';
import GraphDetailPanel from './graph/GraphDetailPanel.vue';

// Props & Emits
const props = defineProps<{
  filterClusterId?: number | null | 'unclustered';
  isActive?: boolean;
}>();

const emit = defineEmits<{
  (e: 'select-file', path: string): void;
  (e: 'graph-loaded', data: { clusters: any[]; stats: any }): void;
}>();

// Composable
const {
  graphData,
  isLoading,
  error,
  selectedNode,
  hoveredNode,
  showOnlyCluster,
  filteredNodes,
  filteredEdges,
  clusters,
  stats,
  relatedNotes,
  searchQuery,
  searchResults,
  loadGraphData,
  selectNode,
  filterByCluster,
  refresh,
  clearGraphData,
  getConnectedNodes,
  searchInGraph
} = useGraph();

const visualizerRef = ref<InstanceType<typeof GraphVisualizer> | null>(null);

// 시뮬레이션용 데이터
const renderedNodes = computed(() => filteredNodes.value);
const renderedEdges = computed(() => filteredEdges.value);

// 치수
const dimensions = computed(() => ({
  width: 1200,
  height: 800
}));

// 연결된 노트
const connectedNotes = computed(() => {
  if (!selectedNode.value) return [];
  return getConnectedNodes(selectedNode.value.id);
});

// 검색 매칭 노드 ID
const searchMatchIds = computed(() => {
  if (!searchQuery.value.trim()) return new Set<string>();
  return new Set(searchResults.value.map(r => r.path));
});

// 컨텍스트 메뉴 상태
const showContextMenu = ref(false);
const contextMenuPos = ref({ x: 0, y: 0 });
const contextMenuNode = ref<GraphNode | null>(null);

// 노드 우클릭 핸들러
const handleNodeContextMenu = (event: MouseEvent, node: GraphNode) => {
  contextMenuNode.value = node;
  contextMenuPos.value = { x: event.clientX, y: event.clientY };
  showContextMenu.value = true;
};

// 컨텍스트 메뉴 외부 클릭 시 닫기
const handleOutsideClick = () => {
  if (showContextMenu.value) {
    showContextMenu.value = false;
    contextMenuNode.value = null;
  }
};

const handleRefresh = async () => {
  if (isLoadingGraph.value) return;
  isLoadingGraph.value = true;
  try {
    await loadGraphData();
    lastLoadedEnvId.value = currentEnvId.value;
  } finally {
    isLoadingGraph.value = false;
  }
};

const handleNodeHover = (node: GraphNode | null) => {
  hoveredNode.value = node;
};

const handleNodeClick = (node: GraphNode) => {
  selectNode(node);
};

const handleNodeDblClick = (node: GraphNode) => {
  emit('select-file', node.id);
};

const handleOpenNote = (path?: string) => {
  const target = path || contextMenuNode.value?.id || selectedNode.value?.id;
  if (target) {
    emit('select-file', target);
  }
  showContextMenu.value = false;
};

const handleShowRelated = () => {
  if (contextMenuNode.value) {
    selectNode(contextMenuNode.value);
  }
  showContextMenu.value = false;
};

const handleFocusNode = (nodeId: string) => {
  const node = graphData.value?.nodes.find(n => n.id === nodeId);
  if (node) {
    selectNode(node);
    visualizerRef.value?.focusNode?.(node);
  }
};

// Props 감시
watch(() => props.filterClusterId, (newVal) => {
  filterByCluster(newVal ?? null);
});

// 환경 감시
const { currentId: currentEnvId } = useEnvironment();
const lastLoadedEnvId = ref<string | null>(null);
const isLoadingGraph = ref(false);

async function loadGraphForCurrentEnv() {
  if (isLoadingGraph.value) return;
  
  isLoadingGraph.value = true;
  try {
    lastLoadedEnvId.value = currentEnvId.value;
    clearGraphData();
    await loadGraphData();
  } finally {
    isLoadingGraph.value = false;
  }
}

watch(() => props.isActive, async (newVal) => {
  if (newVal) {
    const envChanged = lastLoadedEnvId.value !== currentEnvId.value;
    const noData = !graphData.value || graphData.value.nodes.length === 0;
    
    if (envChanged || noData) {
      await loadGraphForCurrentEnv();
    }
  }
}, { immediate: true });

watch(currentEnvId, async (newEnvId) => {
  if (newEnvId && newEnvId !== lastLoadedEnvId.value && props.isActive) {
    await loadGraphForCurrentEnv();
  }
});

watch(graphData, (newData) => {
  if (newData) {
    emit('graph-loaded', {
      clusters: clusters.value,
      stats: stats.value
    });
  }
}, { immediate: true });

defineExpose({
  refresh: handleRefresh,
  filterByCluster,
  clusters,
  stats,
  isLoading,
  searchInGraph
});

onMounted(async () => {
  await loadGraphData();
  document.addEventListener('click', handleOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick);
});
</script>

<style scoped>
.graph-view {
  display: flex;
  height: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow: hidden;
  position: relative;
}
</style>
