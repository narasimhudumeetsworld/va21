# VA21 Omni Agent - One-Line Installation

**Quick Install (Linux/macOS):**

```bash
curl -fsSL https://raw.githubusercontent.com/narasimhudumeetsworld/va21/main/install.sh | bash
```

**Manual Installation:**

1. Download the installer:
   ```bash
   curl -L https://raw.githubusercontent.com/narasimhudumeetsworld/va21/main/install.sh -o install.sh
   chmod +x install.sh
   ./install.sh
   ```

2. After installation, run:
   ```bash
   cd ~/va21-omni-agent
   ./va21-launcher.sh
   ```

**What the installer does:**
- ✅ Downloads the VA21 Omni Agent repository
- ✅ Sets up a portable Python environment  
- ✅ Installs all required dependencies
- ✅ Downloads the Guardian AI security model
- ✅ Creates launcher scripts for easy startup
- ✅ Configures the secure localhost server

**Windows Installation:**
Download and run `va21-launcher.bat` after cloning the repository.

**System Requirements:**
- Python 3.8+ (for portable environment)
- 2GB RAM minimum (4GB recommended) 
- 1GB disk space for models and dependencies
- Internet connection for initial setup

**Security Features Included:**
- 🛡️ Guardian AI Security Core (ONNX-based)
- 🔒 Air Gap Browser Protection  
- 🕵️ Real-time Threat Intelligence
- 🔄 Self-Analysis & Healing
- ⏱️ 5-Day Quarantine Protocol
- 🌐 Localhost-only Operation