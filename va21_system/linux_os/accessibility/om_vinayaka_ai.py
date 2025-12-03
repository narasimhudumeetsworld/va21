#!/usr/bin/env python3
"""
VA21 OS - Om Vinayaka Accessibility Knowledge Base AI
======================================================

The Om Vinayaka AI is the central accessibility intelligence system that:
- Automatically activates when accessibility and voice features are used
- Creates Zork-style UX for EVERY app when first installed
- Enables voice users to interact with ANY app in the full OS
- Asks clarifying questions to understand user intent
- Executes actions across the entire OS via the FARA layer
- Stores all app interfaces in a LangChain + Obsidian mind map knowledge base
- LEARNS from user interactions to get smarter over time!

This creates a unified, conversational accessibility experience where
every application can be controlled through natural language.

Architecture:
- Om Vinayaka AI: Central orchestrator for all accessibility features
- App Zork Generator: Creates Zork UX for each app automatically
- Accessibility Knowledge Base: LangChain + Obsidian with mind maps
- Voice Controller: System-wide voice input and output
- FARA Layer: Universal action execution across all apps
- Terminal Zork Adapter: Zork UX for CLI tools (Gemini CLI, Codex, Copilot CLI, etc.)
- Self-Learning Engine: Learns patterns, preferences, and improves over time

Self-Learning System:
- Learns common command patterns from user interactions
- Tracks user preferences for personalized experience
- Monitors app usage patterns to optimize suggestions
- Improves narratives based on what resonates with users
- Gets smarter with continued use!

NOTE: Guardian AI runs in a sandboxed Ollama in the kernel and is completely
isolated from this user-facing accessibility system.

Om Vinayaka - May obstacles be removed from your computing journey.
"""

import os
import sys
import json
import hashlib
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

OM_VINAYAKA_VERSION = "1.1.0"  # Updated with self-learning

# Knowledge base paths
DEFAULT_KNOWLEDGE_BASE_PATH = os.path.expanduser("~/.va21/accessibility_knowledge_base")
DEFAULT_MINDMAP_PATH = os.path.expanduser("~/.va21/accessibility_knowledge_base/mindmaps")

# CLI Tools that should get Zork interfaces
CLI_TOOLS_TO_WRAP = [
    "gemini",
    "codex", 
    "gh-copilot",
    "github-copilot-cli",
    "aider",
    "claude",
    "cursor",
    "continue",
    "cody",
]


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL ZORK ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CLIToolInterface:
    """Zork-style interface for a CLI tool."""
    tool_name: str
    tool_description: str
    available_commands: List[str]
    room_description: str
    items: Dict[str, str]
    narratives: Dict[str, str]
    created_at: str


class TerminalZorkAdapter:
    """
    Creates Zork-style accessibility interfaces for terminal/CLI tools.
    
    This enables voice users and accessibility users to interact with
    CLI tools like Gemini CLI, Codex, GitHub Copilot CLI, etc. using
    natural language through a Zork-like conversational interface.
    
    The adapter:
    1. Wraps CLI tool commands in narrative descriptions
    2. Translates natural language to CLI commands
    3. Presents output in accessible, conversational format
    4. Provides contextual help and clarification
    """
    
    def __init__(self, knowledge_base=None):
        self.knowledge_base = knowledge_base
        self.tool_interfaces: Dict[str, CLIToolInterface] = {}
        self._load_default_interfaces()
    
    def _load_default_interfaces(self):
        """Load default Zork interfaces for common CLI tools."""
        
        # Gemini CLI Interface
        self.tool_interfaces["gemini"] = CLIToolInterface(
            tool_name="Gemini CLI",
            tool_description="Google's Gemini AI assistant in the terminal",
            available_commands=["ask", "chat", "code", "explain", "help", "quit"],
            room_description="""You stand before the GEMINI ORACLE, a shimmering portal of AI wisdom.
The oracle awaits your questions with infinite patience, ready to assist
with any task - from coding challenges to creative writing.""",
            items={
                "question_scroll": "Ask the oracle any question",
                "code_wand": "Request code generation or analysis",
                "explanation_lens": "Get detailed explanations of concepts",
            },
            narratives={
                "ask": "The Gemini Oracle considers your question deeply...",
                "code": "The Oracle summons lines of code from the digital ether...",
                "explain": "The Oracle unfolds the mystery in clear terms...",
            },
            created_at=datetime.now().isoformat()
        )
        
        # GitHub Copilot CLI Interface
        self.tool_interfaces["gh-copilot"] = CLIToolInterface(
            tool_name="GitHub Copilot CLI",
            tool_description="AI-powered command-line assistant from GitHub",
            available_commands=["suggest", "explain", "help", "exit"],
            room_description="""You enter the COPILOT CHAMBER, where an AI companion hovers nearby.
The Copilot can suggest shell commands, explain complex operations,
and help you navigate the terminal with natural language.""",
            items={
                "suggestion_crystal": "Ask for command suggestions",
                "explain_tome": "Get explanations of commands",
                "shell_compass": "Navigate terminal operations",
            },
            narratives={
                "suggest": "The Copilot analyzes your intent and conjures a command...",
                "explain": "The Copilot illuminates the meaning of the command...",
            },
            created_at=datetime.now().isoformat()
        )
        
        # Codex/OpenAI CLI Interface
        self.tool_interfaces["codex"] = CLIToolInterface(
            tool_name="OpenAI Codex CLI",
            tool_description="OpenAI's code-focused AI assistant",
            available_commands=["generate", "complete", "edit", "explain", "help", "quit"],
            room_description="""You descend into the CODEX SANCTUM, walls lined with glowing code.
Ancient programming wisdom flows through crystalline conduits.
The Codex awaits your programming challenges.""",
            items={
                "generation_staff": "Generate new code from description",
                "completion_orb": "Complete partial code",
                "edit_chisel": "Edit and improve existing code",
            },
            narratives={
                "generate": "The Codex channels programming wisdom into new code...",
                "complete": "The Codex perceives your intent and completes the pattern...",
                "edit": "The Codex carefully reshapes the code...",
            },
            created_at=datetime.now().isoformat()
        )
        
        # Generic AI CLI Interface (for unknown tools)
        self.tool_interfaces["generic_ai_cli"] = CLIToolInterface(
            tool_name="AI Assistant CLI",
            tool_description="An AI assistant in the terminal",
            available_commands=["ask", "help", "quit"],
            room_description="""You encounter an AI ASSISTANT in the terminal realm.
It stands ready to help with your questions and tasks.""",
            items={
                "query_scroll": "Ask the assistant anything",
                "help_book": "Get usage instructions",
            },
            narratives={
                "ask": "The assistant processes your request...",
                "help": "The assistant provides guidance...",
            },
            created_at=datetime.now().isoformat()
        )
    
    def get_interface(self, tool_name: str) -> CLIToolInterface:
        """Get or create a Zork interface for a CLI tool."""
        tool_key = tool_name.lower().replace(" ", "-").replace("_", "-")
        
        # Check for exact match
        if tool_key in self.tool_interfaces:
            return self.tool_interfaces[tool_key]
        
        # Check for partial match
        for key, interface in self.tool_interfaces.items():
            if key in tool_key or tool_key in key:
                return interface
        
        # Return generic interface
        return self.tool_interfaces["generic_ai_cli"]
    
    def wrap_command(self, tool_name: str, command: str, output: str) -> str:
        """Wrap CLI tool output in Zork-style narrative."""
        interface = self.get_interface(tool_name)
        
        # Find matching narrative
        cmd_lower = command.lower()
        narrative = None
        for cmd, narr in interface.narratives.items():
            if cmd in cmd_lower:
                narrative = narr
                break
        
        if not narrative:
            narrative = f"The {interface.tool_name} responds..."
        
        wrapped = f"""
╔═══════════════════════════════════════════════════════════════════╗
║  {interface.tool_name.center(63)}║
╚═══════════════════════════════════════════════════════════════════╝

{narrative}

{'-' * 60}
{output}
{'-' * 60}

What would you like to do next? (say 'help' for options)
"""
        return wrapped
    
    def describe_tool(self, tool_name: str) -> str:
        """Get a Zork-style description of a CLI tool."""
        interface = self.get_interface(tool_name)
        
        items_desc = "\n".join([f"  • {name}: {desc}" 
                                for name, desc in interface.items.items()])
        commands_desc = ", ".join(interface.available_commands)
        
        return f"""
{interface.room_description}

Available tools:
{items_desc}

Commands you can use: {commands_desc}

How would you like to interact with {interface.tool_name}?
"""
    
    def translate_to_command(self, tool_name: str, natural_language: str) -> Optional[str]:
        """Translate natural language to CLI tool command."""
        interface = self.get_interface(tool_name)
        nl_lower = natural_language.lower()
        
        # Simple keyword matching for common intents
        intent_map = {
            "ask": ["ask", "question", "query", "what", "how", "why", "when", "where", "who"],
            "code": ["code", "program", "function", "write code", "generate code"],
            "explain": ["explain", "what does", "what is", "describe", "clarify"],
            "suggest": ["suggest", "recommend", "what should", "help me"],
            "help": ["help", "usage", "how to", "commands"],
            "quit": ["quit", "exit", "leave", "bye", "goodbye"],
        }
        
        for cmd, keywords in intent_map.items():
            if any(kw in nl_lower for kw in keywords):
                if cmd in interface.available_commands:
                    # Extract the actual query part
                    query = natural_language
                    for kw in keywords:
                        query = query.lower().replace(kw, "").strip()
                    
                    if cmd in ["ask", "code", "explain", "suggest"]:
                        return f"{cmd} {query}"
                    return cmd
        
        # Default: treat as a question
        if "ask" in interface.available_commands:
            return f"ask {natural_language}"
        
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# ACCESSIBILITY MIND MAP
# ═══════════════════════════════════════════════════════════════════════════════

class AccessibilityMindMap:
    """
    Obsidian-style mind map for accessibility knowledge.
    
    Stores and connects:
    - App Zork interfaces
    - User preferences
    - Learned interaction patterns
    - Accessibility feature connections
    """
    
    def __init__(self, mindmap_path: str = None):
        self.mindmap_path = mindmap_path or DEFAULT_MINDMAP_PATH
        os.makedirs(self.mindmap_path, exist_ok=True)
        
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        
        self._load_mindmap()
    
    def _load_mindmap(self):
        """Load existing mind map from disk."""
        index_file = os.path.join(self.mindmap_path, "mindmap_index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    self.nodes = data.get('nodes', {})
                    self.edges = data.get('edges', [])
            except Exception:
                pass
    
    def _save_mindmap(self):
        """Save mind map to disk."""
        index_file = os.path.join(self.mindmap_path, "mindmap_index.json")
        with open(index_file, 'w') as f:
            json.dump({
                'nodes': self.nodes,
                'edges': self.edges,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def add_app_node(self, app_id: str, app_name: str, category: str, 
                     zork_interface_id: str = None):
        """Add an application node to the mind map."""
        node_id = f"app_{app_id}"
        self.nodes[node_id] = {
            'type': 'application',
            'id': app_id,
            'name': app_name,
            'category': category,
            'zork_interface_id': zork_interface_id,
            'created_at': datetime.now().isoformat()
        }
        
        # Connect to category node
        category_node_id = f"category_{category}"
        if category_node_id not in self.nodes:
            self.nodes[category_node_id] = {
                'type': 'category',
                'name': category,
                'created_at': datetime.now().isoformat()
            }
        
        self.edges.append({
            'source': node_id,
            'target': category_node_id,
            'relationship': 'belongs_to'
        })
        
        self._save_mindmap()
        
        # Create Obsidian-style markdown note
        self._create_app_note(app_id, app_name, category)
    
    def _create_app_note(self, app_id: str, app_name: str, category: str):
        """Create an Obsidian-style markdown note for an app."""
        note_content = f"""# {app_name}

## Metadata
- **App ID**: {app_id}
- **Category**: [[{category}]]
- **Zork Interface**: Available

## Accessibility Features
This application has been analyzed and a custom Zork-style interface
has been generated for accessibility users.

## Related Apps
See [[{category}]] for related applications.

## Voice Commands
- "Open {app_name}"
- "What can I do in {app_name}?"
- "Help with {app_name}"

---
*Generated by Om Vinayaka Accessibility AI on {datetime.now().strftime('%Y-%m-%d')}*
"""
        note_path = os.path.join(self.mindmap_path, f"{app_id}.md")
        with open(note_path, 'w') as f:
            f.write(note_content)
    
    def add_feature_connection(self, app_id: str, feature: str):
        """Connect an app to an accessibility feature."""
        app_node = f"app_{app_id}"
        feature_node = f"feature_{feature}"
        
        if feature_node not in self.nodes:
            self.nodes[feature_node] = {
                'type': 'accessibility_feature',
                'name': feature,
                'created_at': datetime.now().isoformat()
            }
        
        self.edges.append({
            'source': app_node,
            'target': feature_node,
            'relationship': 'supports'
        })
        
        self._save_mindmap()
    
    def get_apps_by_category(self, category: str) -> List[Dict]:
        """Get all apps in a category."""
        return [
            node for node in self.nodes.values()
            if node.get('type') == 'application' and node.get('category') == category
        ]
    
    def get_related_apps(self, app_id: str) -> List[Dict]:
        """Get apps related to a given app (same category)."""
        app_node = self.nodes.get(f"app_{app_id}")
        if not app_node:
            return []
        
        category = app_node.get('category')
        return [
            node for node in self.nodes.values()
            if node.get('type') == 'application' 
            and node.get('category') == category
            and node.get('id') != app_id
        ]
    
    def get_graph(self) -> Dict:
        """Get the complete mind map graph for visualization."""
        return {
            'nodes': list(self.nodes.values()),
            'edges': self.edges
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OM VINAYAKA ACCESSIBILITY AI
# ═══════════════════════════════════════════════════════════════════════════════

class OmVinayakaAI:
    """
    Om Vinayaka Accessibility Knowledge Base AI
    
    The central intelligence system for VA21 accessibility that:
    1. Automatically activates when accessibility/voice features are used
    2. Creates Zork-style UX for every app when first installed
    3. Enables voice users to interact with ANY app in the full OS
    4. Asks clarifying questions to understand user intent
    5. Executes actions across the entire OS via FARA layer
    6. Stores app interfaces in LangChain + Obsidian mind maps
    7. LEARNS from interactions to get smarter over time!
    
    Self-Learning Features:
    - Learns common command patterns
    - Tracks user preferences
    - Monitors app usage patterns
    - Improves narratives based on feedback
    - Gets smarter with continued use!
    
    This is the USER-FACING AI, completely separate from Guardian AI
    which runs in a sandboxed Ollama at the kernel level.
    """
    
    def __init__(self, 
                 knowledge_base_path: str = None,
                 fara_layer = None,
                 app_zork_manager = None):
        self.knowledge_base_path = knowledge_base_path or DEFAULT_KNOWLEDGE_BASE_PATH
        os.makedirs(self.knowledge_base_path, exist_ok=True)
        
        # Import components lazily to avoid circular imports
        self.fara_layer = fara_layer
        self.app_zork_manager = app_zork_manager
        
        # Initialize sub-components
        self.mind_map = AccessibilityMindMap()
        self.terminal_adapter = TerminalZorkAdapter()
        
        # Initialize Self-Learning Engine
        self.learning_engine = None
        self._init_learning_engine()
        
        # State
        self.is_active = False
        self.current_context: Dict = {}
        self.conversation_history: List[Dict] = []
        self.pending_clarification = None
        
        # Registered apps with Zork interfaces
        self.registered_apps: Dict[str, str] = {}  # app_name -> interface_id
        
        # Load existing registrations
        self._load_registrations()
        
        print(f"[Om Vinayaka] Accessibility AI initialized v{OM_VINAYAKA_VERSION}")
        if self.learning_engine:
            print("[Om Vinayaka] Self-Learning Engine: ACTIVE - I get smarter as you use me!")
    
    def _init_learning_engine(self):
        """Initialize the Self-Learning Engine."""
        try:
            from .self_learning import get_learning_engine
            self.learning_engine = get_learning_engine()
        except ImportError as e:
            print(f"[Om Vinayaka] Self-learning not available: {e}")
            self.learning_engine = None
    
    def _load_registrations(self):
        """Load registered app interfaces."""
        reg_file = os.path.join(self.knowledge_base_path, "registrations.json")
        if os.path.exists(reg_file):
            try:
                with open(reg_file, 'r') as f:
                    self.registered_apps = json.load(f)
            except Exception:
                pass
    
    def _save_registrations(self):
        """Save registered app interfaces."""
        reg_file = os.path.join(self.knowledge_base_path, "registrations.json")
        with open(reg_file, 'w') as f:
            json.dump(self.registered_apps, f, indent=2)
    
    def activate(self):
        """Activate the Om Vinayaka Accessibility AI."""
        self.is_active = True
        
        # Start a learning session
        if self.learning_engine:
            self.learning_engine.start_session()
        
        print("[Om Vinayaka] Accessibility AI ACTIVATED")
        print("[Om Vinayaka] Voice control and Zork UX ready for all applications")
        if self.learning_engine:
            stats = self.learning_engine.get_statistics()
            print(f"[Om Vinayaka] Learned patterns: {stats['patterns_learned']}, "
                  f"Interactions: {stats['total_interactions']}")
        return self._get_welcome_message()
    
    def deactivate(self):
        """Deactivate the Om Vinayaka Accessibility AI."""
        self.is_active = False
        
        # End learning session
        if self.learning_engine:
            self.learning_engine.end_session()
        
        print("[Om Vinayaka] Accessibility AI deactivated")
    
    def _get_welcome_message(self) -> str:
        """Get the welcome message for accessibility users."""
        # Add learning stats if available
        learning_note = ""
        if self.learning_engine:
            stats = self.learning_engine.get_statistics()
            if stats['patterns_learned'] > 0:
                learning_note = f"\n🧠 I've learned {stats['patterns_learned']} command patterns from our interactions!"
        
        return f"""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                     🙏 OM VINAYAKA 🙏                              ║
║                                                                   ║
║           VA21 Accessibility Intelligence System                  ║
║                  with Self-Learning AI                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

Welcome! I am your accessibility companion for the entire VA21 system.

I can help you:
• Control ANY application with your voice or natural language
• Navigate the system through conversational interaction
• Get explanations of what things do (not just what they're called)
• Execute complex tasks with simple commands
• LEARN from our interactions to serve you better!

Every application has been given a Zork-style adventure interface,
making computing accessible and even fun!
{learning_note}
Hold the Super key to speak, or just type what you'd like to do.

What would you like to accomplish today?
"""
    
    def register_app_on_install(self, app_name: str, 
                                 desktop_file: str = None) -> Dict:
        """
        Automatically register an app when it's installed.
        Creates a Zork-style interface for the app.
        
        This is called by the system when any app is installed.
        """
        print(f"[Om Vinayaka] Registering new app: {app_name}")
        
        # Use the app Zork manager if available
        if self.app_zork_manager:
            interface = self.app_zork_manager.register_app(app_name, desktop_file)
            interface_id = interface.app_id
        else:
            # Create a simple registration
            interface_id = hashlib.md5(app_name.lower().encode()).hexdigest()[:12]
        
        # Register in our tracking
        self.registered_apps[app_name.lower()] = interface_id
        self._save_registrations()
        
        # Add to mind map
        category = self._detect_app_category(app_name)
        self.mind_map.add_app_node(interface_id, app_name, category, interface_id)
        
        # Add accessibility feature connections
        self.mind_map.add_feature_connection(interface_id, "voice_control")
        self.mind_map.add_feature_connection(interface_id, "zork_interface")
        self.mind_map.add_feature_connection(interface_id, "natural_language")
        
        print(f"[Om Vinayaka] Created Zork interface for: {app_name}")
        
        return {
            'app_name': app_name,
            'interface_id': interface_id,
            'category': category,
            'status': 'registered'
        }
    
    def _detect_app_category(self, app_name: str) -> str:
        """Detect the category of an application."""
        app_lower = app_name.lower()
        
        categories = {
            'text_editor': ['vim', 'nano', 'gedit', 'kate', 'code', 'vscode', 'emacs', 'notepad'],
            'file_manager': ['nautilus', 'thunar', 'dolphin', 'files', 'ranger', 'nnn'],
            'web_browser': ['firefox', 'chrome', 'chromium', 'safari', 'brave', 'edge'],
            'terminal': ['terminal', 'konsole', 'xterm', 'alacritty', 'kitty', 'gnome-terminal'],
            'media_player': ['vlc', 'mpv', 'totem', 'rhythmbox', 'spotify'],
            'office': ['libreoffice', 'writer', 'calc', 'impress', 'word', 'excel'],
            'graphics': ['gimp', 'inkscape', 'krita', 'blender'],
            'ai_cli': ['gemini', 'codex', 'copilot', 'claude', 'aider', 'continue', 'cody'],
            'development': ['git', 'docker', 'npm', 'python', 'cargo', 'make'],
        }
        
        for category, keywords in categories.items():
            if any(kw in app_lower for kw in keywords):
                return category
        
        return 'other'
    
    def process_user_input(self, user_input: str, 
                           current_app: str = None) -> Dict[str, Any]:
        """
        Process user input with context awareness and self-learning.
        
        Understands natural language, asks clarifying questions when needed,
        executes actions via the FARA layer, and LEARNS from interactions!
        
        Returns:
            {
                'response': str - What to say to the user
                'action': Optional[str] - Action to execute
                'needs_clarification': bool - Whether we need more info
                'clarification_question': Optional[str] - What to ask
            }
        """
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'app_context': current_app,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check for pending clarification response
        if self.pending_clarification:
            result = self._handle_clarification_response(user_input, current_app)
            return result
        
        # SELF-LEARNING: Try to predict action from learned patterns first
        if self.learning_engine:
            prediction = self.learning_engine.predict_action(user_input, current_app)
            if prediction and prediction[1] > 0.7:  # High confidence prediction
                action, confidence = prediction
                # Use the learned pattern!
                response = self._get_action_response(action, current_app)
                
                # Learn from this successful prediction
                self.learning_engine.learn_command(user_input, action, current_app, True)
                
                return {
                    'response': response,
                    'action': action,
                    'needs_clarification': False,
                    'clarification_question': None,
                    'learned_prediction': True,
                    'confidence': confidence
                }
        
        # Understand intent (fallback to rule-based understanding)
        intent = self._understand_intent(user_input, current_app)
        
        # Handle based on intent
        if intent['type'] == 'app_action':
            result = self._handle_app_action(intent, current_app)
        elif intent['type'] == 'navigation':
            result = self._handle_navigation(intent)
        elif intent['type'] == 'question':
            result = self._handle_question(intent, current_app)
        elif intent['type'] == 'system_control':
            return self._handle_system_control(intent)
        elif intent['type'] == 'cli_tool':
            return self._handle_cli_tool(intent)
        elif intent['type'] == 'help':
            return self._handle_help(intent, current_app)
        else:
            return self._ask_clarification(user_input, current_app)
    
    def _understand_intent(self, user_input: str, current_app: str = None) -> Dict:
        """Understand the user's intent from their input."""
        input_lower = user_input.lower().strip()
        
        # CLI tool detection
        for tool in CLI_TOOLS_TO_WRAP:
            if tool in input_lower:
                return {
                    'type': 'cli_tool',
                    'tool': tool,
                    'query': input_lower.replace(tool, '').strip()
                }
        
        # App actions
        action_keywords = {
            'save': ['save', 'store', 'keep', 'preserve'],
            'open': ['open', 'load', 'start', 'launch', 'run'],
            'close': ['close', 'exit', 'quit', 'leave'],
            'copy': ['copy', 'duplicate'],
            'paste': ['paste', 'put'],
            'delete': ['delete', 'remove', 'erase'],
            'undo': ['undo', 'revert', 'go back'],
            'redo': ['redo', 'repeat'],
            'search': ['search', 'find', 'look for'],
            'create': ['create', 'new', 'make'],
        }
        
        for action, keywords in action_keywords.items():
            if any(kw in input_lower for kw in keywords):
                return {
                    'type': 'app_action',
                    'action': action,
                    'full_input': user_input
                }
        
        # Navigation
        nav_keywords = ['go to', 'navigate', 'take me to', 'show me', 'open']
        for kw in nav_keywords:
            if kw in input_lower:
                destination = input_lower.replace(kw, '').strip()
                return {
                    'type': 'navigation',
                    'destination': destination
                }
        
        # System control
        system_keywords = ['volume', 'brightness', 'wifi', 'bluetooth', 
                          'shutdown', 'restart', 'sleep', 'lock']
        for kw in system_keywords:
            if kw in input_lower:
                return {
                    'type': 'system_control',
                    'control': kw,
                    'full_input': user_input
                }
        
        # Questions
        if any(q in input_lower for q in ['what', 'how', 'where', 'why', 'when', 'who', '?']):
            return {
                'type': 'question',
                'question': user_input
            }
        
        # Help
        if 'help' in input_lower:
            topic = input_lower.replace('help', '').strip()
            return {
                'type': 'help',
                'topic': topic
            }
        
        # Unknown
        return {
            'type': 'unknown',
            'input': user_input
        }
    
    def _handle_app_action(self, intent: Dict, current_app: str) -> Dict:
        """Handle an action request for an application."""
        action = intent['action']
        
        # Check if action needs confirmation
        dangerous_actions = ['delete', 'close', 'quit']
        if action in dangerous_actions:
            self.pending_clarification = {
                'type': 'confirm',
                'action': action,
                'context': current_app
            }
            return {
                'response': f"You want to {action}. This may have permanent effects. Are you sure?",
                'action': None,
                'needs_clarification': True,
                'clarification_question': "Please confirm yes or no."
            }
        
        # Execute via FARA layer if available
        if self.fara_layer:
            result = self.fara_layer.execute_action(action, {'app': current_app})
            return {
                'response': result.get('description', f"Executing {action}..."),
                'action': action,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # Default response
        return {
            'response': f"I'll {action} in {current_app or 'the current application'}.",
            'action': action,
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _handle_navigation(self, intent: Dict) -> Dict:
        """Handle navigation requests."""
        destination = intent.get('destination', '')
        
        if not destination:
            self.pending_clarification = {'type': 'navigation'}
            return {
                'response': "Where would you like to go?",
                'action': None,
                'needs_clarification': True,
                'clarification_question': "Tell me the app, folder, or location."
            }
        
        return {
            'response': f"Navigating to {destination}...",
            'action': f"navigate:{destination}",
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _handle_question(self, intent: Dict, current_app: str) -> Dict:
        """Handle user questions."""
        question = intent.get('question', '').lower()
        
        # What can I do?
        if 'what can i do' in question or 'what are my options' in question:
            if current_app:
                return {
                    'response': f"In {current_app}, you can use voice or typed commands to interact naturally. Try actions like save, open, search, or create. Ask me 'help' for a full list of what's available.",
                    'action': None,
                    'needs_clarification': False,
                    'clarification_question': None
                }
            return {
                'response': "You can control any application with voice or text. Navigate between apps, perform actions, search the web, or manage system settings. What would you like to do?",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # Where am I?
        if 'where am i' in question:
            return {
                'response': f"You are currently in {current_app or 'the VA21 OS'}. Every app has a Zork-style interface ready for you. Just tell me what you want to do.",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # How do I?
        if 'how do i' in question:
            task = question.replace('how do i', '').strip().rstrip('?')
            return {
                'response': f"To {task}, just tell me what you want to accomplish. For example, say 'I want to {task}' and I'll guide you step by step.",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        return {
            'response': f"That's a good question. Could you tell me more about what you're trying to understand?",
            'action': None,
            'needs_clarification': True,
            'clarification_question': "What specifically would you like to know?"
        }
    
    def _handle_system_control(self, intent: Dict) -> Dict:
        """Handle system control requests."""
        control = intent.get('control', '')
        
        control_messages = {
            'volume': "I can adjust the volume. Would you like it up, down, or muted?",
            'brightness': "I can adjust screen brightness. Brighter or dimmer?",
            'wifi': "I can toggle WiFi. Turn it on or off?",
            'bluetooth': "I can toggle Bluetooth. Turn it on or off?",
            'shutdown': "You want to shut down. This will close everything. Are you sure?",
            'restart': "You want to restart. This will close everything. Are you sure?",
            'sleep': "I'll put the computer to sleep now.",
            'lock': "I'll lock the screen now.",
        }
        
        message = control_messages.get(control, f"I can help with {control}. What would you like?")
        
        needs_clarification = control in ['volume', 'brightness', 'wifi', 'bluetooth', 'shutdown', 'restart']
        
        if control in ['shutdown', 'restart']:
            self.pending_clarification = {'type': 'confirm', 'action': control}
        elif control in ['volume', 'brightness', 'wifi', 'bluetooth']:
            self.pending_clarification = {'type': 'system_adjust', 'control': control}
        
        return {
            'response': message,
            'action': control if control in ['sleep', 'lock'] else None,
            'needs_clarification': needs_clarification,
            'clarification_question': None
        }
    
    def _handle_cli_tool(self, intent: Dict) -> Dict:
        """Handle CLI tool interactions with Zork wrapper."""
        tool = intent.get('tool', '')
        query = intent.get('query', '')
        
        interface = self.terminal_adapter.get_interface(tool)
        
        if not query:
            # Describe the tool
            description = self.terminal_adapter.describe_tool(tool)
            return {
                'response': description,
                'action': None,
                'needs_clarification': True,
                'clarification_question': f"What would you like to ask {interface.tool_name}?"
            }
        
        # Translate and execute
        command = self.terminal_adapter.translate_to_command(tool, query)
        
        return {
            'response': f"I'll ask {interface.tool_name}: {query}",
            'action': f"cli:{tool}:{command}",
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _handle_help(self, intent: Dict, current_app: str) -> Dict:
        """Handle help requests."""
        topic = intent.get('topic', '')
        
        if topic:
            return {
                'response': f"I can help with {topic}. Just tell me what you're trying to accomplish and I'll guide you through it.",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        help_text = f"""
I'm your Om Vinayaka accessibility assistant. Here's how I can help:

🗣️ VOICE CONTROL
   Hold the Super key and speak naturally

🎮 ZORK INTERFACE  
   Every app has a text adventure style interface

📱 APP CONTROL
   Say "save", "open", "search", "create", etc.

🔧 SYSTEM CONTROL
   Volume, brightness, WiFi, shutdown, etc.

💻 CLI TOOLS
   Gemini, Copilot, Codex - all wrapped in accessible interfaces

❓ QUESTIONS
   Ask "what can I do?", "where am I?", "how do I...?"

Currently in: {current_app or 'VA21 OS'}

What would you like to do?
"""
        return {
            'response': help_text,
            'action': None,
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _ask_clarification(self, user_input: str, current_app: str) -> Dict:
        """Ask for clarification when intent is unclear."""
        self.pending_clarification = {'type': 'general', 'original': user_input}
        
        return {
            'response': f"I want to help with '{user_input}', but I'm not sure what you mean. Are you trying to: do something in an app, navigate somewhere, ask a question, or control the system?",
            'action': None,
            'needs_clarification': True,
            'clarification_question': "Could you tell me more about what you'd like to do?"
        }
    
    def _handle_clarification_response(self, user_input: str, 
                                       current_app: str) -> Dict:
        """Handle user's response to a clarification question."""
        clarification = self.pending_clarification
        self.pending_clarification = None
        input_lower = user_input.lower().strip()
        
        # Handle confirmation responses
        if clarification.get('type') == 'confirm':
            if any(w in input_lower for w in ['yes', 'yeah', 'sure', 'ok', 'confirm', 'proceed']):
                action = clarification.get('action')
                return {
                    'response': f"Confirmed. Executing {action}...",
                    'action': action,
                    'needs_clarification': False,
                    'clarification_question': None
                }
            else:
                return {
                    'response': "Cancelled. What else can I help you with?",
                    'action': None,
                    'needs_clarification': False,
                    'clarification_question': None
                }
        
        # Handle navigation clarification
        if clarification.get('type') == 'navigation':
            return self._handle_navigation({'destination': user_input})
        
        # Handle system adjustment clarification
        if clarification.get('type') == 'system_adjust':
            control = clarification.get('control')
            return {
                'response': f"Adjusting {control}: {user_input}",
                'action': f"{control}:{user_input}",
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # Default: process as new request
        return self.process_user_input(user_input, current_app)
    
    def get_app_description(self, app_name: str) -> str:
        """Get a Zork-style description of an application."""
        if self.app_zork_manager:
            return self.app_zork_manager.describe_app(app_name)
        
        # Check if it's a CLI tool
        if any(tool in app_name.lower() for tool in CLI_TOOLS_TO_WRAP):
            return self.terminal_adapter.describe_tool(app_name)
        
        # Default description
        return f"""
You are ready to interact with {app_name}.

This application has a Zork-style accessibility interface.
Just tell me what you'd like to do, or ask for help.

What would you like to accomplish?
"""
    
    def get_status(self) -> Dict:
        """Get the status of the Om Vinayaka AI."""
        return {
            'version': OM_VINAYAKA_VERSION,
            'is_active': self.is_active,
            'registered_apps': len(self.registered_apps),
            'conversation_length': len(self.conversation_history),
            'mind_map_nodes': len(self.mind_map.nodes),
            'cli_tools_supported': len(self.terminal_adapter.tool_interfaces)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON AND FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

_om_vinayaka_instance = None


def get_om_vinayaka(knowledge_base_path: str = None,
                    fara_layer = None,
                    app_zork_manager = None) -> OmVinayakaAI:
    """Get or create the Om Vinayaka AI singleton."""
    global _om_vinayaka_instance
    
    if _om_vinayaka_instance is None:
        _om_vinayaka_instance = OmVinayakaAI(
            knowledge_base_path=knowledge_base_path,
            fara_layer=fara_layer,
            app_zork_manager=app_zork_manager
        )
    
    return _om_vinayaka_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the Om Vinayaka Accessibility AI."""
    print("=" * 70)
    print("VA21 OS - Om Vinayaka Accessibility AI Test")
    print("=" * 70)
    
    # Initialize
    om_vinayaka = get_om_vinayaka()
    
    # Activate and show welcome
    welcome = om_vinayaka.activate()
    print(welcome)
    
    # Test app registration
    print("\n--- Testing App Registration ---")
    result = om_vinayaka.register_app_on_install("Firefox")
    print(f"Registered: {result}")
    
    result = om_vinayaka.register_app_on_install("Visual Studio Code")
    print(f"Registered: {result}")
    
    result = om_vinayaka.register_app_on_install("Gemini CLI")
    print(f"Registered: {result}")
    
    # Test CLI tool description
    print("\n--- CLI Tool Zork Interface ---")
    print(om_vinayaka.terminal_adapter.describe_tool("gemini"))
    
    # Test user input processing
    print("\n--- Testing User Input Processing ---")
    
    test_inputs = [
        ("What can I do here?", "Firefox"),
        ("Save my work", "Visual Studio Code"),
        ("Ask gemini about Python", None),
        ("Help", None),
        ("Go to the research lab", None),
    ]
    
    for user_input, app in test_inputs:
        print(f"\n> User ({app or 'System'}): {user_input}")
        response = om_vinayaka.process_user_input(user_input, app)
        print(f"< Om Vinayaka: {response['response'][:200]}...")
        if response['action']:
            print(f"  [Action: {response['action']}]")
    
    # Show status
    print("\n--- Status ---")
    status = om_vinayaka.get_status()
    print(json.dumps(status, indent=2))
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
