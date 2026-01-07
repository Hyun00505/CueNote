import { ref } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';

const coreStatus = ref('checking...');

export function useHealth() {
  async function checkHealth() {
    try {
      const res = await fetch(`${CORE_BASE}/health`);
      const data = await res.json();
      coreStatus.value = data.status ?? 'unknown';
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

