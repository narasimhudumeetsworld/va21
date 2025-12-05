#!/usr/bin/env python3
"""
VA21 OS - Unified App Knowledge System
=======================================

🙏 OM VINAYAKA - UNIFIED FARA + ZORK KNOWLEDGE SYSTEM 🙏

This module unifies the FARA compatibility layer and Zork UX generator
to work together seamlessly. All app knowledge is stored in a unified
Obsidian knowledge base with mind maps and LangChain integration.

Features:
1. Unified App Profile: Combines FARA and Zork interfaces for each app
2. Obsidian Knowledge Base: All menus, interactions, app layers saved
3. Mind Maps: Visual representation of app capabilities
4. LangChain Integration: Semantic search and intelligent retrieval
5. Om Vinayaka Integration: Enables dynamic clarifying questions

Every App Profile Contains:
- FARA Profile: Voice commands, keyboard shortcuts, automation
- Zork Interface: Text adventure descriptions, narratives
- UI Elements: All menus, buttons, text fields, interactions
- Mind Map: Visual representation of app structure
- LangChain Embeddings: For semantic search

Om Vinayaka - May obstacles be removed from app understanding.
Making EVERY application fully accessible and intelligently controllable.

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav
"""

import os
import re
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

UNIFIED_KNOWLEDGE_VERSION = "1.0.0"
DEFAULT_UNIFIED_KB_PATH = os.path.expanduser("~/.va21/unified_app_knowledge")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AppMenu:
    """A menu in an application."""
    menu_id: str
    menu_name: str
    menu_items: List[Dict] = field(default_factory=list)
    keyboard_shortcut: Optional[str] = None
    description: str = ""


@dataclass
class AppInteraction:
    """An interaction pattern in an application."""
    interaction_id: str
    interaction_type: str  # click, type, select, drag, etc.
    target_element: str
    description: str
    voice_command: Optional[str] = None
    result: str = ""


@dataclass
class AppLayer:
    """A layer/view within an application."""
    layer_id: str
    layer_name: str
    description: str
    elements: List[Dict] = field(default_factory=list)
    menus: List[str] = field(default_factory=list)  # Menu IDs
    interactions: List[str] = field(default_factory=list)  # Interaction IDs
    zork_description: str = ""


@dataclass
class UnifiedAppProfile:
    """
    Unified profile combining FARA and Zork for an application.
    
    This is the master profile that Om Vinayaka AI uses to understand
    and control any application.
    """
    # Basic Info
    profile_id: str
    app_name: str
    app_executable: str
    app_category: str
    
    # FARA Profile Data
    fara_profile_id: Optional[str] = None
    voice_commands: Dict[str, str] = field(default_factory=dict)
    keyboard_shortcuts: Dict[str, str] = field(default_factory=dict)
    automation_patterns: Dict[str, str] = field(default_factory=dict)
    
    # Zork Interface Data
    zork_interface_id: Optional[str] = None
    zork_welcome: str = ""
    zork_rooms: Dict[str, str] = field(default_factory=dict)
    zork_items: Dict[str, str] = field(default_factory=dict)
    zork_actions: Dict[str, str] = field(default_factory=dict)
    
    # Detailed UI Structure
    menus: List[Dict] = field(default_factory=list)
    interactions: List[Dict] = field(default_factory=list)
    layers: List[Dict] = field(default_factory=list)
    ui_elements: List[Dict] = field(default_factory=list)
    
    # Knowledge Base
    obsidian_note_path: Optional[str] = None
    mind_map_path: Optional[str] = None
    langchain_embeddings_path: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    
    # Om Vinayaka Integration
    om_vinayaka_enabled: bool = True
    clarifying_questions: List[str] = field(default_factory=list)
    usage_tips: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════════

class UnifiedAppKnowledgeBase:
    """
    Unified Knowledge Base for FARA + Zork App Profiles.
    
    Stores all app knowledge in Obsidian-compatible format with:
    - Markdown notes with YAML frontmatter
    - Mind maps (Mermaid diagrams)
    - Wiki-style [[links]] between apps and concepts
    - LangChain-compatible structure for semantic search
    """
    
    def __init__(self, kb_path: str = None):
        self.kb_path = kb_path or DEFAULT_UNIFIED_KB_PATH
        
        # Create directory structure
        self.profiles_path = os.path.join(self.kb_path, "profiles")
        self.mindmaps_path = os.path.join(self.kb_path, "mindmaps")
        self.menus_path = os.path.join(self.kb_path, "menus")
        self.interactions_path = os.path.join(self.kb_path, "interactions")
        self.layers_path = os.path.join(self.kb_path, "layers")
        self.embeddings_path = os.path.join(self.kb_path, "embeddings")
        
        for path in [self.profiles_path, self.mindmaps_path, self.menus_path,
                     self.interactions_path, self.layers_path, self.embeddings_path]:
            os.makedirs(path, exist_ok=True)
        
        # In-memory index
        self.profiles: Dict[str, UnifiedAppProfile] = {}
        self._load_index()
        
        print(f"[UnifiedKB] Knowledge base initialized at {self.kb_path}")
    
    def _load_index(self):
        """Load profile index from disk."""
        index_file = os.path.join(self.kb_path, "_unified_index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    for pid, pdata in data.get('profiles', {}).items():
                        self.profiles[pid] = UnifiedAppProfile(**pdata)
            except Exception as e:
                print(f"[UnifiedKB] Error loading index: {e}")
    
    def _save_index(self):
        """Save profile index to disk."""
        index_file = os.path.join(self.kb_path, "_unified_index.json")
        index_data = {
            'profiles': {pid: asdict(p) for pid, p in self.profiles.items()},
            'updated_at': datetime.now().isoformat(),
            'version': UNIFIED_KNOWLEDGE_VERSION
        }
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def save_unified_profile(self, profile: UnifiedAppProfile):
        """
        Save a unified app profile to the knowledge base.
        
        Creates:
        1. JSON profile data
        2. Obsidian markdown note
        3. Mind map
        4. Individual menu/interaction/layer notes
        """
        # Save to memory
        self.profiles[profile.profile_id] = profile
        profile.updated_at = datetime.now().isoformat()
        
        # Save JSON
        json_path = os.path.join(self.profiles_path, f"{profile.profile_id}.json")
        with open(json_path, 'w') as f:
            json.dump(asdict(profile), f, indent=2)
        
        # Save Obsidian note
        note_path = self._save_obsidian_note(profile)
        profile.obsidian_note_path = note_path
        
        # Save mind map
        mindmap_path = self._save_mind_map(profile)
        profile.mind_map_path = mindmap_path
        
        # Save individual components
        self._save_menus(profile)
        self._save_interactions(profile)
        self._save_layers(profile)
        
        # Update index
        self._save_index()
        
        return note_path
    
    def _save_obsidian_note(self, profile: UnifiedAppProfile) -> str:
        """Save main profile as Obsidian markdown note."""
        note_path = os.path.join(self.profiles_path, f"{profile.app_name.lower().replace(' ', '_')}.md")
        
        # Build voice commands list
        voice_cmds = "\n".join([f"- **\"{cmd}\"** → {action}" 
                                for cmd, action in list(profile.voice_commands.items())[:20]])
        
        # Build keyboard shortcuts list
        shortcuts = "\n".join([f"- **{shortcut}** → {action}"
                               for shortcut, action in list(profile.keyboard_shortcuts.items())[:15]])
        
        # Build menus list with links
        menus_links = "\n".join([f"- [[Menu - {m.get('menu_name', 'Unknown')}]]" 
                                 for m in profile.menus[:10]])
        
        # Build layers list with links
        layers_links = "\n".join([f"- [[Layer - {l.get('layer_name', 'Unknown')}]]"
                                  for l in profile.layers[:10]])
        
        # Build clarifying questions
        questions = "\n".join([f"- {q}" for q in profile.clarifying_questions[:10]])
        
        # Build usage tips
        tips = "\n".join([f"- {t}" for t in profile.usage_tips[:10]])
        
        content = f"""---
type: unified_app_profile
profile_id: {profile.profile_id}
app_name: {profile.app_name}
app_category: {profile.app_category}
fara_profile_id: {profile.fara_profile_id or 'auto-generated'}
zork_interface_id: {profile.zork_interface_id or 'auto-generated'}
created_at: {profile.created_at}
updated_at: {profile.updated_at}
version: {profile.version}
tags:
  - app_profile
  - unified
  - {profile.app_category}
  - om_vinayaka
---

# 🎮 {profile.app_name} - Unified App Profile

## Overview
- **Category**: [[{profile.app_category}]]
- **Executable**: `{profile.app_executable}`
- **Om Vinayaka Enabled**: {'✅ Yes' if profile.om_vinayaka_enabled else '❌ No'}

## 🗣️ Voice Commands
Om Vinayaka AI can control this app with these voice commands:

{voice_cmds if voice_cmds else "No voice commands configured yet."}

## ⌨️ Keyboard Shortcuts
{shortcuts if shortcuts else "No shortcuts mapped yet."}

## 📋 Menus
{menus_links if menus_links else "No menus detected yet."}

## 🎭 App Layers/Views
{layers_links if layers_links else "No layers detected yet."}

## 🎪 Zork Interface

### Welcome Message
> {profile.zork_welcome or "Welcome to " + profile.app_name + "!"}

### Available Rooms
```
{json.dumps(profile.zork_rooms, indent=2) if profile.zork_rooms else "{}"}
```

### Available Actions
```
{json.dumps(profile.zork_actions, indent=2) if profile.zork_actions else "{}"}
```

## 🤔 Clarifying Questions
Om Vinayaka AI may ask these questions to help you:

{questions if questions else "- What would you like to do in this app?"}

## 💡 Usage Tips
{tips if tips else "- Try saying 'help' for available commands"}

## 🧠 Mind Map
![[{profile.app_name.lower().replace(' ', '_')}_mindmap]]

## Related
- [[FARA Overview]]
- [[Zork Interface Guide]]
- [[Om Vinayaka AI]]
- [[All Apps]]

---
*Generated by Om Vinayaka Unified Knowledge System v{UNIFIED_KNOWLEDGE_VERSION}*
"""
        
        with open(note_path, 'w') as f:
            f.write(content)
        
        return note_path
    
    def _save_mind_map(self, profile: UnifiedAppProfile) -> str:
        """Save mind map for the app profile."""
        mindmap_path = os.path.join(self.mindmaps_path, 
                                     f"{profile.app_name.lower().replace(' ', '_')}_mindmap.md")
        
        # Build menu nodes
        menu_nodes = "\n".join([f"      {m.get('menu_name', 'Menu')}" 
                                for m in profile.menus[:8]])
        
        # Build voice command nodes
        voice_nodes = "\n".join([f"      {cmd[:20]}" 
                                 for cmd in list(profile.voice_commands.keys())[:8]])
        
        # Build layer nodes
        layer_nodes = "\n".join([f"      {l.get('layer_name', 'Layer')}"
                                 for l in profile.layers[:8]])
        
        content = f"""---
type: mindmap
app_name: {profile.app_name}
created_at: {datetime.now().isoformat()}
tags:
  - mindmap
  - {profile.app_category}
---

# 🧠 {profile.app_name} Mind Map

## Visual Structure

```mermaid
mindmap
  root(({profile.app_name}))
    FARA Layer
      Voice Commands
{voice_nodes or "        (none)"}
      Keyboard Shortcuts
        Ctrl+S Save
        Ctrl+O Open
      Automation
        Actions
        Patterns
    Zork Interface
      Rooms
        Main View
        Settings
      Items
        Files
        Tools
      Actions
        look
        go
        take
    Menus
{menu_nodes or "      (detecting...)"}
    Layers
{layer_nodes or "      Main View"}
    UI Elements
      Buttons
      Text Fields
      Lists
```

## Knowledge Graph

```mermaid
graph TD
    A[{profile.app_name}] --> B[FARA Profile]
    A --> C[Zork Interface]
    A --> D[UI Structure]
    
    B --> B1[Voice Commands]
    B --> B2[Shortcuts]
    B --> B3[Automation]
    
    C --> C1[Rooms]
    C --> C2[Items]
    C --> C3[Actions]
    
    D --> D1[Menus]
    D --> D2[Layers]
    D --> D3[Elements]
    
    B1 --> E[Om Vinayaka AI]
    C1 --> E
    D1 --> E
    
    E --> F[Dynamic Interaction]
    E --> G[Clarifying Questions]
    E --> H[User Help]
```

## Quick Links
- [[{profile.app_name.lower().replace(' ', '_')}|Full Profile]]
- [[FARA Overview]]
- [[Om Vinayaka AI]]

---
*Generated by Om Vinayaka Unified Knowledge System*
"""
        
        with open(mindmap_path, 'w') as f:
            f.write(content)
        
        return mindmap_path
    
    def _save_menus(self, profile: UnifiedAppProfile):
        """Save individual menu notes."""
        for menu in profile.menus:
            menu_name = menu.get('menu_name', 'Unknown')
            safe_name = re.sub(r'[^\w\s-]', '', menu_name).strip().replace(' ', '_')
            menu_path = os.path.join(self.menus_path, f"menu_{safe_name}_{profile.profile_id[:6]}.md")
            
            items_list = "\n".join([f"- {item.get('name', 'Item')}: {item.get('action', '')}"
                                    for item in menu.get('menu_items', [])])
            
            content = f"""---
type: app_menu
app_name: {profile.app_name}
menu_name: {menu_name}
tags:
  - menu
  - {profile.app_category}
---

# 📋 Menu: {menu_name}

**App**: [[{profile.app_name.lower().replace(' ', '_')}|{profile.app_name}]]

## Menu Items
{items_list or "No items detected"}

## Keyboard Shortcut
{menu.get('keyboard_shortcut', 'None')}

## Description
{menu.get('description', 'Standard application menu')}

---
*Part of {profile.app_name} knowledge base*
"""
            with open(menu_path, 'w') as f:
                f.write(content)
    
    def _save_interactions(self, profile: UnifiedAppProfile):
        """Save individual interaction notes."""
        for interaction in profile.interactions:
            int_id = interaction.get('interaction_id', 'unknown')
            int_path = os.path.join(self.interactions_path, 
                                     f"interaction_{int_id}_{profile.profile_id[:6]}.md")
            
            content = f"""---
type: app_interaction
app_name: {profile.app_name}
interaction_type: {interaction.get('interaction_type', 'unknown')}
tags:
  - interaction
  - {profile.app_category}
---

# 🎯 Interaction: {interaction.get('description', 'Unknown')}

**App**: [[{profile.app_name.lower().replace(' ', '_')}|{profile.app_name}]]

## Details
- **Type**: {interaction.get('interaction_type', 'unknown')}
- **Target**: {interaction.get('target_element', 'unknown')}
- **Voice Command**: "{interaction.get('voice_command', 'none')}"

## Expected Result
{interaction.get('result', 'Action executed')}

---
*Part of {profile.app_name} knowledge base*
"""
            with open(int_path, 'w') as f:
                f.write(content)
    
    def _save_layers(self, profile: UnifiedAppProfile):
        """Save individual layer/view notes."""
        for layer in profile.layers:
            layer_name = layer.get('layer_name', 'Unknown')
            safe_name = re.sub(r'[^\w\s-]', '', layer_name).strip().replace(' ', '_')
            layer_path = os.path.join(self.layers_path, 
                                       f"layer_{safe_name}_{profile.profile_id[:6]}.md")
            
            elements_list = "\n".join([f"- {el.get('type', 'element')}: {el.get('name', 'unknown')}"
                                        for el in layer.get('elements', [])])
            
            content = f"""---
type: app_layer
app_name: {profile.app_name}
layer_name: {layer_name}
tags:
  - layer
  - {profile.app_category}
---

# 🎭 Layer: {layer_name}

**App**: [[{profile.app_name.lower().replace(' ', '_')}|{profile.app_name}]]

## Description
{layer.get('description', 'Application view/layer')}

## Zork Description
> {layer.get('zork_description', f'You are in the {layer_name} area.')}

## UI Elements
{elements_list or "No elements detected"}

## Available Menus
{', '.join([f'[[Menu - {m}]]' for m in layer.get('menus', [])])}

## Interactions
{', '.join([f'[[Interaction - {i}]]' for i in layer.get('interactions', [])])}

---
*Part of {profile.app_name} knowledge base*
"""
            with open(layer_path, 'w') as f:
                f.write(content)
    
    def get_profile(self, app_name: str) -> Optional[UnifiedAppProfile]:
        """Get unified profile by app name."""
        for profile in self.profiles.values():
            if profile.app_name.lower() == app_name.lower():
                return profile
        
        # Fuzzy match
        app_lower = app_name.lower()
        for profile in self.profiles.values():
            if app_lower in profile.app_name.lower():
                return profile
        
        return None
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """
        Search the knowledge base for relevant information.
        
        This is LangChain-compatible for semantic search.
        """
        results = []
        query_lower = query.lower()
        
        for profile in self.profiles.values():
            score = 0
            
            # Check app name
            if query_lower in profile.app_name.lower():
                score += 10
            
            # Check voice commands
            for cmd in profile.voice_commands.keys():
                if query_lower in cmd.lower():
                    score += 5
            
            # Check category
            if query_lower in profile.app_category.lower():
                score += 3
            
            if score > 0:
                results.append({
                    'profile_id': profile.profile_id,
                    'app_name': profile.app_name,
                    'score': score,
                    'note_path': profile.obsidian_note_path
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def get_clarifying_questions(self, app_name: str, context: str = None) -> List[str]:
        """Get clarifying questions Om Vinayaka AI can ask about an app."""
        profile = self.get_profile(app_name)
        if not profile:
            return ["What application would you like to work with?"]
        
        questions = profile.clarifying_questions.copy()
        
        # Add context-aware questions
        if not questions:
            questions = [
                f"What would you like to do in {profile.app_name}?",
                f"Would you like to see available commands for {profile.app_name}?",
                f"Should I explain how {profile.app_name} works?",
            ]
        
        return questions


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED APP CREATOR
# ═══════════════════════════════════════════════════════════════════════════════

class UnifiedAppCreator:
    """
    Creates unified app profiles that combine FARA and Zork.
    
    When an app is installed:
    1. Creates FARA profile (voice commands, automation)
    2. Creates Zork interface (text adventure)
    3. Combines into unified profile
    4. Saves to Obsidian knowledge base
    5. Registers with Om Vinayaka AI
    """
    
    VERSION = UNIFIED_KNOWLEDGE_VERSION
    
    def __init__(self, kb_path: str = None):
        self.knowledge_base = UnifiedAppKnowledgeBase(kb_path)
        
        # Import FARA and Zork creators lazily
        self.fara_creator = None
        self.zork_manager = None
        
        # Om Vinayaka callback
        self._om_vinayaka_callback = None
        
        print(f"[UnifiedCreator] Initialized v{self.VERSION}")
    
    def set_om_vinayaka_callback(self, callback):
        """Set callback for Om Vinayaka AI integration."""
        self._om_vinayaka_callback = callback
    
    def set_fara_creator(self, fara_creator):
        """Set the FARA creator instance."""
        self.fara_creator = fara_creator
    
    def set_zork_manager(self, zork_manager):
        """Set the Zork manager instance."""
        self.zork_manager = zork_manager
    
    def create_unified_profile(self, app_name: str, 
                               app_executable: str = None,
                               app_category: str = None) -> UnifiedAppProfile:
        """
        Create a unified app profile combining FARA and Zork.
        
        This is the main method called when an app is installed.
        """
        print(f"[UnifiedCreator] Creating unified profile for: {app_name}")
        
        # Generate profile ID
        profile_id = hashlib.sha256(app_name.lower().encode()).hexdigest()[:12]
        
        # Get FARA profile
        fara_data = self._get_fara_data(app_name, app_executable, app_category)
        
        # Get Zork interface
        zork_data = self._get_zork_data(app_name, app_category)
        
        # Detect menus and UI structure
        menus = self._detect_menus(app_name, app_category)
        layers = self._detect_layers(app_name, app_category)
        interactions = self._detect_interactions(app_name, app_category)
        ui_elements = self._detect_ui_elements(app_name, app_category)
        
        # Generate clarifying questions
        clarifying_questions = self._generate_clarifying_questions(app_name, app_category)
        
        # Generate usage tips
        usage_tips = self._generate_usage_tips(app_name, app_category)
        
        # Create unified profile
        profile = UnifiedAppProfile(
            profile_id=profile_id,
            app_name=app_name,
            app_executable=app_executable or app_name.lower(),
            app_category=app_category or 'other',
            
            # FARA data
            fara_profile_id=fara_data.get('profile_id'),
            voice_commands=fara_data.get('voice_commands', {}),
            keyboard_shortcuts=fara_data.get('keyboard_shortcuts', {}),
            automation_patterns=fara_data.get('automation_patterns', {}),
            
            # Zork data
            zork_interface_id=zork_data.get('interface_id'),
            zork_welcome=zork_data.get('welcome', f"Welcome to {app_name}!"),
            zork_rooms=zork_data.get('rooms', {}),
            zork_items=zork_data.get('items', {}),
            zork_actions=zork_data.get('actions', {}),
            
            # UI Structure
            menus=menus,
            layers=layers,
            interactions=interactions,
            ui_elements=ui_elements,
            
            # Om Vinayaka integration
            clarifying_questions=clarifying_questions,
            usage_tips=usage_tips,
            om_vinayaka_enabled=True
        )
        
        # Save to knowledge base
        note_path = self.knowledge_base.save_unified_profile(profile)
        
        # Notify Om Vinayaka AI
        if self._om_vinayaka_callback:
            self._om_vinayaka_callback({
                'event': 'unified_profile_created',
                'app_name': app_name,
                'profile_id': profile_id,
                'voice_commands': len(profile.voice_commands),
                'menus': len(menus),
                'layers': len(layers),
                'note_path': note_path
            })
        
        print(f"[UnifiedCreator] Profile created: {profile_id}")
        print(f"[UnifiedCreator]   - Voice commands: {len(profile.voice_commands)}")
        print(f"[UnifiedCreator]   - Menus: {len(menus)}")
        print(f"[UnifiedCreator]   - Layers: {len(layers)}")
        print(f"[UnifiedCreator]   - Knowledge base: {note_path}")
        
        return profile
    
    def _get_fara_data(self, app_name: str, executable: str, category: str) -> Dict:
        """Get FARA profile data for the app."""
        if self.fara_creator:
            try:
                profile = self.fara_creator.create_profile_for_app(
                    app_name=app_name,
                    executable=executable,
                    category=category
                )
                return {
                    'profile_id': profile.profile_id,
                    'voice_commands': profile.voice_commands,
                    'keyboard_shortcuts': {
                        a.get('action_id'): a.get('keyboard_shortcut')
                        for a in profile.actions if a.get('keyboard_shortcut')
                    },
                    'automation_patterns': profile.automation_patterns
                }
            except Exception as e:
                print(f"[UnifiedCreator] FARA error: {e}")
        
        # Generate default FARA data
        return self._generate_default_fara(app_name, category)
    
    def _get_zork_data(self, app_name: str, category: str) -> Dict:
        """Get Zork interface data for the app."""
        if self.zork_manager:
            try:
                interface = self.zork_manager.get_or_create_interface(app_name)
                return {
                    'interface_id': getattr(interface, 'interface_id', None),
                    'welcome': getattr(interface, 'welcome_text', f"Welcome to {app_name}!"),
                    'rooms': getattr(interface, 'rooms', {}),
                    'items': getattr(interface, 'items', {}),
                    'actions': getattr(interface, 'actions', {})
                }
            except Exception as e:
                print(f"[UnifiedCreator] Zork error: {e}")
        
        # Generate default Zork data
        return self._generate_default_zork(app_name, category)
    
    def _generate_default_fara(self, app_name: str, category: str) -> Dict:
        """Generate default FARA data."""
        base_commands = {
            'save': 'save',
            'open': 'open',
            'close': 'close',
            'help': 'help',
            'undo': 'undo',
        }
        
        base_shortcuts = {
            'save': 'Ctrl+S',
            'open': 'Ctrl+O',
            'close': 'Alt+F4',
            'undo': 'Ctrl+Z',
        }
        
        return {
            'profile_id': hashlib.sha256(app_name.encode()).hexdigest()[:8],
            'voice_commands': base_commands,
            'keyboard_shortcuts': base_shortcuts,
            'automation_patterns': {}
        }
    
    def _generate_default_zork(self, app_name: str, category: str) -> Dict:
        """Generate default Zork interface data."""
        return {
            'interface_id': hashlib.sha256(app_name.encode()).hexdigest()[:8],
            'welcome': f"""
You find yourself at the entrance of {app_name}.

The interface before you presents various options and tools.
A warm glow emanates from the screen, inviting you to explore.

What would you like to do?
""",
            'rooms': {
                'main': f"The main area of {app_name}",
                'settings': "The settings sanctum",
                'help': "The hall of knowledge"
            },
            'items': {},
            'actions': {
                'look': 'Examine your surroundings',
                'help': 'Get assistance',
                'exit': 'Leave this area'
            }
        }
    
    def _detect_menus(self, app_name: str, category: str) -> List[Dict]:
        """Detect menus in the application."""
        # Common menus based on category
        common_menus = [
            {'menu_id': 'file', 'menu_name': 'File', 'keyboard_shortcut': 'Alt+F',
             'menu_items': [
                 {'name': 'New', 'action': 'new', 'shortcut': 'Ctrl+N'},
                 {'name': 'Open', 'action': 'open', 'shortcut': 'Ctrl+O'},
                 {'name': 'Save', 'action': 'save', 'shortcut': 'Ctrl+S'},
                 {'name': 'Close', 'action': 'close', 'shortcut': 'Ctrl+W'},
             ]},
            {'menu_id': 'edit', 'menu_name': 'Edit', 'keyboard_shortcut': 'Alt+E',
             'menu_items': [
                 {'name': 'Undo', 'action': 'undo', 'shortcut': 'Ctrl+Z'},
                 {'name': 'Redo', 'action': 'redo', 'shortcut': 'Ctrl+Y'},
                 {'name': 'Cut', 'action': 'cut', 'shortcut': 'Ctrl+X'},
                 {'name': 'Copy', 'action': 'copy', 'shortcut': 'Ctrl+C'},
                 {'name': 'Paste', 'action': 'paste', 'shortcut': 'Ctrl+V'},
             ]},
            {'menu_id': 'view', 'menu_name': 'View', 'keyboard_shortcut': 'Alt+V',
             'menu_items': []},
            {'menu_id': 'help', 'menu_name': 'Help', 'keyboard_shortcut': 'Alt+H',
             'menu_items': [
                 {'name': 'About', 'action': 'about'},
                 {'name': 'Documentation', 'action': 'docs'},
             ]},
        ]
        
        return common_menus
    
    def _detect_layers(self, app_name: str, category: str) -> List[Dict]:
        """Detect layers/views in the application."""
        return [
            {
                'layer_id': 'main',
                'layer_name': 'Main View',
                'description': f'The primary interface of {app_name}',
                'zork_description': f'You are in the main area of {app_name}. Various tools and options surround you.',
                'elements': [],
                'menus': ['file', 'edit', 'view', 'help'],
                'interactions': []
            },
            {
                'layer_id': 'settings',
                'layer_name': 'Settings',
                'description': 'Application settings and preferences',
                'zork_description': 'You enter the settings sanctum. Configurations await your adjustment.',
                'elements': [],
                'menus': [],
                'interactions': []
            }
        ]
    
    def _detect_interactions(self, app_name: str, category: str) -> List[Dict]:
        """Detect interactions in the application."""
        return [
            {
                'interaction_id': 'save',
                'interaction_type': 'keyboard',
                'target_element': 'document',
                'description': 'Save current work',
                'voice_command': 'save',
                'result': 'Document saved'
            },
            {
                'interaction_id': 'open',
                'interaction_type': 'dialog',
                'target_element': 'file_dialog',
                'description': 'Open a file',
                'voice_command': 'open file',
                'result': 'File dialog opened'
            }
        ]
    
    def _detect_ui_elements(self, app_name: str, category: str) -> List[Dict]:
        """Detect UI elements in the application."""
        return [
            {'type': 'menubar', 'name': 'Menu Bar', 'location': 'top'},
            {'type': 'toolbar', 'name': 'Main Toolbar', 'location': 'top'},
            {'type': 'content_area', 'name': 'Content Area', 'location': 'center'},
            {'type': 'statusbar', 'name': 'Status Bar', 'location': 'bottom'},
        ]
    
    def _generate_clarifying_questions(self, app_name: str, category: str) -> List[str]:
        """Generate clarifying questions for Om Vinayaka AI."""
        base_questions = [
            f"What would you like to do in {app_name}?",
            f"Would you like me to explain the features of {app_name}?",
            "Should I show you the available voice commands?",
            "Do you need help finding something specific?",
            "Would you like to create something new or open an existing file?",
        ]
        
        category_questions = {
            'text_editor': [
                "What would you like to write or edit?",
                "Should I help you format your document?",
            ],
            'web_browser': [
                "What website would you like to visit?",
                "Would you like me to search for something?",
            ],
            'file_manager': [
                "What files are you looking for?",
                "Should I help you organize your folders?",
            ],
            'ide': [
                "What programming language are you working with?",
                "Would you like me to help debug your code?",
            ],
        }
        
        if category and category in category_questions:
            base_questions.extend(category_questions[category])
        
        return base_questions
    
    def _generate_usage_tips(self, app_name: str, category: str) -> List[str]:
        """Generate usage tips for the app."""
        tips = [
            f"Hold Super key and say 'help' to see available commands",
            f"Say 'look around' to get a description of the current view",
            f"Ask 'what can I do here?' to see available actions",
            f"Use voice commands like 'save', 'open', 'close' for quick actions",
        ]
        
        return tips
    
    def get_profile(self, app_name: str) -> Optional[UnifiedAppProfile]:
        """Get unified profile for an app."""
        return self.knowledge_base.get_profile(app_name)
    
    def get_status(self) -> Dict:
        """Get creator status."""
        return {
            'version': self.VERSION,
            'profiles_count': len(self.knowledge_base.profiles),
            'knowledge_base_path': self.knowledge_base.kb_path
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_unified_creator_instance = None


def get_unified_creator(kb_path: str = None) -> UnifiedAppCreator:
    """Get or create the Unified App Creator singleton."""
    global _unified_creator_instance
    
    if _unified_creator_instance is None:
        _unified_creator_instance = UnifiedAppCreator(kb_path)
    
    return _unified_creator_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the Unified App Knowledge System."""
    print("=" * 70)
    print("VA21 OS - Unified App Knowledge System Test")
    print("=" * 70)
    
    # Initialize
    creator = get_unified_creator()
    
    # Create test profiles
    test_apps = [
        ("Firefox", "firefox", "web_browser"),
        ("VS Code", "code", "ide"),
        ("GNOME Files", "nautilus", "file_manager"),
    ]
    
    print("\n--- Creating unified profiles ---\n")
    
    for app_name, executable, category in test_apps:
        profile = creator.create_unified_profile(app_name, executable, category)
        print(f"✓ Created: {app_name}")
    
    # Search knowledge base
    print("\n--- Knowledge Base Search ---\n")
    results = creator.knowledge_base.search_knowledge("browser")
    for r in results:
        print(f"Found: {r['app_name']} (score: {r['score']})")
    
    # Get clarifying questions
    print("\n--- Clarifying Questions ---\n")
    questions = creator.knowledge_base.get_clarifying_questions("Firefox")
    for q in questions[:3]:
        print(f"- {q}")
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
