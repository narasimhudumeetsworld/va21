# VA21 OS - The Next Generation Secure Desktop Environment

## 🛡️ Security-First AI-Powered Operating System

VA21 OS is a revolutionary Debian-based operating system that combines enterprise-grade security with cutting-edge AI capabilities. Built on the rock-solid foundation of Debian GNU/Linux, VA21 OS represents a new paradigm in secure computing.

![VA21 OS Interface](https://github.com/user-attachments/assets/a6013877-03bd-40c1-8bb5-d41e3385f1da)

## ✨ What's New in VA21 OS

### 🤖 Multi-Agent Task Automation System (NEW!)
Inspired by the best features from [Agent Zero](https://github.com/agent0ai/agent-zero) and [OpenCode](https://github.com/sst/opencode):

- **Multi-Agent Roles** (inspired by OpenCode):
  - **Build Agent**: Full access for development work
  - **Plan Agent**: Read-only for analysis and safe exploration
  - **General Agent**: Complex multi-step task handling
  - **Security Agent**: Guardian AI integration

- **Agent Cooperation** (inspired by Agent Zero):
  - Hierarchical superior/subordinate agent relationships
  - Agent-to-agent communication protocols
  - Persistent memory for solutions and instructions
  - Dynamic tool creation by agents

- **All Protected by Guardian AI**:
  - Think>Vet>Act methodology for every action
  - Sandboxed execution environment
  - Real-time security monitoring

### 🧠 Dynamic AI Quantization System (NEW!)
- **Adaptive Performance**: AI models automatically quantize to 4-bit, 5-bit, or 8-bit based on available system memory
- **Memory-Aware Loading**: Intelligent model loading and unloading
- **Quality Preservation**: Optimal quality-to-memory tradeoffs

### 📚 Tiered Memory System with Obsidian Brain Maps (NEW!)
- **Three-Tier Architecture**:
  - Working Memory (current context)
  - Short-Term Memory (session)
  - Long-Term Memory (persistent)
- **Separate Knowledge Bases**: Each AI (Guardian, Helper, Agent) has its own memory space
- **Interconnected Context**: Tiered tags and context-aware retrieval
- **Anti-Hallucination Engine**: Validates all AI memory retrieval

### 🎨 Futuristic Interface & Easter Eggs
- **Halo/Cortana Theme**: Type "cortana call the masterchief" to activate a stunning holographic interface inspired by the Halo universe
- **Dark/Light Theme Toggle**: Switch between themes with Ctrl+Shift+T
- **Command Palette**: Quick access to all commands with Ctrl+K
- **Minimal Toggle Option**: Easy theme switching from settings

### 💾 Advanced Backup with Version History
- **Automatic Periodic Backups**: Never lose your work again
- **Pre-Reset Safety Backups**: Easily restore during system reset
- **Version History Timeline**: Browse and restore from any point in time
- **Helper AI Integration**: Ask the AI to restore from backups naturally
- **Compression & Auto-Cleanup**: Efficient storage management

### 📦 App Center with Flathub & Debian Integration
- **One-Click App Installation**: Search, preview, and install apps easily
- **Flatpak Support**: Access thousands of sandboxed applications via Flathub
- **Debian Packages**: Full access to the vast Debian repository
- **Spotlight-Like Search**: Find and install apps right from the command palette

### 🔌 FARA App Compatibility Layer (Alpha)
- **Microsoft FARA-Inspired Technology**: Intelligent UI automation for legacy apps
- **Screenshot-Based Analysis**: Visual understanding of application interfaces
- **Legacy GTK2/Qt4 Support**: Seamless integration with older applications
- **Wine Compatibility**: Run Windows applications with FARA assistance
- **Context-Aware Automation**: AI-driven action planning for complex workflows

### 🤖 Intelligent Helper AI
- **Backup Knowledge**: AI knows your version history (sanitized for security)
- **Natural Language Restoration**: Just ask "restore from yesterday"
- **System Awareness**: Get status updates and recommendations
- **Task Automation**: Request automated tasks through natural conversation
- **Easter Egg Activation**: Fun interactions unlock special features

## 🔒 Core Security Architecture

### Triple-AI System
- **Guardian AI (Security Core)**: Always-active security analysis using ONNX models with Think>Vet>Act methodology
- **Helper AI (User Interface)**: User-facing assistant with backup and system knowledge
- **Multi-Agent System (Automation)**: Task automation with Guardian AI oversight
- **Air Gap Protection**: Complete isolation from screen content and sensitive data
- **Principle of Least Privilege**: No direct website interactions or form submissions

### Security Features
- ✅ **Real-time Threat Analysis**: Every input analyzed before processing
- ✅ **Self-Analysis & Healing**: Autonomous code security scanning
- ✅ **5-Day Quarantine Protocol**: Safe integration of external intelligence
- ✅ **Localhost-Only Operation**: No external network exposure
- ✅ **Pattern-Based Detection**: Advanced malware and injection detection
- ✅ **Anti-Hallucination Engine**: Prevents AI from making up information

## 🔬 Research Command Center

### Multiple Sandboxed Terminals
- **Tiling Window Management**: Run multiple terminal sessions with quad, triple, or six-pane layouts
- **Isolation Levels**: Minimal, Standard, and Strict sandbox levels
- **Session Logging**: All terminal activity logged to the knowledge vault

### Obsidian-Style Knowledge Vault
- **Wiki-Style Links**: Create interconnected notes with `[[link]]` syntax
- **Knowledge Graph**: Visual representation of your research connections
- **LLM Memory Integration**: Persistent memory for AI context
- **Brain Maps**: Visual memory maps for each AI component

### Sensitive Information Protection
- **Automatic Redaction**: Detect and redact API keys, passwords, tokens
- **Category-Based Filtering**: Control what gets redacted

## 🚀 Quick Installation

### One-Line Install (Debian/Ubuntu)
```bash
curl -fsSL https://raw.githubusercontent.com/narasimhudumeetsworld/va21/main/install.sh | bash
```

### Docker Installation
```bash
cd va21-omni-agent
docker-compose up -d
```

Access the interface at: **http://localhost:5000**

## 📋 System Requirements

### Minimum Requirements (7GB RAM)
- **Debian-based Linux** (Debian 12+, Ubuntu 22.04+, Linux Mint 21+)
- **Python 3.8+**
- **7GB RAM** (for standard usage with AI features)
- **2GB disk space** for models and dependencies
- **Flatpak** (optional, for App Center)

### Recommended Requirements (10GB RAM)
- **8-10GB RAM** (for heavy multitasking with all AI models)
- **4GB disk space** for full model suite
- **Modern CPU** (Intel Core i5/AMD Ryzen 5 or better)
- **SSD storage** for faster model loading

### Memory Optimization
VA21 uses **dynamic context-aware AI activation** to minimize RAM usage:
- 🧠 **Lazy Loading** - Models loaded only when needed
- 📦 **Dynamic Quantization** - 4-bit, 5-bit, or 8-bit based on available RAM
- 🔄 **Context-Aware Unloading** - Automatic memory management
- 💾 **Memory Mapping** - Efficient large file handling

| Usage Scenario | RAM Required | Quantization | Description |
|---------------|--------------|--------------|-------------|
| Minimal | ~3GB | 4-bit | Basic browsing, text editing |
| Standard | ~5GB | 5-bit | Multiple apps, AI chat |
| Heavy Multitasking | ~7GB | 8-bit | Many apps, FARA compatibility |
| Full Development | ~9GB | 8-bit/FP16 | All AI features, IDE, Docker |

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open Command Palette |
| `Ctrl+B` | Toggle Side Panel |
| `Ctrl+Shift+T` | Toggle Theme |
| `Ctrl+Shift+S` | Create Backup |
| `Ctrl+Shift+R` | Open Restore Dialog |

## 🎮 Easter Eggs

- Type **"cortana call the masterchief"** in the chat to unlock the Halo interface theme!
- More secrets to discover...

## 🏗️ Technical Stack

- **OS Base**: Debian GNU/Linux
- **Backend**: Flask + Socket.IO Python server
- **Frontend**: React.js with custom theming
- **Package Management**: Flatpak + APT integration
- **AI Models**: IBM Granite, Microsoft ONNX/FARA, Meta LLaMA
- **Security**: Multi-layer protection with Guardian AI

## 🙏 Acknowledgments

VA21 OS is built on the shoulders of giants:

### Multi-Agent Automation Inspiration
- **Agent Zero** - [github.com/agent0ai/agent-zero](https://github.com/agent0ai/agent-zero) (MIT License)
  For multi-agent cooperation patterns, persistent memory concepts, and hierarchical agent design
- **OpenCode** - [github.com/sst/opencode](https://github.com/sst/opencode) (MIT License)
  For multi-agent roles (Build/Plan agents), provider-agnostic design, and read-only analysis mode

### AI & Machine Learning
- **IBM Research** - For [Granite language models](https://huggingface.co/collections/ibm-granite/granite-40-language-models) powering intelligent features
- **Microsoft** - For [ONNX Runtime](https://onnxruntime.ai/), [FARA technology](https://github.com/microsoft/fara), and Phi models
- **Meta AI** - For LLaMA models and PyTorch
- **Hugging Face** - For democratizing AI model access
- **Ollama** - For simple local LLM deployment

### Open Source Foundation

- **Debian Project** - For creating the most stable and versatile Linux distribution
- **Linux Foundation** - For their stewardship of the Linux kernel
- **Linux Community** - Every contributor who makes open source possible
- **Flathub** - For revolutionizing Linux application distribution

## 📄 License

This project is licensed under a modified Apache License 2.0 with proprietary components.
- **Permissive (Apache 2.0)**: Most features with acknowledgment
- **Proprietary**: Guardian AI, Think>Vet>Act, Sandbox Testing, Anti-Hallucination Engine

See [LICENSE](LICENSE) for full terms and acknowledgments.

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.

---

**🛡️ VA21 OS - Secure by Design, Intelligent by Nature** 🐧
