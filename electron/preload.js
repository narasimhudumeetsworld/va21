const { contextBridge, ipcRenderer } = require('electron');

console.log("Preload script loaded successfully.");

contextBridge.exposeInMainWorld('electronAPI', {
  // Navigation (now tab-specific)
  navigateTo: (url) => ipcRenderer.send('tabs:navigate', url),
  navigateBack: () => ipcRenderer.send('tabs:go-back'),
  navigateForward: () => ipcRenderer.send('tabs:go-forward'),
  navigateReload: () => ipcRenderer.send('tabs:reload'),

  // Side Panel
  toggleSidePanel: (isOpen) => ipcRenderer.invoke('sidepanel:toggle', isOpen),

  // Tab Management
  newTab: (tab) => ipcRenderer.send('tabs:new', tab),
  selectTab: (id) => ipcRenderer.send('tabs:select', id),
  closeTab: (id) => ipcRenderer.send('tabs:close', id),

  // Listener for updates from main process (e.g., title/url changes)
  onTabUpdate: (callback) => {
    const channel = 'tabs:update';
    const listener = (_event, value) => callback(value);
    ipcRenderer.on(channel, listener);
    // Return a function to unregister the listener to prevent memory leaks
    return () => ipcRenderer.removeListener(channel, listener);
  },

  // Settings
  getSettings: () => ipcRenderer.invoke('settings:get'),
  saveSettings: (settings) => ipcRenderer.send('settings:save', settings)
});
