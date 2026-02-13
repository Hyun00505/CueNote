import { ref, computed } from 'vue';
import { API_ENDPOINTS, API_BASE_URL } from '../config/api';
import { useEnvironment } from './useEnvironment';
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

// 스테이징 선택 상태
const stagedFiles = ref<Set<string>>(new Set());
const stagedCount = computed(() => stagedFiles.value.size);

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
      const res = await fetch(API_ENDPOINTS.GITHUB.CHECK_GIT);
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
      const res = await fetch(API_ENDPOINTS.GITHUB.VALIDATE_TOKEN, {
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
      const res = await fetch(API_ENDPOINTS.GITHUB.REPOS, {
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

    // 환경으로 추가 (백엔드에 등록)
    const { addEnvironment } = useEnvironment();
    const envAdded = await addEnvironment(
      repo.name,
      `github://${repo.owner}/${repo.name}`,
      'github',
      {
        owner: repo.owner,
        repo: repo.name,
        full_name: repo.full_name,
        private: repo.private
      }
    );

    if (!envAdded) {
      console.error('[GitHub] Failed to add environment');
      return false;
    }

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
      const res = await fetch(API_ENDPOINTS.GITHUB.CLONE, {
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

  // 환경 전환 시 GitHub 모드 활성화 (클론/풀 없이)
  // 이미 클론된 환경을 전환할 때 사용
  async function switchToGitHubEnv(repo: GitHubRepo): Promise<boolean> {
    selectedRepo.value = repo;
    saveSettings();
    isGitHubActive.value = true;
    
    // 파일 목록 가져오기
    await fetchRepoFiles();
    // Git 상태 확인
    await checkGitStatus();
    
    return true;
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
      const res = await fetch(API_ENDPOINTS.GITHUB.REPO_FILES, {
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

  // 파일 저장 (로컬)
  async function saveFile(filePath: string, content: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(API_ENDPOINTS.GITHUB.SAVE_FILE, {
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
      const res = await fetch(API_ENDPOINTS.GITHUB.CREATE_FOLDER, {
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
      const res = await fetch(API_ENDPOINTS.GITHUB.RENAME_FILE, {
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
      const res = await fetch(API_ENDPOINTS.GITHUB.RENAME_FOLDER, {
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
      const res = await fetch(API_ENDPOINTS.GITHUB.CREATE_FILE, {
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

  // 파일 삭제 (실제 삭제)
  async function deleteFile(filePath: string): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    try {
      const res = await fetch(API_ENDPOINTS.GITHUB.DELETE_FILE, {
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
      
      const res = await fetch(`${API_ENDPOINTS.GITHUB.TRASH}?${params}`);
      
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
      const res = await fetch(API_ENDPOINTS.GITHUB.RESTORE_TRASH, {
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
      
      const res = await fetch(`${API_ENDPOINTS.GITHUB.TRASH}?${params}`, {
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
      
      const res = await fetch(`${API_ENDPOINTS.GITHUB.EMPTY_TRASH}?${params}`, {
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
    if (!token.value || !selectedRepo.value) {
      console.log('[checkGitStatus] Skipped: token or selectedRepo missing');
      return;
    }

    console.log('[checkGitStatus] Checking status for:', selectedRepo.value.owner, selectedRepo.value.name);

    try {
      const res = await fetch(API_ENDPOINTS.GITHUB.STATUS, {
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
        console.log('[checkGitStatus] Response:', data);
        isCloned.value = data.cloned;
        gitChanges.value = data.changes || [];
        console.log('[checkGitStatus] gitChanges updated:', gitChanges.value.length, 'files');
      } else {
        console.error('[checkGitStatus] Request failed:', res.status);
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
      const res = await fetch(API_ENDPOINTS.GITHUB.PULL, {
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

  // Push (변경사항 업로드) - 선택된 파일만 스테이징
  async function push(message: string, selectedFiles?: string[]): Promise<boolean> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return false;
    }

    if (!message.trim()) {
      error.value = '커밋 메시지를 입력해주세요';
      return false;
    }

    // 선택된 파일이 없으면 에러
    const filesToCommit = selectedFiles || Array.from(stagedFiles.value);
    if (filesToCommit.length === 0) {
      error.value = '커밋할 파일을 선택해주세요';
      return false;
    }

    isPushing.value = true;
    error.value = null;

    try {
      const res = await fetch(API_ENDPOINTS.GITHUB.PUSH, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          message: message.trim(),
          files: filesToCommit  // 선택된 파일 목록 전달
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Push에 실패했습니다');
      }

      // 스테이징 상태 초기화
      stagedFiles.value.clear();
      
      // Git 상태 새로고침
      await checkGitStatus();
      
      return true;
    } catch (e: any) {
      console.error('Failed to push:', e);
      error.value = e.message || 'Push에 실패했습니다';
      return false;
    } finally {
      isPushing.value = false;
    }
  }

  // 파일 스테이징 토글
  function toggleStageFile(path: string) {
    if (stagedFiles.value.has(path)) {
      stagedFiles.value.delete(path);
    } else {
      stagedFiles.value.add(path);
    }
    // 반응성을 위해 새 Set 생성
    stagedFiles.value = new Set(stagedFiles.value);
  }

  // 전체 스테이징
  function stageAll() {
    gitChanges.value.forEach(change => {
      stagedFiles.value.add(change.path);
    });
    stagedFiles.value = new Set(stagedFiles.value);
  }

  // 전체 스테이징 해제
  function unstageAll() {
    stagedFiles.value.clear();
    stagedFiles.value = new Set(stagedFiles.value);
  }

  // 파일이 스테이징되었는지 확인
  function isFileStaged(path: string): boolean {
    return stagedFiles.value.has(path);
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

  // 리포지토리 연결 해제 (로컬 클론 파일 삭제)
  async function disconnectRepo(): Promise<boolean> {
    if (selectedRepo.value && token.value) {
      try {
        const res = await fetch(`${API_BASE_URL}/github/disconnect`, {
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
          const errData = await res.json();
          console.error('Failed to disconnect repo:', errData);
          error.value = errData.detail || '연결 해제에 실패했습니다';
          return false;
        }
        
        // 파일 삭제 실패 경고 확인
        const data = await res.json();
        if (data.warning) {
          console.warn('Disconnect warning:', data.warning);
          // 경고가 있어도 연결 해제는 진행
        }
      } catch (e) {
        console.error('Failed to disconnect repo:', e);
        error.value = '연결 해제 중 오류가 발생했습니다';
        return false;
      }
    }
    
    selectedRepo.value = null;
    files.value = [];
    isCloned.value = false;
    gitChanges.value = [];
    stagedFiles.value.clear();
    isGitHubActive.value = false;
    saveSettings();
    return true;
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
      const res = await fetch(`${API_BASE_URL}/github/create-repo`, {
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
    // 앱 시작 시 GitHub 모드는 자동 활성화하지 않음
    isGitHubActive.value = false;
    
    // Git 설치 확인
    await checkGitInstalled();
    
    // 저장된 리포지토리가 있으면 파일 목록 자동 로드
    if (selectedRepo.value && token.value) {
      await fetchRepoFiles();
      await checkGitStatus();
    }
  }

  // GitHub 활성 모드 설정 (환경 전환 시 사용)
  function setGitHubActive(active: boolean) {
    isGitHubActive.value = active;
  }

  // GitHub 리포지토리에 이미지 업로드
  async function uploadImage(base64Data: string, noteName?: string): Promise<string | null> {
    if (!token.value || !selectedRepo.value) {
      error.value = '리포지토리를 먼저 선택해주세요';
      return null;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/github/repo/image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token.value,
          owner: selectedRepo.value.owner,
          repo: selectedRepo.value.name,
          data: base64Data,
          note_name: noteName
        })
      });

      if (!res.ok) {
        console.error('GitHub image upload failed:', res.status);
        return null;
      }

      const data = await res.json();
      // GitHub에서 보이도록 상대 경로 반환 (img/filename.png)
      // 에디터에서는 markdownToHtml에서 로컬 URL로 변환하여 표시
      return data.path;
    } catch (e) {
      console.error('GitHub image upload error:', e);
      return null;
    }
  }

  // GitHub 이미지의 상대 경로를 로컬 URL로 변환 (에디터에서 이미지 표시용)
  function getImageUrl(relativePath: string): string {
    if (!selectedRepo.value) return relativePath;
    return `${API_BASE_URL}/github/repo/image/${selectedRepo.value.owner}/${selectedRepo.value.name}/${relativePath.replace('img/', '')}`;
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

    // Staging State
    stagedFiles,
    stagedCount,

    // Trash State
    trashFiles,

    // Actions
    initGitHub,
    setGitHubActive,
    checkGitInstalled,
    validateToken,
    fetchRepos,
    selectRepo,
    switchToGitHubEnv,
    cloneOrPull,
    fetchRepoFiles,
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
    uploadImage,
    getImageUrl,

    // Staging Actions
    toggleStageFile,
    stageAll,
    unstageAll,
    isFileStaged,

    // Trash Actions
    fetchTrashFiles,
    restoreFromTrash,
    permanentDelete,
    emptyTrash
  };
}
