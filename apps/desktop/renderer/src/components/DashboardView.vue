<template>
  <div class="dashboard-view">
    <div class="dashboard-header">
      <div class="dashboard-title">
        <h1>Today's Focus</h1>
        <p>AI-powered task planning from your notes</p>
      </div>
      <button 
        class="generate-btn" 
        :disabled="planLoading || !hasVault" 
        @click="generatePlan"
      >
        <svg v-if="!planLoading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
        </svg>
        <span class="spinner" v-else></span>
        <span>{{ planLoading ? 'Generating...' : 'Generate Plan' }}</span>
      </button>
    </div>

    <p v-if="planError" class="error-msg">{{ planError }}</p>

    <div v-if="!todayPlan && !planLoading" class="dashboard-empty">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
      </div>
      <h2>Ready to plan your day?</h2>
      <p>Generate an AI-powered plan based on your unchecked TODOs</p>
    </div>

    <div v-if="todayPlan" class="plan-content">
      <div class="plan-tldr">
        <div class="tldr-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
        <p>{{ todayPlan.tldr }}</p>
      </div>

      <div class="plan-grid">
        <div class="plan-card priority">
          <div class="card-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <h3>Next Actions</h3>
          </div>
          <ul class="card-list">
            <li v-for="(item, index) in todayPlan.nextActions" :key="`na-${index}`">
              <span class="list-marker"></span>
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="plan-card quick">
          <div class="card-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <h3>Quick Wins</h3>
          </div>
          <ul class="card-list">
            <li v-for="(item, index) in todayPlan.quickWins" :key="`qw-${index}`">
              <span class="list-marker"></span>
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="plan-card overdue">
          <div class="card-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <h3>Overdue</h3>
            <span class="count-badge" v-if="todayPlan.overdue.length">{{ todayPlan.overdue.length }}</span>
          </div>
          <ul class="card-list">
            <li v-for="todo in todayPlan.overdue" :key="todo.id">
              <span class="list-marker"></span>
              {{ todo.text }}
            </li>
            <li v-if="!todayPlan.overdue.length" class="empty-item">No overdue items 🎉</li>
          </ul>
        </div>

        <div class="plan-card due-soon">
          <div class="card-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <h3>Due Soon</h3>
            <span class="count-badge" v-if="todayPlan.dueSoon.length">{{ todayPlan.dueSoon.length }}</span>
          </div>
          <ul class="card-list">
            <li v-for="todo in todayPlan.dueSoon" :key="todo.id">
              <span class="list-marker"></span>
              {{ todo.text }}
            </li>
            <li v-if="!todayPlan.dueSoon.length" class="empty-item">All caught up!</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePlan } from '../composables';

defineProps<{
  hasVault: boolean;
}>();

const { todayPlan, planLoading, planError, generatePlan } = usePlan();
</script>

<style scoped>
.dashboard-view {
  height: 100%;
  overflow-y: auto;
  padding: 24px 32px;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  animation: fadeIn 0.5s ease;
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

.dashboard-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.dashboard-title p {
  color: var(--text-muted);
  font-size: 14px;
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-glow);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px var(--accent-glow);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.dashboard-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px;
  animation: fadeIn 0.5s ease;
}

.empty-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border-radius: 50%;
  margin-bottom: 24px;
  color: var(--text-muted);
}

.dashboard-empty h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.dashboard-empty p {
  color: var(--text-muted);
  font-size: 14px;
}

.plan-content {
  animation: fadeIn 0.5s ease;
}

.plan-tldr {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, var(--bg-elevated), var(--bg-secondary));
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  margin-bottom: 24px;
}

.tldr-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-primary);
  border-radius: var(--radius-md);
  color: white;
  flex-shrink: 0;
}

.plan-tldr p {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);
  padding-top: 8px;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (max-width: 900px) {
  .plan-grid {
    grid-template-columns: 1fr;
  }
}

.plan-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px;
  transition: all var(--transition-fast);
}

.plan-card:hover {
  border-color: var(--border-default);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.card-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.count-badge {
  margin-left: auto;
  padding: 2px 8px;
  background: var(--bg-active);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.plan-card.priority .card-header svg {
  color: var(--success);
}

.plan-card.quick .card-header svg {
  color: var(--warning);
}

.plan-card.overdue .card-header svg {
  color: var(--error);
}

.plan-card.due-soon .card-header svg {
  color: var(--accent-secondary);
}

.card-list {
  list-style: none;
}

.card-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  font-size: 13px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.card-list li:last-child {
  border-bottom: none;
}

.list-marker {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  flex-shrink: 0;
  margin-top: 6px;
}

.plan-card.priority .list-marker {
  background: var(--success);
}

.plan-card.quick .list-marker {
  background: var(--warning);
}

.plan-card.overdue .list-marker {
  background: var(--error);
}

.plan-card.due-soon .list-marker {
  background: var(--accent-secondary);
}

.empty-item {
  color: var(--text-muted);
  font-style: italic;
}

.error-msg {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-sm);
  color: var(--error);
  font-size: 13px;
  margin-top: 12px;
}
</style>


