<template>
  <div class="calendar-view">
    <!-- 캘린더 헤더 -->
    <div class="calendar-header">
      <div class="calendar-title-section">
        <h1>{{ t('calendar.title') }}</h1>
        <p>{{ t('calendar.subtitle') }}</p>
      </div>
      <div class="calendar-actions">
        <button class="action-btn ai-extract-btn" @click="showExtractModal = true" :title="t('calendar.aiExtract')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
          </svg>
          <span>{{ t('calendar.aiExtract') }}</span>
        </button>
        <button class="action-btn today-btn" @click="scrollToToday">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>{{ t('common.today') }}</span>
        </button>
      </div>
    </div>

    <div class="calendar-body">
      <!-- 캘린더 그리드 -->
      <CalendarGrid
        ref="calendarGridRef"
        :calendar-months="calendarMonths"
        @select-date="selectDate"
        @load-more="loadMoreMonths"
      />

      <!-- 일정 상세 패널 -->
      <SchedulePanel
        :schedules="selectedSchedules"
        :selected-date="selectedDate"
        :loading="loading"
        :error="error"
        @add-schedule="openAddModal"
        @edit-schedule="openEditModal"
        @delete-schedule="openDeleteConfirm"
        @toggle-complete="toggleComplete"
      />
    </div>

    <!-- 일정 추가/수정 모달 -->
    <Teleport to="body">
      <ScheduleFormModal
        :visible="showModal"
        :editing-schedule="editingSchedule"
        :selected-date="selectedDate"
        @close="closeModal"
        @save="handleSaveSchedule"
      />
    </Teleport>

    <!-- 삭제 확인 모달 -->
    <Teleport to="body">
      <ScheduleDeleteModal
        :visible="showDeleteConfirm"
        :schedule-name="deleteTarget?.title || ''"
        @close="showDeleteConfirm = false; deleteTarget = null"
        @confirm="handleDeleteConfirm"
      />
    </Teleport>

    <!-- AI 추출 모달 -->
    <Teleport to="body">
      <AIExtractModal
        :visible="showExtractModal"
        :vault-files="vaultFiles"
        :extracted-schedules="extractedSchedules"
        :confidence="extractConfidence"
        :loading="extractLoading"
        :error="extractError"
        @close="closeExtractModal"
        @extract="handleExtract"
        @save="saveExtractedSchedules"
      />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useSchedule, useVault, useI18n } from '../composables';
import {
  CalendarGrid,
  SchedulePanel,
  ScheduleFormModal,
  ScheduleDeleteModal,
  AIExtractModal
} from './dashboard';
import type { ScheduleItem } from '../types';

const { t } = useI18n();

defineProps<{
  hasVault: boolean;
}>();

const {
  selectedSchedules,
  calendarMonths,
  selectedDate,
  loading,
  error,
  goToToday,
  selectDate,
  loadMoreMonths,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  toggleComplete,
  extractSchedulesFromNote,
  createSchedulesBatch,
  init,
} = useSchedule();

const { vaultFiles } = useVault();

// Refs
const calendarGridRef = ref<InstanceType<typeof CalendarGrid> | null>(null);

// 모달 상태
const showModal = ref(false);
const showDeleteConfirm = ref(false);
const showExtractModal = ref(false);
const editingSchedule = ref<ScheduleItem | null>(null);
const deleteTarget = ref<ScheduleItem | null>(null);

// AI 추출 상태
const extractedSchedules = ref<ScheduleItem[]>([]);
const extractLoading = ref(false);
const extractError = ref('');
const extractConfidence = ref(0);

// 오늘로 스크롤
function scrollToToday() {
  goToToday();
  nextTick(() => {
    calendarGridRef.value?.scrollToToday();
  });
}

// 모달 열기/닫기
function openAddModal() {
  editingSchedule.value = null;
  showModal.value = true;
}

function openEditModal(schedule: ScheduleItem) {
  editingSchedule.value = schedule;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingSchedule.value = null;
}

function openDeleteConfirm(schedule: ScheduleItem) {
  deleteTarget.value = schedule;
  showDeleteConfirm.value = true;
}

async function handleDeleteConfirm() {
  if (deleteTarget.value?.id) {
    await deleteSchedule(deleteTarget.value.id);
  }
  showDeleteConfirm.value = false;
  deleteTarget.value = null;
}

// 일정 저장
async function handleSaveSchedule(data: {
  title: string;
  description: string;
  date: string;
  startTime: string;
  endTime: string;
  color: string;
}) {
  if (editingSchedule.value?.id) {
    await updateSchedule(editingSchedule.value.id, data);
  } else {
    await createSchedule(data);
  }
  closeModal();
}

// AI 추출
async function handleExtract(content: string) {
  extractLoading.value = true;
  extractError.value = '';
  extractedSchedules.value = [];

  try {
    const result = await extractSchedulesFromNote(content);
    extractedSchedules.value = result.schedules || [];
    extractConfidence.value = result.confidence || 0;
  } catch (e: any) {
    extractError.value = e.message || 'AI 추출 중 오류가 발생했습니다.';
  } finally {
    extractLoading.value = false;
  }
}

function closeExtractModal() {
  showExtractModal.value = false;
  extractedSchedules.value = [];
  extractError.value = '';
  extractConfidence.value = 0;
}

async function saveExtractedSchedules(indexes: number[]) {
  const schedulesToSave = indexes.map(i => extractedSchedules.value[i]);
  if (schedulesToSave.length > 0) {
    await createSchedulesBatch(schedulesToSave);
  }
  closeExtractModal();
}

// 초기화
onMounted(() => {
  init();
  // 오늘 날짜로 스크롤
  nextTick(() => {
    calendarGridRef.value?.scrollToToday();
  });
});

// 외부에서 호출 가능하도록 노출
defineExpose({
  scrollToToday
});
</script>

<style scoped>
.calendar-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

/* Header */
.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 32px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  flex-shrink: 0;
}

.calendar-title-section h1 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  letter-spacing: -0.02em;
}

.calendar-title-section p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.calendar-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 9px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.ai-extract-btn {
  background: rgba(139, 92, 246, 0.08);
  border-color: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
}

.ai-extract-btn:hover {
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.35);
}

.today-btn {
  background: rgba(201, 167, 108, 0.1);
  border-color: rgba(201, 167, 108, 0.25);
  color: #e8d5b7;
}

.today-btn:hover {
  background: rgba(201, 167, 108, 0.18);
  border-color: rgba(201, 167, 108, 0.4);
}

/* Body */
.calendar-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 340px;
  min-height: 0;
  overflow: hidden;
}

/* Light theme */
:global([data-theme="light"]) .calendar-header {
  background: #ffffff;
  border-bottom-color: rgba(0, 0, 0, 0.06);
}

:global([data-theme="light"]) .calendar-title-section h1 {
  color: #1f2937;
}

:global([data-theme="light"]) .action-btn {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.1);
  color: #374151;
}

:global([data-theme="light"]) .action-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.15);
  color: #111827;
}

:global([data-theme="light"]) .ai-extract-btn {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
  color: #6366f1;
}

:global([data-theme="light"]) .ai-extract-btn:hover {
  background: rgba(99, 102, 241, 0.14);
  border-color: rgba(99, 102, 241, 0.3);
}

:global([data-theme="light"]) .today-btn {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

:global([data-theme="light"]) .today-btn:hover {
  background: rgba(59, 130, 246, 0.14);
  border-color: rgba(59, 130, 246, 0.3);
}
</style>
