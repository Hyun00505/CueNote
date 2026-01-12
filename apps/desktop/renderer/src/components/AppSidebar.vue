<template>
  <aside 
    class="sidebar" 
    :class="{ collapsed: isCollapsed }"
    :style="{ width: isCollapsed ? 'var(--sidebar-collapsed)' : `${sidebarWidth}px` }"
  >
    <!-- 리사이즈 핸들 -->
    <div 
      class="resize-handle"
      @mousedown="startResize"
    ></div>
    
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">
          <svg class="logo-svg" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 미니멀 노트 아이콘 -->
            <rect x="7" y="4" width="18" height="24" rx="2" fill="currentColor" opacity="0.15"/>
            <rect x="7" y="4" width="18" height="24" rx="2" stroke="currentColor" stroke-width="1.5" opacity="0.6"/>
            <!-- 노트 라인들 -->
            <line x1="11" y1="11" x2="21" y2="11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.4"/>
            <line x1="11" y1="16" x2="18" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.3"/>
            <line x1="11" y1="21" x2="19" y2="21" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.2"/>
          </svg>
        </div>
        <span class="logo-text">
          <span class="logo-cue">Cue</span><span class="logo-note">Note</span>
        </span>
      </div>
      <button class="icon-btn" @click="$emit('toggle-collapse')" title="Toggle Sidebar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <!-- Environment Section -->
      <div class="sidebar-section environment-section">
        <div class="env-header">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6M4.22 19.78l4.24-4.24M15.54 8.46l4.24-4.24"/>
          </svg>
          <span class="env-label">환경</span>
          <button class="env-add-btn" @click="showEnvModal = true" title="환경 추가">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
          </button>
        </div>
        
        <div class="env-selector" @click="toggleEnvDropdown">
          <div class="env-current">
            <span class="env-name">{{ currentEnvironment?.name || '환경 선택' }}</span>
            <svg :class="{ rotated: envDropdownOpen }" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </div>
        </div>
        
        <div v-if="envDropdownOpen" class="env-dropdown">
          <div 
            v-for="env in environments" 
            :key="env.id" 
            class="env-item"
            :class="{ active: env.id === currentId, invalid: !env.exists }"
            @click="handleSelectEnvironment(env.id)"
          >
            <div class="env-item-info">
              <span class="env-item-name">{{ env.name }}</span>
              <span class="env-item-path">{{ truncatePath(env.path) }}</span>
            </div>
            <button 
              v-if="environments.length > 1" 
              class="env-remove-btn" 
              @click.stop="handleRemoveEnvironment(env.id)"
              title="환경 제거"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 그래프 뷰 클러스터 패널 -->
      <template v-if="currentView === 'graph'">
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
            <button 
              class="refresh-graph-btn"
              @click="emit('refresh-graph')"
              :disabled="isGraphLoading"
              title="클러스터 다시 분석"
            >
              <svg 
                width="12" height="12" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="2"
                :class="{ spinning: isGraphLoading }"
              >
                <path d="M21 2v6h-6M3 22v-6h6M21 12A9 9 0 0 0 6 6l-3 3M3 12a9 9 0 0 0 15 6l3-3" />
              </svg>
            </button>
          </div>

          <!-- 그래프 통계 -->
          <div class="graph-stats" v-if="graphStats">
            <div class="stat-item">
              <span class="stat-value">{{ graphStats.totalNotes }}</span>
              <span class="stat-label">노트</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ graphStats.totalClusters }}</span>
              <span class="stat-label">주제</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ graphStats.totalEdges }}</span>
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
              <span class="cluster-count">{{ graphStats?.totalNotes || 0 }}</span>
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
                @click.stop="openClusterEdit(cluster)"
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

      <!-- 기본 Vault Section (그래프 뷰가 아닐 때) -->
      <template v-else>
        <div class="sidebar-section">
          <div v-if="vaultPath && todoCount !== null" class="vault-stats">
            <span class="stat">{{ vaultFiles.length }} notes</span>
            <span class="stat-dot">·</span>
            <span class="stat">{{ todoCount }} tasks</span>
          </div>

          <p v-if="vaultError" class="error-msg">{{ vaultError }}</p>
        </div>
      </template>

      <!-- Files List (그래프 뷰가 아닐 때만) -->
      <div class="sidebar-section files-section" v-if="vaultPath && currentView !== 'graph'">
        <div class="section-header-row">
          <div class="section-label">Notes</div>
          <button class="new-file-btn" @click="startCreateFile" title="New note" :disabled="isCreating || isInputMode">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
          </button>
        </div>

        <!-- 새 파일 이름 입력 -->
        <div v-if="isInputMode" class="new-file-input-wrapper">
          <svg class="file-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <input
            ref="inputRef"
            v-model="newFileName"
            type="text"
            class="file-name-input"
            placeholder="노트 이름 입력..."
            @keydown.enter="handleCreateFile"
            @keydown.escape="cancelCreate"
            @blur="handleCreateFile"
          />
        </div>

        <ul class="file-list" v-if="vaultFiles.length > 0 || isInputMode">
          <li
            v-for="(file, index) in vaultFiles"
            :key="file"
            class="file-item"
            :class="{ active: file === activeFile, editing: editingFile === file }"
            :style="{ '--delay': `${index * 20}ms` }"
          >
            <!-- 이름 변경 모드 -->
            <div v-if="editingFile === file" class="file-edit-wrapper">
              <svg class="file-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <input
                ref="editInputRef"
                v-model="editingName"
                type="text"
                class="file-name-input"
                @keydown.enter="handleRename"
                @keydown.escape="cancelRename"
                @blur="handleRename"
              />
            </div>
            <!-- 일반 모드 -->
            <template v-else>
              <button class="file-btn" @click="$emit('select-file', file)" @dblclick.stop="startRename(file)">
                <svg class="file-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="8" y1="13" x2="16" y2="13"/>
                  <line x1="8" y1="17" x2="12" y2="17"/>
                </svg>
                <span class="file-name">{{ getFileName(file) }}</span>
                <span v-if="dirtyFiles.includes(file)" class="dirty-indicator" title="저장되지 않음"></span>
              </button>
              <div class="file-actions">
                <button 
                  class="rename-btn" 
                  @click.stop="startRename(file)"
                  title="Rename"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
                  </svg>
                </button>
                <button 
                  class="delete-btn" 
                  @click.stop="handleDeleteFile(file)"
                  title="Move to trash"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14z"/>
                  </svg>
                </button>
              </div>
            </template>
          </li>
        </ul>

        <div v-else-if="!isInputMode" class="empty-files">
          <p>No notes yet</p>
          <button class="create-first-btn" @click="startCreateFile" :disabled="isCreating">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Create your first note
          </button>
        </div>
      </div>

      <!-- Trash Section (그래프 뷰가 아닐 때만) -->
      <div class="sidebar-section trash-section" v-if="vaultPath && trashFiles.length > 0 && currentView !== 'graph'">
        <div class="section-header-row">
          <div class="section-label trash-label" @click="toggleTrash">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ rotated: !trashExpanded }">
              <path d="M6 9l6 6 6-6"/>
            </svg>
            Trash
            <span class="trash-count">{{ trashFiles.length }}</span>
          </div>
          <button class="empty-trash-btn" @click="handleEmptyTrash" title="Empty trash">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14z"/>
            </svg>
          </button>
        </div>

        <ul class="file-list trash-list" v-if="trashExpanded">
          <li
            v-for="file in trashFiles"
            :key="file"
            class="file-item trash-item"
          >
            <div class="trash-file-info">
              <svg class="file-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <span class="file-name">{{ getFileName(file) }}</span>
            </div>
            <div class="trash-actions">
              <button 
                class="restore-btn" 
                @click="handleRestoreFile(file)"
                title="Restore"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                  <path d="M21 3v5h-5"/>
                  <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
                </svg>
              </button>
              <button 
                class="permanent-delete-btn" 
                @click="handlePermanentDelete(file)"
                title="Delete permanently"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Status Bar -->
    <div class="sidebar-footer">
      <div class="status-indicator" :class="coreStatus === 'ok' ? 'online' : 'offline'">
        <span class="status-dot"></span>
        <span class="status-text">{{ coreStatus === 'ok' ? 'Core Online' : 'Offline' }}</span>
      </div>
    </div>
  </aside>

  <!-- 환경 추가 모달 -->
  <Teleport to="body">
    <div v-if="showEnvModal" class="env-modal-overlay" @click.self="closeEnvModal">
      <div class="env-modal">
        <div class="env-modal-header">
          <h3>{{ t('env.addNew') }}</h3>
          <button class="env-modal-close" @click="closeEnvModal">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="env-modal-body">
          <div class="env-form-group">
            <label>{{ t('env.name') }}</label>
            <input 
              v-model="newEnvName" 
              type="text" 
              :placeholder="t('env.namePlaceholder')"
              @keydown.enter="handleAddEnvironment"
            />
          </div>
          <div class="env-form-group">
            <label>{{ t('env.folderPath') }}</label>
            <div class="env-path-input">
              <input 
                v-model="newEnvPath" 
                type="text" 
                :placeholder="t('env.folderPlaceholder')"
                readonly
              />
              <button class="env-browse-btn" @click="browseFolder">{{ t('env.browse') }}</button>
            </div>
          </div>
          <p v-if="envError" class="env-error">{{ envError }}</p>
        </div>
        <div class="env-modal-footer">
          <button class="env-modal-btn cancel" @click="closeEnvModal">{{ t('common.cancel') }}</button>
          <button class="env-modal-btn primary" @click="handleAddEnvironment" :disabled="!newEnvName || !newEnvPath">
            {{ t('common.add') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- 환경 삭제 확인 모달 -->
  <Teleport to="body">
    <div v-if="showDeleteEnvModal" class="env-modal-overlay delete-confirm" @click.self="closeDeleteEnvModal">
      <div class="env-modal delete-modal">
        <div class="delete-modal-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 8v4M12 16h.01"/>
          </svg>
        </div>
        <div class="delete-modal-content">
          <h3>{{ t('env.remove') }}</h3>
          <p class="delete-env-name">{{ envToDelete?.name }}</p>
          <p class="delete-description">
            {{ t('env.removeQuestion') }}<br/>
            <span class="delete-note">{{ t('env.removeNote') }}</span>
          </p>
        </div>
        <div class="delete-modal-footer">
          <button class="env-modal-btn cancel" @click="closeDeleteEnvModal">{{ t('common.cancel') }}</button>
          <button class="env-modal-btn danger" @click="confirmDeleteEnvironment">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            {{ t('env.removeBtn') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- 클러스터 편집 모달 -->
  <ClusterEditModal
    :visible="showClusterEditModal"
    :cluster="editingCluster"
    @close="closeClusterEdit"
    @save="handleClusterSave"
    @reset="handleClusterReset"
  />
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, watch, computed } from 'vue';
import { useVault, useHealth, useEnvironment, useI18n } from '../composables';
import ClusterEditModal from './ClusterEditModal.vue';

import type { ViewType, ClusterInfo } from '../types';

const props = defineProps<{
  collapsed: boolean;
  activeFile: string | null;
  dirtyFiles: string[];
  currentView: ViewType;
  // 그래프 뷰용 props
  clusters?: ClusterInfo[];
  selectedClusterId?: number | null;
  graphStats?: { totalNotes: number; totalClusters: number; totalEdges: number };
  isGraphLoading?: boolean;
}>();

const emit = defineEmits<{
  'toggle-collapse': [];
  'select-file': [file: string];
  'file-deleted': [file: string];
  'file-created': [file: string];
  'file-restored': [file: string];
  'file-renamed': [oldPath: string, newPath: string];
  'environment-changed': [];
  'sidebar-width-change': [width: number];
  // 그래프 뷰용 이벤트
  'filter-cluster': [clusterId: number | null];
  'refresh-graph': [];
  'similarity-change': [value: number];
  'update-cluster': [data: { id: number; label: string; color: string; keywords: string[] }];
  'reset-cluster': [clusterId: number];
}>();

// i18n
const { t } = useI18n();

// 리사이즈 관련 상태
const MIN_WIDTH = 180;
const MAX_WIDTH = 500;
const DEFAULT_WIDTH = 260;
const COLLAPSE_THRESHOLD = 120;

const sidebarWidth = ref(DEFAULT_WIDTH);
const isResizing = ref(false);
const isCollapsed = computed(() => props.collapsed);

// 리사이즈 시작
function startResize(e: MouseEvent) {
  if (isCollapsed.value) return;
  
  isResizing.value = true;
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
}

// 리사이즈 처리
function handleResize(e: MouseEvent) {
  if (!isResizing.value) return;
  
  const newWidth = e.clientX;
  
  // 너무 작으면 collapse
  if (newWidth < COLLAPSE_THRESHOLD) {
    emit('toggle-collapse');
    stopResize();
    return;
  }
  
  // 범위 내로 제한
  sidebarWidth.value = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, newWidth));
  emit('sidebar-width-change', sidebarWidth.value);
}

// 리사이즈 종료
function stopResize() {
  isResizing.value = false;
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  
  // 로컬 스토리지에 너비 저장
  localStorage.setItem('cuenote-sidebar-width', sidebarWidth.value.toString());
}

// 초기 너비 로드
onMounted(() => {
  const savedWidth = localStorage.getItem('cuenote-sidebar-width');
  if (savedWidth) {
    sidebarWidth.value = parseInt(savedWidth, 10);
  }
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
});

const { 
  vaultPath, 
  vaultFiles, 
  trashFiles,
  vaultError, 
  todoCount, 
  openVault, 
  deleteFile, 
  createFile,
  renameFile,
  restoreFile,
  permanentDelete,
  emptyTrash,
  refreshFiles
} = useVault();
const { coreStatus } = useHealth();
const {
  environments,
  currentId,
  currentEnvironment,
  error: envError,
  fetchEnvironments,
  addEnvironment,
  selectEnvironment,
  removeEnvironment
} = useEnvironment();

// State
const isCreating = ref(false);
const trashExpanded = ref(true);
const newFileName = ref('');
const isInputMode = ref(false);
const editingFile = ref<string | null>(null);
const editingName = ref('');
const inputRef = ref<HTMLInputElement | null>(null);
const editInputRef = ref<HTMLInputElement | null>(null);

// Environment State
const envDropdownOpen = ref(false);
const showEnvModal = ref(false);
const newEnvName = ref('');
const newEnvPath = ref('');
const showDeleteEnvModal = ref(false);
const envToDelete = ref<{ id: string; name: string; path: string } | null>(null);

// Graph State
const minSimilarity = ref(0.3);

function handleSimilarityInput(e: Event) {
  const value = parseFloat((e.target as HTMLInputElement).value);
  minSimilarity.value = value;
  emit('similarity-change', value);
}

// Cluster Edit Modal State
const showClusterEditModal = ref(false);
const editingCluster = ref<ClusterInfo | null>(null);

function openClusterEdit(cluster: ClusterInfo) {
  editingCluster.value = cluster;
  showClusterEditModal.value = true;
}

function closeClusterEdit() {
  showClusterEditModal.value = false;
  editingCluster.value = null;
}

function handleClusterSave(data: { id: number; label: string; color: string; keywords: string[] }) {
  emit('update-cluster', data);
}

function handleClusterReset(clusterId: number) {
  emit('reset-cluster', clusterId);
}

// 환경 초기화
onMounted(async () => {
  await fetchEnvironments();
});

// 환경 드롭다운 토글
function toggleEnvDropdown() {
  envDropdownOpen.value = !envDropdownOpen.value;
}

// 환경 선택
async function handleSelectEnvironment(id: string) {
  if (id === currentId.value) {
    envDropdownOpen.value = false;
    return;
  }
  
  const success = await selectEnvironment(id);
  if (success) {
    envDropdownOpen.value = false;
    // 파일 목록 새로고침
    await refreshFiles();
    emit('environment-changed');
  }
}

// 환경 제거 모달 열기
function handleRemoveEnvironment(id: string) {
  const env = environments.value.find(e => e.id === id);
  if (env) {
    envToDelete.value = { id: env.id, name: env.name, path: env.path };
    showDeleteEnvModal.value = true;
    envDropdownOpen.value = false;
  }
}

// 환경 삭제 확인 모달 닫기
function closeDeleteEnvModal() {
  showDeleteEnvModal.value = false;
  envToDelete.value = null;
}

// 환경 삭제 확정
async function confirmDeleteEnvironment() {
  if (!envToDelete.value) return;
  
  const success = await removeEnvironment(envToDelete.value.id);
  if (success) {
    await refreshFiles();
    emit('environment-changed');
  }
  closeDeleteEnvModal();
}

// 환경 추가 모달 닫기
function closeEnvModal() {
  showEnvModal.value = false;
  newEnvName.value = '';
  newEnvPath.value = '';
}

// 폴더 선택 (Electron 다이얼로그)
async function browseFolder() {
  // Electron 환경에서 폴더 선택 다이얼로그 열기
  if (window.cuenote?.selectVault) {
    const result = await window.cuenote.selectVault();
    if (result) {
      newEnvPath.value = result;
    }
  } else {
    // 웹 환경에서는 수동 입력
    const path = prompt('폴더 경로를 입력하세요:');
    if (path) {
      newEnvPath.value = path;
    }
  }
}

// 환경 추가
async function handleAddEnvironment() {
  if (!newEnvName.value || !newEnvPath.value) return;
  
  const success = await addEnvironment(newEnvName.value, newEnvPath.value);
  if (success) {
    closeEnvModal();
    await refreshFiles();
    emit('environment-changed');
  }
}

// 경로 truncate
function truncatePath(path: string): string {
  if (path.length <= 30) return path;
  const parts = path.split(/[/\\]/);
  if (parts.length <= 3) return path;
  return `...${parts.slice(-2).join('/')}`;
}

function getFileName(path: string): string {
  const name = path.split(/[/\\]/).pop() || path;
  return name.replace(/\.md$/i, '');
}

function toggleTrash() {
  trashExpanded.value = !trashExpanded.value;
}

// 새 파일 생성 모드 시작
async function startCreateFile() {
  if (isCreating.value) return;
  isInputMode.value = true;
  newFileName.value = '';
  await nextTick();
  inputRef.value?.focus();
}

// 파일 생성 확정
async function handleCreateFile() {
  const name = newFileName.value.trim();
  if (!name) {
    // 빈 이름이면 취소
    isInputMode.value = false;
    return;
  }
  
  isCreating.value = true;
  isInputMode.value = false;
  
  const createdPath = await createFile(name);
  isCreating.value = false;
  
  if (createdPath) {
    emit('file-created', createdPath);
  }
  
  newFileName.value = '';
}

// 파일 생성 취소
function cancelCreate() {
  isInputMode.value = false;
  newFileName.value = '';
}

// 파일 이름 변경 모드 시작
async function startRename(file: string) {
  editingFile.value = file;
  editingName.value = getFileName(file);
  await nextTick();
  editInputRef.value?.focus();
  editInputRef.value?.select();
}

// 파일 이름 변경 확정
async function handleRename() {
  if (!editingFile.value) return;
  
  const newName = editingName.value.trim();
  if (!newName || newName === getFileName(editingFile.value)) {
    // 변경 없거나 빈 이름이면 취소
    cancelRename();
    return;
  }
  
  const oldPath = editingFile.value;
  const newPath = newName.endsWith('.md') ? newName : `${newName}.md`;
  
  const renamedPath = await renameFile(oldPath, newPath);
  
  if (renamedPath) {
    emit('file-renamed', oldPath, renamedPath);
  }
  
  cancelRename();
}

// 파일 이름 변경 취소
function cancelRename() {
  editingFile.value = null;
  editingName.value = '';
}

// 파일 삭제 (팝업 없이 바로 휴지통으로 이동)
async function handleDeleteFile(file: string) {
  const success = await deleteFile(file);
  if (success) {
    emit('file-deleted', file);
  }
}

// 휴지통에서 파일 복원
async function handleRestoreFile(filename: string) {
  const restoredPath = await restoreFile(filename);
  if (restoredPath) {
    emit('file-restored', restoredPath);
  }
}

// 휴지통에서 영구 삭제
async function handlePermanentDelete(filename: string) {
  await permanentDelete(filename);
}

// 휴지통 비우기
async function handleEmptyTrash() {
  await emptyTrash();
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed) !important;
}

/* 리사이즈 핸들 */
.resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  cursor: col-resize;
  background: transparent;
  transition: background 0.15s ease;
  z-index: 100;
}

.resize-handle:hover {
  background: var(--accent-primary);
}

.sidebar.collapsed .resize-handle {
  display: none;
}

.sidebar.collapsed .logo-text,
.sidebar.collapsed .vault-btn span,
.sidebar.collapsed .vault-stats,
.sidebar.collapsed .file-name,
.sidebar.collapsed .section-label,
.sidebar.collapsed .section-header-row,
.sidebar.collapsed .delete-btn,
.sidebar.collapsed .empty-files,
.sidebar.collapsed .trash-section,
.sidebar.collapsed .status-text,
.sidebar.collapsed .new-file-input-wrapper,
.sidebar.collapsed .file-edit-wrapper,
.sidebar.collapsed .modified-indicator {
  display: none;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
  padding: 12px 8px;
  gap: 0;
}

.sidebar.collapsed .sidebar-header .logo {
  display: none;
}

.sidebar.collapsed .sidebar-header .icon-btn {
  margin: 0 auto;
}

.sidebar.collapsed .sidebar-content {
  padding: 8px 4px;
}

.sidebar.collapsed .sidebar-section {
  padding: 4px;
}

.sidebar.collapsed .vault-btn {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .file-item {
  justify-content: center;
}

.sidebar.collapsed .file-btn {
  justify-content: center;
  padding: 10px 0;
  width: 100%;
  min-height: 40px;
}

.sidebar.collapsed .file-btn .file-icon {
  margin: 0;
  width: 18px;
  height: 18px;
}

.sidebar.collapsed .file-item.active .file-btn {
  background: var(--bg-active);
  border-radius: 8px;
}

.sidebar.collapsed .files-section {
  padding: 4px;
}

.sidebar.collapsed .file-list {
  gap: 4px;
  padding: 4px;
}

/* Header */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.logo-icon:hover {
  color: var(--text-primary);
}

.logo-svg {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.3px;
  display: flex;
  align-items: baseline;
}

.logo-cue {
  color: var(--text-primary);
  font-family: var(--font-sans);
}

.logo-note {
  color: var(--text-muted);
  font-family: var(--font-sans);
  font-weight: 400;
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
}

/* Content */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.sidebar-section {
  margin-bottom: 20px;
}

/* Vault Button */
.vault-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.vault-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.vault-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.stat-dot {
  color: var(--text-muted);
  opacity: 0.5;
}

/* Files Section */
.section-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px 10px;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  opacity: 0.7;
}

.new-file-btn {
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

.new-file-btn:hover {
  background: rgba(232, 213, 183, 0.1);
  border-color: rgba(232, 213, 183, 0.2);
  color: #e8d5b7;
}

.empty-files {
  padding: 20px 12px;
  text-align: center;
}

.empty-files p {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.create-first-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(232, 213, 183, 0.08);
  border: 1px solid rgba(232, 213, 183, 0.15);
  border-radius: 6px;
  color: #e8d5b7;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.create-first-btn:hover {
  background: rgba(232, 213, 183, 0.12);
  border-color: rgba(232, 213, 183, 0.25);
}

.file-list {
  list-style: none;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  border-radius: 6px;
  margin-bottom: 2px;
  position: relative;
  animation: fadeIn 0.2s ease backwards;
  animation-delay: var(--delay);
}

.file-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: none;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.12s ease;
  min-width: 0;
}

.file-btn:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
}

.file-item.active .file-btn {
  background: rgba(232, 213, 183, 0.1);
  color: #e8d5b7;
}

.file-icon {
  flex-shrink: 0;
  opacity: 0.6;
}

.file-item.active .file-icon {
  opacity: 1;
  color: #e8d5b7;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 450;
}

.dirty-indicator {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #f59e0b;
  border-radius: 50%;
  margin-left: 6px;
  flex-shrink: 0;
}

/* File Actions */
.file-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s ease;
  margin-right: 4px;
}

.file-item:hover .file-actions {
  opacity: 1;
}

.rename-btn,
.delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: none;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.rename-btn:hover {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
}

.delete-btn:hover {
  background: rgba(220, 38, 38, 0.15);
  color: #dc2626;
}

/* New File Input */
.new-file-input-wrapper,
.file-edit-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  margin-bottom: 2px;
  background: rgba(139, 92, 246, 0.08);
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 6px;
}

.file-edit-wrapper {
  flex: 1;
}

.file-item.editing {
  padding: 0;
}

.file-name-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 450;
  padding: 2px 0;
}

.file-name-input::placeholder {
  color: var(--text-muted);
  font-weight: 400;
}

.new-file-input-wrapper .file-icon,
.file-edit-wrapper .file-icon {
  color: #a78bfa;
  opacity: 0.8;
}

/* Footer */
.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  padding: 8px 10px;
  border-radius: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  flex-shrink: 0;
}

.status-indicator.online .status-dot {
  background: #22c55e;
}

.status-indicator.offline .status-dot {
  background: #dc2626;
}

.status-text {
  font-weight: 450;
}

.error-msg {
  padding: 10px 12px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 6px;
  color: #dc2626;
  font-size: 12px;
  margin-top: 12px;
}

/* Trash Section */
.trash-section {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
}

.trash-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
}

.trash-label svg {
  transition: transform 0.15s ease;
}

.trash-label svg.rotated {
  transform: rotate(-90deg);
}

.trash-count {
  background: rgba(255, 255, 255, 0.06);
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 10px;
  margin-left: 4px;
}

.empty-trash-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s ease;
}

.trash-section:hover .empty-trash-btn {
  opacity: 1;
}

.empty-trash-btn:hover {
  background: rgba(220, 38, 38, 0.15);
  color: #dc2626;
}

.trash-list {
  max-height: 150px;
}

.trash-item {
  opacity: 0.7;
}

.trash-item:hover {
  opacity: 1;
}

.trash-file-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  min-width: 0;
}

.trash-file-info .file-icon {
  opacity: 0.5;
}

.trash-file-info .file-name {
  font-size: 12px;
  color: var(--text-muted);
}

.trash-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s ease;
  margin-right: 4px;
}

.trash-item:hover .trash-actions {
  opacity: 1;
}

.restore-btn,
.permanent-delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: none;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.restore-btn:hover {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.permanent-delete-btn:hover {
  background: rgba(220, 38, 38, 0.15);
  color: #dc2626;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Environment Section */
.environment-section {
  padding: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.env-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--text-muted);
}

.env-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

.env-add-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.env-add-btn:hover {
  background: var(--bg-hover);
  color: var(--accent);
}

.env-selector {
  cursor: pointer;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  transition: all 0.15s ease;
}

.env-selector:hover {
  border-color: var(--accent);
}

.env-current {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.env-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.env-current svg {
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.env-current svg.rotated {
  transform: rotate(180deg);
}

.env-dropdown {
  margin-top: 4px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.env-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.15s ease;
  border-bottom: 1px solid var(--border-subtle);
}

.env-item:last-child {
  border-bottom: none;
}

.env-item:hover {
  background: var(--bg-hover);
}

.env-item.active {
  background: rgba(var(--accent-rgb), 0.1);
}

.env-item.invalid {
  opacity: 0.5;
}

.env-item-info {
  flex: 1;
  min-width: 0;
}

.env-item-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.env-item-path {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 2px;
}

.env-remove-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s ease;
}

.env-item:hover .env-remove-btn {
  opacity: 1;
}

.env-remove-btn:hover {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

/* Environment Modal */
.env-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

.env-modal {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideUp 0.2s ease;
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.env-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.env-modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.env-modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.env-modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.env-modal-body {
  padding: 24px;
}

.env-form-group {
  margin-bottom: 16px;
}

.env-form-group:last-child {
  margin-bottom: 0;
}

.env-form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.env-form-group input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.15s ease;
}

.env-form-group input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.1);
}

.env-path-input {
  display: flex;
  gap: 8px;
}

.env-path-input input {
  flex: 1;
}

.env-browse-btn {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.env-browse-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent);
}

.env-error {
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 6px;
  color: #dc2626;
  font-size: 13px;
}

.env-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.env-modal-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.env-modal-btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.env-modal-btn.cancel:hover {
  background: var(--bg-hover);
}

.env-modal-btn.primary {
  background: var(--accent);
  border: 1px solid var(--accent);
  color: white;
}

.env-modal-btn.primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.env-modal-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.env-modal-btn.danger {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  border: 1px solid #dc2626;
  color: white;
  display: flex;
  align-items: center;
  gap: 6px;
}

.env-modal-btn.danger:hover {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

/* Delete Confirmation Modal */
.env-modal-overlay.delete-confirm {
  backdrop-filter: blur(4px);
}

.env-modal.delete-modal {
  width: 360px;
  text-align: center;
  padding: 0;
}

.delete-modal-icon {
  padding: 24px 24px 0;
  color: #f59e0b;
}

.delete-modal-icon svg {
  filter: drop-shadow(0 4px 12px rgba(245, 158, 11, 0.3));
}

.delete-modal-content {
  padding: 16px 24px 20px;
}

.delete-modal-content h3 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.delete-env-name {
  margin: 0 0 12px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--accent);
}

.delete-description {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.delete-note {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.delete-modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
  justify-content: center;
}

.delete-modal-footer .env-modal-btn {
  flex: 1;
  max-width: 120px;
}

/* ─────────────────────────────────────────────────────────────────────────────
   Graph View - Cluster Panel Styles
   ───────────────────────────────────────────────────────────────────────────── */

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

/* Collapsed sidebar environment */
.sidebar.collapsed .environment-section {
  padding: 4px;
}

.sidebar.collapsed .env-header,
.sidebar.collapsed .env-dropdown {
  display: none;
}

.sidebar.collapsed .env-selector {
  padding: 8px;
  justify-content: center;
}

.sidebar.collapsed .env-name,
.sidebar.collapsed .env-current svg {
  display: none;
}

.sidebar.collapsed .env-selector::before {
  content: '';
  display: block;
  width: 16px;
  height: 16px;
  background: currentColor;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6M4.22 19.78l4.24-4.24M15.54 8.46l4.24-4.24'/%3E%3C/svg%3E") center/contain no-repeat;
  color: var(--text-muted);
}

/* 리사이즈 중 트랜지션 비활성화 */
.sidebar:not(.collapsed) {
  transition: none;
}
</style>


