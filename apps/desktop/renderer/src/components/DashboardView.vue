<template>
  <div class="dashboard-view">
    <!-- Background Decorations -->
    <div class="dashboard-bg">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="dashboard-content">
      <div class="dashboard-header">
        <div class="dashboard-title">
          <div class="title-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
          </div>
          <div class="title-text">
            <h1>Today's Focus</h1>
            <p>AI-powered task planning from your notes</p>
          </div>
        </div>
        <button
          class="generate-btn"
          :disabled="planLoading || !hasVault"
          @click="generatePlan"
        >
          <div class="btn-glow"></div>
          <svg v-if="!planLoading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
        <div class="empty-visual">
          <div class="empty-rings">
            <div class="ring ring-1"></div>
            <div class="ring ring-2"></div>
            <div class="ring ring-3"></div>
          </div>
          <div class="empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
          </div>
        </div>
        <h2>Ready to plan your day?</h2>
        <p>Generate an AI-powered plan based on your unchecked TODOs</p>
        <div class="empty-features">
          <div class="feature">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <span>Smart prioritization</span>
          </div>
          <div class="feature">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <span>Quick wins detection</span>
          </div>
          <div class="feature">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>Deadline tracking</span>
          </div>
        </div>
      </div>

      <div v-if="todayPlan" class="plan-content">
        <div class="plan-tldr">
          <div class="tldr-accent"></div>
          <div class="tldr-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <div class="tldr-content">
            <span class="tldr-label">TL;DR</span>
            <p>{{ todayPlan.tldr }}</p>
          </div>
        </div>

        <div class="plan-grid">
          <div class="plan-card priority" :style="{ '--index': 0 }">
            <div class="card-glow"></div>
            <div class="card-header">
              <div class="card-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
              <h3>Next Actions</h3>
              <span class="card-badge" v-if="todayPlan.nextActions.length">{{ todayPlan.nextActions.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(item, index) in todayPlan.nextActions" :key="`na-${index}`" :style="{ '--item-index': index }">
                <span class="list-marker"></span>
                <span class="list-text">{{ item }}</span>
              </li>
              <li v-if="!todayPlan.nextActions.length" class="empty-item">
                <span>No actions scheduled</span>
              </li>
            </ul>
          </div>

          <div class="plan-card quick" :style="{ '--index': 1 }">
            <div class="card-glow"></div>
            <div class="card-header">
              <div class="card-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
              </div>
              <h3>Quick Wins</h3>
              <span class="card-badge" v-if="todayPlan.quickWins.length">{{ todayPlan.quickWins.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(item, index) in todayPlan.quickWins" :key="`qw-${index}`" :style="{ '--item-index': index }">
                <span class="list-marker"></span>
                <span class="list-text">{{ item }}</span>
              </li>
              <li v-if="!todayPlan.quickWins.length" class="empty-item">
                <span>No quick wins found</span>
              </li>
            </ul>
          </div>

          <div class="plan-card overdue" :style="{ '--index': 2 }">
            <div class="card-glow"></div>
            <div class="card-header">
              <div class="card-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
              </div>
              <h3>Overdue</h3>
              <span class="card-badge danger" v-if="todayPlan.overdue.length">{{ todayPlan.overdue.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(todo, index) in todayPlan.overdue" :key="todo.id" :style="{ '--item-index': index }">
                <span class="list-marker"></span>
                <span class="list-text">{{ todo.text }}</span>
              </li>
              <li v-if="!todayPlan.overdue.length" class="empty-item success">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>No overdue items</span>
              </li>
            </ul>
          </div>

          <div class="plan-card due-soon" :style="{ '--index': 3 }">
            <div class="card-glow"></div>
            <div class="card-header">
              <div class="card-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
              </div>
              <h3>Due Soon</h3>
              <span class="card-badge" v-if="todayPlan.dueSoon.length">{{ todayPlan.dueSoon.length }}</span>
            </div>
            <ul class="card-list">
              <li v-for="(todo, index) in todayPlan.dueSoon" :key="todo.id" :style="{ '--item-index': index }">
                <span class="list-marker"></span>
                <span class="list-text">{{ todo.text }}</span>
              </li>
              <li v-if="!todayPlan.dueSoon.length" class="empty-item success">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
  position: relative;
}

.dashboard-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.orb-1 {
  top: -100px;
  right: -100px;
  width: 400px;
  height: 400px;
  background: var(--accent-primary);
  animation: float 15s ease-in-out infinite;
}

.orb-2 {
  bottom: -150px;
  left: -150px;
  width: 500px;
  height: 500px;
  background: #8b5cf6;
  animation: float 20s ease-in-out infinite reverse;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--border-subtle) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
  opacity: 0.5;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, 30px) scale(1.1); }
}

.dashboard-content {
  position: relative;
  padding: 32px 40px;
  z-index: 1;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  animation: slideUp 0.5s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  border-radius: var(--radius-lg);
  color: white;
  box-shadow: var(--shadow-md), var(--shadow-glow);
}

.title-text h1 {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.title-text p {
  color: var(--text-muted);
  font-size: 14px;
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: var(--gradient-primary);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-smooth);
  position: relative;
  overflow: hidden;
}

.btn-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 50%);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.generate-btn:hover:not(:disabled) .btn-glow {
  opacity: 1;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.generate-btn:active:not(:disabled) {
  transform: translateY(-1px);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.dashboard-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 80px 40px;
  animation: scaleIn 0.5s ease;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.empty-visual {
  position: relative;
  width: 160px;
  height: 160px;
  margin-bottom: 32px;
}

.empty-rings {
  position: absolute;
  inset: 0;
}

.ring {
  position: absolute;
  inset: 0;
  border: 1px solid var(--accent-glow);
  border-radius: 50%;
  animation: pulse-ring 3s ease-in-out infinite;
}

.ring-1 { animation-delay: 0s; }
.ring-2 { animation-delay: 1s; inset: 20px; }
.ring-3 { animation-delay: 2s; inset: 40px; }

@keyframes pulse-ring {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.05); }
}

.empty-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 50%;
  color: var(--accent-secondary);
}

.dashboard-empty h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.dashboard-empty p {
  color: var(--text-muted);
  font-size: 15px;
  margin-bottom: 32px;
}

.empty-features {
  display: flex;
  gap: 24px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--glass-bg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: 13px;
}

.feature svg {
  color: var(--accent-secondary);
}

.plan-content {
  animation: slideUp 0.5s ease;
}

.plan-tldr {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 24px 28px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.tldr-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--gradient-primary);
}

.tldr-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  color: white;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm), 0 0 20px var(--accent-glow);
}

.tldr-content {
  flex: 1;
}

.tldr-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--accent-secondary);
  margin-bottom: 8px;
  display: block;
}

.tldr-content p {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-primary);
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

@media (max-width: 1000px) {
  .plan-grid {
    grid-template-columns: 1fr;
  }
}

.plan-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: all var(--transition-smooth);
  animation: cardSlideUp 0.5s ease backwards;
  animation-delay: calc(var(--index) * 100ms);
}

@keyframes cardSlideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.plan-card:hover {
  border-color: var(--border-strong);
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, currentColor 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-smooth);
  pointer-events: none;
}

.plan-card:hover .card-glow {
  opacity: 0.03;
}

.plan-card.priority { color: var(--success); }
.plan-card.quick { color: var(--warning); }
.plan-card.overdue { color: var(--error); }
.plan-card.due-soon { color: var(--accent-secondary); }

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: currentColor;
  border-radius: var(--radius-md);
  color: white;
  box-shadow: 0 0 20px currentColor;
}

.card-icon svg {
  color: white;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-badge {
  margin-left: auto;
  padding: 4px 12px;
  background: var(--glass-bg);
  border: 1px solid currentColor;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  color: currentColor;
}

.card-badge.danger {
  background: var(--error);
  border-color: var(--error);
  color: white;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.card-list {
  list-style: none;
}

.card-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-subtle);
  animation: itemFadeIn 0.3s ease backwards;
  animation-delay: calc(var(--item-index, 0) * 50ms + 0.3s);
}

@keyframes itemFadeIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.card-list li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.list-marker {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
  margin-top: 6px;
  box-shadow: 0 0 8px currentColor;
}

.list-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.empty-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 14px;
  font-style: italic;
}

.empty-item.success {
  color: var(--success);
  font-style: normal;
}

.empty-item.success svg {
  color: var(--success);
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  border-radius: var(--radius-md);
  color: var(--error);
  font-size: 14px;
  margin-bottom: 24px;
  animation: slideUp 0.3s ease;
}

.error-msg svg {
  flex-shrink: 0;
}
</style>
