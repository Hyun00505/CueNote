<template>
  <div class="tree-item-wrapper">
    <!-- 폴더 노드 -->
    <div 
      v-if="item.type === 'folder'" 
      class="tree-item folder-item"
      :class="{ 'expanded': isExpanded, 'drag-over': isDragOver, 'editing': editingFolder === item.path }"
      :style="{ paddingLeft: `${depth * 12 + 8}px` }"
      @click="toggleExpand"
      @dblclick.stop="startFolderRename"
      @contextmenu.prevent="showFolderMenu"
      @dragover.prevent="onDragOver"
      @dragleave="onDragLeave"
      @drop.prevent="onDrop"
    >
      <svg class="expand-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline :points="isExpanded ? '6 9 12 15 18 9' : '9 6 15 12 9 18'" />
      </svg>
      <svg class="folder-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path v-if="isExpanded" d="M5 19a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4l2 2h9a2 2 0 0 1 2 2v1M5 19h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2z"/>
        <path v-else d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>
      
      <!-- 폴더 이름 편집 모드 -->
      <input
        v-if="editingFolder === item.path"
        ref="folderEditInputRef"
        :value="editingFolderName"
        @input="onFolderEditInput"
        @keydown.enter="emit('folder-rename-confirm')"
        @keydown.escape="emit('folder-rename-cancel')"
        @blur="emit('folder-rename-confirm')"
        class="folder-name-edit-input"
        @click.stop
      />
      <span v-else class="item-name">{{ item.name }}</span>
      
      <!-- 폴더 액션 버튼들 -->
      <div class="folder-actions" v-if="editingFolder !== item.path">
        <button class="folder-action-btn" @click.stop="emit('create-file-in', item.path)" title="새 파일">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </button>
        <div class="delete-popover-wrapper">
          <button class="folder-action-btn delete" @click.stop="showFolderDeletePopover = true" title="폴더 삭제">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
          <!-- 폴더 삭제 확인 팝오버 -->
          <Transition name="popover">
            <div v-if="showFolderDeletePopover" class="delete-popover" @click.stop>
              <p class="delete-popover-text">삭제할까요?</p>
              <div class="delete-popover-actions">
                <button class="popover-btn cancel" @click.stop="showFolderDeletePopover = false">취소</button>
                <button class="popover-btn confirm" @click.stop="confirmFolderDelete">삭제</button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- 폴더 자식 노드들 -->
    <div v-if="item.type === 'folder' && isExpanded && item.children" class="tree-children">
      <FileTreeItem
        v-for="child in item.children"
        :key="child.path"
        :item="child"
        :active-file="activeFile"
        :dirty-files="dirtyFiles"
        :depth="depth + 1"
        :editing-file="editingFile"
        :editing-name="editingName"
        :editing-folder="editingFolder"
        :editing-folder-name="editingFolderName"
        :is-github="isGitHub"
        @select-file="emit('select-file', $event)"
        @start-rename="emit('start-rename', $event)"
        @delete-file="emit('delete-file', $event)"
        @delete-folder="emit('delete-folder', $event)"
        @create-file-in="emit('create-file-in', $event)"
        @rename-confirm="emit('rename-confirm')"
        @rename-cancel="emit('rename-cancel')"
        @update-editing-name="emit('update-editing-name', $event)"
        @move-file="emit('move-file', $event)"
        @start-folder-rename="emit('start-folder-rename', $event)"
        @folder-rename-confirm="emit('folder-rename-confirm')"
        @folder-rename-cancel="emit('folder-rename-cancel')"
        @update-editing-folder-name="emit('update-editing-folder-name', $event)"
      />
    </div>

    <!-- 파일 노드 -->
    <div 
      v-else-if="item.type === 'file'"
      class="tree-item file-item"
      :class="{ 
        'active': activeFile === item.path,
        'dirty': dirtyFiles?.includes(item.path),
        'editing': editingFile === item.path,
        'dragging': isDragging
      }"
      :style="{ paddingLeft: `${depth * 12 + 8}px` }"
      :draggable="editingFile !== item.path"
      @click="emit('select-file', item.path)"
      @dblclick="startRename"
      @contextmenu.prevent="showFileMenu"
      @dragstart="onDragStart"
      @dragend="onDragEnd"
    >
      <svg class="file-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      
      <!-- 편집 모드 -->
      <input
        v-if="editingFile === item.path"
        ref="editInputRef"
        :value="editingName"
        @input="onEditInput"
        @keydown.enter="emit('rename-confirm')"
        @keydown.escape="emit('rename-cancel')"
        @blur="emit('rename-confirm')"
        class="file-name-edit-input"
        @click.stop
      />
      <span v-else class="item-name">{{ displayName }}</span>
      
      <!-- 변경 표시 -->
      <span v-if="dirtyFiles?.includes(item.path)" class="dirty-indicator">●</span>
      
      <!-- 파일 액션 버튼 -->
      <div class="file-actions" v-if="editingFile !== item.path">
        <div class="delete-popover-wrapper">
          <button class="file-action-btn delete" @click.stop="showFileDeletePopover = true" title="삭제">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
          <!-- 파일 삭제 확인 팝오버 -->
          <Transition name="popover">
            <div v-if="showFileDeletePopover" class="delete-popover" @click.stop>
              <p class="delete-popover-text">삭제할까요?</p>
              <div class="delete-popover-actions">
                <button class="popover-btn cancel" @click.stop="showFileDeletePopover = false">취소</button>
                <button class="popover-btn confirm" @click.stop="confirmFileDelete">삭제</button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue';

interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: TreeNode[];
}

const props = defineProps<{
  item: TreeNode;
  activeFile: string | null;
  dirtyFiles?: string[];
  depth: number;
  editingFile?: string | null;
  editingName?: string;
  editingFolder?: string | null;
  editingFolderName?: string;
  isGitHub?: boolean;
}>();

const emit = defineEmits<{
  'select-file': [path: string];
  'start-rename': [path: string];
  'delete-file': [path: string];
  'delete-folder': [path: string];
  'create-file-in': [folderPath: string];
  'rename-confirm': [];
  'rename-cancel': [];
  'update-editing-name': [name: string];
  'move-file': [payload: { oldPath: string; newPath: string }];
  'start-folder-rename': [path: string];
  'folder-rename-confirm': [];
  'folder-rename-cancel': [];
  'update-editing-folder-name': [name: string];
}>();

const isExpanded = ref(true);
const editInputRef = ref<HTMLInputElement | null>(null);
const folderEditInputRef = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);
const isDragOver = ref(false);

// 삭제 팝오버 상태
const showFileDeletePopover = ref(false);
const showFolderDeletePopover = ref(false);

// 팝오버 외부 클릭 시 닫기
function handleOutsideClick(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (!target.closest('.delete-popover-wrapper')) {
    showFileDeletePopover.value = false;
    showFolderDeletePopover.value = false;
  }
}

// 팝오버 열릴 때 외부 클릭 감지
watch([showFileDeletePopover, showFolderDeletePopover], ([file, folder]) => {
  if (file || folder) {
    setTimeout(() => document.addEventListener('click', handleOutsideClick), 0);
  } else {
    document.removeEventListener('click', handleOutsideClick);
  }
});

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick);
});

// 파일 삭제 확인
function confirmFileDelete() {
  showFileDeletePopover.value = false;
  emit('delete-file', props.item.path);
}

// 폴더 삭제 확인
function confirmFolderDelete() {
  showFolderDeletePopover.value = false;
  emit('delete-folder', props.item.path);
}

// 파일명 표시 (확장자 제거)
const displayName = computed(() => {
  if (props.item.type === 'file') {
    return props.item.name.replace(/\.md$/i, '');
  }
  return props.item.name;
});

// 폴더 토글
function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}

// 파일 이름 변경 시작
function startRename() {
  emit('start-rename', props.item.path);
}

// 편집 입력 핸들러
function onEditInput(event: Event) {
  const target = event.target as HTMLInputElement;
  emit('update-editing-name', target.value);
}

// 편집 시작 시 input에 포커스
watch(() => props.editingFile, async (newVal) => {
  if (newVal === props.item.path) {
    await nextTick();
    editInputRef.value?.focus();
    editInputRef.value?.select();
  }
});

// 폴더 이름 변경 시작
function startFolderRename() {
  emit('start-folder-rename', props.item.path);
}

// 폴더 편집 입력 핸들러
function onFolderEditInput(event: Event) {
  const target = event.target as HTMLInputElement;
  emit('update-editing-folder-name', target.value);
}

// 폴더 편집 시작 시 input에 포커스
watch(() => props.editingFolder, async (newVal) => {
  if (newVal === props.item.path) {
    await nextTick();
    folderEditInputRef.value?.focus();
    folderEditInputRef.value?.select();
  }
});

// 파일 컨텍스트 메뉴
function showFileMenu(event: MouseEvent) {
  if (props.isGitHub) return;
  // 여기에 컨텍스트 메뉴 로직 추가 가능
  // 현재는 더블클릭으로 이름 변경, 별도 삭제 버튼 사용
}

// 폴더 컨텍스트 메뉴
function showFolderMenu(event: MouseEvent) {
  if (props.isGitHub) return;
  // 폴더 컨텍스트 메뉴
}

// 드래그 시작 (파일)
function onDragStart(event: DragEvent) {
  if (props.item.type !== 'file') return;
  
  isDragging.value = true;
  event.dataTransfer?.setData('text/plain', props.item.path);
  event.dataTransfer!.effectAllowed = 'move';
}

// 드래그 종료 (파일)
function onDragEnd() {
  isDragging.value = false;
}

// 드래그 오버 (폴더)
function onDragOver(event: DragEvent) {
  if (props.item.type !== 'folder') return;
  
  event.dataTransfer!.dropEffect = 'move';
  isDragOver.value = true;
}

// 드래그 리브 (폴더)
function onDragLeave() {
  isDragOver.value = false;
}

// 드롭 (폴더)
function onDrop(event: DragEvent) {
  if (props.item.type !== 'folder') return;
  
  isDragOver.value = false;
  
  const oldPath = event.dataTransfer?.getData('text/plain');
  if (!oldPath) return;
  
  // 같은 폴더로 이동하는 경우 무시
  const oldFolder = oldPath.includes('/') ? oldPath.substring(0, oldPath.lastIndexOf('/')) : '';
  if (oldFolder === props.item.path) return;
  
  // 파일명 추출
  const fileName = oldPath.includes('/') ? oldPath.substring(oldPath.lastIndexOf('/') + 1) : oldPath;
  const newPath = `${props.item.path}/${fileName}`;
  
  // 자기 자신의 하위 폴더로 이동 방지
  if (newPath.startsWith(oldPath + '/')) return;
  
  emit('move-file', { oldPath, newPath });
  
  // 폴더 펼치기
  isExpanded.value = true;
}
</script>

<style scoped>
.tree-item-wrapper {
  user-select: none;
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s ease;
  position: relative;
}

.tree-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

/* 파일 아이템 */
.file-item {
  margin-left: 4px;
}

.file-item.active {
  background: rgba(139, 92, 246, 0.15);
  border-left: 2px solid #a78bfa;
  margin-left: 2px;
}

.file-item.dirty .item-name {
  font-style: italic;
}

.file-item .file-icon {
  color: var(--text-muted);
  opacity: 0.7;
  flex-shrink: 0;
}

.file-item.active .file-icon {
  color: #a78bfa;
  opacity: 1;
}

/* 폴더 아이템 */
.folder-item {
  font-weight: 500;
}

.folder-item .expand-icon {
  flex-shrink: 0;
  color: var(--text-muted);
  opacity: 0.6;
  transition: transform 0.15s ease;
}

.folder-item.expanded .expand-icon {
  opacity: 0.8;
}

.folder-item .folder-icon {
  color: #f59e0b;
  flex-shrink: 0;
}

.folder-item.expanded .folder-icon {
  color: #fbbf24;
}

/* 아이템 이름 */
.item-name {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 변경 표시 */
.dirty-indicator {
  color: #f59e0b;
  font-size: 8px;
  flex-shrink: 0;
  margin-left: 4px;
}

/* 폴더 액션 버튼 */
.folder-actions {
  display: none;
  gap: 2px;
  flex-shrink: 0;
  margin-left: auto;
}

.folder-item:hover .folder-actions {
  display: flex;
}

.folder-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.folder-action-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: var(--text-primary);
}

.folder-action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* 파일 액션 버튼 */
.file-actions {
  display: none;
  gap: 2px;
  flex-shrink: 0;
  margin-left: auto;
}

.file-item:hover .file-actions {
  display: flex;
}

.file-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.file-action-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: var(--text-primary);
}

.file-action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* 파일 이름 편집 입력 */
.file-name-edit-input,
.folder-name-edit-input {
  flex: 1;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 13px;
  color: var(--text-primary);
  outline: none;
}

.file-name-edit-input:focus,
.folder-name-edit-input:focus {
  border-color: #a78bfa;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.15);
}

.folder-item.editing {
  background: rgba(139, 92, 246, 0.1);
}

/* 자식 노드들 */
.tree-children {
  /* 자식 노드 표시 */
}

/* 드래그 앤 드롭 스타일 */
.file-item[draggable="true"] {
  cursor: grab;
}

.file-item[draggable="true"]:active {
  cursor: grabbing;
}

.file-item.dragging {
  opacity: 0.5;
}

.folder-item.drag-over {
  background: rgba(139, 92, 246, 0.2);
  border: 1px dashed #a78bfa;
  border-radius: 6px;
}

/* 삭제 팝오버 */
.delete-popover-wrapper {
  position: relative;
}

.delete-popover {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 4px;
  background: var(--bg-secondary, #1e1e2e);
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  padding: 10px 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 100;
  min-width: 120px;
}

.delete-popover-text {
  font-size: 12px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  white-space: nowrap;
}

.delete-popover-actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.popover-btn {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.popover-btn.cancel {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-muted);
}

.popover-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.12);
  color: var(--text-primary);
}

.popover-btn.confirm {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.popover-btn.confirm:hover {
  background: rgba(239, 68, 68, 0.35);
}

/* 팝오버 애니메이션 */
.popover-enter-active,
.popover-leave-active {
  transition: all 0.15s ease;
}

.popover-enter-from,
.popover-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.95);
}
</style>
