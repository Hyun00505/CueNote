<template>
  <div
    v-if="visible"
    class="modal-overlay"
    @click.self="emit('close')"
  >
    <div class="schedule-modal">
      <div class="schedule-modal-header">
        <span class="modal-title">{{ isEdit ? t('schedule.edit') : t('schedule.new') }}</span>
        <button
          class="modal-close"
          @click="emit('close')"
        >
          ×
        </button>
      </div>

      <div class="schedule-modal-body">
        <div class="input-field title-field">
          <input
            v-model="form.title"
            type="text"
            :placeholder="t('schedule.titlePlaceholder')"
            autofocus
          >
        </div>

        <div class="input-row">
          <div class="input-field date-field">
            <label>📅 {{ t('schedule.date') }}</label>
            <input
              v-model="form.date"
              type="date"
            >
          </div>
        </div>

        <!-- 종일 체크박스 -->
        <div class="allday-toggle">
          <label class="allday-checkbox">
            <input
              v-model="form.isAllDay"
              type="checkbox"
            >
            <span class="checkbox-custom" />
            <span class="checkbox-label">{{ t('calendar.allDay') }}</span>
          </label>
        </div>

        <!-- 시간 입력 (종일이 아닐 때만) -->
        <div
          v-if="!form.isAllDay"
          class="time-section"
        >
          <!-- 빠른 시간 선택 버튼 (상단) -->
          <div class="quick-times">
            <button 
              v-for="preset in timePresets" 
              :key="preset.label"
              type="button"
              class="quick-time-btn"
              :class="{ active: isPresetActive(preset) }"
              @click="applyPreset(preset)"
            >
              {{ preset.label }}
            </button>
          </div>

          <div class="time-inputs">
            <div class="time-input-group start">
              <div class="time-label">
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
                  <polyline points="12 6 12 12 16 14" />
                </svg>
                <span>{{ t('schedule.startTime') }}</span>
              </div>
              <div class="time-picker">
                <select
                  v-model="startHour"
                  class="time-select hour-select"
                >
                  <option value="">
                    {{ currentLanguage === 'ko' ? '시' : 'Hour' }}
                  </option>
                  <option
                    v-for="h in 24"
                    :key="h-1"
                    :value="String(h-1).padStart(2, '0')"
                  >
                    {{ formatHourOption(h-1) }}
                  </option>
                </select>
                <select
                  v-model="startMinute"
                  class="time-select minute-select"
                >
                  <option value="">
                    {{ currentLanguage === 'ko' ? '분' : 'Min' }}
                  </option>
                  <option
                    v-for="m in minuteOptions"
                    :key="m"
                    :value="m"
                  >
                    {{ m }}{{ currentLanguage === 'ko' ? '분' : '' }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="time-connector">
              <div class="connector-line" />
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line
                  x1="5"
                  y1="12"
                  x2="19"
                  y2="12"
                />
                <polyline points="12 5 19 12 12 19" />
              </svg>
              <div class="connector-line" />
            </div>
            
            <div class="time-input-group end">
              <div class="time-label">
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
                  <polyline points="12 6 12 12 8 14" />
                </svg>
                <span>{{ t('schedule.endTime') }}</span>
              </div>
              <div class="time-picker">
                <select
                  v-model="endHour"
                  class="time-select hour-select"
                  :disabled="!startHour"
                >
                  <option value="">
                    {{ currentLanguage === 'ko' ? '시' : 'Hour' }}
                  </option>
                  <option 
                    v-for="h in 24" 
                    :key="h-1" 
                    :value="String(h-1).padStart(2, '0')"
                    :disabled="isEndHourDisabled(h-1)"
                  >
                    {{ formatHourOption(h-1) }}
                  </option>
                </select>
                <select
                  v-model="endMinute"
                  class="time-select minute-select"
                  :disabled="!endHour"
                >
                  <option value="">
                    {{ currentLanguage === 'ko' ? '분' : 'Min' }}
                  </option>
                  <option 
                    v-for="m in minuteOptions" 
                    :key="m" 
                    :value="m"
                    :disabled="isEndMinuteDisabled(m)"
                  >
                    {{ m }}{{ currentLanguage === 'ko' ? '분' : '' }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- 선택된 시간 요약 -->
          <div
            v-if="form.startTime && form.endTime"
            class="time-summary"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
              <path d="M12 6v6l4 2" />
            </svg>
            <span>{{ formatTimeSummary() }}</span>
          </div>
        </div>

        <div class="input-field memo-field">
          <label>📝 {{ t('schedule.memo') }}</label>
          <textarea
            v-model="form.description"
            :placeholder="t('schedule.memoPlaceholder')"
            rows="2"
          />
        </div>

        <div class="color-field">
          <label>{{ t('schedule.labelColor') }}</label>
          <div class="color-options">
            <button
              v-for="color in colorOptions"
              :key="color"
              class="color-dot"
              :class="{ active: form.color === color }"
              :style="{ background: color }"
              @click="form.color = color"
            />
          </div>
        </div>
      </div>

      <div class="schedule-modal-footer">
        <button
          class="btn-cancel"
          @click="emit('close')"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          class="btn-save"
          :disabled="!form.title.trim()"
          @click="handleSave"
        >
          {{ isEdit ? t('common.edit') : t('common.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useI18n } from '../../composables';
import type { ScheduleItem } from '../../types';

const props = defineProps<{
  visible: boolean;
  editingSchedule: ScheduleItem | null;
  selectedDate: string | null;
}>();

const emit = defineEmits<{
  'close': [];
  'save': [data: { title: string; description: string; date: string; startTime: string; endTime: string; color: string }];
}>();

const { t, currentLanguage } = useI18n();

const colorOptions = [
  '#c9a76c', '#22c55e', '#3b82f6', '#8b5cf6',
  '#ec4899', '#f59e0b', '#ef4444', '#6b7280',
];

const minuteOptions = ['00', '15', '30', '45'];

const timePresets = computed(() => {
  const isKo = currentLanguage.value === 'ko';
  return [
    { label: isKo ? '오전' : 'Morning', start: '09:00', end: '12:00' },
    { label: isKo ? '오후' : 'Afternoon', start: '13:00', end: '18:00' },
    { label: isKo ? '저녁' : 'Evening', start: '18:00', end: '21:00' },
    { label: isKo ? '1시간' : '1 Hour', start: '', end: '', duration: 60 },
    { label: isKo ? '2시간' : '2 Hours', start: '', end: '', duration: 120 },
  ];
});

const isEdit = ref(false);

const form = ref({
  title: '',
  description: '',
  date: '',
  startTime: '',
  endTime: '',
  color: '#c9a76c',
  isAllDay: false,
});

// 시간/분 분리 관리
const startHour = ref('');
const startMinute = ref('');
const endHour = ref('');
const endMinute = ref('');

// 시간 옵션 포맷 (오전/오후 표시)
function formatHourOption(hour: number): string {
  const isKo = currentLanguage.value === 'ko';
  if (isKo) {
    if (hour === 0) return '오전 12시';
    if (hour < 12) return `오전 ${hour}시`;
    if (hour === 12) return '오후 12시';
    return `오후 ${hour - 12}시`;
  } else {
    if (hour === 0) return '12 AM';
    if (hour < 12) return `${hour} AM`;
    if (hour === 12) return '12 PM';
    return `${hour - 12} PM`;
  }
}

// 시간 문자열에서 시/분 분리
function parseTime(time: string) {
  if (!time) return { hour: '', minute: '' };
  const [h, m] = time.split(':');
  return { hour: h || '', minute: m || '' };
}

// 시/분을 시간 문자열로 합성
function buildTime(hour: string, minute: string): string {
  if (!hour) return '';
  return `${hour}:${minute || '00'}`;
}

// 시간 변경 감지 - 시작 시간 변경 시 종료 시간도 자동 설정
watch([startHour, startMinute], ([newHour, newMinute], [oldHour, oldMinute]) => {
  form.value.startTime = buildTime(startHour.value, startMinute.value);
  
  // 시작 시간이 새로 설정되면 종료 시간도 같이 설정 (1시간 후)
  if (newHour && (!endHour.value || (oldHour !== newHour))) {
    const startH = parseInt(newHour);
    const startM = parseInt(newMinute || '00');
    const endTotalMinutes = startH * 60 + startM + 60; // 1시간 후
    const endH = Math.floor(endTotalMinutes / 60) % 24;
    const endM = endTotalMinutes % 60;
    
    endHour.value = String(endH).padStart(2, '0');
    endMinute.value = String(endM).padStart(2, '0');
  }
  
  // 종료 시간이 시작 시간보다 앞이면 조정
  if (startHour.value && endHour.value) {
    const startTotal = parseInt(startHour.value) * 60 + parseInt(startMinute.value || '00');
    const endTotal = parseInt(endHour.value) * 60 + parseInt(endMinute.value || '00');
    if (endTotal <= startTotal) {
      const newEndTotal = startTotal + 60;
      endHour.value = String(Math.floor(newEndTotal / 60) % 24).padStart(2, '0');
      endMinute.value = String(newEndTotal % 60).padStart(2, '0');
    }
  }
});

watch([endHour, endMinute], () => {
  form.value.endTime = buildTime(endHour.value, endMinute.value);
});

// 종료 시간 선택 제한 - 시작 시간보다 앞 시간은 비활성화
function isEndHourDisabled(hour: number): boolean {
  if (!startHour.value) return false;
  const startH = parseInt(startHour.value);
  return hour < startH;
}

function isEndMinuteDisabled(minute: string): boolean {
  if (!startHour.value || !endHour.value) return false;
  const startH = parseInt(startHour.value);
  const startM = parseInt(startMinute.value || '00');
  const endH = parseInt(endHour.value);
  const m = parseInt(minute);
  
  // 같은 시간대면 시작 분보다 작거나 같은 분은 비활성화
  if (endH === startH) {
    return m <= startM;
  }
  return false;
}

// 시간 요약 텍스트
function formatTimeSummary(): string {
  if (!form.value.startTime || !form.value.endTime) return '';
  
  const startTotal = parseInt(startHour.value) * 60 + parseInt(startMinute.value || '00');
  const endTotal = parseInt(endHour.value) * 60 + parseInt(endMinute.value || '00');
  const durationMin = endTotal - startTotal;
  
  const hours = Math.floor(durationMin / 60);
  const mins = durationMin % 60;
  
  const isKo = currentLanguage.value === 'ko';
  
  let durationStr = '';
  if (hours > 0 && mins > 0) {
    durationStr = isKo ? `${hours}시간 ${mins}분` : `${hours}h ${mins}m`;
  } else if (hours > 0) {
    durationStr = isKo ? `${hours}시간` : `${hours} hour${hours > 1 ? 's' : ''}`;
  } else {
    durationStr = isKo ? `${mins}분` : `${mins} min`;
  }
  
  return isKo 
    ? `총 ${durationStr} 동안` 
    : `Duration: ${durationStr}`;
}

// 종일 토글 시 시간 초기화
watch(() => form.value.isAllDay, (isAllDay) => {
  if (isAllDay) {
    form.value.startTime = '';
    form.value.endTime = '';
    startHour.value = '';
    startMinute.value = '';
    endHour.value = '';
    endMinute.value = '';
  }
});

// 빠른 시간 프리셋 적용
function applyPreset(preset: { start: string; end: string; duration?: number }) {
  if (preset.duration) {
    // 현재 시작 시간 기준으로 duration 계산
    const now = new Date();
    const currentHour = startHour.value ? parseInt(startHour.value) : now.getHours();
    const currentMinute = startMinute.value ? parseInt(startMinute.value) : 0;
    
    startHour.value = String(currentHour).padStart(2, '0');
    startMinute.value = String(currentMinute).padStart(2, '0');
    
    const endTotalMinutes = currentHour * 60 + currentMinute + preset.duration;
    const endH = Math.floor(endTotalMinutes / 60) % 24;
    const endM = endTotalMinutes % 60;
    
    endHour.value = String(endH).padStart(2, '0');
    endMinute.value = String(endM).padStart(2, '0');
  } else {
    const start = parseTime(preset.start);
    const end = parseTime(preset.end);
    
    startHour.value = start.hour;
    startMinute.value = start.minute;
    endHour.value = end.hour;
    endMinute.value = end.minute;
  }
}

// 프리셋이 현재 선택과 일치하는지
function isPresetActive(preset: { start: string; end: string; duration?: number }): boolean {
  if (preset.duration) return false;
  return form.value.startTime === preset.start && form.value.endTime === preset.end;
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    if (props.editingSchedule) {
      isEdit.value = true;
      const hasTime = !!props.editingSchedule.startTime;
      form.value = {
        title: props.editingSchedule.title,
        description: props.editingSchedule.description,
        date: props.editingSchedule.date,
        startTime: props.editingSchedule.startTime,
        endTime: props.editingSchedule.endTime,
        color: props.editingSchedule.color,
        isAllDay: !hasTime,
      };
      
      // 시간 분리
      const start = parseTime(props.editingSchedule.startTime);
      const end = parseTime(props.editingSchedule.endTime);
      startHour.value = start.hour;
      startMinute.value = start.minute;
      endHour.value = end.hour;
      endMinute.value = end.minute;
    } else {
      isEdit.value = false;
      let defaultDate = props.selectedDate;
      if (!defaultDate) {
        const today = new Date();
        defaultDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
      }
      form.value = {
        title: '',
        description: '',
        date: defaultDate,
        startTime: '',
        endTime: '',
        color: '#c9a76c',
        isAllDay: true,
      };
      
      // 시간 초기화
      startHour.value = '';
      startMinute.value = '';
      endHour.value = '';
      endMinute.value = '';
    }
  }
});

function handleSave() {
  if (!form.value.title.trim()) return;
  
  // isAllDay는 저장 데이터에서 제외
  const { isAllDay, ...saveData } = form.value;
  emit('save', saveData);
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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

.schedule-modal {
  width: 420px;
  max-width: 95vw;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 16px;
  overflow: hidden;
  animation: modalIn 0.2s ease;
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
  background: var(--surface-3);
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
  background: var(--surface-1);
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
  background: var(--surface-2);
}

/* 종일 체크박스 */
.allday-toggle {
  margin-bottom: 16px;
}

.allday-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: var(--surface-1);
  border: 1px solid var(--surface-4);
  border-radius: 12px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.allday-checkbox:hover {
  background: var(--surface-2);
  border-color: var(--glass-highlight);
}

.allday-checkbox input {
  display: none;
}

.checkbox-custom {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--surface-3);
  border-radius: 12px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.checkbox-custom::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.allday-checkbox input:checked + .checkbox-custom {
  background: linear-gradient(135deg, #c9a76c 0%, #e8d5b7 100%);
}

.allday-checkbox input:checked + .checkbox-custom::after {
  left: 23px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.checkbox-label::before {
  content: '🌅';
  font-size: 16px;
}

/* 시간 섹션 */
.time-section {
  margin-bottom: 16px;
  padding: 18px;
  background: linear-gradient(145deg, var(--surface-1) 0%, var(--surface-2) 100%);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
}

/* 빠른 시간 선택 */
.quick-times {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--surface-3);
}

.quick-time-btn {
  padding: 7px 14px;
  background: var(--surface-2);
  border: 1px solid var(--surface-4);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.quick-time-btn:hover {
  background: var(--surface-3);
  border-color: var(--glass-highlight);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.quick-time-btn.active {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.2) 0%, rgba(201, 167, 108, 0.1) 100%);
  border-color: rgba(201, 167, 108, 0.4);
  color: #c9a76c;
  box-shadow: 0 2px 8px rgba(201, 167, 108, 0.15);
}

.time-inputs {
  display: flex;
  align-items: stretch;
  gap: 8px;
}

.time-input-group {
  flex: 1;
  padding: 12px;
  background: var(--surface-2);
  border: 1px solid var(--surface-4);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.time-input-group:hover {
  background: var(--surface-3);
}

.time-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.time-label svg {
  opacity: 0.6;
  flex-shrink: 0;
}

.time-input-group.start .time-label svg {
  color: #22c55e;
  opacity: 1;
}

.time-input-group.end .time-label svg {
  color: #ef4444;
  opacity: 1;
}

.time-picker {
  display: flex;
  align-items: center;
  gap: 4px;
}

.time-select {
  flex: 1;
  padding: 8px 6px;
  background: var(--surface-1);
  border: 1px solid var(--surface-4);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
  padding-right: 20px;
  min-width: 0;
}

.time-select:focus {
  outline: none;
  border-color: rgba(201, 167, 108, 0.5);
  background-color: var(--bg-primary);
  box-shadow: 0 0 0 2px rgba(201, 167, 108, 0.1);
}

.time-select:hover:not(:disabled) {
  border-color: var(--glass-highlight);
  background-color: var(--bg-primary);
}

.time-select:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.time-select option:disabled {
  color: var(--text-muted);
  opacity: 0.5;
}

.hour-select {
  flex: 2;
}

.minute-select {
  min-width: 70px;
}

/* 시간 연결부 */
.time-connector {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 2px;
}

.time-connector svg {
  color: #c9a76c;
  flex-shrink: 0;
  width: 14px;
  height: 14px;
}

.connector-line {
  display: none;
}

/* 시간 요약 */
.time-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
  padding: 10px 16px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.1) 0%, rgba(201, 167, 108, 0.05) 100%);
  border: 1px solid rgba(201, 167, 108, 0.2);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #c9a76c;
}

.time-summary svg {
  opacity: 0.7;
}

.memo-field textarea {
  width: 100%;
  padding: 12px;
  background: var(--surface-1);
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
  background: var(--surface-2);
}

.memo-field textarea::placeholder {
  color: var(--text-muted);
}

.color-field {
  margin-top: 4px;
}

.color-field label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.color-field label::before {
  content: '🎨';
  font-size: 14px;
}

.color-options {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: var(--surface-1);
  border: 1px solid var(--surface-4);
  border-radius: 12px;
}

.color-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.color-dot:hover {
  transform: scale(1.2) translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.color-dot.active {
  border-color: white;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2), 0 4px 12px rgba(0, 0, 0, 0.3);
  transform: scale(1.1);
}

.schedule-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 18px 20px;
  border-top: 1px solid var(--border-subtle);
  background: linear-gradient(180deg, var(--surface-1) 0%, var(--surface-2) 100%);
}

.btn-cancel,
.btn-save {
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-cancel {
  background: var(--surface-2);
  border: 1px solid var(--surface-4);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: var(--surface-3);
  border-color: var(--glass-highlight);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.btn-save {
  background: linear-gradient(135deg, #c9a76c 0%, #d4b67d 100%);
  border: none;
  color: #1a1a1a;
  box-shadow: 0 4px 12px rgba(201, 167, 108, 0.3);
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #d4b67d 0%, #e8d5b7 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(201, 167, 108, 0.4);
}

.btn-save:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}

</style>
