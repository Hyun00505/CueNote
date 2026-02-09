<template>
  <Teleport to="body">
    <Transition name="panel-slide">
      <div
        v-if="visible"
        class="proofread-panel"
        @click.stop
      >
        <!-- 헤더 -->
        <div class="panel-header">
          <div class="header-title">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
            <span>{{ t('proofread.title') }}</span>
            <span
              v-if="languageDetected"
              class="lang-badge"
            >
              {{ getLanguageLabel(languageDetected) }}
            </span>
          </div>
          <div class="header-actions">
            <span
              v-if="items.length > 0"
              class="item-count"
            >
              {{ appliedCount }}/{{ items.length }} {{ t('proofread.modified') }}
            </span>
            <button
              class="close-btn"
              :title="t('common.close')"
              @click="handleClose"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                />
                <line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- 로딩 상태 -->
        <div
          v-if="loading"
          class="loading-state"
        >
          <div class="loading-spinner" />
          <span>{{ t('proofread.checking') }}</span>
        </div>

        <!-- 오류 없음 -->
        <div
          v-else-if="items.length === 0 && !loading"
          class="empty-state"
        >
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path d="M9 12l2 2 4-4" />
            <circle
              cx="12"
              cy="12"
              r="10"
            />
          </svg>
          <span>{{ t('proofread.noErrors') }}</span>
          <p>{{ t('proofread.noErrorsDesc') }}</p>
        </div>

        <!-- 수정 항목 목록 -->
        <div
          v-else
          class="items-container"
        >
          <div 
            v-for="(item, index) in items" 
            :key="index"
            class="correction-item"
            :class="{ applied: item.applied, skipped: item.skipped }"
            @click="!item.applied && !item.skipped && focusItem(index)"
          >
            <div class="item-type">
              <span :class="['type-badge', item.type]">
                {{ getTypeLabel(item.type) }}
              </span>
            </div>
            
            <div class="item-content">
              <div class="correction-row">
                <span class="original">{{ item.original }}</span>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
                <span class="corrected">{{ item.corrected }}</span>
              </div>
              <p
                v-if="item.reason"
                class="reason"
              >
                {{ item.reason }}
              </p>
            </div>

            <div
              v-if="!item.applied && !item.skipped"
              class="item-actions"
            >
              <button 
                class="action-btn skip" 
                :title="t('proofread.ignoreAll').split(' ')[1]"
                @click="skipItem(index)"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line
                    x1="18"
                    y1="6"
                    x2="6"
                    y2="18"
                  />
                  <line
                    x1="6"
                    y1="6"
                    x2="18"
                    y2="18"
                  />
                </svg>
              </button>
              <button 
                class="action-btn apply" 
                :title="t('proofread.applyAll').split(' ')[1]"
                @click="applyItem(index)"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              </button>
            </div>

            <div
              v-else
              class="item-status"
            >
              <span
                v-if="item.applied"
                class="status applied"
              >✓ {{ t('proofread.applied') }}</span>
              <span
                v-else-if="item.skipped"
                class="status skipped"
              >— {{ t('proofread.skipped') }}</span>
            </div>
          </div>
        </div>

        <!-- 하단 액션 바 -->
        <div
          v-if="items.length > 0 && !loading"
          class="panel-footer"
        >
          <button 
            class="footer-btn secondary" 
            :disabled="remainingCount === 0"
            @click="skipAll"
          >
            {{ t('proofread.ignoreAll') }}
          </button>
          <button 
            class="footer-btn primary" 
            :disabled="remainingCount === 0"
            @click="applyAll"
          >
            {{ t('proofread.applyAll') }} ({{ remainingCount }})
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from '../composables';

interface CorrectionItem {
  original: string;
  corrected: string;
  reason: string;
  type: string;
  applied?: boolean;
  skipped?: boolean;
}

const props = defineProps<{
  visible: boolean;
  loading: boolean;
  originalText: string;
  correctedText: string;
  items: CorrectionItem[];
  languageDetected: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'apply-item', data: { index: number; original: string; corrected: string }): void;
  (e: 'apply-all'): void;
  (e: 'skip-item', index: number): void;
  (e: 'skip-all'): void;
  (e: 'focus-item', index: number): void;
}>();

const { t } = useI18n();

const appliedCount = computed(() => props.items.filter(i => i.applied).length);
const remainingCount = computed(() => props.items.filter(i => !i.applied && !i.skipped).length);

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    spelling: t('proofread.spelling'),
    grammar: t('proofread.grammar'),
    punctuation: t('proofread.punctuation'),
    spacing: t('proofread.spacing')
  };
  return labels[type] || type;
}

function getLanguageLabel(lang: string): string {
  if (lang === 'ko') return t('proofread.korean');
  if (lang === 'en') return t('proofread.english');
  return t('proofread.mixed');
}

function applyItem(index: number) {
  const item = props.items[index];
  emit('apply-item', {
    index,
    original: item.original,
    corrected: item.corrected
  });
}

function skipItem(index: number) {
  emit('skip-item', index);
}

function applyAll() {
  emit('apply-all');
}

function skipAll() {
  emit('skip-all');
}

function handleClose() {
  emit('close');
}

function focusItem(index: number) {
  emit('focus-item', index);
}
</script>

<style scoped>
.proofread-panel {
  position: fixed;
  top: 80px;
  right: 20px;
  width: 380px;
  max-height: calc(100vh - 120px);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 헤더 */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--success);
  font-size: 14px;
  font-weight: 600;
}

.header-title svg {
  opacity: 0.9;
}

.lang-badge {
  padding: 3px 8px;
  background: var(--success-glow);
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 500;
  color: var(--success);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-count {
  font-size: 12px;
  color: var(--text-muted);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  color: var(--text-muted);
  font-size: 14px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--success-glow);
  border-top-color: var(--success);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 빈 상태 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  text-align: center;
}

.empty-state svg {
  color: var(--success);
  opacity: 0.8;
}

.empty-state span {
  color: var(--success);
  font-size: 16px;
  font-weight: 600;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 13px;
  margin: 0;
}

/* 항목 컨테이너 */
.items-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.items-container::-webkit-scrollbar {
  width: 6px;
}

.items-container::-webkit-scrollbar-track {
  background: transparent;
}

.items-container::-webkit-scrollbar-thumb {
  background: var(--glass-border);
  border-radius: 3px;
}

.items-container::-webkit-scrollbar-thumb:hover {
  background: var(--glass-highlight);
}

/* 개별 수정 항목 */
.correction-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  background: var(--bg-hover);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  margin-bottom: 10px;
  transition: all var(--transition-fast);
}

.correction-item:not(.applied):not(.skipped) {
  cursor: pointer;
}

.correction-item:not(.applied):not(.skipped):hover {
  background: var(--bg-active);
  border-color: var(--border-default);
}

.correction-item.applied {
  background: var(--success-glow);
  border-color: var(--success);
  opacity: 0.7;
}

.correction-item.skipped {
  background: var(--bg-hover);
  opacity: 0.5;
}

.item-type {
  display: flex;
  align-items: center;
}

.type-badge {
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-badge.spelling {
  background: var(--error-glow);
  color: var(--error);
  border: 1px solid var(--error);
}

.type-badge.grammar {
  background: var(--warning-glow);
  color: var(--warning);
  border: 1px solid var(--warning);
}

.type-badge.punctuation {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.3);
}

.type-badge.spacing {
  background: var(--info-glow);
  color: var(--info);
  border: 1px solid var(--info);
}

.item-content {
  flex: 1;
}

.correction-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.correction-row svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.original {
  padding: 4px 10px;
  background: var(--error-glow);
  border: 1px solid var(--error);
  border-radius: var(--radius-sm);
  color: var(--error);
  font-size: 14px;
  text-decoration: line-through;
  text-decoration-color: var(--error);
}

.corrected {
  padding: 4px 10px;
  background: var(--success-glow);
  border: 1px solid var(--success);
  border-radius: var(--radius-sm);
  color: var(--success);
  font-size: 14px;
  font-weight: 500;
}

.reason {
  margin: 8px 0 0 0;
  padding: 8px 10px;
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.5;
}

/* 항목 액션 버튼 */
.item-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn.skip {
  background: var(--bg-hover);
  color: var(--text-muted);
}

.action-btn.skip:hover {
  background: var(--error-glow);
  color: var(--error);
}

.action-btn.apply {
  background: var(--success-glow);
  color: var(--success);
}

.action-btn.apply:hover {
  background: rgba(34, 197, 94, 0.3);
}

.item-status {
  margin-top: 4px;
}

.status {
  font-size: 11px;
  font-weight: 500;
}

.status.applied {
  color: var(--success);
}

.status.skipped {
  color: var(--text-muted);
}

/* 하단 액션 바 */
.panel-footer {
  display: flex;
  gap: 10px;
  padding: 14px 16px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-subtle);
}

.footer-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.footer-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.footer-btn.secondary {
  background: var(--bg-hover);
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

.footer-btn.secondary:hover:not(:disabled) {
  background: var(--bg-active);
}

.footer-btn.primary {
  background: var(--success-glow);
  color: var(--success);
  border: 1px solid var(--success);
}

.footer-btn.primary:hover:not(:disabled) {
  background: rgba(34, 197, 94, 0.3);
}

/* 트랜지션 */
.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.25s ease;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
