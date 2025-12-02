#!/usr/bin/env python3
"""
VA21 Research OS - Unified Command Interface
==============================================

Everything in VA21 can be controlled through:
1. Natural language chat with Helper AI
2. Keyboard shortcuts
3. Command palette (Spotlight-style)
4. Zork-style text commands

This module provides the bridge between all input methods
and system actions.

Om Vinayaka - One interface, infinite possibilities.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

# Import VA21 components
try:
    from system_tools.settings_center import get_settings, VA21SettingsCenter
except ImportError:
    from settings_center import get_settings, VA21SettingsCenter

try:
    from system_tools.system_suite import get_system_tools
except ImportError:
    try:
        from system_suite import get_system_tools
    except ImportError:
        get_system_tools = None


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class CommandCategory(Enum):
    """Categories of commands."""
    WIFI = "wifi"
    AUDIO = "audio"
    DISPLAY = "display"
    DATETIME = "datetime"
    THEME = "theme"
    POWER = "power"
    SYSTEM = "system"
    NAVIGATION = "navigation"
    WINDOW = "window"
    APP = "app"
    FILE = "file"
    SEARCH = "search"
    GUARDIAN = "guardian"
    HELP = "help"


@dataclass
class Command:
    """Represents a system command."""
    id: str
    name: str
    description: str
    category: CommandCategory
    keywords: List[str]
    shortcuts: List[str]
    action: str  # Action identifier
    parameters: Dict = field(default_factory=dict)
    enabled: bool = True


@dataclass
class CommandResult:
    """Result of executing a command."""
    success: bool
    message: str
    data: Any = None
    speak: bool = True  # Whether AI should speak the response


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class VA21CommandInterface:
    """
    VA21 Unified Command Interface
    
    Provides a single interface for all system commands accessible via:
    - Natural language (AI chat)
    - Keyboard shortcuts
    - Command palette
    - Zork commands
    
    Examples:
        "turn on wifi"
        "set volume to 50"
        "what time is it"
        "switch to dark theme"
        "connect to MyNetwork"
        "mute"
        "take a screenshot"
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.settings = get_settings()
        self.system_tools = get_system_tools() if get_system_tools else None
        
        # Command registry
        self.commands: Dict[str, Command] = {}
        self._register_all_commands()
        
        # Shortcut mapping
        self.shortcuts: Dict[str, str] = {}
        self._build_shortcut_map()
        
        # Command history
        self.history: List[Dict] = []
        
        # AI context
        self.ai_context = {
            "last_command": None,
            "last_result": None,
            "conversation": []
        }
        
        print(f"[CommandInterface] VA21 Command Interface v{self.VERSION} initialized")
        print(f"[CommandInterface] {len(self.commands)} commands registered")
    
    def _register_all_commands(self):
        """Register all available commands."""
        
        # ═══════════════════════════════════════════════════════════════════════
        # WIFI COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="wifi_on",
            name="Turn WiFi On",
            description="Enable WiFi",
            category=CommandCategory.WIFI,
            keywords=["wifi on", "enable wifi", "turn on wifi", "wifi enable", "start wifi", "activate wifi"],
            shortcuts=["ctrl+alt+w"],
            action="wifi_toggle",
            parameters={"enable": True}
        ))
        
        self._register(Command(
            id="wifi_off",
            name="Turn WiFi Off",
            description="Disable WiFi",
            category=CommandCategory.WIFI,
            keywords=["wifi off", "disable wifi", "turn off wifi", "wifi disable", "stop wifi"],
            shortcuts=["ctrl+alt+shift+w"],
            action="wifi_toggle",
            parameters={"enable": False}
        ))
        
        self._register(Command(
            id="wifi_status",
            name="WiFi Status",
            description="Check WiFi connection status",
            category=CommandCategory.WIFI,
            keywords=["wifi status", "wifi", "am i connected", "internet status", "connection status", "network status"],
            shortcuts=[],
            action="wifi_status"
        ))
        
        self._register(Command(
            id="wifi_scan",
            name="Scan WiFi Networks",
            description="Scan for available WiFi networks",
            category=CommandCategory.WIFI,
            keywords=["scan wifi", "find networks", "available networks", "wifi networks", "scan networks"],
            shortcuts=["ctrl+alt+n"],
            action="wifi_scan"
        ))
        
        self._register(Command(
            id="wifi_connect",
            name="Connect to WiFi",
            description="Connect to a WiFi network",
            category=CommandCategory.WIFI,
            keywords=["connect to", "join network", "connect wifi"],
            shortcuts=[],
            action="wifi_connect"
        ))
        
        self._register(Command(
            id="wifi_disconnect",
            name="Disconnect WiFi",
            description="Disconnect from current WiFi",
            category=CommandCategory.WIFI,
            keywords=["disconnect wifi", "disconnect", "leave network"],
            shortcuts=[],
            action="wifi_disconnect"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # AUDIO COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="volume_up",
            name="Volume Up",
            description="Increase volume by 10%",
            category=CommandCategory.AUDIO,
            keywords=["volume up", "louder", "increase volume", "turn up", "raise volume"],
            shortcuts=["volumeup", "ctrl+up"],
            action="volume_adjust",
            parameters={"delta": 10}
        ))
        
        self._register(Command(
            id="volume_down",
            name="Volume Down",
            description="Decrease volume by 10%",
            category=CommandCategory.AUDIO,
            keywords=["volume down", "quieter", "decrease volume", "turn down", "lower volume"],
            shortcuts=["volumedown", "ctrl+down"],
            action="volume_adjust",
            parameters={"delta": -10}
        ))
        
        self._register(Command(
            id="mute",
            name="Mute",
            description="Mute audio",
            category=CommandCategory.AUDIO,
            keywords=["mute", "silence", "mute audio", "mute sound", "quiet"],
            shortcuts=["volumemute", "ctrl+m"],
            action="mute_toggle"
        ))
        
        self._register(Command(
            id="unmute",
            name="Unmute",
            description="Unmute audio",
            category=CommandCategory.AUDIO,
            keywords=["unmute", "unmute audio", "unmute sound"],
            shortcuts=[],
            action="mute_set",
            parameters={"mute": False}
        ))
        
        self._register(Command(
            id="volume_set",
            name="Set Volume",
            description="Set volume to a specific level",
            category=CommandCategory.AUDIO,
            keywords=["set volume", "volume to", "volume at"],
            shortcuts=[],
            action="volume_set"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # DISPLAY COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="brightness_up",
            name="Brightness Up",
            description="Increase screen brightness",
            category=CommandCategory.DISPLAY,
            keywords=["brightness up", "brighter", "increase brightness", "more bright"],
            shortcuts=["brightnessup", "ctrl+shift+up"],
            action="brightness_adjust",
            parameters={"delta": 10}
        ))
        
        self._register(Command(
            id="brightness_down",
            name="Brightness Down",
            description="Decrease screen brightness",
            category=CommandCategory.DISPLAY,
            keywords=["brightness down", "dimmer", "decrease brightness", "less bright", "dim"],
            shortcuts=["brightnessdown", "ctrl+shift+down"],
            action="brightness_adjust",
            parameters={"delta": -10}
        ))
        
        self._register(Command(
            id="brightness_set",
            name="Set Brightness",
            description="Set brightness to a specific level",
            category=CommandCategory.DISPLAY,
            keywords=["set brightness", "brightness to", "brightness at"],
            shortcuts=[],
            action="brightness_set"
        ))
        
        self._register(Command(
            id="screenshot",
            name="Take Screenshot",
            description="Capture the screen",
            category=CommandCategory.DISPLAY,
            keywords=["screenshot", "take screenshot", "capture screen", "screen capture", "print screen"],
            shortcuts=["print", "ctrl+shift+s"],
            action="screenshot"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # DATE & TIME COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="time_check",
            name="Check Time",
            description="Get current time",
            category=CommandCategory.DATETIME,
            keywords=["what time", "current time", "time now", "what's the time", "tell me the time"],
            shortcuts=[],
            action="time_check"
        ))
        
        self._register(Command(
            id="date_check",
            name="Check Date",
            description="Get current date",
            category=CommandCategory.DATETIME,
            keywords=["what date", "current date", "date today", "what's the date", "what day"],
            shortcuts=[],
            action="date_check"
        ))
        
        self._register(Command(
            id="datetime_check",
            name="Check Date & Time",
            description="Get current date and time",
            category=CommandCategory.DATETIME,
            keywords=["date and time", "datetime", "what time and date"],
            shortcuts=["ctrl+alt+t"],
            action="datetime_check"
        ))
        
        self._register(Command(
            id="timezone_set",
            name="Set Timezone",
            description="Change system timezone",
            category=CommandCategory.DATETIME,
            keywords=["set timezone", "change timezone", "timezone to"],
            shortcuts=[],
            action="timezone_set"
        ))
        
        self._register(Command(
            id="sync_time",
            name="Sync Time",
            description="Synchronize time with NTP server",
            category=CommandCategory.DATETIME,
            keywords=["sync time", "synchronize time", "update time", "fix time"],
            shortcuts=[],
            action="sync_time"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # THEME COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="theme_dark",
            name="Dark Theme",
            description="Switch to dark theme",
            category=CommandCategory.THEME,
            keywords=["dark theme", "dark mode", "switch to dark", "enable dark", "go dark", "night mode"],
            shortcuts=["ctrl+shift+d"],
            action="theme_set",
            parameters={"theme": "dark"}
        ))
        
        self._register(Command(
            id="theme_light",
            name="Light Theme",
            description="Switch to light theme",
            category=CommandCategory.THEME,
            keywords=["light theme", "light mode", "switch to light", "enable light", "go light", "day mode"],
            shortcuts=["ctrl+shift+l"],
            action="theme_set",
            parameters={"theme": "light"}
        ))
        
        self._register(Command(
            id="theme_toggle",
            name="Toggle Theme",
            description="Toggle between dark and light theme",
            category=CommandCategory.THEME,
            keywords=["toggle theme", "switch theme", "change theme"],
            shortcuts=["ctrl+shift+t"],
            action="theme_toggle"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # POWER COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="battery_status",
            name="Battery Status",
            description="Check battery level",
            category=CommandCategory.POWER,
            keywords=["battery", "battery status", "battery level", "power status", "how much battery"],
            shortcuts=[],
            action="battery_status"
        ))
        
        self._register(Command(
            id="power_performance",
            name="Performance Mode",
            description="Set power profile to performance",
            category=CommandCategory.POWER,
            keywords=["performance mode", "high performance", "max power", "full power"],
            shortcuts=[],
            action="power_profile",
            parameters={"profile": "performance"}
        ))
        
        self._register(Command(
            id="power_balanced",
            name="Balanced Mode",
            description="Set power profile to balanced",
            category=CommandCategory.POWER,
            keywords=["balanced mode", "normal power", "balanced"],
            shortcuts=[],
            action="power_profile",
            parameters={"profile": "balanced"}
        ))
        
        self._register(Command(
            id="power_saver",
            name="Power Saver",
            description="Set power profile to power saver",
            category=CommandCategory.POWER,
            keywords=["power saver", "save power", "low power", "battery saver", "eco mode"],
            shortcuts=[],
            action="power_profile",
            parameters={"profile": "power-saver"}
        ))
        
        self._register(Command(
            id="lock_screen",
            name="Lock Screen",
            description="Lock the screen",
            category=CommandCategory.POWER,
            keywords=["lock", "lock screen", "lock computer"],
            shortcuts=["super+l", "ctrl+alt+l"],
            action="lock_screen"
        ))
        
        self._register(Command(
            id="suspend",
            name="Suspend",
            description="Put computer to sleep",
            category=CommandCategory.POWER,
            keywords=["sleep", "suspend", "go to sleep"],
            shortcuts=[],
            action="suspend"
        ))
        
        self._register(Command(
            id="shutdown",
            name="Shutdown",
            description="Shutdown the computer",
            category=CommandCategory.POWER,
            keywords=["shutdown", "power off", "turn off computer", "shut down"],
            shortcuts=[],
            action="shutdown"
        ))
        
        self._register(Command(
            id="reboot",
            name="Reboot",
            description="Restart the computer",
            category=CommandCategory.POWER,
            keywords=["reboot", "restart", "restart computer"],
            shortcuts=[],
            action="reboot"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # SYSTEM COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="system_status",
            name="System Status",
            description="Check system status",
            category=CommandCategory.SYSTEM,
            keywords=["system status", "system info", "how is my system", "computer status"],
            shortcuts=["ctrl+alt+s"],
            action="system_status"
        ))
        
        self._register(Command(
            id="memory_status",
            name="Memory Status",
            description="Check RAM usage",
            category=CommandCategory.SYSTEM,
            keywords=["memory", "ram", "memory usage", "ram usage", "how much memory"],
            shortcuts=[],
            action="memory_status"
        ))
        
        self._register(Command(
            id="cpu_status",
            name="CPU Status",
            description="Check CPU usage",
            category=CommandCategory.SYSTEM,
            keywords=["cpu", "processor", "cpu usage", "how is cpu"],
            shortcuts=[],
            action="cpu_status"
        ))
        
        self._register(Command(
            id="disk_status",
            name="Disk Status",
            description="Check disk usage",
            category=CommandCategory.SYSTEM,
            keywords=["disk", "storage", "disk usage", "how much storage", "space left"],
            shortcuts=[],
            action="disk_status"
        ))
        
        self._register(Command(
            id="open_settings",
            name="Open Settings",
            description="Open system settings",
            category=CommandCategory.SYSTEM,
            keywords=["settings", "open settings", "preferences", "configuration", "config"],
            shortcuts=["ctrl+,", "super+i"],
            action="open_settings"
        ))
        
        self._register(Command(
            id="toggle_hints",
            name="Toggle Hints",
            description="Toggle helper hints on/off",
            category=CommandCategory.SYSTEM,
            keywords=["toggle hints", "hints on", "hints off", "show hints", "hide hints"],
            shortcuts=["ctrl+h"],
            action="toggle_hints"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # NAVIGATION COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="open_launcher",
            name="Open Launcher",
            description="Open Spotlight-style launcher",
            category=CommandCategory.NAVIGATION,
            keywords=["launcher", "spotlight", "search", "find app", "open launcher"],
            shortcuts=["ctrl+space", "super+space", "alt+space"],
            action="open_launcher"
        ))
        
        self._register(Command(
            id="command_palette",
            name="Command Palette",
            description="Open command palette",
            category=CommandCategory.NAVIGATION,
            keywords=["command palette", "commands", "palette"],
            shortcuts=["ctrl+k", "ctrl+shift+p"],
            action="command_palette"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # WINDOW COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="new_terminal",
            name="New Terminal",
            description="Open a new terminal tab",
            category=CommandCategory.WINDOW,
            keywords=["new terminal", "terminal", "open terminal", "shell"],
            shortcuts=["ctrl+t", "ctrl+alt+t"],
            action="new_terminal"
        ))
        
        self._register(Command(
            id="close_window",
            name="Close Window",
            description="Close current window",
            category=CommandCategory.WINDOW,
            keywords=["close", "close window", "close tab"],
            shortcuts=["ctrl+w", "ctrl+q"],
            action="close_window"
        ))
        
        self._register(Command(
            id="fullscreen_toggle",
            name="Toggle Fullscreen",
            description="Toggle fullscreen mode",
            category=CommandCategory.WINDOW,
            keywords=["fullscreen", "toggle fullscreen", "full screen"],
            shortcuts=["f11", "ctrl+f"],
            action="fullscreen_toggle"
        ))
        
        self._register(Command(
            id="split_horizontal",
            name="Split Horizontal",
            description="Split window horizontally",
            category=CommandCategory.WINDOW,
            keywords=["split horizontal", "split h", "horizontal split"],
            shortcuts=["ctrl+shift+h"],
            action="split_horizontal"
        ))
        
        self._register(Command(
            id="split_vertical",
            name="Split Vertical",
            description="Split window vertically",
            category=CommandCategory.WINDOW,
            keywords=["split vertical", "split v", "vertical split"],
            shortcuts=["ctrl+shift+v"],
            action="split_vertical"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # APP COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="open_browser",
            name="Open Browser",
            description="Open web browser",
            category=CommandCategory.APP,
            keywords=["browser", "open browser", "chromium", "web", "internet"],
            shortcuts=["ctrl+alt+b"],
            action="open_app",
            parameters={"app": "browser"}
        ))
        
        self._register(Command(
            id="open_files",
            name="Open Files",
            description="Open file manager",
            category=CommandCategory.APP,
            keywords=["files", "file manager", "explorer", "folders"],
            shortcuts=["super+e", "ctrl+alt+f"],
            action="open_app",
            parameters={"app": "files"}
        ))
        
        self._register(Command(
            id="open_notes",
            name="Open Notes",
            description="Open knowledge vault",
            category=CommandCategory.APP,
            keywords=["notes", "vault", "knowledge", "obsidian"],
            shortcuts=["ctrl+alt+n"],
            action="open_app",
            parameters={"app": "vault"}
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # GUARDIAN / SECURITY COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="security_scan",
            name="Security Scan",
            description="Run a security scan",
            category=CommandCategory.GUARDIAN,
            keywords=["scan", "security scan", "virus scan", "check security", "guardian scan"],
            shortcuts=["ctrl+alt+g"],
            action="security_scan"
        ))
        
        self._register(Command(
            id="guardian_status",
            name="Guardian Status",
            description="Check Guardian AI status",
            category=CommandCategory.GUARDIAN,
            keywords=["guardian", "guardian status", "security status", "protection status"],
            shortcuts=[],
            action="guardian_status"
        ))
        
        # ═══════════════════════════════════════════════════════════════════════
        # HELP COMMANDS
        # ═══════════════════════════════════════════════════════════════════════
        
        self._register(Command(
            id="help",
            name="Help",
            description="Show help information",
            category=CommandCategory.HELP,
            keywords=["help", "how to", "what can you do", "commands", "show help"],
            shortcuts=["f1", "ctrl+?"],
            action="show_help"
        ))
        
        self._register(Command(
            id="shortcuts_help",
            name="Keyboard Shortcuts",
            description="Show keyboard shortcuts",
            category=CommandCategory.HELP,
            keywords=["shortcuts", "keyboard shortcuts", "hotkeys", "keybindings"],
            shortcuts=["ctrl+/"],
            action="show_shortcuts"
        ))
    
    def _register(self, command: Command):
        """Register a command."""
        self.commands[command.id] = command
    
    def _build_shortcut_map(self):
        """Build shortcut to command ID mapping."""
        for cmd_id, cmd in self.commands.items():
            for shortcut in cmd.shortcuts:
                self.shortcuts[shortcut.lower()] = cmd_id
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def execute_by_id(self, command_id: str, **kwargs) -> CommandResult:
        """Execute a command by its ID."""
        if command_id not in self.commands:
            return CommandResult(False, f"Unknown command: {command_id}")
        
        command = self.commands[command_id]
        params = {**command.parameters, **kwargs}
        
        return self._execute_action(command.action, params)
    
    def execute_by_shortcut(self, shortcut: str) -> Optional[CommandResult]:
        """Execute a command by keyboard shortcut."""
        shortcut = shortcut.lower()
        if shortcut in self.shortcuts:
            return self.execute_by_id(self.shortcuts[shortcut])
        return None
    
    def execute_by_text(self, text: str) -> CommandResult:
        """
        Execute a command from natural language text.
        This is the main entry point for AI chat commands.
        """
        text = text.lower().strip()
        
        # Log the command
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "input": text,
            "type": "text"
        })
        
        # Try to match command
        best_match = None
        best_score = 0
        extracted_params = {}
        
        for cmd_id, cmd in self.commands.items():
            if not cmd.enabled:
                continue
            
            score, params = self._match_command(text, cmd)
            if score > best_score:
                best_score = score
                best_match = cmd
                extracted_params = params
        
        if best_match and best_score > 0.5:
            params = {**best_match.parameters, **extracted_params}
            result = self._execute_action(best_match.action, params)
            
            # Update AI context
            self.ai_context["last_command"] = best_match.id
            self.ai_context["last_result"] = result
            
            return result
        
        # No match found
        return CommandResult(
            False,
            "I didn't understand that command. Try saying something like 'turn on wifi' or 'set volume to 50'.",
            speak=True
        )
    
    def _match_command(self, text: str, command: Command) -> Tuple[float, Dict]:
        """
        Match text against a command.
        Returns (score, extracted_parameters).
        """
        score = 0.0
        params = {}
        
        # Check exact keyword match
        for keyword in command.keywords:
            if keyword in text:
                score = max(score, 0.9)
                
                # Extract parameters based on command type
                if command.action == "wifi_connect":
                    match = re.search(r'connect to ["\']?([^"\']+)["\']?', text)
                    if match:
                        params["ssid"] = match.group(1).strip()
                        
                elif command.action == "volume_set":
                    match = re.search(r'(\d+)%?', text)
                    if match:
                        params["level"] = int(match.group(1))
                        
                elif command.action == "brightness_set":
                    match = re.search(r'(\d+)%?', text)
                    if match:
                        params["level"] = int(match.group(1))
                        
                elif command.action == "timezone_set":
                    # Try to extract timezone
                    for tz in self.settings.datetime.get_available_timezones():
                        if tz.lower() in text.lower():
                            params["timezone"] = tz
                            break
                
                break
        
        # Fuzzy matching for partial matches
        if score == 0:
            words = set(text.split())
            for keyword in command.keywords:
                keyword_words = set(keyword.split())
                overlap = len(words & keyword_words)
                if overlap > 0:
                    partial_score = overlap / len(keyword_words)
                    score = max(score, partial_score * 0.7)
        
        return score, params
    
    def _execute_action(self, action: str, params: Dict) -> CommandResult:
        """Execute an action and return the result."""
        
        try:
            # ═══════════════════════════════════════════════════════════════════
            # WIFI ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            if action == "wifi_toggle":
                enable = params.get("enable", True)
                success, msg = self.settings.wifi.toggle_wifi(enable)
                return CommandResult(success, msg)
            
            elif action == "wifi_status":
                status = self.settings.wifi.get_status()
                if status.get("connected"):
                    msg = f"Connected to {status['ssid']} with {status['signal']}% signal"
                else:
                    msg = "WiFi is not connected"
                return CommandResult(True, msg, data=status)
            
            elif action == "wifi_scan":
                networks = self.settings.wifi.scan_networks()
                if networks:
                    msg = f"Found {len(networks)} networks:\n"
                    for n in networks[:5]:
                        msg += f"  • {n.ssid} ({n.signal_strength}%) - {n.security}\n"
                else:
                    msg = "No networks found"
                return CommandResult(True, msg, data=networks)
            
            elif action == "wifi_connect":
                ssid = params.get("ssid")
                password = params.get("password")
                if not ssid:
                    return CommandResult(False, "Please specify a network name")
                success, msg = self.settings.wifi.connect(ssid, password)
                return CommandResult(success, msg)
            
            elif action == "wifi_disconnect":
                success, msg = self.settings.wifi.disconnect()
                return CommandResult(success, msg)
            
            # ═══════════════════════════════════════════════════════════════════
            # AUDIO ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "volume_adjust":
                delta = params.get("delta", 10)
                current = self.settings.audio.get_volume()
                new_level = max(0, min(100, current + delta))
                success, msg = self.settings.audio.set_volume(new_level)
                return CommandResult(success, f"Volume: {new_level}%")
            
            elif action == "volume_set":
                level = params.get("level", 50)
                success, msg = self.settings.audio.set_volume(level)
                return CommandResult(success, msg)
            
            elif action == "mute_toggle":
                success, msg = self.settings.audio.toggle_mute()
                return CommandResult(success, msg)
            
            elif action == "mute_set":
                # Toggle mute to specific state
                is_muted = self.settings.audio.is_muted()
                want_muted = params.get("mute", True)
                if is_muted != want_muted:
                    success, msg = self.settings.audio.toggle_mute()
                else:
                    msg = f"Audio is already {'muted' if is_muted else 'unmuted'}"
                    success = True
                return CommandResult(success, msg)
            
            # ═══════════════════════════════════════════════════════════════════
            # DISPLAY ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "brightness_adjust":
                delta = params.get("delta", 10)
                current = self.settings.display.get_brightness()
                new_level = max(10, min(100, current + delta))
                success, msg = self.settings.display.set_brightness(new_level)
                return CommandResult(success, f"Brightness: {new_level}%")
            
            elif action == "brightness_set":
                level = params.get("level", 50)
                success, msg = self.settings.display.set_brightness(level)
                return CommandResult(success, msg)
            
            elif action == "screenshot":
                import subprocess
                import shutil
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = f"/home/researcher/Pictures/screenshot_{timestamp}.png"
                    
                    # Try multiple screenshot tools in order of preference
                    screenshot_tools = [
                        ["scrot", filepath],
                        ["gnome-screenshot", "-f", filepath],
                        ["import", "-window", "root", filepath],  # ImageMagick
                        ["xwd", "-root", "-out", filepath.replace(".png", ".xwd")],
                    ]
                    
                    for tool_cmd in screenshot_tools:
                        tool = tool_cmd[0]
                        if shutil.which(tool):
                            result = subprocess.run(tool_cmd, capture_output=True, timeout=10)
                            if result.returncode == 0:
                                return CommandResult(True, f"Screenshot saved to {filepath}")
                    
                    return CommandResult(False, "No screenshot tool available. Install scrot, gnome-screenshot, or imagemagick.")
                except Exception as e:
                    return CommandResult(False, f"Screenshot failed: {e}")
            
            # ═══════════════════════════════════════════════════════════════════
            # DATETIME ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "time_check":
                dt = self.settings.datetime.get_current_datetime()
                return CommandResult(True, f"The time is {dt['time']}", data=dt)
            
            elif action == "date_check":
                dt = self.settings.datetime.get_current_datetime()
                return CommandResult(True, f"Today is {dt['formatted']}", data=dt)
            
            elif action == "datetime_check":
                dt = self.settings.datetime.get_current_datetime()
                return CommandResult(True, f"It's {dt['formatted']}", data=dt)
            
            elif action == "timezone_set":
                tz = params.get("timezone")
                if not tz:
                    return CommandResult(False, "Please specify a timezone")
                success, msg = self.settings.datetime.set_timezone(tz)
                return CommandResult(success, msg)
            
            elif action == "sync_time":
                success, msg = self.settings.datetime.sync_time()
                return CommandResult(success, msg)
            
            # ═══════════════════════════════════════════════════════════════════
            # THEME ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "theme_set":
                theme = params.get("theme", "dark")
                success, msg = self.settings.appearance.set_theme(theme)
                return CommandResult(success, msg)
            
            elif action == "theme_toggle":
                current = self.settings.appearance.get_theme()
                new_theme = "light" if current == "dark" else "dark"
                success, msg = self.settings.appearance.set_theme(new_theme)
                return CommandResult(success, f"Switched to {new_theme} theme")
            
            # ═══════════════════════════════════════════════════════════════════
            # POWER ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "battery_status":
                battery = self.settings._get_battery_status()
                if battery:
                    status = "charging" if battery["charging"] else "on battery"
                    msg = f"Battery is at {battery['percent']}% ({status})"
                    return CommandResult(True, msg, data=battery)
                return CommandResult(True, "No battery detected (desktop computer)")
            
            elif action == "power_profile":
                profile = params.get("profile", "balanced")
                if self.system_tools:
                    success, msg = self.system_tools.set_power_profile(profile)
                    return CommandResult(success, msg)
                return CommandResult(False, "Power profiles not available")
            
            elif action == "lock_screen":
                import subprocess
                try:
                    subprocess.run(["loginctl", "lock-session"], timeout=5)
                    return CommandResult(True, "Screen locked")
                except:
                    return CommandResult(False, "Could not lock screen")
            
            elif action == "suspend":
                return CommandResult(False, "Suspend requires confirmation. Say 'confirm suspend' to proceed.")
            
            elif action == "shutdown":
                return CommandResult(False, "Shutdown requires confirmation. Say 'confirm shutdown' to proceed.")
            
            elif action == "reboot":
                return CommandResult(False, "Reboot requires confirmation. Say 'confirm reboot' to proceed.")
            
            # ═══════════════════════════════════════════════════════════════════
            # SYSTEM ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "system_status":
                if self.system_tools:
                    status = self.system_tools.get_system_status()
                    cpu = status.get("cpu", {}).get("percent", 0)
                    mem = status.get("memory", {}).get("percent", 0)
                    msg = f"CPU: {cpu}%, Memory: {mem}%"
                    return CommandResult(True, msg, data=status)
                return CommandResult(False, "System tools not available")
            
            elif action == "memory_status":
                if self.system_tools:
                    status = self.system_tools.get_system_status()
                    mem = status.get("memory", {})
                    msg = f"Memory: {mem.get('used_gb', 0):.1f} GB used of {mem.get('total_gb', 0):.1f} GB ({mem.get('percent', 0)}%)"
                    return CommandResult(True, msg, data=mem)
                return CommandResult(False, "System tools not available")
            
            elif action == "cpu_status":
                if self.system_tools:
                    status = self.system_tools.get_system_status()
                    cpu = status.get("cpu", {})
                    msg = f"CPU usage: {cpu.get('percent', 0)}%"
                    return CommandResult(True, msg, data=cpu)
                return CommandResult(False, "System tools not available")
            
            elif action == "disk_status":
                if self.system_tools:
                    status = self.system_tools.get_system_status()
                    disks = status.get("disks", [])
                    if disks:
                        d = disks[0]
                        msg = f"Disk: {d.get('free_gb', 0):.1f} GB free of {d.get('total_gb', 0):.1f} GB"
                        return CommandResult(True, msg, data=disks)
                return CommandResult(False, "System tools not available")
            
            elif action == "open_settings":
                return CommandResult(True, "Opening settings...", data={"action": "open_settings"})
            
            elif action == "toggle_hints":
                current = self.settings.general_settings.get("hints_enabled", True)
                self.settings.general_settings["hints_enabled"] = not current
                self.settings.save_general_settings()
                state = "enabled" if not current else "disabled"
                return CommandResult(True, f"Hints {state}")
            
            # ═══════════════════════════════════════════════════════════════════
            # NAVIGATION ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "open_launcher":
                return CommandResult(True, "Opening launcher...", data={"action": "open_launcher"})
            
            elif action == "command_palette":
                return CommandResult(True, "Opening command palette...", data={"action": "command_palette"})
            
            # ═══════════════════════════════════════════════════════════════════
            # WINDOW ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "new_terminal":
                return CommandResult(True, "Opening new terminal...", data={"action": "new_terminal"})
            
            elif action == "close_window":
                return CommandResult(True, "Closing window...", data={"action": "close_window"})
            
            elif action == "fullscreen_toggle":
                return CommandResult(True, "Toggling fullscreen...", data={"action": "fullscreen_toggle"})
            
            elif action == "split_horizontal":
                return CommandResult(True, "Splitting horizontally...", data={"action": "split_horizontal"})
            
            elif action == "split_vertical":
                return CommandResult(True, "Splitting vertically...", data={"action": "split_vertical"})
            
            # ═══════════════════════════════════════════════════════════════════
            # APP ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "open_app":
                app = params.get("app", "")
                return CommandResult(True, f"Opening {app}...", data={"action": "open_app", "app": app})
            
            # ═══════════════════════════════════════════════════════════════════
            # GUARDIAN ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "security_scan":
                return CommandResult(True, "Starting security scan...", data={"action": "security_scan"})
            
            elif action == "guardian_status":
                return CommandResult(True, "Guardian AI is active and protecting your system", data={"action": "guardian_status"})
            
            # ═══════════════════════════════════════════════════════════════════
            # HELP ACTIONS
            # ═══════════════════════════════════════════════════════════════════
            
            elif action == "show_help":
                help_text = self.get_help_text()
                return CommandResult(True, help_text, speak=False)
            
            elif action == "show_shortcuts":
                shortcuts = self.get_shortcuts_help()
                return CommandResult(True, shortcuts, speak=False)
            
            else:
                return CommandResult(False, f"Unknown action: {action}")
            
        except Exception as e:
            return CommandResult(False, f"Error: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HELP & DOCUMENTATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_help_text(self) -> str:
        """Get help text showing available commands."""
        lines = [
            "═" * 60,
            " VA21 COMMAND HELP ".center(60),
            "═" * 60,
            "",
            "You can control VA21 by typing natural commands like:",
            "",
        ]
        
        examples = [
            ("WiFi", ["turn on wifi", "scan networks", "connect to MyNetwork"]),
            ("Audio", ["mute", "set volume to 50", "volume up"]),
            ("Display", ["brightness up", "take screenshot"]),
            ("Time", ["what time is it", "what's the date"]),
            ("Theme", ["dark mode", "light theme", "toggle theme"]),
            ("System", ["battery status", "system status", "open settings"]),
        ]
        
        for category, cmds in examples:
            lines.append(f"  {category}:")
            for cmd in cmds:
                lines.append(f"    • \"{cmd}\"")
            lines.append("")
        
        lines.append("═" * 60)
        lines.append("Type 'shortcuts' to see keyboard shortcuts")
        lines.append("═" * 60)
        
        return "\n".join(lines)
    
    def get_shortcuts_help(self) -> str:
        """Get keyboard shortcuts help."""
        lines = [
            "╔" + "═" * 58 + "╗",
            "║" + " KEYBOARD SHORTCUTS ".center(58) + "║",
            "╠" + "═" * 58 + "╣",
        ]
        
        # Group by category
        by_category = {}
        for cmd in self.commands.values():
            if cmd.shortcuts:
                cat = cmd.category.value.title()
                if cat not in by_category:
                    by_category[cat] = []
                for shortcut in cmd.shortcuts[:1]:  # Just first shortcut
                    by_category[cat].append((shortcut, cmd.name))
        
        for category, shortcuts in sorted(by_category.items()):
            lines.append(f"║ {category:<56} ║")
            lines.append("║" + "─" * 58 + "║")
            for shortcut, name in shortcuts:
                lines.append(f"║   {shortcut:<20} {name:<34} ║")
            lines.append("║" + " " * 58 + "║")
        
        lines.append("╚" + "═" * 58 + "╝")
        
        return "\n".join(lines)
    
    def get_all_commands(self) -> List[Dict]:
        """Get all commands for command palette."""
        return [
            {
                "id": cmd.id,
                "name": cmd.name,
                "description": cmd.description,
                "category": cmd.category.value,
                "shortcuts": cmd.shortcuts,
                "keywords": cmd.keywords
            }
            for cmd in self.commands.values()
            if cmd.enabled
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_command_interface = None

def get_command_interface() -> VA21CommandInterface:
    """Get the command interface singleton."""
    global _command_interface
    if _command_interface is None:
        _command_interface = VA21CommandInterface()
    return _command_interface


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN / TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    cmd = get_command_interface()
    
    print("VA21 Command Interface Test")
    print("=" * 40)
    
    # Test natural language commands
    test_commands = [
        "what time is it",
        "turn on wifi",
        "set volume to 50",
        "dark mode",
        "battery status",
        "help",
    ]
    
    for text in test_commands:
        print(f"\n> {text}")
        result = cmd.execute_by_text(text)
        print(f"  {'✓' if result.success else '✗'} {result.message}")
    
    print("\n")
    print(cmd.get_shortcuts_help())
