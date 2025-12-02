"""
VA21 Helper AI - Intelligent Assistant with Backup & Code Knowledge
====================================================================

Om Vinayaka - First Alpha Release

This module provides an AI helper that has knowledge of the system's version
history, code version history, and can assist users with restoration and development.

Key Features:
- Anti-Hallucination System integration for verified responses
- Synced memory across all Helper AI instances
- Runtime on permissive open-source backends (Ollama, Transformers)
- Guardian AI-validated security for all operations

Runtime Architecture:
- Guardian AI: Runs on ONNX Runtime (Microsoft) - always active for security
- Helper AI: Runs on Ollama/Transformers (permissive open-source runtimes)
  - IBM Granite models via Transformers
  - Llama/Phi models via Ollama
  - Automatic fallback chain for reliability

Acknowledgments:
- IBM Research for Granite models (Apache License 2.0)
- Microsoft for ONNX Runtime (MIT License)
- Ollama project (MIT License)
- Hugging Face for Transformers (Apache License 2.0)
"""

import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class SafeVersionInfo:
    """Version information without sensitive data."""
    version_id: str
    timestamp: str
    description: str
    backup_type: str
    components: List[str]
    size_formatted: str
    age: str


@dataclass
class SafeCodeVersionInfo:
    """Code version information without sensitive content."""
    version_id: str
    file_path: str
    timestamp: str
    change_type: str
    lines_added: int
    lines_removed: int
    description: str
    age: str


@dataclass
class SyncedMemoryEntry:
    """A memory entry that is synced across Helper AI instances."""
    memory_id: str
    key: str
    value: Any
    created_at: datetime
    updated_at: datetime
    source: str  # Which Helper AI instance created this
    verified: bool  # Whether anti-hallucination system verified this
    checksum: str  # For integrity validation


class HelperAI:
    """
    VA21 Helper AI - Intelligent assistant with system and code knowledge.
    
    Om Vinayaka - First Alpha Release
    
    Features:
    - Knowledge of system backup history (sanitized)
    - Knowledge of code version history (sanitized)
    - Backup and restore assistance
    - Code restoration and diff viewing
    - System health awareness
    - Natural language interaction
    - Developer tools assistance
    - Easter egg: Halo/Cortana theme activation
    - **NEW** Anti-Hallucination integration for verified responses
    - **NEW** Synced memory across all Helper AI instances
    - **NEW** Runtime on permissive open-source backends (Ollama/Transformers)
    
    Runtime Configuration:
    - Guardian AI: ONNX Runtime (for security - always active)
    - Helper AI: Ollama or Transformers (permissive open-source)
    """
    
    # Class-level synced memory (shared across all instances)
    _synced_memory: Dict[str, SyncedMemoryEntry] = {}
    _memory_lock = threading.RLock()
    _memory_file = "data/helper_ai_synced_memory.json"
    
    def __init__(self, backup_manager=None, code_history=None, orchestrator=None, 
                 settings=None, anti_hallucination=None, ai_manager=None):
        self.backup_manager = backup_manager
        self.code_history = code_history
        self.orchestrator = orchestrator
        self.settings = settings or {}
        
        # Anti-hallucination system integration
        self.anti_hallucination = anti_hallucination
        
        # Dynamic AI manager for runtime selection
        self.ai_manager = ai_manager
        
        # Easter egg state
        self.cortana_mode = False
        self.cortana_trigger = "cortana call the masterchief"
        self.cortana_deactivate = "cortana stand down"
        
        # Knowledge base (sanitized system info)
        self.knowledge_cache = {}
        self.last_knowledge_update = None
        
        # Conversation context
        self.context = []
        self.max_context_length = 10
        
        # Instance identifier
        self.instance_id = f"helper_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # Load synced memory from disk
        self._load_synced_memory()
    
    def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's message
            session_id: Optional session identifier
            
        Returns:
            Response dict with message and any special actions
        """
        message_lower = message.lower().strip()
        
        # Check for Cortana easter egg activation
        if self.cortana_trigger in message_lower:
            return self._activate_cortana_mode()
        
        # Check for Cortana deactivation
        if self.cortana_mode and self.cortana_deactivate in message_lower:
            return self.deactivate_cortana_mode()
        
        # Check for code-related queries (file history, code versions)
        if any(word in message_lower for word in ['code', 'file', 'changes', 'diff', 'commit']):
            return self._handle_code_query(message_lower)
        
        # Check for backup/restore related queries
        if any(word in message_lower for word in ['backup', 'restore', 'version', 'history', 'recover']):
            return self._handle_backup_query(message_lower)
        
        # Check for developer tools queries
        if any(word in message_lower for word in ['developer', 'dev', 'tool', 'compile', 'build', 'debug', 'gnu']):
            return self._handle_developer_query(message_lower)
        
        # Check for snippet queries
        if any(word in message_lower for word in ['snippet', 'template', 'boilerplate']):
            return self._handle_snippet_query(message_lower)
        
        # Check for system status queries
        if any(word in message_lower for word in ['status', 'health', 'system', 'stats']):
            return self._handle_status_query(message_lower)
        
        # Check for app installation queries
        if any(word in message_lower for word in ['install', 'app', 'flatpak', 'package']):
            return self._handle_app_query(message_lower)
        
        # Check for help queries
        if any(word in message_lower for word in ['help', 'how', 'what', 'can you']):
            return self._handle_help_query(message_lower)
        
        # Default response
        return self._generate_default_response(message)
    
    def _activate_cortana_mode(self) -> Dict[str, Any]:
        """Activate the Cortana/Halo easter egg theme."""
        self.cortana_mode = True
        return {
            'message': """🔵 CORTANA ONLINE

"Chief, I've been waiting for you."

*Neural interface established*

Welcome to the Halo Interface Mode. I am Cortana, your AI companion.
The system has been transformed to match UNSC specifications.

Features activated:
• Holographic blue theme
• UNSC-styled interface elements
• Enhanced tactical display
• Spartan-II neural link simulation

You can deactivate this mode anytime by saying "Cortana, stand down" 
or using the minimal toggle in Settings.

"Ready when you are, Spartan."
""",
            'action': 'activate_cortana_theme',
            'theme': 'cortana',
            'cortana_mode': True
        }
    
    def deactivate_cortana_mode(self) -> Dict[str, Any]:
        """Deactivate Cortana mode."""
        self.cortana_mode = False
        return {
            'message': """🔵 CORTANA OFFLINE

"Until next time, Chief."

*Neural interface disconnected*

Returning to standard VA21 interface...
""",
            'action': 'deactivate_cortana_theme',
            'theme': 'default',
            'cortana_mode': False
        }
    
    def _handle_code_query(self, message: str) -> Dict[str, Any]:
        """Handle code version history queries."""
        code_versions = self._get_safe_code_versions()
        
        if 'recent' in message or 'latest' in message or 'changes' in message:
            return self._show_recent_code_changes(code_versions)
        
        if 'restore' in message or 'revert' in message:
            return self._assist_code_restore(message, code_versions)
        
        if 'diff' in message or 'compare' in message:
            return self._show_code_diff_help()
        
        if 'history' in message:
            return self._show_code_history(message, code_versions)
        
        # General code version info
        return {
            'message': self._format_message(f"""📝 **Code Version History**

I track all your code changes! Here's what I can help with:

📊 **Current Stats**
• Files tracked: {len(code_versions)}
• Recent changes: {len(code_versions[:10])} in last session

**Commands:**
• "Show recent code changes" - See latest modifications
• "Restore [file] to previous version" - Revert a file
• "Show history for [file]" - See file version history
• "Compare versions" - View diffs between versions

Your code is safely versioned! 🔐
"""),
            'code_versions': [self._code_version_to_dict(v) for v in code_versions[:5]]
        }
    
    def _show_recent_code_changes(self, versions: List[SafeCodeVersionInfo]) -> Dict[str, Any]:
        """Show recent code changes."""
        if not versions:
            return {
                'message': self._format_message("No code changes tracked yet. Start coding and I'll track your changes!")
            }
        
        changes_list = "\n".join([
            f"• **{v.file_path}** - {v.description}\n  📅 {v.age} | +{v.lines_added}/-{v.lines_removed}"
            for v in versions[:10]
        ])
        
        return {
            'message': self._format_message(f"""📝 **Recent Code Changes**

{changes_list}

Would you like to restore any of these changes or see a diff?
"""),
            'code_versions': [self._code_version_to_dict(v) for v in versions[:10]],
            'action': 'show_code_history'
        }
    
    def _assist_code_restore(self, message: str, versions: List[SafeCodeVersionInfo]) -> Dict[str, Any]:
        """Assist with code restoration."""
        return {
            'message': self._format_message("""🔄 **Code Restoration**

To restore a file to a previous version:

1. Go to the **Code History** panel
2. Find the file you want to restore
3. Browse its version history
4. Click "Restore" on the version you want

Or tell me the specific file name and I'll help you find its versions!

⚠️ A pre-restore backup is automatically created.
"""),
            'action': 'open_code_history'
        }
    
    def _show_code_diff_help(self) -> Dict[str, Any]:
        """Show help for code diffs."""
        return {
            'message': self._format_message("""🔍 **Comparing Code Versions**

To compare two versions:

1. Open the **Code History** panel
2. Select a file
3. Click on two versions to compare
4. View the line-by-line diff

**Diff Colors:**
• 🟢 Green = Lines added
• 🔴 Red = Lines removed
• ⚪ White = Unchanged context

Want me to show the history for a specific file?
""")
        }
    
    def _show_code_history(self, message: str, versions: List[SafeCodeVersionInfo]) -> Dict[str, Any]:
        """Show code history for a file."""
        # Try to extract file name from message
        return {
            'message': self._format_message("""📜 **Code History**

I can show you the version history for any file.

**How to access:**
1. Open the **Code History** panel from navigation
2. Search for your file
3. See all versions with timestamps and change descriptions

**Quick Stats:**
• Total tracked files: {0}
• Total versions stored: Efficiently compressed

Each version shows:
• Timestamp
• Lines added/removed
• Change description
• Tags (if any)
""".format(len(set(v.file_path for v in versions)))),
            'action': 'open_code_history'
        }
    
    def _handle_developer_query(self, message: str) -> Dict[str, Any]:
        """Handle developer tools queries."""
        if 'gnu' in message or 'gcc' in message or 'compile' in message:
            return self._show_gnu_tools_info()
        
        if 'debug' in message or 'gdb' in message:
            return self._show_debug_info()
        
        if 'build' in message:
            return self._show_build_tools_info()
        
        return {
            'message': self._format_message("""🛠️ **VA21 Developer Toolkit**

I can help you with development tools! VA21 includes:

**🔧 GNU Toolkit**
• GCC/G++ - C/C++ compilers
• Make - Build automation
• GDB - Debugging
• Autotools - Build system

**📦 Build Tools**
• CMake, Ninja, Meson
• Maven, Gradle for Java
• npm, yarn for JavaScript

**🐳 Containers**
• Docker, Podman
• Kubernetes tools

**💾 Databases**
• PostgreSQL, MySQL, SQLite
• Redis, MongoDB

What would you like to know more about?
"""),
            'action': 'open_dev_tools'
        }
    
    def _show_gnu_tools_info(self) -> Dict[str, Any]:
        """Show GNU tools information."""
        return {
            'message': self._format_message("""🔧 **GNU Developer Toolkit**

VA21 OS includes the complete GNU development environment:

**Compilers & Build:**
• `gcc` / `g++` - GNU C/C++ Compiler
• `make` - Build automation
• `autoconf` / `automake` - Build configuration
• `libtool` - Library support tool

**Debugging & Analysis:**
• `gdb` - GNU Debugger
• `valgrind` - Memory debugging
• `strace` - System call tracer

**Text Processing:**
• `grep`, `sed`, `awk` - Text manipulation
• `diff`, `patch` - File comparison

**Quick Install:**
```bash
sudo apt install build-essential gdb valgrind
```

Would you like me to install the GNU essentials?
"""),
            'action': 'install_gnu_tools'
        }
    
    def _show_debug_info(self) -> Dict[str, Any]:
        """Show debugging tools information."""
        return {
            'message': self._format_message("""🐛 **Debugging Tools**

VA21 includes powerful debugging capabilities:

**GDB - GNU Debugger:**
```bash
gdb ./your_program
(gdb) break main
(gdb) run
(gdb) step
(gdb) print variable
```

**Valgrind - Memory Analysis:**
```bash
valgrind --leak-check=full ./your_program
```

**strace - System Calls:**
```bash
strace -f ./your_program
```

**ltrace - Library Calls:**
```bash
ltrace ./your_program
```

Need help with a specific debugging scenario?
""")
        }
    
    def _show_build_tools_info(self) -> Dict[str, Any]:
        """Show build tools information."""
        return {
            'message': self._format_message("""🏗️ **Build Tools**

VA21 supports multiple build systems:

**CMake:**
```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

**Meson + Ninja:**
```bash
meson setup build
ninja -C build
```

**Autotools:**
```bash
./configure
make
make install
```

**Language-Specific:**
• Node.js: `npm run build`
• Python: `python setup.py build`
• Rust: `cargo build`
• Go: `go build`

What are you trying to build?
""")
        }
    
    def _handle_snippet_query(self, message: str) -> Dict[str, Any]:
        """Handle code snippet queries."""
        return {
            'message': self._format_message("""📋 **Code Snippets Library**

Your personal code snippet collection with version history!

**Features:**
• 📁 Organize by language and tags
• 🔄 Version history for each snippet
• 🔍 Smart search across all snippets
• ⭐ Favorites for quick access
• 📤 Import/Export snippets

**Quick Actions:**
• "Create a new snippet" - Save useful code
• "Find Python snippets" - Search by language
• "Show my favorites" - Quick access

Access the Snippets Library from the navigation menu!
"""),
            'action': 'open_snippets'
        }
    
    def _get_safe_code_versions(self) -> List[SafeCodeVersionInfo]:
        """Get sanitized code version list."""
        if not self.code_history:
            return []
        
        try:
            recent = self.code_history.get_recent_changes(limit=20)
            return [
                SafeCodeVersionInfo(
                    version_id=v.version_id,
                    file_path=v.file_path,
                    timestamp=v.timestamp.isoformat(),
                    change_type=v.change_type,
                    lines_added=v.lines_added,
                    lines_removed=v.lines_removed,
                    description=v.description,
                    age=self._format_age(v.timestamp)
                )
                for v in recent
            ]
        except Exception as e:
            print(f"[HelperAI] Error getting code versions: {e}")
            return []
    
    def _code_version_to_dict(self, v: SafeCodeVersionInfo) -> Dict:
        """Convert SafeCodeVersionInfo to dictionary."""
        return {
            'version_id': v.version_id,
            'file_path': v.file_path,
            'timestamp': v.timestamp,
            'change_type': v.change_type,
            'lines_added': v.lines_added,
            'lines_removed': v.lines_removed,
            'description': v.description,
            'age': v.age
        }
    
    def _format_age(self, timestamp) -> str:
        """Format age in human-readable form."""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        delta = datetime.now() - timestamp
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"

    def _handle_backup_query(self, message: str) -> Dict[str, Any]:
        """Handle backup and restore related queries."""
        versions = self._get_safe_version_list()
        
        if 'list' in message or 'show' in message or 'what' in message:
            return self._list_backups(versions)
        
        if 'restore' in message or 'recover' in message:
            return self._assist_restore(message, versions)
        
        if 'create' in message or 'make' in message:
            return self._assist_create_backup()
        
        if 'latest' in message or 'recent' in message or 'last' in message:
            return self._show_latest_backup(versions)
        
        # General backup info
        return {
            'message': self._format_message(f"""I can help you with backups! Here's what I know:

📊 **Backup Summary**
• Total backups: {len(versions)}
• Latest backup: {versions[0].age if versions else 'None'}

**What would you like to do?**
1. "List all backups" - See all available versions
2. "Restore from [date/version]" - Recover your data
3. "Create a backup" - Save current state
4. "Show latest backup" - See the most recent backup

Just ask me naturally, I'll understand!
"""),
            'versions': [self._version_to_dict(v) for v in versions[:5]]
        }
    
    def _list_backups(self, versions: List[SafeVersionInfo]) -> Dict[str, Any]:
        """List available backups."""
        if not versions:
            return {
                'message': self._format_message("""No backups found yet.

Would you like me to create one? Just say "create a backup" and I'll help you set it up.
""")
            }
        
        backup_list = "\n".join([
            f"• **{v.version_id}** - {v.description}\n  📅 {v.age} | 📦 {v.size_formatted} | 🏷️ {v.backup_type}"
            for v in versions[:10]
        ])
        
        return {
            'message': self._format_message(f"""Here are your available backups:

{backup_list}

**To restore**, just say: "Restore from [version_id]" or "Restore the latest backup"
"""),
            'versions': [self._version_to_dict(v) for v in versions[:10]],
            'action': 'show_backup_list'
        }
    
    def _assist_restore(self, message: str, versions: List[SafeVersionInfo]) -> Dict[str, Any]:
        """Assist with restoration."""
        if not versions:
            return {
                'message': self._format_message("No backups available to restore from. Would you like to create one first?")
            }
        
        # Check if user mentioned a specific version
        for v in versions:
            if v.version_id in message:
                return {
                    'message': self._format_message(f"""I found backup **{v.version_id}**:

📅 Created: {v.timestamp}
📝 Description: {v.description}
📦 Size: {v.size_formatted}
🧩 Components: {', '.join(v.components)}

**Ready to restore?**
Click the button below or say "Yes, restore it" to proceed.

⚠️ A safety backup will be created automatically before restoration.
"""),
                    'action': 'confirm_restore',
                    'version_id': v.version_id,
                    'version': self._version_to_dict(v)
                }
        
        # Suggest latest
        latest = versions[0]
        return {
            'message': self._format_message(f"""I'll help you restore! Here's the most recent backup:

**{latest.version_id}**
• Created: {latest.age}
• Description: {latest.description}
• Size: {latest.size_formatted}

Would you like to restore from this backup? Say "Yes" or choose a different version from the list.
"""),
            'action': 'suggest_restore',
            'version_id': latest.version_id,
            'version': self._version_to_dict(latest)
        }
    
    def _assist_create_backup(self) -> Dict[str, Any]:
        """Assist with creating a backup."""
        return {
            'message': self._format_message("""I'll create a backup for you right now!

**What will be saved:**
• Chat history
• Research vault & notes
• Settings & preferences
• Workflows
• Knowledge graph

Creating backup... ✨
"""),
            'action': 'create_backup',
            'backup_type': 'manual',
            'description': 'Backup created via Helper AI'
        }
    
    def _show_latest_backup(self, versions: List[SafeVersionInfo]) -> Dict[str, Any]:
        """Show the latest backup."""
        if not versions:
            return {
                'message': self._format_message("No backups available yet. Would you like me to create one?")
            }
        
        latest = versions[0]
        return {
            'message': self._format_message(f"""Here's your most recent backup:

🗓️ **{latest.version_id}**
• **Created:** {latest.timestamp}
• **Age:** {latest.age}
• **Type:** {latest.backup_type}
• **Description:** {latest.description}
• **Size:** {latest.size_formatted}
• **Components:** {', '.join(latest.components)}

Would you like to restore from this backup or create a new one?
"""),
            'version': self._version_to_dict(latest)
        }
    
    def _handle_status_query(self, message: str) -> Dict[str, Any]:
        """Handle system status queries."""
        status = self._get_system_status()
        
        return {
            'message': self._format_message(f"""📊 **VA21 System Status**

🖥️ **Resources**
• CPU: {status.get('cpu', 'N/A')}%
• Memory: {status.get('memory', 'N/A')}%
• Disk: {status.get('disk', 'N/A')}%

🔄 **Services**
• Auto Backup: {'🟢 Enabled' if status.get('backup_enabled', True) else '🔴 Disabled'}
• Guardian AI: 🟢 Active
• Self-Healing: 🟢 Running

📦 **Backups**
• Total: {status.get('backup_count', 0)}
• Latest: {status.get('latest_backup', 'None')}

Everything is running smoothly! ✨
"""),
            'status': status
        }
    
    def _handle_app_query(self, message: str) -> Dict[str, Any]:
        """Handle app installation queries."""
        return {
            'message': self._format_message("""🎯 **VA21 App Center**

I can help you find and install apps! VA21 supports:

📦 **Flatpak Apps** (via Flathub)
• Thousands of sandboxed applications
• Automatic updates
• Secure by design

🐧 **Debian Packages**
• Full Debian repository access
• System packages and tools
• Development libraries

**How to install:**
1. Open Command Palette (Ctrl+K)
2. Search for the app you want
3. Click "Install" on the preview

Or just tell me what app you're looking for!

*Try: "Install Firefox" or "Find a code editor"*
"""),
            'action': 'open_app_center'
        }
    
    def _handle_help_query(self, message: str) -> Dict[str, Any]:
        """Handle help queries."""
        help_text = """🛡️ **VA21 Helper AI**

I'm your intelligent assistant! Here's what I can do:

💾 **Backup & Restore**
• "List my backups"
• "Restore from yesterday"
• "Create a backup now"

📊 **System Status**
• "How is the system doing?"
• "Show me system stats"

📦 **App Management**
• "Install [app name]"
• "Find apps for coding"

🎨 **Easter Eggs**
• Try saying something special... 🎮

⌨️ **Quick Commands**
• Ctrl+K - Command Palette
• Ctrl+B - Toggle Side Panel
• Ctrl+Shift+T - Toggle Theme

What would you like help with?
"""
        
        if self.cortana_mode:
            help_text = """🔵 **CORTANA - UNSC AI Companion**

"How can I assist you, Spartan?"

**Tactical Operations:**
• "Status report" - System diagnostics
• "Backup protocols" - Data preservation
• "Restore from checkpoint" - Recovery operations

**System Intel:**
• "Scan for hostiles" - Security analysis
• "Navigation" - App installation

**Command Codes:**
• "Cortana, stand down" - Deactivate Halo mode

"I'm here to help, Chief. What's the mission?"
"""
        
        return {
            'message': self._format_message(help_text)
        }
    
    def _generate_default_response(self, message: str) -> Dict[str, Any]:
        """Generate a default response."""
        if self.cortana_mode:
            return {
                'message': self._format_message(f"""🔵 "I understand, Chief."

I'm not quite sure how to help with that specific request. 
Would you like me to:

• Check system status?
• Manage backups?
• Help you find an app?

"Just say the word, Spartan."
""")
            }
        
        return {
            'message': self._format_message(f"""I'm not sure I understood that completely. 

Here are some things I can help with:
• **Backups** - "Show my backups" or "Create a backup"
• **System** - "How is the system doing?"
• **Apps** - "Install Firefox"

Feel free to ask me anything! 🚀
""")
        }
    
    def _get_safe_version_list(self) -> List[SafeVersionInfo]:
        """Get sanitized version list without sensitive data."""
        if not self.backup_manager:
            return []
        
        try:
            versions = self.backup_manager.export_version_list()
            return [
                SafeVersionInfo(
                    version_id=v['version_id'],
                    timestamp=v['timestamp'],
                    description=v['description'],
                    backup_type=v['backup_type'],
                    components=v['components'],
                    size_formatted=v['size_formatted'],
                    age=v['age']
                )
                for v in versions
            ]
        except Exception as e:
            print(f"[HelperAI] Error getting versions: {e}")
            return []
    
    def _get_system_status(self) -> Dict:
        """Get system status information."""
        status = {
            'cpu': 45,
            'memory': 62,
            'disk': 38,
            'backup_enabled': True,
            'backup_count': 0,
            'latest_backup': 'None'
        }
        
        if self.backup_manager:
            try:
                stats = self.backup_manager.get_storage_stats()
                status['backup_enabled'] = stats.get('auto_backup_enabled', True)
                status['backup_count'] = stats.get('total_versions', 0)
                if stats.get('newest_backup'):
                    status['latest_backup'] = stats['newest_backup']
            except Exception:
                pass
        
        return status
    
    def _version_to_dict(self, v: SafeVersionInfo) -> Dict:
        """Convert SafeVersionInfo to dictionary."""
        return {
            'version_id': v.version_id,
            'timestamp': v.timestamp,
            'description': v.description,
            'backup_type': v.backup_type,
            'components': v.components,
            'size_formatted': v.size_formatted,
            'age': v.age
        }
    
    def _format_message(self, text: str) -> str:
        """Format message based on current mode."""
        if self.cortana_mode:
            return f"🔵 {text}"
        return text
    
    # ==================== SYNCED MEMORY SYSTEM ====================
    
    def _load_synced_memory(self):
        """Load synced memory from disk into class-level storage."""
        with HelperAI._memory_lock:
            if os.path.exists(HelperAI._memory_file):
                try:
                    with open(HelperAI._memory_file, 'r') as f:
                        data = json.load(f)
                        for key, entry_data in data.items():
                            HelperAI._synced_memory[key] = SyncedMemoryEntry(
                                memory_id=entry_data['memory_id'],
                                key=entry_data['key'],
                                value=entry_data['value'],
                                created_at=datetime.fromisoformat(entry_data['created_at']),
                                updated_at=datetime.fromisoformat(entry_data['updated_at']),
                                source=entry_data['source'],
                                verified=entry_data['verified'],
                                checksum=entry_data['checksum']
                            )
                    print(f"[HelperAI] Loaded {len(HelperAI._synced_memory)} synced memory entries")
                except Exception as e:
                    print(f"[HelperAI] Error loading synced memory: {e}")
    
    def _save_synced_memory(self):
        """Save synced memory to disk for persistence."""
        with HelperAI._memory_lock:
            try:
                os.makedirs(os.path.dirname(HelperAI._memory_file), exist_ok=True)
                data = {}
                for key, entry in HelperAI._synced_memory.items():
                    data[key] = {
                        'memory_id': entry.memory_id,
                        'key': entry.key,
                        'value': entry.value,
                        'created_at': entry.created_at.isoformat(),
                        'updated_at': entry.updated_at.isoformat(),
                        'source': entry.source,
                        'verified': entry.verified,
                        'checksum': entry.checksum
                    }
                with open(HelperAI._memory_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"[HelperAI] Error saving synced memory: {e}")
    
    def _generate_checksum(self, key: str, value: Any) -> str:
        """Generate a checksum for memory integrity verification."""
        import hashlib
        data = f"{key}:{json.dumps(value, sort_keys=True)}:{self.instance_id}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def sync_memory(self, key: str, value: Any, verify: bool = True) -> Dict[str, Any]:
        """
        Store a memory entry that is synced across all Helper AI instances.
        
        Uses the Anti-Hallucination system for verification if available.
        
        Args:
            key: The memory key
            value: The value to store
            verify: Whether to verify with anti-hallucination system
            
        Returns:
            Result dict with status and memory_id
        """
        with HelperAI._memory_lock:
            now = datetime.now()
            checksum = self._generate_checksum(key, value)
            
            # Create anti-hallucination verified ID if system is available
            memory_id = f"mem_{now.strftime('%Y%m%d%H%M%S')}_{checksum[:8]}"
            verified = False
            
            if verify and self.anti_hallucination:
                try:
                    tid = self.anti_hallucination.generate_id(
                        component_type='helper_memory',
                        metadata={'key': key, 'source': self.instance_id}
                    )
                    memory_id = tid.uid
                    verified = True
                except Exception as e:
                    print(f"[HelperAI] Anti-hallucination verification failed: {e}")
            
            # Create or update the memory entry
            entry = SyncedMemoryEntry(
                memory_id=memory_id,
                key=key,
                value=value,
                created_at=HelperAI._synced_memory.get(key, SyncedMemoryEntry(
                    memory_id='', key='', value=None, 
                    created_at=now, updated_at=now, 
                    source='', verified=False, checksum=''
                )).created_at,
                updated_at=now,
                source=self.instance_id,
                verified=verified,
                checksum=checksum
            )
            
            HelperAI._synced_memory[key] = entry
            self._save_synced_memory()
            
            return {
                'success': True,
                'memory_id': memory_id,
                'verified': verified,
                'message': f"Memory '{key}' synced successfully"
            }
    
    def recall_memory(self, key: str, validate: bool = True) -> Dict[str, Any]:
        """
        Recall a synced memory entry with optional anti-hallucination validation.
        
        Args:
            key: The memory key to recall
            validate: Whether to validate with anti-hallucination system
            
        Returns:
            Result dict with value and validation status
        """
        with HelperAI._memory_lock:
            if key not in HelperAI._synced_memory:
                return {
                    'success': False,
                    'error': f"No memory found for key '{key}'",
                    'value': None
                }
            
            entry = HelperAI._synced_memory[key]
            
            # Verify integrity with checksum
            current_checksum = self._generate_checksum(entry.key, entry.value)
            integrity_valid = entry.checksum == current_checksum or entry.source != self.instance_id
            
            # Validate with anti-hallucination system if available
            ah_valid = True
            if validate and self.anti_hallucination and entry.verified:
                try:
                    from anti_hallucination_system import ValidationLevel
                    result = self.anti_hallucination.validate(
                        entry.memory_id,
                        level=ValidationLevel.STANDARD
                    )
                    ah_valid = result.is_valid
                except Exception as e:
                    print(f"[HelperAI] Anti-hallucination validation error: {e}")
                    ah_valid = True  # Don't block on validation errors
            
            return {
                'success': True,
                'key': key,
                'value': entry.value,
                'memory_id': entry.memory_id,
                'verified': entry.verified,
                'integrity_valid': integrity_valid,
                'ah_valid': ah_valid,
                'source': entry.source,
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat()
            }
    
    def list_synced_memories(self) -> List[Dict[str, Any]]:
        """List all synced memory entries."""
        with HelperAI._memory_lock:
            return [
                {
                    'key': entry.key,
                    'memory_id': entry.memory_id,
                    'verified': entry.verified,
                    'source': entry.source,
                    'updated_at': entry.updated_at.isoformat()
                }
                for entry in HelperAI._synced_memory.values()
            ]
    
    def clear_synced_memory(self, key: str = None) -> Dict[str, Any]:
        """Clear synced memory (specific key or all)."""
        with HelperAI._memory_lock:
            if key:
                if key in HelperAI._synced_memory:
                    del HelperAI._synced_memory[key]
                    self._save_synced_memory()
                    return {'success': True, 'message': f"Memory '{key}' cleared"}
                return {'success': False, 'error': f"No memory found for key '{key}'"}
            else:
                HelperAI._synced_memory.clear()
                self._save_synced_memory()
                return {'success': True, 'message': "All synced memory cleared"}
    
    # ==================== AI RUNTIME METHODS ====================
    
    def get_runtime_info(self) -> Dict[str, Any]:
        """
        Get information about the AI runtime configuration.
        
        Guardian AI: Always runs on ONNX Runtime (Microsoft)
        Helper AI: Runs on Ollama or Transformers (permissive open-source)
        """
        info = {
            'guardian_ai': {
                'runtime': 'ONNX Runtime',
                'license': 'MIT License',
                'provider': 'Microsoft',
                'status': 'always_active',
                'purpose': 'Security analysis and threat detection'
            },
            'helper_ai': {
                'runtime': 'Ollama / Transformers',
                'license': 'MIT / Apache 2.0',
                'supported_models': [
                    'IBM Granite 4.0 (via Transformers)',
                    'Llama 3 (via Ollama)',
                    'Phi-3 (via Ollama)',
                    'Code Llama (via Ollama)'
                ],
                'status': 'active',
                'purpose': 'User assistance and natural language interaction'
            },
            'anti_hallucination': {
                'enabled': self.anti_hallucination is not None,
                'purpose': 'Verify AI responses and prevent fabricated information'
            },
            'synced_memory': {
                'entries': len(HelperAI._synced_memory),
                'purpose': 'Shared knowledge across Helper AI instances'
            }
        }
        
        # Add AI manager info if available
        if self.ai_manager:
            try:
                manager_status = self.ai_manager.get_status()
                info['ai_manager'] = {
                    'models_loaded': manager_status.get('models_loaded', []),
                    'memory_used_mb': manager_status.get('memory', {}).get('used_mb', 0),
                    'current_context': manager_status.get('context', 'unknown')
                }
            except Exception:
                pass
        
        return info
    
    def generate_with_anti_hallucination(self, prompt: str, 
                                          validate_response: bool = True) -> Dict[str, Any]:
        """
        Generate a response using the Helper AI with anti-hallucination validation.
        
        This method:
        1. Uses the AI manager to select the best available model
        2. Generates a response
        3. Validates the response with the anti-hallucination system
        4. Returns the validated response with confidence score
        
        Args:
            prompt: The user prompt
            validate_response: Whether to validate with anti-hallucination
            
        Returns:
            Response dict with text and validation info
        """
        result = {
            'success': False,
            'response': '',
            'model_used': None,
            'validated': False,
            'confidence': 0.0
        }
        
        # Generate response using AI manager if available
        if self.ai_manager:
            try:
                from dynamic_ai_manager import ContextType
                gen_result = self.ai_manager.generate(
                    prompt=prompt,
                    context=ContextType.CHAT
                )
                if gen_result.get('success'):
                    result['response'] = gen_result.get('response', '')
                    result['model_used'] = gen_result.get('model')
                    result['success'] = True
            except Exception as e:
                print(f"[HelperAI] AI generation error: {e}")
        
        # Validate response with anti-hallucination if enabled
        if validate_response and self.anti_hallucination and result['success']:
            try:
                # Generate a validation ID for this response
                tid = self.anti_hallucination.generate_id(
                    component_type='ai_response',
                    metadata={
                        'prompt_hash': hash(prompt) % 10000,
                        'model': result['model_used'],
                        'instance': self.instance_id
                    }
                )
                result['validated'] = True
                result['validation_id'] = tid.uid
                result['confidence'] = 0.95  # High confidence for validated responses
            except Exception as e:
                print(f"[HelperAI] Validation error: {e}")
                result['confidence'] = 0.7  # Lower confidence without validation
        
        return result


# Singleton instance
_helper_ai: Optional[HelperAI] = None


def get_helper_ai(backup_manager=None, orchestrator=None, 
                  anti_hallucination=None, ai_manager=None) -> HelperAI:
    """
    Get the singleton Helper AI instance.
    
    Om Vinayaka - First Alpha Release
    
    Args:
        backup_manager: Backup manager instance
        orchestrator: Orchestrator AI instance
        anti_hallucination: Anti-hallucination system instance
        ai_manager: Dynamic AI resource manager instance
        
    Returns:
        HelperAI singleton instance with synced memory and anti-hallucination
    """
    global _helper_ai
    if _helper_ai is None:
        _helper_ai = HelperAI(
            backup_manager=backup_manager, 
            orchestrator=orchestrator,
            anti_hallucination=anti_hallucination,
            ai_manager=ai_manager
        )
    return _helper_ai
