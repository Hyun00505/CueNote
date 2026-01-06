const { app, BrowserWindow } = require('electron');
const path = require('path');
const { createServer } = require('vite');
const vue = require('@vitejs/plugin-vue');

let mainWindow;
let viteServer;

async function createViteServer() {
  viteServer = await createServer({
    root: path.join(__dirname, 'renderer'),
    plugins: [(vue.default || vue)()],
    server: {
      port: 5173,
      strictPort: true
    }
  });
  await viteServer.listen();
  const urls = viteServer.resolvedUrls?.local ?? [];
  return urls[0] || 'http://localhost:5173';
}

async function createWindow() {
  const devUrl = await createViteServer();

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'renderer', 'preload.js')
    }
  });

  await mainWindow.loadURL(devUrl);
}

app.whenReady().then(() => {
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
