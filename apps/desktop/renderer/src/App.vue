<template>
  <div
    class="app-container"
    :class="{ 'is-resizing': isResizing }"
  >
    <AppSidebar
      v-if="currentView !== 'settings' && currentView !== 'dashboard'"
      :collapsed="sidebarCollapsed"
      :active-file="activeFile"
      :dirty-files="dirtyFiles"
      :current-view="currentView"
      :clusters="graphClusters"
      :selected-cluster-id="selectedClusterId"
      :graph-stats="graphStats"
      :is-graph-loading="isGraphLoading"
      :unclustered-count="unclusteredCount"
      @toggle-collapse="handleToggleCollapse"
      @select-file="handleSelectFile"
      @select-github-file="handleSelectGitHubFile"
      @file-deleted="handleFileDeleted"
      @file-created="handleFileCreated"
      @file-restored="handleFileRestored"
      @sidebar-width-change="handleSidebarWidthChange"
      @filter-cluster="handleFilterCluster"
      @refresh-graph="handleRefreshGraph"
      @update-cluster="handleUpdateCluster"
      @reset-cluster="handleResetCluster"
      @create-cluster="handleCreateCluster"
      @delete-cluster="handleDeleteCluster"
      @environment-changed="handleEnvironmentChanged"
    />

    <!-- 저장 확인 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showUnsavedModal"
          class="unsaved-modal-overlay"
          @click.self="cancelFileSwitch"
        >
          <div class="unsaved-modal">
            <div class="unsaved-modal-icon">
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line
                  x1="12"
                  y1="9"
                  x2="12"
                  y2="13"
                />
                <line
                  x1="12"
                  y1="17"
                  x2="12.01"
                  y2="17"
                />
              </svg>
            </div>
            <h3>저장되지 않은 변경사항</h3>
            <p>현재 문서에 저장되지 않은 변경사항이 있습니다.<br>저장하시겠습니까?</p>
            <div class="unsaved-modal-actions">
              <button
                class="btn-discard"
                @click="discardAndSwitch"
              >
                저장 안 함
              </button>
              <button
                class="btn-cancel"
                @click="cancelFileSwitch"
              >
                취소
              </button>
              <button
                class="btn-save"
                @click="saveAndSwitch"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                  <polyline points="17 21 17 13 7 13 7 21" />
                  <polyline points="7 3 7 8 15 8" />
                </svg>
                저장
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <main class="main-content">
      <MainHeader
        v-if="currentView !== 'settings'"
        :active-file="activeFile"
        :vault-name="vaultName"
        :current-view="currentView"
        @change-view="handleChangeView"
        @open-settings="handleOpenSettings"
      />

      <div class="content-area">
        <EditorView
          v-show="currentView === 'editor'"
          ref="editorViewRef"
          :active-file="activeFile"
          :is-github-file="isGitHubFile"
          :github-content="githubFileContent"
          @dirty-change="isFileDirty = $event"
          @dirty-files-change="handleDirtyFilesChange"
        />

        <DashboardView
          v-show="currentView === 'dashboard'"
          ref="dashboardViewRef"
          :has-vault="!!vaultPath"
        />

        <GraphView
          v-show="currentView === 'graph'"
          ref="graphViewRef"
          :filter-cluster-id="selectedClusterId"
          :is-active="currentView === 'graph'"
          @select-file="handleSelectFile"
          @graph-loaded="handleGraphLoaded"
        />

        <SettingsView
          v-if="currentView === 'settings'"
          @back="handleBackFromSettings"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { AppSidebar, MainHeader, EditorView, DashboardView, SettingsView, GraphView } from './components';
import { useVault, useHealth, useFonts, useGraph, useGitHub } from './composables';
import type { ViewType, ClusterInfo } from './types';
import { API_ENDPOINTS } from './config/api';

const sidebarCollapsed = ref(false);
const currentView = ref<ViewType>('editor');
const activeFile = ref<string | null>(null);
const previousView = ref<ViewType>('editor');
const isFileDirty = ref(false);
const isResizing = ref(false);
const dirtyFiles = ref<string[]>([]);

// GitHub 파일 관련
const isGitHubFile = ref(false);
const githubFileContent = ref<string | null>(null);

// 저장 확인 모달 관련
const showUnsavedModal = ref(false);
const pendingFile = ref<string | null>(null);
const editorViewRef = ref<InstanceType<typeof EditorView> | null>(null);
const dashboardViewRef = ref<InstanceType<typeof DashboardView> | null>(null);
const graphViewRef = ref<InstanceType<typeof GraphView> | null>(null);

// 그래프 뷰 관련 상태
const graphClusters = ref<ClusterInfo[]>([]);
const graphStats = ref({ totalNotes: 0, totalClusters: 0, totalEdges: 0 });
const selectedClusterId = ref<number | null | 'unclustered'>(null);
const isGraphLoading = ref(false);

// dirty 파일 목록 업데이트
function handleDirtyFilesChange(files: string[]) {
  dirtyFiles.value = files;
}

// 뷰 전환 핸들러
function handleChangeView(view: ViewType) {
  currentView.value = view;

  // 캘린더 뷰로 전환할 때 오늘 날짜로 스크롤
  if (view === 'dashboard') {
    nextTick(() => {
      dashboardViewRef.value?.scrollToToday();
    });
  }
}

// 사이드바 토글
function handleToggleCollapse() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
}

// 사이드바 너비 변경 처리
function handleSidebarWidthChange(width: number) {
  isResizing.value = true;
  // 짧은 지연 후 리사이즈 상태 해제
  setTimeout(() => {
    isResizing.value = false;
  }, 100);
}

const { vaultPath, initVault, refreshFiles } = useVault();
const { checkHealth } = useHealth();
const { initFonts } = useFonts();
const { renameFile: renameGitHubFile } = useGitHub();

const vaultName = computed(() => {
  return vaultPath.value?.split(/[/\\]/).pop() ?? null;
});

function handleSelectFile(file: string) {
  // 같은 파일이면 무시
  if (file === activeFile.value && !isGitHubFile.value) return;

  // GitHub 모드 해제
  isGitHubFile.value = false;
  githubFileContent.value = null;

  // 바로 파일 전환 (저장하지 않은 변경사항은 캐시에 유지됨)
  activeFile.value = file;
  currentView.value = 'editor';
}

// GitHub 파일 선택 핸들러 (로컬 파일과 동일하게 처리)
// 백엔드의 /vault/file API가 GitHub 환경에서도 클론 경로를 사용
function handleSelectGitHubFile(path: string) {
  // 같은 파일이면 무시
  if (path === activeFile.value && isGitHubFile.value) return;

  isGitHubFile.value = true;
  githubFileContent.value = null; // content는 EditorView에서 /vault/file로 로드
  activeFile.value = path;
  currentView.value = 'editor';
}

async function saveAndSwitch() {
  // EditorView의 save 함수 호출
  if (editorViewRef.value?.save) {
    await editorViewRef.value.save();
  }
  showUnsavedModal.value = false;
  if (pendingFile.value) {
    activeFile.value = pendingFile.value;
    pendingFile.value = null;
  }
  currentView.value = 'editor';
}

function discardAndSwitch() {
  showUnsavedModal.value = false;
  isFileDirty.value = false;
  if (pendingFile.value) {
    activeFile.value = pendingFile.value;
    pendingFile.value = null;
  }
  currentView.value = 'editor';
}

function cancelFileSwitch() {
  showUnsavedModal.value = false;
  pendingFile.value = null;
}

function handleFileDeleted(file: string) {
  // 삭제된 파일이 현재 열린 파일이면 선택 해제
  if (activeFile.value === file) {
    activeFile.value = null;
  }
}

function handleFileCreated(file: string) {
  // 새로 생성된 파일을 자동으로 선택하고 에디터로 이동
  activeFile.value = file;
  currentView.value = 'editor';
}

function handleFileRestored(file: string) {
  // 복원된 파일을 자동으로 선택
  activeFile.value = file;
  currentView.value = 'editor';
}

// 환경 변경 핸들러
async function handleEnvironmentChanged() {
  console.log('[App] Environment changed, current view:', currentView.value);

  // 현재 선택된 파일 초기화
  activeFile.value = null;
  isGitHubFile.value = false;
  githubFileContent.value = null;

  // 그래프 관련 상태 초기화
  graphClusters.value = [];
  graphStats.value = { totalNotes: 0, totalClusters: 0, totalEdges: 0 };
  selectedClusterId.value = null;

  // 그래프 뷰가 비활성 상태면 데이터만 초기화
  // (활성 상태면 GraphView의 환경 watch가 자동으로 새 데이터 로드)
  if (currentView.value !== 'graph') {
    clearGraphData();
  }
}

function handleOpenSettings() {
  previousView.value = currentView.value;
  currentView.value = 'settings';
}

// 파일 이름 변경
async function handleRenameFile(payload: { oldPath: string; newName: string }) {
  const { oldPath, newName } = payload;

  // 기존 경로에서 폴더 경로 추출
  const pathParts = oldPath.split('/');
  pathParts.pop(); // 파일명 제거
  const folderPath = pathParts.join('/');

  // 새 경로 생성
  const newPath = folderPath ? `${folderPath}/${newName}.md` : `${newName}.md`;

  try {
    if (isGitHubFile.value) {
      // GitHub 파일인 경우
      const success = await renameGitHubFile(oldPath, newPath);
      if (success) {
        activeFile.value = newPath;
      }
    } else {
      // 로컬 파일인 경우
      const response = await fetch(API_ENDPOINTS.VAULT.RENAME, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_path: oldPath, new_path: newPath })
      });

      if (response.ok) {
        activeFile.value = newPath;
        await refreshFiles();
      } else {
        const error = await response.json();
        console.error('Failed to rename file:', error);
      }
    }
  } catch (error) {
    console.error('Error renaming file:', error);
  }
}

function handleBackFromSettings() {
  // 설정에서 돌아올 때 이전 뷰로 복원
  currentView.value = previousView.value;
}

// 그래프 뷰 관련 핸들러
function handleGraphLoaded(data: { clusters: ClusterInfo[]; stats: any }) {
  graphClusters.value = data.clusters;
  graphStats.value = data.stats;
  isGraphLoading.value = false;
}

function handleFilterCluster(clusterId: number | null | 'unclustered') {
  selectedClusterId.value = clusterId;
}

async function handleRefreshGraph() {
  isGraphLoading.value = true;
  if (graphViewRef.value?.refresh) {
    await graphViewRef.value.refresh();
  }
}

// 클러스터 설정 업데이트
const { updateCluster, resetClusterSettings, createCluster, deleteCluster, clearGraphData, unclusteredCount } = useGraph();

async function handleUpdateCluster(data: { id: number; label: string; color: string; keywords: string[] }) {
  await updateCluster(data.id, {
    label: data.label,
    color: data.color,
    keywords: data.keywords
  });

  // 로컬 상태가 즉시 업데이트되므로 새로고침 불필요
  // 사이드바 클러스터 목록도 자동 반영
  updateGraphClustersFromLocal();
}

async function handleResetCluster(_clusterId: number) {
  // 전체 클러스터 설정 초기화 (개별 클러스터 초기화는 추후 구현)
  await resetClusterSettings();
  await handleRefreshGraph();
}

async function handleCreateCluster(data: { label: string; color: string; keywords: string[] }) {
  const newCluster = await createCluster(data.label, data.color, data.keywords);
  if (newCluster) {
    // 로컬 상태가 즉시 업데이트되므로 새로고침 불필요
    updateGraphClustersFromLocal();
  }
}

async function handleDeleteCluster(clusterId: number) {
  const success = await deleteCluster(clusterId);
  if (success) {
    // 삭제된 클러스터 필터링 중이었다면 전체 보기로 전환
    if (selectedClusterId.value === clusterId) {
      selectedClusterId.value = null;
    }
    updateGraphClustersFromLocal();
  }
}

// 로컬 그래프 데이터에서 사이드바 클러스터 목록 업데이트
const { graphData } = useGraph();
function updateGraphClustersFromLocal() {
  if (graphData.value) {
    graphClusters.value = [...graphData.value.clusters];
    graphStats.value = {
      totalNotes: graphData.value.totalNotes,
      totalClusters: graphData.value.clusters.length,
      totalEdges: graphData.value.edges.length
    };
  }
}

// 설정 페이지로 이동 시 이전 뷰 저장
watch(currentView, (newView, oldView) => {
  if (newView === 'settings' && oldView !== 'settings') {
    previousView.value = oldView;
  }
});

// 테마 초기화 함수
function initTheme() {
  const savedTheme = localStorage.getItem('cuenote-theme');
  const validThemes = ['dark', 'dim', 'github-dark', 'light'];
  const theme = validThemes.includes(savedTheme as string) ? savedTheme : 'dark';
  document.documentElement.setAttribute('data-theme', theme);
}

onMounted(async () => {
  // 앱 시작 시 테마 초기화 (설정 페이지 방문 전에도 적용)
  initTheme();

  // 앱 시작 시 뷰를 에디터로 명시적 초기화 (중복 설정으로 확실하게)
  currentView.value = 'editor';
  previousView.value = 'editor';

  // 선택된 파일 초기화 (새 파일 없이 시작)
  activeFile.value = null;
  isGitHubFile.value = false;
  githubFileContent.value = null;

  checkHealth();
  initFonts();
  // 앱 시작 시 기본 vault(data 폴더) 자동 로드
  await initVault();

  // Vue 렌더링 사이클 완료 후 한 번 더 확인
  await nextTick();
  if (currentView.value !== 'editor') {
    currentView.value = 'editor';
  }
});
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow: hidden;
}

.app-container.is-resizing {
  cursor: col-resize;
  user-select: none;
}

.app-container.is-resizing * {
  pointer-events: none;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary);
}

.content-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* 뷰 컴포넌트들의 기본 스타일 - v-show가 제대로 작동하도록 */
.content-area>* {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

/* 저장 확인 모달 */
.unsaved-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.unsaved-modal {
  background: var(--bg-secondary, #1e1e2e);
  border: 1px solid var(--border-primary, #313244);
  border-radius: 12px;
  padding: 28px 32px;
  width: 380px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.unsaved-modal-icon {
  color: #f9e2af;
  margin-bottom: 16px;
}

.unsaved-modal h3 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #cdd6f4);
}

.unsaved-modal p {
  margin: 0 0 24px;
  font-size: 14px;
  color: var(--text-secondary, #a6adc8);
  line-height: 1.5;
}

.unsaved-modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.unsaved-modal-actions button {
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-discard {
  background: transparent;
  border: 1px solid var(--border-primary, #45475a);
  color: var(--text-secondary, #a6adc8);
}

.btn-discard:hover {
  background: rgba(243, 139, 168, 0.15);
  border-color: #f38ba8;
  color: #f38ba8;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-primary, #45475a);
  color: var(--text-secondary, #a6adc8);
}

.btn-cancel:hover {
  background: var(--bg-tertiary, #313244);
  border-color: var(--border-secondary, #585b70);
}

.btn-save {
  background: linear-gradient(135deg, #89b4fa, #74c7ec);
  border: none;
  color: #1e1e2e;
}

.btn-save:hover {
  background: linear-gradient(135deg, #74c7ec, #89dceb);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(137, 180, 250, 0.3);
}

/* 모달 트랜지션 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .unsaved-modal,
.modal-leave-active .unsaved-modal {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .unsaved-modal,
.modal-leave-to .unsaved-modal {
  transform: scale(0.95);
  opacity: 0;
}
</style>
