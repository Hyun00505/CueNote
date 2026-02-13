<template>
  <aside
    class="detail-panel"
    :class="{ open: selectedNode }"
  >
    <div
      v-if="selectedNode"
      class="detail-content"
    >
      <!-- 헤더 -->
      <div class="detail-header">
        <div 
          class="detail-cluster-badge"
          :style="{ background: selectedNode.color }"
        >
          {{ selectedClusterLabel }}
        </div>
        <button
          class="close-btn"
          @click="emit('close')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- 제목 -->
      <h2 class="detail-title">{{ selectedNode.label }}</h2>
      
      <!-- 경로 -->
      <div class="detail-meta">
        <span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          {{ selectedNode.id }}
        </span>
      </div>

      <!-- 미리보기 -->
      <div 
        v-if="selectedNode.preview"
        class="note-preview"
      >
        <p>{{ selectedNode.preview }}</p>
      </div>

      <!-- 관련 노트 추천 -->
      <div 
        v-if="relatedNotes.length > 0"
        class="related-notes"
      >
        <h4>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3" />
            <circle cx="4" cy="8" r="2" />
            <circle cx="20" cy="8" r="2" />
            <circle cx="4" cy="16" r="2" />
            <circle cx="20" cy="16" r="2" />
          </svg>
          관련 노트
        </h4>
        <div class="related-list">
          <button
            v-for="note in relatedNotes"
            :key="note.path"
            class="related-item"
            @click="emit('focus-node', note.path)"
          >
            <span 
              class="related-dot" 
              :style="{ background: note.color }"
            />
            <div class="related-info">
              <span class="related-name">{{ note.title }}</span>
              <span class="related-similarity">{{ Math.round(note.similarity * 100) }}% 유사</span>
            </div>
          </button>
        </div>
      </div>

      <!-- 연결된 노트 -->
      <div 
        v-if="connectedNotes.length > 0"
        class="connected-notes"
      >
        <h4>연결된 노트 ({{ connectedNotes.length }})</h4>
        <div class="connected-list">
          <button
            v-for="note in connectedNotes.slice(0, 8)"
            :key="note.id"
            class="connected-item"
            @click="emit('open-node', note)"
          >
            <span 
              class="connected-dot" 
              :style="{ background: note.color }"
            />
            <span class="connected-name">{{ note.label }}</span>
          </button>
          <div 
            v-if="connectedNotes.length > 8" 
            class="connected-more"
          >
            외 {{ connectedNotes.length - 8 }}개...
          </div>
        </div>
      </div>

      <!-- 클러스터 키워드 -->
      <div
        v-if="currentClusterKeywords.length > 0"
        class="cluster-keywords-section"
      >
        <h4>클러스터 키워드</h4>
        <div class="keyword-tags">
          <span 
            v-for="keyword in currentClusterKeywords" 
            :key="keyword"
            class="keyword-tag"
          >
            {{ keyword }}
          </span>
        </div>
      </div>

      <!-- 노트 열기 버튼 -->
      <button
        class="open-note-btn"
        @click="emit('open-file', selectedNode.id)"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1="10" y1="14" x2="21" y2="3" />
        </svg>
        노트 열기
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { GraphNode, ClusterInfo, RelatedNote } from '../../types';

const props = defineProps<{
  selectedNode: GraphNode | null;
  connectedNotes: GraphNode[];
  relatedNotes: RelatedNote[];
  clusters: ClusterInfo[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'open-node', node: GraphNode): void;
  (e: 'open-file', path: string): void;
  (e: 'focus-node', nodeId: string): void;
}>();

const selectedClusterLabel = computed(() => {
  if (!props.selectedNode) return '미분류';
  const cluster = props.clusters.find(c => c.id === props.selectedNode!.cluster);
  return cluster?.label || '미분류';
});

const currentClusterKeywords = computed(() => {
  if (!props.selectedNode) return [];
  const cluster = props.clusters.find(c => c.id === props.selectedNode!.cluster);
  return cluster?.keywords || [];
});
</script>

<style scoped>
.detail-panel {
  width: 0;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-subtle);
  transition: width 0.3s ease;
  overflow: hidden;
}

.detail-panel.open {
  width: 300px;
}

.detail-content {
  padding: 20px;
  width: 300px;
  height: 100%;
  overflow-y: auto;
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
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.detail-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.4;
  word-break: break-all;
}

.detail-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 12px;
  color: var(--text-muted);
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 노트 미리보기 */
.note-preview {
  margin-bottom: 20px;
  padding: 12px;
  background: var(--surface-1);
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.note-preview p {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* 관련 노트 추천 */
.related-notes {
  margin-bottom: 20px;
}

.related-notes h4 {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  text-align: left;
  color: var(--text-secondary);
  transition: all 0.15s ease;
}

.related-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.related-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.related-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.related-name {
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.related-similarity {
  font-size: 10px;
  color: var(--text-muted);
}

/* 연결된 노트 */
.connected-notes {
  margin-bottom: 20px;
}

.connected-notes h4 {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 10px 0;
}

.connected-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.connected-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  text-align: left;
  color: var(--text-secondary);
  transition: all 0.15s ease;
}

.connected-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.connected-dot {
  width: 6px;
  height: 6px;
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
  padding: 4px 8px;
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
}

/* 클러스터 키워드 */
.cluster-keywords-section {
  margin-bottom: 20px;
}

.cluster-keywords-section h4 {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 10px 0;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.keyword-tag {
  padding: 4px 8px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}

/* 노트 열기 버튼 */
.open-note-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: var(--accent-primary, #8b5cf6);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.open-note-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
}

.open-note-btn:active {
  transform: translateY(0);
}
</style>
