const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec } = require('child_process');
const https = require('https');

const VENDOR_DIR = path.join(__dirname, '..', 'vendor');
const PYTHON_WIN_URL = 'https://www.python.org/ftp/python/3.9.5/python-3.9.5-embed-amd64.zip';
const PYTHON_WIN_DIR = path.join(VENDOR_DIR, 'python-win');
const PYTHON_EXECUTABLE_WIN = path.join(PYTHON_WIN_DIR, 'python.exe');
const GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py';
const GET_PIP_PATH = path.join(VENDOR_DIR, 'get-pip.py');
const REQUIREMENTS_PATH = path.join(__dirname, '..', 'va21-omni-agent', 'backend', 'requirements.txt');

function executeCommand(command) {
    return new Promise((resolve, reject) => {
        console.log(`Executing: ${command}`);
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error executing command: ${command}`);
                console.error(stderr);
                reject(error);
                return;
            }
            console.log(stdout);
            resolve(stdout);
        });
    });
}

function downloadFile(url, dest) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(dest);
        https.get(url, (response) => {
            if (response.statusCode !== 200) {
                return reject(new Error(`Failed to get '${url}' (${response.statusCode})`));
            }
            response.pipe(file);
            file.on('finish', () => {
                file.close(resolve);
            });
        }).on('error', (err) => {
            fs.unlink(dest, () => reject(err));
        });
    });
}

async function setupWindows() {
    if (!fs.existsSync(VENDOR_DIR)) {
        fs.mkdirSync(VENDOR_DIR, { recursive: true });
    }

    if (fs.existsSync(PYTHON_EXECUTABLE_WIN)) {
        console.log('Python for Windows already exists.');
    } else {
        console.log('Downloading Python for Windows...');
        const zipPath = path.join(VENDOR_DIR, 'python-win.zip');
        await downloadFile(PYTHON_WIN_URL, zipPath);

        console.log('Extracting Python...');
        const decompress = require('decompress');
        await decompress(zipPath, VENDOR_DIR);
        fs.renameSync(path.join(VENDOR_DIR, 'python-3.9.5-embed-amd64'), PYTHON_WIN_DIR);
        fs.unlinkSync(zipPath);
        console.log('Python for Windows downloaded and extracted.');
    }

    console.log('Downloading get-pip.py...');
    await downloadFile(GET_PIP_URL, GET_PIP_PATH);

    console.log('Installing pip...');
    await executeCommand(`"${PYTHON_EXECUTABLE_WIN}" "${GET_PIP_PATH}"`);

    console.log('Installing dependencies from requirements.txt...');
    await executeCommand(`"${PYTHON_EXECUTABLE_WIN}" -m pip install -r "${REQUIREMENTS_PATH}"`);

    console.log('Windows Python setup complete.');
}

async function setupLinux() {
    if (!fs.existsSync(VENDOR_DIR)) {
        fs.mkdirSync(VENDOR_DIR, { recursive: true });
    }
    const pythonLinuxDir = path.join(VENDOR_DIR, 'python-linux');
    const pythonExecutable = path.join(pythonLinuxDir, 'bin', 'python');

    if (fs.existsSync(pythonExecutable)) {
        console.log('Python for Linux already exists.');
    } else {
        console.log('Creating Python virtual environment for Linux...');
        try {
            await executeCommand(`python3 -m venv ${pythonLinuxDir}`);
            console.log('Python virtual environment created.');
        } catch (error) {
            console.error('Failed to create Python virtual environment. Please ensure python3 and venv are installed.');
            throw error;
        }
    }

    console.log('Installing dependencies from requirements.txt...');
    await executeCommand(`"${pythonExecutable}" -m pip install -r "${REQUIREMENTS_PATH}"`);

    console.log('Linux Python setup complete.');
}

async function main() {
    const platform = os.platform();
    if (platform === 'win32') {
        await setupWindows();
    } else if (platform === 'darwin') {
        console.log('macOS detected. Please ensure Python 3 is installed manually.');
        // On macOS, we'll rely on the system to check for Python and prompt the user.
        // If we wanted to automate it, we would need a reliable .tar.gz link.
        // For now, we assume the main process will handle the check.
    } else if (platform === 'linux') {
        await setupLinux();
    } else {
        console.log(`Unsupported platform: ${platform}`);
    }
}

main().catch(error => {
    console.error('An error occurred during Python setup:', error);
    process.exit(1);
});
