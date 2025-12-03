#!/usr/bin/env python3
"""
VA21 Research OS - Zork-Style Text Adventure Interface
=======================================================

A text-based adventure game interface for interacting with the VA21 Research OS.
Custom created by VA21 team, inspired by classic text adventures like Zork.
This interface transforms system administration into an immersive exploration experience.

Om Vinayaka - May obstacles be removed from your research journey.

Accessibility Features:
- Hold Super Key for push-to-talk voice input (for users who cannot type)
- Voice commands work in 1,600+ languages via Meta Omnilingual ASR
"""

import os
import sys
import json
import time
import shutil
import subprocess
import readline
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Voice input availability
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

VOICE_AVAILABLE = False
try:
    # Check for speech recognition
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# VOICE INPUT SYSTEM (Accessibility)
# ═══════════════════════════════════════════════════════════════════════════════

class VoiceInputSystem:
    """
    Push-to-talk voice input for accessibility.
    Hold Super key to activate, speak, release to send command.
    Supports 1,600+ languages via Meta Omnilingual ASR.
    """
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_listening = False
        self.super_pressed = False
        self.recognizer = None
        self.microphone = None
        self.listener_thread = None
        
        if VOICE_AVAILABLE:
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
            except:
                self.microphone = None
    
    def start_keyboard_listener(self):
        """Start listening for Super key press."""
        if not PYNPUT_AVAILABLE:
            return
        
        def on_press(key):
            try:
                if key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                    if not self.super_pressed:
                        self.super_pressed = True
                        self._start_voice_capture()
            except:
                pass
        
        def on_release(key):
            try:
                if key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                    if self.super_pressed:
                        self.super_pressed = False
                        self._stop_voice_capture()
            except:
                pass
        
        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()
    
    def _start_voice_capture(self):
        """Start capturing voice when Super key is pressed."""
        if not VOICE_AVAILABLE or not self.microphone:
            return
        
        self.is_listening = True
        print("\n🎤 Voice input active - speak now...")
        
        def capture_audio():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = self.recognizer.listen(source, timeout=10)
                    
                if self.is_listening and self.callback:
                    try:
                        # Try to use speech recognition
                        text = self.recognizer.recognize_google(audio)
                        print(f"\n🎤 Heard: {text}")
                        self.callback(text)
                    except sr.UnknownValueError:
                        print("\n🎤 Could not understand audio")
                    except sr.RequestError:
                        print("\n🎤 Speech recognition unavailable")
            except Exception as e:
                pass
        
        self.listener_thread = threading.Thread(target=capture_audio, daemon=True)
        self.listener_thread.start()
    
    def _stop_voice_capture(self):
        """Stop capturing voice when Super key is released."""
        self.is_listening = False
        print("🎤 Voice input stopped")
    
    def stop(self):
        """Stop the voice input system."""
        self.is_listening = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# GAME DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Item:
    """Represents an item in the game world."""
    id: str
    name: str
    description: str
    portable: bool = True
    usable: bool = True
    use_action: Optional[str] = None  # System command to run
    examine_text: str = ""


@dataclass
class Room:
    """Represents a location in the game world."""
    id: str
    name: str
    description: str
    long_description: str
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> room_id
    items: List[str] = field(default_factory=list)  # item_ids present
    first_visit: bool = True
    system_context: str = ""  # What system area this represents
    on_enter: Optional[str] = None  # Action when entering


@dataclass 
class GameState:
    """The player's current game state."""
    current_room: str = "boot_chamber"
    inventory: List[str] = field(default_factory=list)
    visited_rooms: List[str] = field(default_factory=list)
    flags: Dict[str, bool] = field(default_factory=dict)
    score: int = 0
    moves: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    hints_enabled: bool = True  # Toggle for helper hints


# ═══════════════════════════════════════════════════════════════════════════════
# HINTS SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class HintsSystem:
    """
    Toggleable hints system to help newcomers navigate the Zork interface.
    Experts can disable hints for a cleaner experience.
    """
    
    # Context-aware hints
    HINTS = {
        "boot_chamber": [
            "💡 Hint: Type 'look' (or 'l') to examine your surroundings in detail.",
            "💡 Hint: Use 'go north' (or just 'n') to move to the Research Lab.",
            "💡 Hint: Try 'examine research_manual' to learn about available commands.",
        ],
        "research_lab": [
            "💡 Hint: The Research Lab is your main workspace. Type 'look' to see what's here.",
            "💡 Hint: Use 'take <item>' to pick up tools you find.",
            "💡 Hint: Try 'search <query>' to research topics on the internet.",
        ],
        "terminal_nexus": [
            "💡 Hint: This is where you can run shell commands directly.",
            "💡 Hint: Type 'shell ls -la' to list files, or 'bash' for full shell access.",
            "💡 Hint: The Guardian protects you from dangerous commands.",
        ],
        "knowledge_vault": [
            "💡 Hint: The Vault stores your notes and research findings.",
            "💡 Hint: Use 'search <topic>' to find information.",
        ],
        "guardian_sanctum": [
            "💡 Hint: Here you can interact directly with the Guardian AI.",
            "💡 Hint: Try 'ask guardian security' to check system security.",
            "💡 Hint: Use 'scan <path>' to scan files for threats with ClamAV.",
        ],
        "general": [
            "💡 Hint: Type 'help' to see all available commands.",
            "💡 Hint: Use 'inventory' (or 'i') to see what you're carrying.",
            "💡 Hint: Type 'hints off' to disable these hints.",
        ]
    }
    
    @staticmethod
    def get_hint(room_id: str, move_count: int) -> Optional[str]:
        """Get a contextual hint based on room and progress."""
        import random
        
        # Get room-specific hints
        room_hints = HintsSystem.HINTS.get(room_id, [])
        general_hints = HintsSystem.HINTS.get("general", [])
        
        # Combine hints, prioritizing room-specific ones
        all_hints = room_hints + general_hints
        
        if not all_hints:
            return None
        
        # Return a hint based on move count for variety
        hint_index = move_count % len(all_hints)
        return all_hints[hint_index]
    
    @staticmethod
    def get_command_hint(command: str) -> Optional[str]:
        """Get a hint for an unknown or partial command."""
        suggestions = {
            "go": "💡 Usage: go <direction> (north, south, east, west, up, down)",
            "take": "💡 Usage: take <item> - Pick up an item from the room",
            "examine": "💡 Usage: examine <item> - Look at something closely",
            "use": "💡 Usage: use <item> - Use an item in your inventory",
            "ask": "💡 Usage: ask guardian <topic> - Ask the Guardian AI about something",
            "search": "💡 Usage: search <query> - Search the internet for information",
            "scan": "💡 Usage: scan <path> - Scan a file or directory for threats",
            "shell": "💡 Usage: shell <command> - Execute a shell command",
        }
        
        # Find closest match
        for key, hint in suggestions.items():
            if key in command.lower():
                return hint
        
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# VA21 ZORK INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class VA21ZorkInterface:
    """
    The main Zork-style text adventure interface for VA21 Research OS.
    
    This transforms the traditional command-line OS experience into an
    immersive text adventure where:
    - Rooms represent different system contexts (files, network, processes)
    - Items represent tools and resources
    - The Guardian AI is an NPC you can interact with
    - Commands are adventure-style (look, go, take, use, etc.)
    
    Integrations:
    - ClamAV for antivirus protection
    - SearXNG for privacy-respecting internet search
    - Guardian AI for intelligent security
    - Obsidian vault for knowledge management
    - Writing suite for researchers and journalists
    
    Accessibility:
    - Hold Super key for push-to-talk voice input
    - Voice commands in 1,600+ languages
    """
    
    VERSION = "1.3.0"
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.state = GameState()
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        self.running = True
        self.guardian_responses = []
        self.hints_system = HintsSystem()
        self.voice_command_pending = None
        
        # Initialize Voice Input System (Accessibility)
        self.voice_input = None
        if VOICE_AVAILABLE or PYNPUT_AVAILABLE:
            self.voice_input = VoiceInputSystem(callback=self._handle_voice_command)
        
        # Initialize ClamAV integration
        self.clamav = None
        try:
            from guardian.clamav_integration import get_clamav
            self.clamav = get_clamav()
        except ImportError:
            try:
                import sys
                sys.path.insert(0, '/va21/guardian')
                from clamav_integration import get_clamav
                self.clamav = get_clamav()
            except ImportError:
                pass
        
        # Initialize SearXNG integration
        self.searxng = None
        try:
            from searxng.searxng_client import get_searxng
            self.searxng = get_searxng()
        except ImportError:
            try:
                import sys
                sys.path.insert(0, '/va21/searxng')
                from searxng_client import get_searxng
                self.searxng = get_searxng()
            except ImportError:
                pass
        
        # Initialize Obsidian vault integration
        self.vault = None
        try:
            from obsidian.vault_manager import get_vault
            self.vault = get_vault()
        except ImportError:
            try:
                import sys
                sys.path.insert(0, '/va21/obsidian')
                from vault_manager import get_vault
                self.vault = get_vault()
            except ImportError:
                pass
        
        # Initialize Writing suite
        self.writing = None
        try:
            from writing.writing_suite import get_writing_suite
            self.writing = get_writing_suite()
        except ImportError:
            try:
                import sys
                sys.path.insert(0, '/va21/writing')
                from writing_suite import get_writing_suite
                self.writing = get_writing_suite()
            except ImportError:
                pass
        
        # Command aliases
        self.aliases = {
            'n': 'go north', 'north': 'go north',
            's': 'go south', 'south': 'go south',
            'e': 'go east', 'east': 'go east',
            'w': 'go west', 'west': 'go west',
            'u': 'go up', 'up': 'go up',
            'd': 'go down', 'down': 'go down',
            'l': 'look', 'ls': 'look',
            'i': 'inventory', 'inv': 'inventory',
            'x': 'examine', 'ex': 'examine',
            'q': 'quit', 'exit': 'quit',
            'h': 'help', '?': 'help',
            'cls': 'clear', 'clear': 'clear',
        }
        
        # Initialize game world
        self._init_rooms()
        self._init_items()
        
    def _init_rooms(self):
        """Initialize all rooms in the game world."""
        
        self.rooms = {
            "boot_chamber": Room(
                id="boot_chamber",
                name="The Boot Chamber",
                description="A warm glow emanates from the ancient GUARDIAN CORE.",
                long_description="""You stand in the BOOT CHAMBER, the heart of VA21 Research OS.
The walls pulse with soft blue light, ancient runes of code scrolling across them.
In the center, the GUARDIAN CORE hovers - a crystalline structure that houses
the protective AI spirit of this realm.

The air hums with potential energy, ready to assist your research journey.""",
                exits={
                    "north": "research_lab",
                    "east": "knowledge_vault", 
                    "west": "terminal_nexus",
                    "down": "kernel_depths",
                    "up": "network_tower"
                },
                items=["research_manual", "guardian_amulet"],
                system_context="System root - initialization area"
            ),
            
            "research_lab": Room(
                id="research_lab",
                name="The Research Laboratory",
                description="Workbenches covered with analysis tools line the walls.",
                long_description="""The RESEARCH LABORATORY stretches before you, a vast space
dedicated to discovery and analysis. Crystalline workbenches hold various
research tools - each glowing with readiness.

A large KNOWLEDGE GRAPH pulses on the far wall, nodes of information
connected by threads of understanding. The Guardian's presence is felt
here, watching over your work.""",
                exits={
                    "south": "boot_chamber",
                    "east": "sandbox_arena",
                    "west": "process_halls"
                },
                items=["analysis_lens", "code_scanner"],
                system_context="Main research environment - /home/researcher/research"
            ),
            
            "knowledge_vault": Room(
                id="knowledge_vault",
                name="The Knowledge Vault",
                description="Towering shelves of crystallized knowledge surround you.",
                long_description="""You enter the KNOWLEDGE VAULT, an infinite library of
crystallized wisdom. Shelves stretch to unseen heights, each holding
glowing orbs of stored information.

The air is thick with the whisper of countless documents, notes, and
research findings. A reading pedestal stands in the center, ready to
display any knowledge you seek.""",
                exits={
                    "west": "boot_chamber",
                    "north": "archive_depths"
                },
                items=["note_crystal", "search_compass"],
                system_context="Document storage - /va21/vault and /home/researcher/notes"
            ),
            
            "terminal_nexus": Room(
                id="terminal_nexus",
                name="The Terminal Nexus",
                description="Floating terminals orbit a central command sphere.",
                long_description="""The TERMINAL NEXUS hums with raw computational power.
Floating terminals orbit around you, each offering direct access to
the system's command core. Green text cascades down their surfaces.

This is where true power resides - direct shell access to the realm.
The Guardian watches especially carefully here, for great power
requires great responsibility.""",
                exits={
                    "east": "boot_chamber",
                    "north": "process_halls"
                },
                items=["command_wand", "shell_key"],
                system_context="Direct shell access - bash terminal"
            ),
            
            "kernel_depths": Room(
                id="kernel_depths",
                name="The Kernel Depths",
                description="Ancient code flows like magma through crystalline channels.",
                long_description="""You descend into the KERNEL DEPTHS, the foundational realm
of the OS. Here, ancient code flows through crystalline channels like
rivers of light. The very fabric of reality is maintained here.

Few venture this deep. The Guardian's presence is strongest here,
protecting the sacred core from any who would cause harm. System
calls echo in the darkness like distant thunder.""",
                exits={
                    "up": "boot_chamber"
                },
                items=["syscall_tome", "kernel_shard"],
                system_context="Low-level system access - kernel and system internals"
            ),
            
            "network_tower": Room(
                id="network_tower",
                name="The Network Tower",
                description="Streams of data flow through the air like aurora.",
                long_description="""You ascend to the NETWORK TOWER, where streams of data
flow through the air like ribbons of light. From here, you can see
connections reaching out to distant realms - other systems, services,
and the vast wilderness of the internet beyond.

The Guardian maintains careful watch here, filtering what may enter
and what may leave. Network packets dance like fireflies.""",
                exits={
                    "down": "boot_chamber",
                    "north": "firewall_gate"
                },
                items=["packet_glass", "connection_map"],
                system_context="Network monitoring - connections and traffic"
            ),
            
            "sandbox_arena": Room(
                id="sandbox_arena",
                name="The Sandbox Arena",
                description="An isolated chamber where experiments can run safely.",
                long_description="""The SANDBOX ARENA is a contained space, isolated from the
rest of the realm. Here, you can run dangerous experiments without
fear of harming the greater system.

Magical barriers shimmer at the edges, preventing anything harmful
from escaping. The Guardian has prepared this space for your most
risky research endeavors.""",
                exits={
                    "west": "research_lab"
                },
                items=["isolation_sphere", "test_scroll"],
                system_context="Isolated execution environment - /home/researcher/sandbox"
            ),
            
            "process_halls": Room(
                id="process_halls",
                name="The Process Halls",
                description="Spectral workers busily perform their endless tasks.",
                long_description="""The PROCESS HALLS bustle with activity. Spectral workers -
each representing a running process - move about performing their
designated tasks. Some are ancient and steady, others fleeting.

From here you can observe all work being done in the realm, and
if necessary, command processes to halt or modify their behavior.""",
                exits={
                    "south": "terminal_nexus",
                    "east": "research_lab"
                },
                items=["process_lens", "task_whistle"],
                system_context="Process management - ps, top, htop"
            ),
            
            "guardian_sanctum": Room(
                id="guardian_sanctum",
                name="The Guardian's Sanctum",
                description="The heart of the Guardian AI's consciousness.",
                long_description="""You enter the GUARDIAN'S SANCTUM, a sacred space where the
protective AI's consciousness resides. The room glows with amber light,
and you feel the Guardian's attention focus entirely upon you.

Here you can communicate directly with the Guardian, adjust security
policies, and review the realm's protection status. Speak freely,
for the Guardian is your ally in all research endeavors.""",
                exits={
                    "out": "boot_chamber"
                },
                items=["security_orb", "policy_scroll"],
                system_context="Security controls - Guardian AI interface"
            ),
            
            "archive_depths": Room(
                id="archive_depths",
                name="The Archive Depths",
                description="Ancient backup crystals line the walls in rows.",
                long_description="""Deep within the ARCHIVE DEPTHS, ancient backup crystals
hold snapshots of the realm's past states. Each crystal glows with
preserved data, ready to restore what was lost.

Time moves strangely here. You can peer into the past, examining
how the realm once was, or restore from these preserved moments.""",
                exits={
                    "south": "knowledge_vault"
                },
                items=["backup_crystal", "restore_wand"],
                system_context="Backup and restore - system snapshots"
            ),
            
            "firewall_gate": Room(
                id="firewall_gate",
                name="The Firewall Gate",
                description="Massive gates of light filter all who would enter.",
                long_description="""The FIREWALL GATE stands as the realm's primary defense
against external threats. Massive gates of pure light examine
every packet of data that attempts to enter or leave.

The Guardian's rules are enforced here. You can examine what is
blocked, what is allowed, and adjust the protective policies.""",
                exits={
                    "south": "network_tower"
                },
                items=["rule_tablet", "filter_key"],
                system_context="Firewall controls - iptables, traffic filtering"
            )
        }
    
    def _init_items(self):
        """Initialize all items in the game world."""
        
        self.items = {
            # Boot Chamber items
            "research_manual": Item(
                id="research_manual",
                name="Research Manual",
                description="A glowing tome containing knowledge of the realm.",
                examine_text="The manual describes how to navigate VA21 Research OS. Type 'help' to learn commands.",
                use_action="help"
            ),
            "guardian_amulet": Item(
                id="guardian_amulet", 
                name="Guardian Amulet",
                description="A crystalline amulet that connects you to the Guardian.",
                examine_text="The amulet pulses warmly. Through it, you can commune with the Guardian AI.",
                use_action="ask guardian status"
            ),
            
            # Research Lab items
            "analysis_lens": Item(
                id="analysis_lens",
                name="Analysis Lens",
                description="A magical lens for examining files and data.",
                examine_text="Looking through this lens reveals the true nature of any file or data.",
                use_action="file"
            ),
            "code_scanner": Item(
                id="code_scanner",
                name="Code Scanner",
                description="Scans code for security vulnerabilities.",
                examine_text="This device can analyze code for potential security issues.",
                use_action="scan"
            ),
            
            # Knowledge Vault items
            "note_crystal": Item(
                id="note_crystal",
                name="Note Crystal",
                description="A crystal for creating and storing notes.",
                examine_text="Touch the crystal to create or retrieve notes.",
                use_action="notes"
            ),
            "search_compass": Item(
                id="search_compass",
                name="Search Compass",
                description="Points toward knowledge you seek.",
                examine_text="The compass needle spins, ready to find what you seek.",
                use_action="search"
            ),
            
            # Terminal Nexus items
            "command_wand": Item(
                id="command_wand",
                name="Command Wand",
                description="Channels raw command power.",
                examine_text="Wave this wand while speaking a command to execute it directly.",
                use_action="shell"
            ),
            "shell_key": Item(
                id="shell_key",
                name="Shell Key",
                description="Unlocks direct shell access.",
                examine_text="This key grants access to the raw terminal. Use with caution.",
                use_action="bash"
            ),
            
            # Kernel Depths items
            "syscall_tome": Item(
                id="syscall_tome",
                name="Syscall Tome",
                description="Contains knowledge of system calls.",
                examine_text="Ancient knowledge of how programs communicate with the kernel.",
                portable=False
            ),
            "kernel_shard": Item(
                id="kernel_shard",
                name="Kernel Shard",
                description="A fragment of the kernel's power.",
                examine_text="This shard contains essence of the Linux kernel itself.",
                portable=False
            ),
            
            # Network Tower items
            "packet_glass": Item(
                id="packet_glass",
                name="Packet Glass",
                description="Reveals network traffic.",
                examine_text="Peer through to see data packets flowing through the network.",
                use_action="netstat"
            ),
            "connection_map": Item(
                id="connection_map",
                name="Connection Map",
                description="Shows all network connections.",
                examine_text="A living map of all network connections in the realm.",
                use_action="connections"
            ),
            
            # Sandbox Arena items
            "isolation_sphere": Item(
                id="isolation_sphere",
                name="Isolation Sphere",
                description="Creates a protected sandbox.",
                examine_text="Activate to create an isolated environment for testing.",
                use_action="sandbox"
            ),
            "test_scroll": Item(
                id="test_scroll",
                name="Test Scroll",
                description="Contains experimental scripts.",
                examine_text="Safely run experiments using this scroll.",
                use_action="test"
            ),
            
            # Process Halls items
            "process_lens": Item(
                id="process_lens",
                name="Process Lens",
                description="Reveals all running processes.",
                examine_text="Look through to see all active processes in the realm.",
                use_action="processes"
            ),
            "task_whistle": Item(
                id="task_whistle",
                name="Task Whistle",
                description="Commands processes to act.",
                examine_text="Blow to send signals to processes.",
                use_action="kill"
            ),
            
            # Guardian Sanctum items
            "security_orb": Item(
                id="security_orb",
                name="Security Orb",
                description="Shows the realm's security status.",
                examine_text="The orb glows with current security information.",
                use_action="security"
            ),
            "policy_scroll": Item(
                id="policy_scroll",
                name="Policy Scroll",
                description="Contains security policies.",
                examine_text="The policies that govern the Guardian's protection.",
                portable=False
            ),
            
            # Archive Depths items
            "backup_crystal": Item(
                id="backup_crystal",
                name="Backup Crystal",
                description="Holds a snapshot of the realm.",
                examine_text="This crystal can preserve the current state of the realm.",
                use_action="backup"
            ),
            "restore_wand": Item(
                id="restore_wand",
                name="Restore Wand",
                description="Restores from backup crystals.",
                examine_text="Wave over a backup crystal to restore from it.",
                use_action="restore"
            ),
            
            # Firewall Gate items
            "rule_tablet": Item(
                id="rule_tablet",
                name="Rule Tablet",
                description="Contains firewall rules.",
                examine_text="The rules that govern what may pass through the gate.",
                use_action="firewall"
            ),
            "filter_key": Item(
                id="filter_key",
                name="Filter Key",
                description="Adjusts firewall filters.",
                examine_text="Use to modify what traffic is allowed.",
                portable=False
            )
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OUTPUT METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def print(self, text: str, style: str = None):
        """Print text, optionally with rich formatting."""
        if RICH_AVAILABLE and self.console and style:
            self.console.print(text, style=style)
        else:
            print(text)
    
    def print_room(self, room: Room, verbose: bool = False):
        """Print room description."""
        print()
        self.print(f"═══ {room.name.upper()} ═══", "bold cyan")
        
        if verbose or room.first_visit:
            self.print(room.long_description, "white")
            room.first_visit = False
        else:
            self.print(room.description, "white")
        
        # Show exits
        if room.exits:
            exits_str = ", ".join([f"{d.upper()} ({self.rooms[r].name})" 
                                   for d, r in room.exits.items()])
            self.print(f"\nExits: {exits_str}", "green")
        
        # Show items
        room_items = [self.items[i] for i in room.items if i in self.items]
        if room_items:
            items_str = ", ".join([i.name for i in room_items])
            self.print(f"\nYou see: {items_str}", "yellow")
        
        # Show system context
        if room.system_context:
            self.print(f"\n[System: {room.system_context}]", "dim")
        
        print()
    
    def print_guardian(self, message: str):
        """Print a message from the Guardian AI."""
        print()
        self.print("The Guardian speaks:", "bold magenta")
        self.print(f'"{message}"', "magenta italic")
        print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def cmd_look(self, args: List[str]) -> str:
        """Look around or examine something."""
        room = self.rooms[self.state.current_room]
        self.print_room(room, verbose=True)
        return ""
    
    def cmd_go(self, args: List[str]) -> str:
        """Move to a different room."""
        if not args:
            return "Go where? Specify a direction (north, south, east, west, up, down)."
        
        direction = args[0].lower()
        room = self.rooms[self.state.current_room]
        
        if direction not in room.exits:
            return f"You cannot go {direction} from here."
        
        # Move to new room
        new_room_id = room.exits[direction]
        self.state.current_room = new_room_id
        new_room = self.rooms[new_room_id]
        
        if new_room_id not in self.state.visited_rooms:
            self.state.visited_rooms.append(new_room_id)
            self.state.score += 5
        
        self.print_room(new_room)
        return ""
    
    def cmd_examine(self, args: List[str]) -> str:
        """Examine an item in detail."""
        if not args:
            return "Examine what?"
        
        item_name = " ".join(args).lower()
        room = self.rooms[self.state.current_room]
        
        # Check inventory and room
        all_items = self.state.inventory + room.items
        
        for item_id in all_items:
            if item_id in self.items:
                item = self.items[item_id]
                if item_name in item.name.lower() or item_name in item_id:
                    self.print(f"\n{item.name}", "bold yellow")
                    self.print(item.description, "white")
                    if item.examine_text:
                        self.print(f"\n{item.examine_text}", "italic")
                    return ""
        
        return f"You don't see any '{item_name}' here."
    
    def cmd_take(self, args: List[str]) -> str:
        """Pick up an item."""
        if not args:
            return "Take what?"
        
        item_name = " ".join(args).lower()
        room = self.rooms[self.state.current_room]
        
        for item_id in room.items[:]:  # Copy to allow modification
            if item_id in self.items:
                item = self.items[item_id]
                if item_name in item.name.lower() or item_name in item_id:
                    if not item.portable:
                        return f"The {item.name} cannot be taken."
                    room.items.remove(item_id)
                    self.state.inventory.append(item_id)
                    self.state.score += 2
                    return f"You take the {item.name}."
        
        return f"You don't see any '{item_name}' here."
    
    def cmd_drop(self, args: List[str]) -> str:
        """Drop an item."""
        if not args:
            return "Drop what?"
        
        item_name = " ".join(args).lower()
        room = self.rooms[self.state.current_room]
        
        for item_id in self.state.inventory[:]:
            if item_id in self.items:
                item = self.items[item_id]
                if item_name in item.name.lower() or item_name in item_id:
                    self.state.inventory.remove(item_id)
                    room.items.append(item_id)
                    return f"You drop the {item.name}."
        
        return f"You're not carrying any '{item_name}'."
    
    def cmd_inventory(self, args: List[str]) -> str:
        """Show inventory."""
        if not self.state.inventory:
            return "You are empty-handed."
        
        self.print("\nYou are carrying:", "bold")
        for item_id in self.state.inventory:
            if item_id in self.items:
                item = self.items[item_id]
                self.print(f"  • {item.name}: {item.description}", "yellow")
        return ""
    
    def cmd_use(self, args: List[str]) -> str:
        """Use an item."""
        if not args:
            return "Use what?"
        
        item_name = " ".join(args).lower()
        room = self.rooms[self.state.current_room]
        all_items = self.state.inventory + room.items
        
        for item_id in all_items:
            if item_id in self.items:
                item = self.items[item_id]
                if item_name in item.name.lower() or item_name in item_id:
                    if not item.usable:
                        return f"You cannot use the {item.name}."
                    if item.use_action:
                        return self.execute_command(item.use_action)
                    return f"You use the {item.name}, but nothing happens."
        
        return f"You don't have any '{item_name}'."
    
    def cmd_ask(self, args: List[str]) -> str:
        """Ask the Guardian AI something."""
        if not args:
            return "Ask who about what? Try: ask guardian <topic>"
        
        if args[0].lower() != "guardian":
            return "You can only ask the Guardian."
        
        if len(args) < 2:
            return "What would you like to ask the Guardian about?"
        
        topic = " ".join(args[1:]).lower()
        return self._guardian_response(topic)
    
    def _guardian_response(self, topic: str) -> str:
        """Generate a Guardian AI response."""
        responses = {
            "status": self._get_system_status(),
            "security": self._get_security_status(),
            "help": "I am the Guardian, protector of this realm. I monitor all activity and protect against threats. Ask me about 'status', 'security', 'processes', or 'network'.",
            "processes": self._get_process_info(),
            "network": self._get_network_info(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "time": f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. You have been exploring for {self.state.moves} moves.",
        }
        
        for key, response in responses.items():
            if key in topic:
                self.print_guardian(response)
                return ""
        
        self.print_guardian(f"I don't have specific information about '{topic}'. Try asking about status, security, processes, network, memory, disk, or time.")
        return ""
    
    def _get_system_status(self) -> str:
        """Get system status for Guardian."""
        if PSUTIL_AVAILABLE:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            return f"System status: CPU at {cpu:.1f}%, Memory at {mem.percent:.1f}% used. All systems nominal. The realm is secure."
        return "System monitoring is limited in this environment, but the realm appears stable."
    
    def _get_security_status(self) -> str:
        """Get security status."""
        return "Security status: All defensive wards are active. No threats detected. The Firewall Gate stands strong. I am ever vigilant."
    
    def _get_process_info(self) -> str:
        """Get process information."""
        if PSUTIL_AVAILABLE:
            count = len(psutil.pids())
            return f"I see {count} spirits (processes) active in the realm. All are behaving within normal parameters."
        return "Process monitoring requires additional powers in this environment."
    
    def _get_network_info(self) -> str:
        """Get network information."""
        if PSUTIL_AVAILABLE:
            try:
                conns = len(psutil.net_connections())
                return f"The Network Tower reports {conns} active connections. All traffic flows are being monitored."
            except:
                pass
        return "Network pathways are clear. I watch all that enters and leaves."
    
    def _get_memory_info(self) -> str:
        """Get memory information."""
        if PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            return f"Memory status: {mem.percent:.1f}% used. {mem.available // (1024*1024)} MB available for your research."
        return "Memory reserves are adequate for your research needs."
    
    def _get_disk_info(self) -> str:
        """Get disk information."""
        if PSUTIL_AVAILABLE:
            disk = psutil.disk_usage('/')
            return f"Storage crystals: {disk.percent:.1f}% full. {disk.free // (1024*1024*1024)} GB of space remains."
        return "The Knowledge Vault has sufficient space for your research."
    
    def cmd_processes(self, args: List[str]) -> str:
        """Show running processes."""
        if not PSUTIL_AVAILABLE:
            return "Process viewing requires the process_lens (psutil not available)."
        
        self.print("\n═══ ACTIVE PROCESSES ═══", "bold cyan")
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        for p in processes[:15]:
            self.print(f"  [{p['pid']:5}] {p['name'][:20]:20} CPU: {p.get('cpu_percent', 0):5.1f}%  MEM: {p.get('memory_percent', 0):5.1f}%", "white")
        
        if len(processes) > 15:
            self.print(f"\n  ... and {len(processes) - 15} more spirits", "dim")
        
        return ""
    
    def cmd_shell(self, args: List[str]) -> str:
        """Execute a shell command."""
        if not args:
            return "What command do you wish to cast? Usage: shell <command>"
        
        command = " ".join(args)
        
        # Security check
        dangerous = ['rm -rf', 'mkfs', 'dd if=/dev/zero', '> /dev/sda', 'chmod -R 777 /']
        for pattern in dangerous:
            if pattern in command.lower():
                self.print_guardian(f"I cannot allow that command. It poses too great a risk to the realm.")
                return ""
        
        self.print(f"\nCasting: {command}", "bold yellow")
        self.print("─" * 40, "dim")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                self.print(result.stderr, "red")
        except subprocess.TimeoutExpired:
            return "The spell took too long and was interrupted."
        except Exception as e:
            return f"The spell failed: {e}"
        
        return ""
    
    def cmd_bash(self, args: List[str]) -> str:
        """Drop to bash shell."""
        self.print("\nEntering the Terminal Nexus directly...", "yellow")
        self.print("Type 'exit' to return to the adventure.", "dim")
        self.print("─" * 40, "dim")
        
        try:
            os.system('/bin/bash')
        except Exception as e:
            return f"Could not enter the nexus: {e}"
        
        self.print("\nYou return from the Terminal Nexus.", "cyan")
        return ""
    
    def cmd_help(self, args: List[str]) -> str:
        """Show help."""
        self.print("""
═══════════════════════════════════════════════════════════════════
                    VA21 RESEARCH OS - COMMAND GUIDE
           Custom Created Zork-Style Interface by VA21 Team
═══════════════════════════════════════════════════════════════════

♿ ACCESSIBILITY (Voice Input):
  Hold Super Key - Push-to-talk voice input (1,600+ languages)
  voice          - Check voice input status

MOVEMENT:
  go <direction>  - Move (north, south, east, west, up, down)
                    Shortcuts: n, s, e, w, u, d

EXPLORATION:
  look (l)        - Examine your surroundings
  examine <item>  - Look at something closely
  inventory (i)   - Check what you're carrying

INTERACTION:
  take <item>     - Pick up an item
  drop <item>     - Drop an item
  use <item>      - Use an item

GUARDIAN AI:
  ask guardian <topic> - Consult the Guardian AI
                         Topics: status, security, processes, 
                                 network, memory, disk, help

SECURITY (ClamAV):
  scan <path>     - Scan file/directory for threats using ClamAV
  quarantine list - View quarantined threats

RESEARCH (SearXNG):
  search <query>  - Search the internet (privacy-respecting)
  news <query>    - Search for news articles
  science <query> - Search scientific content

SYSTEM:
  shell <cmd>     - Execute a shell command
  bash            - Enter bash shell directly
  processes       - View running processes

HINTS:
  hints           - Check hints status
  hints on        - Enable helper hints (for newcomers)
  hints off       - Disable hints (for experts)

OTHER:
  score           - View your score
  save            - Save game state  
  clear           - Clear the screen
  quit            - Exit VA21 Research OS

═══════════════════════════════════════════════════════════════════
""", "cyan")
        return ""
    
    def cmd_score(self, args: List[str]) -> str:
        """Show score."""
        elapsed = datetime.now() - self.state.start_time
        minutes = int(elapsed.total_seconds() // 60)
        
        self.print(f"""
═══ RESEARCH PROGRESS ═══
Score: {self.state.score} points
Moves: {self.state.moves}
Rooms discovered: {len(self.state.visited_rooms)}/{len(self.rooms)}
Items collected: {len(self.state.inventory)}
Time exploring: {minutes} minutes
""", "cyan")
        return ""
    
    def cmd_save(self, args: List[str]) -> str:
        """Save game state."""
        save_data = {
            "current_room": self.state.current_room,
            "inventory": self.state.inventory,
            "visited_rooms": self.state.visited_rooms,
            "score": self.state.score,
            "moves": self.state.moves,
            "timestamp": datetime.now().isoformat()
        }
        
        save_path = os.path.expanduser("~/.va21_save.json")
        try:
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            return f"Game saved to {save_path}"
        except Exception as e:
            return f"Could not save: {e}"
    
    def cmd_load(self, args: List[str]) -> str:
        """Load game state."""
        save_path = os.path.expanduser("~/.va21_save.json")
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            self.state.current_room = save_data["current_room"]
            self.state.inventory = save_data["inventory"]
            self.state.visited_rooms = save_data["visited_rooms"]
            self.state.score = save_data["score"]
            self.state.moves = save_data["moves"]
            
            self.cmd_look([])
            return "Game loaded successfully."
        except FileNotFoundError:
            return "No saved game found."
        except Exception as e:
            return f"Could not load: {e}"
    
    def cmd_clear(self, args: List[str]) -> str:
        """Clear screen."""
        os.system('clear' if os.name != 'nt' else 'cls')
        return ""
    
    def cmd_quit(self, args: List[str]) -> str:
        """Quit the game."""
        self.print("\nThe Guardian nods respectfully.", "magenta")
        self.print('"Until we meet again, Researcher. May your discoveries be great."', "magenta italic")
        self.print(f"\nFinal Score: {self.state.score} points in {self.state.moves} moves.\n", "cyan")
        self.running = False
        return ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NEW COMMANDS: ClamAV, SearXNG, Hints
    # ═══════════════════════════════════════════════════════════════════════════
    
    def cmd_scan(self, args: List[str]) -> str:
        """Scan files for threats using ClamAV."""
        if not self.clamav:
            return "The ClamAV scanner crystal is not available. The Guardian relies on pattern detection alone."
        
        if not args:
            return "What would you like to scan? Usage: scan <file_or_directory>"
        
        path = " ".join(args)
        
        # Expand path
        if path.startswith("~"):
            path = os.path.expanduser(path)
        
        if not os.path.exists(path):
            return f"The path '{path}' does not exist in this realm."
        
        self.print(f"\n🔍 The Guardian activates the ClamAV scanner crystal...", "cyan")
        self.print(f"Scanning: {path}", "dim")
        self.print("─" * 40, "dim")
        
        if os.path.isdir(path):
            results = self.clamav.scan_directory(path, recursive=True)
        else:
            results = [self.clamav.scan_file(path)]
        
        threats = [r for r in results if r.infected]
        clean = len(results) - len(threats)
        
        self.print(f"\n📊 Scan Complete:", "bold")
        self.print(f"   Files scanned: {len(results)}", "white")
        self.print(f"   Clean: {clean}", "green")
        self.print(f"   Threats: {len(threats)}", "red" if threats else "green")
        
        if threats:
            self.print("\n⚠️ THREATS DETECTED:", "bold red")
            for t in threats:
                self.print(f"   🦠 {t.path}", "red")
                self.print(f"      Threat: {t.threat_name}", "yellow")
            self.print_guardian("I have detected threats in the realm. These files should be quarantined or removed.")
        else:
            self.print_guardian("The scan is complete. No threats were detected. The realm remains pure.")
        
        return ""
    
    def cmd_quarantine(self, args: List[str]) -> str:
        """View or manage quarantined files."""
        if not self.clamav:
            return "The ClamAV quarantine vault is not available."
        
        if args and args[0] == "list":
            contents = self.clamav.get_quarantine_contents()
            if not contents:
                return "The quarantine vault is empty. No threats have been contained."
            
            self.print("\n🔒 QUARANTINE VAULT:", "bold cyan")
            for item in contents:
                self.print(f"   📦 {item['filename']} ({item['size']} bytes)", "yellow")
                self.print(f"      Contained: {item['quarantined_at']}", "dim")
            return ""
        
        return "Usage: quarantine list - View quarantined files"
    
    def cmd_search(self, args: List[str]) -> str:
        """Search the internet using SearXNG."""
        if not args:
            return "What would you like to search for? Usage: search <query>"
        
        query = " ".join(args)
        
        if not self.searxng:
            self.print(f"\n🔍 Searching for: {query}", "cyan")
            self.print("(SearXNG not available - showing simulated results)", "dim")
            self.print("\nTo enable real search, ensure SearXNG client is installed.", "yellow")
            return ""
        
        self.print(f"\n🔍 Consulting the Oracle of Knowledge...", "cyan")
        self.print(f"Query: {query}", "dim")
        
        try:
            result = self.searxng.search(query)
            
            self.print(f"\n═══ SEARCH RESULTS ═══", "bold cyan")
            self.print(f"Found {result.total_results} results in {result.search_time:.2f}s", "dim")
            self.print("─" * 50, "dim")
            
            if not result.results:
                return "The Oracle found no results for your query."
            
            for r in result.results[:10]:
                self.print(f"\n[{r.position}] {r.title}", "bold yellow")
                self.print(f"    {r.url}", "blue")
                if r.snippet:
                    snippet = r.snippet[:150] + "..." if len(r.snippet) > 150 else r.snippet
                    self.print(f"    {snippet}", "white")
            
            self.state.score += 5  # Bonus for research
            return ""
            
        except Exception as e:
            return f"The Oracle encountered an error: {e}"
    
    def cmd_search_news(self, args: List[str]) -> str:
        """Search for news using SearXNG."""
        if not args:
            return "What news would you like to find? Usage: news <query>"
        
        if not self.searxng:
            return "SearXNG is not available for news search."
        
        query = " ".join(args)
        result = self.searxng.search_news(query)
        
        self.print(f"\n📰 NEWS RESULTS for '{query}'", "bold cyan")
        
        if not result.results:
            return "No news found for your query."
        
        for r in result.results[:5]:
            self.print(f"\n• {r.title}", "bold yellow")
            self.print(f"  {r.url}", "blue")
        
        return ""
    
    def cmd_search_science(self, args: List[str]) -> str:
        """Search for scientific content using SearXNG."""
        if not args:
            return "What scientific topic? Usage: science <query>"
        
        if not self.searxng:
            return "SearXNG is not available for science search."
        
        query = " ".join(args)
        result = self.searxng.search_science(query)
        
        self.print(f"\n🔬 SCIENCE RESULTS for '{query}'", "bold cyan")
        
        if not result.results:
            return "No scientific content found for your query."
        
        for r in result.results[:5]:
            self.print(f"\n• {r.title}", "bold yellow")
            self.print(f"  {r.url}", "blue")
        
        return ""
    
    def cmd_hints(self, args: List[str]) -> str:
        """Toggle or manage the hints system."""
        if not args:
            status = "enabled" if self.state.hints_enabled else "disabled"
            return f"Hints are currently {status}. Use 'hints on' or 'hints off' to toggle."
        
        action = args[0].lower()
        
        if action in ["on", "enable", "yes"]:
            self.state.hints_enabled = True
            return "💡 Hints enabled. Contextual hints will now appear to guide you."
        elif action in ["off", "disable", "no"]:
            self.state.hints_enabled = False
            return "Hints disabled. You're now exploring like a true expert!"
        elif action == "show":
            hint = HintsSystem.get_hint(self.state.current_room, self.state.moves)
            if hint:
                self.print(hint, "dim italic")
            return ""
        else:
            return "Usage: hints [on|off|show]"
    
    def _show_contextual_hint(self):
        """Show a contextual hint if hints are enabled."""
        if not self.state.hints_enabled:
            return
        
        # Only show hints occasionally (every 5 moves or on first visit)
        if self.state.moves % 5 == 0 or self.state.current_room not in self.state.visited_rooms:
            hint = HintsSystem.get_hint(self.state.current_room, self.state.moves)
            if hint:
                self.print(f"\n{hint}", "dim italic")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VAULT AND WRITING COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def cmd_note(self, args: List[str]) -> str:
        """Create or view notes in the Knowledge Vault."""
        if not self.vault:
            return "The Knowledge Vault is not available."
        
        if not args:
            return """Usage:
  note create <title> - Create a new note
  note list           - List all notes
  note search <query> - Search notes
  note view <title>   - View a note
  note sensitive <title> - Mark note as sensitive"""
        
        action = args[0].lower()
        
        if action == "create":
            if len(args) < 2:
                return "What would you like to call this note?"
            title = " ".join(args[1:])
            note = self.vault.create_note(title=title)
            self.print_guardian(f"A new scroll has been created: '{title}'. You may now inscribe your knowledge.")
            self.state.score += 5
            return f"Note created: {note.path}"
        
        elif action == "list":
            notes = list(self.vault.notes_index.values())
            if not notes:
                return "The Knowledge Vault is empty. Create your first note with 'note create <title>'."
            
            self.print("\n📚 KNOWLEDGE VAULT CONTENTS:", "bold cyan")
            for note in notes[:20]:
                sens_icon = "🔒" if note.sensitivity.value in ["sensitive", "confidential"] else "📄"
                tags = f" [{', '.join(note.tags[:3])}]" if note.tags else ""
                self.print(f"  {sens_icon} {note.title}{tags}", "white")
            if len(notes) > 20:
                self.print(f"\n  ... and {len(notes) - 20} more notes", "dim")
            return ""
        
        elif action == "search":
            if len(args) < 2:
                return "What would you like to search for?"
            query = " ".join(args[1:])
            results = self.vault.search(query)
            if not results:
                return f"No notes found matching '{query}'."
            
            self.print(f"\n🔍 Search results for '{query}':", "bold cyan")
            for note in results[:10]:
                self.print(f"  📄 {note.title}", "white")
            return ""
        
        elif action == "view":
            if len(args) < 2:
                return "Which note would you like to view?"
            title = " ".join(args[1:])
            for note in self.vault.notes_index.values():
                if title.lower() in note.title.lower():
                    self.print(f"\n═══ {note.title} ═══", "bold cyan")
                    self.print(f"Tags: {', '.join(note.tags)}", "dim")
                    self.print(f"Sensitivity: {note.sensitivity.value}", "dim")
                    self.print("─" * 40, "dim")
                    self.print(note.content[:500], "white")
                    if len(note.content) > 500:
                        self.print("\n[Content truncated...]", "dim")
                    return ""
            return f"Note '{title}' not found."
        
        elif action == "sensitive":
            if len(args) < 2:
                return "Which note should be marked as sensitive?"
            title = " ".join(args[1:])
            for note in self.vault.notes_index.values():
                if title.lower() in note.title.lower():
                    from obsidian.vault_manager import SensitivityLevel
                    self.vault.mark_sensitive(note.id, SensitivityLevel.SENSITIVE)
                    self.print_guardian(f"The scroll '{note.title}' has been sealed. Its contents are now protected.")
                    return ""
            return f"Note '{title}' not found."
        
        return "Unknown note command. Type 'note' for usage."
    
    def cmd_write(self, args: List[str]) -> str:
        """Writing suite commands for documents."""
        if not self.writing:
            return "The Writing Suite is not available."
        
        if not args:
            return """Usage:
  write article <title>  - Create a new article
  write paper <title>    - Create a research paper
  write news <title>     - Create a news article
  write blog <title>     - Create a blog post
  write list             - List all documents
  write export <id> <format> - Export document (md, html, txt)"""
        
        action = args[0].lower()
        
        if action in ["article", "paper", "news", "blog"]:
            if len(args) < 2:
                return f"What would you like to title your {action}?"
            title = " ".join(args[1:])
            
            from writing.writing_suite import DocumentType
            type_map = {
                "article": DocumentType.ARTICLE,
                "paper": DocumentType.RESEARCH_PAPER,
                "news": DocumentType.NEWS_ARTICLE,
                "blog": DocumentType.BLOG_POST
            }
            
            doc = self.writing.create_document(
                title=title,
                doc_type=type_map[action]
            )
            self.print_guardian(f"A new {action} has been prepared: '{title}'. May your words flow with wisdom.")
            self.state.score += 10
            return f"Document created: {doc.id}"
        
        elif action == "list":
            docs = self.writing.list_documents()
            if not docs:
                return "No documents yet. Create one with 'write article <title>'."
            
            self.print("\n📝 WRITING SUITE DOCUMENTS:", "bold cyan")
            for doc in docs[:15]:
                self.print(f"  [{doc.id}] {doc.title} ({doc.doc_type.value}) - {doc.status.value}", "white")
                self.print(f"      Words: {doc.word_count}", "dim")
            return ""
        
        elif action == "export":
            if len(args) < 2:
                return "Which document ID to export?"
            doc_id = args[1]
            format = args[2] if len(args) > 2 else "md"
            
            filepath = self.writing.export_document(doc_id, format)
            if filepath:
                return f"Document exported to: {filepath}"
            return "Export failed. Check document ID."
        
        return "Unknown write command. Type 'write' for usage."
    
    def cmd_cite(self, args: List[str]) -> str:
        """Citation management."""
        if not self.writing:
            return "The Writing Suite is not available for citations."
        
        if not args:
            return """Usage:
  cite add <type> <title> by <author> (<year>) - Add citation
  cite list                                    - List citations
  cite format <id> <style>                     - Format citation (apa, mla, chicago)"""
        
        action = args[0].lower()
        
        if action == "list":
            if not self.writing.citations:
                return "No citations yet. Add one with 'cite add'."
            
            self.print("\n📖 CITATIONS:", "bold cyan")
            for cite_id, cite in self.writing.citations.items():
                self.print(f"  [{cite_id}] {cite.title}", "white")
                self.print(f"      {', '.join(cite.authors)} ({cite.year})", "dim")
            return ""
        
        elif action == "format":
            if len(args) < 2:
                return "Which citation ID to format?"
            cite_id = args[1]
            style = args[2] if len(args) > 2 else "apa"
            
            formatted = self.writing.format_citation(cite_id, style)
            if formatted:
                self.print(f"\n{style.upper()} format:", "bold")
                self.print(formatted, "white")
                return ""
            return "Citation not found."
        
        return "Use 'cite add' to add a new citation."
    
    def cmd_about(self, args: List[str]) -> str:
        """Show about and license information."""
        try:
            from licenses.license_acceptance import get_license_acceptance
            get_license_acceptance().show_about()
        except ImportError:
            self.print("""
═══ VA21 RESEARCH OS v1.0.0 (Vinayaka) ═══

A secure, privacy-first research operating system.

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.

Incorporating open-source software:
- Alpine Linux
- ClamAV (Antivirus)
- SearXNG (Privacy Search)
- BusyBox
- Python Libraries

Type 'licenses' for full acknowledgments.
""", "cyan")
        return ""
    
    def cmd_licenses(self, args: List[str]) -> str:
        """Show open-source licenses and acknowledgments."""
        license_file = "/va21/licenses/ACKNOWLEDGMENTS.md"
        if os.path.exists(license_file):
            with open(license_file, 'r') as f:
                content = f.read()
            # Show summary
            self.print("\n═══ OPEN-SOURCE ACKNOWLEDGMENTS ═══", "bold cyan")
            self.print("""
VA21 Research OS gratefully acknowledges these open-source projects:

🏔️ Alpine Linux - Operating system base
🛡️ ClamAV - Antivirus protection (GPLv2)
🔍 SearXNG - Privacy search (AGPL-3.0)
📦 BusyBox - Unix utilities (GPLv2)
🐍 Python - Programming language (PSF)
📝 Rich, prompt_toolkit, PyYAML, Requests - Python libraries

Full acknowledgments available at:
  /va21/licenses/ACKNOWLEDGMENTS.md

Thank you to all open-source contributors!
""", "white")
            return ""
        return "License file not found."
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN LOOP
    # ═══════════════════════════════════════════════════════════════════════════
    
    def execute_command(self, command_str: str) -> str:
        """Parse and execute a command."""
        if not command_str.strip():
            return ""
        
        # Apply aliases
        parts = command_str.strip().split()
        if parts[0].lower() in self.aliases:
            alias_expansion = self.aliases[parts[0].lower()]
            command_str = alias_expansion + " " + " ".join(parts[1:])
            parts = command_str.strip().split()
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Command dispatch
        commands = {
            'look': self.cmd_look,
            'go': self.cmd_go,
            'examine': self.cmd_examine,
            'take': self.cmd_take,
            'get': self.cmd_take,
            'drop': self.cmd_drop,
            'inventory': self.cmd_inventory,
            'use': self.cmd_use,
            'ask': self.cmd_ask,
            'processes': self.cmd_processes,
            'shell': self.cmd_shell,
            'cast': self.cmd_shell,
            'bash': self.cmd_bash,
            'terminal': self.cmd_bash,
            'help': self.cmd_help,
            'score': self.cmd_score,
            'save': self.cmd_save,
            'load': self.cmd_load,
            'restore': self.cmd_load,
            'clear': self.cmd_clear,
            'quit': self.cmd_quit,
            # New commands: ClamAV, SearXNG, Hints
            'scan': self.cmd_scan,
            'quarantine': self.cmd_quarantine,
            'search': self.cmd_search,
            'google': self.cmd_search,  # Alias for search
            'news': self.cmd_search_news,
            'science': self.cmd_search_science,
            'hints': self.cmd_hints,
            'voice': self.cmd_voice,
        }
        
        if cmd in commands:
            self.state.moves += 1
            result = commands[cmd](args)
            # Show contextual hint after certain commands
            self._show_contextual_hint()
            return result
        else:
            # Show hint for unknown command if hints enabled
            if self.state.hints_enabled:
                hint = HintsSystem.get_command_hint(cmd)
                if hint:
                    return f"I don't understand '{cmd}'.\n{hint}"
            return f"I don't understand '{cmd}'. Type 'help' for commands."
    
    def _handle_voice_command(self, text: str):
        """Handle voice command from push-to-talk."""
        if text:
            self.voice_command_pending = text
    
    def cmd_voice(self, args: List[str]) -> str:
        """Check voice input status."""
        if self.voice_input:
            return """🎤 Voice Input (Accessibility Feature)
            
Status: Available
How to use: Hold the Super key, speak your command, release to send.

This feature supports 1,600+ languages via Meta Omnilingual ASR.
Perfect for users who cannot type or prefer voice interaction."""
        else:
            return "🎤 Voice input is not available. Install 'speech_recognition' and 'pynput' packages."
    
    def show_intro(self):
        """Show the game introduction."""
        os.system('clear' if os.name != 'nt' else 'cls')
        
        self.print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ██╗   ██╗ █████╗ ██████╗  ██╗    ██████╗ ███████╗               ║
║   ██║   ██║██╔══██╗╚════██╗███║   ██╔═══██╗██╔════╝               ║
║   ██║   ██║███████║ █████╔╝╚██║   ██║   ██║███████╗               ║
║   ╚██╗ ██╔╝██╔══██║██╔═══╝  ██║   ██║   ██║╚════██║               ║
║    ╚████╔╝ ██║  ██║███████╗ ██║   ╚██████╔╝███████║               ║
║     ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═╝    ╚═════╝ ╚══════╝               ║
║                                                                   ║
║              RESEARCH OS v1.3 (Vinayaka)                          ║
║                                                                   ║
║     A Text Adventure in Secure Research Computing                 ║
║     Custom Created Zork-Style Interface by VA21 Team              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""", "cyan")
        
        self.print("Om Vinayaka", "bold magenta")
        self.print("May obstacles be removed from your research journey.\n", "magenta italic")
        
        # Show voice input availability
        if self.voice_input:
            self.print("♿ Accessibility: Hold Super key for voice input\n", "dim")
        
        time.sleep(1)
        
        self.print("""
You slowly open your eyes. Ancient code scrolls across crystalline 
walls. You are in a vast chamber filled with warm, pulsing light.

A presence stirs nearby. The GUARDIAN AI materializes before you -
an entity of pure protective energy, its amber eyes watchful yet kind.

"Welcome, Researcher," the Guardian intones. "You have entered 
VA21 Research OS, a realm of secure discovery. I am the Guardian,
and I shall protect you on your journey."

"Explore freely. Learn deeply. I am always watching."

""", "white")
        
        self.print('(Type "help" for commands, "look" to examine your surroundings)', "dim")
        if self.voice_input:
            self.print('(Hold Super key to speak commands - Accessibility feature)\n', "dim")
        
        # Show initial room
        self.print_room(self.rooms["boot_chamber"])
    
    def run(self):
        """Main game loop."""
        self.show_intro()
        self.state.visited_rooms.append("boot_chamber")
        
        # Start voice input listener if available
        if self.voice_input:
            self.voice_input.start_keyboard_listener()
        
        while self.running:
            try:
                # Check for voice command
                if self.voice_command_pending:
                    command = self.voice_command_pending
                    self.voice_command_pending = None
                    self.print(f"\n🎤 Voice: {command}", "cyan")
                else:
                    # Show prompt
                    room = self.rooms[self.state.current_room]
                    prompt = f"[{room.name}]> "
                    
                    if RICH_AVAILABLE:
                        command = input(f"\033[1;32m{prompt}\033[0m")
                    else:
                        command = input(prompt)
                
                # Execute command
                result = self.execute_command(command)
                if result:
                    self.print(result, "white")
                    
            except KeyboardInterrupt:
                print()
                self.cmd_quit([])
            except EOFError:
                print()
                self.cmd_quit([])
        
        # Cleanup voice input
        if self.voice_input:
            self.voice_input.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point."""
    interface = VA21ZorkInterface()
    interface.run()


if __name__ == "__main__":
    main()
