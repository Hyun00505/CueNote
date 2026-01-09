<template>
  <Teleport to="body">
    <Transition name="panel-slide">
      <div v-if="visible" class="proofread-panel" @click.stop>
        <!-- 헤더 -->
        <div class="panel-header">
          <div class="header-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 11l3 3L22 4"/>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
            <span>맞춤법 검사</span>
            <span class="lang-badge" v-if="languageDetected">
              {{ languageDetected === 'ko' ? '한국어' : languageDetected === 'en' ? '영어' : '혼합' }}
            </span>
          </div>
          <div class="header-actions">
            <span class="item-count" v-if="items.length > 0">
              {{ appliedCount }}/{{ items.length }} 수정됨
            </span>
            <button class="close-btn" @click="handleClose" title="닫기">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>맞춤법을 검사하고 있습니다...</span>
        </div>

        <!-- 오류 없음 -->
        <div v-else-if="items.length === 0 && !loading" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 12l2 2 4-4"/>
            <circle cx="12" cy="12" r="10"/>
          </svg>
          <span>맞춤법 오류가 없습니다!</span>
          <p>텍스트가 올바르게 작성되었습니다.</p>
        </div>

        <!-- 수정 항목 목록 -->
        <div v-else class="items-container">
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
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
                <span class="corrected">{{ item.corrected }}</span>
              </div>
              <p class="reason" v-if="item.reason">{{ item.reason }}</p>
            </div>

            <div class="item-actions" v-if="!item.applied && !item.skipped">
              <button 
                class="action-btn skip" 
                @click="skipItem(index)"
                title="무시"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
              <button 
                class="action-btn apply" 
                @click="applyItem(index)"
                title="적용"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
              </button>
            </div>

            <div class="item-status" v-else>
              <span v-if="item.applied" class="status applied">✓ 적용됨</span>
              <span v-else-if="item.skipped" class="status skipped">— 무시됨</span>
            </div>
          </div>
        </div>

        <!-- 하단 액션 바 -->
        <div class="panel-footer" v-if="items.length > 0 && !loading">
          <button 
            class="footer-btn secondary" 
            @click="skipAll"
            :disabled="remainingCount === 0"
          >
            모두 무시
          </button>
          <button 
            class="footer-btn primary" 
            @click="applyAll"
            :disabled="remainingCount === 0"
          >
            모두 적용 ({{ remainingCount }})
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

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

const appliedCount = computed(() => props.items.filter(i => i.applied).length);
const remainingCount = computed(() => props.items.filter(i => !i.applied && !i.skipped).length);

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    spelling: '맞춤법',
    grammar: '문법',
    punctuation: '구두점',
    spacing: '띄어쓰기'
  };
  return labels[type] || type;
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
  background: linear-gradient(135deg, #1a1a1f 0%, #16161a 100%);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 16px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    0 0 60px -20px rgba(34, 197, 94, 0.2);
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
  background: linear-gradient(90deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.08) 100%);
  border-bottom: 1px solid rgba(34, 197, 94, 0.2);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #4ade80;
  font-size: 14px;
  font-weight: 600;
}

.header-title svg {
  opacity: 0.9;
}

.lang-badge {
  padding: 3px 8px;
  background: rgba(34, 197, 94, 0.2);
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
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
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
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
  border: 3px solid rgba(34, 197, 94, 0.2);
  border-top-color: #4ade80;
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
  color: #4ade80;
  opacity: 0.8;
}

.empty-state span {
  color: #4ade80;
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
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

/* 개별 수정 항목 */
.correction-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  margin-bottom: 10px;
  transition: all 0.2s ease;
}

.correction-item:not(.applied):not(.skipped) {
  cursor: pointer;
}

.correction-item:not(.applied):not(.skipped):hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.correction-item.applied {
  background: rgba(34, 197, 94, 0.08);
  border-color: rgba(34, 197, 94, 0.2);
  opacity: 0.7;
}

.correction-item.skipped {
  background: rgba(255, 255, 255, 0.01);
  opacity: 0.5;
}

.item-type {
  display: flex;
  align-items: center;
}

.type-badge {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-badge.spelling {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.type-badge.grammar {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.type-badge.punctuation {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.type-badge.spacing {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.2);
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
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 6px;
  color: #f87171;
  font-size: 14px;
  text-decoration: line-through;
  text-decoration-color: rgba(239, 68, 68, 0.5);
}

.corrected {
  padding: 4px 10px;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.25);
  border-radius: 6px;
  color: #4ade80;
  font-size: 14px;
  font-weight: 500;
}

.reason {
  margin: 8px 0 0 0;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
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
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn.skip {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

.action-btn.skip:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.action-btn.apply {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.action-btn.apply:hover {
  background: rgba(34, 197, 94, 0.25);
  color: #86efac;
}

.item-status {
  margin-top: 4px;
}

.status {
  font-size: 11px;
  font-weight: 500;
}

.status.applied {
  color: #4ade80;
}

.status.skipped {
  color: var(--text-muted);
}

/* 하단 액션 바 */
.panel-footer {
  display: flex;
  gap: 10px;
  padding: 14px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.footer-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.footer-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-btn.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.footer-btn.primary {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.3) 0%, rgba(16, 185, 129, 0.25) 100%);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.footer-btn.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.4) 0%, rgba(16, 185, 129, 0.35) 100%);
  border-color: rgba(34, 197, 94, 0.5);
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
