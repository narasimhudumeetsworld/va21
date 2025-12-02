# VA21 Research OS - The Ultimate Research Operating System

## Overview

VA21 Research OS is a **real**, stripped-down Linux-based operating system designed for secure research. It features its own **advanced desktop environment** that's more powerful than traditional DEs, with everything controllable via **natural language AI chat** or **keyboard shortcuts**.

**The go-to OS for Researchers, Writers, Journalists, and Security Experts.**

## Philosophy

> "Om Vinayaka" - Named after Lord Ganesha, the remover of obstacles, 
> VA21 removes the obstacles between professionals and secure computing.

### Design Principles

1. **Real Linux Base** - Available in both Debian and Alpine editions
2. **Full GNU Toolkit** - Complete GNU/Linux userland with glibc support
3. **AI-Powered Control** - Chat with Helper AI to control everything
4. **Keyboard-Driven** - Every action has a keyboard shortcut
5. **Guardian AI Protection** - AI-powered security at system level
6. **Zork-Style Interface** - Unique text adventure command interaction
7. **Spotlight Launcher** - Cmd/Ctrl+Space for universal access
8. **Tiling Window Manager** - Full keyboard control

## 🎮 Control Everything with Chat or Keyboard

VA21's revolutionary interface lets you control **everything** through natural language:

### Chat with Helper AI
```
You: "turn on wifi"
AI: WiFi enabled ✓

You: "connect to MyNetwork"
AI: Connected to MyNetwork with 85% signal ✓

You: "set volume to 50"
AI: Volume: 50% ✓

You: "what time is it"
AI: The time is 3:45 PM ✓

You: "dark mode"
AI: Switched to dark theme ✓

You: "battery status"
AI: Battery is at 78% (on battery) ✓
```

### Or Use Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Launcher | `Ctrl+Space` |
| Command Palette | `Ctrl+K` |
| Toggle Theme | `Ctrl+Shift+T` |
| Volume Up/Down | `Ctrl+Up/Down` |
| Brightness Up/Down | `Ctrl+Shift+Up/Down` |
| Mute | `Ctrl+M` |
| New Terminal | `Ctrl+T` |
| Lock Screen | `Super+L` |
| Take Screenshot | `Print` or `Ctrl+Shift+S` |
| Toggle WiFi | `Ctrl+Alt+W` |
| System Status | `Ctrl+Alt+S` |
| Open Settings | `Ctrl+,` |
| Help | `F1` |

## 📦 Two Editions

### Debian Edition (Full GNU)
- Complete GNU toolkit with glibc
- Maximum compatibility with Linux software
- Ideal for desktop installation
- ~500MB base image

```bash
docker build -f Dockerfile.debian -t va21-os:debian .
docker run -it --rm va21-os:debian
```

### Alpine Edition (Lightweight)
- musl libc + BusyBox
- Minimal footprint (~100MB)
- Perfect for containers and VMs
- Fast boot times

```bash
docker build -f Dockerfile.alpine-desktop -t va21-os:alpine .
docker run -it --rm va21-os:alpine
```

## ⚙️ Built-in Settings

All settings are accessible via chat or the Settings Center:

### 📶 WiFi & Network
- Scan and connect to networks
- View signal strength
- Forget saved networks
- Toggle WiFi on/off

### 🕐 Date & Time
- Set timezone
- Sync with NTP
- View current time/date

### 🔊 Sound
- Volume control (0-100%)
- Mute/unmute
- Audio device selection

### 🔆 Display
- Brightness control
- Resolution settings
- Multi-monitor support

### 🎨 Appearance
- Dark/Light theme
- Accent colors
- Font settings

### 🔋 Power
- Battery status
- Power profiles (Performance/Balanced/Saver)
- Sleep/Suspend settings

## 🎮 Bundled Games

VA21 comes with classic text adventure games, just like Windows used to bundle games!

### Mini Zork (Built-in)
A Zork-inspired adventure written in Python - no setup needed!

```
> play mini_zork

West of House
You are standing in an open field west of a white house,
with a boarded front door. There is a small mailbox here.

> open mailbox
Opening the mailbox reveals a leaflet...
```

### Classic Zork Trilogy (Optional)
The legendary games that inspired VA21's interface:

| Game | Year | Description |
|------|------|-------------|
| 🏰 Zork I | 1980 | The Great Underground Empire |
| 🧙 Zork II | 1981 | The Wizard of Frobozz |
| 👑 Zork III | 1982 | The Dungeon Master |

Historical source available at:
- https://github.com/historicalsource/zork1
- https://github.com/historicalsource/zork2
- https://github.com/historicalsource/zork3

### Play Games
```
> games                    # Show games menu
> play mini_zork          # Start built-in adventure
> play zork1              # Play Zork I (if installed)
```

Or ask the AI: *"let's play zork"*

## Features by Audience

### 🔬 For Researchers
- **Research Suite** - Literature management, citation generation (20+ styles)
- **Obsidian Vault** - Knowledge management with wiki-links
- **Data Analysis** - Experiment tracking, data visualization
- **Collaboration** - Project management, team features
- **Ethics Checklist** - Built-in research ethics guidelines

### ✍️ For Writers
- **Writing Suite** - Document creation, templates
- **Citation Manager** - APA, MLA, Chicago, Harvard, IEEE...
- **Export Options** - Markdown, HTML, PDF, DOCX
- **Distraction-free** - Focus mode for writing
- **AI Assistance** - Writing suggestions, improvements

### 📰 For Journalists
- **Source Protection** - Secure source management
- **Fact-Checking** - Verification workflow
- **FOIA Manager** - Track public records requests
- **Deadline Tracker** - Never miss a deadline
- **Story Pipeline** - Idea to publication workflow
- **Legal Checklist** - Pre-publication review

### 🔒 For Security Experts
- **Security Toolkit** - Hash analysis, cryptography tools
- **Forensics** - File analysis, log parsing
- **Vulnerability Management** - Track and document findings
- **Incident Response** - IR checklist and workflow
- **CTF Tools** - Hints and utilities for competitions
- **Network Analysis** - Port scanning, URL analysis

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21/va21_system/linux_os

# Run VA21 Research OS (Alpine - lightweight)
./run.sh

# Or run Debian edition
docker build -f Dockerfile.debian -t va21-os:debian .
docker run -it --rm va21-os:debian
```

### Using Podman

```bash
cd va21/va21_system/linux_os
./run.sh podman

# Or manually:
podman build -t va21-research-os .
podman run -it --rm va21-research-os
```

### Using Docker Compose

```bash
# Start in background
docker-compose up -d

# Enter the Zork interface
docker-compose exec va21 va21

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VA21 Research OS                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Zork-Style Text Interface              │   │
│  │   "You are in the Research Lab. Guardian watches." │   │
│  │   [Toggleable Hints for Newcomers]                  │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Guardian AI │  │   SearXNG    │  │   ClamAV         │  │
│  │  (Security)  │  │  (Search)    │  │  (Antivirus)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │     Alpine Linux + BusyBox (Minimal Userland)       │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│         Docker / Podman / VirtualBox Container              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Alpine Linux Base
- Minimal Linux distribution (~5MB)
- BusyBox for essential utilities
- Python for Guardian AI and tools

### 2. Guardian AI
- AI-powered security monitoring
- Command analysis and threat detection
- Pattern-based malicious code detection
- Integrated with ClamAV for virus scanning

### 3. ClamAV Integration
- Open-source antivirus engine
- Community-maintained virus database
- File and directory scanning
- Quarantine capability

### 4. SearXNG Integration
- Privacy-respecting metasearch engine
- Multiple search categories (general, news, science, IT)
- No tracking or ads
- Can use public instances or self-hosted

### 5. Zork-Style Interface
- Text adventure game interaction
- Rooms = system contexts
- Items = tools and resources
- Guardian AI as NPC companion
- Toggleable hints for beginners

## Building VA21 OS

### Prerequisites

You need either Docker or Podman installed:

```bash
# Docker (Ubuntu/Debian)
sudo apt-get install docker.io docker-compose

# Podman (Ubuntu/Debian)  
sudo apt-get install podman podman-compose

# macOS
brew install docker  # or podman
```

### Build and Run

```bash
# Clone the repository
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21/va21_system/linux_os

# Build and run (auto-detects docker/podman)
./run.sh

# Or build only
./run.sh build
```

## Usage - Zork-Style Interface

When VA21 OS boots, you enter a text adventure world:

```
========================================
   VA21 Research OS v1.0 (Vinayaka)
========================================

You awaken in the BOOT CHAMBER. The ancient Guardian AI 
stirs to life, its amber eyes watching you carefully.

"Welcome, Researcher," the Guardian speaks. "What knowledge
do you seek today?"

> look

You are in the BOOT CHAMBER.
A warm glow emanates from the GUARDIAN CORE in the center.
Exits: NORTH (Research Lab), EAST (Knowledge Vault), 
       WEST (Terminal Nexus), DOWN (Kernel Depths)

Items here: research_kit, security_manual

The GUARDIAN AI hovers nearby, ready to assist.

> go north

You enter the RESEARCH LAB.
Workbenches line the walls, covered with analysis tools.
A large KNOWLEDGE GRAPH pulses with interconnected nodes.

> ask guardian about security

The Guardian AI's eyes glow brighter.
"Security is paramount here. I monitor all syscalls, 
analyze all network traffic, and protect the sacred 
kernel from intrusion. Would you like me to perform
a security scan?"

> yes

The Guardian begins scanning...
[████████████████████████] 100%

"All clear. No threats detected. The Research OS 
is secure."
```

### Command Reference

| Adventure Command | System Action |
|------------------|---------------|
| `look` | Show current context/status |
| `go <direction>` | Change to different system context |
| `examine <item>` | Get detailed info about a resource |
| `take <item>` | Load a tool/module |
| `use <item>` | Execute a tool |
| `ask guardian <topic>` | Query Guardian AI |
| `search <query>` | Search internet (SearXNG) |
| `scan <path>` | Scan for threats (ClamAV) |
| `shell <cmd>` | Run a shell command |
| `inventory` | List loaded tools |
| `hints on/off` | Toggle helper hints |
| `save` | Create system snapshot |
| `quit` | Exit VA21 Research OS |

### System Contexts (Rooms)

| Room | System Area |
|------|-------------|
| Boot Chamber | System initialization |
| Research Lab | Main research environment |
| Knowledge Vault | Document/note storage |
| Terminal Nexus | Shell access |
| Kernel Depths | Low-level system access |
| Network Tower | Network monitoring |
| Guardian Sanctum | Security controls |
| Sandbox Arena | Isolated execution |

## Directory Structure

```
va21_system/linux_os/
├── Dockerfile              # Container build file
├── docker-compose.yml      # Compose configuration
├── run.sh                  # Quick start script
├── requirements.txt        # Python dependencies
├── guardian/
│   ├── guardian_core.py    # Main Guardian AI
│   └── clamav_integration.py # ClamAV antivirus
├── searxng/
│   └── searxng_client.py   # SearXNG search
├── zork_shell/
│   └── zork_interface.py   # Text adventure shell
├── scripts/
│   └── entrypoint.sh       # Container entry
└── config/
    └── va21.yaml           # Configuration
```

## Running Modes

### 1. Docker (Recommended)
```bash
./run.sh docker
# or
docker-compose up -d
```

### 2. Podman
```bash
./run.sh podman
```

### 3. VirtualBox
```bash
./run.sh vbox
# Follow instructions to import into VirtualBox
```

## Security Features

### Guardian AI
- **Command Analysis**: AI-powered threat detection
- **Pattern Matching**: Blocks dangerous commands
- **Behavior Monitoring**: Anomaly detection
- **Real-time Protection**: Always watching

### ClamAV Integration
- **Virus Scanning**: Open-source antivirus engine
- **Regular Updates**: Community-maintained signatures
- **Quarantine**: Isolate detected threats
- **Full Scan**: Scan files and directories

### Container Security
- **Isolation**: Runs in isolated container
- **Resource Limits**: Controlled CPU/memory
- **Non-root User**: Runs as 'researcher' user
- **Read-only Layers**: Immutable base system

## Hints System

VA21 Research OS includes a toggleable hints system to help newcomers:

```
> hints on    # Enable helpful hints
> hints off   # Disable hints (for experts)
> hints show  # Show a hint for current location
```

Hints provide contextual help like:
- 💡 Hint: Type 'look' to examine your surroundings
- 💡 Hint: Use 'search <query>' to research on the internet
- 💡 Hint: Try 'scan <path>' to check for threats

## License

This project is licensed under the Prayaga Vaibhav Proprietary License.
Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.

## Acknowledgments

- Alpine Linux Project
- ClamAV Team (Open Source Antivirus)
- SearXNG Project (Privacy Search)
- Classic Zork (Infocom) for interface inspiration
