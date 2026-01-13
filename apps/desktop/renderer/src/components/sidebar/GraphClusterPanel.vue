<template>
  <div class="sidebar-section cluster-section">
    <div class="cluster-header">
      <div class="cluster-title">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3" />
          <circle cx="4" cy="8" r="2" />
          <circle cx="20" cy="8" r="2" />
          <circle cx="4" cy="16" r="2" />
          <circle cx="20" cy="16" r="2" />
          <line x1="6" y1="8" x2="9" y2="10" />
          <line x1="18" y1="8" x2="15" y2="10" />
          <line x1="6" y1="16" x2="9" y2="14" />
          <line x1="18" y1="16" x2="15" y2="14" />
        </svg>
        <span>AI 클러스터</span>
      </div>
      <div class="cluster-header-actions">
        <button 
          class="add-cluster-btn"
          @click="emit('create-cluster')"
          title="새 클러스터 추가"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </button>
        <button 
          class="refresh-graph-btn"
          @click="emit('refresh-graph')"
          :disabled="isLoading"
          title="클러스터 다시 분석"
        >
          <svg 
            width="12" height="12" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="2"
            :class="{ spinning: isLoading }"
          >
            <path d="M21 2v6h-6M3 22v-6h6M21 12A9 9 0 0 0 6 6l-3 3M3 12a9 9 0 0 0 15 6l3-3" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 그래프 통계 -->
    <div class="graph-stats" v-if="stats">
      <div class="stat-item">
        <span class="stat-value">{{ stats.totalNotes }}</span>
        <span class="stat-label">노트</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.totalClusters }}</span>
        <span class="stat-label">주제</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.totalEdges }}</span>
        <span class="stat-label">연결</span>
      </div>
    </div>

    <!-- 클러스터 목록 -->
    <div class="cluster-list">
      <button
        class="cluster-item all"
        :class="{ active: selectedClusterId === null }"
        @click="emit('filter-cluster', null)"
      >
        <span class="cluster-dot all-gradient"></span>
        <span class="cluster-name">전체 보기</span>
        <span class="cluster-count">{{ stats?.totalNotes || 0 }}</span>
      </button>
      
      <div
        v-for="cluster in clusters"
        :key="cluster.id"
        class="cluster-item-wrapper"
      >
        <button
          class="cluster-item"
          :class="{ active: selectedClusterId === cluster.id }"
          @click="emit('filter-cluster', cluster.id)"
        >
          <span class="cluster-dot" :style="{ background: cluster.color }"></span>
          <div class="cluster-info">
            <span class="cluster-name">{{ cluster.label }}</span>
            <span class="cluster-keywords" v-if="cluster.keywords.length">
              {{ cluster.keywords.slice(0, 3).join(' · ') }}
            </span>
          </div>
          <span class="cluster-count">{{ cluster.noteCount }}</span>
        </button>
        <button 
          class="cluster-edit-btn"
          @click.stop="emit('edit-cluster', cluster)"
          title="클러스터 편집"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 유사도 슬라이더 -->
    <div class="similarity-control">
      <label>
        <span>연결 민감도</span>
        <span class="similarity-value">{{ Math.round(minSimilarity * 100) }}%</span>
      </label>
      <input
        type="range"
        min="0.1"
        max="0.8"
        step="0.05"
        :value="minSimilarity"
        @input="handleSimilarityInput"
      />
      <div class="similarity-hint">
        <span>많은 연결</span>
        <span>적은 연결</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ClusterInfo } from '../../types';

const props = defineProps<{
  clusters: ClusterInfo[];
  selectedClusterId: number | null;
  stats: { totalNotes: number; totalClusters: number; totalEdges: number } | null;
  isLoading: boolean;
  minSimilarity: number;
}>();

const emit = defineEmits<{
  'filter-cluster': [clusterId: number | null];
  'refresh-graph': [];
  'similarity-change': [value: number];
  'edit-cluster': [cluster: ClusterInfo];
  'create-cluster': [];
}>();

function handleSimilarityInput(e: Event) {
  const value = parseFloat((e.target as HTMLInputElement).value);
  emit('similarity-change', value);
}
</script>

<style scoped>
.cluster-section {
  padding: 0;
}

.cluster-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.cluster-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.cluster-title svg {
  color: var(--accent-primary, #8b5cf6);
}

.cluster-header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.add-cluster-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-cluster-btn:hover {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.2);
  color: var(--accent-primary, #8b5cf6);
}

.refresh-graph-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 4px;
  color: var(--accent-primary, #8b5cf6);
  cursor: pointer;
  transition: all 0.15s ease;
}

.refresh-graph-btn:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.2);
  border-color: var(--accent-primary, #8b5cf6);
}

.refresh-graph-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-graph-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Graph Stats */
.graph-stats {
  display: flex;
  padding: 12px 16px;
  gap: 8px;
  border-bottom: 1px solid var(--border-subtle);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-item .stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-primary, #8b5cf6);
}

.stat-item .stat-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
}

/* Cluster List */
.cluster-list {
  padding: 8px;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.cluster-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
  margin-bottom: 2px;
}

.cluster-item:hover {
  background: var(--bg-hover);
  border-color: var(--border-subtle);
}

.cluster-item.active {
  background: rgba(139, 92, 246, 0.12);
  border-color: rgba(139, 92, 246, 0.25);
  color: var(--text-primary);
}

.cluster-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cluster-dot.all-gradient {
  background: linear-gradient(135deg, #8b5cf6, #3b82f6, #22c55e);
}

.cluster-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cluster-item .cluster-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cluster-keywords {
  font-size: 10px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cluster-count {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-primary, #8b5cf6);
  background: rgba(139, 92, 246, 0.12);
  padding: 2px 6px;
  border-radius: 8px;
  flex-shrink: 0;
}

/* 클러스터 아이템 래퍼 */
.cluster-item-wrapper {
  display: flex;
  align-items: stretch;
  gap: 4px;
  margin-bottom: 2px;
}

.cluster-item-wrapper .cluster-item {
  flex: 1;
  margin-bottom: 0;
}

.cluster-edit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s ease;
}

.cluster-item-wrapper:hover .cluster-edit-btn {
  opacity: 1;
}

.cluster-edit-btn:hover {
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.25);
  color: var(--accent-primary, #8b5cf6);
}

/* Similarity Control */
.similarity-control {
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}

.similarity-control label {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.similarity-value {
  color: var(--accent-primary, #8b5cf6);
  font-weight: 600;
}

.similarity-control input[type="range"] {
  width: 100%;
  height: 4px;
  background: var(--bg-hover);
  border-radius: 2px;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.similarity-control input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  background: var(--accent-primary, #8b5cf6);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.3);
}

.similarity-hint {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: var(--text-muted);
  opacity: 0.6;
  margin-top: 4px;
}
</style>
