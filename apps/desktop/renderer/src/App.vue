<template>
  <div class="app-container" :class="{ 'is-resizing': isResizing }">
    <AppSidebar
      v-if="currentView !== 'settings'"
      :collapsed="sidebarCollapsed"
      :active-file="activeFile"
      :dirty-files="dirtyFiles"
      @toggle-collapse="handleToggleCollapse"
      @select-file="handleSelectFile"
      @file-deleted="handleFileDeleted"
      @file-created="handleFileCreated"
      @file-restored="handleFileRestored"
      @sidebar-width-change="handleSidebarWidthChange"
    />

    <!-- 저장 확인 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showUnsavedModal" class="unsaved-modal-overlay" @click.self="cancelFileSwitch">
          <div class="unsaved-modal">
            <div class="unsaved-modal-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <h3>저장되지 않은 변경사항</h3>
            <p>현재 문서에 저장되지 않은 변경사항이 있습니다.<br/>저장하시겠습니까?</p>
            <div class="unsaved-modal-actions">
              <button class="btn-discard" @click="discardAndSwitch">
                저장 안 함
              </button>
              <button class="btn-cancel" @click="cancelFileSwitch">
                취소
              </button>
              <button class="btn-save" @click="saveAndSwitch">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                  <polyline points="17 21 17 13 7 13 7 21"/>
                  <polyline points="7 3 7 8 15 8"/>
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
        @open-settings="currentView = 'settings'"
      />

      <div class="content-area">
        <EditorView
          ref="editorViewRef"
          v-show="currentView === 'editor'"
          :active-file="activeFile"
          @dirty-change="isFileDirty = $event"
          @dirty-files-change="handleDirtyFilesChange"
        />

        <DashboardView
          ref="dashboardViewRef"
          v-show="currentView === 'dashboard'"
          :has-vault="!!vaultPath"
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
import { computed, nextTick, onMounted, ref } from 'vue';
import { AppSidebar, MainHeader, EditorView, DashboardView, SettingsView } from './components';
import { useVault, useHealth, useFonts } from './composables';
import type { ViewType } from './types';

const sidebarCollapsed = ref(false);
const currentView = ref<ViewType>('editor');
const activeFile = ref<string | null>(null);
const previousView = ref<ViewType>('editor');
const isFileDirty = ref(false);
const isResizing = ref(false);
const dirtyFiles = ref<string[]>([]);

// 저장 확인 모달 관련
const showUnsavedModal = ref(false);
const pendingFile = ref<string | null>(null);
const editorViewRef = ref<InstanceType<typeof EditorView> | null>(null);
const dashboardViewRef = ref<InstanceType<typeof DashboardView> | null>(null);

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

const { vaultPath, initVault } = useVault();
const { checkHealth } = useHealth();
const { initFonts } = useFonts();

const vaultName = computed(() => {
  return vaultPath.value?.split(/[/\\]/).pop() ?? null;
});

function handleSelectFile(file: string) {
  // 같은 파일이면 무시
  if (file === activeFile.value) return;
  
  // 바로 파일 전환 (저장하지 않은 변경사항은 캐시에 유지됨)
  activeFile.value = file;
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

function handleBackFromSettings() {
  // 설정에서 돌아올 때 이전 뷰로 복원
  currentView.value = previousView.value;
}

// 설정 페이지로 이동 시 이전 뷰 저장
import { watch } from 'vue';
watch(currentView, (newView, oldView) => {
  if (newView === 'settings' && oldView !== 'settings') {
    previousView.value = oldView;
  }
});

onMounted(async () => {
  checkHealth();
  initFonts();
  // 앱 시작 시 기본 vault(data 폴더) 자동 로드
  await initVault();
});
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
  background: var(--bg-primary);
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

/* 저장 확인 모달 */
.unsaved-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.65);
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
