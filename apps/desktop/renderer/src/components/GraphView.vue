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
      :link-edit-mode="linkEditMode"
      :link-source-node="linkSourceNode"
      :is-note-locked="isNoteLocked"
      :has-edge-between="hasEdgeBetween"
      @node-click="handleNodeClick"
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
        <!-- 연결 편집 모드 오버레이 -->
        <div
          v-if="linkEditMode"
          class="link-edit-overlay"
          @click="cancelLinkEdit"
        >
          <div
            class="link-edit-banner"
            @click.stop
          >
            <div class="link-edit-icon">
              <!-- 아이콘 생략 (간소화) -->
              <svg
                v-if="linkEditMode === 'add'"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line
                  x1="12"
                  y1="5"
                  x2="12"
                  y2="19"
                />
                <line
                  x1="5"
                  y1="12"
                  x2="19"
                  y2="12"
                />
              </svg>
              <svg
                v-else
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line
                  x1="5"
                  y1="12"
                  x2="19"
                  y2="12"
                />
              </svg>
            </div>
            <div class="link-edit-text">
              <strong>{{ linkSourceNode?.label }}</strong>
              <span>{{ linkEditMode === 'add' ? '에 연결할 노드를 클릭하세요' : '에서 연결을 삭제할 노드를 클릭하세요' }}</span>
            </div>
            <button
              class="link-edit-cancel"
              @click="cancelLinkEdit"
            >
              취소
            </button>
          </div>
        </div>

        <GraphControls
          :show-only-cluster="showOnlyCluster"
          :are-all-filtered-nodes-locked="areAllFilteredNodesLocked"
          @zoom-in="visualizerRef?.zoomIn()"
          @zoom-out="visualizerRef?.zoomOut()"
          @reset-zoom="visualizerRef?.resetZoom()"
          @lock-all="handleLockAllFiltered"
        />
      </template>
    </GraphVisualizer>

    <GraphContextMenu
      :show="showContextMenu"
      :pos="contextMenuPos"
      :node="contextMenuNode"
      :clusters="clusters"
      :is-locked="contextMenuNode ? isNoteLocked(contextMenuNode.id) : false"
      @move-to-cluster="handleMoveToCluster"
      @start-link-add="startLinkAdd"
      @start-link-remove="startLinkRemove"
      @toggle-lock="handleToggleLock"
      @reset-cluster="handleResetNoteCluster"
    />

    <GraphDetailPanel
      :selected-node="selectedNode"
      :selected-cluster="selectedCluster"
      :clusters="clusters"
      :connected-notes="connectedNotes"
      :is-locked="selectedNode ? isNoteLocked(selectedNode.id) : false"
      @close="selectNode(null)"
      @move-cluster="handleMoveSelectedToCluster"
      @toggle-lock="handleToggleSelectedLock"
      @open-node="handleNodeClick"
      @open-file="handleOpenNote"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
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
  selectedCluster,
  hoveredNode,
  showOnlyCluster,
  filteredNodes,
  filteredEdges,
  clusters,
  stats,
  loadGraphData,
  selectNode,
  filterByCluster,
  refresh,
  clearGraphData,
  getConnectedNodes,
  moveNoteToCluster,
  resetNoteCluster,
  loadLockedNotes,
  toggleNoteLock,
  isNoteLocked,
  lockNotesBatch,
  areAllFilteredNodesLocked,
  addCustomEdge,
  removeCustomEdge
} = useGraph();

const visualizerRef = ref<InstanceType<typeof GraphVisualizer> | null>(null);

// 시뮬레이션용 데이터 (GraphVisualizer와의 인터페이스용)
// useGraph의 filteredNodes는 반응형이므로, 이를 그대로 전달하면 Visualizer 내부에서 복사하여 시뮬레이션 돌림
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

// 컨텍스트 메뉴 상태
const showContextMenu = ref(false);
const contextMenuPos = ref({ x: 0, y: 0 });
const contextMenuNode = ref<GraphNode | null>(null);

// 연결 편집 모드 상태
const linkEditMode = ref<'add' | 'remove' | null>(null);
const linkSourceNode = ref<GraphNode | null>(null);

/**
 * 노드 우클릭 핸들러
 */
const handleNodeContextMenu = (event: MouseEvent, node: GraphNode) => {
  contextMenuNode.value = node;
  contextMenuPos.value = { x: event.clientX, y: event.clientY };
  showContextMenu.value = true;
};

/**
 * 노트를 다른 클러스터로 이동
 */
const handleMoveToCluster = async (clusterId: number) => {
  if (!contextMenuNode.value) return;
  
  await moveNoteToCluster(contextMenuNode.value.id, clusterId);
  showContextMenu.value = false;
  contextMenuNode.value = null;
  
  // 시뮬레이션 재시작 (Visualizer 내부 watcher 가 처리)
};

/**
 * 노트의 클러스터 오버라이드 제거 (AI 클러스터링으로 복원)
 */
const handleResetNoteCluster = async () => {
  if (!contextMenuNode.value) return;
  if (isNoteLocked(contextMenuNode.value.id)) return;
  
  await resetNoteCluster(contextMenuNode.value.id);
  showContextMenu.value = false;
  contextMenuNode.value = null;
};

/**
 * 노트 클러스터 잠금/해제 토글 (컨텍스트 메뉴)
 */
const handleToggleLock = async () => {
  if (!contextMenuNode.value) return;
  
  const isLocked = isNoteLocked(contextMenuNode.value.id);
  await toggleNoteLock(contextMenuNode.value.id, !isLocked);
};

/**
 * 선택된 노드를 다른 클러스터로 이동 (상세 패널)
 */
const handleMoveSelectedToCluster = async (clusterId: number) => {
  if (!selectedNode.value) return;
  if (selectedNode.value.cluster === clusterId) return;
  
  await moveNoteToCluster(selectedNode.value.id, clusterId);
};

/**
 * 선택된 노드 잠금/해제 토글 (상세 패널)
 */
const handleToggleSelectedLock = async () => {
  if (!selectedNode.value) return;
  
  const isLocked = isNoteLocked(selectedNode.value.id);
  await toggleNoteLock(selectedNode.value.id, !isLocked);
};

/**
 * 현재 필터된 모든 노트 잠금/해제
 */
const handleLockAllFiltered = async () => {
  const nodes = filteredNodes.value;
  if (nodes.length === 0) return;
  
  const allLocked = areAllFilteredNodesLocked.value;
  const notePaths = nodes.map(n => n.id);
  
  await lockNotesBatch(notePaths, !allLocked);
};

/**
 * 연결 추가 모드 시작
 */
const startLinkAdd = () => {
  linkEditMode.value = 'add';
  linkSourceNode.value = contextMenuNode.value;
  showContextMenu.value = false;
};

/**
 * 연결 삭제 모드 시작
 */
const startLinkRemove = () => {
  linkEditMode.value = 'remove';
  linkSourceNode.value = contextMenuNode.value;
  showContextMenu.value = false;
};

/**
 * 연결 편집 모드 취소
 */
const cancelLinkEdit = () => {
  linkEditMode.value = null;
  linkSourceNode.value = null;
};

/**
 * 두 노드 간 연결 존재 여부 확인
 */
const hasEdgeBetween = (node1: string, node2: string): boolean => {
  if (!graphData.value) return false;
  return graphData.value.edges.some(
    e => (e.source === node1 && e.target === node2) ||
         (e.source === node2 && e.target === node1)
  );
};

/**
 * 연결 편집 완료 (두 번째 노드 클릭)
 */
const completeLinkEdit = async (targetNode: GraphNode) => {
  if (!linkSourceNode.value || linkSourceNode.value.id === targetNode.id) {
    cancelLinkEdit();
    return;
  }
  
  const source = linkSourceNode.value.id;
  const target = targetNode.id;
  
  if (linkEditMode.value === 'add') {
    await addCustomEdge(source, target);
  } else if (linkEditMode.value === 'remove') {
    await removeCustomEdge(source, target);
  }
  
  cancelLinkEdit();
};

/**
 * 컨텍스트 메뉴 외부 클릭 시 닫기
 */
const handleOutsideClick = (event: MouseEvent) => {
  if (showContextMenu.value) {
    showContextMenu.value = false;
    contextMenuNode.value = null;
  }
};

const handleRefresh = async () => {
  if (isLoadingGraph.value) return;
  isLoadingGraph.value = true;
  try {
    await loadLockedNotes();
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
  if (linkEditMode.value && linkSourceNode.value) {
    completeLinkEdit(node);
    return;
  }
  selectNode(node);
};

const handleOpenNote = (path?: string) => {
  const target = path || selectedNode.value?.id;
  if (target) {
    emit('select-file', target);
  }
};

// Props 감시
watch(() => props.filterClusterId, (newVal) => {
  filterByCluster(newVal ?? null);
});

// 환경 감시 (환경 변경 시 그래프 데이터 재로드)
const { currentId: currentEnvId } = useEnvironment();
const lastLoadedEnvId = ref<string | null>(null);
const isLoadingGraph = ref(false);

async function loadGraphForCurrentEnv() {
  if (isLoadingGraph.value) return;
  
  isLoadingGraph.value = true;
  try {
    lastLoadedEnvId.value = currentEnvId.value;
    clearGraphData();
    await loadLockedNotes();
    await loadGraphData();
  } finally {
    isLoadingGraph.value = false;
  }
}

watch(() => props.isActive, async (newVal, oldVal) => {
  if (newVal) {
    const envChanged = lastLoadedEnvId.value !== currentEnvId.value;
    const noData = !graphData.value || graphData.value.nodes.length === 0;
    
    if (envChanged || noData) {
      await loadGraphForCurrentEnv();
    }
  }
}, { immediate: true });

watch(currentEnvId, async (newEnvId, oldEnvId) => {
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
  isLoading
});

onMounted(async () => {
  await loadLockedNotes();
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

/* 연결 편집 모드 오버레이 (GraphVisualizer 내부 슬롯에서 사용) */
.link-edit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 100;
}

.link-edit-banner {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  pointer-events: auto;
}

.link-edit-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--accent-primary, #8b5cf6);
  border-radius: 8px;
  color: white;
}

.link-edit-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.link-edit-text strong {
  font-size: 13px;
  color: var(--text-primary);
}

.link-edit-text span {
  font-size: 11px;
  color: var(--text-muted);
}

.link-edit-cancel {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.link-edit-cancel:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  color: #ef4444;
}
</style>
