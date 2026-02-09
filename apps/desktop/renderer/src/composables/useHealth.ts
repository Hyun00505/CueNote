import { ref } from 'vue';
import { API_BASE_URL } from '../config/api';

const coreStatus = ref('checking...');

export function useHealth() {
  async function checkHealth() {
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        coreStatus.value = data.status ?? 'unknown';
      } else {
        coreStatus.value = 'error'; // Or handle non-OK responses differently
        console.error('Health check failed with status:', res.status);
      }
    } catch (error) {
      coreStatus.value = 'unreachable';
      console.error('Health check failed', error);
    }
  }

  return {
    coreStatus,
    checkHealth
  };
}

