<template>
  <div class="graph-view">
    <!-- 메인 그래프 영역 -->
    <main class="graph-container" ref="containerRef">
      <!-- 로딩 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" stroke-opacity="0.25" />
            <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round">
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 12 12"
                to="360 12 12"
                dur="1s"
                repeatCount="indefinite"
              />
            </path>
          </svg>
          <span>AI가 노트를 분석하고 있습니다...</span>
        </div>
      </div>

      <!-- 에러 -->
      <div v-else-if="error" class="error-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <p>{{ error }}</p>
        <button @click="handleRefresh">다시 시도</button>
      </div>

      <!-- 빈 상태 -->
      <div v-else-if="!graphData || graphData.totalNotes === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="3" />
          <circle cx="4" cy="8" r="2" />
          <circle cx="20" cy="8" r="2" />
          <circle cx="4" cy="16" r="2" />
          <circle cx="20" cy="16" r="2" />
        </svg>
        <h3>노트를 추가해주세요</h3>
        <p>노트가 있어야 AI 클러스터링을 할 수 있습니다.</p>
      </div>

      <!-- SVG 그래프 -->
      <svg
        v-else
        ref="svgRef"
        class="graph-svg"
        :viewBox="`0 0 ${dimensions.width} ${dimensions.height}`"
      >
        <defs>
          <!-- 그라데이션 필터 -->
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g class="zoom-group" ref="zoomGroupRef">
          <!-- 엣지 -->
          <g class="edges">
            <line
              v-for="(edge, index) in renderedEdges"
              :key="`edge-${index}`"
              class="edge"
              :x1="edge.sourceX"
              :y1="edge.sourceY"
              :x2="edge.targetX"
              :y2="edge.targetY"
              :stroke-opacity="edge.opacity"
              :stroke-width="edge.width"
            />
          </g>

          <!-- 노드 -->
          <g class="nodes">
            <g
              v-for="node in renderedNodes"
              :key="node.id"
              class="node"
              :class="{ 
                selected: selectedNode?.id === node.id,
                dimmed: hoveredNode && hoveredNode.id !== node.id && !isConnected(hoveredNode.id, node.id),
                locked: isNoteLocked(node.id)
              }"
              :transform="`translate(${node.x}, ${node.y})`"
              @mouseenter="handleNodeHover(node)"
              @mouseleave="handleNodeHover(null)"
              @click="handleNodeClick(node)"
              @contextmenu.prevent="handleNodeContextMenu($event, node)"
            >
              <circle
                class="node-circle"
                :r="getNodeRadius(node)"
                :fill="node.color"
                :filter="selectedNode?.id === node.id ? 'url(#glow)' : undefined"
              />
              <!-- 잠금 아이콘 -->
              <g v-if="isNoteLocked(node.id)" class="lock-icon" :transform="`translate(${getNodeRadius(node) - 4}, ${-getNodeRadius(node) + 4})`">
                <circle r="8" fill="var(--bg-primary)" stroke="var(--accent-primary, #8b5cf6)" stroke-width="1.5" />
                <path 
                  d="M-3 1h6v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-4z M-2 1v-2a2 2 0 0 1 4 0v2" 
                  fill="none" 
                  stroke="var(--accent-primary, #8b5cf6)" 
                  stroke-width="1.2"
                  stroke-linecap="round"
                />
              </g>
              <text
                class="node-label"
                :y="getNodeRadius(node) + 14"
                text-anchor="middle"
              >
                {{ truncateLabel(node.label) }}
              </text>
            </g>
          </g>
        </g>
      </svg>

      <!-- 노트 클러스터 이동 컨텍스트 메뉴 -->
      <div 
        v-if="showContextMenu" 
        class="context-menu"
        :style="{ left: contextMenuPos.x + 'px', top: contextMenuPos.y + 'px' }"
        @click.stop
      >
        <div class="context-menu-header">
          <div class="context-header-row">
            <span class="context-note-name">{{ contextMenuNode?.label }}</span>
            <span 
              v-if="contextMenuNode && isNoteLocked(contextMenuNode.id)" 
              class="lock-badge"
              title="클러스터 잠금됨"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </span>
          </div>
          <span class="context-hint">클러스터 이동</span>
        </div>
        <div class="context-menu-items">
          <button
            v-for="cluster in clusters"
            :key="cluster.id"
            class="context-menu-item"
            :class="{ current: contextMenuNode?.cluster === cluster.id }"
            @click="handleMoveToCluster(cluster.id)"
          >
            <span class="cluster-dot" :style="{ background: cluster.color }"></span>
            <span class="cluster-label">{{ cluster.label }}</span>
            <svg 
              v-if="contextMenuNode?.cluster === cluster.id" 
              width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </button>
        </div>
        <div class="context-menu-footer">
          <!-- 잠금/해제 버튼 -->
          <button 
            class="lock-btn"
            :class="{ locked: contextMenuNode && isNoteLocked(contextMenuNode.id) }"
            @click="handleToggleLock"
          >
            <!-- 잠금된 상태: 닫힌 자물쇠 -->
            <svg v-if="contextMenuNode && isNoteLocked(contextMenuNode.id)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            <!-- 잠금 안 된 상태: 열린 자물쇠 -->
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 9.9-1" />
            </svg>
            {{ contextMenuNode && isNoteLocked(contextMenuNode.id) ? '잠금 해제' : 'AI 분류 잠금' }}
          </button>
          <!-- AI 복원 버튼 -->
          <button 
            class="reset-btn" 
            @click="handleResetNoteCluster"
            :disabled="contextMenuNode && isNoteLocked(contextMenuNode.id)"
            :title="contextMenuNode && isNoteLocked(contextMenuNode.id) ? '잠금 해제 후 사용 가능' : ''"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
            </svg>
            AI 자동 분류로 복원
          </button>
        </div>
      </div>

      <!-- 줌 컨트롤 -->
      <div class="zoom-controls">
        <!-- 전체 잠금 버튼 (클러스터 필터 시에만 표시) -->
        <button 
          v-if="showOnlyCluster !== null"
          class="lock-all-btn"
          :class="{ locked: areAllFilteredNodesLocked }"
          @click="handleLockAllFiltered"
          :title="areAllFilteredNodesLocked ? '전체 잠금 해제' : '전체 잠금'"
        >
          <!-- 잠금된 상태: 닫힌 자물쇠 -->
          <svg v-if="areAllFilteredNodesLocked" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <!-- 잠금 안 된 상태: 열린 자물쇠 -->
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 9.9-1" />
          </svg>
        </button>
        <button @click="zoomIn" title="확대">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
            <line x1="11" y1="8" x2="11" y2="14" />
            <line x1="8" y1="11" x2="14" y2="11" />
          </svg>
        </button>
        <button @click="zoomOut" title="축소">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
            <line x1="8" y1="11" x2="14" y2="11" />
          </svg>
        </button>
        <button @click="resetZoom" title="초기화">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
          </svg>
        </button>
      </div>
    </main>

    <!-- 우측 노드 상세 패널 -->
    <aside class="detail-panel" :class="{ open: selectedNode }">
      <div v-if="selectedNode" class="detail-content">
        <div class="detail-header">
          <div 
            class="detail-cluster-badge"
            :style="{ background: selectedNode.color }"
          >
            {{ selectedCluster?.label || '미분류' }}
          </div>
          <button class="close-btn" @click="selectNode(null)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <h2 class="detail-title">{{ selectedNode.label }}</h2>
        
        <div class="detail-meta">
          <span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            {{ selectedNode.id }}
          </span>
        </div>

        <!-- 클러스터 변경 섹션 -->
        <div class="cluster-change-section">
          <h4>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3" />
              <circle cx="4" cy="8" r="2" />
              <circle cx="20" cy="8" r="2" />
            </svg>
            클러스터 소속
          </h4>
          <div class="cluster-select-list">
            <button
              v-for="cluster in clusters"
              :key="cluster.id"
              class="cluster-select-item"
              :class="{ active: selectedNode.cluster === cluster.id }"
              @click="handleMoveSelectedToCluster(cluster.id)"
            >
              <span class="cluster-dot" :style="{ background: cluster.color }"></span>
              <span class="cluster-name">{{ cluster.label }}</span>
              <svg 
                v-if="selectedNode.cluster === cluster.id" 
                class="check-icon"
                width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </button>
          </div>
          <div class="cluster-change-actions">
            <button 
              class="lock-toggle-btn"
              :class="{ locked: selectedNode && isNoteLocked(selectedNode.id) }"
              @click="handleToggleSelectedLock"
            >
              <svg v-if="selectedNode && isNoteLocked(selectedNode.id)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
              <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 9.9-1" />
              </svg>
              {{ selectedNode && isNoteLocked(selectedNode.id) ? '잠금 해제' : 'AI 분류 잠금' }}
            </button>
          </div>
        </div>

        <!-- 연결된 노트 -->
        <div class="connected-notes">
          <h4>연결된 노트 ({{ connectedNotes.length }})</h4>
          <div class="connected-list">
            <button
              v-for="note in connectedNotes.slice(0, 10)"
              :key="note.id"
              class="connected-item"
              @click="handleNodeClick(note)"
            >
              <span 
                class="connected-dot" 
                :style="{ background: note.color }"
              ></span>
              <span class="connected-name">{{ note.label }}</span>
            </button>
            <div 
              v-if="connectedNotes.length > 10" 
              class="connected-more"
            >
              외 {{ connectedNotes.length - 10 }}개...
            </div>
          </div>
        </div>

        <!-- 클러스터 키워드 -->
        <div v-if="selectedCluster?.keywords.length" class="cluster-keywords-section">
          <h4>클러스터 키워드</h4>
          <div class="keyword-tags">
            <span 
              v-for="keyword in selectedCluster.keywords" 
              :key="keyword"
              class="keyword-tag"
            >
              {{ keyword }}
            </span>
          </div>
        </div>

        <button class="open-note-btn" @click="handleOpenNote">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
          노트 열기
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import * as d3Force from 'd3-force';
import * as d3Selection from 'd3-selection';
import * as d3Zoom from 'd3-zoom';
import * as d3Drag from 'd3-drag';
import { useGraph } from '../composables/useGraph';
import type { GraphNode, GraphEdge } from '../types';

// Props & Emits
const props = defineProps<{
  filterClusterId?: number | null;
  minSimilarityProp?: number;
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
  minSimilarity,
  showOnlyCluster,
  filteredNodes,
  filteredEdges,
  clusters,
  stats,
  loadGraphData,
  selectNode,
  filterByCluster,
  setMinSimilarity,
  refresh,
  getConnectedNodes,
  moveNoteToCluster,
  resetNoteCluster,
  lockedNotes,
  loadLockedNotes,
  toggleNoteLock,
  isNoteLocked,
  lockNotesBatch,
  areAllFilteredNodesLocked
} = useGraph();

// Refs
const containerRef = ref<HTMLElement | null>(null);
const svgRef = ref<SVGSVGElement | null>(null);
const zoomGroupRef = ref<SVGGElement | null>(null);

// 시뮬레이션 상태
const simulation = ref<d3Force.Simulation<GraphNode, GraphEdge> | null>(null);
const renderedNodes = ref<GraphNode[]>([]);
const renderedEdges = ref<Array<{
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  opacity: number;
  width: number;
}>>([]);

// 줌 상태 - shallowRef를 사용하여 Vue의 프록시가 D3 ZoomTransform을 변형하지 않도록 함
const currentZoom = shallowRef<d3Zoom.ZoomTransform>(d3Zoom.zoomIdentity);
let zoomBehavior: d3Zoom.ZoomBehavior<SVGSVGElement, unknown> | null = null;

// 드래그 상태
const isDragging = ref(false);

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

/**
 * 노드 우클릭 핸들러
 */
const handleNodeContextMenu = (event: MouseEvent, node: GraphNode) => {
  event.preventDefault();
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
  
  // 시뮬레이션 재시작
  await nextTick();
  initSimulation();
};

/**
 * 노트의 클러스터 오버라이드 제거 (AI 클러스터링으로 복원)
 */
const handleResetNoteCluster = async () => {
  if (!contextMenuNode.value) return;
  if (isNoteLocked(contextMenuNode.value.id)) return; // 잠금된 노트는 복원 불가
  
  await resetNoteCluster(contextMenuNode.value.id);
  showContextMenu.value = false;
  contextMenuNode.value = null;
  
  // 시뮬레이션 재시작
  await nextTick();
  initSimulation();
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
  if (selectedNode.value.cluster === clusterId) return; // 같은 클러스터면 무시
  
  await moveNoteToCluster(selectedNode.value.id, clusterId);
  
  // 시뮬레이션 재시작
  await nextTick();
  initSimulation();
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
 * 컨텍스트 메뉴 외부 클릭 시 닫기
 */
const handleOutsideClick = (event: MouseEvent) => {
  if (showContextMenu.value) {
    showContextMenu.value = false;
    contextMenuNode.value = null;
  }
};

// Props 감시
watch(() => props.filterClusterId, (newVal) => {
  filterByCluster(newVal ?? null);
});

watch(() => props.minSimilarityProp, (newVal) => {
  if (newVal !== undefined) {
    setMinSimilarity(newVal);
  }
});

// 뷰가 활성화될 때 데이터가 없으면 로드
watch(() => props.isActive, async (newVal, oldVal) => {
  if (newVal && !oldVal) {
    // 활성화되었고 데이터가 없으면 로드
    if (!graphData.value || graphData.value.totalNotes === 0) {
      await loadLockedNotes();
      await loadGraphData();
      await nextTick();
      initSimulation();
      initZoom(true);
      setTimeout(() => {
        initDrag();
      }, 100);
    }
  }
}, { immediate: true });

// 그래프 데이터 로드 후 부모에게 알림
watch(graphData, (newData) => {
  if (newData) {
    emit('graph-loaded', {
      clusters: clusters.value,
      stats: stats.value
    });
  }
}, { immediate: true });

/**
 * 노드 반지름 계산
 */
const getNodeRadius = (node: GraphNode) => {
  return Math.max(8, Math.min(24, 8 + node.size * 2));
};

/**
 * 라벨 자르기
 */
const truncateLabel = (label: string) => {
  return label.length > 15 ? label.slice(0, 15) + '...' : label;
};

/**
 * 두 노드가 연결되어 있는지 확인
 */
const isConnected = (nodeId1: string, nodeId2: string) => {
  return filteredEdges.value.some(e => {
    const sourceId = typeof e.source === 'string' ? e.source : (e.source as GraphNode).id;
    const targetId = typeof e.target === 'string' ? e.target : (e.target as GraphNode).id;
    return (sourceId === nodeId1 && targetId === nodeId2) ||
           (sourceId === nodeId2 && targetId === nodeId1);
  });
};

/**
 * 시뮬레이션 초기화
 */
const initSimulation = () => {
  if (!filteredNodes.value.length) return;

  const nodes = filteredNodes.value.map(n => ({ ...n }));
  const edges = filteredEdges.value.map(e => ({
    ...e,
    source: typeof e.source === 'string' ? e.source : e.source.id,
    target: typeof e.target === 'string' ? e.target : e.target.id
  }));

  // 기존 시뮬레이션 정지
  if (simulation.value) {
    simulation.value.stop();
  }

  const centerX = dimensions.value.width / 2;
  const centerY = dimensions.value.height / 2;

  simulation.value = d3Force.forceSimulation<GraphNode>(nodes)
    .force('link', d3Force.forceLink<GraphNode, any>(edges)
      .id((d: GraphNode) => d.id)
      .distance(100)
      .strength((d: any) => d.weight * 0.5))
    .force('charge', d3Force.forceManyBody().strength(-200))
    .force('center', d3Force.forceCenter(centerX, centerY))
    .force('collision', d3Force.forceCollide<GraphNode>().radius((d) => getNodeRadius(d) + 5))
    .force('x', d3Force.forceX(centerX).strength(0.05))
    .force('y', d3Force.forceY(centerY).strength(0.05))
    .on('tick', () => {
      renderedNodes.value = [...(simulation.value?.nodes() || [])];
      updateEdges();
    });
};

/**
 * 엣지 위치 업데이트
 */
const updateEdges = () => {
  const nodeMap = new Map(renderedNodes.value.map(n => [n.id, n]));
  
  renderedEdges.value = filteredEdges.value.map(e => {
    const sourceId = typeof e.source === 'string' ? e.source : (e.source as GraphNode).id;
    const targetId = typeof e.target === 'string' ? e.target : (e.target as GraphNode).id;
    const sourceNode = nodeMap.get(sourceId);
    const targetNode = nodeMap.get(targetId);
    
    return {
      sourceX: sourceNode?.x || 0,
      sourceY: sourceNode?.y || 0,
      targetX: targetNode?.x || 0,
      targetY: targetNode?.y || 0,
      opacity: 0.2 + e.weight * 0.5,
      width: 1 + e.weight * 2
    };
  });
};

/**
 * 줌 초기화 (버그 수정됨)
 * @param resetToIdentity - true면 줌을 초기 상태로 리셋, false면 현재 상태 유지
 */
const initZoom = (resetToIdentity = false) => {
  if (!svgRef.value || !zoomGroupRef.value) return;

  const svg = d3Selection.select(svgRef.value);
  const zoomGroup = d3Selection.select(zoomGroupRef.value);

  // 현재 줌 상태 저장
  const currentTransform = currentZoom.value;

  // 기존 줌 동작 제거
  svg.on('.zoom', null);

  zoomBehavior = d3Zoom.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.2, 4])
    // 노드 드래그 중에는 줌 비활성화
    .filter((event) => {
      // 노드 위에서 드래그 중이면 줌 비활성화
      if (isDragging.value) return false;
      // 우클릭은 무시
      if (event.button === 2) return false;
      // 그 외 휠/더블클릭/터치 허용
      return !event.target.closest('.node');
    })
    .on('zoom', (event) => {
      currentZoom.value = event.transform;
      zoomGroup.attr('transform', event.transform.toString());
    });

  svg.call(zoomBehavior);
  
  // 첫 초기화시에만 줌 리셋, 이후에는 현재 상태 유지
  if (resetToIdentity) {
    svg.call(zoomBehavior.transform, d3Zoom.zoomIdentity);
  } else {
    // 현재 줌 상태 복원
    svg.call(zoomBehavior.transform, currentTransform);
  }
};

/**
 * 노드 드래그 기능 초기화
 */
const initDrag = () => {
  if (!svgRef.value) return;
  
  const svg = d3Selection.select(svgRef.value);
  const nodes = svg.selectAll('.node');
  
  const dragBehavior = d3Drag.drag<SVGGElement, GraphNode>()
    .on('start', (event, d) => {
      isDragging.value = true;
      // 드래그 시작 시 시뮬레이션 활성화
      if (simulation.value) {
        simulation.value.alphaTarget(0.3).restart();
      }
      // 노드 고정
      d.fx = d.x;
      d.fy = d.y;
    })
    .on('drag', (event, d) => {
      // 줌 변환 적용하여 좌표 계산
      const transform = currentZoom.value;
      d.fx = (event.sourceEvent.offsetX - transform.x) / transform.k;
      d.fy = (event.sourceEvent.offsetY - transform.y) / transform.k;
    })
    .on('end', (event, d) => {
      isDragging.value = false;
      // 드래그 종료 시 시뮬레이션 감속
      if (simulation.value) {
        simulation.value.alphaTarget(0);
      }
      // 노드 고정 해제 (원하면 고정 유지 가능)
      d.fx = null;
      d.fy = null;
    });
  
  nodes.call(dragBehavior as any);
};

/**
 * 줌 컨트롤
 */
const zoomIn = () => {
  if (!svgRef.value || !zoomBehavior) return;
  const svg = d3Selection.select(svgRef.value);
  svg.transition().duration(300).call(zoomBehavior.scaleBy, 1.3);
};

const zoomOut = () => {
  if (!svgRef.value || !zoomBehavior) return;
  const svg = d3Selection.select(svgRef.value);
  svg.transition().duration(300).call(zoomBehavior.scaleBy, 0.7);
};

const resetZoom = () => {
  if (!svgRef.value || !zoomBehavior) return;
  const svg = d3Selection.select(svgRef.value);
  svg.transition().duration(500).call(
    zoomBehavior.transform,
    d3Zoom.zoomIdentity
  );
};

/**
 * 이벤트 핸들러
 */
const handleRefresh = async () => {
  await refresh();
  await nextTick();
  initSimulation();
};

const handleNodeHover = (node: GraphNode | null) => {
  hoveredNode.value = node;
};

const handleNodeClick = (node: GraphNode) => {
  selectNode(node);
};

const handleOpenNote = () => {
  if (selectedNode.value) {
    emit('select-file', selectedNode.value.id);
  }
};

// 외부에서 호출할 수 있도록 노출
defineExpose({
  refresh: handleRefresh,
  filterByCluster,
  setMinSimilarity,
  clusters,
  stats,
  isLoading
});

// 데이터 변경 감지
watch([filteredNodes, filteredEdges], async () => {
  initSimulation();
  await nextTick();
  initDrag();
  // 줌 동작 재초기화 (필터링 후 줌이 안되는 버그 수정)
  initZoom();
}, { deep: true });

// 마운트
onMounted(async () => {
  // 잠금된 노트 목록 먼저 로드
  await loadLockedNotes();
  
  await loadGraphData();
  await nextTick();
  initSimulation();
  initZoom(true); // 첫 마운트 시에만 줌 리셋
  
  // 약간의 딜레이 후 드래그 초기화 (노드 렌더링 대기)
  setTimeout(() => {
    initDrag();
  }, 100);
  
  // 컨텍스트 메뉴 외부 클릭 리스너
  document.addEventListener('click', handleOutsideClick);
});

// 언마운트
onUnmounted(() => {
  if (simulation.value) {
    simulation.value.stop();
  }
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
}

/* 그래프 컨테이너 */
.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.graph-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.graph-svg:active {
  cursor: grabbing;
}

/* 엣지 */
.edge {
  stroke: var(--accent-primary, #8b5cf6);
  stroke-opacity: 0.3;
  stroke-linecap: round;
}

/* 노드 */
.node {
  cursor: grab;
  transition: opacity 0.2s;
}

.node:active {
  cursor: grabbing;
}

.node.dimmed {
  opacity: 0.2;
}

.node-circle {
  transition: all 0.2s;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 2px;
}

.node:hover .node-circle {
  stroke: rgba(255, 255, 255, 0.5);
  stroke-width: 3px;
}

.node.selected .node-circle {
  stroke: #fff;
  stroke-width: 3px;
}

.node-label {
  font-size: 11px;
  fill: var(--text-secondary);
  pointer-events: none;
  font-family: var(--font-sans);
}

.node:hover .node-label,
.node.selected .node-label {
  fill: var(--text-primary);
  font-weight: 500;
}

/* 줌 컨트롤 */
.zoom-controls {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.zoom-controls button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.zoom-controls button:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary, #8b5cf6);
  color: var(--accent-primary, #8b5cf6);
}

.zoom-controls .lock-all-btn {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: var(--accent-primary, #8b5cf6);
  margin-bottom: 8px;
}

.zoom-controls .lock-all-btn:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.zoom-controls .lock-all-btn.locked {
  background: var(--accent-primary, #8b5cf6);
  color: #fff;
}

.zoom-controls .lock-all-btn.locked:hover {
  background: rgba(239, 68, 68, 0.8);
  border-color: rgba(239, 68, 68, 0.8);
}

/* 컨텍스트 메뉴 */
.context-menu {
  position: fixed;
  z-index: 1000;
  min-width: 200px;
  max-width: 280px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  animation: contextMenuFadeIn 0.15s ease;
}

@keyframes contextMenuFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.context-menu-header {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}

.context-note-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.context-hint {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.context-menu-items {
  max-height: 240px;
  overflow-y: auto;
  padding: 6px;
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
  text-align: left;
}

.context-menu-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.context-menu-item.current {
  background: rgba(139, 92, 246, 0.12);
  color: var(--accent-primary, #8b5cf6);
}

.context-menu-item .cluster-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.context-menu-item .cluster-label {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.context-menu-footer {
  padding: 8px;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}

.context-header-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lock-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: rgba(139, 92, 246, 0.2);
  border-radius: 4px;
  color: var(--accent-primary, #8b5cf6);
}

.context-menu-footer {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.lock-btn,
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.lock-btn:hover,
.reset-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--accent-primary, #8b5cf6);
  color: var(--accent-primary, #8b5cf6);
}

.lock-btn.locked {
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.3);
  color: var(--accent-primary, #8b5cf6);
}

.lock-btn.locked:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.reset-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 잠금된 노드 스타일 */
.node.locked .node-circle {
  stroke: var(--accent-primary, #8b5cf6);
  stroke-width: 2px;
  stroke-dasharray: 4 2;
}

.lock-icon {
  pointer-events: none;
}

/* 로딩/에러/빈 상태 */
.loading-overlay,
.error-state,
.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--accent-primary, #8b5cf6);
}

.loading-spinner span {
  font-size: 14px;
  color: var(--text-muted);
}

.error-state {
  color: #ef4444;
}

.error-state p {
  color: var(--text-secondary);
  font-size: 14px;
}

.error-state button {
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.15s ease;
}

.error-state button:hover {
  background: rgba(239, 68, 68, 0.2);
}

.empty-state {
  color: var(--text-muted);
}

.empty-state h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-secondary);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 상세 패널 */
.detail-panel {
  width: 0;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-subtle);
  transition: width 0.3s ease;
  overflow: hidden;
}

.detail-panel.open {
  width: 280px;
}

.detail-content {
  padding: 20px;
  width: 280px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.detail-cluster-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.detail-title {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.3;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  margin-bottom: 16px;
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  word-break: break-all;
}

.detail-meta svg {
  flex-shrink: 0;
}

/* 클러스터 변경 섹션 */
.cluster-change-section {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.cluster-change-section h4 {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 10px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
}

.cluster-change-section h4 svg {
  color: var(--accent-primary, #8b5cf6);
}

.cluster-select-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 150px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.cluster-select-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.cluster-select-item:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary, #8b5cf6);
}

.cluster-select-item.active {
  background: rgba(139, 92, 246, 0.12);
  border-color: var(--accent-primary, #8b5cf6);
  color: var(--accent-primary, #8b5cf6);
}

.cluster-select-item .cluster-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cluster-select-item .cluster-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cluster-select-item .check-icon {
  flex-shrink: 0;
  color: var(--accent-primary, #8b5cf6);
}

.cluster-change-actions {
  display: flex;
  gap: 6px;
}

.lock-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px 10px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.lock-toggle-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary, #8b5cf6);
  color: var(--accent-primary, #8b5cf6);
}

.lock-toggle-btn.locked {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: var(--accent-primary, #8b5cf6);
}

/* 연결된 노트 */
.connected-notes {
  margin-bottom: 16px;
}

.connected-notes h4,
.cluster-keywords-section h4 {
  margin: 0 0 10px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
}

.connected-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.connected-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.connected-item:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary, #8b5cf6);
}

.connected-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.connected-name {
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.connected-more {
  padding: 8px 10px;
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
}

/* 키워드 태그 */
.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.keyword-tag {
  padding: 4px 8px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 10px;
  font-size: 11px;
  color: var(--accent-primary, #a78bfa);
}

/* 노트 열기 버튼 */
.open-note-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  margin-top: 16px;
  background: var(--accent-primary, #8b5cf6);
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.15s ease;
}

.open-note-btn:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}
</style>
