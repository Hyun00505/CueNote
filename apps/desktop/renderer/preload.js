const { contextBridge, ipcRenderer, webFrame } = require('electron');

console.log('[Preload] Loading preload.js');

contextBridge.exposeInMainWorld('cuenote', {
  selectVault: () => {
    console.log('[Preload] selectVault called');
    return ipcRenderer.invoke('cuenote:select-vault');
  },
  openExternal: (url) => ipcRenderer.invoke('cuenote:open-external', url),
  
  // 폰트 관련 API
  selectFont: () => ipcRenderer.invoke('cuenote:select-font'),
  saveFont: (sourcePath, fontName) => ipcRenderer.invoke('cuenote:save-font', { sourcePath, fontName }),
  deleteFont: (fontPath) => ipcRenderer.invoke('cuenote:delete-font', fontPath),
  getFontsPath: () => ipcRenderer.invoke('cuenote:get-fonts-path'),
  
  // UI 스케일 API (Electron 네이티브 zoom)
  setZoomFactor: (factor) => webFrame.setZoomFactor(factor),
  getZoomFactor: () => webFrame.getZoomFactor(),
  
  // PDF 내보내기 API
  printToPDF: (options) => ipcRenderer.invoke('cuenote:print-to-pdf', options)
});
