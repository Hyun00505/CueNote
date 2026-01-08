<template>
  <div class="app-container">
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :active-file="activeFile"
      @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
      @select-file="handleSelectFile"
    />

    <main class="main-content">
      <MainHeader
        :active-file="activeFile"
        :vault-name="vaultName"
        :current-view="currentView"
        @change-view="currentView = $event"
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { AppSidebar, MainHeader, EditorView, DashboardView } from './components';
import { useVault, useHealth } from './composables';
import type { ViewType } from './types';

const sidebarCollapsed = ref(false);
const currentView = ref<ViewType>('editor');
const activeFile = ref<string | null>(null);

const { vaultPath, initVault } = useVault();
const { checkHealth } = useHealth();

const vaultName = computed(() => {
  return vaultPath.value?.split(/[/\\]/).pop() ?? null;
});

function handleSelectFile(file: string) {
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
