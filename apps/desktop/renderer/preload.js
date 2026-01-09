const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('cuenote', {
  selectVault: () => ipcRenderer.invoke('cuenote:select-vault'),
  openExternal: (url) => ipcRenderer.invoke('cuenote:open-external', url)
});
