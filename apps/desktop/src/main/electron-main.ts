import { app, BrowserWindow, dialog, ipcMain } from 'electron'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import waitOn from 'wait-on'

const devServerUrl = 'http://localhost:5173'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

async function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  })

  if (app.isPackaged) {
    await mainWindow.loadFile(path.resolve(__dirname, '../renderer/index.html'))
    return
  }

  await waitOn({ resources: [devServerUrl], timeout: 60_000 })
  await mainWindow.loadURL(devServerUrl)
}

app.whenReady().then(() => {
  ipcMain.handle('cuenote:select-vault', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory'],
    })

    if (result.canceled || result.filePaths.length === 0) {
      return null
    }

    return result.filePaths[0]
  })

  void createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      void createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
