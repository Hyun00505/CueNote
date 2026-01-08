const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const { createServer } = require('vite');
const vue = require('@vitejs/plugin-vue');

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

async function createViteServer() {
  try {
    viteServer = await createServer({
      root: path.join(__dirname, 'renderer'),
      plugins: [(vue.default || vue)()],
      server: {
        port: 5173,
        strictPort: false,  // 포트가 사용 중이면 다른 포트 사용
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
    const devUrl = await createViteServer();

    mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      backgroundColor: '#0f0f12', // 초기 배경색 설정으로 흰색 깜빡임 방지
      show: false, // 준비될 때까지 숨김
      webPreferences: {
        preload: path.join(__dirname, 'renderer', 'preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
        // 성능 최적화
        backgroundThrottling: false, // 백그라운드 스로틀링 비활성화
        enableWebSQL: false, // 사용하지 않는 기능 비활성화
      }
    });

    // 창이 준비되면 표시 (부드러운 시작)
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
    });

    mainWindow.loadURL(devUrl).catch(err => {
      console.error('Failed to load URL:', err);
    });
  } catch (err) {
    console.error('Failed to create window:', err);
    app.quit();
  }
}

app.whenReady().then(() => {
  ipcMain.handle('cuenote:select-vault', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    });
    if (result.canceled) {
      return null;
    }
    return result.filePaths[0] || null;
  });

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
  if (viteServer) {
    await viteServer.close();
  }
});
