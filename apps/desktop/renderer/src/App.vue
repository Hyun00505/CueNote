<template>
  <div class="app-container">
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :active-file="activeFile"
      @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
      @select-file="handleSelectFile"
      @file-deleted="handleFileDeleted"
      @file-created="handleFileCreated"
      @file-restored="handleFileRestored"
    />

    <main class="main-content">
      <MainHeader
        :active-file="activeFile"
        :vault-name="vaultName"
        :current-view="currentView"
        @change-view="currentView = $event"
        @open-settings="showSettings = true"
      />

      <div class="content-area">
        <EditorView
          v-show="currentView === 'editor'"
          :active-file="activeFile"
        />

        <DashboardView
          v-show="currentView === 'dashboard'"
          :has-vault="!!vaultPath"
        />
      </div>
    </main>

    <!-- Settings Modal -->
    <SettingsModal
      :is-open="showSettings"
      @close="showSettings = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { AppSidebar, MainHeader, EditorView, DashboardView, SettingsModal } from './components';
import { useVault, useHealth } from './composables';
import type { ViewType } from './types';

const sidebarCollapsed = ref(false);
const currentView = ref<ViewType>('editor');
const activeFile = ref<string | null>(null);
const showSettings = ref(false);

const { vaultPath, initVault } = useVault();
const { checkHealth } = useHealth();

const vaultName = computed(() => {
  return vaultPath.value?.split(/[/\\]/).pop() ?? null;
});

function handleSelectFile(file: string) {
  activeFile.value = file;
  currentView.value = 'editor';
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

onMounted(async () => {
  checkHealth();
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
</style>
