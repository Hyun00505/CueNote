<template>
  <div class="empty-state-container">
    <!-- 로딩 -->
    <div
      v-if="loading"
      class="loading-overlay"
    >
      <div class="loading-spinner">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke-opacity="0.25"
          />
          <path
            d="M12 2a10 10 0 0 1 10 10"
            stroke-linecap="round"
          >
            <animateTransform
              attributeName="transform"
              type="rotate"
              from="0 12 12"
              to="360 12 12"
              dur="1s"
              repeatCount="indefinite"
            />
          </path>
        </svg>
        <span>AI가 노트를 분석하고 있습니다...</span>
      </div>
    </div>

    <!-- 에러 -->
    <div
      v-else-if="error"
      class="error-state"
    >
      <svg
        width="48"
        height="48"
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
          x1="15"
          y1="9"
          x2="9"
          y2="15"
        />
        <line
          x1="9"
          y1="9"
          x2="15"
          y2="15"
        />
      </svg>
      <p>{{ error }}</p>
      <button @click="emit('refresh')">
        다시 시도
      </button>
    </div>

    <!-- 빈 상태 (전체 노트 없음) -->
    <div
      v-else-if="isEmpty"
      class="empty-state"
    >
      <svg
        width="64"
        height="64"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <circle
          cx="12"
          cy="12"
          r="3"
        />
        <circle
          cx="4"
          cy="8"
          r="2"
        />
        <circle
          cx="20"
          cy="8"
          r="2"
        />
        <circle
          cx="4"
          cy="16"
          r="2"
        />
        <circle
          cx="20"
          cy="16"
          r="2"
        />
      </svg>
      <h3>노트를 추가해주세요</h3>
      <p>노트가 있어야 AI 클러스터링을 할 수 있습니다.</p>
    </div>

    <!-- 빈 클러스터 선택 시 -->
    <div
      v-else-if="clusterEmpty"
      class="empty-state cluster-empty"
    >
      <svg
        width="64"
        height="64"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke-dasharray="4 2"
        />
        <line
          x1="12"
          y1="8"
          x2="12"
          y2="12"
        />
        <circle
          cx="12"
          cy="15"
          r="0.5"
          fill="currentColor"
        />
      </svg>
      <h3>빈 클러스터</h3>
      <p>이 클러스터에는 노트가 없습니다.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  loading: boolean;
  error: string | null;
  isEmpty: boolean;
  clusterEmpty: boolean;
}>();

const emit = defineEmits<{
  (e: 'refresh'): void;
}>();
</script>

<style scoped>
.empty-state-container {
  display: contents; /* 부모의 layout에 영향받지 않도록 */
}

.loading-overlay,
.error-state,
.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: var(--bg-primary);
  z-index: 10;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--accent-primary, #8b5cf6);
}

.loading-spinner span {
  font-size: 14px;
  color: var(--text-muted);
}

.error-state {
  color: #ef4444;
}

.error-state p {
  color: var(--text-secondary);
  font-size: 14px;
}

.error-state button {
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.15s ease;
}

.error-state button:hover {
  background: rgba(239, 68, 68, 0.2);
}

.empty-state {
  color: var(--text-muted);
}

.empty-state h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-secondary);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.empty-state.cluster-empty svg {
  color: var(--accent-primary, #8b5cf6);
  opacity: 0.5;
}
</style>
