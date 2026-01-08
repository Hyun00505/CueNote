import { ref } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';

const vaultPath = ref<string | null>(null);
const vaultFiles = ref<string[]>([]);
const vaultError = ref('');
const vaultLoading = ref(false);
const todoCount = ref<number | null>(null);

export function useVault() {
  /**
   * 앱 시작 시 기본 vault(프로젝트 루트의 data 폴더)를 자동으로 로드합니다.
   */
  async function initVault() {
    vaultLoading.value = true;
    vaultError.value = '';
    try {
      // 기본 vault 열기 (path 없이 호출하면 서버가 기본 data 폴더 사용)
      const openRes = await fetch(`${CORE_BASE}/vault/open`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const openData = await openRes.json();
      vaultPath.value = openData.path || 'data';
      
      await refreshFiles();
      await refreshTodoCount();
    } catch (error) {
      vaultError.value = 'Failed to initialize vault.';
      console.error('Vault init failed', error);
    } finally {
      vaultLoading.value = false;
    }
  }

  /**
   * 사용자가 수동으로 다른 vault 폴더를 선택할 때 사용합니다.
   */
  async function openVault() {
    vaultError.value = '';
    const selected = await window.cuenote.selectVault();
    if (!selected) {
      return;
    }
    vaultPath.value = selected;
    try {
      await fetch(`${CORE_BASE}/vault/open`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: selected })
      });
      await refreshFiles();
      await refreshTodoCount();
    } catch (error) {
      vaultError.value = 'Failed to load vault files.';
      console.error('Vault load failed', error);
    }
  }

  async function refreshFiles() {
    try {
      const res = await fetch(`${CORE_BASE}/vault/files`);
      const data = await res.json();
      vaultFiles.value = Array.isArray(data.files) ? data.files : [];
    } catch (error) {
      console.error('Failed to refresh files', error);
      vaultFiles.value = [];
    }
  }

  async function refreshTodoCount() {
    try {
      const res = await fetch(`${CORE_BASE}/todos?checked=false`);
      const data = await res.json();
      todoCount.value = Array.isArray(data.todos) ? data.todos.length : 0;
    } catch (error) {
      todoCount.value = null;
      console.error('Failed to fetch TODO count', error);
    }
  }

  return {
    vaultPath,
    vaultFiles,
    vaultError,
    vaultLoading,
    todoCount,
    initVault,
    openVault,
    refreshFiles,
    refreshTodoCount
  };
}

