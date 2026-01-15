<template>
  <div class="sidebar-section environment-section">
    <div class="env-header">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6M4.22 19.78l4.24-4.24M15.54 8.46l4.24-4.24"/>
      </svg>
      <span class="env-label">환경</span>
      <div class="env-actions">
        <button class="env-add-btn" @click="emit('open-add-modal')" title="로컬 환경 추가">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
            </svg>
        </button>
      </div>
    </div>
    
    <!-- 환경 선택기 -->
    <div class="env-selector" @click="toggleDropdown">
      <div class="env-current" :class="{ 'github-mode': currentEnvironment?.type === 'github' }">
        <!-- GitHub 모드 -->
        <template v-if="currentEnvironment?.type === 'github'">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="env-github-icon">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
          </svg>
          <span class="env-name">{{ currentEnvironment.name }}</span>
          <span class="env-github-badge">GitHub</span>
        </template>
        <!-- 로컬 모드 -->
        <template v-else>
          <span class="env-name">{{ currentEnvironment?.name || '환경 선택' }}</span>
        </template>
        <svg :class="{ rotated: dropdownOpen }" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="env-chevron">
          <path d="M6 9l6 6 6-6"/>
        </svg>
      </div>
    </div>
    
    <!-- 환경 드롭다운 -->
    <div v-if="dropdownOpen" class="env-dropdown">
      
      <!-- GitHub 환경들 -->
      <div v-if="githubEnvironments.length > 0" class="env-dropdown-section">
        <div class="env-dropdown-section-title">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
          </svg>
          GitHub Repos
        </div>
        <div 
          v-for="env in githubEnvironments"
          :key="env.id"
          class="env-item github-item"
          :class="{ active: env.id === currentId }"
          @click="selectEnv(env.id)"
        >
          <div class="env-item-info">
            <span class="env-item-name">{{ env.name }}</span>
            <span class="env-item-path">{{ env.github?.owner }}/{{ env.github?.repo }}</span>
          </div>
          <button 
            class="env-remove-btn" 
            @click.stop="emit('remove-environment', env.id)"
            title="연결 해제"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 로컬 환경들 -->
      <div v-if="localEnvironments.length > 0" class="env-dropdown-section">
        <div class="env-dropdown-section-title">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          로컬 폴더
        </div>
        <div 
          v-for="env in localEnvironments" 
          :key="env.id" 
          class="env-item"
          :class="{ active: env.id === currentId, invalid: !env.exists }"
          @click="selectEnv(env.id)"
        >
          <div class="env-item-info">
            <span class="env-item-name">{{ env.name }}</span>
            <span class="env-item-path">{{ truncatePath(env.path) }}</span>
          </div>
          <button 
            v-if="environments.length > 1" 
            class="env-remove-btn" 
            @click.stop="emit('remove-environment', env.id)"
            title="환경 제거"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

       <div v-if="environments.length === 0" class="env-empty">
        환경이 없습니다.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Environment } from '../../composables/useEnvironment';

const props = defineProps<{
  environments: Environment[];
  currentId: string | null;
  currentEnvironment: Environment | null;
}>();

const emit = defineEmits<{
  'open-add-modal': [];
  'select-environment': [id: string];
  'remove-environment': [id: string];
}>();

const dropdownOpen = ref(false);

const githubEnvironments = computed(() => 
  props.environments.filter(env => env.type === 'github')
);

const localEnvironments = computed(() => 
  props.environments.filter(env => env.type !== 'github')
);

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}

function selectEnv(id: string) {
  emit('select-environment', id);
  dropdownOpen.value = false;
}

function truncatePath(path: string): string {
  if (path.length <= 30) return path;
  const parts = path.split(/[/\\]/);
  if (parts.length <= 3) return path;
  return `...${parts.slice(-2).join('/')}`;
}

// 외부에서 드롭다운 닫기
function closeDropdown() {
  dropdownOpen.value = false;
}

defineExpose({ closeDropdown });
</script>

<style scoped>
.environment-section {
  padding: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.env-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--text-muted);
}

.env-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

.env-add-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.env-add-btn:hover {
  background: var(--bg-hover);
  color: var(--accent);
}

.env-selector {
  cursor: pointer;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  transition: all 0.15s ease;
}

.env-selector:hover {
  border-color: var(--accent);
}

.env-current {
  display: flex;
  align-items: center;
  gap: 8px;
}

.env-current.github-mode {
  gap: 6px;
}

.env-github-icon {
  color: var(--accent);
  flex-shrink: 0;
}

.env-github-badge {
  font-size: 9px;
  padding: 2px 5px;
  background: var(--bg-active);
  color: var(--text-primary);
  border-radius: 4px;
  font-weight: 500;
  flex-shrink: 0;
}

.env-chevron {
  margin-left: auto;
  flex-shrink: 0;
}

.env-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.env-current svg {
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.env-current svg.rotated {
  transform: rotate(180deg);
}

.env-dropdown {
  margin-top: 4px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 350px;
  overflow-y: auto;
}

.env-dropdown-section {
  padding: 6px 0;
}

.env-dropdown-section + .env-dropdown-section {
  border-top: 1px solid var(--border-subtle);
}

.env-dropdown-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.env-dropdown-section-title svg {
  opacity: 0.6;
}

.env-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.env-item:hover {
  background: var(--bg-hover);
}

.env-item.github-item {
  background: var(--bg-hover);
}

.env-item.github-item:hover {
  background: var(--bg-active);
}

.env-item.active {
  background: var(--bg-active);
}

.env-item.invalid {
  opacity: 0.5;
}

.env-item-info {
  flex: 1;
  min-width: 0;
}

.env-item-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.env-item-path {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 2px;
}

.env-remove-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s ease;
}

.env-item:hover .env-remove-btn {
  opacity: 1;
}

.env-remove-btn:hover {
  background: var(--error-glow);
  color: var(--error);
}
</style>
