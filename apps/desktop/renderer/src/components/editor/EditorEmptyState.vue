<template>
  <div class="empty-state">
    <div class="empty-visual">
      <div class="empty-glow" />
      <div class="empty-icon">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
          <polyline points="14 2 14 8 20 8" />
          <line
            x1="16"
            y1="13"
            x2="8"
            y2="13"
          />
          <line
            x1="16"
            y1="17"
            x2="8"
            y2="17"
          />
          <line
            x1="10"
            y1="9"
            x2="8"
            y2="9"
          />
        </svg>
      </div>
    </div>
    <h2>{{ t('editor.emptyTitle') }}</h2>
    <p>{{ t('editor.emptySubtitle') }}</p>
    <div class="empty-hint">
      <svg
        class="empty-hint-arrow"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="M5 12h14M12 5l-7 7 7 7" />
      </svg>
      <span>{{ t('editor.emptyHint') }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '../../composables';

const { t } = useI18n();
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  animation: fadeIn 0.4s ease;
  position: relative;
  overflow: hidden;
}

.empty-visual {
  position: relative;
  margin-bottom: 24px;
}

.empty-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  opacity: 0.5;
  filter: blur(20px);
}

.empty-icon {
  position: relative;
  width: 80px;
  height: 80px;
  background: var(--bg-hover);
  border: 1px solid var(--border-subtle);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  box-shadow: var(--shadow-lg);
}

.empty-state h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.empty-state p {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0 0 32px 0;
}

.empty-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-hover);
  border-radius: 100px;
  font-size: 13px;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

.empty-hint-arrow {
  color: var(--primary);
  animation: slideRight 1.5s infinite ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideRight {

  0%,
  100% {
    transform: translateX(0);
  }

  50% {
    transform: translateX(4px);
  }
}
</style>
