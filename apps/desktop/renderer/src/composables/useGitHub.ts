import { ref, computed } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';
const STORAGE_KEY = 'cuenote-github';

export interface GitHubUser {
  login: string;
  name: string | null;
  avatar_url: string;
  html_url: string;
}

export interface GitHubRepo {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  private: boolean;
  html_url: string;
  default_branch: string;
  owner: string;
}

export interface GitHubFile {
  name: string;
  path: string;
  type: 'file' | 'dir';
  size?: number;
  children?: GitHubFile[];
}

export interface GitHubSettings {
  token: string;
  user: GitHubUser | null;
  selectedRepo: GitHubRepo | null;
}

export interface GitChange {
  path: string;
  status: string;
  status_text: string;
}

// 전역 상태
const token = ref<string>('');
const user = ref<GitHubUser | null>(null);
const repos = ref<GitHubRepo[]>([]);
const selectedRepo = ref<GitHubRepo | null>(null);
const files = ref<GitHubFile[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const isValidating = ref(false);
const isLoggedIn = computed(() => !!user.value);

// Git 클론 관련 상태
const isCloned = ref(false);
const isCloning = ref(false);
const isPulling = ref(false);
const isPushing = ref(false);
const gitChanges = ref<GitChange[]>([]);
const hasChanges = computed(() => gitChanges.value.length > 0);
const gitInstalled = ref(true);

// GitHub 활성 모드 (환경 전환 시에도 연결 유지)
const isGitHubActive = ref(false);

// 휴지통 관련 상태
const trashFiles = ref<string[]>([]);

// 로컬 스토리지에서 설정 로드
function loadSettings(): GitHubSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.error('Failed to load GitHub settings:', e);
  }
  return { token: '', user: null, selectedRepo: null };
}

// 설정 저장
function saveSettings() {
  try {
    const settings: GitHubSettings = {
      token: token.value,
      user: user.value,
      selectedRepo: selectedRepo.value
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch (e) {
    console.error('Failed to save GitHub settings:', e);
  }
}

export function useGitHub() {
  // Git 설치 확인
  async function checkGitInstalled(): Promise<boolean> {
    try {
      const res = await fetch(`${CORE_BASE}/github/check-git`);
      const data = await res.json();
      gitInstalled.value = data.installed;
      return data.installed;
    } catch {
      gitInstalled.value = false;
      return false;
    }
  }

  // GitHub 토큰 검증
  async function validateToken(newToken: string): Promise<boolean> {
    if (!newToken) {
      error.value = '토큰을 입력해주세요';
      return false;
    }

    isValidating.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/validate-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: newToken })
      });
      
      const data = await res.json();
      
      if (data.valid) {
        token.value = newToken;
        user.value = data.user;
        saveSettings();
        return true;
      } else {
        error.value = data.error || '유효하지 않은 토큰입니다';
        return false;
      }
    } catch (e) {
      console.error('Failed to validate token:', e);
      error.value = '토큰 검증에 실패했습니다';
      return false;
    } finally {
      isValidating.value = false;
    }
  }

  // 리포지토리 목록 가져오기
  async function fetchRepos(): Promise<GitHubRepo[]> {
    if (!token.value) {
      error.value = '먼저 GitHub에 로그인해주세요';
      return [];
    }

    loading.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/repos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token.value })
      });

      if (!res.ok) {
        throw new Error('리포지토리 목록을 가져올 수 없습니다');
      }

      const data = await res.json();
      repos.value = data.repos || [];
      return repos.value;
    } catch (e) {
      console.error('Failed to fetch repos:', e);
      error.value = '리포지토리 목록을 가져오는데 실패했습니다';
      return [];
    } finally {
      loading.value = false;
    }
  }

  // 리포지토리 선택 및 클론
  async function selectRepo(repo: GitHubRepo): Promise<boolean> {
    if (!gitInstalled.value) {
      error.value = 'Git이 설치되어 있지 않습니다. Git을 설치한 후 다시 시도해주세요.';
      return false;
    }

    selectedRepo.value = repo;
    saveSettings();
    
    // 클론 또는 Pull
    const success = await cloneOrPull();
    if (success) {
      isGitHubActive.value = true;
    }
    return success;
  }

  // 리포지토리 클론 또는 Pull
  async function cloneOrPull(): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    isCloning.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/clone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          branch: selectedRepo.value.default_branch
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || '클론에 실패했습니다');
      }

      const data = await res.json();
      files.value = data.files || [];
      isCloned.value = true;
      
      // Git 상태 확인
      await checkGitStatus();
      
      return true;
    } catch (e: any) {
      console.error('Failed to clone repo:', e);
      error.value = e.message || '클론에 실패했습니다';
      return false;
    } finally {
      isCloning.value = false;
    }
  }

  // 파일 목록 가져오기 (로컬)
  async function fetchRepoFiles(): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    loading.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/files`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: ''
        })
      });

      if (!res.ok) {
        throw new Error('파일 목록을 가져올 수 없습니다');
      }

      const data = await res.json();
      files.value = data.files || [];
      isCloned.value = data.cloned || false;
      return true;
    } catch (e) {
      console.error('Failed to fetch repo files:', e);
      error.value = '파일 목록을 가져오는데 실패했습니다';
      return false;
    } finally {
      loading.value = false;
    }
  }

  // 파일 내용 가져오기
  async function fetchFileContent(filePath: string): Promise<string | null> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return null;
    }

    loading.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/file-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: filePath
        })
      });

      if (!res.ok) {
        throw new Error('파일 내용을 가져올 수 없습니다');
      }

      const data = await res.json();
      return data.content;
    } catch (e) {
      console.error('Failed to fetch file content:', e);
      error.value = '파일 내용을 가져오는데 실패했습니다';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 파일 저장 (로컬)
  async function saveFile(filePath: string, content: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/save-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: filePath,
          content
        })
      });

      if (!res.ok) {
        throw new Error('파일 저장에 실패했습니다');
      }

      // Git 상태 업데이트
      await checkGitStatus();
      
      return true;
    } catch (e) {
      console.error('Failed to save file:', e);
      error.value = '파일 저장에 실패했습니다';
      return false;
    }
  }

  // 새 파일 생성
  async function createFolder(folderPath: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/create-folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: folderPath,
          content: ''
        })
      });

      if (!res.ok) {
        const data = await res.json();
        error.value = data.detail || '폴더 생성에 실패했습니다';
        return false;
      }

      // 파일 목록 새로고침
      await fetchRepoFiles();
      // Git 상태 업데이트
      await checkGitStatus();
      return true;
    } catch (e) {
      error.value = '폴더 생성 중 오류가 발생했습니다';
      console.error('Create folder error:', e);
      return false;
    }
  }

  async function renameFile(oldPath: string, newPath: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/rename-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          old_path: oldPath,
          new_path: newPath
        })
      });

      if (!res.ok) {
        const data = await res.json();
        error.value = data.detail || '파일 이름 변경에 실패했습니다';
        return false;
      }

      // 파일 목록 새로고침
      await fetchRepoFiles();
      // Git 상태 업데이트
      await checkGitStatus();
      return true;
    } catch (e) {
      error.value = '파일 이름 변경 중 오류가 발생했습니다';
      console.error('Rename file error:', e);
      return false;
    }
  }

  async function renameFolder(oldPath: string, newPath: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/rename-folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          old_path: oldPath,
          new_path: newPath
        })
      });

      if (!res.ok) {
        const data = await res.json();
        error.value = data.detail || '폴더 이름 변경에 실패했습니다';
        return false;
      }

      // 파일 목록 새로고침
      await fetchRepoFiles();
      // Git 상태 업데이트
      await checkGitStatus();
      return true;
    } catch (e) {
      error.value = '폴더 이름 변경 중 오류가 발생했습니다';
      console.error('Rename folder error:', e);
      return false;
    }
  }

  async function createFile(filePath: string, content: string = ''): Promise<string | null> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return null;
    }

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/create-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: filePath,
          content
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || '파일 생성에 실패했습니다');
      }

      const data = await res.json();
      
      // 파일 목록 새로고침
      await fetchRepoFiles();
      await checkGitStatus();
      
      // 실제 생성된 파일 경로 반환 (백엔드에서 .md 확장자 추가됨)
      return data.path || filePath;
    } catch (e: any) {
      console.error('Failed to create file:', e);
      error.value = e.message || '파일 생성에 실패했습니다';
      return null;
    }
  }

  // 파일 삭제
  async function deleteFile(filePath: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/delete-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: filePath
        })
      });

      if (!res.ok) {
        throw new Error('파일 삭제에 실패했습니다');
      }

      // 파일 목록 새로고침
      await fetchRepoFiles();
      await fetchTrashFiles();
      await checkGitStatus();
      
      return true;
    } catch (e) {
      console.error('Failed to delete file:', e);
      error.value = '파일 삭제에 실패했습니다';
      return false;
    }
  }

  // 휴지통 파일 목록 조회
  async function fetchTrashFiles(): Promise<void> {
    if (!token.value || !selectedRepo.value) return;

    try {
      const params = new URLSearchParams({
        token: token.value,
        owner: selectedRepo.value.owner,
        repo: selectedRepo.value.name
      });
      
      const res = await fetch(`${CORE_BASE}/github/repo/trash?${params}`);
      
      if (res.ok) {
        const data = await res.json();
        trashFiles.value = data.files || [];
      }
    } catch (e) {
      console.error('Failed to fetch trash files:', e);
    }
  }

  // 휴지통에서 파일 복원
  async function restoreFromTrash(filename: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(`${CORE_BASE}/github/repo/trash/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: filename
        })
      });

      if (!res.ok) {
        throw new Error('파일 복원에 실패했습니다');
      }

      await fetchRepoFiles();
      await fetchTrashFiles();
      await checkGitStatus();
      return true;
    } catch (e) {
      console.error('Failed to restore file:', e);
      error.value = '파일 복원에 실패했습니다';
      return false;
    }
  }

  // 휴지통에서 파일 영구 삭제
  async function permanentDelete(filename: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const params = new URLSearchParams({
        token: token.value,
        owner: selectedRepo.value.owner,
        repo: selectedRepo.value.name,
        filename
      });
      
      const res = await fetch(`${CORE_BASE}/github/repo/trash?${params}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        throw new Error('파일 삭제에 실패했습니다');
      }

      await fetchTrashFiles();
      return true;
    } catch (e) {
      console.error('Failed to permanently delete:', e);
      error.value = '파일 삭제에 실패했습니다';
      return false;
    }
  }

  // 휴지통 비우기
  async function emptyTrash(): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const params = new URLSearchParams({
        token: token.value,
        owner: selectedRepo.value.owner,
        repo: selectedRepo.value.name
      });
      
      const res = await fetch(`${CORE_BASE}/github/repo/trash/empty?${params}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        throw new Error('휴지통 비우기에 실패했습니다');
      }

      trashFiles.value = [];
      return true;
    } catch (e) {
      console.error('Failed to empty trash:', e);
      error.value = '휴지통 비우기에 실패했습니다';
      return false;
    }
  }

  // Git 상태 확인
  async function checkGitStatus(): Promise<void> {
    if (!token.value || !selectedRepo.value) return;

    try {
      const res = await fetch(`${CORE_BASE}/github/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          path: ''
        })
      });

      if (res.ok) {
        const data = await res.json();
        isCloned.value = data.cloned;
        gitChanges.value = data.changes || [];
      }
    } catch (e) {
      console.error('Failed to check git status:', e);
    }
  }

  // Pull (최신 변경사항 가져오기)
  async function pull(): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    isPulling.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/pull`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Pull에 실패했습니다');
      }

      const data = await res.json();
      files.value = data.files || [];
      
      await checkGitStatus();
      
      return true;
    } catch (e: any) {
      console.error('Failed to pull:', e);
      error.value = e.message || 'Pull에 실패했습니다';
      return false;
    } finally {
      isPulling.value = false;
    }
  }

  // Push (변경사항 업로드)
  async function push(message: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    if (!message.trim()) {
      error.value = '커밋 메시지를 입력해주세요';
      return false;
    }

    isPushing.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/push`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          message: message.trim()
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Push에 실패했습니다');
      }

      // 상태 초기화
      gitChanges.value = [];
      
      return true;
    } catch (e: any) {
      console.error('Failed to push:', e);
      error.value = e.message || 'Push에 실패했습니다';
      return false;
    } finally {
      isPushing.value = false;
    }
  }

  // 로그아웃
  function logout() {
    token.value = '';
    user.value = null;
    repos.value = [];
    selectedRepo.value = null;
    files.value = [];
    error.value = null;
    isCloned.value = false;
    gitChanges.value = [];
    localStorage.removeItem(STORAGE_KEY);
  }

  // 리포지토리 연결 해제
  async function disconnectRepo() {
    if (selectedRepo.value && token.value) {
      try {
        await fetch(`${CORE_BASE}/github/disconnect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: token.value,
            owner: selectedRepo.value.owner,
            repo: selectedRepo.value.name,
            path: ''
          })
        });
      } catch (e) {
        console.error('Failed to disconnect repo:', e);
      }
    }
    
    selectedRepo.value = null;
    files.value = [];
    isCloned.value = false;
    gitChanges.value = [];
    isGitHubActive.value = false;
    saveSettings();
  }

  // 새 리포지토리 생성
  async function createRepo(name: string, description: string, isPrivate: boolean, initReadme: boolean): Promise<GitHubRepo | null> {
    if (!token.value) {
      error.value = '먼저 GitHub에 로그인해주세요';
      return null;
    }

    loading.value = true;
    error.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/github/create-repo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          name,
          description,
          private: isPrivate,
          auto_init: initReadme
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || '리포지토리 생성에 실패했습니다');
      }

      const data = await res.json();
      
      // 리포지토리 목록 새로고침
      await fetchRepos();
      
      return data.repo;
    } catch (e: any) {
      console.error('Failed to create repo:', e);
      error.value = e.message || '리포지토리 생성에 실패했습니다';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 초기화
  async function initGitHub() {
    const settings = loadSettings();
    token.value = settings.token;
    user.value = settings.user;
    selectedRepo.value = settings.selectedRepo;
    
    // Git 설치 확인
    await checkGitInstalled();
    
    // 저장된 리포지토리가 있으면 파일 목록 자동 로드
    if (selectedRepo.value && token.value) {
      await fetchRepoFiles();
      await checkGitStatus();
      // 저장된 리포가 있으면 GitHub 모드 활성화
      isGitHubActive.value = true;
    }
  }

  // GitHub 활성 모드 설정 (환경 전환 시 사용)
  function setGitHubActive(active: boolean) {
    isGitHubActive.value = active;
  }

  return {
    // State
    token,
    user,
    repos,
    selectedRepo,
    files,
    loading,
    error,
    isValidating,
    isLoggedIn,
    
    // Git Clone State
    isCloned,
    isCloning,
    isPulling,
    isPushing,
    gitChanges,
    hasChanges,
    gitInstalled,
    isGitHubActive,
    
    // Trash State
    trashFiles,
    
    // Actions
    initGitHub,
    setGitHubActive,
    checkGitInstalled,
    validateToken,
    fetchRepos,
    selectRepo,
    cloneOrPull,
    fetchRepoFiles,
    fetchFileContent,
    saveFile,
    createFile,
    createFolder,
    renameFile,
    renameFolder,
    deleteFile,
    checkGitStatus,
    pull,
    push,
    logout,
    disconnectRepo,
    createRepo,
    
    // Trash Actions
    fetchTrashFiles,
    restoreFromTrash,
    permanentDelete,
    emptyTrash
  };
}
