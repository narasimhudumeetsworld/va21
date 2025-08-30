const { app, BrowserWindow, BrowserView, ipcMain, protocol, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { download } = require('electron-dl');
const extract = require('extract-zip');
const tar = require('tar');

let pythonProcess = null;
let mainWindow = null;
const views = {};
let activeViewId = null;

let CHROME_HEIGHT = 90; // Default value

// --- Path Configurations ---
const USER_DATA_PATH = app.getPath('userData');
const SETTINGS_PATH = path.join(USER_DATA_PATH, 'settings.json');

const MODEL_BASE_URL = 'https://huggingface.co/microsoft/Phi-4-mini-reasoning-onnx/resolve/main/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4';
const MODEL_FILES = [ 'added_tokens.json', 'config.json', 'configuration_phi3.py', 'genai_config.json', 'merges.txt', 'model.onnx', 'model.onnx.data', 'special_tokens_map.json', 'tokenizer.json', 'tokenizer_config.json', 'vocab.json' ];
const MODEL_PATH = path.join(__dirname, '..', 'va21-omni-agent', 'backend');

const VENDOR_PATH = path.join(__dirname, '..', 'vendor');
const PYTHON_WIN_URL = 'https://www.python.org/ftp/python/3.11.12/python-3.11.12-embed-amd64.zip';
const PYTHON_WIN_PATH = path.join(VENDOR_PATH, 'python-win');
const PYTHON_MAC_URL = ''; // Still need this
const PYTHON_MAC_PATH = path.join(VENDOR_PATH, 'python-mac');
const PYTHON_LINUX_PATH = path.join(VENDOR_PATH, 'python-linux');

// --- Helper Functions ---

async function showDownloaderWindow(title, message) {
    const downloaderWindow = new BrowserWindow({ width: 450, height: 220, frame: false, resizable: false, movable: true, webPreferences: { nodeIntegration: true, contextIsolation: false } });
    downloaderWindow.loadFile(path.join(__dirname, 'downloader.html'));
    await new Promise(resolve => downloaderWindow.once('ready-to-show', resolve));
    downloaderWindow.webContents.executeJavaScript(`document.querySelector('h1').innerText = '${title}'; document.querySelector('p:nth-of-type(1)').innerText = '${message}';`);
    return downloaderWindow;
}

async function ensureModelExists() {
    if (fs.existsSync(path.join(MODEL_PATH, 'model.onnx.data'))) return;
    const downloader = await showDownloaderWindow('Preparing Guardian AI...', 'Downloading necessary security models...');
    for (let i = 0; i < MODEL_FILES.length; i++) {
        await download(downloader, `${MODEL_BASE_URL}/${MODEL_FILES[i]}`, { directory: MODEL_PATH, onProgress: p => downloader.webContents.send('download-progress', { percent: (i + p.percent) / MODEL_FILES.length }) });
    }
    downloader.close();
}

async function ensurePythonExists() {
    const platform = process.platform;
    let pythonExe;
    if (platform === 'win32') {
        pythonExe = path.join(PYTHON_WIN_PATH, 'python.exe');
    } else if (platform === 'darwin') {
        pythonExe = path.join(PYTHON_MAC_PATH, 'bin', 'python3');
    } else if (platform === 'linux') {
        pythonExe = path.join(PYTHON_LINUX_PATH, 'bin', 'python');
    }

    if (!pythonExe || !fs.existsSync(pythonExe)) {
        dialog.showErrorBox('Python Not Found', 'Python executable not found. Please run the setup script or install Python manually.');
        app.quit();
    }
}

function getPythonExecutablePath() {
    const platform = process.platform;
    if (platform === 'win32') return path.join(PYTHON_WIN_PATH, 'python.exe');
    if (platform === 'darwin') return path.join(PYTHON_MAC_PATH, 'bin', 'python3');
    if (platform === 'linux') return path.join(PYTHON_LINUX_PATH, 'bin', 'python');
    return 'python3'; // Fallback
}

function createWindow() {
  mainWindow = new BrowserWindow({ width: 1200, height: 800, frame: false, titleBarStyle: 'hidden', webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, sandbox: true } });
  mainWindow.loadFile(path.join(__dirname, '..', 'va21-omni-agent', 'frontend', 'build', 'index.html'));
  mainWindow.on('resize', () => {
    const activeView = getActiveView();
    if (activeView) {
        const [width, height] = mainWindow.getSize();
        activeView.setBounds({ x: 0, y: CHROME_HEIGHT, width, height: height - CHROME_HEIGHT });
    }
  });
}

function getActiveView() { return views[activeViewId]; }

// --- App Lifecycle & IPC ---

app.whenReady().then(async () => {
  await ensureModelExists();
  await ensurePythonExists();

  protocol.registerFileProtocol('app', (request, callback) => {
    const url = request.url.substring(6);
    callback({ path: path.normalize(path.join(__dirname, '..', 'va21-omni-agent', 'frontend', 'public', `${url}.html`)) });
  });

  const pythonExecutable = getPythonExecutablePath();
  const backendScript = path.join(MODEL_PATH, 'app.py');

  console.log(`Spawning backend: ${pythonExecutable} ${backendScript} --settings_path ${SETTINGS_PATH}`);
  pythonProcess = spawn(pythonExecutable, [backendScript, '--settings_path', SETTINGS_PATH], { cwd: MODEL_PATH });
  pythonProcess.stdout.on('data', (data) => console.log(`Python Backend: ${data}`));
  pythonProcess.stderr.on('data', (data) => console.error(`Python Backend Error: ${data}`));
  pythonProcess.on('close', (code) => console.log(`Python backend process exited with code ${code}`));

  createWindow();
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });

app.on('will-quit', () => { if (pythonProcess) pythonProcess.kill(); });

// --- Settings IPC ---
ipcMain.handle('settings:get', async () => {
    try {
        if (fs.existsSync(SETTINGS_PATH)) {
            const settings = fs.readFileSync(SETTINGS_PATH, 'utf-8');
            return JSON.parse(settings);
        }
    } catch (error) {
        console.error('Error reading settings file:', error);
    }
    // Return defaults if file doesn't exist or is invalid
    return { provider: 'ollama', url: 'http://localhost:11434', api_key: '', backup_provider: 'local', backup_path: '', github_pat: '' };
});
ipcMain.on('settings:save', (event, settings) => {
    try {
        fs.writeFileSync(SETTINGS_PATH, JSON.stringify(settings, null, 2));
    } catch (error) {
        console.error('Error saving settings file:', error);
    }
});

// --- Tab & Chrome IPC ---
ipcMain.on('chrome:set-height', (event, height) => {
    CHROME_HEIGHT = height;
    for (const id in views) {
        const [winWidth, winHeight] = mainWindow.getSize();
        views[id].setBounds({ x: 0, y: CHROME_HEIGHT, width: winWidth, height: winHeight - CHROME_HEIGHT });
    }
});
ipcMain.on('tabs:new', (event, tab) => {
    const { id, url } = tab;
    const [width, height] = mainWindow.getSize();
    const view = new BrowserView({ webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true } });
    views[id] = view;
    view.setBounds({ x: 0, y: CHROME_HEIGHT, width, height: height - CHROME_HEIGHT });
    view.setAutoResize({ width: true, height: true });
    view.webContents.loadURL(url);
    const wc = view.webContents;
    wc.on('page-title-updated', (evt, title) => mainWindow.webContents.send('tabs:update', { id: id, title: title }));
    wc.on('did-navigate', (evt, newUrl) => mainWindow.webContents.send('tabs:update', { id: id, url: newUrl }));
    mainWindow.addBrowserView(view);
    mainWindow.setBrowserView(view);
    activeViewId = id;
});
ipcMain.on('tabs:select', (event, id) => { const view = views[id]; if (view) { mainWindow.setBrowserView(view); activeViewId = id; } });
ipcMain.on('tabs:close', (event, id) => { const view = views[id]; if (view) { mainWindow.removeBrowserView(view); view.webContents.destroy(); delete views[id]; if (activeViewId === id) activeViewId = null; } });
ipcMain.on('tabs:navigate', (event, url) => getActiveView()?.webContents.loadURL(url));
ipcMain.on('tabs:go-back', () => getActiveView()?.webContents.canGoBack() && getActiveView().webContents.goBack());
ipcMain.on('tabs:go-forward', () => getActiveView()?.webContents.canGoForward() && getActiveView().webContents.goForward());
ipcMain.on('tabs:reload', () => getActiveView()?.webContents.reload());
ipcMain.handle('sidepanel:toggle', (event, isOpen) => {
    const view = getActiveView();
    if (view) {
        const [width, height] = mainWindow.getSize();
        const panelWidth = isOpen ? 500 : 0;
        view.setBounds({ x: 0, y: CHROME_HEIGHT, width: width - panelWidth, height: height - CHROME_HEIGHT });
    }
});
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
