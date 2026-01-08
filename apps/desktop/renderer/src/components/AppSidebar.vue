<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">
          <span class="logo-symbol">C</span>
        </div>
        <span class="logo-text">CueNote</span>
      </div>
      <button class="icon-btn" @click="$emit('toggle-collapse')" title="Toggle Sidebar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <!-- Vault Section -->
      <div class="sidebar-section">
        <button class="vault-btn" @click="openVault">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <span>{{ vaultPath ? vaultPath.split(/[/\\]/).pop() : 'Open Vault' }}</span>
        </button>

        <div v-if="vaultPath && todoCount !== null" class="vault-stats">
          <span class="stat">{{ vaultFiles.length }} notes</span>
          <span class="stat-dot">·</span>
          <span class="stat">{{ todoCount }} tasks</span>
        </div>

        <p v-if="vaultError" class="error-msg">{{ vaultError }}</p>
      </div>

      <!-- Files List -->
      <div class="sidebar-section files-section" v-if="vaultPath">
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

      <!-- Trash Section -->
      <div class="sidebar-section trash-section" v-if="vaultPath && trashFiles.length > 0">
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
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { useVault, useHealth } from '../composables';

const props = defineProps<{
  collapsed: boolean;
  activeFile: string | null;
}>();

const emit = defineEmits<{
  'toggle-collapse': [];
  'select-file': [file: string];
  'file-deleted': [file: string];
  'file-created': [file: string];
  'file-restored': [file: string];
  'file-renamed': [oldPath: string, newPath: string];
}>();

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
  emptyTrash
} = useVault();
const { coreStatus } = useHealth();

// State
const isCreating = ref(false);
const trashExpanded = ref(true);
const newFileName = ref('');
const isInputMode = ref(false);
const editingFile = ref<string | null>(null);
const editingName = ref('');
const inputRef = ref<HTMLInputElement | null>(null);
const editInputRef = ref<HTMLInputElement | null>(null);

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
  width: var(--sidebar-width);
  height: 100%;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease;
  position: relative;
  z-index: 10;
  overflow: hidden;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed);
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
.sidebar.collapsed .status-text {
  display: none;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
  padding: 16px;
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
  padding: 10px;
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
  background: #1a1a2e;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-symbol {
  font-family: 'Georgia', serif;
  font-size: 16px;
  font-weight: 600;
  color: #e8d5b7;
  font-style: italic;
}

.logo-text {
  font-family: 'Georgia', serif;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.3px;
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
</style>


