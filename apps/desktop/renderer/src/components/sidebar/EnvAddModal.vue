<template>
  <Teleport to="body">
    <div v-if="visible" class="env-modal-overlay" @click.self="emit('close')">
      <div class="env-modal env-modal-large">
        <div class="env-modal-header">
          <h3>{{ t('env.addNew') }}</h3>
          <button class="env-modal-close" @click="emit('close')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- 탭 선택 -->
        <div class="env-modal-tabs">
          <button 
            class="env-tab" 
            :class="{ active: currentTab === 'local' }"
            @click="currentTab = 'local'"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            로컬 폴더
          </button>
          <button 
            class="env-tab" 
            :class="{ active: currentTab === 'github' }"
            @click="currentTab = 'github'; handleGitHubTabOpen()"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
            </svg>
            GitHub
            <span v-if="isGitHubLoggedIn" class="tab-badge connected">연결됨</span>
          </button>
        </div>

        <!-- 로컬 폴더 탭 -->
        <div v-if="currentTab === 'local'" class="env-modal-body">
          <div class="env-form-group">
            <label>{{ t('env.name') }}</label>
            <input 
              v-model="newEnvName" 
              type="text" 
              :placeholder="t('env.namePlaceholder')"
              @keydown.enter="handleAddEnvironment"
            />
          </div>
          <div class="env-form-group">
            <label>{{ t('env.folderPath') }}</label>
            <div class="env-path-input">
              <input 
                v-model="newEnvPath" 
                type="text" 
                :placeholder="t('env.folderPlaceholder')"
                readonly
              />
              <button class="env-browse-btn" @click="browseFolder">{{ t('env.browse') }}</button>
            </div>
          </div>
          <p v-if="error" class="env-error">{{ error }}</p>
        </div>

        <!-- GitHub 탭 -->
        <div v-else-if="currentTab === 'github'" class="env-modal-body github-tab-body">
          <!-- GitHub 로그인 상태 -->
          <div v-if="isGitHubLoggedIn" class="github-logged-section">
            <div class="github-user-bar">
              <img :src="githubUser?.avatar_url" :alt="githubUser?.login" class="github-avatar-sm" />
              <span class="github-username-sm">{{ githubUser?.name || githubUser?.login }}</span>
              <button class="github-logout-btn-sm" @click="emit('github-logout')" title="로그아웃">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                  <polyline points="16 17 21 12 16 7"/>
                  <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
              </button>
            </div>

            <!-- 리포지토리 목록 -->
            <div class="github-repos-section">
              <div class="github-repos-header">
                <span>리포지토리 선택</span>
                <button class="github-create-repo-btn" @click="emit('open-create-repo')">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 5v14M5 12h14"/>
                  </svg>
                  새 리포지토리
                </button>
              </div>
              
              <div v-if="githubLoading" class="github-repos-loading">
                <span class="loading-spinner-sm"></span>
                <span>리포지토리 목록을 불러오는 중...</span>
              </div>
              <div v-else-if="githubRepos.length === 0" class="github-repos-empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                <span>리포지토리가 없습니다</span>
                <button class="github-create-repo-btn primary" @click="emit('open-create-repo')">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 5v14M5 12h14"/>
                  </svg>
                  첫 리포지토리 만들기
                </button>
              </div>
              <div v-else class="github-repos-list-env">
                <button
                  v-for="repo in githubRepos"
                  :key="repo.id"
                  class="github-repo-item-env"
                  :class="{ selected: selectedRepoId === repo.id }"
                  @click="selectedRepoId = repo.id"
                >
                  <div class="repo-item-icon-env">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                  </div>
                  <div class="repo-item-info-env">
                    <div class="repo-item-name-env">
                      {{ repo.name }}
                      <span v-if="repo.private" class="repo-private-badge-env">Private</span>
                    </div>
                    <span v-if="repo.description" class="repo-item-desc-env">{{ repo.description }}</span>
                  </div>
                  <div v-if="selectedRepoId === repo.id" class="repo-selected-check">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- GitHub 로그인 폼 -->
          <div v-else class="github-login-section">
            <div class="github-login-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
              </svg>
            </div>
            <h4>GitHub에 연결하기</h4>
            <p class="github-login-desc">Personal Access Token을 입력하여 GitHub 리포지토리에 연결하세요.</p>
            
            <div class="github-token-input-wrapper">
              <input
                type="password"
                v-model="githubTokenInput"
                placeholder="GitHub Personal Access Token"
                class="github-token-input"
                @keydown.enter="handleGitHubLogin"
              />
              <button 
                class="github-login-btn"
                @click="handleGitHubLogin"
                :disabled="githubValidating || !githubTokenInput.trim()"
              >
                <span v-if="githubValidating" class="loading-spinner-sm"></span>
                <span v-else>연결</span>
              </button>
            </div>
            
            <div v-if="githubError" class="github-error">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              {{ githubError }}
            </div>
            
            <button type="button" class="github-token-link" @click="openGitHubTokenPage">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
              Personal Access Token 발급받기
            </button>
            
            <p class="github-token-hint">
              GitHub에서 "repo" 권한이 포함된 Personal Access Token을 발급받아 입력해주세요.
            </p>
          </div>
        </div>

        <!-- 푸터 -->
        <div class="env-modal-footer">
          <button class="env-modal-btn cancel" @click="emit('close')">{{ t('common.cancel') }}</button>
          <button 
            v-if="currentTab === 'local'"
            class="env-modal-btn primary" 
            @click="handleAddEnvironment" 
            :disabled="!newEnvName || !newEnvPath"
          >
            {{ t('common.add') }}
          </button>
          <button 
            v-else-if="currentTab === 'github' && isGitHubLoggedIn"
            class="env-modal-btn primary" 
            @click="handleAddGitHubEnvironment" 
            :disabled="!selectedRepoId || isCloning"
          >
            <span v-if="isCloning" class="loading-spinner-sm"></span>
            <span v-else>{{ t('common.add') }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from '../../composables';
import type { GitHubUser, GitHubRepo } from '../../composables/useGitHub';

const props = defineProps<{
  visible: boolean;
  error: string | null;
  isGitHubLoggedIn: boolean;
  githubUser: GitHubUser | null;
  githubRepos: GitHubRepo[];
  githubLoading: boolean;
  githubError: string | null;
  githubValidating: boolean;
  isCloning?: boolean; // Add isCloning prop
}>();

const emit = defineEmits<{
  'close': [];
  'add-local': [name: string, path: string];
  'add-github': [repoId: number];
  'github-login': [token: string];
  'github-logout': [];
  'open-create-repo': [];
  'fetch-repos': [];
}>();

const { t } = useI18n();

const currentTab = ref<'local' | 'github'>('local');
const newEnvName = ref('');
const newEnvPath = ref('');
const githubTokenInput = ref('');
const selectedRepoId = ref<number | null>(null);

// 모달이 열릴 때 초기화
watch(() => props.visible, (newVal) => {
  if (newVal) {
    currentTab.value = 'local';
    newEnvName.value = '';
    newEnvPath.value = '';
    githubTokenInput.value = '';
    selectedRepoId.value = null;
  }
});

function handleGitHubTabOpen() {
  if (props.isGitHubLoggedIn) {
    emit('fetch-repos');
  }
}

function handleGitHubLogin() {
  if (!githubTokenInput.value.trim()) return;
  emit('github-login', githubTokenInput.value.trim());
  githubTokenInput.value = '';
}

function openGitHubTokenPage() {
  const url = 'https://github.com/settings/tokens/new?description=CueNote&scopes=repo';
  if (window.cuenote?.openExternal) {
    window.cuenote.openExternal(url);
  } else {
    window.open(url, '_blank');
  }
}

async function browseFolder() {
  if (window.cuenote?.selectVault) {
    const result = await window.cuenote.selectVault();
    if (result) {
      newEnvPath.value = result;
    }
  } else {
    const path = prompt('폴더 경로를 입력하세요:');
    if (path) {
      newEnvPath.value = path;
    }
  }
}

function handleAddEnvironment() {
  if (!newEnvName.value || !newEnvPath.value) return;
  emit('add-local', newEnvName.value, newEnvPath.value);
}

function handleAddGitHubEnvironment() {
  if (!selectedRepoId.value) return;
  emit('add-github', selectedRepoId.value);
}
</script>

<style scoped>
.env-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.env-modal {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideUp 0.2s ease;
}

.env-modal.env-modal-large {
  width: 520px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.env-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.env-modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.env-modal-close {
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

.env-modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 탭 */
.env-modal-tabs {
  display: flex;
  gap: 0;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.env-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.env-tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.env-tab.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
}

.env-tab svg {
  opacity: 0.7;
}

.env-tab.active svg {
  opacity: 1;
}

.tab-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.tab-badge.connected {
  background: var(--success-glow);
  color: var(--success);
}

.env-modal-body {
  padding: 24px;
}

.github-tab-body {
  min-height: 300px;
  max-height: 400px;
  overflow-y: auto;
}

/* 로컬 폴더 폼 */
.env-form-group {
  margin-bottom: 16px;
}

.env-form-group:last-child {
  margin-bottom: 0;
}

.env-form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.env-form-group input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.15s ease;
}

.env-form-group input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.env-path-input {
  display: flex;
  gap: 8px;
}

.env-path-input input {
  flex: 1;
}

.env-browse-btn {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.env-browse-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.env-error {
  margin-top: 12px;
  padding: 10px 12px;
  background: var(--error-glow);
  border: 1px solid var(--error-glow);
  border-radius: 6px;
  color: var(--error);
  font-size: 13px;
}

/* GitHub 로그인 섹션 */
.github-logged-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.github-user-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.github-avatar-sm {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.github-username-sm {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.github-logout-btn-sm {
  margin-left: auto;
  padding: 6px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.github-logout-btn-sm:hover {
  background: var(--error-glow);
  color: var(--error);
}

.github-repos-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.github-repos-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.github-create-repo-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.github-create-repo-btn:hover {
  background: var(--accent-glow);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.github-create-repo-btn.primary {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: white;
  font-size: 12px;
  padding: 8px 12px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.github-create-repo-btn.primary:hover {
  background: var(--accent-hover);
  box-shadow: 0 4px 12px var(--accent-glow);
}

.github-repos-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  color: var(--text-muted);
  font-size: 13px;
}

.github-repos-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 20px;
  color: var(--text-muted);
  text-align: center;
}

.github-repos-empty svg {
  opacity: 0.3;
}

.github-repos-list-env {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 250px;
  overflow-y: auto;
}

.github-repo-item-env {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-hover);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.github-repo-item-env:hover {
  background: var(--bg-hover);
  border-color: var(--border-hover);
}

.github-repo-item-env.selected {
  background: var(--bg-active);
  border-color: var(--accent-primary);
}

.repo-item-icon-env {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--bg-primary);
  border-radius: 6px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.repo-item-info-env {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.repo-item-name-env {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.repo-private-badge-env {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--bg-hover);
  border-radius: 4px;
  color: var(--text-muted);
}

.repo-item-desc-env {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.repo-selected-check {
  color: var(--accent-primary);
}

/* GitHub 로그인 섹션 */
.github-login-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 16px;
  text-align: center;
}

.github-login-icon {
  color: var(--text-muted);
  opacity: 0.5;
}

.github-login-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.github-login-desc {
  font-size: 13px;
  color: var(--text-secondary);
  max-width: 280px;
  margin: 0;
}

.github-token-input-wrapper {
  display: flex;
  gap: 8px;
  width: 100%;
  max-width: 320px;
}

.github-token-input {
  flex: 1;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s ease;
}

.github-token-input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.github-token-input::placeholder {
  color: var(--text-muted);
}

.github-login-btn {
  padding: 10px 16px;
  background: var(--accent-primary);
  border: 1px solid var(--accent-primary);
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 60px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.github-login-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  box-shadow: 0 4px 12px var(--accent-glow);
}

.github-login-btn:disabled {
  background: var(--bg-disabled);
  border-color: var(--bg-disabled);
  color: white;
  opacity: 0.7;
  cursor: not-allowed;
}

.github-error {
  margin-top: 12px;
  color: var(--error);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.github-token-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--accent-primary);
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.github-token-link:hover {
  text-decoration: underline;
  color: var(--accent-hover);
}

.github-token-hint {
  font-size: 11px;
  color: var(--text-muted);
  max-width: 320px;
  margin: 0;
}

.loading-spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-default);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 푸터 */
.env-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.env-modal-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.env-modal-btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
}

.env-modal-btn.cancel:hover {
  background: var(--bg-hover);
  border-color: var(--text-muted);
}

.env-modal-btn.primary {
  background: var(--accent-primary);
  color: white;
  border: none;
}

.env-modal-btn.primary:hover:not(:disabled) {
  opacity: 0.9;
  transform: none;
  box-shadow: none;
}

.env-modal-btn.primary:disabled {
  background: var(--text-muted);
  border-color: var(--text-muted);
  color: var(--bg-primary);
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
