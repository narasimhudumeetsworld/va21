# VA21 OS - Secure AI-Powered Linux Operating System

**Om Vinayaka** 🙏 - The Remover of Obstacles

## 🛡️ A Complete Linux Operating System

VA21 OS is a **full Linux operating system** designed for researchers, writers, journalists, and security professionals. It's a real OS that you install on your computer - not an app, not a container.

**🙏 Om Vinayaka AI at the CORE** - Controls everything except Guardian AI (sandboxed security)

### What is VA21 OS?

- **Full Linux OS** based on Debian GNU/Linux
- **Om Vinayaka AI** at the core - intelligent accessibility controlling all subsystems
- **Zork-style text adventure interface** for EVERY application
- **Local AI via Ollama** - Privacy-first, your data never leaves your device
- **1,600+ language support** via Meta Omnilingual ASR
- **Guardian AI security** powered by IBM Granite 4.0 (sandboxed at kernel level)
- **~5 GB base installation** (AI models downloaded during install)

### Installation

> **📢 Release Status**: VA21 OS is in active development. The OV21-omni prerelease contains the core AI components. Full ISO builds are coming soon - for now, build from source or use the Python modules directly.

Download from the [Releases page](../../releases):

| Edition | Description | Status |
|---------|-------------|--------|
| **OV21-omni** | Core AI components prerelease | ✅ Available |
| **VA21 OS Debian** | Full GNU toolkit ISO | 🚧 Coming Soon |
| **VA21 OS Alpine** | Lightweight ISO | 🚧 Coming Soon |

**Build from Source** (Recommended for now):
```bash
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21/va21_system/linux_os
./scripts/build_iso.sh debian
# ISO will be in output/ directory
```

**Or Install Components Directly**:
```bash
pip install -e va21/va21_system/linux_os/
```

### Quick Start (From Source)

```bash
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21/va21_system/linux_os
./scripts/build_iso.sh debian
# ISO will be in output/ directory
```

---

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  VA21 OS - Complete Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│  🛡️ KERNEL LEVEL - Guardian AI (Sandboxed Ollama - Port 11435)         │
│  ├── IBM Granite 4.0 2B - Isolated security AI                         │
│  ├── Completely separate from user-facing AI                           │
│  ├── Cannot be influenced by user conversations                        │
│  ├── Think → Vet → Act methodology                                     │
│  └── Independent threat analysis and blocking                          │
├─────────────────────────────────────────────────────────────────────────┤
│  🙏 OM VINAYAKA AI - CORE CONTROLLER (User-facing Ollama - Port 11434) │
│  ├── CONTROLS ALL SUBSYSTEMS (except Guardian)                         │
│  ├── Automatic Zork UX for every app when installed                    │
│  ├── Automatic FARA profiles for voice control of ANY app              │
│  ├── System-wide voice control for ALL applications                    │
│  ├── CLI tool wrappers (Gemini, Copilot, Codex, etc.)                  │
│  ├── LangChain + Obsidian mind maps knowledge base                     │
│  ├── Self-learning system that improves over time                      │
│  ├── Clarifying questions to understand user intent                    │
│  ├── Performance optimizer with model preloading                       │
│  ├── Feature discovery for new users                                   │
│  └── FARA layer executes actions across entire OS                      │
├─────────────────────────────────────────────────────────────────────────┤
│  🎤 Voice Intelligence Layer (Controlled by Om Vinayaka)               │
│  ├── Meta Omnilingual ASR (1,600+ langs) - Apache 2.0                  │
│  ├── Whisper/Solus AI (backup) - MIT                                   │
│  ├── Rhasspy (wake words) - MIT                                        │
│  ├── Piper TTS (fast) - MIT                                            │
│  ├── Kokoro TTS (premium) - Apache 2.0                                 │
│  └── Hold Super Key = Push-to-Talk (Accessibility)                     │
├─────────────────────────────────────────────────────────────────────────┤
│  🤖 Multi-Agent System (Controlled by Om Vinayaka)                     │
│  ├── Automatic role assignment (Coder, Reviewer, Planner, etc.)        │
│  ├── Experience levels (Junior, Mid, Senior, Expert)                   │
│  ├── Context summaries for each agent                                  │
│  ├── Microsoft AutoGen patterns - MIT                                  │
│  └── LangChain orchestration - MIT                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  🎮 Zork-Style Interface (Custom Created!)                             │
│  ├── Text adventure UI for EVERY application                           │
│  ├── Automatic interface generation on app install                     │
│  ├── Native tiling window manager                                      │
│  ├── Obsidian-style Knowledge Vault                                    │
│  └── Research Command Center                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  💻 Sandboxed Terminals with Zork Accessibility                        │
│  ├── Gemini CLI, Codex, GitHub Copilot CLI support                     │
│  ├── Natural language to CLI command translation                       │
│  ├── Zork narrative wrapping for all output                            │
│  └── Voice control for terminal applications                           │
├─────────────────────────────────────────────────────────────────────────┤
│  🧠 Self-Learning System                                               │
│  ├── Learns common command patterns                                    │
│  ├── Tracks user preferences                                           │
│  ├── Monitors app usage patterns                                       │
│  ├── Improves narratives over time                                     │
│  └── Gets smarter with continued use!                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  💾 Debian GNU/Linux Foundation                                        │
│  ├── Full GNU toolkit                                                  │
│  ├── Debian package management                                         │
│  ├── Flatpak integration                                               │
│  └── ISO releases for real hardware install                            │
└─────────────────────────────────────────────────────────────────────────┘
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

### 🎤 Voice Intelligence Layer (Meta Omnilingual ASR)

Complete multilingual voice processing with **1,600+ language support** including **100+ Indian dialects**:

| Component | Technology | License | Purpose |
|-----------|------------|---------|---------|
| **ASR (Primary)** | [Meta Omnilingual ASR](https://github.com/facebookresearch/fairseq) ⭐⭐⭐⭐⭐ | Apache 2.0 | 1,600+ languages (Released Nov 2025) |
| **ASR (Backup)** | [OpenAI Whisper](https://github.com/openai/whisper) | MIT | Offline backup ASR |
| **Wake Word** | [Rhasspy](https://github.com/rhasspy/rhasspy) | MIT | Custom wake word detection |
| **TTS (Fast)** | [Piper TTS](https://github.com/rhasspy/piper) | MIT | Fast speech synthesis |
| **TTS (Premium)** | [Kokoro TTS](https://github.com/remsky/Kokoro-FastAPI) | Apache 2.0 | Premium natural voices |
| **Local LLM** | [Ollama](https://ollama.com) + [IBM Granite](https://huggingface.co/ibm-granite) | MIT + Apache 2.0 | Privacy-first local AI |

**Indian Language Support:** Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Malayalam, Punjabi, Odia, Assamese, and **100+ more dialects!**

### ♿ Intelligent Accessibility with Om Vinayaka AI (Unique to VA21!)

VA21's accessibility goes **far beyond traditional screen readers**. Powered by the **Om Vinayaka Accessibility Knowledge Base AI**:

| Traditional Screen Readers | VA21 + Om Vinayaka AI |
|---------------------------|-------------------------------|
| Reads keywords: "menu", "button" | Explains purpose: "This saves your work" |
| No context awareness | Understands your intent and current task |
| Just announces elements | Asks clarifying questions when needed |
| User must know commands | Natural conversation in any language |
| Single app support | **Zork-style UX for EVERY app** |
| Limited CLI support | **Wraps CLI tools like Gemini, Copilot, Codex** |

**Om Vinayaka AI Features:**
- **Automatic Zork UX Generation**: Every app gets a text adventure interface when installed
- **System-Wide Voice Control**: Control ANY application with voice, not just specific apps
- **CLI Tool Wrapper**: Gemini CLI, GitHub Copilot CLI, Codex, and more - all accessible via Zork interfaces
- **Knowledge Base**: LangChain + Obsidian mind maps store all app interfaces
- **Clarifying Questions**: AI asks for details when your intent is unclear
- **Context-Aware Execution**: Understands what app is active and what you want

**How it works:**
- **Hold Super Key**: Activates voice detection
- **Speak naturally**: "I want to search the internet" or "Save my document"
- **Om Vinayaka AI understands**: Asks clarifying questions if needed
- **FARA Layer executes**: Performs action in any application
- **1,600+ languages**: Hindi, Tamil, Telugu, Spanish, French, and more

**Example conversation:**
```
User: "I want to find something on the internet"
VA21: "I can help you search. What would you like to look up?"
User: "Climate change research papers"
VA21: "Searching for climate change research papers. I'm using 
      privacy-respecting search so your query isn't tracked."
```

**CLI Tool Accessibility Example:**
```
User: "Ask Gemini about Python decorators"
VA21: "You stand before the GEMINI ORACLE, a shimmering portal of AI wisdom.
      The oracle considers your question deeply...
      [Gemini's response about Python decorators]
      What else would you like to ask?"
```

### 🔒 Guardian AI Security (Sandboxed)
Powered by IBM Granite 4.0 via **sandboxed Ollama in the kernel**:
- **Complete Isolation**: Guardian AI runs separately from user-facing AI
- **Think → Vet → Act** methodology
- **Real-time threat analysis**
- **ClamAV antivirus integration**
- **Air gap browser protection**
- **Cannot be influenced by user conversations**

### 🔒 AI Privacy & Security System
Powered by [IBM AI Privacy Toolkit](https://github.com/IBM/ai-privacy-toolkit) (MIT) + [LLM Guard](https://github.com/protectai/llm-guard) (MIT):
- **Data Anonymization**: GDPR-compliant AI processing
- **Prompt Injection Detection**: Blocks malicious inputs
- **Output Scanning**: Filters harmful content

### 🤖 Multi-Agent System with Automatic Role Assignment (NEW!)

VA21 OS includes a powerful multi-agent system that works seamlessly with Om Vinayaka AI:

**Automatic Agent Assignment:**
| Role | Experience | Responsibilities |
|------|------------|------------------|
| Orchestrator | Expert (10+ years) | Coordinates all agents, assigns tasks |
| Planner | Senior (5-10 years) | Breaks down complex tasks, estimates effort |
| Coder | Mid-Senior | Writes clean, efficient code |
| Reviewer | Senior | Reviews code for quality and security |
| Researcher | Mid | Researches topics, gathers information |
| Debugger | Senior | Identifies and fixes bugs |

**How it works:**
1. **You describe what you need** - "Build me a web scraper for news articles"
2. **Om Vinayaka AI understands** - Asks clarifying questions if needed
3. **Planner breaks it down** - Creates actionable task list
4. **Agents are auto-assigned** - Based on task type and complexity
5. **Work is executed** - Each agent focuses on their specialty
6. **Results are unified** - Om Vinayaka presents the final output

**Local AI with Ollama (Privacy-First):**
```bash
# VA21 uses local Ollama by default - your data never leaves your device!
# Models supported:
- granite3.3:2b     # General tasks (IBM Granite)
- granite-code:3b   # Code generation
- granite-guardian:2b # Security (sandboxed)

# Or use external APIs (optional):
export OPENAI_API_KEY="your-key"      # OpenAI
export ANTHROPIC_API_KEY="your-key"   # Anthropic Claude
export GROQ_API_KEY="your-key"        # Groq (fast)
```

**Agent Cooperation Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    🙏 OM VINAYAKA AI (Hub)                      │
│         Understands intent, routes to agents, learns            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Orchestr. │ │ Planner  │ │  Coder   │ │ Reviewer │           │
│  │ (Expert) │ │ (Senior) │ │  (Mid)   │ │ (Senior) │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│         │           │            │            │                 │
│         └───────────┴────────────┴────────────┘                 │
│                    LOCAL OLLAMA (Privacy)                       │
│                    or External APIs (Optional)                  │
└─────────────────────────────────────────────────────────────────┘
```

### 🧠 Dynamic AI Quantization System
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

## 🏗️ VA21 OS - Complete Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  VA21 OS - Complete Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│  🛡️ KERNEL LEVEL - Guardian AI (Sandboxed Ollama - Port 11435)         │
│  ├── IBM Granite 4.0 2B - Isolated security AI                         │
│  ├── Completely separate from user-facing AI                           │
│  ├── Cannot be influenced by user conversations                        │
│  ├── Think → Vet → Act methodology                                     │
│  └── Independent threat analysis and blocking                          │
├─────────────────────────────────────────────────────────────────────────┤
│  🙏 OM VINAYAKA ACCESSIBILITY AI (User-facing Ollama - Port 11434)     │
│  ├── Automatic Zork UX for every app when installed                    │
│  ├── System-wide voice control for ALL applications                    │
│  ├── CLI tool wrappers (Gemini, Copilot, Codex, etc.)                  │
│  ├── LangChain + Obsidian mind maps knowledge base                     │
│  ├── Self-learning system that improves over time                      │
│  ├── Clarifying questions to understand user intent                    │
│  └── FARA layer executes actions across entire OS                      │
├─────────────────────────────────────────────────────────────────────────┤
│  🎤 Voice Intelligence Layer                                           │
│  ├── Meta Omnilingual ASR (1,600+ langs) - Apache                      │
│  ├── Whisper/Solus AI (backup) - MIT                                   │
│  ├── Rhasspy (wake words) - MIT                                        │
│  ├── Piper TTS (fast) - MIT                                            │
│  ├── Kokoro TTS (premium) - Apache 2.0                                 │
│  └── Hold Super Key = Push-to-Talk (Accessibility)                     │
├─────────────────────────────────────────────────────────────────────────┤
│  🤖 Multi-Agent System                                                 │
│  ├── Microsoft AutoGen - MIT                                           │
│  ├── Agent Zero patterns - MIT                                         │
│  ├── OpenCode patterns (Build/Plan) - MIT                              │
│  └── LangChain orchestration - MIT                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  🎮 Zork-Style Interface (Custom Created!)                             │
│  ├── Text adventure UI for EVERY application                           │
│  ├── Automatic interface generation on app install                     │
│  ├── Native tiling window manager                                      │
│  ├── Obsidian-style Knowledge Vault                                    │
│  └── Research Command Center                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  💻 Sandboxed Terminals with Zork Accessibility                        │
│  ├── Gemini CLI, Codex, GitHub Copilot CLI support                     │
│  ├── Natural language to CLI command translation                       │
│  ├── Zork narrative wrapping for all output                            │
│  └── Voice control for terminal applications                           │
├─────────────────────────────────────────────────────────────────────────┤
│  🧠 Self-Learning System                                               │
│  ├── Learns common command patterns                                    │
│  ├── Tracks user preferences                                           │
│  ├── Monitors app usage patterns                                       │
│  ├── Improves narratives over time                                     │
│  └── Gets smarter with continued use!                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  💾 Debian GNU/Linux Foundation                                        │
│  ├── Full GNU toolkit                                                  │
│  ├── Debian package management                                         │
│  ├── Flatpak integration                                               │
│  └── ISO releases for real hardware install                            │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🔒 Core Security Architecture

### Triple-AI System (Om Vinayaka at Core)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SECURITY ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🛡️ GUARDIAN AI (Kernel Level - Port 11435) [ISOLATED]                 │
│  ├── IBM Granite Guardian 2B model                                      │
│  ├── Think → Vet → Act methodology                                      │
│  ├── CANNOT be influenced by user conversations                         │
│  └── Independent threat analysis                                        │
│                                                                         │
│  ════════════════════ ISOLATION BARRIER ════════════════════            │
│                                                                         │
│  🙏 OM VINAYAKA AI (Core Controller - Port 11434)                       │
│  ├── Controls ALL user-facing subsystems                                │
│  ├── Intelligent accessibility for 1,600+ languages                     │
│  ├── Self-learning system                                               │
│  ├── Anti-Hallucination Engine                                          │
│  │                                                                      │
│  │   ┌─────────┬─────────┬─────────┬─────────┬─────────┐                │
│  └───┤ Agents  │ Research│ Writing │ Coding  │ System  │                │
│      └─────────┴─────────┴─────────┴─────────┴─────────┘                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Guardian AI (Security Core)**: Sandboxed at kernel level - ISOLATED from Om Vinayaka
- **Om Vinayaka AI (Core Controller)**: Controls all user-facing systems with intelligent accessibility
- **Multi-Agent System**: Task automation controlled BY Om Vinayaka AI
- **Air Gap Protection**: Complete isolation between Guardian and user-facing AI
- **Principle of Least Privilege**: No direct website interactions or form submissions

### Security Features
- ✅ **Real-time Threat Analysis**: Every input analyzed by Guardian before processing
- ✅ **Self-Analysis & Healing**: Autonomous code security scanning
- ✅ **5-Day Quarantine Protocol**: Safe integration of external intelligence
- ✅ **Localhost-Only Operation**: No external network exposure
- ✅ **Pattern-Based Detection**: Advanced malware and injection detection
- ✅ **Anti-Hallucination Engine**: Om Vinayaka prevents AI from making up information
- ✅ **Om Vinayaka at Core**: All user interactions flow through intelligent accessibility

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

### 🧠 Context-Aware Summary Engine
Prevents AI hallucinations and context overflow:
- **Automatic Summarization**: When AI context gets too large
- **Full Preservation**: Complete knowledge stored in Obsidian vault
- **Smart Compression**: Prioritizes critical context over background info
- **Hallucination Prevention**: AI never loses important context

## 💻 System Requirements

### Minimum Requirements
| Component | Requirement |
|-----------|-------------|
| **RAM** | 4 GB |
| **CPU** | 2 cores |
| **Storage** | 20 GB |
| **Note** | AI features will be limited |

### Recommended Requirements
| Component | Requirement |
|-----------|-------------|
| **RAM** | 8 GB |
| **CPU** | 4 cores |
| **Storage** | 40 GB |
| **Note** | Full AI experience |

### Optimal Requirements
| Component | Requirement |
|-----------|-------------|
| **RAM** | 16 GB |
| **CPU** | 8 cores |
| **Storage** | 80 GB |
| **GPU** | NVIDIA with CUDA (optional) |
| **Note** | Best performance with all features |

### RAM Breakdown (Full Installation)
| Component | RAM (MB) |
|-----------|----------|
| Base OS (Debian) | 512 |
| Desktop Environment | 256 |
| Guardian AI (Sandboxed Ollama) | 2048 |
| User-facing Ollama | 2048 |
| Om Vinayaka AI | 256 |
| Voice Recognition | 512 |
| Text-to-Speech | 256 |
| Summary Engine | 64 |
| **Total Calculated** | **~6 GB** |

## 🚀 Quick Installation

### From ISO (Recommended)

Download the VA21 OS ISO from the [Releases page](../../releases) and install like any Linux distribution:

```bash
# Write ISO to USB drive
sudo dd if=va21-os.iso of=/dev/sdX bs=4M status=progress

# Or use in VirtualBox/VMware
# Create VM → Use ISO as boot disk → Install
```

### Build from Source

```bash
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21/va21_system/linux_os
./scripts/build_iso.sh debian
# ISO will be in output/ directory
```

## 📋 Additional System Requirements

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

VA21 OS is built with privacy-first, local-first technologies:

### Core System
| Component | Technology | License |
|-----------|------------|---------|
| **OS Base** | Debian GNU/Linux | DFSG |
| **Window Manager** | Custom Tiling WM | Apache 2.0 |
| **Shell** | Zork-Style Interface | Apache 2.0 |
| **Package Manager** | Flatpak + APT | Various |

### 🙏 Om Vinayaka AI Stack (Central Intelligence)
| Component | Technology | License | Purpose |
|-----------|------------|---------|---------|
| **Local LLM** | [Ollama](https://ollama.com) | MIT | Privacy-first local AI |
| **AI Models** | [IBM Granite](https://huggingface.co/ibm-granite) | Apache 2.0 | General + Code + Security |
| **Orchestration** | [LangChain](https://github.com/langchain-ai/langchain) | MIT | AI workflow management |
| **Knowledge Base** | Obsidian-style Vault | - | Mind maps + Wiki links |
| **FARA Layer** | Microsoft FARA Integration | MIT | Universal app control |

### 🎤 Voice Intelligence Layer
| Component | Technology | License | Purpose |
|-----------|------------|---------|---------|
| **ASR (Primary)** | Meta Omnilingual ASR ⭐⭐⭐⭐⭐ | Apache 2.0 | 1,600+ languages |
| **ASR (Backup)** | [OpenAI Whisper](https://github.com/openai/whisper) | MIT | Offline backup |
| **Wake Word** | [Rhasspy](https://github.com/rhasspy/rhasspy) | MIT | "Hey VA21" detection |
| **TTS (Fast)** | [Piper TTS](https://github.com/rhasspy/piper) | MIT | Fast synthesis |
| **TTS (Premium)** | [Kokoro TTS](https://github.com/remsky/Kokoro-FastAPI) | Apache 2.0 | Natural voices |

### 🤖 Multi-Agent System
| Component | Technology | License | Purpose |
|-----------|------------|---------|---------|
| **Framework** | [Microsoft AutoGen](https://github.com/microsoft/autogen) ⭐⭐⭐⭐⭐ | MIT | Agent conversation |
| **Patterns** | [Agent Zero](https://github.com/agent0ai/agent-zero) | MIT | Cooperation patterns |
| **Roles** | [OpenCode](https://github.com/sst/opencode) | MIT | Build/Plan agents |
| **Deployment** | [LMDeploy](https://github.com/InternLM/lmdeploy) | Apache 2.0 | Efficient inference |

### 🔒 Security & Privacy
| Component | Technology | License | Purpose |
|-----------|------------|---------|---------|
| **Guardian AI** | Sandboxed Ollama (port 11435) | Proprietary | Kernel-level security |
| **LLM Security** | [LLM Guard](https://github.com/protectai/llm-guard) | MIT | Prompt injection defense |
| **Privacy** | [IBM AI Privacy Toolkit](https://github.com/IBM/ai-privacy-toolkit) | MIT | GDPR compliance |
| **Antivirus** | ClamAV | GPL | Malware protection |

### 🏢 Key Technology Partners
| Partner | Contributions |
|---------|---------------|
| **IBM** | Granite AI models, AI Privacy Toolkit |
| **Microsoft** | ONNX Runtime, FARA, AutoGen, Phi models |
| **Meta AI** | Omnilingual ASR (1,600+ languages), LLaMA, PyTorch |
| **Hugging Face** | Model hosting, Transformers library |
| **Ollama** | Local LLM deployment |

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
