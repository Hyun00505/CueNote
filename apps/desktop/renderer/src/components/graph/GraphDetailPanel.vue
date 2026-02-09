<template>
  <aside
    class="detail-panel"
    :class="{ open: selectedNode }"
  >
    <div
      v-if="selectedNode"
      class="detail-content"
    >
      <div class="detail-header">
        <div 
          class="detail-cluster-badge"
          :style="{ background: selectedNode.color }"
        >
          {{ selectedCluster?.label || '미분류' }}
        </div>
        <button
          class="close-btn"
          @click="emit('close')"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line
              x1="18"
              y1="6"
              x2="6"
              y2="18"
            />
            <line
              x1="6"
              y1="6"
              x2="18"
              y2="18"
            />
          </svg>
        </button>
      </div>

      <h2 class="detail-title">
        {{ selectedNode.label }}
      </h2>
      
      <div class="detail-meta">
        <span>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          {{ selectedNode.id }}
        </span>
      </div>

      <!-- 클러스터 변경 섹션 -->
      <div class="cluster-change-section">
        <h4>
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle
              cx="12"
              cy="12"
              r="3"
            />
            <circle
              cx="4"
              cy="8"
              r="2"
            />
            <circle
              cx="20"
              cy="8"
              r="2"
            />
          </svg>
          클러스터 소속
        </h4>
        <div class="cluster-select-list">
          <button
            v-for="cluster in clusters"
            :key="cluster.id"
            class="cluster-select-item"
            :class="{ active: selectedNode.cluster === cluster.id }"
            @click="emit('move-cluster', cluster.id)"
          >
            <span
              class="cluster-dot"
              :style="{ background: cluster.color }"
            />
            <span class="cluster-name">{{ cluster.label }}</span>
            <svg 
              v-if="selectedNode.cluster === cluster.id" 
              class="check-icon"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </button>
        </div>
        <div class="cluster-change-actions">
          <button 
            class="lock-toggle-btn"
            :class="{ locked: isLocked }"
            @click="emit('toggle-lock')"
          >
            <svg
              v-if="isLocked"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect
                x="3"
                y="11"
                width="18"
                height="11"
                rx="2"
                ry="2"
              />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            <svg
              v-else
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect
                x="3"
                y="11"
                width="18"
                height="11"
                rx="2"
                ry="2"
              />
              <path d="M7 11V7a5 5 0 0 1 9.9-1" />
            </svg>
            {{ isLocked ? '잠금 해제' : 'AI 분류 잠금' }}
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
            @click="emit('open-node', note)"
          >
            <span 
              class="connected-dot" 
              :style="{ background: note.color }"
            />
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
      <div
        v-if="selectedCluster?.keywords.length"
        class="cluster-keywords-section"
      >
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

      <button
        class="open-note-btn"
        @click="emit('open-file', selectedNode.id)"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line
            x1="10"
            y1="14"
            x2="21"
            y2="3"
          />
        </svg>
        노트 열기
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { GraphNode } from '../../types';

defineProps<{
  selectedNode: GraphNode | null;
  selectedCluster: any;
  clusters: any[];
  connectedNotes: GraphNode[];
  isLocked: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'move-cluster', clusterId: number): void;
  (e: 'toggle-lock'): void;
  (e: 'open-node', node: GraphNode): void;
  (e: 'open-file', path: string): void;
}>();
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
  margin-bottom: 20px;
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
  margin-bottom: 24px;
  font-size: 12px;
  color: var(--text-muted);
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.cluster-change-section {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--surface-1);
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.cluster-change-section h4 {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.cluster-select-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
  max-height: 150px;
  overflow-y: auto;
}

.cluster-select-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  color: var(--text-secondary);
}

.cluster-select-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.cluster-select-item.active {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.2);
  color: var(--text-primary);
}

.cluster-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.cluster-name {
  font-size: 12px;
  flex: 1;
  text-align: left;
}

.check-icon {
  color: var(--accent-primary, #8b5cf6);
}

.cluster-change-actions {
  display: flex;
  justify-content: flex-end;
}

.lock-toggle-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.lock-toggle-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.lock-toggle-btn.locked {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: var(--accent-primary, #8b5cf6);
}

.lock-toggle-btn.locked:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.connected-notes {
  margin-bottom: 24px;
}

.connected-notes h4 {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
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

.cluster-keywords-section {
  margin-bottom: 24px;
}

.cluster-keywords-section h4 {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
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
