const { contextBridge, ipcRenderer } = require('electron');

console.log("Preload script loaded successfully.");

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object.
contextBridge.exposeInMainWorld('electronAPI', {
  navigateTo: (url) => ipcRenderer.invoke('navigate:to', url),
  navigateBack: () => ipcRenderer.invoke('navigate:back'),
  navigateForward: () => ipcRenderer.invoke('navigate:forward'),
  navigateReload: () => ipcRenderer.invoke('navigate:reload'),
  toggleSidePanel: (isOpen) => ipcRenderer.invoke('sidepanel:toggle', isOpen),
});
