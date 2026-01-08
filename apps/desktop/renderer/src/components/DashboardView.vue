<template>
  <div class="dashboard-view">
    <div class="dashboard-content">
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
          <svg v-if="!planLoading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
          <span class="spinner" v-else></span>
          <span>{{ planLoading ? 'Generating...' : 'Generate Plan' }}</span>
        </button>
      </div>

      <p v-if="planError" class="error-msg">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ planError }}
      </p>

      <div v-if="!todayPlan && !planLoading" class="dashboard-empty">
        <div class="empty-icon">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
        </div>
        <h2>Ready to plan your day?</h2>
        <p>Generate an AI-powered plan based on your unchecked TODOs</p>
        <div class="empty-features">
          <div class="feature">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <span>Smart prioritization</span>
          </div>
          <div class="feature">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <span>Quick wins</span>
          </div>
          <div class="feature">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>Deadline tracking</span>
          </div>
        </div>
      </div>

      <div v-if="todayPlan" class="plan-content">
        <div class="plan-tldr">
          <div class="tldr-content">
            <span class="tldr-label">Summary</span>
            <p>{{ todayPlan.tldr }}</p>
          </div>
        </div>

        <div class="plan-grid">
          <div class="plan-card priority">
            <div class="card-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <h3>Next Actions</h3>
              <span class="card-badge" v-if="todayPlan.nextActions.length">{{ todayPlan.nextActions.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(item, index) in todayPlan.nextActions" :key="`na-${index}`">
                <span class="list-marker"></span>
                <span class="list-text">{{ item }}</span>
              </li>
              <li v-if="!todayPlan.nextActions.length" class="empty-item">
                <span>No actions scheduled</span>
              </li>
            </ul>
          </div>

          <div class="plan-card quick">
            <div class="card-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              <h3>Quick Wins</h3>
              <span class="card-badge" v-if="todayPlan.quickWins.length">{{ todayPlan.quickWins.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(item, index) in todayPlan.quickWins" :key="`qw-${index}`">
                <span class="list-marker"></span>
                <span class="list-text">{{ item }}</span>
              </li>
              <li v-if="!todayPlan.quickWins.length" class="empty-item">
                <span>No quick wins found</span>
              </li>
            </ul>
          </div>

          <div class="plan-card overdue">
            <div class="card-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <h3>Overdue</h3>
              <span class="card-badge danger" v-if="todayPlan.overdue.length">{{ todayPlan.overdue.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(todo, index) in todayPlan.overdue" :key="todo.id">
                <span class="list-marker"></span>
                <span class="list-text">{{ todo.text }}</span>
              </li>
              <li v-if="!todayPlan.overdue.length" class="empty-item success">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>No overdue items</span>
              </li>
            </ul>
          </div>

          <div class="plan-card due-soon">
            <div class="card-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
              <h3>Due Soon</h3>
              <span class="card-badge" v-if="todayPlan.dueSoon.length">{{ todayPlan.dueSoon.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(todo, index) in todayPlan.dueSoon" :key="todo.id">
                <span class="list-marker"></span>
                <span class="list-text">{{ todo.text }}</span>
              </li>
              <li v-if="!todayPlan.dueSoon.length" class="empty-item success">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>All caught up!</span>
              </li>
            </ul>
          </div>
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
  background: var(--bg-primary);
}

.dashboard-content {
  padding: 28px 36px;
  max-width: 1000px;
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
}

.dashboard-title h1 {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.dashboard-title p {
  color: var(--text-muted);
  font-size: 13px;
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(201, 167, 108, 0.12);
  border: 1px solid rgba(201, 167, 108, 0.25);
  border-radius: 8px;
  color: #e8d5b7;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.generate-btn:hover:not(:disabled) {
  background: rgba(201, 167, 108, 0.18);
  border-color: rgba(201, 167, 108, 0.35);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(232, 213, 183, 0.2);
  border-top-color: #e8d5b7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.dashboard-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 60px 40px;
}

.empty-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.dashboard-empty h2 {
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.dashboard-empty p {
  color: var(--text-muted);
  font-size: 13px;
  margin-bottom: 24px;
}

.empty-features {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.feature {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  color: var(--text-secondary);
  font-size: 12px;
}

.feature svg {
  color: #c9a76c;
  opacity: 0.8;
}

.plan-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.plan-tldr {
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  margin-bottom: 24px;
}

.tldr-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #c9a76c;
  margin-bottom: 6px;
  display: block;
}

.tldr-content p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 800px) {
  .plan-grid {
    grid-template-columns: 1fr;
  }
}

.plan-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 18px;
  transition: all 0.15s ease;
}

.plan-card:hover {
  border-color: var(--border-default);
  background: rgba(255, 255, 255, 0.03);
}

.plan-card.priority { --card-color: #22c55e; }
.plan-card.quick { --card-color: #eab308; }
.plan-card.overdue { --card-color: #dc2626; }
.plan-card.due-soon { --card-color: #c9a76c; }

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.card-header svg {
  color: var(--card-color);
  opacity: 0.85;
}

.card-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-badge {
  margin-left: auto;
  padding: 3px 10px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--card-color);
}

.card-badge.danger {
  background: rgba(220, 38, 38, 0.15);
  color: #dc2626;
}

.card-list {
  list-style: none;
}

.card-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-subtle);
}

.card-list li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.list-marker {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--card-color);
  flex-shrink: 0;
  margin-top: 6px;
  opacity: 0.7;
}

.list-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.empty-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 13px;
  font-style: italic;
}

.empty-item.success {
  color: #22c55e;
  font-style: normal;
}

.empty-item.success svg {
  opacity: 0.8;
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  margin-bottom: 20px;
}

.error-msg svg {
  flex-shrink: 0;
  opacity: 0.8;
}
</style>
