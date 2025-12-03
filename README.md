# VA21 OS - Secure AI-Powered Linux Operating System

**Om Vinayaka** 🙏

## 🛡️ A Complete Linux Operating System

VA21 OS is a **full Linux operating system** designed for researchers, writers, journalists, and security professionals. It's a real OS that you install on your computer - not an app, not a container.

![VA21 OS Interface](https://github.com/user-attachments/assets/a6013877-03bd-40c1-8bb5-d41e3385f1da)

### What is VA21 OS?

- **Full Linux OS** based on Debian GNU/Linux
- **Zork-style text adventure interface** for unique interaction
- **Native tiling window manager** for efficient multitasking
- **Guardian AI security** powered by IBM Granite 4.0 via Ollama
- **~5 GB base installation** (AI models downloaded during install)

### Installation

Download the ISO from the [Releases page](../../releases) and install like any Linux distribution:

| Edition | Description | Size |
|---------|-------------|------|
| **VA21 OS Debian** | Full GNU toolkit, maximum compatibility | ~5 GB |
| **VA21 OS Alpine** | Lightweight, fast boot | ~2 GB |

```bash
# Write ISO to USB drive
sudo dd if=va21-os.iso of=/dev/sdX bs=4M status=progress

# Or use in VirtualBox/VMware
# Create VM → Use ISO as boot disk → Install
```

### Quick Start (From Source)

```bash
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21/va21_system/linux_os
./scripts/build_iso.sh debian
# ISO will be in output/ directory
```

---

## ✨ Features

### 🎮 Zork-Style Interface

VA21 OS features a unique text adventure interface inspired by classic Zork:

```
========================================
   VA21 Research OS v1.0 (Vinayaka)
========================================

You awaken in the BOOT CHAMBER. The ancient Guardian AI 
stirs to life, its amber eyes watching you carefully.

"Welcome, Researcher," the Guardian speaks.

> look

You are in the BOOT CHAMBER.
Exits: NORTH (Research Lab), EAST (Knowledge Vault)

> go north

You enter the RESEARCH LAB...
```

### 🎤 Voice Intelligence Layer
Complete multilingual voice processing with 1,600+ language support:

| Component | Technology | License | Purpose |
|-----------|------------|---------|---------|
| ASR (Primary) | [Meta Omnilingual ASR](https://github.com/facebookresearch/fairseq) | Apache 2.0 | 1,600+ languages |
| ASR (Secondary) | [Whisper/Solus AI](https://github.com/openai/whisper) | MIT | Offline backup |
| Wake Word | [Rhasspy](https://github.com/rhasspy/rhasspy) | MIT | Custom triggers |
| TTS (Fast) | [Piper](https://github.com/rhasspy/piper) | MIT | Fast synthesis |
| TTS (Premium) | [Kokoro](https://github.com/remsky/Kokoro-FastAPI) | Apache 2.0 | Premium voices |
| LLM Processing | [LangChain](https://github.com/langchain-ai/langchain) + [Granite 4.0](https://ollama.com/library/granite4) | MIT + Apache 2.0 | AI reasoning |
| Security | Guardian AI + [LLM Guard](https://github.com/protectai/llm-guard) | Proprietary + MIT | Safety layer |

**Indian Language Support:** Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Malayalam, Punjabi, and 100+ more!

### 🔒 Guardian AI Security
Powered by IBM Granite 4.0 via Ollama:
- **Think → Vet → Act** methodology
- **Real-time threat analysis**
- **ClamAV antivirus integration**
- **Air gap browser protection**

### 🔒 AI Privacy & Security System
Powered by [IBM AI Privacy Toolkit](https://github.com/IBM/ai-privacy-toolkit) (MIT) + [LLM Guard](https://github.com/protectai/llm-guard) (MIT):
- **Data Anonymization**: GDPR-compliant AI processing
- **Prompt Injection Detection**: Blocks malicious inputs
- **Output Scanning**: Filters harmful content

### 🤖 Multi-Agent Task Automation System
Inspired by [Microsoft AutoGen](https://github.com/microsoft/autogen), [Agent Zero](https://github.com/agent0ai/agent-zero), and [OpenCode](https://github.com/sst/opencode):

- **Multi-Agent Conversation Framework**: Agents collaborate autonomously
- **Specialized Agents**: Code Agent, Research Agent, Reflection Agent
- **Orchestrator Agent**: Coordinates all specialized agents
  - *Aligns with VA21's Microsoft FARA integration*

- **Multi-Agent Roles** (inspired by OpenCode):
  - **Build Agent**: Full access for development work
  - **Plan Agent**: Read-only for analysis and safe exploration
  - **General Agent**: Complex multi-step task handling

- **Agent Cooperation** (inspired by Agent Zero):
  - Hierarchical superior/subordinate agent relationships
  - Agent-to-agent communication protocols
  - Persistent memory for solutions and instructions
  - Dynamic tool creation by agents

- **Enhanced VA21 Architecture**:
  ```
  Guardian AI + Orchestrator AI + Helper AI + AutoGen Agents + Embedding AI
  ```
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

### Disk Space Requirements
- **VA21 OS Base Installation**: ~5 GB (includes Zork UI, Guardian AI, all features)
- **With All AI Models**: ~10 GB (full model suite downloaded during install)

> **Note:** Guardian AI model is always included. Other AI models are downloaded on-demand during first use.
> See [docs/MODEL_REQUIREMENTS.md](docs/MODEL_REQUIREMENTS.md) for detailed breakdown.

### Minimum Requirements (7GB RAM)
- **Debian-based Linux** (Debian 12+, Ubuntu 22.04+, Linux Mint 21+)
- **Python 3.8+**
- **7GB RAM** (for standard usage with AI features)
- **5GB disk space** for VA21 OS base installation
- **Flatpak** (optional, for App Center)

### Recommended Requirements (10GB RAM)
- **8-10GB RAM** (for heavy multitasking with all AI models)
- **10GB disk space** for full installation with all AI models
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
- **AI Models**: IBM Granite, Microsoft ONNX/FARA, Meta LLaMA, Meta Omnilingual ASR
- **Voice**: Meta Omnilingual ASR, Whisper, Rhasspy, Piper TTS, Kokoro TTS
- **Security**: Guardian AI, LLM Guard, IBM AI Privacy Toolkit
- **Multi-Agent**: Microsoft AutoGen, Agent Zero patterns, OpenCode patterns

## 🙏 Acknowledgments

VA21 OS is built on the shoulders of giants:

### Voice Intelligence Layer
- **Meta Omnilingual ASR** - [Apache 2.0] ⭐⭐⭐⭐⭐
  1,600+ languages including 100+ Indian dialects (Released November 2025)
- **OpenAI Whisper** - [github.com/openai/whisper](https://github.com/openai/whisper) (MIT) - Offline backup ASR
- **Rhasspy** - [github.com/rhasspy/rhasspy](https://github.com/rhasspy/rhasspy) (MIT) - Wake word detection
- **Piper TTS** - [github.com/rhasspy/piper](https://github.com/rhasspy/piper) (MIT) - Fast TTS synthesis
- **Kokoro TTS** - [github.com/remsky/Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) (Apache 2.0) - Premium voices

### Security & Privacy
- **IBM AI Privacy Toolkit** - [github.com/IBM/ai-privacy-toolkit](https://github.com/IBM/ai-privacy-toolkit) (MIT) - GDPR compliance
- **LLM Guard** - [github.com/protectai/llm-guard](https://github.com/protectai/llm-guard) (MIT) - LLM security
- **LMDeploy** - [github.com/InternLM/lmdeploy](https://github.com/InternLM/lmdeploy) (Apache 2.0) - Efficient LLM deployment

### Multi-Agent Automation
- **Microsoft AutoGen** - [github.com/microsoft/autogen](https://github.com/microsoft/autogen) (MIT) ⭐⭐⭐⭐⭐
  Multi-agent conversation framework (Backed by Microsoft Research)
- **Agent Zero** - [github.com/agent0ai/agent-zero](https://github.com/agent0ai/agent-zero) (MIT)
  Multi-agent cooperation patterns
- **OpenCode** - [github.com/sst/opencode](https://github.com/sst/opencode) (MIT)
  Role-based agents (Build/Plan)

### LLM & AI Processing
- **LangChain** - [github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) (MIT) - AI orchestration
- **IBM Granite** - [huggingface.co/ibm-granite](https://huggingface.co/collections/ibm-granite/granite-40-language-models) (Apache 2.0)
- **Microsoft** - ONNX Runtime, FARA, AutoGen, Phi models (MIT)
- **Meta AI** - Omnilingual ASR (Apache 2.0), LLaMA, PyTorch
- **Hugging Face** - Democratizing AI model access
- **Ollama** - Simple local LLM deployment (MIT)

### Open Source Foundation
- **Debian Project** - Rock-solid OS foundation
- **Linux Foundation** - Linux kernel stewardship
- **Linux Community** - Every contributor who makes open source possible
- **Flathub** - Revolutionizing Linux application distribution

## 📄 License

This project is licensed under a modified Apache License 2.0 with proprietary components.
- **Permissive (Apache 2.0)**: Most features with acknowledgment
- **Proprietary**: Guardian AI, Think>Vet>Act, Sandbox Testing, Anti-Hallucination Engine

See [LICENSE](LICENSE) for full terms and acknowledgments.

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.

---

**🛡️ VA21 OS - Secure by Design, Intelligent by Nature** 🐧
