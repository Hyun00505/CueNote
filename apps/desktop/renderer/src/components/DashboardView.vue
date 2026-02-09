<template>
  <div class="calendar-view">
    <!-- 배경 효과 -->
    <div class="view-background">
      <div class="bg-gradient bg-gradient-1" />
      <div class="bg-gradient bg-gradient-2" />
      <div class="bg-noise" />
    </div>

    <div class="calendar-body">
      <!-- 캘린더 그리드 -->
      <CalendarGrid
        ref="calendarGridRef"
        :calendar-months="calendarMonths"
        :all-schedules="rangeSchedules"
        @select-date="selectDate"
        @load-more="loadMoreMonths"
        @fetch-range-schedules="fetchSchedulesByDateRange"
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
        @ai-extract="showExtractModal = true"
        @go-today="scrollToToday"
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
  rangeSchedules,
  goToToday,
  selectDate,
  loadMoreMonths,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  toggleComplete,
  extractSchedulesFromNote,
  createSchedulesBatch,
  fetchSchedulesByDateRange,
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
  setTimeout(() => {
    calendarGridRef.value?.scrollToToday(true); // 버튼 클릭시에는 부드럽게 애니메이션
  }, 50);
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
  // 오늘 날짜로 스크롤 (DOM 완전히 렌더링 후)
  setTimeout(() => {
    calendarGridRef.value?.scrollToToday(false); // 초기 로드시에는 애니메이션 없이
  }, 150);
});

// 외부에서 호출 가능하도록 노출
defineExpose({
  scrollToToday
});
</script>

<style scoped>
.calendar-view {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow: hidden;
}

/* 배경 효과 */
.view-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.04;
}

.bg-gradient-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #c9a76c 0%, #e8d5b7 50%, #d4a574 100%);
  top: -200px;
  left: -200px;
  animation: gradientFloat1 20s ease-in-out infinite;
}

.bg-gradient-2 {
  width: 500px;
  height: 500px;
  background: linear-gradient(225deg, #10b981 0%, #34d399 50%, #6ee7b7 100%);
  bottom: -150px;
  right: -150px;
  animation: gradientFloat2 25s ease-in-out infinite;
}

@keyframes gradientFloat1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, 20px) scale(1.05); }
  66% { transform: translate(-20px, 30px) scale(0.95); }
}

@keyframes gradientFloat2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-25px, -15px) scale(1.03); }
  66% { transform: translate(20px, -25px) scale(0.97); }
}

.bg-noise {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.015;
  mix-blend-mode: overlay;
}

/* 본문 */
.calendar-body {
  position: relative;
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 380px;
  min-height: 0;
  overflow: hidden;
  z-index: 1;
}

/* 반응형 */
@media (max-width: 900px) {
  .calendar-body {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 1fr;
  }
}
</style>
