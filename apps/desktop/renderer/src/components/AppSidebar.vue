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
    />

    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">
          <svg
            class="logo-svg"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect
              x="7"
              y="4"
              width="18"
              height="24"
              rx="2"
              fill="currentColor"
              opacity="0.15"
            />
            <rect
              x="7"
              y="4"
              width="18"
              height="24"
              rx="2"
              stroke="currentColor"
              stroke-width="1.5"
              opacity="0.6"
            />
            <line
              x1="11"
              y1="11"
              x2="21"
              y2="11"
              stroke="currentColor"
              stroke-width="1.2"
              stroke-linecap="round"
              opacity="0.4"
            />
            <line
              x1="11"
              y1="16"
              x2="18"
              y2="16"
              stroke="currentColor"
              stroke-width="1.2"
              stroke-linecap="round"
              opacity="0.3"
            />
            <line
              x1="11"
              y1="21"
              x2="19"
              y2="21"
              stroke="currentColor"
              stroke-width="1.2"
              stroke-linecap="round"
              opacity="0.2"
            />
          </svg>
        </div>
        <span class="logo-text">
          <span class="logo-cue">Cue</span><span class="logo-note">Note</span>
        </span>
      </div>
      <button
        class="icon-btn"
        title="Toggle Sidebar"
        @click="$emit('toggle-collapse')"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <!-- Environment Section -->
      <EnvironmentSelector
        ref="envSelectorRef"
        :environments="environments"
        :current-id="currentId"
        :current-environment="currentEnvironment"
        @open-add-modal="showEnvModal = true"
        @select-environment="handleSelectEnvironment"
        @remove-environment="handleRemoveEnvironment"
      />

      <!-- 그래프 뷰 클러스터 패널 -->
      <template v-if="currentView === 'graph'">
        <GraphClusterPanel
          :clusters="clusters || []"
          :selected-cluster-id="selectedClusterId || null"
          :stats="graphStats || null"
          :is-loading="isGraphLoading || false"
          :unclustered-count="unclusteredCount || 0"
          @filter-cluster="emit('filter-cluster', $event)"
          @refresh-graph="emit('refresh-graph')"
          @edit-cluster="openClusterEdit"
          @create-cluster="openClusterCreate"
        />
      </template>

      <!-- 기본 Vault Section (그래프 뷰가 아닐 때) -->
      <template v-else>
        <div class="sidebar-section">
          <div
            v-if="vaultPath && todoCount !== null"
            class="vault-stats"
          >
            <span class="stat">{{ vaultFiles.length }} notes</span>
            <span class="stat-dot">·</span>
            <span class="stat">{{ todoCount }} tasks</span>
          </div>

          <p
            v-if="vaultError"
            class="error-msg"
          >
            {{ vaultError }}
          </p>
        </div>
      </template>

      <!-- Files List (그래프 뷰가 아닐 때만) -->
      <FileList
        v-if="currentView !== 'graph'"
        :is-git-hub-mode="isGitHubMode"
        :active-file="activeFile"
        :dirty-files="dirtyFiles"
        :vault-path="vaultPath"
        :vault-files="vaultFiles"
        :vault-folders="vaultFolders"
        :github-files="githubFiles"
        :github-loading="githubLoading"
        @select-file="emit('select-file', $event)"
        @select-github-file="handleSelectGitHubFile"
        @delete-file="handleDeleteFile"
        @create-file="handleCreateFile"
        @folder-created="handleFolderCreated"
        @rename-file="handleRenameFile"
        @rename-folder="handleRenameFolder"
        @move-file="handleMoveFile"
        @create-github-file="handleCreateGitHubFile"
        @create-github-folder="handleCreateGitHubFolder"
        @rename-github-file="handleRenameGitHubFile"
        @rename-github-folder="handleRenameGitHubFolder"
        @delete-github-file="handleDeleteGitHubFile"
        @delete-github-folder="handleDeleteGitHubFolder"
      />

      <!-- Git Panel (GitHub 모드일 때만) -->
      <GitPanel
        v-if="currentView !== 'graph'"
        :is-git-hub-mode="isGitHubMode"
        @commit-success="handleCommitSuccess"
      />

      <!-- Trash Section - 로컬 모드 (그래프 뷰가 아닐 때만) -->
      <TrashSection
        v-if="!isGitHubMode && vaultPath && trashFiles.length > 0 && currentView !== 'graph'"
        :trash-files="trashFiles"
        @restore-file="handleRestoreFile"
        @permanent-delete="handlePermanentDelete"
        @empty-trash="handleEmptyTrash"
      />

      <!-- Trash Section - GitHub 모드 (그래프 뷰가 아닐 때만) -->
      <TrashSection
        v-if="isGitHubMode && githubTrashFiles.length > 0 && currentView !== 'graph'"
        :trash-files="githubTrashFiles"
        @restore-file="handleGitHubRestoreFile"
        @permanent-delete="handleGitHubPermanentDelete"
        @empty-trash="handleGitHubEmptyTrash"
      />
    </div>

    <!-- Status Bar -->
    <div class="sidebar-footer">
      <div
        class="status-indicator"
        :class="coreStatus === 'ok' ? 'online' : 'offline'"
      >
        <span class="status-dot" />
        <span class="status-text">{{ coreStatus === 'ok' ? 'Core Online' : 'Offline' }}</span>
      </div>
    </div>
  </aside>

  <!-- 환경 추가 모달 -->
  <EnvAddModal
    :visible="showEnvModal"
    :error="envError"
    :is-git-hub-logged-in="isGitHubLoggedIn"
    :github-user="githubUser"
    :github-repos="githubRepos"
    :github-loading="githubLoading"
    :github-error="githubError"
    :github-validating="githubValidating"
    :is-cloning="isCloning"
    @close="closeEnvModal"
    @add-local="handleAddLocalEnvironment"
    @add-github="handleAddGitHubEnvironment"
    @github-login="handleGitHubLogin"
    @github-logout="handleGitHubLogout"
    @open-create-repo="showCreateRepoModal = true"
    @fetch-repos="fetchGitHubRepos"
  />

  <!-- GitHub 리포지토리 생성 모달 -->
  <CreateRepoModal
    :visible="showCreateRepoModal"
    :creating="creatingRepo"
    :error="createRepoError"
    @close="showCreateRepoModal = false"
    @create="handleCreateRepo"
  />

  <!-- 환경 삭제 확인 모달 -->
  <DeleteEnvModal
    :visible="showDeleteEnvModal"
    :env-name="envToDelete?.name || ''"
    @close="closeDeleteEnvModal"
    @confirm="confirmDeleteEnvironment"
  />



  <!-- 클러스터 편집 모달 -->
  <ClusterEditModal
    :visible="showClusterEditModal"
    :cluster="editingCluster"
    :is-create-mode="isClusterCreateMode"
    @close="closeClusterEdit"
    @save="handleClusterSave"
    @reset="handleClusterReset"
    @create="handleClusterCreate"
    @delete="handleClusterDelete"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useVault, useHealth, useEnvironment, useGitHub } from '../composables';
import ClusterEditModal from './ClusterEditModal.vue';
import {
  EnvironmentSelector,
  GraphClusterPanel,
  FileList,
  TrashSection,
  EnvAddModal,
  CreateRepoModal,
  DeleteEnvModal,
  DisconnectGitHubModal,
  GitPanel
} from './sidebar';

import type { ViewType, ClusterInfo } from '../types';

const props = defineProps<{
  collapsed: boolean;
  activeFile: string | null;
  dirtyFiles: string[];
  currentView: ViewType;
  clusters?: ClusterInfo[];
  selectedClusterId?: number | null | 'unclustered';
  graphStats?: { totalNotes: number; totalClusters: number; totalEdges: number };
  isGraphLoading?: boolean;
  unclusteredCount?: number;
}>();

const emit = defineEmits<{
  'toggle-collapse': [];
  'select-file': [file: string];
  'select-github-file': [path: string];
  'file-deleted': [file: string];
  'file-created': [file: string];
  'file-restored': [file: string];
  'file-renamed': [oldPath: string, newPath: string];
  'environment-changed': [];
  'sidebar-width-change': [width: number];
  'filter-cluster': [clusterId: number | null | 'unclustered'];
  'refresh-graph': [];
  'update-cluster': [data: { id: number; label: string; color: string; keywords: string[] }];
  'reset-cluster': [clusterId: number];
  'create-cluster': [data: { label: string; color: string; keywords: string[] }];
  'delete-cluster': [clusterId: number];
}>();

// 리사이즈 관련
const MIN_WIDTH = 180;
const MAX_WIDTH = 500;
const DEFAULT_WIDTH = 260;
const COLLAPSE_THRESHOLD = 120;

const sidebarWidth = ref(DEFAULT_WIDTH);
const isResizing = ref(false);
const isCollapsed = computed(() => props.collapsed);

function startResize(e: MouseEvent) {
  if (isCollapsed.value) return;
  isResizing.value = true;
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
}

function handleResize(e: MouseEvent) {
  if (!isResizing.value) return;
  const newWidth = e.clientX;
  if (newWidth < COLLAPSE_THRESHOLD) {
    emit('toggle-collapse');
    stopResize();
    return;
  }
  sidebarWidth.value = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, newWidth));
  emit('sidebar-width-change', sidebarWidth.value);
}

function stopResize() {
  isResizing.value = false;
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  localStorage.setItem('cuenote-sidebar-width', sidebarWidth.value.toString());
}

// Composables
const {
  vaultPath,
  vaultFiles,
  vaultFolders,
  trashFiles,
  vaultError,
  todoCount,
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

const {
  user: githubUser,
  repos: githubRepos,
  selectedRepo: githubSelectedRepo,
  files: githubFiles,
  loading: githubLoading,
  error: githubError,
  isValidating: githubValidating,
  isLoggedIn: isGitHubLoggedIn,
  isGitHubActive,
  isCloning,
  trashFiles: githubTrashFiles,
  initGitHub,
  setGitHubActive,
  validateToken: validateGitHubToken,
  fetchRepos: fetchGitHubRepos,
  selectRepo: selectGitHubRepo,
  logout: logoutGitHub,
  createRepo: createGitHubRepo,
  disconnectRepo,
  fetchTrashFiles: fetchGitHubTrashFiles,
  restoreFromTrash: restoreGitHubFromTrash,
  permanentDelete: permanentDeleteGitHub,
  emptyTrash: emptyGitHubTrash
} = useGitHub();

// Computed
const isGitHubMode = computed(() => {
  return isGitHubLoggedIn.value && githubSelectedRepo.value !== null && isGitHubActive.value;
});

// Refs
const envSelectorRef = ref<InstanceType<typeof EnvironmentSelector> | null>(null);
const showEnvModal = ref(false);
const showDeleteEnvModal = ref(false);
const envToDelete = ref<{ id: string; name: string; path: string } | null>(null);
// showDisconnectGitHubModal removed
const showCreateRepoModal = ref(false);
const creatingRepo = ref(false);
const createRepoError = ref<string | null>(null);

// Graph/Cluster State
const showClusterEditModal = ref(false);
const editingCluster = ref<ClusterInfo | null>(null);
const isClusterCreateMode = ref(false);

// Init
onMounted(async () => {
  const savedWidth = localStorage.getItem('cuenote-sidebar-width');
  if (savedWidth) {
    sidebarWidth.value = parseInt(savedWidth, 10);
  }
  await fetchEnvironments();
  await initGitHub();

  // 현재 환경이 GitHub이면 GitHub 모드 활성화
  const env = currentEnvironment.value;
  if (env?.type === 'github' && env.github) {
    const { switchToGitHubEnv } = useGitHub();
    await switchToGitHubEnv({
      id: -1,
      name: env.github.repo,
      full_name: env.github.full_name,
      owner: env.github.owner,
      private: env.github.private || false,
      html_url: `https://github.com/${env.github.owner}/${env.github.repo}`,
      description: null,
      default_branch: 'main'
    });
    // GitHub 환경의 파일 목록도 vault를 통해 갱신
    await refreshFiles();
  }
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
});

// Environment handlers
async function handleSelectEnvironment(id: string) {
  envSelectorRef.value?.closeDropdown();

  if (id === currentId.value) return;

  const success = await selectEnvironment(id);

  if (success) {
    // 선택된 환경이 GitHub 타입이면 GitHub 활성화
    const env = environments.value.find(e => e.id === id);
    if (env?.type === 'github' && env.github) {
      // 이미 클론된 환경이므로 클론/풀 없이 GitHub 모드만 활성화
      // selectGitHubRepo는 매번 클론/풀을 수행하므로 사용하지 않음
      const { switchToGitHubEnv } = useGitHub();
      await switchToGitHubEnv({
        id: -1,
        name: env.github.repo,
        full_name: env.github.full_name,
        owner: env.github.owner,
        private: env.github.private || false,
        html_url: `https://github.com/${env.github.owner}/${env.github.repo}`,
        description: null,
        default_branch: 'main'
      });
      // GitHub 환경의 파일 목록도 vault를 통해 갱신
      await refreshFiles();
    } else {
      // 로컬 환경이면 GitHub 비활성화
      setGitHubActive(false);
      await refreshFiles();
    }

    emit('environment-changed');
  }
}
// handleSelectGitHubEnv removed
// handleDisconnectGitHub removed
// closeDisconnectGitHubModal removed
// confirmDisconnectGitHub removed

function handleRemoveEnvironment(id: string) {
  const env = environments.value.find(e => e.id === id);
  if (env) {
    envToDelete.value = { id: env.id, name: env.name, path: env.path };
    showDeleteEnvModal.value = true;
    envSelectorRef.value?.closeDropdown();
  }
}

function closeEnvModal() {
  showEnvModal.value = false;
}

async function handleAddLocalEnvironment(name: string, path: string) {
  const success = await addEnvironment(name, path);
  if (success) {
    closeEnvModal();
    await refreshFiles();
    emit('environment-changed');
  }
}

async function handleAddGitHubEnvironment(repoId: number) {
  const repo = githubRepos.value.find(r => r.id === repoId);
  if (!repo) return;

  // GitHub 리포지토리를 선택하면 자동으로 환경으로 추가됨 (modify selectRepo in useGitHub)
  await selectGitHubRepo(repo);
  closeEnvModal();
  emit('environment-changed');
}

async function handleGitHubLogin(token: string) {
  const success = await validateGitHubToken(token);
  if (success) {
    await fetchGitHubRepos();
  }
}

function handleGitHubLogout() {
  logoutGitHub();
}

function closeDeleteEnvModal() {
  showDeleteEnvModal.value = false;
  envToDelete.value = null;
}

async function confirmDeleteEnvironment() {
  if (!envToDelete.value) return;

  // GitHub 환경인 경우 연결 해제 로직도 수행 가능하나, 
  // 여기서는 단순히 환경 목록에서 제거하고 필요한 경우 useGitHub 상태도 클리어

  const success = await removeEnvironment(envToDelete.value.id);
  if (success) {
    await refreshFiles();
    emit('environment-changed');
  }
  closeDeleteEnvModal();
}

// Create Repo handler
async function handleCreateRepo(payload: { name: string; description: string; isPrivate: boolean; initReadme: boolean }) {
  creatingRepo.value = true;
  createRepoError.value = null;

  try {
    const repo = await createGitHubRepo(payload.name, payload.description, payload.isPrivate, payload.initReadme);
    if (repo) {
      showCreateRepoModal.value = false;
    } else {
      createRepoError.value = githubError.value || '리포지토리 생성에 실패했습니다';
    }
  } catch (e: any) {
    createRepoError.value = e.message || '리포지토리 생성에 실패했습니다';
  } finally {
    creatingRepo.value = false;
  }
}

// File handlers
// GitHub 파일 선택 - content 미리 로드 없이 경로만 전달
// EditorView에서 /vault/file API로 직접 로드 (로컬 파일과 동일)
function handleSelectGitHubFile(path: string) {
  emit('select-github-file', path);
}

async function handleDeleteFile(file: string) {
  const success = await deleteFile(file);
  if (success) {
    emit('file-deleted', file);
  }
}

async function handleCreateFile(name: string) {
  const createdPath = await createFile(name);
  if (createdPath) {
    emit('file-created', createdPath);
  }
}

async function handleFolderCreated(_folderName: string) {
  // 폴더가 생성되면 파일 목록만 새로고침
  await refreshFiles();
}

// GitHub 파일 생성
async function handleCreateGitHubFile(path: string) {
  const { createFile } = useGitHub();
  // .md 확장자 없는 파일명으로 제목 생성
  const title = path.replace(/\.md$/i, '').split('/').pop() || 'Untitled';
  const content = `# ${title}\n\n`;

  const createdPath = await createFile(path, content);
  if (createdPath) {
    // 파일 목록 새로고침을 위해 환경 변경 이벤트 발생
    emit('environment-changed');
    // 생성된 파일 선택 (EditorView에서 /vault/file로 로드)
    emit('select-github-file', createdPath);
  }
}

// GitHub 폴더 생성 (폴더 내 .gitkeep 파일로 스테이징)
async function handleCreateGitHubFolder(folderName: string) {
  const { createFolder } = useGitHub();
  const success = await createFolder(folderName);
  if (success) {
    emit('environment-changed');
  }
}

async function handleRenameGitHubFile(oldPath: string, newPath: string) {
  const { renameFile } = useGitHub();
  const success = await renameFile(oldPath, newPath);
  if (success) {
    emit('environment-changed');
  }
}

async function handleRenameGitHubFolder(oldPath: string, newPath: string) {
  const { renameFolder } = useGitHub();
  const success = await renameFolder(oldPath, newPath);
  if (success) {
    emit('environment-changed');
  }
}

async function handleDeleteGitHubFile(path: string) {
  const { deleteFile } = useGitHub();
  const success = await deleteFile(path);
  if (success) {
    emit('environment-changed');
  }
}

async function handleDeleteGitHubFolder(path: string) {
  const { deleteFile } = useGitHub();
  // deleteFile은 폴더도 삭제 가능 (shutil.rmtree 사용)
  const success = await deleteFile(path);
  if (success) {
    emit('environment-changed');
  }
}

async function handleRenameFile(oldPath: string, newPath: string) {
  const renamedPath = await renameFile(oldPath, newPath);
  if (renamedPath) {
    emit('file-renamed', oldPath, renamedPath);
  }
}

async function handleRenameFolder(oldPath: string, newPath: string) {
  try {
    const response = await fetch('http://localhost:23432/vault/folder/rename', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_path: oldPath, new_path: newPath })
    });

    if (response.ok) {
      await refreshFiles();
      emit('environment-changed');
    } else {
      const error = await response.json();
      console.error('Failed to rename folder:', error);
    }
  } catch (error) {
    console.error('Error renaming folder:', error);
  }
}

async function handleMoveFile(oldPath: string, newPath: string) {
  if (isGitHubMode.value) {
    // GitHub 모드일 때는 GitHub renameFile 사용
    const { renameFile: renameGitHubFile } = useGitHub();
    const success = await renameGitHubFile(oldPath, newPath);
    if (success) {
      emit('environment-changed');
    }
  } else {
    // 로컬 모드일 때는 vault renameFile 사용
    const movedPath = await renameFile(oldPath, newPath);
    if (movedPath) {
      emit('file-renamed', oldPath, movedPath);
    }
  }
}

async function handleRestoreFile(filename: string) {
  const restoredPath = await restoreFile(filename);
  if (restoredPath) {
    emit('file-restored', restoredPath);
  }
}

async function handlePermanentDelete(filename: string) {
  await permanentDelete(filename);
}

async function handleEmptyTrash() {
  await emptyTrash();
}

// GitHub Trash handlers
async function handleGitHubRestoreFile(filename: string) {
  const success = await restoreGitHubFromTrash(filename);
  if (success) {
    emit('environment-changed');
  }
}

async function handleGitHubPermanentDelete(filename: string) {
  await permanentDeleteGitHub(filename);
}

async function handleGitHubEmptyTrash() {
  await emptyGitHubTrash();
}

// Git handlers
function handleCommitSuccess() {
  // 커밋 성공 시 파일 목록 새로고침
  emit('environment-changed');
}

// Graph handlers
function openClusterEdit(cluster: ClusterInfo) {
  editingCluster.value = cluster;
  isClusterCreateMode.value = false;
  showClusterEditModal.value = true;
}

function openClusterCreate() {
  editingCluster.value = null;
  isClusterCreateMode.value = true;
  showClusterEditModal.value = true;
}

function closeClusterEdit() {
  showClusterEditModal.value = false;
  editingCluster.value = null;
  isClusterCreateMode.value = false;
}

function handleClusterSave(data: { id: number; label: string; color: string; keywords: string[] }) {
  emit('update-cluster', data);
}

function handleClusterReset(clusterId: number) {
  emit('reset-cluster', clusterId);
}

function handleClusterCreate(data: { label: string; color: string; keywords: string[] }) {
  emit('create-cluster', data);
}

function handleClusterDelete(clusterId: number) {
  emit('delete-cluster', clusterId);
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
  color: var(--text-primary);
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

/* Collapsed state hiding */
.sidebar.collapsed .logo-text,
.sidebar.collapsed .vault-stats,
.sidebar.collapsed .status-text,
.sidebar.collapsed .sidebar-content {
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

.sidebar.collapsed .sidebar-footer {
  padding: 12px 8px;
  justify-content: center;
}

.sidebar.collapsed .status-indicator {
  justify-content: center;
  padding: 8px;
}

/* Header */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  min-height: var(--header-height);
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
  background: var(--bg-hover);
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

.error-msg {
  padding: 10px 12px;
  background: var(--error-glow);
  border: 1px solid var(--error-glow);
  border-radius: 6px;
  color: var(--error);
  font-size: 12px;
  margin-top: 12px;
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
  background: var(--success);
}

.status-indicator.offline .status-dot {
  background: var(--error);
}

.status-text {
  font-weight: 450;
}
</style>
