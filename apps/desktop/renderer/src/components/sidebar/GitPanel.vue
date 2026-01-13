<template>
  <div class="git-panel" v-if="isVisible">
    <div class="panel-header" @click="toggleExpanded">
      <div class="header-left">
        <svg class="expand-icon" :class="{ expanded: isExpanded }" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 6 15 12 9 18" />
        </svg>
        <svg class="git-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
        <span class="panel-title">Source Control</span>
      </div>
      <div class="header-right">
        <span v-if="changesCount > 0" class="badge">{{ changesCount }}</span>
        <button class="action-btn" @click.stop="handlePull" :disabled="isPulling" title="Pull">
          <svg :class="{ spinning: isPulling }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="panel-content" v-show="isExpanded">
      <!-- Git이 설치되지 않은 경우 -->
      <div class="warning-message" v-if="!gitInstalled">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <div>
          <p>Git이 설치되어 있지 않습니다</p>
          <span>Git을 설치한 후 앱을 재시작해주세요</span>
        </div>
      </div>

      <!-- 클론되지 않은 경우 -->
      <div class="clone-prompt" v-else-if="!isCloned">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <p>리포지토리를 클론해주세요</p>
        <button class="clone-btn" @click="handleClone" :disabled="isCloning">
          <svg v-if="isCloning" class="spinning" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
          </svg>
          <span>{{ isCloning ? '클론 중...' : '클론하기' }}</span>
        </button>
      </div>

      <!-- 클론된 경우 -->
      <template v-else>
        <!-- 커밋 메시지 입력 -->
        <div class="commit-section">
          <textarea
            v-model="commitMessage"
            class="commit-input"
            placeholder="커밋 메시지를 입력하세요..."
            rows="3"
            :disabled="isPushing || changesCount === 0"
          ></textarea>
          
          <div class="commit-actions">
            <button 
              class="commit-btn"
              :disabled="!canCommit"
              @click="handlePush"
            >
              <svg v-if="isPushing" class="spinning" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
              </svg>
              {{ isPushing ? '푸시 중...' : 'Commit & Push' }}
            </button>
          </div>
        </div>

        <!-- 변경된 파일 목록 -->
        <div class="changes-section" v-if="changesCount > 0">
          <div class="section-header">
            <span class="section-title">Changes</span>
            <span class="changes-count">{{ changesCount }}</span>
          </div>
          <div class="file-list">
            <div 
              v-for="change in gitChanges" 
              :key="change.path"
              class="changed-file"
              :title="change.path"
            >
              <span class="status-dot" :class="getStatusClass(change.status)"></span>
              <span class="file-name">{{ getFileName(change.path) }}</span>
            </div>
          </div>
        </div>

        <!-- 변경사항 없음 -->
        <div class="empty-state" v-else>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <p>변경사항이 없습니다</p>
          <span class="hint">파일을 수정하면 여기에 표시됩니다</span>
        </div>
      </template>

      <!-- 에러 메시지 -->
      <div class="error-message" v-if="error">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useGitHub } from '../../composables/useGitHub';

const props = defineProps<{
  isGitHubMode: boolean;
}>();

const emit = defineEmits<{
  'commit-success': [];
  'files-changed': [];
}>();

const {
  gitInstalled,
  isCloned,
  isCloning,
  isPulling,
  isPushing,
  gitChanges,
  hasChanges,
  error,
  cloneOrPull,
  pull,
  push,
  checkGitStatus
} = useGitHub();

const isExpanded = ref(true);
const commitMessage = ref('');

const isVisible = computed(() => props.isGitHubMode);
const changesCount = computed(() => gitChanges.value.length);
const canCommit = computed(() => 
  !isPushing.value && 
  changesCount.value > 0 && 
  commitMessage.value.trim().length > 0
);

function toggleExpanded() {
  isExpanded.value = !isExpanded.value;
}

function getFileName(path: string): string {
  const parts = path.split('/');
  return parts[parts.length - 1];
}

function getStatusClass(status: string): string {
  switch (status) {
    case 'M':
    case 'MM':
      return 'modified';
    case 'A':
    case 'AM':
      return 'added';
    case 'D':
      return 'deleted';
    case '??':
      return 'untracked';
    default:
      return '';
  }
}

async function handleClone() {
  const success = await cloneOrPull();
  if (success) {
    emit('files-changed');
  }
}

async function handlePull() {
  const success = await pull();
  if (success) {
    emit('files-changed');
  }
}

async function handlePush() {
  if (!canCommit.value) return;
  
  const success = await push(commitMessage.value.trim());
  if (success) {
    commitMessage.value = '';
    emit('commit-success');
  }
}

// GitHub 모드가 활성화되면 상태 확인
watch(() => props.isGitHubMode, async (isActive) => {
  if (isActive) {
    await checkGitStatus();
  }
}, { immediate: true });
</script>

<style scoped>
.git-panel {
  border-top: 1px solid var(--border-subtle);
  padding-top: 12px;
  margin-top: 12px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s ease;
}

.panel-header:hover {
  background: rgba(255, 255, 255, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-icon {
  color: var(--text-muted);
  transition: transform 0.15s ease;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.git-icon {
  color: var(--text-muted);
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.badge {
  background: rgba(255, 255, 255, 0.15);
  color: var(--text-primary);
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.panel-content {
  padding: 8px;
}

/* 경고 메시지 */
.warning-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 8px;
  color: #f59e0b;
}

.warning-message svg {
  flex-shrink: 0;
  margin-top: 2px;
}

.warning-message p {
  font-size: 13px;
  font-weight: 500;
  margin: 0 0 4px;
}

.warning-message span {
  font-size: 11px;
  opacity: 0.8;
}

/* 클론 프롬프트 */
.clone-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  text-align: center;
}

.clone-prompt svg {
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 12px;
}

.clone-prompt p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px;
}

.clone-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.clone-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.clone-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 커밋 섹션 */
.commit-section {
  margin-bottom: 16px;
}

.commit-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: all 0.15s ease;
}

.commit-input:focus {
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05);
}

.commit-input::placeholder {
  color: var(--text-muted);
}

.commit-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.commit-actions {
  margin-top: 10px;
}

.commit-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.commit-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.25);
}

.commit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 변경 섹션 */
.changes-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 4px;
  margin-bottom: 6px;
}

.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.changes-count {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 10px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.changed-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.15s ease;
}

.changed-file:hover {
  background: rgba(255, 255, 255, 0.04);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.modified {
  background: #f59e0b;
}

.status-dot.added {
  background: #22c55e;
}

.status-dot.deleted {
  background: #ef4444;
}

.status-dot.untracked {
  background: #3b82f6;
}

.file-name {
  flex: 1;
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 빈 상태 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  text-align: center;
}

.empty-state svg {
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 12px;
}

.empty-state p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 4px;
}

.empty-state .hint {
  font-size: 11px;
  color: var(--text-muted);
}

/* 에러 메시지 */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 6px;
  color: #ef4444;
  font-size: 12px;
  margin-top: 12px;
}
</style>
