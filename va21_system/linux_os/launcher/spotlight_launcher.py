#!/usr/bin/env python3
"""
VA21 Research OS - Spotlight-like Launcher
============================================

A keyboard-driven launcher inspired by macOS Spotlight.
Activated with Cmd+Space (macOS) or Ctrl+Space (Linux/Windows).

Features:
- Universal search across apps, files, notes, commands
- Terminal tabs management
- Application launching
- Quick actions
- AI-powered suggestions

Keyboard shortcuts:
- Cmd/Ctrl+Space: Open launcher
- Escape: Close launcher
- Arrow keys: Navigate
- Enter: Execute
- Tab: Cycle categories
- Cmd/Ctrl+T: New terminal tab
- Cmd/Ctrl+N: New note

Om Vinayaka - Swift as thought, accessible as breath.
"""

import os
import sys
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class ResultType(Enum):
    """Types of search results."""
    APPLICATION = "application"
    TERMINAL = "terminal"
    FILE = "file"
    NOTE = "note"
    COMMAND = "command"
    SEARCH = "search"
    SETTING = "setting"
    ACTION = "action"
    RECENT = "recent"


@dataclass
class SearchResult:
    """A single search result."""
    id: str
    title: str
    subtitle: str
    result_type: ResultType
    icon: str
    action: Callable = None
    keywords: List[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class TerminalTab:
    """A terminal tab."""
    id: str
    title: str
    working_dir: str
    process: Any = None
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class VA21Launcher:
    """
    VA21 Spotlight-like Launcher
    
    A universal launcher for the VA21 Research OS providing quick access
    to everything via keyboard.
    
    Features:
    - Fuzzy search across all resources
    - Terminal tab management
    - Application launching
    - Quick command execution
    - AI-powered suggestions
    - Recent items tracking
    """
    
    VERSION = "1.0.0"
    
    # Category icons
    ICONS = {
        ResultType.APPLICATION: "📱",
        ResultType.TERMINAL: "💻",
        ResultType.FILE: "📄",
        ResultType.NOTE: "📝",
        ResultType.COMMAND: "⚡",
        ResultType.SEARCH: "🔍",
        ResultType.SETTING: "⚙️",
        ResultType.ACTION: "🎯",
        ResultType.RECENT: "🕐",
    }
    
    def __init__(self, config_path: str = "/va21/config"):
        self.config_path = config_path
        self.is_visible = False
        self.current_query = ""
        self.selected_index = 0
        self.results: List[SearchResult] = []
        
        # Terminal tabs
        self.terminal_tabs: Dict[str, TerminalTab] = {}
        self.active_terminal: Optional[str] = None
        
        # Recent items
        self.recent_items: List[SearchResult] = []
        self.max_recent = 10
        
        # Registered applications
        self.applications: Dict[str, SearchResult] = {}
        
        # Quick actions
        self.actions: Dict[str, SearchResult] = {}
        
        # Settings
        self.settings: Dict[str, SearchResult] = {}
        
        # Search providers
        self.search_providers: List[Callable] = []
        
        # Keyboard shortcuts
        self.shortcuts = {
            "toggle_launcher": ["ctrl+space", "cmd+space", "alt+space"],
            "close": ["escape"],
            "select": ["enter", "return"],
            "up": ["up", "ctrl+p", "ctrl+k"],
            "down": ["down", "ctrl+n", "ctrl+j"],
            "new_terminal": ["ctrl+t", "cmd+t"],
            "new_note": ["ctrl+n", "cmd+n"],
            "tab_next": ["ctrl+tab"],
            "tab_prev": ["ctrl+shift+tab"],
        }
        
        # Initialize default items
        self._init_applications()
        self._init_actions()
        self._init_settings()
        
        # Load recent items
        self._load_recent()
        
        print(f"[Launcher] VA21 Launcher v{self.VERSION} initialized")
    
    def _init_applications(self):
        """Initialize default applications."""
        default_apps = [
            SearchResult(
                id="app_terminal",
                title="Terminal",
                subtitle="Open a new terminal tab",
                result_type=ResultType.APPLICATION,
                icon="💻",
                keywords=["terminal", "shell", "bash", "console", "cmd"]
            ),
            SearchResult(
                id="app_browser",
                title="Chromium Browser",
                subtitle="Secure web browser",
                result_type=ResultType.APPLICATION,
                icon="🌐",
                keywords=["browser", "web", "chromium", "chrome", "internet"]
            ),
            SearchResult(
                id="app_research",
                title="Research Center",
                subtitle="Research Command Center",
                result_type=ResultType.APPLICATION,
                icon="🔬",
                keywords=["research", "science", "lab", "knowledge"]
            ),
            SearchResult(
                id="app_vault",
                title="Knowledge Vault",
                subtitle="Obsidian-style notes",
                result_type=ResultType.APPLICATION,
                icon="📚",
                keywords=["vault", "notes", "obsidian", "knowledge", "wiki"]
            ),
            SearchResult(
                id="app_guardian",
                title="Guardian Dashboard",
                subtitle="Security monitoring",
                result_type=ResultType.APPLICATION,
                icon="🛡️",
                keywords=["guardian", "security", "protection", "scan"]
            ),
            SearchResult(
                id="app_writing",
                title="Writing Suite",
                subtitle="Professional writing tools",
                result_type=ResultType.APPLICATION,
                icon="✍️",
                keywords=["write", "writing", "document", "paper", "article"]
            ),
            SearchResult(
                id="app_settings",
                title="Settings",
                subtitle="System configuration",
                result_type=ResultType.APPLICATION,
                icon="⚙️",
                keywords=["settings", "config", "preferences", "options"]
            ),
            SearchResult(
                id="app_files",
                title="File Manager",
                subtitle="Browse files",
                result_type=ResultType.APPLICATION,
                icon="📁",
                keywords=["files", "folder", "browse", "explorer"]
            ),
            SearchResult(
                id="app_search",
                title="SearXNG Search",
                subtitle="Privacy-respecting search",
                result_type=ResultType.APPLICATION,
                icon="🔍",
                keywords=["search", "searxng", "google", "find"]
            ),
            SearchResult(
                id="app_zork",
                title="Zork Interface",
                subtitle="Text adventure OS interface",
                result_type=ResultType.APPLICATION,
                icon="🎮",
                keywords=["zork", "adventure", "game", "text"]
            ),
        ]
        
        for app in default_apps:
            self.applications[app.id] = app
    
    def _init_actions(self):
        """Initialize quick actions."""
        default_actions = [
            SearchResult(
                id="action_new_terminal",
                title="New Terminal",
                subtitle="Open a new terminal tab",
                result_type=ResultType.ACTION,
                icon="➕",
                keywords=["new", "terminal", "tab"]
            ),
            SearchResult(
                id="action_new_note",
                title="New Note",
                subtitle="Create a new note",
                result_type=ResultType.ACTION,
                icon="📝",
                keywords=["new", "note", "create"]
            ),
            SearchResult(
                id="action_scan",
                title="Security Scan",
                subtitle="Run a security scan",
                result_type=ResultType.ACTION,
                icon="🔒",
                keywords=["scan", "security", "virus", "check"]
            ),
            SearchResult(
                id="action_search_web",
                title="Search Web...",
                subtitle="Search the internet",
                result_type=ResultType.ACTION,
                icon="🌐",
                keywords=["search", "web", "internet"]
            ),
            SearchResult(
                id="action_lock",
                title="Lock Screen",
                subtitle="Lock the screen",
                result_type=ResultType.ACTION,
                icon="🔐",
                keywords=["lock", "secure", "screen"]
            ),
            SearchResult(
                id="action_shutdown",
                title="Shutdown",
                subtitle="Shutdown VA21 OS",
                result_type=ResultType.ACTION,
                icon="⏻",
                keywords=["shutdown", "power", "off", "exit", "quit"]
            ),
        ]
        
        for action in default_actions:
            self.actions[action.id] = action
    
    def _init_settings(self):
        """Initialize settings items."""
        default_settings = [
            SearchResult(
                id="setting_hints",
                title="Toggle Hints",
                subtitle="Enable/disable helper hints",
                result_type=ResultType.SETTING,
                icon="💡",
                keywords=["hints", "help", "tips"]
            ),
            SearchResult(
                id="setting_theme",
                title="Theme",
                subtitle="Change color theme",
                result_type=ResultType.SETTING,
                icon="🎨",
                keywords=["theme", "color", "dark", "light"]
            ),
            SearchResult(
                id="setting_keyboard",
                title="Keyboard Shortcuts",
                subtitle="View and customize shortcuts",
                result_type=ResultType.SETTING,
                icon="⌨️",
                keywords=["keyboard", "shortcuts", "keys", "hotkeys"]
            ),
            SearchResult(
                id="setting_security",
                title="Security Settings",
                subtitle="Guardian AI configuration",
                result_type=ResultType.SETTING,
                icon="🛡️",
                keywords=["security", "guardian", "protection"]
            ),
        ]
        
        for setting in default_settings:
            self.settings[setting.id] = setting
    
    def _load_recent(self):
        """Load recent items from disk."""
        recent_file = os.path.join(self.config_path, "recent.json")
        try:
            if os.path.exists(recent_file):
                with open(recent_file, 'r') as f:
                    data = json.load(f)
                # Reconstruct recent items
                for item_data in data:
                    result = SearchResult(
                        id=item_data['id'],
                        title=item_data['title'],
                        subtitle=item_data['subtitle'],
                        result_type=ResultType.RECENT,
                        icon=item_data.get('icon', '🕐'),
                        keywords=item_data.get('keywords', [])
                    )
                    self.recent_items.append(result)
        except Exception as e:
            print(f"[Launcher] Error loading recent: {e}")
    
    def _save_recent(self):
        """Save recent items to disk."""
        recent_file = os.path.join(self.config_path, "recent.json")
        try:
            os.makedirs(self.config_path, exist_ok=True)
            data = []
            for item in self.recent_items[:self.max_recent]:
                data.append({
                    'id': item.id,
                    'title': item.title,
                    'subtitle': item.subtitle,
                    'icon': item.icon,
                    'keywords': item.keywords
                })
            with open(recent_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[Launcher] Error saving recent: {e}")
    
    def add_to_recent(self, result: SearchResult):
        """Add an item to recent history."""
        # Remove if already exists
        self.recent_items = [r for r in self.recent_items if r.id != result.id]
        # Add to front
        self.recent_items.insert(0, result)
        # Trim to max
        self.recent_items = self.recent_items[:self.max_recent]
        # Save
        self._save_recent()
    
    def search(self, query: str) -> List[SearchResult]:
        """
        Search across all resources.
        
        Args:
            query: Search query
            
        Returns:
            List of matching results
        """
        self.current_query = query
        results = []
        query_lower = query.lower()
        
        # If empty query, show recent items
        if not query.strip():
            return self.recent_items[:5]
        
        # Search applications
        for app in self.applications.values():
            score = self._match_score(query_lower, app)
            if score > 0:
                app.score = score
                results.append(app)
        
        # Search actions
        for action in self.actions.values():
            score = self._match_score(query_lower, action)
            if score > 0:
                action.score = score
                results.append(action)
        
        # Search settings
        for setting in self.settings.values():
            score = self._match_score(query_lower, setting)
            if score > 0:
                setting.score = score
                results.append(setting)
        
        # Search terminal tabs
        for tab in self.terminal_tabs.values():
            if query_lower in tab.title.lower():
                results.append(SearchResult(
                    id=f"terminal_{tab.id}",
                    title=tab.title,
                    subtitle=f"Terminal: {tab.working_dir}",
                    result_type=ResultType.TERMINAL,
                    icon="💻",
                    score=0.8
                ))
        
        # Custom search providers
        for provider in self.search_providers:
            try:
                provider_results = provider(query)
                results.extend(provider_results)
            except Exception as e:
                print(f"[Launcher] Search provider error: {e}")
        
        # Web search fallback
        if query.strip():
            results.append(SearchResult(
                id="search_web",
                title=f"Search web for '{query}'",
                subtitle="Use SearXNG to search the internet",
                result_type=ResultType.SEARCH,
                icon="🔍",
                score=0.1
            ))
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        
        self.results = results[:20]
        return self.results
    
    def _match_score(self, query: str, result: SearchResult) -> float:
        """Calculate match score for a result."""
        score = 0.0
        
        # Exact match in title
        if query == result.title.lower():
            score += 1.0
        elif query in result.title.lower():
            score += 0.8
        
        # Match in subtitle
        if query in result.subtitle.lower():
            score += 0.3
        
        # Match in keywords
        for keyword in result.keywords:
            if query == keyword:
                score += 0.7
            elif query in keyword or keyword in query:
                score += 0.4
        
        # Fuzzy matching
        if score == 0:
            # Check if all characters appear in order
            title_lower = result.title.lower()
            pos = 0
            for char in query:
                found = title_lower.find(char, pos)
                if found >= 0:
                    pos = found + 1
                    score += 0.1
        
        return score
    
    def execute(self, result: SearchResult) -> Optional[str]:
        """
        Execute a search result action.
        
        Args:
            result: The result to execute
            
        Returns:
            Optional message
        """
        self.add_to_recent(result)
        
        if result.action:
            return result.action()
        
        # Default actions based on type
        if result.result_type == ResultType.APPLICATION:
            return self._launch_application(result)
        elif result.result_type == ResultType.TERMINAL:
            return self._switch_terminal(result.id.replace("terminal_", ""))
        elif result.result_type == ResultType.ACTION:
            return self._execute_action(result)
        elif result.result_type == ResultType.SEARCH:
            return f"search:{self.current_query}"
        elif result.result_type == ResultType.SETTING:
            return self._open_setting(result)
        
        return None
    
    def _launch_application(self, app: SearchResult) -> str:
        """Launch an application."""
        return f"launch:{app.id}"
    
    def _execute_action(self, action: SearchResult) -> str:
        """Execute a quick action."""
        return f"action:{action.id}"
    
    def _open_setting(self, setting: SearchResult) -> str:
        """Open a setting."""
        return f"setting:{setting.id}"
    
    def _switch_terminal(self, tab_id: str) -> str:
        """Switch to a terminal tab."""
        if tab_id in self.terminal_tabs:
            self.active_terminal = tab_id
            return f"terminal:{tab_id}"
        return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Terminal Tab Management
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_terminal(self, title: str = None, working_dir: str = None) -> TerminalTab:
        """Create a new terminal tab."""
        tab_id = f"term_{datetime.now().strftime('%H%M%S%f')}"
        
        if title is None:
            title = f"Terminal {len(self.terminal_tabs) + 1}"
        
        if working_dir is None:
            working_dir = os.path.expanduser("~")
        
        tab = TerminalTab(
            id=tab_id,
            title=title,
            working_dir=working_dir,
            is_active=True
        )
        
        # Deactivate other tabs
        for other in self.terminal_tabs.values():
            other.is_active = False
        
        self.terminal_tabs[tab_id] = tab
        self.active_terminal = tab_id
        
        print(f"[Launcher] Created terminal: {title}")
        return tab
    
    def close_terminal(self, tab_id: str) -> bool:
        """Close a terminal tab."""
        if tab_id not in self.terminal_tabs:
            return False
        
        tab = self.terminal_tabs.pop(tab_id)
        
        # Switch to another tab if this was active
        if self.active_terminal == tab_id:
            if self.terminal_tabs:
                self.active_terminal = list(self.terminal_tabs.keys())[-1]
                self.terminal_tabs[self.active_terminal].is_active = True
            else:
                self.active_terminal = None
        
        print(f"[Launcher] Closed terminal: {tab.title}")
        return True
    
    def get_terminal_tabs(self) -> List[TerminalTab]:
        """Get all terminal tabs."""
        return list(self.terminal_tabs.values())
    
    def rename_terminal(self, tab_id: str, new_title: str) -> bool:
        """Rename a terminal tab."""
        if tab_id in self.terminal_tabs:
            self.terminal_tabs[tab_id].title = new_title
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UI Interface (Text-based)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def render(self) -> str:
        """Render the launcher UI."""
        lines = []
        
        # Header
        lines.append("╔" + "═" * 60 + "╗")
        lines.append("║" + " VA21 LAUNCHER ".center(60) + "║")
        lines.append("╠" + "═" * 60 + "╣")
        
        # Search input
        query_display = self.current_query if self.current_query else "Type to search..."
        lines.append(f"║ 🔍 {query_display:<56} ║")
        lines.append("╠" + "═" * 60 + "╣")
        
        # Results
        if not self.results:
            if not self.current_query:
                lines.append("║" + " Recent Items ".center(60) + "║")
                for i, item in enumerate(self.recent_items[:5]):
                    prefix = "►" if i == self.selected_index else " "
                    lines.append(f"║ {prefix} {item.icon} {item.title:<50} ║")
            else:
                lines.append("║" + " No results found ".center(60) + "║")
        else:
            for i, result in enumerate(self.results[:10]):
                prefix = "►" if i == self.selected_index else " "
                type_badge = self.ICONS.get(result.result_type, "")
                title = result.title[:40]
                lines.append(f"║ {prefix} {result.icon} {title:<45} {type_badge} ║")
                if i == self.selected_index:
                    subtitle = result.subtitle[:55]
                    lines.append(f"║    {subtitle:<56} ║")
        
        # Footer
        lines.append("╠" + "═" * 60 + "╣")
        lines.append("║ ⌨️  ↑↓:Navigate  ⏎:Select  ⎋:Close  ⌘T:New Terminal   ║")
        lines.append("╚" + "═" * 60 + "╝")
        
        return "\n".join(lines)
    
    def handle_key(self, key: str) -> Optional[str]:
        """
        Handle keyboard input.
        
        Args:
            key: Key pressed
            
        Returns:
            Optional action to execute
        """
        if key in ["up", "ctrl+p", "ctrl+k"]:
            self.selected_index = max(0, self.selected_index - 1)
        elif key in ["down", "ctrl+n", "ctrl+j"]:
            max_idx = len(self.results) - 1 if self.results else len(self.recent_items) - 1
            self.selected_index = min(max_idx, self.selected_index + 1)
        elif key in ["enter", "return"]:
            items = self.results if self.results else self.recent_items[:5]
            if 0 <= self.selected_index < len(items):
                return self.execute(items[self.selected_index])
        elif key == "escape":
            self.is_visible = False
            return "close"
        elif key in ["ctrl+t", "cmd+t"]:
            self.create_terminal()
            return "new_terminal"
        elif key == "tab":
            # Cycle through categories
            pass
        
        return None
    
    def get_keyboard_help(self) -> str:
        """Get keyboard shortcuts help."""
        return """
╔════════════════════════════════════════════════════════════════╗
║                    KEYBOARD SHORTCUTS                          ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  LAUNCHER                                                      ║
║  ─────────────────────────────────────────────────────────────║
║  Ctrl+Space / Cmd+Space    Open/Close Launcher                 ║
║  Escape                    Close Launcher                      ║
║  ↑ / ↓                     Navigate results                    ║
║  Enter                     Select/Execute                      ║
║  Tab                       Cycle categories                    ║
║                                                                ║
║  TERMINALS                                                     ║
║  ─────────────────────────────────────────────────────────────║
║  Ctrl+T / Cmd+T            New terminal tab                    ║
║  Ctrl+W / Cmd+W            Close terminal tab                  ║
║  Ctrl+Tab                  Next terminal                       ║
║  Ctrl+Shift+Tab            Previous terminal                   ║
║  Ctrl+1-9                  Switch to tab 1-9                   ║
║                                                                ║
║  NAVIGATION                                                    ║
║  ─────────────────────────────────────────────────────────────║
║  Ctrl+N / Cmd+N            New note                            ║
║  Ctrl+F / Cmd+F            Find in page                        ║
║  Ctrl+G / Cmd+G            Go to (files, notes)                ║
║  Ctrl+P / Cmd+P            Command palette                     ║
║                                                                ║
║  WINDOWS                                                       ║
║  ─────────────────────────────────────────────────────────────║
║  Ctrl+H / Cmd+H            Split horizontally                  ║
║  Ctrl+V / Cmd+V            Split vertically                    ║
║  Ctrl+Arrow                Move focus                          ║
║  Ctrl+Shift+Arrow          Resize pane                         ║
║  Ctrl+Q / Cmd+Q            Quit                                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_launcher_instance = None

def get_launcher() -> VA21Launcher:
    """Get the launcher singleton."""
    global _launcher_instance
    if _launcher_instance is None:
        _launcher_instance = VA21Launcher()
    return _launcher_instance


if __name__ == "__main__":
    launcher = get_launcher()
    
    # Test search
    print("Testing launcher...")
    results = launcher.search("terminal")
    print(f"Found {len(results)} results for 'terminal'")
    
    # Render UI
    print(launcher.render())
    
    # Show keyboard help
    print(launcher.get_keyboard_help())
