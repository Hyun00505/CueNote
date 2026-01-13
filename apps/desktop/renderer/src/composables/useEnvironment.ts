import { ref, computed } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';

export interface Environment {
  id: string;
  name: string;
  path: string;
  exists?: boolean;
  is_current?: boolean;
  // GitHub 환경 관련
  type?: 'local' | 'github';
  github?: {
    owner: string;
    repo: string;
    full_name: string;
    private: boolean;
  };
}

// 전역 상태
const environments = ref<Environment[]>([]);
const currentId = ref<string | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

export function useEnvironment() {
  // 현재 환경
  const currentEnvironment = computed(() => {
    return environments.value.find(e => e.id === currentId.value) || null;
  });

  // 환경 목록 조회
  async function fetchEnvironments() {
    loading.value = true;
    error.value = null;
    
    try {
      const res = await fetch(`${CORE_BASE}/environment/list`);
      const data = await res.json();
      
      environments.value = data.environments || [];
      currentId.value = data.current_id || null;
      
      // 환경이 없으면 기본 환경 초기화
      if (environments.value.length === 0) {
        await initDefaultEnvironment();
      }
    } catch (e) {
      console.error('Failed to fetch environments:', e);
      error.value = '환경 목록을 불러오는데 실패했습니다';
    } finally {
      loading.value = false;
    }
  }

  // 기본 환경 초기화
  async function initDefaultEnvironment() {
    try {
      const res = await fetch(`${CORE_BASE}/environment/init-default`, {
        method: 'POST'
      });
      const data = await res.json();
      
      if (data.environment) {
        environments.value = [data.environment];
        currentId.value = data.environment.id;
      }
    } catch (e) {
      console.error('Failed to init default environment:', e);
    }
  }

  // 환경 추가
  async function addEnvironment(name: string, path: string): Promise<boolean> {
    loading.value = true;
    error.value = null;
    
    try {
      const res = await fetch(`${CORE_BASE}/environment/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, path })
      });
      
      if (!res.ok) {
        const data = await res.json();
        error.value = data.detail || '환경 추가에 실패했습니다';
        return false;
      }
      
      await fetchEnvironments();
      return true;
    } catch (e) {
      console.error('Failed to add environment:', e);
      error.value = '환경 추가에 실패했습니다';
      return false;
    } finally {
      loading.value = false;
    }
  }

  // 환경 선택 (현재 환경 변경)
  async function selectEnvironment(id: string): Promise<boolean> {
    loading.value = true;
    error.value = null;
    
    try {
      const res = await fetch(`${CORE_BASE}/environment/set-current`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      
      if (!res.ok) {
        const data = await res.json();
        error.value = data.detail || '환경 선택에 실패했습니다';
        return false;
      }
      
      currentId.value = id;
      return true;
    } catch (e) {
      console.error('Failed to select environment:', e);
      error.value = '환경 선택에 실패했습니다';
      return false;
    } finally {
      loading.value = false;
    }
  }

  // 환경 제거
  async function removeEnvironment(id: string): Promise<boolean> {
    loading.value = true;
    error.value = null;
    
    try {
      const res = await fetch(`${CORE_BASE}/environment/remove`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      
      if (!res.ok) {
        const data = await res.json();
        error.value = data.detail || '환경 제거에 실패했습니다';
        return false;
      }
      
      const data = await res.json();
      currentId.value = data.new_current_id;
      await fetchEnvironments();
      return true;
    } catch (e) {
      console.error('Failed to remove environment:', e);
      error.value = '환경 제거에 실패했습니다';
      return false;
    } finally {
      loading.value = false;
    }
  }

  return {
    environments,
    currentId,
    currentEnvironment,
    loading,
    error,
    fetchEnvironments,
    addEnvironment,
    selectEnvironment,
    removeEnvironment,
    initDefaultEnvironment
  };
}
