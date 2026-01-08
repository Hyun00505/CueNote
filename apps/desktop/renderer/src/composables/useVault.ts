import { ref } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';

const vaultPath = ref<string | null>(null);
const vaultFiles = ref<string[]>([]);
const trashFiles = ref<string[]>([]);
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
      await refreshTrash();
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
      await refreshTrash();
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

  async function deleteFile(path: string): Promise<boolean> {
    try {
      const res = await fetch(`${CORE_BASE}/vault/file`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      });
      
      if (!res.ok) {
        const error = await res.json();
        console.error('Failed to delete file:', error);
        return false;
      }
      
      // 파일 목록과 TODO 카운트, 휴지통 갱신
      await refreshFiles();
      await refreshTodoCount();
      await refreshTrash();
      return true;
    } catch (error) {
      console.error('Failed to delete file', error);
      return false;
    }
  }

  async function createFile(fileName?: string): Promise<string | null> {
    try {
      // 파일명이 주어진 경우 PUT으로 빈 파일 생성
      if (fileName) {
        const path = fileName.endsWith('.md') ? fileName : `${fileName}.md`;
        const res = await fetch(`${CORE_BASE}/vault/file`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path, content: `# ${fileName.replace(/\.md$/, '')}\n\n` })
        });
        
        if (!res.ok) {
          const error = await res.json();
          console.error('Failed to create file:', error.detail);
          return null;
        }
        
        await refreshFiles();
        return path;
      }
      
      // 파일명이 없으면 기존 방식 (Untitled)
      const res = await fetch(`${CORE_BASE}/vault/file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!res.ok) {
        const error = await res.json();
        console.error('Failed to create file:', error.detail);
        return null;
      }
      
      const data = await res.json();
      
      // 파일 목록 갱신
      await refreshFiles();
      return data.path;
    } catch (error) {
      console.error('Failed to create file', error);
      return null;
    }
  }

  async function renameFile(oldPath: string, newPath: string): Promise<string | null> {
    try {
      const res = await fetch(`${CORE_BASE}/vault/file/rename`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_path: oldPath, new_path: newPath })
      });
      
      if (!res.ok) {
        const error = await res.json();
        console.error('Failed to rename file:', error.detail);
        return null;
      }
      
      const data = await res.json();
      
      // 파일 목록 갱신
      await refreshFiles();
      return data.new_path;
    } catch (error) {
      console.error('Failed to rename file', error);
      return null;
    }
  }

  // 휴지통 관련 함수들
  async function refreshTrash() {
    try {
      const res = await fetch(`${CORE_BASE}/vault/trash`);
      const data = await res.json();
      trashFiles.value = Array.isArray(data.files) ? data.files : [];
    } catch (error) {
      console.error('Failed to refresh trash', error);
      trashFiles.value = [];
    }
  }

  async function restoreFile(filename: string): Promise<string | null> {
    try {
      const res = await fetch(`${CORE_BASE}/vault/trash/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
      });
      
      if (!res.ok) {
        const error = await res.json();
        console.error('Failed to restore file:', error);
        return null;
      }
      
      const data = await res.json();
      
      // 파일 목록과 휴지통 갱신
      await refreshFiles();
      await refreshTrash();
      return data.path;
    } catch (error) {
      console.error('Failed to restore file', error);
      return null;
    }
  }

  async function permanentDelete(filename: string): Promise<boolean> {
    try {
      const res = await fetch(`${CORE_BASE}/vault/trash`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
      });
      
      if (!res.ok) {
        const error = await res.json();
        console.error('Failed to permanently delete file:', error);
        return false;
      }
      
      // 휴지통 갱신
      await refreshTrash();
      return true;
    } catch (error) {
      console.error('Failed to permanently delete file', error);
      return false;
    }
  }

  async function emptyTrash(): Promise<boolean> {
    try {
      const res = await fetch(`${CORE_BASE}/vault/trash/empty`, {
        method: 'DELETE'
      });
      
      if (!res.ok) {
        console.error('Failed to empty trash');
        return false;
      }
      
      // 휴지통 갱신
      await refreshTrash();
      return true;
    } catch (error) {
      console.error('Failed to empty trash', error);
      return false;
    }
  }

  return {
    vaultPath,
    vaultFiles,
    trashFiles,
    vaultError,
    vaultLoading,
    todoCount,
    initVault,
    openVault,
    refreshFiles,
    refreshTodoCount,
    deleteFile,
    createFile,
    renameFile,
    refreshTrash,
    restoreFile,
    permanentDelete,
    emptyTrash
  };
}

