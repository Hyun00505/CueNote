<template>
  <!-- GitHub 모드일 때 -->
  <div class="sidebar-section files-section" v-if="isGitHubMode">
    <div class="section-header-row">
      <div class="section-label">GitHub Notes</div>
      <div class="section-actions">
        <button class="new-folder-btn" @click="startCreateGitHubFolder" title="새 폴더">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            <line x1="12" y1="11" x2="12" y2="17"/>
            <line x1="9" y1="14" x2="15" y2="14"/>
          </svg>
        </button>
        <button class="new-file-btn" @click="startCreateGitHubFile" title="새 노트">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </button>
        <button class="collapse-btn" @click="triggerGitHubCollapse" title="모두 접기">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="4 14 12 6 20 14" />
            <line x1="12" y1="18" x2="12" y2="6" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 새 GitHub 폴더 입력 -->
    <div v-if="isGitHubFolderInputMode" class="new-file-input-wrapper folder-input">
      <svg class="file-icon folder" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>
      <input
        ref="githubFolderInputRef"
        v-model="newGitHubFolderName"
        type="text"
        class="file-name-input"
        placeholder="폴더 이름"
        @keydown.enter="confirmCreateGitHubFolder"
        @keydown.escape="cancelGitHubFolderInput"
        @blur="cancelGitHubFolderInput"
      />
    </div>

    <!-- 새 GitHub 파일 입력 -->
    <div v-if="isGitHubFileInputMode" class="new-file-input-wrapper">
      <svg class="file-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      <input
        ref="githubFileInputRef"
        v-model="newGitHubFileName"
        type="text"
        class="file-name-input"
        placeholder="파일이름.md"
        @keydown.enter="confirmCreateGitHubFile"
        @keydown.escape="cancelGitHubFileInput"
        @blur="cancelGitHubFileInput"
      />
    </div>

    <div v-if="githubLoading" class="github-files-loading">
      <span class="loading-spinner-small"></span>
      <span>파일 불러오는 중...</span>
    </div>

    <!-- GitHub 파일 트리 -->
    <div class="file-tree" v-else-if="githubFileTree.length > 0">
      <template v-for="item in githubFileTree" :key="item.path">
        <FileTreeItem
          :item="item"
          :active-file="activeFile"
          :depth="0"
          :is-github="true"
          :collapse-trigger="githubCollapseTrigger"
          :editing-file="githubEditingFile"
          :editing-name="githubEditingName"
          :editing-folder="githubEditingFolder"
          :editing-folder-name="githubEditingFolderName"
          @select-file="emit('select-github-file', $event)"
          @start-rename="startGitHubRename"
          @rename-confirm="handleGitHubRename"
          @rename-cancel="cancelGitHubRename"
          @update-editing-name="githubEditingName = $event"
          @start-folder-rename="startGitHubFolderRename"
          @folder-rename-confirm="handleGitHubFolderRename"
          @folder-rename-cancel="cancelGitHubFolderRename"
          @update-editing-folder-name="githubEditingFolderName = $event"
          @delete-file="emit('delete-github-file', $event)"
          @delete-folder="emit('delete-github-folder', $event)"
          @create-file-in="startCreateGitHubFileIn"
          @move-file="handleMoveFile"
        />
      </template>
    </div>

    <div v-else class="empty-files">
      <p>마크다운 파일이 없습니다</p>
    </div>
  </div>

  <!-- 로컬 모드일 때 -->
  <div class="sidebar-section files-section" v-else-if="vaultPath">
    <div class="section-header-row">
      <div class="section-label">Notes</div>
      <div class="section-actions">
        <button class="new-folder-btn" @click="startCreateFolder" title="새 폴더">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            <line x1="12" y1="11" x2="12" y2="17"/>
            <line x1="9" y1="14" x2="15" y2="14"/>
          </svg>
        </button>
        <button class="new-file-btn" @click="startCreateFile()" title="새 노트" :disabled="isCreating || isInputMode">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </button>
        <button class="collapse-btn" @click="triggerLocalCollapse" title="모두 접기">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="4 14 12 6 20 14" />
            <line x1="12" y1="18" x2="12" y2="6" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 새 폴더 입력 -->
    <div v-if="isFolderInputMode" class="new-file-input-wrapper folder-input">
      <svg class="file-icon folder" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>
      <input
        ref="folderInputRef"
        v-model="newFolderName"
        type="text"
        class="file-name-input"
        placeholder="폴더 이름 입력..."
        @keydown.enter="handleCreateFolder"
        @keydown.escape="cancelCreateFolder"
        @blur="handleCreateFolder"
      />
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

    <!-- 파일 트리 -->
    <div 
      class="file-tree" 
      v-if="localFileTree.length > 0 || isInputMode || isFolderInputMode"
      @dragover.prevent="onRootDragOver"
      @dragleave="onRootDragLeave"
      @drop.prevent="onRootDrop"
      :class="{ 'root-drag-over': isRootDragOver }"
    >
      <template v-for="item in localFileTree" :key="item.path">
        <FileTreeItem
          :item="item"
          :active-file="activeFile"
          :dirty-files="dirtyFiles"
          :depth="0"

          :editing-file="editingFile"
          :collapse-trigger="localCollapseTrigger"
          :editing-name="editingName"
          :editing-folder="editingFolder"
          :editing-folder-name="editingFolderName"
          @select-file="emit('select-file', $event)"
          @start-rename="startRename"
          @delete-file="emit('delete-file', $event)"
          @delete-folder="handleDeleteFolder"
          @create-file-in="startCreateFileIn"
          @rename-confirm="handleRename"
          @rename-cancel="cancelRename"
          @update-editing-name="editingName = $event"
          @move-file="handleMoveFile"
          @start-folder-rename="startFolderRename"
          @folder-rename-confirm="handleFolderRename"
          @folder-rename-cancel="cancelFolderRename"
          @update-editing-folder-name="editingFolderName = $event"
        />
      </template>
    </div>

    <div v-else-if="!isInputMode && !isFolderInputMode" class="empty-files">
      <p>No notes yet</p>
      <button class="create-first-btn" @click="startCreateFile()" :disabled="isCreating">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        Create your first note
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import FileTreeItem from './FileTreeItem.vue';
import type { GitHubFile } from '../../composables/useGitHub';

interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: TreeNode[];
}

const CORE_BASE = 'http://127.0.0.1:8787';

const props = defineProps<{
  isGitHubMode: boolean;
  activeFile: string | null;
  dirtyFiles: string[];
  vaultPath: string | null;
  vaultFiles: string[];
  vaultFolders?: string[];
  githubFiles: GitHubFile[];
  githubLoading: boolean;
}>();

const emit = defineEmits<{
  'select-file': [file: string];
  'select-github-file': [path: string];
  'delete-file': [file: string];
  'delete-github-file': [path: string];
  'delete-github-folder': [path: string];
  'create-file': [name: string];
  'folder-created': [name: string];
  'rename-file': [oldPath: string, newPath: string];
  'rename-folder': [oldPath: string, newPath: string];
  'rename-github-file': [oldPath: string, newPath: string];
  'rename-github-folder': [oldPath: string, newPath: string];
  'move-file': [oldPath: string, newPath: string];
  'create-github-file': [path: string];
  'create-github-folder': [path: string];
}>();

// 생성 관련 상태
const isCreating = ref(false);
const newFileName = ref('');
const isInputMode = ref(false);
const inputRef = ref<HTMLInputElement | null>(null);
const createInFolder = ref<string | null>(null);

// 폴더 생성 상태
const isFolderInputMode = ref(false);
const newFolderName = ref('');
const folderInputRef = ref<HTMLInputElement | null>(null);

// GitHub 파일/폴더 생성 상태
const isGitHubFileInputMode = ref(false);
const isGitHubFolderInputMode = ref(false);
const newGitHubFileName = ref('');
const newGitHubFolderName = ref('');
const githubFileInputRef = ref<HTMLInputElement | null>(null);
const githubFolderInputRef = ref<HTMLInputElement | null>(null);

// 편집 관련 상태
const editingFile = ref<string | null>(null);
const editingName = ref('');

// 폴더 이름 변경 관련 상태
const editingFolder = ref<string | null>(null);
const editingFolderName = ref('');

// GitHub 파일/폴더 이름 변경 관련 상태
const githubEditingFile = ref<string | null>(null);
const githubEditingName = ref('');
const githubEditingFolder = ref<string | null>(null);
const githubEditingFolderName = ref('');

// 드래그 앤 드롭 상태
const isRootDragOver = ref(false);

// Collapse Triggers
const githubCollapseTrigger = ref(0);
const localCollapseTrigger = ref(0);

function triggerGitHubCollapse() {
  githubCollapseTrigger.value++;
}

function triggerLocalCollapse() {
  localCollapseTrigger.value++;
}

// 로컬 파일 트리 구조 생성
const localFileTree = computed<TreeNode[]>(() => {
  return buildFileTree(props.vaultFiles, props.vaultFolders);
});

// GitHub 파일 트리 구조 생성 (백엔드에서 이미 트리 구조로 반환)
const githubFileTree = computed<TreeNode[]>(() => {
  // 새로운 API는 children이 포함된 트리 구조를 반환
  return convertGitHubFilesToTree(props.githubFiles);
});

// GitHub 파일 구조를 TreeNode로 변환
function convertGitHubFilesToTree(files: GitHubFile[]): TreeNode[] {
  return files.map(file => ({
    name: file.name,
    path: file.path,
    type: (file.type === 'dir' ? 'folder' : 'file') as 'file' | 'folder',
    children: file.children ? convertGitHubFilesToTree(file.children) : undefined
  })).sort((a, b) => {
    // 폴더 먼저, 그 다음 파일 (이름순)
    if (a.type !== b.type) {
      return a.type === 'folder' ? -1 : 1;
    }
    return a.name.localeCompare(b.name);
  });
}

function buildFileTree(files: string[], folders?: string[]): TreeNode[] {
  const root: TreeNode[] = [];
  const folderMap = new Map<string, TreeNode>();

  // 먼저 모든 폴더 경로 수집 (파일 경로에서 추출 + 빈 폴더 목록)
  const folderPaths = new Set<string>();
  
  // 파일 경로에서 폴더 추출
  for (const filePath of files) {
    const parts = filePath.split('/');
    let currentPath = '';
    for (let i = 0; i < parts.length - 1; i++) {
      currentPath = currentPath ? `${currentPath}/${parts[i]}` : parts[i];
      folderPaths.add(currentPath);
    }
  }
  
  // 빈 폴더도 추가 (별도로 전달받은 폴더 목록)
  if (folders) {
    for (const folder of folders) {
      folderPaths.add(folder);
      // 상위 폴더도 추가
      const parts = folder.split('/');
      let currentPath = '';
      for (let i = 0; i < parts.length; i++) {
        currentPath = currentPath ? `${currentPath}/${parts[i]}` : parts[i];
        folderPaths.add(currentPath);
      }
    }
  }

  // 폴더 노드 생성
  const sortedFolders = Array.from(folderPaths).sort();
  for (const folderPath of sortedFolders) {
    const parts = folderPath.split('/');
    const name = parts[parts.length - 1];
    const parentPath = parts.slice(0, -1).join('/');
    
    const node: TreeNode = {
      name,
      path: folderPath,
      type: 'folder',
      children: []
    };
    
    folderMap.set(folderPath, node);
    
    if (parentPath && folderMap.has(parentPath)) {
      folderMap.get(parentPath)!.children!.push(node);
    } else if (!parentPath) {
      root.push(node);
    }
  }

  // 파일 노드 추가
  for (const filePath of files) {
    const parts = filePath.split('/');
    const name = parts[parts.length - 1];
    const parentPath = parts.slice(0, -1).join('/');
    
    const node: TreeNode = {
      name,
      path: filePath,
      type: 'file'
    };
    
    if (parentPath && folderMap.has(parentPath)) {
      folderMap.get(parentPath)!.children!.push(node);
    } else if (!parentPath) {
      root.push(node);
    }
  }

  // 정렬: 폴더 먼저, 그 다음 파일 (이름순)
  const sortNodes = (nodes: TreeNode[]) => {
    nodes.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === 'folder' ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
    for (const node of nodes) {
      if (node.children) {
        sortNodes(node.children);
      }
    }
  };
  
  sortNodes(root);
  return root;
}

// 새 파일 생성 모드 시작
async function startCreateFile(folderPath?: string) {
  if (isCreating.value) return;
  createInFolder.value = folderPath || null;
  isInputMode.value = true;
  newFileName.value = '';
  await nextTick();
  inputRef.value?.focus();
}

// 특정 폴더에 파일 생성
function startCreateFileIn(folderPath: string) {
  startCreateFile(folderPath);
}

// 파일 생성 확정
async function handleCreateFile() {
  const name = newFileName.value.trim();
  if (!name) {
    isInputMode.value = false;
    createInFolder.value = null;
    return;
  }
  
  isCreating.value = true;
  isInputMode.value = false;
  
  const fileName = name.endsWith('.md') ? name : `${name}.md`;
  const fullPath = createInFolder.value ? `${createInFolder.value}/${fileName}` : fileName;
  
  // 폴더 내 파일 생성인 경우 API 호출
  if (createInFolder.value) {
    try {
      const res = await fetch(`${CORE_BASE}/vault/file/with-folder?path=${encodeURIComponent(fullPath)}`, {
        method: 'POST'
      });
      if (res.ok) {
        emit('create-file', fullPath);
      }
    } catch (e) {
      console.error('Failed to create file:', e);
    }
  } else {
    emit('create-file', name);
  }
  
  isCreating.value = false;
  newFileName.value = '';
  createInFolder.value = null;
}

// 파일 생성 취소
function cancelCreate() {
  isInputMode.value = false;
  newFileName.value = '';
  createInFolder.value = null;
}

// 새 폴더 생성 모드 시작
async function startCreateFolder() {
  isFolderInputMode.value = true;
  newFolderName.value = '';
  await nextTick();
  folderInputRef.value?.focus();
}

// 폴더 생성 확정
async function handleCreateFolder() {
  const name = newFolderName.value.trim();
  if (!name) {
    isFolderInputMode.value = false;
    return;
  }
  
  try {
    const res = await fetch(`${CORE_BASE}/vault/folder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: name })
    });
    
    if (res.ok) {
      // 폴더 생성 이벤트 발생 (파일 생성이 아님)
      emit('folder-created', name);
    }
  } catch (e) {
    console.error('Failed to create folder:', e);
  }
  
  isFolderInputMode.value = false;
  newFolderName.value = '';
}

// 폴더 생성 취소
function cancelCreateFolder() {
  isFolderInputMode.value = false;
  newFolderName.value = '';
}

// GitHub 파일 생성 모드 시작
async function startCreateGitHubFile() {
  isGitHubFileInputMode.value = true;
  newGitHubFileName.value = '';
  await nextTick();
  githubFileInputRef.value?.focus();
}

// GitHub 파일 생성 확정
function confirmCreateGitHubFile() {
  const name = newGitHubFileName.value.trim();
  if (!name) {
    isGitHubFileInputMode.value = false;
    return;
  }
  
  const fileName = name.endsWith('.md') ? name : `${name}.md`;
  emit('create-github-file', fileName);
  
  isGitHubFileInputMode.value = false;
  newGitHubFileName.value = '';
}

// GitHub 파일 생성 취소
function cancelGitHubFileInput() {
  isGitHubFileInputMode.value = false;
  newGitHubFileName.value = '';
}

// GitHub 폴더 생성 모드 시작
async function startCreateGitHubFolder() {
  isGitHubFolderInputMode.value = true;
  newGitHubFolderName.value = '';
  await nextTick();
  githubFolderInputRef.value?.focus();
}

// GitHub 폴더 생성 확정
function confirmCreateGitHubFolder() {
  const name = newGitHubFolderName.value.trim();
  if (!name) {
    isGitHubFolderInputMode.value = false;
    return;
  }
  
  emit('create-github-folder', name);
  
  isGitHubFolderInputMode.value = false;
  newGitHubFolderName.value = '';
}

// GitHub 폴더 생성 취소
function cancelGitHubFolderInput() {
  isGitHubFolderInputMode.value = false;
  newGitHubFolderName.value = '';
}

// GitHub 파일 이름 변경 시작
function startGitHubRename(file: string) {
  githubEditingFile.value = file;
  const parts = file.split('/');
  const name = parts[parts.length - 1];
  githubEditingName.value = name.replace(/\.md$/i, '');
}

// GitHub 파일 이름 변경 확정
function handleGitHubRename() {
  if (!githubEditingFile.value) return;
  
  const newName = githubEditingName.value.trim();
  const parts = githubEditingFile.value.split('/');
  const oldName = parts[parts.length - 1].replace(/\.md$/i, '');
  
  if (!newName || newName === oldName) {
    cancelGitHubRename();
    return;
  }
  
  const oldPath = githubEditingFile.value;
  const newFileName = newName.endsWith('.md') ? newName : `${newName}.md`;
  
  // 폴더 경로 유지
  const folderPath = parts.slice(0, -1).join('/');
  const newPath = folderPath ? `${folderPath}/${newFileName}` : newFileName;
  
  emit('rename-github-file', oldPath, newPath);
  cancelGitHubRename();
}

// GitHub 파일 이름 변경 취소
function cancelGitHubRename() {
  githubEditingFile.value = null;
  githubEditingName.value = '';
}

// GitHub 폴더 이름 변경 시작
function startGitHubFolderRename(folderPath: string) {
  githubEditingFolder.value = folderPath;
  const parts = folderPath.split('/');
  githubEditingFolderName.value = parts[parts.length - 1];
}

// GitHub 폴더 이름 변경 확정
function handleGitHubFolderRename() {
  if (!githubEditingFolder.value) return;
  
  const newName = githubEditingFolderName.value.trim();
  const parts = githubEditingFolder.value.split('/');
  const oldName = parts[parts.length - 1];
  
  if (!newName || newName === oldName) {
    cancelGitHubFolderRename();
    return;
  }
  
  const oldPath = githubEditingFolder.value;
  
  // 부모 폴더 경로 유지
  const parentPath = parts.slice(0, -1).join('/');
  const newPath = parentPath ? `${parentPath}/${newName}` : newName;
  
  emit('rename-github-folder', oldPath, newPath);
  cancelGitHubFolderRename();
}

// GitHub 폴더 이름 변경 취소
function cancelGitHubFolderRename() {
  githubEditingFolder.value = null;
  githubEditingFolderName.value = '';
}

// GitHub 폴더 내 파일 생성
function startCreateGitHubFileIn(folderPath: string) {
  // 폴더 경로를 포함한 파일 생성
  isGitHubFileInputMode.value = true;
  newGitHubFileName.value = `${folderPath}/`;
  nextTick(() => {
    githubFileInputRef.value?.focus();
  });
}

// 폴더 삭제
async function handleDeleteFolder(folderPath: string) {
  
  try {
    const res = await fetch(`${CORE_BASE}/vault/folder?path=${encodeURIComponent(folderPath)}`, {
      method: 'DELETE'
    });
    
    if (res.ok) {
      emit('create-file', ''); // 새로고침 트리거
    }
  } catch (e) {
    console.error('Failed to delete folder:', e);
  }
}

// 파일 이름 변경 모드 시작
function startRename(file: string) {
  editingFile.value = file;
  const parts = file.split('/');
  const name = parts[parts.length - 1];
  editingName.value = name.replace(/\.md$/i, '');
}

// 파일 이름 변경 확정
async function handleRename() {
  if (!editingFile.value) return;
  
  const newName = editingName.value.trim();
  const parts = editingFile.value.split('/');
  const oldName = parts[parts.length - 1].replace(/\.md$/i, '');
  
  if (!newName || newName === oldName) {
    cancelRename();
    return;
  }
  
  const oldPath = editingFile.value;
  const newFileName = newName.endsWith('.md') ? newName : `${newName}.md`;
  
  // 폴더 경로 유지
  const folderPath = parts.slice(0, -1).join('/');
  const newPath = folderPath ? `${folderPath}/${newFileName}` : newFileName;
  
  emit('rename-file', oldPath, newPath);
  cancelRename();
}

// 파일 이름 변경 취소
function cancelRename() {
  editingFile.value = null;
  editingName.value = '';
}

// 폴더 이름 변경 시작
function startFolderRename(folderPath: string) {
  editingFolder.value = folderPath;
  const parts = folderPath.split('/');
  editingFolderName.value = parts[parts.length - 1];
}

// 폴더 이름 변경 확정
async function handleFolderRename() {
  if (!editingFolder.value) return;
  
  const newName = editingFolderName.value.trim();
  const parts = editingFolder.value.split('/');
  const oldName = parts[parts.length - 1];
  
  if (!newName || newName === oldName) {
    cancelFolderRename();
    return;
  }
  
  const oldPath = editingFolder.value;
  
  // 부모 폴더 경로 유지
  const parentPath = parts.slice(0, -1).join('/');
  const newPath = parentPath ? `${parentPath}/${newName}` : newName;
  
  emit('rename-folder', oldPath, newPath);
  cancelFolderRename();
}

// 폴더 이름 변경 취소
function cancelFolderRename() {
  editingFolder.value = null;
  editingFolderName.value = '';
}

// 파일 이동 처리
function handleMoveFile(payload: { oldPath: string; newPath: string }) {
  emit('move-file', payload.oldPath, payload.newPath);
}

// 루트 레벨로 드래그 (폴더에서 루트로 이동)
function onRootDragOver(event: DragEvent) {
  // 폴더 내부 드래그는 무시
  const target = event.target as HTMLElement;
  if (target.closest('.folder-item') || target.closest('.file-item')) {
    isRootDragOver.value = false;
    return;
  }
  
  event.dataTransfer!.dropEffect = 'move';
  isRootDragOver.value = true;
}

function onRootDragLeave(event: DragEvent) {
  // 자식 요소로 이동할 때 무시
  const relatedTarget = event.relatedTarget as HTMLElement;
  if (relatedTarget && (event.currentTarget as HTMLElement).contains(relatedTarget)) {
    return;
  }
  isRootDragOver.value = false;
}

function onRootDrop(event: DragEvent) {
  // 폴더 위에 드롭된 경우 무시 (폴더가 처리)
  const target = event.target as HTMLElement;
  if (target.closest('.folder-item')) {
    isRootDragOver.value = false;
    return;
  }
  
  isRootDragOver.value = false;
  
  const oldPath = event.dataTransfer?.getData('text/plain');
  if (!oldPath) return;
  
  // 이미 루트에 있는 파일은 무시
  if (!oldPath.includes('/')) return;
  
  // 파일명 추출
  const fileName = oldPath.substring(oldPath.lastIndexOf('/') + 1);
  const newPath = fileName;
  
  emit('move-file', oldPath, newPath);
}
</script>

<style scoped>
.files-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

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

.section-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.new-file-btn,
.new-folder-btn,
.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.new-file-btn:hover {
  background: var(--bg-active);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.new-folder-btn:hover {
  background: var(--bg-active);
  border-color: var(--border-default);
  color: var(--text-primary);
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
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.create-first-btn:hover {
  background: var(--bg-active);
  border-color: var(--text-secondary);
}

.file-tree {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  min-height: 50px;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.file-tree.root-drag-over {
  background: var(--accent-glow);
  border: 1px dashed var(--accent-primary);
}

/* New File/Folder Input */
.new-file-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  margin-bottom: 2px;
  background: var(--bg-active);
  border: 1px solid var(--accent-primary);
  border-radius: 6px;
}

.new-file-input-wrapper.folder-input {
  background: var(--bg-active);
  border-color: var(--warning);
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

.new-file-input-wrapper .file-icon {
  color: var(--accent-primary);
  opacity: 0.8;
}

.new-file-input-wrapper.folder-input .file-icon {
  color: var(--warning);
}

/* GitHub File Styles */
.github-files-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.loading-spinner-small {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid var(--border-default);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
