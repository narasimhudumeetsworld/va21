#!/usr/bin/env python3
"""
VA21 OS - App Zork Interface Generator
=======================================

This module creates Zork-style text adventure interfaces for EVERY application.
When an app is installed, VA21 analyzes it and generates a custom Zork-like
interface layer, stored in the accessibility knowledge base.

This allows voice users and accessibility users to interact with ANY application
using natural language through a unified, conversational interface.

Architecture:
- App Analyzer: Scans app UI, menus, and functions
- Zork Generator: Creates text adventure interface for the app
- Knowledge Base: Stores app interfaces in Obsidian-style vault with LangChain
- FARA Bridge: Connects Zork commands to actual app actions

Om Vinayaka - May obstacles be removed from your computing journey.
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# APP INTERFACE STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class UIElementType(Enum):
    """Types of UI elements that can be mapped to Zork actions."""
    MENU = "menu"
    BUTTON = "button"
    TEXT_INPUT = "text_input"
    LIST = "list"
    TAB = "tab"
    TOOLBAR = "toolbar"
    DIALOG = "dialog"
    PANEL = "panel"
    CANVAS = "canvas"
    STATUS_BAR = "status_bar"


@dataclass
class UIElement:
    """Represents a UI element that can be interacted with."""
    element_type: UIElementType
    name: str
    label: str
    action: str  # What happens when activated
    description: str  # Natural language description
    keyboard_shortcut: Optional[str] = None
    children: List['UIElement'] = field(default_factory=list)


@dataclass
class ZorkRoom:
    """A 'room' in the Zork interface representing an app state/view."""
    room_id: str
    name: str
    description: str
    long_description: str
    exits: Dict[str, str]  # direction -> room_id
    items: List[str]  # Available actions/tools
    ui_mapping: Dict[str, str]  # Zork action -> UI action


@dataclass
class AppZorkInterface:
    """Complete Zork interface for an application."""
    app_id: str
    app_name: str
    app_description: str
    rooms: Dict[str, ZorkRoom]
    items: Dict[str, str]  # item_id -> description
    commands: Dict[str, str]  # command -> action
    welcome_message: str
    created_at: str
    version: str = "1.0"


# ═══════════════════════════════════════════════════════════════════════════════
# APP ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

class AppAnalyzer:
    """
    Analyzes applications to understand their UI structure.
    
    Uses multiple methods:
    1. Desktop file parsing (.desktop)
    2. Window introspection (accessibility APIs)
    3. Menu structure analysis
    4. Common app pattern matching
    """
    
    def __init__(self):
        self.known_patterns = self._load_known_patterns()
    
    def _load_known_patterns(self) -> Dict[str, Dict]:
        """Load known patterns for common applications."""
        return {
            # Text Editors
            'gedit': {
                'category': 'text_editor',
                'rooms': ['main_editor', 'preferences', 'search_dialog'],
                'main_actions': ['new', 'open', 'save', 'save_as', 'print', 'find', 'replace', 'undo', 'redo'],
            },
            'vim': {
                'category': 'text_editor',
                'rooms': ['normal_mode', 'insert_mode', 'command_mode', 'visual_mode'],
                'main_actions': ['write', 'quit', 'search', 'replace', 'undo', 'redo', 'copy', 'paste'],
            },
            'nano': {
                'category': 'text_editor', 
                'rooms': ['editor'],
                'main_actions': ['save', 'exit', 'search', 'cut', 'paste', 'goto_line'],
            },
            
            # File Managers
            'nautilus': {
                'category': 'file_manager',
                'rooms': ['file_browser', 'properties', 'preferences'],
                'main_actions': ['open', 'copy', 'paste', 'delete', 'rename', 'new_folder', 'search', 'properties'],
            },
            'thunar': {
                'category': 'file_manager',
                'rooms': ['file_browser', 'properties'],
                'main_actions': ['open', 'copy', 'paste', 'delete', 'rename', 'new_folder', 'search'],
            },
            
            # Web Browsers
            'firefox': {
                'category': 'web_browser',
                'rooms': ['main_browser', 'bookmarks', 'history', 'downloads', 'settings', 'developer_tools'],
                'main_actions': ['go_to', 'search', 'back', 'forward', 'refresh', 'new_tab', 'close_tab', 'bookmark', 'download'],
            },
            'chromium': {
                'category': 'web_browser',
                'rooms': ['main_browser', 'bookmarks', 'history', 'downloads', 'settings'],
                'main_actions': ['go_to', 'search', 'back', 'forward', 'refresh', 'new_tab', 'close_tab', 'bookmark'],
            },
            
            # Terminals
            'gnome-terminal': {
                'category': 'terminal',
                'rooms': ['terminal_session'],
                'main_actions': ['run_command', 'new_tab', 'close_tab', 'copy', 'paste', 'clear', 'search'],
            },
            'xterm': {
                'category': 'terminal',
                'rooms': ['terminal_session'],
                'main_actions': ['run_command', 'copy', 'paste', 'clear'],
            },
            
            # Office Applications
            'libreoffice-writer': {
                'category': 'word_processor',
                'rooms': ['document', 'styles', 'insert_menu', 'format_menu', 'tools_menu', 'print_preview'],
                'main_actions': ['new', 'open', 'save', 'save_as', 'print', 'undo', 'redo', 'copy', 'paste', 
                               'find', 'replace', 'insert_image', 'insert_table', 'format_text', 'spell_check'],
            },
            'libreoffice-calc': {
                'category': 'spreadsheet',
                'rooms': ['spreadsheet', 'chart_wizard', 'function_wizard', 'format_cells'],
                'main_actions': ['new', 'open', 'save', 'copy', 'paste', 'insert_row', 'insert_column',
                               'delete_row', 'delete_column', 'sum', 'average', 'create_chart', 'sort', 'filter'],
            },
            
            # Image Editors
            'gimp': {
                'category': 'image_editor',
                'rooms': ['canvas', 'layers', 'tools', 'colors', 'filters', 'export'],
                'main_actions': ['new', 'open', 'save', 'export', 'undo', 'redo', 'select_tool', 'draw', 
                               'fill', 'crop', 'resize', 'rotate', 'add_layer', 'apply_filter'],
            },
            
            # Media Players
            'vlc': {
                'category': 'media_player',
                'rooms': ['player', 'playlist', 'settings', 'equalizer'],
                'main_actions': ['play', 'pause', 'stop', 'next', 'previous', 'volume_up', 'volume_down',
                               'mute', 'fullscreen', 'add_to_playlist', 'shuffle', 'repeat'],
            },
        }
    
    def analyze_app(self, app_name: str, desktop_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an application and return its structure.
        
        Returns information about:
        - App category
        - Main views/screens (rooms)
        - Available actions
        - Menu structure
        - Keyboard shortcuts
        """
        # Check if we have a known pattern
        app_key = app_name.lower().replace(' ', '-')
        if app_key in self.known_patterns:
            return self._analyze_known_app(app_key)
        
        # Try to analyze from desktop file
        if desktop_file and os.path.exists(desktop_file):
            return self._analyze_desktop_file(desktop_file)
        
        # Try to find desktop file
        desktop_paths = [
            f"/usr/share/applications/{app_key}.desktop",
            f"/usr/local/share/applications/{app_key}.desktop",
            os.path.expanduser(f"~/.local/share/applications/{app_key}.desktop"),
        ]
        
        for path in desktop_paths:
            if os.path.exists(path):
                return self._analyze_desktop_file(path)
        
        # Return generic analysis
        return self._analyze_unknown_app(app_name)
    
    def _analyze_known_app(self, app_key: str) -> Dict[str, Any]:
        """Analyze a known application pattern."""
        pattern = self.known_patterns[app_key]
        
        return {
            'app_name': app_key,
            'category': pattern['category'],
            'rooms': pattern['rooms'],
            'main_actions': pattern['main_actions'],
            'has_menu': True,
            'has_toolbar': True,
            'source': 'known_pattern'
        }
    
    def _analyze_desktop_file(self, desktop_file: str) -> Dict[str, Any]:
        """Analyze app from its .desktop file."""
        info = {
            'app_name': '',
            'category': 'unknown',
            'rooms': ['main'],
            'main_actions': ['help', 'quit'],
            'has_menu': True,
            'has_toolbar': False,
            'source': 'desktop_file'
        }
        
        try:
            with open(desktop_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('Name='):
                        info['app_name'] = line.split('=', 1)[1]
                    elif line.startswith('Categories='):
                        categories = line.split('=', 1)[1].lower()
                        if 'editor' in categories or 'texteditor' in categories:
                            info['category'] = 'text_editor'
                            info['main_actions'] = ['new', 'open', 'save', 'undo', 'redo', 'find', 'help', 'quit']
                        elif 'browser' in categories or 'webbrowser' in categories:
                            info['category'] = 'web_browser'
                            info['main_actions'] = ['go_to', 'search', 'back', 'forward', 'refresh', 'help', 'quit']
                        elif 'filemanager' in categories:
                            info['category'] = 'file_manager'
                            info['main_actions'] = ['open', 'copy', 'paste', 'delete', 'new_folder', 'help', 'quit']
                        elif 'terminal' in categories:
                            info['category'] = 'terminal'
                            info['main_actions'] = ['run_command', 'copy', 'paste', 'clear', 'help', 'quit']
                        elif 'graphics' in categories:
                            info['category'] = 'image_editor'
                            info['main_actions'] = ['new', 'open', 'save', 'undo', 'redo', 'help', 'quit']
                        elif 'audio' in categories or 'video' in categories:
                            info['category'] = 'media_player'
                            info['main_actions'] = ['play', 'pause', 'stop', 'next', 'previous', 'help', 'quit']
        except Exception:
            pass
        
        return info
    
    def _analyze_unknown_app(self, app_name: str) -> Dict[str, Any]:
        """Generate generic analysis for unknown app."""
        return {
            'app_name': app_name,
            'category': 'unknown',
            'rooms': ['main'],
            'main_actions': ['help', 'quit'],
            'has_menu': True,
            'has_toolbar': False,
            'source': 'generic'
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ZORK INTERFACE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ZorkInterfaceGenerator:
    """
    Generates Zork-style text adventure interfaces for applications.
    
    Transforms app analysis into:
    - Rooms (app views/screens)
    - Items (available tools/actions)
    - Commands (mapped to app functions)
    - Narrative descriptions
    """
    
    def __init__(self):
        self.room_templates = self._load_room_templates()
        self.action_narratives = self._load_action_narratives()
    
    def _load_room_templates(self) -> Dict[str, Dict]:
        """Load templates for generating room descriptions."""
        return {
            'text_editor': {
                'main_theme': 'The Scribe\'s Workshop',
                'room_prefix': 'You are in',
                'ambient': 'Ink and parchment fill the air. Ancient texts line the walls.',
            },
            'file_manager': {
                'main_theme': 'The Archive Chambers',
                'room_prefix': 'You stand in',
                'ambient': 'Endless shelves of scrolls and documents stretch before you.',
            },
            'web_browser': {
                'main_theme': 'The Portal Nexus',
                'room_prefix': 'You find yourself in',
                'ambient': 'Shimmering gateways to countless realms surround you.',
            },
            'terminal': {
                'main_theme': 'The Command Sanctum',
                'room_prefix': 'You enter',
                'ambient': 'Ancient runes of power glow on obsidian walls.',
            },
            'image_editor': {
                'main_theme': 'The Artist\'s Studio',
                'room_prefix': 'You step into',
                'ambient': 'Colors dance in the air. Canvases await your vision.',
            },
            'media_player': {
                'main_theme': 'The Music Hall',
                'room_prefix': 'You enter',
                'ambient': 'Melodies echo through crystal chambers.',
            },
            'word_processor': {
                'main_theme': 'The Grand Library',
                'room_prefix': 'You are in',
                'ambient': 'Books and manuscripts fill every corner. A quill awaits your words.',
            },
            'spreadsheet': {
                'main_theme': 'The Calculation Chamber',
                'room_prefix': 'You stand in',
                'ambient': 'Numbers float in ordered grids. Logic rules this realm.',
            },
            'unknown': {
                'main_theme': 'The Mystery Chamber',
                'room_prefix': 'You find yourself in',
                'ambient': 'An unfamiliar place with unknown powers.',
            },
        }
    
    def _load_action_narratives(self) -> Dict[str, str]:
        """Load narrative descriptions for common actions."""
        return {
            'save': "You carefully preserve your work for future generations.",
            'open': "You reach out and open the chosen artifact.",
            'new': "A fresh canvas appears before you, ready for creation.",
            'copy': "You create a perfect duplicate of the selected material.",
            'paste': "You place the copied material here.",
            'delete': "The selected item vanishes into the void.",
            'undo': "Time reverses, undoing your last action.",
            'redo': "Time moves forward again, restoring what was undone.",
            'search': "You begin to search through the vast collection.",
            'find': "Your eyes scan for the object of your quest.",
            'help': "Ancient wisdom appears before you.",
            'quit': "You prepare to leave this realm.",
            'play': "Music begins to fill the air.",
            'pause': "Time stands still, the music frozen.",
            'stop': "Silence returns to the chamber.",
            'back': "You step backward through the portal.",
            'forward': "You move forward through the portal.",
            'refresh': "The realm shimmers and renews itself.",
            'go_to': "You speak the destination and a portal opens.",
            'run_command': "You speak words of power.",
            'new_tab': "A new portal window opens before you.",
            'close_tab': "The portal window closes.",
            'bookmark': "You mark this location for future return.",
        }
    
    def generate_interface(self, app_analysis: Dict[str, Any]) -> AppZorkInterface:
        """
        Generate a complete Zork interface for an application.
        """
        app_name = app_analysis.get('app_name', 'Unknown App')
        category = app_analysis.get('category', 'unknown')
        
        # Get template
        template = self.room_templates.get(category, self.room_templates['unknown'])
        
        # Generate rooms
        rooms = self._generate_rooms(app_analysis, template)
        
        # Generate items (actions as collectible tools)
        items = self._generate_items(app_analysis)
        
        # Generate commands
        commands = self._generate_commands(app_analysis)
        
        # Generate welcome message
        welcome = self._generate_welcome(app_name, template)
        
        # Create interface
        interface = AppZorkInterface(
            app_id=self._generate_app_id(app_name),
            app_name=app_name,
            app_description=f"{template['main_theme']} - {app_name}",
            rooms=rooms,
            items=items,
            commands=commands,
            welcome_message=welcome,
            created_at=datetime.now().isoformat(),
        )
        
        return interface
    
    def _generate_app_id(self, app_name: str) -> str:
        """Generate unique ID for app interface."""
        return hashlib.md5(app_name.lower().encode()).hexdigest()[:12]
    
    def _generate_rooms(self, app_analysis: Dict, template: Dict) -> Dict[str, ZorkRoom]:
        """Generate rooms for the app interface."""
        rooms = {}
        room_names = app_analysis.get('rooms', ['main'])
        category = app_analysis.get('category', 'unknown')
        
        for i, room_name in enumerate(room_names):
            room_id = room_name.lower().replace(' ', '_')
            
            # Generate room description
            description = self._generate_room_description(room_name, category, template)
            
            # Generate exits to other rooms
            exits = {}
            if i > 0:
                exits['back'] = room_names[i-1].lower().replace(' ', '_')
            if i < len(room_names) - 1:
                exits['forward'] = room_names[i+1].lower().replace(' ', '_')
            if room_id != 'main' and 'main' in [r.lower().replace(' ', '_') for r in room_names]:
                exits['home'] = 'main'
            
            # Generate items in room (context-specific actions)
            items = self._get_room_items(room_name, app_analysis)
            
            room = ZorkRoom(
                room_id=room_id,
                name=self._format_room_name(room_name),
                description=description['short'],
                long_description=description['long'],
                exits=exits,
                items=items,
                ui_mapping={}
            )
            
            rooms[room_id] = room
        
        return rooms
    
    def _generate_room_description(self, room_name: str, category: str, template: Dict) -> Dict[str, str]:
        """Generate short and long descriptions for a room."""
        prefix = template['room_prefix']
        ambient = template['ambient']
        
        room_specifics = {
            'main': f"the heart of {template['main_theme']}",
            'main_editor': "the main editing chamber",
            'main_browser': "the central portal chamber",
            'file_browser': "the main archive hall",
            'terminal_session': "a chamber of pure command power",
            'preferences': "the configuration sanctuary",
            'settings': "the realm of system adjustment",
            'search_dialog': "the seekers' alcove",
            'bookmarks': "the hall of marked destinations",
            'history': "the chronicles of past journeys",
            'downloads': "the treasure collection room",
            'playlist': "the song collection chamber",
            'layers': "the dimension manipulation room",
            'tools': "the tool arsenal",
            'canvas': "your creative workspace",
            'document': "your writing chamber",
        }
        
        room_key = room_name.lower().replace(' ', '_')
        specific = room_specifics.get(room_key, f"the {room_name}")
        
        short_desc = f"{prefix} {specific}."
        long_desc = f"{prefix} {specific}. {ambient}"
        
        return {'short': short_desc, 'long': long_desc}
    
    def _format_room_name(self, room_name: str) -> str:
        """Format room name for display."""
        return room_name.replace('_', ' ').title()
    
    def _get_room_items(self, room_name: str, app_analysis: Dict) -> List[str]:
        """Get items (actions) available in a room."""
        all_actions = app_analysis.get('main_actions', [])
        
        # Room-specific action mapping
        room_actions = {
            'main': all_actions[:5],
            'main_editor': ['save', 'undo', 'redo', 'find', 'replace'],
            'file_browser': ['open', 'copy', 'paste', 'delete', 'new_folder'],
            'main_browser': ['go_to', 'search', 'back', 'forward', 'refresh'],
            'preferences': ['apply', 'reset', 'cancel'],
            'settings': ['save', 'apply', 'reset'],
        }
        
        room_key = room_name.lower().replace(' ', '_')
        return room_actions.get(room_key, all_actions[:3])
    
    def _generate_items(self, app_analysis: Dict) -> Dict[str, str]:
        """Generate item descriptions for all actions."""
        items = {}
        actions = app_analysis.get('main_actions', [])
        
        for action in actions:
            narrative = self.action_narratives.get(action, f"The power to {action}.")
            items[action] = narrative
        
        return items
    
    def _generate_commands(self, app_analysis: Dict) -> Dict[str, str]:
        """Generate command mappings."""
        commands = {}
        actions = app_analysis.get('main_actions', [])
        
        for action in actions:
            # Map common verbs to the action
            commands[action] = action
            
            # Add aliases
            aliases = {
                'save': ['store', 'keep', 'preserve'],
                'open': ['access', 'load', 'enter'],
                'new': ['create', 'start'],
                'delete': ['remove', 'destroy', 'erase'],
                'copy': ['duplicate', 'clone'],
                'paste': ['put', 'place', 'insert'],
                'search': ['find', 'seek', 'look for'],
                'help': ['assist', 'guide'],
                'quit': ['exit', 'leave', 'close'],
            }
            
            if action in aliases:
                for alias in aliases[action]:
                    commands[alias] = action
        
        return commands
    
    def _generate_welcome(self, app_name: str, template: Dict) -> str:
        """Generate welcome message for the app interface."""
        return f"""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   Welcome to {template['main_theme'][:40]:^40}  ║
║   ({app_name[:45]:^45})  ║
║                                                                   ║
║   {template['ambient'][:55]:^55}  ║
║                                                                   ║
║   Your accessibility assistant is ready to guide you.            ║
║   Speak naturally or type what you'd like to do.                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

Type 'look' to see where you are, or tell me what you'd like to do.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# ACCESSIBILITY KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════════

class AccessibilityKnowledgeBase:
    """
    Stores and retrieves app Zork interfaces in an Obsidian-style vault.
    
    Uses:
    - Markdown files with wiki-style links
    - Mind maps for app relationships
    - LangChain-compatible vector storage
    - Searchable action database
    """
    
    def __init__(self, vault_path: Optional[str] = None):
        self.vault_path = vault_path or os.path.expanduser("~/.va21/accessibility_vault")
        self.apps_path = os.path.join(self.vault_path, "apps")
        self.mindmaps_path = os.path.join(self.vault_path, "mindmaps")
        self.index_path = os.path.join(self.vault_path, "index")
        
        # Ensure directories exist
        for path in [self.vault_path, self.apps_path, self.mindmaps_path, self.index_path]:
            os.makedirs(path, exist_ok=True)
        
        # Load index
        self.app_index = self._load_index()
    
    def _load_index(self) -> Dict[str, Dict]:
        """Load the app index."""
        index_file = os.path.join(self.index_path, "apps.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_index(self):
        """Save the app index."""
        index_file = os.path.join(self.index_path, "apps.json")
        with open(index_file, 'w') as f:
            json.dump(self.app_index, f, indent=2)
    
    def store_interface(self, interface: AppZorkInterface) -> bool:
        """Store an app interface in the knowledge base."""
        try:
            # Create app directory
            app_dir = os.path.join(self.apps_path, interface.app_id)
            os.makedirs(app_dir, exist_ok=True)
            
            # Save interface JSON
            interface_file = os.path.join(app_dir, "interface.json")
            with open(interface_file, 'w') as f:
                json.dump(self._interface_to_dict(interface), f, indent=2)
            
            # Create Obsidian-style markdown
            self._create_obsidian_note(interface, app_dir)
            
            # Update mind map
            self._update_mindmap(interface)
            
            # Update index
            self.app_index[interface.app_id] = {
                'app_name': interface.app_name,
                'description': interface.app_description,
                'created_at': interface.created_at,
                'version': interface.version,
            }
            self._save_index()
            
            return True
        except Exception as e:
            print(f"Error storing interface: {e}")
            return False
    
    def _interface_to_dict(self, interface: AppZorkInterface) -> Dict:
        """Convert interface to dictionary for JSON storage."""
        return {
            'app_id': interface.app_id,
            'app_name': interface.app_name,
            'app_description': interface.app_description,
            'rooms': {
                room_id: {
                    'room_id': room.room_id,
                    'name': room.name,
                    'description': room.description,
                    'long_description': room.long_description,
                    'exits': room.exits,
                    'items': room.items,
                    'ui_mapping': room.ui_mapping,
                }
                for room_id, room in interface.rooms.items()
            },
            'items': interface.items,
            'commands': interface.commands,
            'welcome_message': interface.welcome_message,
            'created_at': interface.created_at,
            'version': interface.version,
        }
    
    def _create_obsidian_note(self, interface: AppZorkInterface, app_dir: str):
        """Create Obsidian-style markdown note for the app."""
        note_content = f"""# {interface.app_name}

## Overview
{interface.app_description}

## Accessibility Interface
This app has been analyzed and a Zork-style interface has been generated.

### Rooms (Views)
"""
        for room_id, room in interface.rooms.items():
            note_content += f"""
#### [[{room.name}]]
{room.long_description}

**Available actions:** {', '.join(room.items)}
**Exits:** {', '.join([f'{d} → [[{interface.rooms.get(r, room).name}]]' for d, r in room.exits.items()])}
"""
        
        note_content += """
### Commands
| Command | Action |
|---------|--------|
"""
        for cmd, action in list(interface.commands.items())[:20]:
            note_content += f"| {cmd} | {action} |\n"
        
        note_content += f"""
### Mind Map Links
- [[App Categories]]
- [[All Apps]]
- [[Accessibility Features]]

---
*Generated by VA21 Accessibility System on {interface.created_at}*
"""
        
        note_file = os.path.join(app_dir, f"{interface.app_name}.md")
        with open(note_file, 'w') as f:
            f.write(note_content)
    
    def _update_mindmap(self, interface: AppZorkInterface):
        """Update the mind map with the new app."""
        mindmap_file = os.path.join(self.mindmaps_path, "apps_mindmap.md")
        
        # Load existing or create new
        if os.path.exists(mindmap_file):
            with open(mindmap_file, 'r') as f:
                content = f.read()
        else:
            content = """# VA21 Apps Mind Map

## Categories
"""
        
        # Add app link if not present
        app_link = f"- [[{interface.app_name}]]"
        if app_link not in content:
            # Find or create category section
            category = interface.app_description.split(' - ')[0] if ' - ' in interface.app_description else 'Other'
            category_header = f"### {category}"
            
            if category_header in content:
                # Add under existing category
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == category_header:
                        lines.insert(i + 1, app_link)
                        break
                content = '\n'.join(lines)
            else:
                # Create new category
                content += f"\n{category_header}\n{app_link}\n"
        
        with open(mindmap_file, 'w') as f:
            f.write(content)
    
    def get_interface(self, app_id: str) -> Optional[AppZorkInterface]:
        """Retrieve an app interface from the knowledge base."""
        app_dir = os.path.join(self.apps_path, app_id)
        interface_file = os.path.join(app_dir, "interface.json")
        
        if not os.path.exists(interface_file):
            return None
        
        try:
            with open(interface_file, 'r') as f:
                data = json.load(f)
            return self._dict_to_interface(data)
        except Exception:
            return None
    
    def _dict_to_interface(self, data: Dict) -> AppZorkInterface:
        """Convert dictionary to interface object."""
        rooms = {}
        for room_id, room_data in data.get('rooms', {}).items():
            rooms[room_id] = ZorkRoom(
                room_id=room_data['room_id'],
                name=room_data['name'],
                description=room_data['description'],
                long_description=room_data['long_description'],
                exits=room_data['exits'],
                items=room_data['items'],
                ui_mapping=room_data['ui_mapping'],
            )
        
        return AppZorkInterface(
            app_id=data['app_id'],
            app_name=data['app_name'],
            app_description=data['app_description'],
            rooms=rooms,
            items=data['items'],
            commands=data['commands'],
            welcome_message=data['welcome_message'],
            created_at=data['created_at'],
            version=data.get('version', '1.0'),
        )
    
    def get_interface_by_name(self, app_name: str) -> Optional[AppZorkInterface]:
        """Find interface by app name."""
        for app_id, info in self.app_index.items():
            if info['app_name'].lower() == app_name.lower():
                return self.get_interface(app_id)
        return None
    
    def search_commands(self, query: str) -> List[Tuple[str, str, str]]:
        """Search for commands across all apps."""
        results = []
        query_lower = query.lower()
        
        for app_id in self.app_index:
            interface = self.get_interface(app_id)
            if interface:
                for cmd, action in interface.commands.items():
                    if query_lower in cmd.lower() or query_lower in action.lower():
                        results.append((interface.app_name, cmd, action))
        
        return results
    
    def list_apps(self) -> List[Dict]:
        """List all apps in the knowledge base."""
        return [
            {'app_id': app_id, **info}
            for app_id, info in self.app_index.items()
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# APP ZORK MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class AppZorkManager:
    """
    Main manager for creating and using Zork interfaces for apps.
    
    Called when:
    1. An app is first installed
    2. An app is launched by accessibility user
    3. User asks to interact with an app
    """
    
    def __init__(self, knowledge_base: Optional[AccessibilityKnowledgeBase] = None):
        self.analyzer = AppAnalyzer()
        self.generator = ZorkInterfaceGenerator()
        self.knowledge_base = knowledge_base or AccessibilityKnowledgeBase()
    
    def register_app(self, app_name: str, desktop_file: Optional[str] = None) -> AppZorkInterface:
        """
        Register an app and create its Zork interface.
        Called when app is installed or first accessed.
        """
        # Check if already registered
        existing = self.knowledge_base.get_interface_by_name(app_name)
        if existing:
            return existing
        
        # Analyze the app
        analysis = self.analyzer.analyze_app(app_name, desktop_file)
        
        # Generate Zork interface
        interface = self.generator.generate_interface(analysis)
        
        # Store in knowledge base
        self.knowledge_base.store_interface(interface)
        
        return interface
    
    def get_app_interface(self, app_name: str) -> Optional[AppZorkInterface]:
        """Get or create interface for an app."""
        interface = self.knowledge_base.get_interface_by_name(app_name)
        if not interface:
            interface = self.register_app(app_name)
        return interface
    
    def process_command(self, app_name: str, command: str) -> Dict[str, Any]:
        """
        Process a command for an app through its Zork interface.
        
        Returns action to execute and narrative response.
        """
        interface = self.get_app_interface(app_name)
        if not interface:
            return {
                'success': False,
                'response': f"I don't have an interface for {app_name} yet. Let me analyze it.",
                'action': None
            }
        
        # Parse command
        cmd_lower = command.lower().strip()
        
        # Check for direct command match
        if cmd_lower in interface.commands:
            action = interface.commands[cmd_lower]
            narrative = interface.items.get(action, f"Executing {action}...")
            return {
                'success': True,
                'response': narrative,
                'action': action,
                'app': app_name
            }
        
        # Check for partial matches
        for cmd, action in interface.commands.items():
            if cmd in cmd_lower or cmd_lower in cmd:
                narrative = interface.items.get(action, f"Executing {action}...")
                return {
                    'success': True,
                    'response': narrative,
                    'action': action,
                    'app': app_name
                }
        
        # No match found
        return {
            'success': False,
            'response': f"I'm not sure how to '{command}' in {app_name}. What would you like to do?",
            'action': None,
            'available_commands': list(interface.commands.keys())[:10]
        }
    
    def describe_app(self, app_name: str) -> str:
        """Get a Zork-style description of an app."""
        interface = self.get_app_interface(app_name)
        if not interface:
            return f"I don't know about {app_name} yet."
        
        # Get main room
        main_room = interface.rooms.get('main') or list(interface.rooms.values())[0]
        
        description = f"""
{interface.welcome_message}

{main_room.long_description}

Available actions: {', '.join(main_room.items)}

What would you like to do?
"""
        return description


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the app Zork interface generator."""
    print("=" * 60)
    print("VA21 OS - App Zork Interface Generator Test")
    print("=" * 60)
    
    manager = AppZorkManager()
    
    # Test with some apps
    test_apps = ['firefox', 'gedit', 'nautilus', 'vlc', 'gimp']
    
    for app_name in test_apps:
        print(f"\n\n{'='*60}")
        print(f"Generating interface for: {app_name}")
        print('='*60)
        
        interface = manager.register_app(app_name)
        print(f"App ID: {interface.app_id}")
        print(f"Description: {interface.app_description}")
        print(f"Rooms: {list(interface.rooms.keys())}")
        print(f"Commands: {list(interface.commands.keys())[:10]}...")
        print(f"\nWelcome Message:\n{interface.welcome_message}")
    
    # Test command processing
    print("\n\n" + "="*60)
    print("Testing Command Processing")
    print("="*60)
    
    test_commands = [
        ('firefox', 'search for something'),
        ('gedit', 'save my work'),
        ('nautilus', 'create a new folder'),
        ('vlc', 'play'),
    ]
    
    for app, cmd in test_commands:
        result = manager.process_command(app, cmd)
        print(f"\n[{app}] '{cmd}':")
        print(f"  Response: {result['response']}")
        print(f"  Action: {result.get('action')}")


if __name__ == "__main__":
    main()
