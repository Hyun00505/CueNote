const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// 개발 모드 감지
const isDev = !app.isPackaged;

// WSL2 환경 감지
const isWSL = process.platform === 'linux' && process.env.WSL_DISTRO_NAME;

if (isWSL) {
  // WSL2 환경에서만 sandbox 및 GPU 관련 이슈 해결 옵션 적용
  app.commandLine.appendSwitch('no-sandbox');
  app.commandLine.appendSwitch('disable-gpu-sandbox');
  app.commandLine.appendSwitch('disable-dev-shm-usage');
  app.commandLine.appendSwitch('disable-gpu');
  app.commandLine.appendSwitch('disable-software-rasterizer');
  app.commandLine.appendSwitch('in-process-gpu');
  app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor');
} else {
  // Windows/macOS 네이티브 환경: 하드웨어 가속 활성화
  app.commandLine.appendSwitch('enable-gpu-rasterization');
  app.commandLine.appendSwitch('enable-zero-copy');
  app.commandLine.appendSwitch('ignore-gpu-blocklist');
}

let mainWindow;
let viteServer;
let coreProcess;

// Python 백엔드 경로 찾기
function getCorePath() {
  if (isDev) {
    // 개발 모드: apps/core 폴더
    return path.join(__dirname, '..', 'core');
  } else {
    // 프로덕션 모드: resources/core 폴더 (PyInstaller로 빌드된 exe)
    return path.join(process.resourcesPath, 'core');
  }
}

// Python 백엔드 실행
async function startCoreServer() {
  const corePath = getCorePath();
  
  if (isDev) {
    // 개발 모드: uvicorn 직접 실행 (사용자가 별도로 실행한다고 가정)
    console.log('[Dev] Core server should be started separately with: pnpm dev:core');
    return true;
  }
  
  // 프로덕션 모드: 번들된 exe 실행
  const coreExe = path.join(corePath, 'cuenote-core.exe');
  
  if (!fs.existsSync(coreExe)) {
    console.error('Core executable not found:', coreExe);
    return false;
  }
  
  return new Promise((resolve) => {
    console.log('Starting core server:', coreExe);
    
    coreProcess = spawn(coreExe, [], {
      cwd: corePath,
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true
    });
    
    coreProcess.stdout.on('data', (data) => {
      console.log('[Core]', data.toString());
    });
    
    coreProcess.stderr.on('data', (data) => {
      console.error('[Core Error]', data.toString());
    });
    
    coreProcess.on('error', (err) => {
      console.error('Failed to start core:', err);
      resolve(false);
    });
    
    // 서버 시작 대기 (최대 30초)
    let attempts = 0;
    const maxAttempts = 60;
    
    const checkServer = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8787/health');
        if (response.ok) {
          console.log('Core server started successfully');
          resolve(true);
          return;
        }
      } catch (e) {
        // 서버 아직 준비 안됨
      }
      
      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(checkServer, 500);
      } else {
        console.error('Core server failed to start in time');
        resolve(false);
      }
    };
    
    // 1초 후 체크 시작
    setTimeout(checkServer, 1000);
  });
}

// Core 서버 종료
function stopCoreServer() {
  if (coreProcess) {
    console.log('Stopping core server...');
    coreProcess.kill();
    coreProcess = null;
  }
}

// 개발 모드: Vite 서버 시작
async function createViteServer() {
  if (!isDev) return null;
  
  try {
    const { createServer } = require('vite');
    const vue = require('@vitejs/plugin-vue');
    
    viteServer = await createServer({
      root: path.join(__dirname, 'renderer'),
      plugins: [(vue.default || vue)()],
      server: {
        port: 5173,
        strictPort: false,
        host: '127.0.0.1'
      }
    });
    await viteServer.listen();
    const urls = viteServer.resolvedUrls?.local ?? [];
    const devUrl = urls[0] || 'http://127.0.0.1:5173';
    console.log('Vite server started at:', devUrl);
    return devUrl;
  } catch (err) {
    console.error('Failed to start Vite server:', err);
    throw err;
  }
}

async function createWindow() {
  try {
    let loadUrl;
    
    if (isDev) {
      // 개발 모드: Vite 서버 사용
      loadUrl = await createViteServer();
    } else {
      // 프로덕션 모드: 빌드된 파일 로드
      loadUrl = `file://${path.join(__dirname, 'dist', 'index.html')}`;
    }

    mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      backgroundColor: '#0f0f12',
      show: false,
      webPreferences: {
        preload: isDev 
          ? path.join(__dirname, 'renderer', 'preload.js')
          : path.join(__dirname, 'dist', 'preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
        backgroundThrottling: false,
        enableWebSQL: false,
      }
    });

    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
    });

    mainWindow.loadURL(loadUrl).catch(err => {
      console.error('Failed to load URL:', err);
    });
    
    // 개발 모드에서 DevTools 열기 (선택사항)
    if (isDev) {
      // mainWindow.webContents.openDevTools();
    }
  } catch (err) {
    console.error('Failed to create window:', err);
    app.quit();
  }
}

app.whenReady().then(async () => {
  // IPC 핸들러 등록
  ipcMain.handle('cuenote:select-vault', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    });
    if (result.canceled) {
      return null;
    }
    return result.filePaths[0] || null;
  });

  // 프로덕션 모드에서 Core 서버 시작
  if (!isDev) {
    const coreStarted = await startCoreServer();
    if (!coreStarted) {
      dialog.showErrorBox(
        'CueNote 시작 오류',
        'Core 서버를 시작할 수 없습니다. 앱을 다시 설치해주세요.'
      );
      app.quit();
      return;
    }
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', async () => {
  // Vite 서버 종료
  if (viteServer) {
    await viteServer.close();
  }
  // Core 서버 종료
  stopCoreServer();
});

// 예기치 않은 종료 시에도 Core 서버 종료
process.on('exit', () => {
  stopCoreServer();
});

process.on('SIGINT', () => {
  stopCoreServer();
  process.exit();
});

process.on('SIGTERM', () => {
  stopCoreServer();
  process.exit();
});
