<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="logo-text">CueNote</span>
      </div>
      <button class="icon-btn" @click="$emit('toggle-collapse')" title="Toggle Sidebar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 3H3C1.89543 3 1 3.89543 1 5V19C1 20.1046 1.89543 21 3 21H21C22.1046 21 23 20.1046 23 19V5C23 3.89543 22.1046 3 21 3Z"/>
          <path d="M9 3V21"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <!-- Vault Section -->
      <div class="sidebar-section">
        <div class="section-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <span>Vault</span>
        </div>
        
        <button class="vault-btn" @click="openVault">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>{{ vaultPath ? 'Change Vault' : 'Open Vault' }}</span>
        </button>

        <div v-if="vaultPath" class="vault-info">
          <div class="vault-path" :title="vaultPath">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4M12 8h.01"/>
            </svg>
            <span>{{ vaultPath.split(/[/\\]/).pop() }}</span>
          </div>
          <div class="vault-stats" v-if="todoCount !== null">
            <div class="stat">
              <span class="stat-value">{{ vaultFiles.length }}</span>
              <span class="stat-label">files</span>
            </div>
            <div class="stat">
              <span class="stat-value">{{ todoCount }}</span>
              <span class="stat-label">todos</span>
            </div>
          </div>
        </div>

        <p v-if="vaultError" class="error-msg">{{ vaultError }}</p>
      </div>

      <!-- Files List -->
      <div class="sidebar-section files-section" v-if="vaultFiles.length > 0">
        <div class="section-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <span>Files</span>
          <span class="badge">{{ vaultFiles.length }}</span>
        </div>
        
        <ul class="file-list">
          <li
            v-for="file in vaultFiles"
            :key="file"
            class="file-item"
            :class="{ active: file === activeFile }"
            @click="$emit('select-file', file)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <span class="file-name">{{ getFileName(file) }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Status Bar -->
    <div class="sidebar-footer">
      <div class="status-indicator" :class="coreStatus === 'ok' ? 'online' : 'offline'">
        <span class="status-dot"></span>
        <span>{{ coreStatus === 'ok' ? 'Connected' : coreStatus }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useVault, useHealth } from '../composables';

defineProps<{
  collapsed: boolean;
  activeFile: string | null;
}>();

defineEmits<{
  'toggle-collapse': [];
  'select-file': [file: string];
}>();

const { vaultPath, vaultFiles, vaultError, todoCount, openVault } = useVault();
const { coreStatus } = useHealth();

function getFileName(path: string): string {
  return path.split(/[/\\]/).pop() || path;
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
  transition: width var(--transition-smooth), transform var(--transition-smooth);
  position: relative;
  z-index: 10;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar.collapsed .logo-text,
.sidebar.collapsed .section-header span,
.sidebar.collapsed .vault-btn span,
.sidebar.collapsed .vault-info,
.sidebar.collapsed .file-name,
.sidebar.collapsed .badge,
.sidebar.collapsed .status-indicator span:last-child {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
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
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: var(--radius-sm);
  color: white;
  box-shadow: var(--shadow-glow);
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--text-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: opacity var(--transition-fast), width var(--transition-fast);
  white-space: nowrap;
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.sidebar-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.badge {
  margin-left: auto;
  background: var(--bg-active);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  color: var(--text-secondary);
}

.vault-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--bg-hover);
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.vault-btn:hover {
  background: var(--bg-active);
  border-color: var(--accent-primary);
  color: var(--accent-secondary);
}

.vault-info {
  margin-top: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  transition: opacity var(--transition-fast);
}

.vault-path {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.vault-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--accent-secondary);
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.files-section {
  flex: 1;
}

.file-list {
  list-style: none;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
}

.file-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.file-item.active {
  background: var(--accent-primary);
  color: white;
  box-shadow: var(--shadow-glow);
}

.file-item.active svg {
  color: white;
}

.file-name {
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: opacity var(--transition-fast), width var(--transition-fast);
}

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
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: background var(--transition-fast);
}

.status-indicator.online .status-dot {
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
}

.status-indicator.offline .status-dot {
  background: var(--error);
}

.error-msg {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-sm);
  color: var(--error);
  font-size: 13px;
  margin-top: 12px;
}
</style>


