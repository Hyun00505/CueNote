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
      <!-- 스크롤 가능한 캘린더 영역 -->
      <div class="calendar-scroll" ref="calendarScrollRef">
        <!-- 이전 달 더보기 버튼 -->
        <button class="load-more-btn" @click="loadMoreMonths('up')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"/>
          </svg>
          이전 달 더보기
        </button>

        <!-- 월별 캘린더 -->
        <div
          v-for="monthData in calendarMonths"
          :key="`${monthData.year}-${monthData.month}`"
          class="month-section"
          :ref="el => setMonthRef(el, monthData.year, monthData.month)"
        >
          <div class="month-header">
            <h2>{{ monthData.label }}</h2>
          </div>

          <!-- 요일 헤더 -->
          <div class="weekday-header">
            <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
          </div>

          <!-- 달력 그리드 -->
          <div class="calendar-grid">
            <div
              v-for="day in monthData.days"
              :key="day.dateStr"
              class="calendar-day"
              :class="{
                'other-month': !day.isCurrentMonth,
                'today': day.isToday,
                'selected': day.isSelected,
                'has-schedules': day.scheduleCount > 0,
                'sunday': day.date.getDay() === 0,
                'saturday': day.date.getDay() === 6,
              }"
              @click="selectDate(day.dateStr)"
            >
              <span class="day-number">{{ day.day }}</span>
              <div v-if="day.scheduleCount > 0" class="schedule-indicator">
                <span class="schedule-count">{{ day.scheduleCount }}</span>
                <span v-if="day.completedCount > 0" class="completed-badge">
                  ✓{{ day.completedCount }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 다음 달 더보기 버튼 -->
        <button class="load-more-btn" @click="loadMoreMonths('down')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
          다음 달 더보기
        </button>
      </div>

      <!-- 일정 상세 패널 -->
      <div class="schedule-panel">
        <div class="panel-header">
          <h3>{{ selectedDateLabel }}</h3>
          <button class="add-schedule-btn" @click="openAddModal">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span>일정 추가</span>
          </button>
        </div>

        <!-- 일정 목록 -->
        <div class="schedule-list" v-if="!loading">
          <div
            v-for="schedule in selectedSchedules"
            :key="schedule.id"
            class="schedule-item"
            :class="{ completed: schedule.completed }"
          >
            <div class="schedule-color-dot" :style="{ background: schedule.color }"></div>
            
            <div class="schedule-main" @click="openEditModal(schedule)">
              <span class="schedule-title">{{ schedule.title }}</span>
              <span class="schedule-time" v-if="schedule.startTime">
                {{ schedule.startTime }}{{ schedule.endTime ? ` ~ ${schedule.endTime}` : '' }}
              </span>
            </div>

            <div class="schedule-actions">
              <button
                class="check-btn"
                @click="toggleComplete(schedule.id)"
                :title="schedule.completed ? '완료 취소' : '완료'"
              >
                <svg v-if="schedule.completed" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="9"/>
                </svg>
              </button>
              <button class="more-btn" @click="confirmDelete(schedule)" title="삭제">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 일정 없음 -->
          <div v-if="selectedSchedules.length === 0" class="empty-state">
            <p>{{ t('calendar.noSchedules') }}</p>
            <button class="add-first-btn" @click="openAddModal">{{ t('calendar.addFirst') }}</button>
          </div>
        </div>

        <!-- 로딩 -->
        <div v-else class="loading-schedules">
          <div class="spinner"></div>
          <span>일정을 불러오는 중...</span>
        </div>

        <!-- 에러 -->
        <div v-if="error" class="error-message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ error }}
        </div>
      </div>
    </div>

    <!-- 일정 추가/수정 모달 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="schedule-modal">
        <div class="schedule-modal-header">
          <span class="modal-title">{{ editingSchedule ? t('schedule.edit') : t('schedule.new') }}</span>
          <button class="modal-close" @click="closeModal">×</button>
        </div>

        <div class="schedule-modal-body">
          <div class="input-field title-field">
            <input
              type="text"
              v-model="formData.title"
              :placeholder="t('schedule.titlePlaceholder')"
              autofocus
            />
          </div>

          <div class="input-row">
            <div class="input-field date-field">
              <label>📅 {{ t('schedule.date') }}</label>
              <input type="date" v-model="formData.date" />
            </div>
          </div>

          <div class="input-row time-row">
            <div class="input-field">
              <label>🕐 {{ t('schedule.startTime') }}</label>
              <input type="time" v-model="formData.startTime" placeholder="--:--" />
            </div>
            <span class="time-divider">~</span>
            <div class="input-field">
              <label>🕐 {{ t('schedule.endTime') }}</label>
              <input type="time" v-model="formData.endTime" placeholder="--:--" />
            </div>
          </div>

          <div class="input-field memo-field">
            <label>📝 {{ t('schedule.memo') }}</label>
            <textarea
              v-model="formData.description"
              :placeholder="t('schedule.memoPlaceholder')"
              rows="2"
            ></textarea>
          </div>

          <div class="color-field">
            <label>{{ t('schedule.labelColor') }}</label>
            <div class="color-options">
              <button
                v-for="color in colorOptions"
                :key="color"
                class="color-dot"
                :class="{ active: formData.color === color }"
                :style="{ background: color }"
                @click="formData.color = color"
              ></button>
            </div>
          </div>
        </div>

        <div class="schedule-modal-footer">
          <button class="btn-cancel" @click="closeModal">{{ t('common.cancel') }}</button>
          <button
            class="btn-save"
            :disabled="!formData.title.trim()"
            @click="saveSchedule"
          >
            {{ editingSchedule ? t('common.edit') : t('common.save') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal-content delete-confirm">
        <div class="modal-header">
          <h3>{{ t('schedule.deleteConfirm') }}</h3>
        </div>
        <div class="modal-body">
          <p>{{ t('schedule.deleteQuestion') }}</p>
          <p class="delete-schedule-name">{{ deleteTarget?.title }}</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showDeleteConfirm = false">{{ t('common.cancel') }}</button>
          <button class="delete-confirm-btn" @click="executeDelete">{{ t('common.delete') }}</button>
        </div>
      </div>
    </div>

    <!-- AI 일정 추출 모달 -->
    <div v-if="showExtractModal" class="modal-overlay" @click.self="closeExtractModal">
      <div class="modal-content extract-modal">
        <div class="modal-header">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
            </svg>
            {{ t('aiExtract.title') }}
          </h3>
          <button class="close-btn" @click="closeExtractModal">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body extract-body">
          <!-- 입력 방식 선택 탭 -->
          <div class="extract-tabs">
            <button 
              class="extract-tab" 
              :class="{ active: extractInputMode === 'file' }"
              @click="extractInputMode = 'file'"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              {{ t('aiExtract.selectNote') }}
            </button>
            <button 
              class="extract-tab" 
              :class="{ active: extractInputMode === 'text' }"
              @click="extractInputMode = 'text'"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="17" y1="10" x2="3" y2="10"/>
                <line x1="21" y1="6" x2="3" y2="6"/>
                <line x1="21" y1="14" x2="3" y2="14"/>
                <line x1="17" y1="18" x2="3" y2="18"/>
              </svg>
              {{ t('aiExtract.directInput') }}
            </button>
          </div>

          <!-- 파일 선택 모드 -->
          <div v-if="extractInputMode === 'file'" class="file-select-section">
            <p class="extract-description">
              {{ t('aiExtract.selectDesc') }}
            </p>

            <!-- 파일 목록 -->
            <div class="file-list-container">
              <div class="file-search">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.3-4.3"/>
                </svg>
                <input 
                  type="text" 
                  v-model="fileSearchQuery"
                  :placeholder="t('aiExtract.searchNotes')"
                  class="file-search-input"
                />
              </div>
              
              <div class="file-list">
                <div
                  v-for="file in filteredVaultFiles"
                  :key="file"
                  class="file-item"
                  :class="{ selected: selectedFile === file }"
                  @click="selectFileForExtract(file)"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  <span class="file-name">{{ file.replace('.md', '') }}</span>
                  <svg v-if="selectedFile === file" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="check-icon">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
                <div v-if="filteredVaultFiles.length === 0" class="no-files">
                  <span>{{ fileSearchQuery ? t('aiExtract.noResults') : t('aiExtract.noNotes') }}</span>
                </div>
              </div>
            </div>

            <!-- 선택된 파일 미리보기 -->
            <div v-if="selectedFile && extractContent" class="file-preview">
              <div class="preview-header">
                <span>📄 {{ selectedFile.replace('.md', '') }}</span>
                <span class="preview-length">{{ extractContent.length }}자</span>
              </div>
              <div class="preview-content">
                {{ extractContent.slice(0, 300) }}{{ extractContent.length > 300 ? '...' : '' }}
              </div>
            </div>

            <!-- 파일 로딩 중 -->
            <div v-if="fileLoading" class="file-loading">
              <div class="spinner"></div>
              <span>{{ t('common.loading') }}</span>
            </div>
          </div>

          <!-- 직접 입력 모드 -->
          <div v-else class="text-input-section">
            <p class="extract-description">
              {{ t('aiExtract.inputDesc') }}
            </p>

            <div class="form-group">
              <textarea
                v-model="extractContent"
                :placeholder="t('aiExtract.inputPlaceholder')"
                class="form-textarea extract-textarea"
                rows="6"
              ></textarea>
            </div>
          </div>

          <!-- 추출된 일정 목록 -->
          <div v-if="extractedSchedules.length > 0" class="extracted-schedules">
            <div class="extracted-header">
              <h4>{{ t('aiExtract.extractedCount') }} ({{ extractedSchedules.length }})</h4>
              <span class="confidence-badge" :class="confidenceClass">
                {{ t('aiExtract.confidence') }} {{ Math.round(extractConfidence * 100) }}%
              </span>
            </div>
            <div class="extracted-list">
              <div
                v-for="(schedule, index) in extractedSchedules"
                :key="index"
                class="extracted-item"
                :style="{ '--item-color': schedule.color }"
              >
                <input
                  type="checkbox"
                  :id="`schedule-${index}`"
                  v-model="selectedExtracted"
                  :value="index"
                />
                <label :for="`schedule-${index}`" class="extracted-item-content">
                  <span class="item-title">{{ schedule.title }}</span>
                  <span class="item-meta">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/>
                      <line x1="8" y1="2" x2="8" y2="6"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    {{ schedule.date }}
                    <template v-if="schedule.startTime">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12 6 12 12 16 14"/>
                      </svg>
                      {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
                    </template>
                  </span>
                </label>
              </div>
            </div>
          </div>

          <!-- 추출 에러 -->
          <div v-if="extractError" class="extract-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ extractError }}
          </div>
        </div>

        <div class="modal-footer">
          <button class="cancel-btn" @click="closeExtractModal">{{ t('common.cancel') }}</button>
          <button
            v-if="extractedSchedules.length === 0"
            class="extract-btn"
            :disabled="!extractContent.trim() || extractLoading"
            @click="handleExtract"
          >
            <span v-if="extractLoading" class="spinner"></span>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
            </svg>
            {{ extractLoading ? t('aiExtract.extracting') : t('aiExtract.extractBtn') }}
          </button>
          <button
            v-else
            class="save-btn"
            :disabled="selectedExtracted.length === 0"
            @click="saveExtractedSchedules"
          >
            {{ t('aiExtract.addSelected') }} ({{ selectedExtracted.length }})
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useSchedule, useSettings, useVault, useI18n } from '../composables';
import type { ScheduleItem } from '../types';

const { t } = useI18n();

const CORE_BASE = 'http://127.0.0.1:8787';

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

const { settings } = useSettings();
const { vaultFiles } = useVault();

// 스크롤 컨테이너 ref
const calendarScrollRef = ref<HTMLElement | null>(null);
const monthRefs = ref<Record<string, HTMLElement | null>>({});

// 모달 상태
const showModal = ref(false);
const showDeleteConfirm = ref(false);
const showExtractModal = ref(false);
const editingSchedule = ref<ScheduleItem | null>(null);
const deleteTarget = ref<ScheduleItem | null>(null);

// AI 추출 상태
const extractInputMode = ref<'file' | 'text'>('file');
const extractContent = ref('');
const extractedSchedules = ref<ScheduleItem[]>([]);
const selectedExtracted = ref<number[]>([]);
const extractLoading = ref(false);
const extractError = ref('');
const extractConfidence = ref(0);

// 파일 선택 관련 상태
const selectedFile = ref<string | null>(null);
const fileSearchQuery = ref('');
const fileLoading = ref(false);

// 마크다운 파일 필터링
const filteredVaultFiles = computed(() => {
  const mdFiles = vaultFiles.value.filter(f => f.endsWith('.md'));
  if (!fileSearchQuery.value.trim()) {
    return mdFiles;
  }
  const query = fileSearchQuery.value.toLowerCase();
  return mdFiles.filter(f => f.toLowerCase().includes(query));
});

// 파일 선택 및 내용 로드
async function selectFileForExtract(filePath: string) {
  if (selectedFile.value === filePath) {
    // 이미 선택된 파일 클릭 시 선택 해제
    selectedFile.value = null;
    extractContent.value = '';
    return;
  }

  selectedFile.value = filePath;
  fileLoading.value = true;
  extractError.value = '';

  try {
    const res = await fetch(`${CORE_BASE}/vault/file?path=${encodeURIComponent(filePath)}`);
    if (res.ok) {
      const data = await res.json();
      extractContent.value = data.content || '';
    } else {
      extractError.value = '파일을 읽을 수 없습니다.';
      extractContent.value = '';
    }
  } catch (e) {
    extractError.value = '파일을 읽는 중 오류가 발생했습니다.';
    extractContent.value = '';
  } finally {
    fileLoading.value = false;
  }
}

// 신뢰도 클래스
const confidenceClass = computed(() => {
  if (extractConfidence.value >= 0.8) return 'high';
  if (extractConfidence.value >= 0.5) return 'medium';
  return 'low';
});

// 폼 데이터
const formData = ref({
  title: '',
  description: '',
  date: '',
  startTime: '',
  endTime: '',
  color: '#c9a76c',
});

// 색상 옵션
const colorOptions = [
  '#c9a76c', '#22c55e', '#3b82f6', '#8b5cf6',
  '#ec4899', '#f59e0b', '#ef4444', '#6b7280',
];

// 요일 (computed로 변경하여 언어 변경 시 반영)
const weekdays = computed(() => [
  t('days.sun'), t('days.mon'), t('days.tue'), t('days.wed'), 
  t('days.thu'), t('days.fri'), t('days.sat')
]);

// 선택된 날짜 라벨
const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return '';
  const [year, month, day] = selectedDate.value.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  const dayOfWeek = weekdays[date.getDay()];
  return `${month}월 ${day}일 (${dayOfWeek})`;
});

// 월 ref 설정
function setMonthRef(el: any, year: number, month: number) {
  if (el) {
    monthRefs.value[`${year}-${month}`] = el;
  }
}

// 오늘로 스크롤
function scrollToToday() {
  goToToday();
  nextTick(() => {
    const today = new Date();
    const key = `${today.getFullYear()}-${today.getMonth() + 1}`;
    const el = monthRefs.value[key];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
}

// 모달 열기/닫기
function openAddModal() {
  editingSchedule.value = null;
  // 항상 오늘 날짜를 기본값으로 설정
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  formData.value = {
    title: '',
    description: '',
    date: todayStr,
    startTime: '',
    endTime: '',
    color: '#c9a76c',
  };
  showModal.value = true;
}

function openEditModal(schedule: ScheduleItem) {
  editingSchedule.value = schedule;
  formData.value = {
    title: schedule.title,
    description: schedule.description,
    date: schedule.date,
    startTime: schedule.startTime,
    endTime: schedule.endTime,
    color: schedule.color,
  };
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingSchedule.value = null;
}

// 저장
async function saveSchedule() {
  if (!formData.value.title.trim()) return;

  if (editingSchedule.value) {
    await updateSchedule(editingSchedule.value.id, formData.value);
  } else {
    await createSchedule(formData.value);
  }
  closeModal();
}

// 삭제
function confirmDelete(schedule: ScheduleItem) {
  deleteTarget.value = schedule;
  showDeleteConfirm.value = true;
}

async function executeDelete() {
  if (deleteTarget.value) {
    await deleteSchedule(deleteTarget.value.id);
    showDeleteConfirm.value = false;
    deleteTarget.value = null;
  }
}

// AI 일정 추출
function closeExtractModal() {
  showExtractModal.value = false;
  extractInputMode.value = 'file';
  extractContent.value = '';
  extractedSchedules.value = [];
  selectedExtracted.value = [];
  extractError.value = '';
  extractConfidence.value = 0;
  selectedFile.value = null;
  fileSearchQuery.value = '';
}

async function handleExtract() {
  if (!extractContent.value.trim()) return;

  extractLoading.value = true;
  extractError.value = '';
  extractedSchedules.value = [];

  try {
    const result = await extractSchedulesFromNote(
      extractContent.value,
      settings.value.llm.provider,
      settings.value.llm.apiKey,
      settings.value.llm.model
    );

    extractedSchedules.value = result.schedules;
    extractConfidence.value = result.confidence;
    selectedExtracted.value = result.schedules.map((_, i) => i);

    if (result.schedules.length === 0) {
      extractError.value = '일정 정보를 찾을 수 없습니다. 다른 내용을 시도해보세요.';
    }
  } catch (e) {
    extractError.value = '일정 추출에 실패했습니다. 다시 시도해주세요.';
  } finally {
    extractLoading.value = false;
  }
}

async function saveExtractedSchedules() {
  if (selectedExtracted.value.length === 0) return;

  const schedulesToAdd = selectedExtracted.value.map(i => ({
    title: extractedSchedules.value[i].title,
    description: extractedSchedules.value[i].description || '',
    date: extractedSchedules.value[i].date,
    startTime: extractedSchedules.value[i].startTime || '',
    endTime: extractedSchedules.value[i].endTime || '',
    color: extractedSchedules.value[i].color || '#c9a76c',
  }));

  await createSchedulesBatch(schedulesToAdd);
  closeExtractModal();
}

// 초기화
onMounted(() => {
  init();
  nextTick(() => {
    scrollToToday();
  });
});
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');

.calendar-view {
  height: 100%;
  overflow: hidden;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  font-family: 'Pretendard Variable', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

/* 헤더 */
.calendar-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 32px 16px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.calendar-title-section h1 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: -0.02em;
}

.calendar-title-section p {
  color: var(--text-muted);
  font-size: 13px;
}

.calendar-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-default);
}

.today-btn:hover {
  color: #c9a76c;
  border-color: rgba(201, 167, 108, 0.3);
}

.ai-extract-btn {
  background: rgba(139, 92, 246, 0.1) !important;
  border-color: rgba(139, 92, 246, 0.2) !important;
  color: #a78bfa !important;
}

.ai-extract-btn:hover {
  background: rgba(139, 92, 246, 0.2) !important;
  border-color: rgba(139, 92, 246, 0.35) !important;
}

/* 본문 */
.calendar-body {
  display: grid;
  grid-template-columns: 1fr 340px;
  flex: 1;
  overflow: hidden;
}

/* 스크롤 캘린더 영역 */
.calendar-scroll {
  padding: 20px 32px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

/* 더보기 버튼 */
.load-more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed var(--border-subtle);
  border-radius: 10px;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.load-more-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-default);
  color: var(--text-secondary);
}

.load-more-btn:last-child {
  margin-bottom: 0;
  margin-top: 20px;
}

/* 월 섹션 */
.month-section {
  margin-bottom: 32px;
}

.month-section:last-of-type {
  margin-bottom: 0;
}

.month-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.month-header h2 {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

/* 요일 헤더 */
.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 6px;
}

.weekday {
  padding: 8px 0;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
}

.weekday:first-child {
  color: #ef4444;
}

.weekday:last-child {
  color: #3b82f6;
}

/* 일요일/토요일 날짜 색상 */
.calendar-day.sunday .day-number {
  color: #ef4444;
}

.calendar-day.saturday .day-number {
  color: #3b82f6;
}

/* 달력 그리드 */
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1.2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 6px 4px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.calendar-day:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-subtle);
}

.calendar-day.other-month {
  opacity: 0.3;
}

.calendar-day.today {
  background: rgba(201, 167, 108, 0.12);
  border-color: rgba(201, 167, 108, 0.35);
}

.calendar-day.today .day-number {
  color: #c9a76c;
  font-weight: 700;
}

.calendar-day.selected {
  background: rgba(201, 167, 108, 0.22);
  border-color: #c9a76c;
}

.calendar-day.has-schedules {
  background: rgba(255, 255, 255, 0.04);
}

.day-number {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.calendar-day.other-month .day-number {
  color: var(--text-muted);
}

.schedule-indicator {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 9px;
}

.schedule-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: rgba(201, 167, 108, 0.3);
  border-radius: 8px;
  color: #e8d5b7;
  font-weight: 600;
}

.completed-badge {
  color: #22c55e;
  font-weight: 600;
}

/* 일정 패널 */
.schedule-panel {
  border-left: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.01);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.panel-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.add-schedule-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 12px;
  background: rgba(201, 167, 108, 0.12);
  border: 1px solid rgba(201, 167, 108, 0.25);
  border-radius: 7px;
  color: #e8d5b7;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-schedule-btn:hover {
  background: rgba(201, 167, 108, 0.2);
  border-color: rgba(201, 167, 108, 0.35);
}

/* 일정 목록 - 심플 디자인 */
.schedule-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.12s ease;
}

.schedule-item:last-child {
  border-bottom: none;
}

.schedule-item:hover {
  background: rgba(255, 255, 255, 0.02);
  margin: 0 -16px;
  padding: 14px 16px;
  border-radius: 8px;
}

.schedule-item.completed .schedule-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.schedule-color-dot {
  width: 4px;
  height: 32px;
  border-radius: 2px;
  flex-shrink: 0;
}

.schedule-main {
  flex: 1;
  min-width: 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.schedule-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.schedule-time {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
}

.schedule-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.schedule-item:hover .schedule-actions {
  opacity: 1;
}

.check-btn,
.more-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s ease;
}

.check-btn:hover {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.more-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.schedule-item.completed .check-btn {
  color: #22c55e;
  opacity: 1;
}

.schedule-item.completed .schedule-actions {
  opacity: 1;
}

/* 빈 상태 - 미니멀 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  text-align: center;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 16px;
  font-weight: 400;
}

.add-first-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px dashed var(--border-default);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.add-first-btn:hover {
  background: rgba(201, 167, 108, 0.08);
  border-color: rgba(201, 167, 108, 0.4);
  color: #c9a76c;
}

/* 로딩 */
.loading-schedules {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 20px;
  color: var(--text-muted);
  font-size: 13px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(201, 167, 108, 0.2);
  border-top-color: #c9a76c;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 에러 */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  margin: 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #ef4444;
  font-size: 12px;
}

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
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

/* 새 일정 모달 - 클린 디자인 */
.schedule-modal {
  width: 380px;
  max-width: 90vw;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 16px;
  overflow: hidden;
  animation: modalIn 0.2s ease;
  font-family: 'Pretendard Variable', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

@keyframes modalIn {
  from { 
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.schedule-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.modal-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.12s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
}

.schedule-modal-body {
  padding: 20px;
}

.input-field {
  margin-bottom: 16px;
}

.input-field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.title-field input {
  width: 100%;
  padding: 14px 0;
  background: none;
  border: none;
  border-bottom: 2px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 500;
  font-family: inherit;
  letter-spacing: -0.02em;
  transition: border-color 0.15s ease;
}

.title-field input:focus {
  outline: none;
  border-bottom-color: #c9a76c;
}

.title-field input::placeholder {
  color: var(--text-muted);
  font-weight: 400;
}

.input-row {
  display: flex;
  gap: 12px;
}

.date-field {
  flex: 1;
}

.date-field input,
.time-row .input-field input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.12s ease;
}

.date-field input:focus,
.time-row .input-field input:focus {
  outline: none;
  border-color: rgba(201, 167, 108, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.time-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 16px;
}

.time-row .input-field {
  flex: 1;
  margin-bottom: 0;
}

.time-divider {
  color: var(--text-muted);
  padding-bottom: 12px;
  font-size: 14px;
}

.memo-field textarea {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: none;
  transition: all 0.12s ease;
  line-height: 1.5;
}

.memo-field textarea:focus {
  outline: none;
  border-color: rgba(201, 167, 108, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.memo-field textarea::placeholder {
  color: var(--text-muted);
}

.color-field {
  margin-top: 4px;
}

.color-field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.color-options {
  display: flex;
  gap: 8px;
}

.color-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.12s ease;
}

.color-dot:hover {
  transform: scale(1.15);
}

.color-dot.active {
  border-color: white;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.15);
}

.schedule-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.01);
}

.btn-cancel,
.btn-save {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.12s ease;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--border-default);
}

.btn-save {
  background: #c9a76c;
  border: none;
  color: #1a1a1a;
}

.btn-save:hover:not(:disabled) {
  background: #d4b67d;
}

.btn-save:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 기존 모달 스타일 (삭제 확인, AI 추출용) */
.modal-content {
  width: 420px;
  max-width: 90vw;
  max-height: 90vh;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 14px;
  overflow: hidden;
  animation: modalIn 0.2s ease;
  font-family: 'Pretendard Variable', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

.modal-content.delete-confirm {
  width: 340px;
}

.modal-content.extract-modal {
  width: 500px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 22px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.modal-body {
  padding: 22px;
}

.extract-body {
  max-height: 55vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 7px;
}

.required {
  color: #ef4444;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 9px 13px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  transition: all 0.15s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: rgba(201, 167, 108, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.form-textarea {
  resize: vertical;
  min-height: 70px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.color-picker {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
}

.color-option {
  width: 26px;
  height: 26px;
  border: 2px solid transparent;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.15s ease;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.selected {
  border-color: white;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 22px;
  border-top: 1px solid var(--border-subtle);
}

.cancel-btn,
.save-btn,
.delete-confirm-btn,
.extract-btn {
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-default);
}

.save-btn {
  background: rgba(201, 167, 108, 0.2);
  border: 1px solid rgba(201, 167, 108, 0.3);
  color: #e8d5b7;
}

.save-btn:hover:not(:disabled) {
  background: rgba(201, 167, 108, 0.3);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-confirm-btn {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.delete-confirm-btn:hover {
  background: rgba(239, 68, 68, 0.3);
}

.delete-schedule-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 8px;
}

.extract-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

.extract-btn:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.3);
}

.extract-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.extract-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
}

.extract-textarea {
  min-height: 110px;
}

/* 추출 탭 */
.extract-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.extract-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.extract-tab:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}

.extract-tab.active {
  background: rgba(139, 92, 246, 0.12);
  border-color: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

/* 파일 선택 섹션 */
.file-select-section,
.text-input-section {
  animation: fadeIn 0.15s ease;
}

.file-list-container {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 14px;
}

.file-search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.02);
}

.file-search svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.file-search-input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.file-search-input::placeholder {
  color: var(--text-muted);
}

.file-list {
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.12s ease;
  border-bottom: 1px solid var(--border-subtle);
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.file-item.selected {
  background: rgba(139, 92, 246, 0.1);
}

.file-item svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.file-item.selected svg {
  color: #a78bfa;
}

.file-item .file-name {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-item .check-icon {
  color: #a78bfa;
}

.no-files {
  padding: 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

/* 파일 미리보기 */
.file-preview {
  background: rgba(139, 92, 246, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 10px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(139, 92, 246, 0.1);
  border-bottom: 1px solid rgba(139, 92, 246, 0.15);
  font-size: 12px;
  font-weight: 600;
  color: #a78bfa;
}

.preview-length {
  font-weight: 400;
  color: var(--text-muted);
}

.preview-content {
  padding: 12px 14px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 파일 로딩 */
.file-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px;
  color: var(--text-muted);
  font-size: 13px;
}

/* 추출된 일정 목록 */
.extracted-schedules {
  margin-top: 18px;
  background: rgba(139, 92, 246, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 10px;
  overflow: hidden;
}

.extracted-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 14px;
  background: rgba(139, 92, 246, 0.1);
  border-bottom: 1px solid rgba(139, 92, 246, 0.15);
}

.extracted-header h4 {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #a78bfa;
}

.confidence-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 7px;
  border-radius: 8px;
}

.confidence-badge.high {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.confidence-badge.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.confidence-badge.low {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.extracted-list {
  padding: 8px;
}

.extracted-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px;
  border-radius: 7px;
  transition: background 0.15s ease;
}

.extracted-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.extracted-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-top: 2px;
  accent-color: #8b5cf6;
}

.extracted-item-content {
  flex: 1;
  cursor: pointer;
}

.extracted-item .item-title {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 3px;
}

.extracted-item .item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-muted);
}

.extracted-item .item-meta svg {
  opacity: 0.7;
}

.extract-error {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 14px;
  padding: 11px 13px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: #ef4444;
}

.extract-error svg {
  flex-shrink: 0;
  margin-top: 1px;
}

/* 반응형 */
@media (max-width: 900px) {
  .calendar-body {
    grid-template-columns: 1fr;
  }

  .schedule-panel {
    border-left: none;
    border-top: 1px solid var(--border-subtle);
    max-height: 350px;
  }
}

/* ============================================
   테마별 스타일 - 라이트 모드 가독성 향상
   ============================================ */

/* Light Theme */
:global([data-theme="light"]) .calendar-day {
  background: rgba(0, 0, 0, 0.02);
}

:global([data-theme="light"]) .calendar-day:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
}

:global([data-theme="light"]) .calendar-day.today {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

:global([data-theme="light"]) .calendar-day.today .day-number {
  color: #2563eb;
}

:global([data-theme="light"]) .calendar-day.selected {
  background: rgba(59, 130, 246, 0.12);
  border-color: #3b82f6;
}

:global([data-theme="light"]) .calendar-day.has-schedules {
  background: rgba(0, 0, 0, 0.03);
}

:global([data-theme="light"]) .schedule-count {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}

:global([data-theme="light"]) .completed-badge {
  color: #16a34a;
}

:global([data-theme="light"]) .schedule-panel {
  background: rgba(0, 0, 0, 0.01);
}

:global([data-theme="light"]) .add-schedule-btn {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
  color: #2563eb;
}

:global([data-theme="light"]) .add-schedule-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
}

:global([data-theme="light"]) .schedule-item {
  border-bottom-color: rgba(0, 0, 0, 0.06);
}

:global([data-theme="light"]) .schedule-item:hover {
  background: rgba(0, 0, 0, 0.02);
}

:global([data-theme="light"]) .schedule-title {
  color: #1f2937;
}

:global([data-theme="light"]) .schedule-time {
  color: #6b7280;
}

:global([data-theme="light"]) .check-btn:hover {
  background: rgba(22, 163, 74, 0.1);
  color: #16a34a;
}

:global([data-theme="light"]) .schedule-item.completed .check-btn {
  color: #16a34a;
}

:global([data-theme="light"]) .more-btn:hover {
  background: rgba(220, 38, 38, 0.08);
  color: #dc2626;
}

:global([data-theme="light"]) .add-first-btn {
  border-color: rgba(0, 0, 0, 0.15);
  color: #6b7280;
}

:global([data-theme="light"]) .add-first-btn:hover {
  background: rgba(59, 130, 246, 0.05);
  border-color: rgba(59, 130, 246, 0.3);
  color: #2563eb;
}

:global([data-theme="light"]) .action-btn {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.1);
  color: #4b5563;
}

:global([data-theme="light"]) .action-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.15);
}

:global([data-theme="light"]) .today-btn:hover {
  color: #2563eb;
  border-color: rgba(59, 130, 246, 0.3);
}

:global([data-theme="light"]) .ai-extract-btn {
  background: rgba(139, 92, 246, 0.08) !important;
  border-color: rgba(139, 92, 246, 0.2) !important;
  color: #7c3aed !important;
}

:global([data-theme="light"]) .ai-extract-btn:hover {
  background: rgba(139, 92, 246, 0.12) !important;
}

:global([data-theme="light"]) .load-more-btn {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
  color: #6b7280;
}

:global([data-theme="light"]) .load-more-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.15);
  color: #374151;
}

/* Light 모달 스타일 */
:global([data-theme="light"]) .schedule-modal,
:global([data-theme="light"]) .modal-content {
  background: #ffffff;
  border-color: rgba(0, 0, 0, 0.1);
}

:global([data-theme="light"]) .schedule-modal-header,
:global([data-theme="light"]) .modal-header {
  border-bottom-color: rgba(0, 0, 0, 0.08);
}

:global([data-theme="light"]) .modal-title,
:global([data-theme="light"]) .modal-header h3 {
  color: #1f2937;
}

:global([data-theme="light"]) .title-field input {
  color: #1f2937;
  border-bottom-color: rgba(0, 0, 0, 0.1);
}

:global([data-theme="light"]) .title-field input:focus {
  border-bottom-color: #3b82f6;
}

:global([data-theme="light"]) .date-field input,
:global([data-theme="light"]) .time-row .input-field input,
:global([data-theme="light"]) .memo-field textarea,
:global([data-theme="light"]) .form-input,
:global([data-theme="light"]) .form-textarea {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
  color: #1f2937;
}

:global([data-theme="light"]) .date-field input:focus,
:global([data-theme="light"]) .time-row .input-field input:focus,
:global([data-theme="light"]) .memo-field textarea:focus,
:global([data-theme="light"]) .form-input:focus,
:global([data-theme="light"]) .form-textarea:focus {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.02);
}

:global([data-theme="light"]) .btn-save {
  background: #3b82f6;
  color: #ffffff;
}

:global([data-theme="light"]) .btn-save:hover:not(:disabled) {
  background: #2563eb;
}

:global([data-theme="light"]) .schedule-modal-footer,
:global([data-theme="light"]) .modal-footer {
  border-top-color: rgba(0, 0, 0, 0.08);
  background: rgba(0, 0, 0, 0.01);
}

/* Sepia Theme - 따뜻한 톤 */
:global([data-theme="sepia"]) .calendar-day {
  background: rgba(92, 75, 55, 0.02);
}

:global([data-theme="sepia"]) .calendar-day:hover {
  background: rgba(92, 75, 55, 0.05);
  border-color: rgba(92, 75, 55, 0.12);
}

:global([data-theme="sepia"]) .calendar-day.today {
  background: rgba(146, 115, 75, 0.1);
  border-color: rgba(146, 115, 75, 0.35);
}

:global([data-theme="sepia"]) .calendar-day.today .day-number {
  color: #7a5a30;
}

:global([data-theme="sepia"]) .calendar-day.selected {
  background: rgba(146, 115, 75, 0.15);
  border-color: #92734b;
}

:global([data-theme="sepia"]) .schedule-count {
  background: rgba(146, 115, 75, 0.2);
  color: #5c4b37;
}

:global([data-theme="sepia"]) .add-schedule-btn {
  background: rgba(146, 115, 75, 0.1);
  border-color: rgba(146, 115, 75, 0.25);
  color: #6b5d4d;
}

:global([data-theme="sepia"]) .add-schedule-btn:hover {
  background: rgba(146, 115, 75, 0.18);
}

:global([data-theme="sepia"]) .schedule-title {
  color: #3d3327;
}

:global([data-theme="sepia"]) .add-first-btn:hover {
  background: rgba(146, 115, 75, 0.08);
  border-color: rgba(146, 115, 75, 0.3);
  color: #5c4b37;
}

:global([data-theme="sepia"]) .action-btn {
  background: rgba(92, 75, 55, 0.03);
  border-color: rgba(92, 75, 55, 0.12);
  color: #6b5d4d;
}

:global([data-theme="sepia"]) .today-btn:hover {
  color: #7a5a30;
  border-color: rgba(146, 115, 75, 0.35);
}

:global([data-theme="sepia"]) .schedule-modal,
:global([data-theme="sepia"]) .modal-content {
  background: #fffcf5;
  border-color: rgba(92, 75, 55, 0.15);
}

:global([data-theme="sepia"]) .title-field input {
  color: #3d3327;
}

:global([data-theme="sepia"]) .title-field input:focus {
  border-bottom-color: #92734b;
}

:global([data-theme="sepia"]) .btn-save {
  background: #92734b;
  color: #fffcf5;
}

:global([data-theme="sepia"]) .btn-save:hover:not(:disabled) {
  background: #7a5a30;
}

/* GitHub Dark Theme - 블루 액센트 */
:global([data-theme="github-dark"]) .calendar-day.today {
  background: rgba(88, 166, 255, 0.1);
  border-color: rgba(88, 166, 255, 0.35);
}

:global([data-theme="github-dark"]) .calendar-day.today .day-number {
  color: #58a6ff;
}

:global([data-theme="github-dark"]) .calendar-day.selected {
  background: rgba(88, 166, 255, 0.15);
  border-color: #58a6ff;
}

:global([data-theme="github-dark"]) .schedule-count {
  background: rgba(88, 166, 255, 0.2);
  color: #79c0ff;
}

:global([data-theme="github-dark"]) .add-schedule-btn {
  background: rgba(88, 166, 255, 0.1);
  border-color: rgba(88, 166, 255, 0.25);
  color: #58a6ff;
}

:global([data-theme="github-dark"]) .add-schedule-btn:hover {
  background: rgba(88, 166, 255, 0.18);
}

:global([data-theme="github-dark"]) .today-btn:hover {
  color: #58a6ff;
  border-color: rgba(88, 166, 255, 0.35);
}

:global([data-theme="github-dark"]) .add-first-btn:hover {
  background: rgba(88, 166, 255, 0.08);
  border-color: rgba(88, 166, 255, 0.3);
  color: #58a6ff;
}

:global([data-theme="github-dark"]) .btn-save {
  background: #238636;
  color: #ffffff;
}

:global([data-theme="github-dark"]) .btn-save:hover:not(:disabled) {
  background: #2ea043;
}

/* Dim Theme - 중간 톤 */
:global([data-theme="dim"]) .calendar-day.today {
  background: rgba(139, 148, 158, 0.12);
  border-color: rgba(139, 148, 158, 0.35);
}

:global([data-theme="dim"]) .calendar-day.today .day-number {
  color: #adbac7;
}

:global([data-theme="dim"]) .calendar-day.selected {
  background: rgba(139, 148, 158, 0.18);
  border-color: #8b949e;
}

:global([data-theme="dim"]) .schedule-count {
  background: rgba(139, 148, 158, 0.25);
  color: #c9d1d9;
}

:global([data-theme="dim"]) .add-schedule-btn {
  background: rgba(139, 148, 158, 0.1);
  border-color: rgba(139, 148, 158, 0.25);
  color: #adbac7;
}

:global([data-theme="dim"]) .add-first-btn:hover {
  background: rgba(139, 148, 158, 0.1);
  border-color: rgba(139, 148, 158, 0.35);
  color: #adbac7;
}

/* Light/Sepia 테마에서 일요일/토요일 색상 조정 */
:global([data-theme="light"]) .calendar-day.sunday .day-number,
:global([data-theme="sepia"]) .calendar-day.sunday .day-number {
  color: #dc2626;
}

:global([data-theme="light"]) .calendar-day.saturday .day-number,
:global([data-theme="sepia"]) .calendar-day.saturday .day-number {
  color: #2563eb;
}

:global([data-theme="light"]) .weekday:first-child,
:global([data-theme="sepia"]) .weekday:first-child {
  color: #dc2626;
}

:global([data-theme="light"]) .weekday:last-child,
:global([data-theme="sepia"]) .weekday:last-child {
  color: #2563eb;
}

/* Light 테마 AI 추출 모달 */
:global([data-theme="light"]) .extract-tab {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.08);
  color: #6b7280;
}

:global([data-theme="light"]) .extract-tab:hover {
  background: rgba(0, 0, 0, 0.04);
  color: #374151;
}

:global([data-theme="light"]) .extract-tab.active {
  background: rgba(139, 92, 246, 0.08);
  border-color: rgba(139, 92, 246, 0.25);
  color: #7c3aed;
}

:global([data-theme="light"]) .file-list-container {
  background: rgba(0, 0, 0, 0.01);
  border-color: rgba(0, 0, 0, 0.08);
}

:global([data-theme="light"]) .file-item {
  border-bottom-color: rgba(0, 0, 0, 0.06);
}

:global([data-theme="light"]) .file-item:hover {
  background: rgba(0, 0, 0, 0.03);
}

:global([data-theme="light"]) .file-item.selected {
  background: rgba(139, 92, 246, 0.06);
}

:global([data-theme="light"]) .file-item .file-name {
  color: #1f2937;
}

:global([data-theme="light"]) .file-preview {
  background: rgba(139, 92, 246, 0.03);
  border-color: rgba(139, 92, 246, 0.12);
}

:global([data-theme="light"]) .preview-header {
  background: rgba(139, 92, 246, 0.06);
  border-bottom-color: rgba(139, 92, 246, 0.1);
  color: #7c3aed;
}

:global([data-theme="light"]) .preview-content {
  color: #4b5563;
}

:global([data-theme="light"]) .extracted-schedules {
  background: rgba(139, 92, 246, 0.03);
  border-color: rgba(139, 92, 246, 0.12);
}

:global([data-theme="light"]) .extracted-header {
  background: rgba(139, 92, 246, 0.06);
  border-bottom-color: rgba(139, 92, 246, 0.1);
}

:global([data-theme="light"]) .extracted-header h4 {
  color: #7c3aed;
}

:global([data-theme="light"]) .extracted-item .item-title {
  color: #1f2937;
}

:global([data-theme="light"]) .extract-btn {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.25);
  color: #7c3aed;
}

:global([data-theme="light"]) .extract-btn:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.18);
}

:global([data-theme="light"]) .delete-confirm-btn {
  background: rgba(220, 38, 38, 0.1);
  border-color: rgba(220, 38, 38, 0.2);
  color: #dc2626;
}

:global([data-theme="light"]) .delete-confirm-btn:hover {
  background: rgba(220, 38, 38, 0.18);
}
</style>
