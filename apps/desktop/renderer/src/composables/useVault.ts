import { ref } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';

const vaultPath = ref<string | null>(null);
const vaultFiles = ref<string[]>([]);
const vaultError = ref('');
const todoCount = ref<number | null>(null);

export function useVault() {
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
    const res = await fetch(`${CORE_BASE}/vault/files`);
    const data = await res.json();
    vaultFiles.value = Array.isArray(data.files) ? data.files : [];
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
    todoCount,
    openVault,
    refreshFiles,
    refreshTodoCount
  };
}

