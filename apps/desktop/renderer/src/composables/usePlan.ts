import { ref } from 'vue';
import type { TodayPlan } from '../types';
import { API_ENDPOINTS } from '../config/api';

const todayPlan = ref<TodayPlan | null>(null);
const planLoading = ref(false);
const planError = ref('');

export function usePlan() {
  async function generatePlan() {
    planError.value = '';
    planLoading.value = true;
    try {
      const res = await fetch(`${API_ENDPOINTS.TODOS}/today`, {
        method: 'POST'
      });
      const data = await res.json();
      todayPlan.value = data as TodayPlan;
    } catch (error) {
      planError.value = 'Failed to generate plan.';
      console.error('Plan generation failed', error);
    } finally {
      planLoading.value = false;
    }
  }

  return {
    todayPlan,
    planLoading,
    planError,
    generatePlan
  };
}

