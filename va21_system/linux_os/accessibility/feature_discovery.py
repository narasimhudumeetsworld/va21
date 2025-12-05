#!/usr/bin/env python3
"""
VA21 OS - Feature Discovery System
===================================

🙏 OM VINAYAKA - FEATURE DISCOVERY & USER ADOPTION SYSTEM 🙏

Addresses adoption barriers in VA21 OS:
- Learning Curve: AI-driven paradigm may feel unfamiliar to traditional Linux users
- Adoption Barriers: Requires experimentation to discover all features
- User Documentation: Video tutorials, beginner guides for traditional Linux users

This system provides:
1. Interactive Feature Discovery: Om Vinayaka AI guides users to discover features
2. Contextual Tutorials: Shows relevant help based on what the user is doing
3. Progressive Disclosure: Reveals features gradually as users become comfortable
4. Traditional Linux Mappings: Shows equivalent traditional commands/workflows
5. Video Tutorial Integration: Links to video tutorials for visual learners
6. Beginner Guides: Step-by-step guides for common tasks

Everything is controlled by Om Vinayaka AI, making the learning experience
conversational and personalized to each user's background.

Om Vinayaka - May obstacles be removed from your learning journey.
Making VA21 accessible to everyone, from Linux experts to newcomers.

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

DISCOVERY_VERSION = "1.0.0"
DEFAULT_DISCOVERY_PATH = os.path.expanduser("~/.va21/feature_discovery")


class UserExperience(Enum):
    """User experience level."""
    NEW_TO_COMPUTING = "new_to_computing"
    TRADITIONAL_LINUX = "traditional_linux"
    WINDOWS_USER = "windows_user"
    MAC_USER = "mac_user"
    POWER_USER = "power_user"
    DEVELOPER = "developer"
    ACCESSIBILITY_USER = "accessibility_user"


class FeatureCategory(Enum):
    """Feature categories."""
    CORE = "core"                    # Essential features everyone should know
    ACCESSIBILITY = "accessibility"  # Voice control, screen reader, etc.
    AI_FEATURES = "ai_features"      # Helper AI, Guardian AI, etc.
    PRODUCTIVITY = "productivity"    # Research suite, writing tools
    SECURITY = "security"            # Guardian AI, privacy features
    CUSTOMIZATION = "customization"  # Themes, settings, preferences
    DEVELOPER = "developer"          # IDE, terminal, development tools
    ADVANCED = "advanced"            # Power user features


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Feature:
    """A VA21 OS feature."""
    feature_id: str
    name: str
    description: str
    category: FeatureCategory
    
    # How to use
    voice_commands: List[str] = field(default_factory=list)
    keyboard_shortcuts: List[str] = field(default_factory=list)
    menu_path: Optional[str] = None
    
    # For traditional Linux users
    linux_equivalent: Optional[str] = None
    traditional_workflow: Optional[str] = None
    
    # Learning resources
    tutorial_text: Optional[str] = None
    video_tutorial_url: Optional[str] = None
    documentation_url: Optional[str] = None
    
    # Discovery metadata
    discovery_hint: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    experience_levels: List[str] = field(default_factory=list)


@dataclass
class UserProgress:
    """Tracks user's discovery progress."""
    user_id: str = "default"
    experience_level: str = "traditional_linux"
    discovered_features: List[str] = field(default_factory=list)
    mastered_features: List[str] = field(default_factory=list)
    current_tutorial: Optional[str] = None
    tutorials_completed: List[str] = field(default_factory=list)
    hints_shown: List[str] = field(default_factory=list)
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Tutorial:
    """An interactive tutorial."""
    tutorial_id: str
    title: str
    description: str
    target_feature: str
    target_audience: List[str]  # Experience levels
    
    # Tutorial steps
    steps: List[Dict] = field(default_factory=list)
    
    # Resources
    video_url: Optional[str] = None
    estimated_time_minutes: int = 5
    
    # Progress tracking
    completion_criteria: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class FeatureDatabase:
    """
    Database of all VA21 OS features with discovery information.
    
    Includes:
    - Feature descriptions
    - Voice commands
    - Traditional Linux equivalents
    - Tutorial links
    - Discovery hints
    """
    
    def __init__(self):
        self.features: Dict[str, Feature] = {}
        self._load_default_features()
    
    def _load_default_features(self):
        """Load default VA21 features."""
        
        # Core Features
        self.features["zork_interface"] = Feature(
            feature_id="zork_interface",
            name="Zork-Style Interface",
            description="Navigate VA21 OS like a text adventure game! Every app gets a conversational interface.",
            category=FeatureCategory.CORE,
            voice_commands=["look around", "where am I", "what can I do here"],
            keyboard_shortcuts=["Super key (hold) + speak"],
            linux_equivalent="bash shell with natural language",
            traditional_workflow="Instead of typing `ls -la`, just say 'what files are here?'",
            tutorial_text="""
## Getting Started with Zork Interface

VA21's unique Zork-style interface lets you interact with your computer using natural language.

### Basic Commands:
- **look** - See what's around you (like `ls`)
- **go [direction]** - Navigate (like `cd`)
- **examine [item]** - Get details (like `cat` or `file`)
- **take [item]** - Select/open something

### Traditional Equivalent:
| Zork Command | Traditional Linux |
|--------------|-------------------|
| look | ls -la |
| go downloads | cd ~/Downloads |
| examine readme | cat readme.txt |
| search for reports | find . -name "*report*" |

### Try It:
1. Hold the Super key
2. Say "look around"
3. VA21 will describe your current location!
""",
            discovery_hint="Try saying 'look around' to see what's in your current location!",
            experience_levels=["new_to_computing", "traditional_linux", "windows_user"]
        )
        
        self.features["voice_control"] = Feature(
            feature_id="voice_control",
            name="System-Wide Voice Control",
            description="Control ANY application with your voice. Hold Super key and speak naturally.",
            category=FeatureCategory.ACCESSIBILITY,
            voice_commands=["save", "open", "close", "search for", "go to"],
            keyboard_shortcuts=["Super (hold) + speak"],
            linux_equivalent="Custom voice commands via Talon/Numen",
            traditional_workflow="Instead of Ctrl+S, just say 'save'. Works in every app!",
            tutorial_text="""
## Voice Control Guide

VA21 provides system-wide voice control that works in ANY application.

### How to Use:
1. **Hold the Super (Windows) key**
2. **Speak your command naturally**
3. **Release to execute**

### Common Commands:
- "Save my work" → Saves current document
- "Open Firefox" → Launches Firefox
- "Search for climate change" → Searches in current app
- "Go back" → Goes to previous page/folder
- "Close this" → Closes current window

### For Traditional Linux Users:
Think of it as speech-to-command translation:
- "list files" → ls
- "change directory to downloads" → cd ~/Downloads
- "show running processes" → ps aux

### Tips:
- Speak naturally, don't worry about exact commands
- Om Vinayaka AI will ask for clarification if needed
- Commands work in 1,600+ languages!
""",
            video_tutorial_url="https://va21.dev/tutorials/voice-control",
            discovery_hint="Hold the Super key and try saying 'what can I do?'",
            experience_levels=["new_to_computing", "traditional_linux", "accessibility_user"]
        )
        
        self.features["helper_ai"] = Feature(
            feature_id="helper_ai",
            name="Om Vinayaka Helper AI",
            description="Your AI assistant that explains things, not just reads them. Ask anything!",
            category=FeatureCategory.AI_FEATURES,
            voice_commands=["help me with", "explain", "how do I", "what is"],
            keyboard_shortcuts=["Ctrl+Space (to summon)"],
            linux_equivalent="man pages + AI explanation",
            traditional_workflow="Instead of `man grep`, ask 'how do I search for text in files?'",
            tutorial_text="""
## Om Vinayaka Helper AI

Unlike traditional screen readers that just announce "button" or "menu",
Om Vinayaka EXPLAINS what things do and ASKS what you want to accomplish.

### What Makes It Different:
| Traditional Screen Reader | Om Vinayaka AI |
|---------------------------|----------------|
| "Save button" | "This saves your document. Would you like me to save it?" |
| "Menu" | "This menu has options for editing your document" |
| Reads keywords | Explains purpose |

### How to Use:
- **Ask questions**: "How do I save my work?"
- **Get explanations**: "What does this button do?"
- **Request actions**: "Help me find my research papers"

### For Traditional Linux Users:
Think of it as having an expert always ready to help:
- Instead of searching Stack Overflow
- Instead of reading lengthy man pages
- Instead of trial and error

### Example Conversation:
**You**: "I want to find all PDF files modified last week"
**AI**: "I'll help you find those. Looking in your home folder... Found 12 PDFs modified in the last 7 days. Would you like me to list them or open the folder?"
""",
            discovery_hint="Try asking 'what can you help me with?'",
            experience_levels=["new_to_computing", "traditional_linux", "windows_user", "accessibility_user"]
        )
        
        self.features["guardian_ai"] = Feature(
            feature_id="guardian_ai",
            name="Guardian AI Security",
            description="Real-time security protection that analyzes all inputs for threats.",
            category=FeatureCategory.SECURITY,
            voice_commands=["check security", "is this safe", "scan for threats"],
            linux_equivalent="ClamAV + AI-powered analysis",
            traditional_workflow="Automatic protection - no commands needed!",
            tutorial_text="""
## Guardian AI - Your Security Companion

Guardian AI runs in a sandboxed environment, continuously analyzing
all system inputs for potential threats.

### What It Protects Against:
- SQL Injection attacks
- XSS (Cross-Site Scripting)
- Command injection
- Path traversal
- Phishing attempts
- Malicious scripts

### How It Works:
```
User Input → Guardian AI Analysis → Safe? → Allow
                                   ↓
                              Threat? → Block & Alert
```

### For Traditional Linux Users:
Like having `sudo` but smarter:
- Analyzes intent, not just commands
- Real-time, not periodic scans
- Air-gapped from sensitive data

### Security Status:
Check anytime: "Hey VA21, what's my security status?"
""",
            discovery_hint="Ask 'what's my security status?' to see Guardian AI in action",
            experience_levels=["traditional_linux", "power_user", "developer"]
        )
        
        self.features["fara_layer"] = Feature(
            feature_id="fara_layer",
            name="FARA App Compatibility",
            description="Automatically makes ANY application controllable via voice and AI.",
            category=FeatureCategory.CORE,
            voice_commands=["control [app]", "automate", "create workflow"],
            linux_equivalent="xdotool + AT-SPI automation",
            traditional_workflow="FARA automatically creates profiles for every app - no setup needed!",
            tutorial_text="""
## FARA - Flexible Automated Response Architecture

FARA automatically creates compatibility profiles for EVERY application
when it's installed, enabling Om Vinayaka AI to control them.

### How It Works:
1. **App Installed** → FARA detects new app
2. **Analysis** → Scans UI elements, menus, shortcuts
3. **Profile Created** → Voice commands mapped automatically
4. **Ready to Use** → Control with voice immediately!

### Supported Apps:
- Native Linux apps (GTK, Qt)
- Electron apps (VS Code, Slack, Discord)
- Wine apps (Windows programs)
- Legacy apps (GTK2, Qt4)
- Terminal apps (with Zork wrapper)

### For Traditional Linux Users:
Like creating `.desktop` files + `xdotool` scripts automatically:
- No manual configuration
- Works with any app
- Learns from your usage

### Example:
**You**: "Save in LibreOffice"
**FARA**: Detects LibreOffice is active → Executes Ctrl+S
""",
            discovery_hint="Install any new app and try controlling it with voice!",
            prerequisites=["voice_control"],
            experience_levels=["traditional_linux", "power_user", "developer"]
        )
        
        self.features["knowledge_vault"] = Feature(
            feature_id="knowledge_vault",
            name="Knowledge Vault",
            description="Obsidian-style note-taking with AI-powered organization.",
            category=FeatureCategory.PRODUCTIVITY,
            voice_commands=["open vault", "create note", "search notes", "link to"],
            keyboard_shortcuts=["Ctrl+Shift+N (new note)", "Ctrl+O (open vault)"],
            linux_equivalent="Obsidian + AI integration",
            traditional_workflow="Create and link notes with [[wiki-style]] syntax",
            tutorial_text="""
## Knowledge Vault - Your Second Brain

An Obsidian-style knowledge management system with AI enhancements.

### Features:
- **Wiki-style linking**: Use [[note name]] to link notes
- **Mind maps**: Visualize connections between ideas
- **AI search**: Find notes by meaning, not just keywords
- **Auto-organization**: AI suggests tags and links

### Basic Usage:
1. "Create note about meeting"
2. Add content with [[links]] to other notes
3. View connections in the graph view

### For Traditional Linux Users:
Like `vim` + `grep` + `find` but visual and connected:
- Notes are plain markdown files
- Stored in `~/.va21/vault/`
- Can edit with any text editor

### Pro Tips:
- Use tags: #project #idea #reference
- Daily notes: "Create daily note"
- Templates: "Use research template"
""",
            video_tutorial_url="https://va21.dev/tutorials/knowledge-vault",
            discovery_hint="Try 'create a new note about [topic]' to start organizing your knowledge!",
            experience_levels=["traditional_linux", "developer", "power_user"]
        )
        
        self.features["research_suite"] = Feature(
            feature_id="research_suite",
            name="Research Suite",
            description="Academic research tools with citation management and web search.",
            category=FeatureCategory.PRODUCTIVITY,
            voice_commands=["search papers", "cite this", "export bibliography"],
            linux_equivalent="Zotero + SearXNG integration",
            tutorial_text="""
## Research Suite - Academic Tools

Integrated research tools for academic work.

### Features:
- **Privacy-Respecting Search**: Uses SearXNG (no tracking)
- **Citation Manager**: Auto-format citations
- **Paper Organization**: AI-assisted categorization
- **Export Options**: BibTeX, APA, MLA, Chicago

### Quick Start:
1. "Search for papers about climate change"
2. "Save this paper to my library"
3. "Cite this in APA format"

### For Traditional Linux Users:
Replaces multiple tools:
- SearXNG for search
- Zotero for citations
- Pandoc for formatting
All integrated with voice control!
""",
            discovery_hint="Try 'search for research papers about [topic]'",
            experience_levels=["traditional_linux", "developer"]
        )
        
        self.features["auto_backup"] = Feature(
            feature_id="auto_backup",
            name="Auto Backup System",
            description="Automatic backups every 6 hours with AI-assisted restoration.",
            category=FeatureCategory.CORE,
            voice_commands=["create backup", "restore from backup", "show backups"],
            linux_equivalent="rsync + cron + LZMA compression",
            traditional_workflow="Automatic - just ask 'restore my file' when needed",
            tutorial_text="""
## Auto Backup - Never Lose Work Again

Automatic, intelligent backups with time-travel restoration.

### How It Works:
- **Automatic**: Backups every 6 hours
- **Efficient**: LZMA compression (70-80% smaller)
- **Smart**: Only backs up changed files
- **Safe**: Survives power loss

### Restoration:
**Natural Language**: "I broke my config file yesterday, can you fix it?"
**AI Response**: Finds relevant backup, shows changes, offers to restore

### For Traditional Linux Users:
Like having this running automatically:
```bash
# But smarter and with AI-assisted restoration
rsync -av --backup --compress ~/
```

### Commands:
- "Create a backup now"
- "Show my backup history"
- "Restore config from yesterday"
""",
            discovery_hint="Ask 'when was my last backup?' to check backup status",
            experience_levels=["traditional_linux", "power_user"]
        )
        
        # Command mappings for traditional Linux users
        self.features["linux_commands"] = Feature(
            feature_id="linux_commands",
            name="Traditional Linux Commands",
            description="Use familiar Linux commands alongside voice control.",
            category=FeatureCategory.CORE,
            keyboard_shortcuts=["Ctrl+Alt+T (terminal)"],
            linux_equivalent="Full bash access available",
            traditional_workflow="All traditional commands work in Terminal!",
            tutorial_text="""
## For Traditional Linux Users

VA21 is built ON Linux, not replacing it. All your favorite commands work!

### Quick Reference - Voice to Command:
| What You Say | Linux Equivalent |
|--------------|------------------|
| "What files are here?" | `ls -la` |
| "Go to downloads" | `cd ~/Downloads` |
| "Find files named report" | `find . -name "*report*"` |
| "Show disk space" | `df -h` |
| "What's running?" | `ps aux` |
| "Search for text in files" | `grep -r "text" .` |
| "Install Firefox" | `sudo apt install firefox` |
| "Update system" | `sudo apt update && sudo apt upgrade` |

### Using Terminal:
- Press `Ctrl+Alt+T` to open terminal
- All bash commands work normally
- Add voice control: hold Super key + speak

### VA21 Enhances, Doesn't Replace:
- Same file system (`/home/user/`)
- Same package managers (`apt`, `flatpak`)
- Same permissions model
- But with AI assistance when you want it

### Pro Tip:
Type `va21 --traditional` to see VA21 commands as traditional Linux equivalents.
""",
            discovery_hint="Press Ctrl+Alt+T for a traditional terminal anytime!",
            experience_levels=["traditional_linux", "developer", "power_user"]
        )
    
    def get_feature(self, feature_id: str) -> Optional[Feature]:
        """Get a feature by ID."""
        return self.features.get(feature_id)
    
    def get_features_by_category(self, category: FeatureCategory) -> List[Feature]:
        """Get all features in a category."""
        return [f for f in self.features.values() if f.category == category]
    
    def get_features_for_experience(self, experience: str) -> List[Feature]:
        """Get features relevant to a user experience level."""
        return [f for f in self.features.values() 
                if not f.experience_levels or experience in f.experience_levels]
    
    def search_features(self, query: str) -> List[Feature]:
        """Search features by keyword."""
        query_lower = query.lower()
        results = []
        
        for feature in self.features.values():
            if (query_lower in feature.name.lower() or
                query_lower in feature.description.lower() or
                any(query_lower in cmd.lower() for cmd in feature.voice_commands)):
                results.append(feature)
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE DISCOVERY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class FeatureDiscoveryEngine:
    """
    🙏 FEATURE DISCOVERY ENGINE - CONTROLLED BY OM VINAYAKA AI 🙏
    
    Helps users discover VA21 OS features through:
    - Contextual hints
    - Progressive disclosure
    - Interactive tutorials
    - Traditional Linux mappings
    """
    
    VERSION = DISCOVERY_VERSION
    
    def __init__(self, discovery_path: str = None):
        self.discovery_path = discovery_path or DEFAULT_DISCOVERY_PATH
        os.makedirs(self.discovery_path, exist_ok=True)
        
        # Initialize components
        self.feature_db = FeatureDatabase()
        self.user_progress = UserProgress()
        
        # Load saved progress
        self._load_progress()
        
        # Om Vinayaka integration
        self._om_vinayaka_callback = None
        
        print(f"[FeatureDiscovery] Engine initialized v{self.VERSION}")
    
    def set_om_vinayaka_callback(self, callback):
        """Set callback for Om Vinayaka AI integration."""
        self._om_vinayaka_callback = callback
    
    def set_user_experience(self, experience: str):
        """Set the user's experience level for personalized discovery."""
        try:
            self.user_progress.experience_level = experience
            self._save_progress()
            print(f"[FeatureDiscovery] User experience set to: {experience}")
        except Exception:
            pass
    
    def get_contextual_hint(self, context: Dict) -> Optional[Dict]:
        """
        Get a contextual hint based on what the user is doing.
        
        Args:
            context: Dict with current_app, action, etc.
        
        Returns:
            Hint dict with title, message, and feature info
        """
        current_app = context.get('current_app', '').lower()
        action = context.get('action', '').lower()
        
        # Don't repeat hints
        hint_key = f"{current_app}:{action}"
        if hint_key in self.user_progress.hints_shown:
            return None
        
        # Find relevant undiscovered features
        relevant_features = []
        
        # If in terminal, suggest voice control
        if 'terminal' in current_app and 'voice_control' not in self.user_progress.discovered_features:
            relevant_features.append(self.feature_db.get_feature('voice_control'))
        
        # If saving, mention auto-backup
        if 'save' in action and 'auto_backup' not in self.user_progress.discovered_features:
            relevant_features.append(self.feature_db.get_feature('auto_backup'))
        
        # If in file manager, suggest voice commands
        if 'file' in current_app and 'fara_layer' not in self.user_progress.discovered_features:
            relevant_features.append(self.feature_db.get_feature('fara_layer'))
        
        if not relevant_features:
            return None
        
        feature = relevant_features[0]
        if not feature:
            return None
        
        # Mark hint as shown
        self.user_progress.hints_shown.append(hint_key)
        self._save_progress()
        
        return {
            'title': f"💡 Tip: {feature.name}",
            'message': feature.discovery_hint or feature.description,
            'feature_id': feature.feature_id,
            'voice_commands': feature.voice_commands[:3]
        }
    
    def get_feature_tutorial(self, feature_id: str) -> Optional[str]:
        """Get the tutorial text for a feature."""
        feature = self.feature_db.get_feature(feature_id)
        if feature:
            # Mark as discovered
            if feature_id not in self.user_progress.discovered_features:
                self.user_progress.discovered_features.append(feature_id)
                self._save_progress()
            
            return feature.tutorial_text
        return None
    
    def get_linux_equivalent(self, voice_command: str) -> Optional[str]:
        """
        Get the traditional Linux equivalent of a VA21 command.
        
        For traditional Linux users who want to understand what's happening.
        """
        # Search all features for matching voice command
        for feature in self.feature_db.features.values():
            for cmd in feature.voice_commands:
                if cmd.lower() in voice_command.lower():
                    if feature.linux_equivalent:
                        return f"""
**VA21 Command**: "{voice_command}"
**Linux Equivalent**: {feature.linux_equivalent}

{feature.traditional_workflow or ''}
"""
        return None
    
    def get_beginner_guide(self) -> str:
        """Get a beginner's guide based on user experience level."""
        exp = self.user_progress.experience_level
        
        if exp == "traditional_linux":
            return self._get_linux_user_guide()
        elif exp == "windows_user":
            return self._get_windows_user_guide()
        elif exp == "accessibility_user":
            return self._get_accessibility_guide()
        else:
            return self._get_general_guide()
    
    def _get_linux_user_guide(self) -> str:
        """Guide for traditional Linux users."""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║               🐧 VA21 OS FOR TRADITIONAL LINUX USERS 🐧                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Welcome, fellow Linux user! VA21 is built ON Linux, not replacing it.
Everything you know still works - we just added an AI layer on top.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 WHAT'S THE SAME:
• Same bash shell (Ctrl+Alt+T for terminal)
• Same file system (/home/user/)
• Same package managers (apt, flatpak, snap)
• Same permissions (sudo still works!)
• Same config files (~/.config, /etc)

🆕 WHAT'S NEW:
• Voice control: Hold Super key + speak
• AI assistant: Ask questions naturally
• Zork interface: Navigate by conversation
• Auto-generated app profiles: Voice control any app

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 QUICK COMMAND TRANSLATION:

| What You Say          | Linux Equivalent           |
|-----------------------|----------------------------|
| "show files"          | ls -la                     |
| "go to downloads"     | cd ~/Downloads             |
| "find reports"        | find . -name "*report*"    |
| "install firefox"     | sudo apt install firefox   |
| "update system"       | sudo apt update && upgrade |
| "show processes"      | ps aux                     |
| "disk space"          | df -h                      |
| "memory usage"        | free -h                    |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 START HERE:
1. Press Ctrl+Alt+T - Your familiar terminal is right there!
2. Try holding Super key and saying "what can I do?"
3. All traditional commands still work

💡 Pro Tip: Type `va21 --show-linux` after any voice command
   to see what Linux commands were executed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Om Vinayaka 🙏 - Intelligence enhances the command line
"""
    
    def _get_windows_user_guide(self) -> str:
        """Guide for Windows users."""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                  🪟 VA21 OS FOR WINDOWS USERS 🪟                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Welcome to VA21! Coming from Windows, you'll find VA21 familiar yet more powerful.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 FAMILIAR CONCEPTS:
• Home folder = Your Documents folder
• File Manager = Like Windows Explorer
• Terminal = Like Command Prompt, but better
• Settings = Like Control Panel

🆕 VA21 SUPERPOWERS:
• Voice control: Hold Super (Windows) key + speak
• AI that explains things, not just reads them
• Every app gets voice control automatically
• Real-time security without antivirus slowdown

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 GETTING STARTED:
1. Try holding Super key and saying "open file manager"
2. Say "save" in any application to save your work
3. Ask "how do I [anything]?" for help

💡 Windows Shortcuts That Work:
• Ctrl+C / Ctrl+V = Copy / Paste
• Ctrl+S = Save
• Alt+F4 = Close window
• Super key = Open menu

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Om Vinayaka 🙏 - Computing made conversational
"""
    
    def _get_accessibility_guide(self) -> str:
        """Guide for accessibility users."""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║              ♿ VA21 OS ACCESSIBILITY GUIDE ♿                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Welcome! VA21 was designed with accessibility at its core.
Om Vinayaka AI is here to help you every step of the way.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗣️ VOICE CONTROL:
• Hold the Super key (between Ctrl and Alt)
• Speak naturally - no memorizing commands!
• I'll ask clarifying questions if needed
• Supports 1,600+ languages

🎮 ZORK INTERFACE:
• Every app becomes a conversation
• I explain what things DO, not just their names
• No visual navigation required

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TRY THESE COMMANDS:
• "Where am I?" - Describes current location
• "What can I do here?" - Lists available actions
• "Help me find [something]" - Assisted search
• "Read this to me" - Screen reader

💡 I'm Different From Regular Screen Readers:
• I don't just say "button" - I explain what it does
• I understand context - I know what you're trying to do
• I ask questions when I need clarification
• I learn your preferences over time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Om Vinayaka 🙏 - Removing obstacles from your computing journey
"""
    
    def _get_general_guide(self) -> str:
        """General getting started guide."""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🙏 WELCOME TO VA21 OS 🙏                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

VA21 OS is an AI-powered operating system where you can control
everything with natural conversation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 GETTING STARTED:

1. **Voice Control**: Hold Super key + speak naturally
   Try: "What can I do here?"

2. **Ask Questions**: I'll explain anything
   Try: "How do I save my work?"

3. **Navigate**: Just describe where you want to go
   Try: "Take me to my documents"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Om Vinayaka 🙏 - Your AI companion for computing
"""
    
    def get_onboarding_questions(self) -> List[Dict]:
        """Get onboarding questions to personalize the experience."""
        return [
            {
                'question': "What's your computing background?",
                'options': [
                    {'value': 'new_to_computing', 'label': "I'm new to computers"},
                    {'value': 'windows_user', 'label': "I've used Windows"},
                    {'value': 'mac_user', 'label': "I've used Mac"},
                    {'value': 'traditional_linux', 'label': "I use Linux (command line)"},
                    {'value': 'developer', 'label': "I'm a software developer"},
                ]
            },
            {
                'question': "Do you use accessibility features?",
                'options': [
                    {'value': True, 'label': "Yes, I use screen readers/voice control"},
                    {'value': False, 'label': "No"},
                ]
            },
            {
                'question': "What will you mainly use VA21 for?",
                'options': [
                    {'value': 'general', 'label': "General computing"},
                    {'value': 'research', 'label': "Research and academic work"},
                    {'value': 'development', 'label': "Software development"},
                    {'value': 'creative', 'label': "Creative work"},
                ]
            }
        ]
    
    def mark_feature_discovered(self, feature_id: str):
        """Mark a feature as discovered by the user."""
        if feature_id not in self.user_progress.discovered_features:
            self.user_progress.discovered_features.append(feature_id)
            self._save_progress()
            
            if self._om_vinayaka_callback:
                self._om_vinayaka_callback({
                    'event': 'feature_discovered',
                    'feature_id': feature_id
                })
    
    def mark_feature_mastered(self, feature_id: str):
        """Mark a feature as mastered by the user."""
        if feature_id not in self.user_progress.mastered_features:
            self.user_progress.mastered_features.append(feature_id)
            self._save_progress()
    
    def get_discovery_progress(self) -> Dict:
        """Get the user's feature discovery progress."""
        total_features = len(self.feature_db.features)
        discovered = len(self.user_progress.discovered_features)
        mastered = len(self.user_progress.mastered_features)
        
        return {
            'total_features': total_features,
            'discovered': discovered,
            'mastered': mastered,
            'discovery_percentage': f"{discovered / max(total_features, 1) * 100:.0f}%",
            'next_to_discover': self._get_next_feature_to_discover(),
            'experience_level': self.user_progress.experience_level
        }
    
    def _get_next_feature_to_discover(self) -> Optional[str]:
        """Get the next recommended feature to discover."""
        # Get features appropriate for user's experience
        relevant = self.feature_db.get_features_for_experience(
            self.user_progress.experience_level
        )
        
        # Find first undiscovered
        for feature in relevant:
            if feature.feature_id not in self.user_progress.discovered_features:
                # Check prerequisites
                prereqs_met = all(
                    p in self.user_progress.discovered_features 
                    for p in feature.prerequisites
                )
                if prereqs_met:
                    return feature.feature_id
        
        return None
    
    def _load_progress(self):
        """Load user progress from disk."""
        progress_file = os.path.join(self.discovery_path, "user_progress.json")
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    self.user_progress = UserProgress(**data)
            except Exception:
                pass
    
    def _save_progress(self):
        """Save user progress to disk."""
        self.user_progress.last_activity = datetime.now().isoformat()
        progress_file = os.path.join(self.discovery_path, "user_progress.json")
        try:
            with open(progress_file, 'w') as f:
                json.dump(asdict(self.user_progress), f, indent=2)
        except Exception:
            pass
    
    def get_status(self) -> Dict:
        """Get feature discovery status."""
        return {
            'version': self.VERSION,
            'user_experience': self.user_progress.experience_level,
            'total_features': len(self.feature_db.features),
            'discovered': len(self.user_progress.discovered_features),
            'mastered': len(self.user_progress.mastered_features),
            'hints_shown': len(self.user_progress.hints_shown)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_discovery_instance = None


def get_feature_discovery() -> FeatureDiscoveryEngine:
    """Get or create the Feature Discovery Engine singleton."""
    global _discovery_instance
    
    if _discovery_instance is None:
        _discovery_instance = FeatureDiscoveryEngine()
    
    return _discovery_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the Feature Discovery Engine."""
    print("=" * 70)
    print("VA21 OS - Feature Discovery Engine Test")
    print("=" * 70)
    
    # Initialize
    discovery = get_feature_discovery()
    
    # Set user experience
    discovery.set_user_experience("traditional_linux")
    
    # Get beginner guide
    print("\n--- Beginner Guide ---\n")
    print(discovery.get_beginner_guide())
    
    # Get feature tutorial
    print("\n--- Feature Tutorial ---\n")
    tutorial = discovery.get_feature_tutorial("voice_control")
    if tutorial:
        print(tutorial[:500] + "...")
    
    # Get Linux equivalent
    print("\n--- Linux Equivalent ---\n")
    equiv = discovery.get_linux_equivalent("show files")
    if equiv:
        print(equiv)
    
    # Get contextual hint
    print("\n--- Contextual Hint ---\n")
    hint = discovery.get_contextual_hint({
        'current_app': 'terminal',
        'action': 'typing'
    })
    if hint:
        print(f"Title: {hint['title']}")
        print(f"Message: {hint['message']}")
    
    # Show progress
    print("\n--- Discovery Progress ---\n")
    progress = discovery.get_discovery_progress()
    print(json.dumps(progress, indent=2))
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
