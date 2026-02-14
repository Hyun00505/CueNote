<template>
  <div class="sidebar-section cluster-section">
    <div class="cluster-header">
      <div class="cluster-title">
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
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
          class="refresh-graph-btn"
          :disabled="isLoading"
          title="클러스터 다시 분석"
          @click="emit('refresh-graph')"
        >
          <svg 
            width="12"
            height="12" 
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

    <!-- 검색 -->
    <div class="graph-search">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input 
        v-model="localSearchQuery"
        type="text"
        placeholder="노트 검색..."
        @input="handleSearch"
      />
      <button 
        v-if="localSearchQuery"
        class="search-clear"
        @click="clearSearch"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>

    <!-- 그래프 통계 -->
    <div
      v-if="stats"
      class="graph-stats"
    >
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
        <span class="cluster-dot all-gradient" />
        <span class="cluster-name">전체 보기</span>
        <span class="cluster-count">{{ stats?.totalNotes || 0 }}</span>
      </button>
      
      <button
        v-for="cluster in clusters"
        :key="cluster.id"
        class="cluster-item"
        :class="{ active: selectedClusterId === cluster.id }"
        @click="emit('filter-cluster', cluster.id)"
      >
        <span
          class="cluster-dot"
          :style="{ background: cluster.color }"
        />
        <div class="cluster-info">
          <span class="cluster-name">{{ cluster.label }}</span>
          <span
            v-if="cluster.keywords.length"
            class="cluster-keywords"
          >
            {{ cluster.keywords.slice(0, 3).join(' · ') }}
          </span>
        </div>
        <span class="cluster-count">{{ cluster.noteCount }}</span>
      </button>
      
      <!-- 미분류 노트 -->
      <button
        v-if="unclusteredCount > 0"
        class="cluster-item unclustered"
        :class="{ active: selectedClusterId === 'unclustered' }"
        @click="emit('filter-cluster', 'unclustered')"
      >
        <span class="cluster-dot unclustered-dot">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </span>
        <span class="cluster-name">미분류</span>
        <span class="cluster-count unclustered">{{ unclusteredCount }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { ClusterInfo } from '../../types';

const props = defineProps<{
  clusters: ClusterInfo[];
  selectedClusterId: number | null | 'unclustered';
  stats: { totalNotes: number; totalClusters: number; totalEdges: number } | null;
  isLoading: boolean;
  unclusteredCount: number;
}>();

const emit = defineEmits<{
  'filter-cluster': [clusterId: number | null | 'unclustered'];
  'refresh-graph': [];
  'search': [query: string];
}>();

const localSearchQuery = ref('');

let searchDebounce: ReturnType<typeof setTimeout> | null = null;

const handleSearch = () => {
  if (searchDebounce) clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    emit('search', localSearchQuery.value);
  }, 300);
};

const clearSearch = () => {
  localSearchQuery.value = '';
  emit('search', '');
};
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
  color: var(--accent-primary);
}

.cluster-header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.refresh-graph-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--bg-hover);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  color: var(--accent-primary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.refresh-graph-btn:hover:not(:disabled) {
  background: var(--accent-glow);
  border-color: var(--accent-primary);
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

/* 검색 */
.graph-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  transition: border-color 0.2s;
}

.graph-search:focus-within {
  border-color: var(--accent-primary);
}

.graph-search svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.graph-search input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
}

.graph-search input::placeholder {
  color: var(--text-muted);
}

.search-clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: transparent;
  border: none;
  border-radius: 50%;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.search-clear:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
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
  color: var(--accent-primary);
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
  background: var(--bg-active);
  border-color: var(--accent-primary);
  color: var(--text-primary);
}

.cluster-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cluster-dot.all-gradient {
  background: linear-gradient(135deg, var(--accent-primary), var(--info), var(--success));
}

.cluster-dot.unclustered-dot {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(156, 163, 175, 0.2);
  border: 1px dashed rgba(156, 163, 175, 0.5);
}

.cluster-dot.unclustered-dot svg {
  color: var(--text-muted);
}

.cluster-item.unclustered {
  opacity: 0.8;
  border-style: dashed;
  border-color: var(--border-subtle);
}

.cluster-item.unclustered:hover {
  opacity: 1;
}

.cluster-item.unclustered.active {
  opacity: 1;
  background: rgba(156, 163, 175, 0.12);
  border-color: rgba(156, 163, 175, 0.25);
}

.cluster-count.unclustered {
  color: var(--text-muted);
  background: rgba(156, 163, 175, 0.15);
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
  color: var(--accent-primary);
  background: var(--bg-hover);
  padding: 2px 6px;
  border-radius: 8px;
  flex-shrink: 0;
}
</style>
