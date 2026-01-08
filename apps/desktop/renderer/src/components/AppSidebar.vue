<template>
  <aside class="sidebar" :class="{ collapsed }">
    <!-- Decorative Gradient Orb -->
    <div class="sidebar-glow"></div>

    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <defs>
              <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#818cf8"/>
                <stop offset="100%" style="stop-color:#c084fc"/>
              </linearGradient>
            </defs>
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="logo-text">CueNote</span>
      </div>
      <button class="icon-btn" @click="$emit('toggle-collapse')" title="Toggle Sidebar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 3H3C1.89543 3 1 3.89543 1 5V19C1 20.1046 1.89543 21 3 21H21C22.1046 21 23 20.1046 23 19V5C23 3.89543 22.1046 3 21 3Z"/>
          <path d="M9 3V21"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <!-- Vault Section -->
      <div class="sidebar-section">
        <div class="section-header">
          <div class="section-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <span>Vault</span>
        </div>

        <button class="vault-btn" @click="openVault">
          <div class="vault-btn-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
          </div>
          <span>{{ vaultPath ? 'Change Vault' : 'Open Vault' }}</span>
          <svg class="vault-btn-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </button>

        <div v-if="vaultPath" class="vault-info">
          <div class="vault-path" :title="vaultPath">
            <div class="vault-path-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <span>{{ vaultPath.split(/[/\\]/).pop() }}</span>
          </div>
          <div class="vault-stats" v-if="todoCount !== null">
            <div class="stat">
              <span class="stat-value">{{ vaultFiles.length }}</span>
              <span class="stat-label">files</span>
            </div>
            <div class="stat-divider"></div>
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
          <div class="section-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <span>Files</span>
          <span class="badge">{{ vaultFiles.length }}</span>
        </div>

        <ul class="file-list">
          <li
            v-for="(file, index) in vaultFiles"
            :key="file"
            class="file-item"
            :class="{ active: file === activeFile }"
            :style="{ '--delay': `${index * 30}ms` }"
            @click="$emit('select-file', file)"
          >
            <div class="file-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
            </div>
            <span class="file-name">{{ getFileName(file) }}</span>
            <div class="file-hover-indicator"></div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Status Bar -->
    <div class="sidebar-footer">
      <div class="status-indicator" :class="coreStatus === 'ok' ? 'online' : 'offline'">
        <span class="status-dot"></span>
        <span class="status-text">{{ coreStatus === 'ok' ? 'Connected' : coreStatus }}</span>
        <span class="status-ping" v-if="coreStatus === 'ok'"></span>
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
  transition: width var(--transition-smooth);
  position: relative;
  z-index: 10;
  overflow: hidden;
}

.sidebar-glow {
  position: absolute;
  top: -100px;
  left: -100px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
  opacity: 0.4;
  pointer-events: none;
  filter: blur(60px);
  animation: float 8s ease-in-out infinite;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed);
}

.sidebar.collapsed .logo-text,
.sidebar.collapsed .section-header span,
.sidebar.collapsed .vault-btn span,
.sidebar.collapsed .vault-btn-arrow,
.sidebar.collapsed .vault-info,
.sidebar.collapsed .file-name,
.sidebar.collapsed .badge,
.sidebar.collapsed .status-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
  padding: 16px 12px;
}

.sidebar.collapsed .vault-btn {
  justify-content: center;
  padding: 12px;
}

.sidebar.collapsed .file-item {
  justify-content: center;
  padding: 10px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--gradient-surface);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--accent-secondary);
  box-shadow: var(--shadow-sm), var(--shadow-inset);
  transition: all var(--transition-smooth);
}

.logo-icon:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-glow);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-tertiary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: all var(--transition-smooth);
  white-space: nowrap;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
  transform: scale(1.05);
}

.icon-btn:active {
  transform: scale(0.95);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.sidebar-section {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  margin-bottom: 14px;
  padding-left: 4px;
}

.section-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border-radius: var(--radius-xs);
  color: var(--text-muted);
}

.badge {
  margin-left: auto;
  background: var(--gradient-primary);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 10px;
  font-weight: 600;
  color: white;
  box-shadow: var(--shadow-xs);
}

.vault-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--glass-bg);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-smooth);
  position: relative;
  overflow: hidden;
}

.vault-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.vault-btn:hover {
  border-color: var(--accent-primary);
  color: var(--text-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.vault-btn:hover::before {
  opacity: 0.1;
}

.vault-btn:active {
  transform: translateY(0);
}

.vault-btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
  color: var(--accent-secondary);
  transition: all var(--transition-fast);
  position: relative;
  z-index: 1;
}

.vault-btn:hover .vault-btn-icon {
  background: var(--accent-primary);
  color: white;
}

.vault-btn span {
  position: relative;
  z-index: 1;
}

.vault-btn-arrow {
  margin-left: auto;
  opacity: 0.5;
  transition: all var(--transition-fast);
  position: relative;
  z-index: 1;
}

.vault-btn:hover .vault-btn-arrow {
  opacity: 1;
  transform: translateX(4px);
}

.vault-info {
  margin-top: 16px;
  padding: 16px;
  background: var(--glass-bg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  transition: all var(--transition-smooth);
  animation: slideUp 0.3s ease;
}

.vault-path {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.vault-path-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-glow);
  border-radius: var(--radius-xs);
  color: var(--accent-secondary);
}

.vault-stats {
  display: flex;
  align-items: center;
  gap: 0;
}

.stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.stat-label {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--border-subtle);
}

.files-section {
  flex: 1;
}

.file-list {
  list-style: none;
  max-height: calc(100vh - 420px);
  overflow-y: auto;
  padding: 4px;
  margin: -4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 4px;
  position: relative;
  animation: slideUp 0.3s ease backwards;
  animation-delay: var(--delay);
}

.file-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.file-item:hover .file-icon {
  color: var(--accent-secondary);
  transform: scale(1.1);
}

.file-item.active {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow-md), 0 0 20px var(--accent-glow);
}

.file-item.active .file-icon {
  color: white;
}

.file-icon {
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.file-name {
  font-size: 13px;
  font-weight: 450;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all var(--transition-smooth);
}

.file-hover-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: var(--gradient-primary);
  border-radius: var(--radius-full);
  transition: height var(--transition-fast);
}

.file-item:hover .file-hover-indicator {
  height: 60%;
}

.file-item.active .file-hover-indicator {
  display: none;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
  background: var(--gradient-surface);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  padding: 10px 14px;
  background: var(--glass-bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.status-indicator.online .status-dot {
  background: var(--success);
  box-shadow: 0 0 12px var(--success-glow);
  animation: pulse 2s ease-in-out infinite;
}

.status-indicator.offline .status-dot {
  background: var(--error);
  box-shadow: 0 0 8px var(--error-glow);
}

.status-text {
  transition: all var(--transition-smooth);
}

.status-ping {
  margin-left: auto;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
  animation: pulse 1.5s ease-in-out infinite;
}

.error-msg {
  padding: 14px 16px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  border-radius: var(--radius-md);
  color: var(--error);
  font-size: 13px;
  margin-top: 16px;
  animation: slideUp 0.3s ease;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(10px, 10px); }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>


