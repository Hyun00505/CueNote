const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('cuenote', {
  selectVault: () => ipcRenderer.invoke('cuenote:select-vault')
});
