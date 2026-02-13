<template>
  <div class="calendar-view">
    <!-- 배경 효과 -->
    <div class="view-background">
      <div class="bg-gradient bg-gradient-1" />
      <div class="bg-gradient bg-gradient-2" />
      <div class="bg-noise" />
    </div>

    <!-- 오늘의 포커스 카드 -->
    <TodayFocusCard
      :schedules="todaySchedules"
      :show-empty="false"
      @go-today="scrollToToday"
    />

    <div class="calendar-body">
      <!-- 캘린더 그리드 (전체 너비) -->
      <CalendarGrid
        ref="calendarGridRef"
        :calendar-months="calendarMonths"
        :all-schedules="rangeSchedules"
        @select-date="handleSelectDate"
        @load-more="loadMoreMonths"
        @fetch-range-schedules="fetchSchedulesByDateRange"
        @quick-add="handleQuickAdd"
        @schedule-click="handleScheduleClick"
      />
    </div>

    <!-- 슬라이드 오버 일정 패널 -->
    <Teleport to="body">
      <Transition name="slide-panel">
        <div
          v-if="showSchedulePanel"
          class="panel-overlay"
          @click.self="showSchedulePanel = false"
        >
          <div class="panel-slide">
            <button class="panel-close-btn" @click="showSchedulePanel = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <SchedulePanel
              :schedules="selectedSchedules"
              :selected-date="selectedDate"
              :loading="loading"
              :error="error"
              @add-schedule="openAddModal"
              @edit-schedule="openEditModal"
              @delete-schedule="openDeleteConfirm"
              @toggle-complete="handleToggleComplete"
              @ai-extract="showExtractModal = true"
              @go-today="scrollToToday"
            />
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 일정 팝오버 -->
    <SchedulePopover
      :visible="showPopover"
      :schedule="popoverSchedule"
      :anchor-rect="popoverAnchor"
      @close="showPopover = false"
      @edit="openEditModal"
      @delete="openDeleteConfirm"
      @toggle-complete="handleToggleComplete"
    />

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
  AIExtractModal,
  TodayFocusCard,
  SchedulePopover,
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
  todaySchedules,
  goToToday,
  selectDate,
  loadMoreMonths,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  toggleComplete,
  quickCreateSchedule,
  fetchTodaySchedules,
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
const showSchedulePanel = ref(false);
const editingSchedule = ref<ScheduleItem | null>(null);
const deleteTarget = ref<ScheduleItem | null>(null);

// 팝오버 상태
const showPopover = ref(false);
const popoverSchedule = ref<ScheduleItem | null>(null);
const popoverAnchor = ref<{ top: number; left: number; width: number; height: number } | null>(null);

// AI 추출 상태
const extractedSchedules = ref<ScheduleItem[]>([]);
const extractLoading = ref(false);
const extractError = ref('');
const extractConfidence = ref(0);

// 날짜 선택 → 슬라이드 패널 열기
function handleSelectDate(date: string) {
  selectDate(date);
  showSchedulePanel.value = true;
  showPopover.value = false;
}

// 일정 블록 클릭 → 팝오버
function handleScheduleClick(schedule: ScheduleItem, event: MouseEvent) {
  const rect = (event.target as HTMLElement).getBoundingClientRect();
  popoverSchedule.value = schedule;
  popoverAnchor.value = {
    top: rect.top,
    left: rect.left,
    width: rect.width,
    height: rect.height,
  };
  showPopover.value = true;
}

// 빠른 일정 추가
async function handleQuickAdd(data: { title: string; date: string; startTime: string; endTime: string }) {
  await quickCreateSchedule(data.title, data.date, data.startTime, data.endTime);
  await fetchTodaySchedules();
}

// 완료 토글 (패널/팝오버 공용)
async function handleToggleComplete(id: string) {
  await toggleComplete(id);
  await fetchTodaySchedules();
}

// 오늘로 스크롤
function scrollToToday() {
  goToToday();
  showSchedulePanel.value = false;
  setTimeout(() => {
    calendarGridRef.value?.scrollToToday(true);
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
  showPopover.value = false;
}

function closeModal() {
  showModal.value = false;
  editingSchedule.value = null;
}

function openDeleteConfirm(schedule: ScheduleItem) {
  deleteTarget.value = schedule;
  showDeleteConfirm.value = true;
  showPopover.value = false;
}

async function handleDeleteConfirm() {
  if (deleteTarget.value?.id) {
    await deleteSchedule(deleteTarget.value.id);
    await fetchTodaySchedules();
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
  await fetchTodaySchedules();
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
    await fetchTodaySchedules();
  }
  closeExtractModal();
}

// 초기화
onMounted(() => {
  init();
  // 오늘 날짜로 스크롤 (DOM 완전히 렌더링 후)
  setTimeout(() => {
    calendarGridRef.value?.scrollToToday(false);
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

/* 본문 - 전체 너비 */
.calendar-body {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  z-index: 1;
}

/* 슬라이드 패널 오버레이 */
.panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 900;
  display: flex;
  justify-content: flex-end;
}

.panel-slide {
  position: relative;
  width: 400px;
  max-width: 90vw;
  height: 100%;
  background: var(--bg-primary);
  border-left: 1px solid var(--surface-3);
  box-shadow: -8px 0 30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-close-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-2);
  border: 1px solid var(--surface-3);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  z-index: 10;
  transition: all 0.15s ease;
}

.panel-close-btn:hover {
  background: var(--surface-3);
  color: var(--text-primary);
}

/* 슬라이드 전환 애니메이션 */
.slide-panel-enter-active {
  transition: opacity 0.2s ease;
}

.slide-panel-enter-active .panel-slide {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-panel-leave-active {
  transition: opacity 0.15s ease;
}

.slide-panel-leave-active .panel-slide {
  transition: transform 0.2s ease;
}

.slide-panel-enter-from {
  opacity: 0;
}

.slide-panel-enter-from .panel-slide {
  transform: translateX(100%);
}

.slide-panel-leave-to {
  opacity: 0;
}

.slide-panel-leave-to .panel-slide {
  transform: translateX(100%);
}
</style>
