<template>
  <div
    v-if="isVisible"
    class="git-panel"
  >
    <div
      class="panel-header"
      @click="toggleExpanded"
    >
      <div class="header-left">
        <svg
          class="expand-icon"
          :class="{ expanded: isExpanded }"
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="9 6 15 12 9 18" />
        </svg>
        <svg
          class="git-icon"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
        </svg>
        <span class="panel-title">Source Control</span>
      </div>
      <div class="header-right">
        <span
          v-if="changesCount > 0"
          class="badge"
        >{{ changesCount }}</span>
        <button
          class="action-btn"
          :disabled="isPulling"
          title="Pull"
          @click.stop="handlePull"
        >
          <svg
            :class="{ spinning: isPulling }"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M23 4v6h-6M1 20v-6h6" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
        </button>
      </div>
    </div>

    <div
      v-show="isExpanded"
      class="panel-content"
    >
      <!-- Git이 설치되지 않은 경우 -->
      <div
        v-if="!gitInstalled"
        class="warning-message"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
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
        <div>
          <p>Git이 설치되어 있지 않습니다</p>
          <span>Git을 설치한 후 앱을 재시작해주세요</span>
        </div>
      </div>

      <!-- 클론되지 않은 경우 -->
      <div
        v-else-if="!isCloned"
        class="clone-prompt"
      >
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line
            x1="12"
            y1="15"
            x2="12"
            y2="3"
          />
        </svg>
        <p>리포지토리를 클론해주세요</p>
        <button
          class="clone-btn"
          :disabled="isCloning"
          @click="handleClone"
        >
          <svg
            v-if="isCloning"
            class="spinning"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
            />
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
            :disabled="isPushing || stagedCount === 0"
          />
          
          <div class="commit-actions">
            <button 
              class="commit-btn"
              :disabled="!canCommit"
              @click="handlePush"
            >
              <svg
                v-if="isPushing"
                class="spinning"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                />
              </svg>
              <svg
                v-else
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22L11 13L2 9L22 2Z" />
              </svg>
              {{ isPushing ? '푸시 중...' : `Commit & Push (${stagedCount})` }}
            </button>
          </div>
        </div>

        <!-- 변경된 파일 목록 -->
        <div
          v-if="changesCount > 0"
          class="changes-section"
        >
          <div class="section-header">
            <div class="section-header-left">
              <label 
                class="custom-checkbox"
                :class="{ checked: isAllSelected, indeterminate: isPartialSelected }"
                title="전체 선택/해제"
                @click.prevent="toggleSelectAll"
              >
                <svg
                  v-if="isAllSelected"
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <svg
                  v-else-if="isPartialSelected"
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                >
                  <line
                    x1="5"
                    y1="12"
                    x2="19"
                    y2="12"
                  />
                </svg>
              </label>
              <span class="section-title">STAGED CHANGES</span>
            </div>
            <span
              class="changes-count"
              :class="{ 'has-staged': stagedCount > 0 }"
            >
              {{ stagedCount }}/{{ changesCount }}
            </span>
          </div>
          <div class="file-list">
            <div 
              v-for="change in gitChanges" 
              :key="change.path"
              class="changed-file"
              :class="{ 'staged': isFileStaged(change.path) }"
              :title="change.path"
              @click="toggleStageFile(change.path)"
            >
              <label 
                class="custom-checkbox"
                :class="{ checked: isFileStaged(change.path) }"
                @click.stop="toggleStageFile(change.path)"
              >
                <svg
                  v-if="isFileStaged(change.path)"
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </label>
              <span class="file-name">{{ getFileName(change.path) }}</span>
              <span
                class="status-badge"
                :class="getStatusClass(change.status_text)"
              >{{ getStatusLabel(change.status_text) }}</span>
            </div>
          </div>
        </div>

        <!-- 변경사항 없음 -->
        <div
          v-else
          class="empty-state"
        >
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <p>변경사항이 없습니다</p>
          <span class="hint">파일을 수정하면 여기에 표시됩니다</span>
        </div>
      </template>

      <!-- 에러 메시지 -->
      <div
        v-if="error"
        class="error-message"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle
            cx="12"
            cy="12"
            r="10"
          />
          <line
            x1="12"
            y1="8"
            x2="12"
            y2="12"
          />
          <line
            x1="12"
            y1="16"
            x2="12.01"
            y2="16"
          />
        </svg>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useGitHub } from '../../composables/useGitHub';
import { useI18n } from '../../composables';

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
  checkGitStatus,
  // Staging
  stagedFiles,
  stagedCount,
  toggleStageFile,
  stageAll,
  unstageAll,
  isFileStaged
} = useGitHub();

const { t } = useI18n();

const isExpanded = ref(true);
const commitMessage = ref('');

const isVisible = computed(() => props.isGitHubMode);
const changesCount = computed(() => gitChanges.value.length);

// 커밋 가능 여부: 선택된 파일이 있고 메시지가 있어야 함
const canCommit = computed(() => 
  !isPushing.value && 
  stagedCount.value > 0 && 
  commitMessage.value.trim().length > 0
);

// 전체 선택 상태
const isAllSelected = computed(() => 
  changesCount.value > 0 && stagedCount.value === changesCount.value
);

// 일부만 선택된 상태
const isPartialSelected = computed(() => 
  stagedCount.value > 0 && stagedCount.value < changesCount.value
);

// 전체 선택/해제 토글
function toggleSelectAll() {
  if (isAllSelected.value) {
    unstageAll();
  } else {
    stageAll();
  }
}

function toggleExpanded() {
  isExpanded.value = !isExpanded.value;
}

function getFileName(path: string): string {
  // 폴더인 경우 (/ 로 끝나거나 .gitkeep)
  if (path.endsWith('/')) {
    const folderPath = path.slice(0, -1);  // 마지막 / 제거
    const parts = folderPath.split('/');
    return parts[parts.length - 1] + '/';  // 폴더임을 표시
  }
  if (path.endsWith('.gitkeep')) {
    const folderPath = path.replace('/.gitkeep', '').replace('.gitkeep', '');
    const parts = folderPath.split('/');
    return parts[parts.length - 1] + '/';  // 폴더임을 표시
  }
  const parts = path.split('/');
  return parts[parts.length - 1];
}

function getStatusClass(status: string): string {
  const statusLower = status.toLowerCase();
  if (statusLower.includes('삭제') || statusLower.includes('delete')) return 'deleted';
  if (statusLower.includes('추가') || statusLower.includes('add') || statusLower.includes('new')) return 'added';
  if (statusLower.includes('수정') || statusLower.includes('modif')) return 'modified';
  return 'default';
}

function getStatusLabel(status: string): string {
  const statusLower = status.toLowerCase();
  if (statusLower.includes('삭제') || statusLower.includes('delete')) return t('git.status.deleted');
  if (statusLower.includes('추가') || statusLower.includes('add') || statusLower.includes('new')) return t('git.status.added');
  if (statusLower.includes('수정') || statusLower.includes('modif')) return t('git.status.modified');
  return status;
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
  background: var(--bg-hover);
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
  background: var(--bg-active);
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
  background: var(--bg-hover);
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
  background: var(--warning-glow);
  border: 1px solid var(--warning-glow);
  border-radius: 8px;
  color: var(--warning);
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
  background: var(--bg-hover);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.clone-btn:hover:not(:disabled) {
  background: var(--bg-active);
  border-color: var(--border-strong);
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
  background: var(--bg-hover);
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
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
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
  background: var(--bg-hover);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.commit-btn:hover:not(:disabled) {
  background: var(--bg-active);
  border-color: var(--border-strong);
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

.section-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 커스텀 체크박스 */
.custom-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border: 1.5px solid var(--border-default);
  border-radius: 4px;
  background: var(--bg-hover);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.custom-checkbox:hover {
  border-color: var(--border-strong);
  background: var(--bg-active);
}

.custom-checkbox.checked {
  background: var(--success);
  border-color: var(--success);
}

.custom-checkbox.checked:hover {
  background: var(--success);
  border-color: var(--success);
  filter: brightness(1.1);
}

.custom-checkbox.indeterminate {
  background: var(--success-glow);
  border-color: var(--success);
}

.custom-checkbox svg {
  color: white;
}

.custom-checkbox.indeterminate svg {
  color: var(--success);
}

.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.changes-count {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg-hover);
  padding: 2px 8px;
  border-radius: 10px;
  transition: all 0.15s ease;
}

.changes-count.has-staged {
  color: var(--success);
  background: var(--success-glow);
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
  padding: 6px 8px;
  border-radius: 4px;
  transition: all 0.15s ease;
  cursor: pointer;
}

.changed-file:hover {
  background: var(--bg-hover);
}

.changed-file.staged {
  background: var(--bg-active);
}

.changed-file.staged:hover {
  background: var(--bg-active);
}

.changed-file .custom-checkbox {
  width: 15px;
  height: 15px;
}

.status-badge {
  margin-left: auto;
  font-size: 10px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: lowercase;
}

.status-badge.deleted {
  color: var(--error);
  background: var(--error-glow);
}

.status-badge.added {
  color: var(--success);
  background: var(--success-glow);
}

.status-badge.modified {
  color: var(--warning);
  background: var(--warning-glow);
}

.status-badge.default {
  color: var(--text-muted);
  background: var(--bg-hover);
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
  background: var(--error-glow);
  border: 1px solid var(--error-glow);
  border-radius: 6px;
  color: var(--error);
  font-size: 12px;
  margin-top: 12px;
}
</style>
