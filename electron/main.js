const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let pythonProcess = null;

function createWindow() {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      sandbox: true
    }
  });

  // Load the React app (the browser's UI)
  const startUrl = process.env.ELECTRON_START_URL || 'http://localhost:3000';
  mainWindow.loadURL(startUrl);

  // Create and set the BrowserView for web content
  const { BrowserView } = require('electron');
  const view = new BrowserView();
  mainWindow.setBrowserView(view);

  const contentTopOffset = 78; // Height of title bar + address bar
  view.setBounds({ x: 0, y: contentTopOffset, width: 1200, height: 800 - contentTopOffset });
  view.setAutoResize({ width: true, height: true });
  view.webContents.loadURL('https://www.google.com');

  // Open DevTools for the BrowserView for debugging
  // view.webContents.openDevTools();
}

const { ipcMain } = require('electron');

app.whenReady().then(() => {
  // Security Hardening: Disable extensions and dev tools
  app.on('web-contents-created', (event, contents) => {
    contents.on('will-attach-webview', (event, webPreferences, params) => {
      // Strip away preload scripts if unused
      delete webPreferences.preload;
      delete webPreferences.preloadURL;

      // Disable Node.js integration
      webPreferences.nodeIntegration = false;
    });

    // Prevent opening new windows (e.g., popups)
    contents.setWindowOpenHandler(() => ({ action: 'deny' }));

    // Disable DevTools
    contents.on('devtools-opened', () => {
      contents.closeDevTools();
    });
  });

  // Start the Python backend
  const backendPath = path.join(__dirname, '..', 'va21-omni-agent', 'backend', 'app.py');
  pythonProcess = spawn('python', [backendPath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python Backend: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Backend Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python backend process exited with code ${code}`);
  });

  createWindow();

  // IPC handlers for browser navigation
  ipcMain.handle('navigate:to', (event, url) => {
    const win = BrowserWindow.getAllWindows()[0];
    const view = win.getBrowserView();
    if (view) {
      view.webContents.loadURL(url);
    }
  });

  ipcMain.handle('navigate:back', () => {
    const win = BrowserWindow.getAllWindows()[0];
    const view = win.getBrowserView();
    if (view && view.webContents.canGoBack()) {
      view.webContents.goBack();
    }
  });

  ipcMain.handle('navigate:forward', () => {
    const win = BrowserWindow.getAllWindows()[0];
    const view = win.getBrowserView();
    if (view && view.webContents.canGoForward()) {
      view.webContents.goForward();
    }
  });

  ipcMain.handle('navigate:reload', () => {
    const win = BrowserWindow.getAllWindows()[0];
    const view = win.getBrowserView();
    if (view) {
      view.webContents.reload();
    }
  });

  const sidePanelWidth = 500;
  ipcMain.handle('sidepanel:toggle', (event, isOpen) => {
    const win = BrowserWindow.getAllWindows()[0];
    const view = win.getBrowserView();
    const [width, height] = win.getSize();
    const contentTopOffset = 78;

    if (view) {
      if (isOpen) {
        view.setBounds({ x: 0, y: contentTopOffset, width: width - sidePanelWidth, height: height - contentTopOffset });
      } else {
        view.setBounds({ x: 0, y: contentTopOffset, width: width, height: height - contentTopOffset });
      }
    }
  });

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  // Kill the python process before quitting
  if (pythonProcess) {
    console.log('Killing Python backend process...');
    pythonProcess.kill();
  }
});
