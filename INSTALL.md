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

## System Requirements

### Minimum Requirements (7GB RAM)
- **Python 3.8+** (for portable environment)
- **7GB RAM** minimum for standard usage
- **2GB disk space** for models and dependencies
- **Internet connection** for initial setup

### Recommended Requirements (10GB RAM)
- **8-10GB RAM** for heavy multitasking with all AI features
- **4GB disk space** for full model suite
- **Modern CPU** (Intel Core i5/AMD Ryzen 5 or better)
- **SSD storage** for faster model loading

### Memory Usage by Scenario

| Usage Scenario | RAM Required | Description |
|---------------|--------------|-------------|
| Minimal | ~3GB | Basic browsing, text editing |
| Standard | ~5GB | Multiple apps, AI chat |
| Heavy Multitasking | ~7GB | Many apps, FARA compatibility |
| Full Development | ~9GB | All AI features, IDE, Docker |

### Memory Optimization Features
VA21 uses dynamic context-aware AI activation:
- 🧠 **Lazy Loading** - Models loaded only when needed
- 📦 **INT8 Quantization** - 50% model size reduction  
- 🔄 **Context-Aware Unloading** - Automatic memory management
- 💾 **Memory Mapping** - Efficient large file handling

**Security Features Included:**
- 🛡️ Guardian AI Security Core (ONNX-based)
- 🔒 Air Gap Browser Protection  
- 🕵️ Real-time Threat Intelligence
- 🔄 Self-Analysis & Healing
- ⏱️ 5-Day Quarantine Protocol
- 🌐 Localhost-only Operation
- 🔌 FARA App Compatibility Layer (Alpha)