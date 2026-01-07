const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const { createServer } = require('vite');
const vue = require('@vitejs/plugin-vue');

// WSL2 환경에서 sandbox 및 shared memory 이슈 해결
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('disable-gpu-sandbox');
app.commandLine.appendSwitch('disable-dev-shm-usage');
app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('disable-software-rasterizer');
app.commandLine.appendSwitch('in-process-gpu');
app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor');

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
      webPreferences: {
        preload: path.join(__dirname, 'renderer', 'preload.js'),
        contextIsolation: true,
        nodeIntegration: false
      }
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
