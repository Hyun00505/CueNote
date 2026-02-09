<template>
  <main
    ref="containerRef"
    class="graph-container"
  >
    <slot name="loading-error-empty" />
    <svg
      ref="svgRef"
      class="graph-svg"
      :viewBox="`0 0 ${width} ${height}`"
    >
      <defs>
        <filter id="glow">
          <feGaussianBlur
            stdDeviation="3"
            result="coloredBlur"
          />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <g
        ref="zoomGroupRef"
        class="zoom-group"
      >
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
              locked: isNoteLocked(node.id),
              'link-source': linkSourceNode?.id === node.id,
              'link-candidate': linkEditMode && linkSourceNode?.id !== node.id,
              'has-connection': linkEditMode === 'remove' && linkSourceNode && hasEdgeBetween(linkSourceNode.id, node.id)
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
            <g
              v-if="isNoteLocked(node.id)"
              class="lock-icon"
              :transform="`translate(${getNodeRadius(node) - 4}, ${-getNodeRadius(node) + 4})`"
            >
              <circle
                r="8"
                fill="var(--bg-primary)"
                stroke="var(--accent-primary, #8b5cf6)"
                stroke-width="1.5"
              />
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
    <slot name="overlays" />
  </main>
</template>

<script setup lang="ts">
import { ref, shallowRef, watch, onMounted, onUnmounted, nextTick } from 'vue';
import * as d3Force from 'd3-force';
import * as d3Selection from 'd3-selection';
import * as d3Zoom from 'd3-zoom';
import * as d3Drag from 'd3-drag';
import type { GraphNode, GraphEdge } from '../../types';

const props = defineProps<{
  nodes: GraphNode[];
  edges: GraphEdge[];
  width: number;
  height: number;
  selectedNode: GraphNode | null;
  hoveredNode: GraphNode | null;
  linkEditMode: 'add' | 'remove' | null;
  linkSourceNode: GraphNode | null;
  isNoteLocked: (id: string) => boolean;
  hasEdgeBetween: (id1: string, id2: string) => boolean;
}>();

const emit = defineEmits<{
  (e: 'node-click', node: GraphNode): void;
  (e: 'node-hover', node: GraphNode | null): void;
  (e: 'node-contextmenu', event: MouseEvent, node: GraphNode): void;
}>();

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

// 줌 상태
const currentZoom = shallowRef<d3Zoom.ZoomTransform>(d3Zoom.zoomIdentity);
let zoomBehavior: d3Zoom.ZoomBehavior<SVGSVGElement, unknown> | null = null;
const isDragging = ref(false);

const getNodeRadius = (node: GraphNode) => Math.max(8, Math.min(24, 8 + node.size * 2));
const truncateLabel = (label: string) => label.length > 15 ? label.slice(0, 15) + '...' : label;

const isConnected = (nodeId1: string, nodeId2: string) => {
  return props.edges.some(e => {
    const sourceId = typeof e.source === 'string' ? e.source : (e.source as GraphNode).id;
    const targetId = typeof e.target === 'string' ? e.target : (e.target as GraphNode).id;
    return (sourceId === nodeId1 && targetId === nodeId2) || (sourceId === nodeId2 && targetId === nodeId1);
  });
};

const initSimulation = () => {
  if (!props.nodes.length) return;

  const nodes = props.nodes.map(n => ({ ...n }));
  const edges = props.edges.map(e => ({
    ...e,
    source: typeof e.source === 'string' ? e.source : e.source.id,
    target: typeof e.target === 'string' ? e.target : e.target.id
  }));

  if (simulation.value) simulation.value.stop();

  const centerX = props.width / 2;
  const centerY = props.height / 2;

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

const updateEdges = () => {
  const nodeMap = new Map(renderedNodes.value.map(n => [n.id, n]));
  renderedEdges.value = props.edges.map(e => {
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

const initZoom = (resetToIdentity = false) => {
  if (!svgRef.value || !zoomGroupRef.value) return;

  const svg = d3Selection.select(svgRef.value);
  const zoomGroup = d3Selection.select(zoomGroupRef.value);
  const currentTransform = currentZoom.value;

  svg.on('.zoom', null);

  zoomBehavior = d3Zoom.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.2, 4])
    .filter((event) => {
      if (isDragging.value) return false;
      if (event.button === 2) return false;
      return !event.target.closest('.node');
    })
    .on('zoom', (event) => {
      currentZoom.value = event.transform;
      zoomGroup.attr('transform', event.transform.toString());
    });

  svg.call(zoomBehavior);
  
  if (resetToIdentity) {
    svg.call(zoomBehavior.transform, d3Zoom.zoomIdentity);
  } else {
    svg.call(zoomBehavior.transform, currentTransform);
  }
};

const initDrag = () => {
  if (!svgRef.value) return;
  
  const svg = d3Selection.select(svgRef.value);
  const nodes = svg.selectAll('.node');
  
  const dragBehavior = d3Drag.drag<SVGGElement, GraphNode>()
    .on('start', (event, d) => {
      isDragging.value = true;
      if (simulation.value) simulation.value.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    })
    .on('drag', (event, d) => {
      const transform = currentZoom.value;
      d.fx = (event.sourceEvent.offsetX - transform.x) / transform.k;
      d.fy = (event.sourceEvent.offsetY - transform.y) / transform.k;
    })
    .on('end', (event, d) => {
      isDragging.value = false;
      if (simulation.value) simulation.value.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    });
  
  nodes.call(dragBehavior as any);
};

// Zoom control methods exposed
const zoomIn = () => {
  if (!svgRef.value || !zoomBehavior) return;
  const svg = d3Selection.select(svgRef.value);
  (svg as any).transition().duration(300).call(zoomBehavior.scaleBy, 1.3);
};

const zoomOut = () => {
  if (!svgRef.value || !zoomBehavior) return;
  const svg = d3Selection.select(svgRef.value);
  (svg as any).transition().duration(300).call(zoomBehavior.scaleBy, 0.7);
};

const resetZoom = () => {
  if (!svgRef.value || !zoomBehavior) return;
  const svg = d3Selection.select(svgRef.value);
  (svg as any).transition().duration(500).call(zoomBehavior.transform, d3Zoom.zoomIdentity);
};

const handleNodeClick = (node: GraphNode) => emit('node-click', node);
const handleNodeHover = (node: GraphNode | null) => emit('node-hover', node);
const handleNodeContextMenu = (event: MouseEvent, node: GraphNode) => emit('node-contextmenu', event, node);

defineExpose({ zoomIn, zoomOut, resetZoom, initSimulation, initDrag, initZoom });

watch([() => props.nodes, () => props.edges], async () => {
  initSimulation();
  await nextTick();
  initDrag();
  initZoom();
}, { deep: true });

onMounted(async () => {
  initSimulation();
  initZoom(true);
  setTimeout(initDrag, 100);
});

onUnmounted(() => {
  if (simulation.value) simulation.value.stop();
});
</script>

<style scoped>
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

.edge {
  stroke: var(--accent-primary, #8b5cf6);
  stroke-opacity: 0.3;
  stroke-linecap: round;
}

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

/* 노드 연결 편집 모드 스타일 */
.node.link-source .node-circle {
  stroke: var(--accent-primary, #8b5cf6);
  stroke-width: 3px;
  filter: url(#glow);
}

.node.link-candidate {
  cursor: crosshair;
}

.node.link-candidate .node-circle {
  stroke: var(--text-muted);
  stroke-width: 2px;
  stroke-dasharray: 4 2;
}

.node.link-candidate:hover .node-circle {
  stroke: #22c55e;
  stroke-width: 3px;
  stroke-dasharray: none;
}

.node.has-connection .node-circle {
  stroke: #ef4444;
  stroke-width: 2px;
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
</style>
