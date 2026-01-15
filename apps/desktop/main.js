const { app, BrowserWindow, dialog, ipcMain, shell, nativeTheme, protocol } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const url = require('url');

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

// 시스템 테마 설정 따르기 (앱 내부에서 data-theme으로 별도 관리)
nativeTheme.themeSource = 'system';

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
    // 아이콘 경로 설정
    const iconPath = isDev
      ? path.join(__dirname, '..', '..', 'assets', 'icon.png')
      : path.join(process.resourcesPath, 'icon.png');

    mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      show: false,
      autoHideMenuBar: true,
      icon: iconPath,
      webPreferences: {
        preload: isDev 
          ? path.join(__dirname, 'renderer', 'preload.js')
          : path.join(__dirname, 'dist', 'preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
        backgroundThrottling: false,
        enableWebSQL: false,
        // 로컬 폰트 파일 로드를 위해 webSecurity 비활성화 (개발 모드에서만)
        webSecurity: !isDev,
      }
    });

    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
    });

    if (isDev) {
      // 개발 모드: Vite 서버 사용
      const devUrl = await createViteServer();
      mainWindow.loadURL(devUrl).catch(err => {
        console.error('Failed to load URL:', err);
      });
    } else {
      // 프로덕션 모드: loadFile 사용 (상대 경로 문제 해결)
      const indexPath = path.join(__dirname, 'dist', 'index.html');
      console.log('Loading:', indexPath);
      mainWindow.loadFile(indexPath).catch(err => {
        console.error('Failed to load file:', err);
      });
    }
    
    // 개발 모드에서 DevTools 열기 (선택사항)
    // if (isDev) {
    //   mainWindow.webContents.openDevTools();
    // }
  } catch (err) {
    console.error('Failed to create window:', err);
    app.quit();
  }
}

app.whenReady().then(async () => {
  // 로컬 폰트 파일 접근을 위한 프로토콜 핸들러 등록
  protocol.handle('cuenote-font', (request) => {
    const filePath = decodeURIComponent(request.url.replace('cuenote-font://', ''));
    return new Response(fs.readFileSync(filePath), {
      headers: { 'Content-Type': 'font/ttf' }
    });
  });

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

  // 외부 링크 열기
  ipcMain.handle('cuenote:open-external', async (_, url) => {
    await shell.openExternal(url);
  });

  // 폰트 파일 선택
  ipcMain.handle('cuenote:select-font', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'Font Files', extensions: ['ttf', 'otf', 'woff', 'woff2'] }
      ]
    });
    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }
    return result.filePaths[0];
  });

  // 폰트 파일 저장 (앱 데이터 폴더로 복사)
  ipcMain.handle('cuenote:save-font', async (_, { sourcePath, fontName }) => {
    try {
      const fontsDir = path.join(app.getPath('userData'), 'fonts');
      
      // fonts 폴더 생성
      if (!fs.existsSync(fontsDir)) {
        fs.mkdirSync(fontsDir, { recursive: true });
      }
      
      // 파일 확장자 추출
      const ext = path.extname(sourcePath).toLowerCase();
      const safeFileName = fontName.replace(/[^a-zA-Z0-9가-힣\-_]/g, '_') + ext;
      const destPath = path.join(fontsDir, safeFileName);
      
      // 파일 복사
      fs.copyFileSync(sourcePath, destPath);
      
      return {
        success: true,
        path: destPath,
        fileName: safeFileName
      };
    } catch (error) {
      console.error('Failed to save font:', error);
      return {
        success: false,
        error: error.message
      };
    }
  });

  // 폰트 파일 삭제
  ipcMain.handle('cuenote:delete-font', async (_, fontPath) => {
    try {
      if (fs.existsSync(fontPath)) {
        fs.unlinkSync(fontPath);
      }
      return { success: true };
    } catch (error) {
      console.error('Failed to delete font:', error);
      return { success: false, error: error.message };
    }
  });

  // 폰트 폴더 경로 가져오기
  ipcMain.handle('cuenote:get-fonts-path', async () => {
    return path.join(app.getPath('userData'), 'fonts');
  });

  // PDF로 저장 (마크다운 콘텐츠만)
  ipcMain.handle('cuenote:print-to-pdf', async (_, options = {}) => {
    let pdfWindow = null;
    
    try {
      // 저장 경로 선택
      const result = await dialog.showSaveDialog(mainWindow, {
        title: 'PDF로 저장',
        defaultPath: options.filename || 'document.pdf',
        filters: [
          { name: 'PDF Files', extensions: ['pdf'] }
        ]
      });

      if (result.canceled || !result.filePath) {
        return { success: false, canceled: true };
      }

      // 숨겨진 창에서 마크다운만 렌더링
      pdfWindow = new BrowserWindow({
        width: 800,
        height: 600,
        show: false,
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true
        }
      });

      // 마크다운 스타일 + 콘텐츠 HTML 생성
      const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${options.title || 'CueNote'}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 11pt;
      line-height: 1.7;
      color: #1a1a1a;
      padding: 40px 50px;
      background: white;
    }
    
    h1, h2, h3, h4, h5, h6 {
      margin-top: 1.5em;
      margin-bottom: 0.5em;
      font-weight: 600;
      line-height: 1.3;
    }
    
    h1 { font-size: 24pt; border-bottom: 2px solid #333; padding-bottom: 8px; }
    h2 { font-size: 18pt; border-bottom: 1px solid #ddd; padding-bottom: 6px; }
    h3 { font-size: 14pt; }
    h4 { font-size: 12pt; }
    
    p {
      margin: 0.8em 0;
    }
    
    ul, ol {
      margin: 0.8em 0;
      padding-left: 2em;
    }
    
    li {
      margin: 0.3em 0;
    }
    
    code {
      font-family: 'Consolas', 'Monaco', monospace;
      background: #f4f4f4;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 0.9em;
    }
    
    pre {
      background: #f8f8f8;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      padding: 16px;
      overflow-x: auto;
      margin: 1em 0;
    }
    
    pre code {
      background: none;
      padding: 0;
    }
    
    blockquote {
      border-left: 4px solid #c9a76c;
      margin: 1em 0;
      padding: 0.5em 1em;
      background: #faf8f5;
      color: #555;
    }
    
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 1em 0;
    }
    
    th, td {
      border: 1px solid #ddd;
      padding: 10px;
      text-align: left;
    }
    
    th {
      background: #f5f5f5;
      font-weight: 600;
    }
    
    img {
      max-width: 100%;
      height: auto;
    }
    
    hr {
      border: none;
      border-top: 1px solid #ddd;
      margin: 2em 0;
    }
    
    a {
      color: #0066cc;
      text-decoration: none;
    }
    
    strong {
      font-weight: 600;
    }
    
    em {
      font-style: italic;
    }
    
    /* 체크박스 스타일 */
    ul[data-type="taskList"] {
      list-style: none;
      padding-left: 0;
    }
    
    ul[data-type="taskList"] li {
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }
    
    input[type="checkbox"] {
      margin-top: 4px;
    }
  </style>
</head>
<body>
  ${options.htmlContent || ''}
</body>
</html>`;

      await pdfWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(htmlContent)}`);
      
      // 렌더링 완료 대기
      await new Promise(resolve => setTimeout(resolve, 500));

      // PDF 생성
      const pdfData = await pdfWindow.webContents.printToPDF({
        marginsType: 0,
        pageSize: 'A4',
        printBackground: true,
        printSelectionOnly: false,
        landscape: false
      });
      
      // 파일로 저장
      fs.writeFileSync(result.filePath, pdfData);
      
      return { 
        success: true, 
        filePath: result.filePath 
      };
    } catch (error) {
      console.error('PDF export failed:', error);
      return { 
        success: false, 
        error: error.message 
      };
    } finally {
      if (pdfWindow) {
        pdfWindow.destroy();
      }
    }
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
