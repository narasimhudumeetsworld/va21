# VA21 OS - Backend Services

**Om Vinayaka** 🙏

This directory contains the backend services for VA21 OS. 

## Important Note

**VA21 is a full operating system**, not a web or Electron application.

The main OS interface is:
- **Zork Shell** (`va21_system/linux_os/zork_shell/`) - Text adventure interface
- **Tiling Window Manager** (`va21_system/linux_os/window_manager/`) - Native window management
- **Guardian AI** - Security core powered by IBM Granite 4.0 via Ollama

## Backend Components

This backend provides:
1. **Local LLM Engine** - IBM Granite 4.0 via Ollama
2. **Guardian AI** - Security analysis service
3. **API Server** - REST API for system services

## Running the Backend

```bash
# Install Ollama first
curl -fsSL https://ollama.com/install.sh | sh

# Download Guardian AI model
ollama pull granite4:2b

# Start the backend
cd backend
python va21_server.py
```

## Frontend Note

The `frontend/` directory contains a React-based web dashboard that can optionally be used for remote administration. It is **NOT** the main OS interface.

The actual OS uses native Linux components:
- Native tiling window manager
- Zork-style text adventure shell
- Terminal-based applications

## Directory Structure

```
va21-omni-agent/
├── backend/           # Python backend services
│   ├── local_llm.py  # IBM Granite 4.0 via Ollama
│   ├── kernel_guardian.py  # Security core
│   └── va21_server.py      # API server
└── frontend/          # Optional web dashboard (NOT main UI)
```

## Core Philosophy

VA21 OS is a self-correcting, security-conscious, AI-native operating system designed for research, development, and secure computing.

**Om Vinayaka - May obstacles be removed from your computing journey.**
