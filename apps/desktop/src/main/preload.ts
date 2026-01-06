import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('cuenote', {
  ping: () => 'pong',
  selectVault: () => ipcRenderer.invoke('cuenote:select-vault'),
})
