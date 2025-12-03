# VA21 OS - Backend AI Services

**Om Vinayaka** 🙏

This directory contains the **backend AI services** for VA21 OS.

## Important Note

**VA21 is a full Linux operating system**, available as:
- **ISO images** for physical or virtual machine installation
- **Docker/Podman containers** for containerized deployment
- **VirtualBox VMs** for testing

**The main OS interface is NOT web-based.** It uses:
- **Zork Shell** - Text adventure command interface
- **Tiling Window Manager** - Native X11/Wayland window management
- **Terminal** - Standard Linux terminal

## This Directory

The `va21-omni-agent/backend/` provides:
1. **Local LLM Engine** - IBM Granite 4.0 via Ollama
2. **Guardian AI API** - Security analysis service
3. **REST API Server** - For system service integration

## The Real OS

The actual VA21 OS is located in:
```
va21_system/linux_os/
├── zork_shell/        # Main text adventure interface
├── window_manager/    # Tiling window manager
├── guardian/          # Guardian AI core
├── kernel/            # Kernel-level security
├── research_suite/    # Research tools
├── writing/           # Writing tools
├── journalism/        # Journalism tools
├── games/             # Built-in games (Zork!)
└── Dockerfile         # Build the OS container
```

## Running VA21 OS

```bash
# From ISO (recommended for installation)
# Download from releases page

# From Docker
cd va21_system/linux_os
./run.sh

# From source
docker build -t va21-os .
docker run -it --rm va21-os
```

## Backend Services (Optional)

These backend services can be started separately for API access:

```bash
# Install Ollama first
curl -fsSL https://ollama.com/install.sh | sh

# Download Guardian AI model
ollama pull granite4:2b

# Start API server
cd backend
python va21_server.py
```

## Frontend Directory

The `frontend/` directory is **deprecated** and will be removed.
VA21 OS does not use React, Electron, or web interfaces.

The native Zork Shell provides the user interface.

---

**Om Vinayaka - May obstacles be removed from your computing journey.**
