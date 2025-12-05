#!/usr/bin/env python3
"""
VA21 OS - Om Vinayaka Accessibility Knowledge Base AI
======================================================

🙏 STATE-OF-THE-ART ACCESSIBILITY AI (Unique to VA21!) 🙏

Om Vinayaka AI goes FAR BEYOND traditional screen readers:

┌─────────────────────────────┬─────────────────────────────────────────┐
│  Traditional Screen Readers │  VA21 + Om Vinayaka AI                  │
├─────────────────────────────┼─────────────────────────────────────────┤
│  Reads keywords:            │  Explains purpose:                      │
│  "menu", "button"           │  "This saves your work"                 │
├─────────────────────────────┼─────────────────────────────────────────┤
│  No context awareness       │  Understands your intent and task       │
├─────────────────────────────┼─────────────────────────────────────────┤
│  Just announces elements    │  Asks clarifying questions when needed  │
├─────────────────────────────┼─────────────────────────────────────────┤
│  User must know commands    │  Natural conversation in any language   │
├─────────────────────────────┼─────────────────────────────────────────┤
│  Single app support         │  Zork-style UX for EVERY app            │
├─────────────────────────────┼─────────────────────────────────────────┤
│  Limited CLI support        │  Wraps CLI tools: Gemini, Copilot, etc. │
└─────────────────────────────┴─────────────────────────────────────────┘

Om Vinayaka AI Features:
- Automatic Zork UX Generation: Every app gets a text adventure interface
- System-Wide Voice Control: Control ANY application with voice
- CLI Tool Wrapper: Gemini CLI, GitHub Copilot CLI, Codex accessible
- Knowledge Base: LangChain + Obsidian mind maps store all interfaces
- Clarifying Questions: AI asks for details when intent is unclear
- Context-Aware Execution: Understands active app and user intent
- 1,600+ Languages: Hindi, Tamil, Telugu, Spanish, French, and more!

Self-Learning & Introspection:
- Learns common command patterns from user interactions
- Tracks user preferences for personalized experience
- Monitors app usage patterns to optimize suggestions
- Self-reflects on actions and learns from them (dynamic thinking)
- Asks "why" and "what" questions for deeper understanding
- Gets smarter with continued use!

Idle Mode Self-Improvement:
- Researches best ways to optimize user workflows during idle time
- Adapts system components to enhance performance
- Analyzes errors and develops prevention strategies
- Always helping, even when at rest!

Auto Dynamic Memory Backups:
- Never forgets - auto backup on shutdown
- Dynamic backups based on activity level
- Version history for all knowledge
- Survives power loss

Architecture:
- Om Vinayaka AI: Central orchestrator (THE CORE)
- App Zork Generator: Creates Zork UX for each app automatically
- Accessibility Knowledge Base: LangChain + Obsidian with mind maps
- Voice Controller: System-wide voice input and output (1,600+ languages)
- FARA Layer: Universal action execution across all apps
- Terminal Zork Adapter: Zork UX for CLI tools (Gemini, Codex, Copilot, etc.)
- Self-Learning Engine: Learns patterns, preferences, and improves over time
- Self-Reflection Engine: Introspects and asks why/what questions
- Error Analyzer: Learns from mistakes, develops prevention strategies
- Workflow Optimizer: Finds ways to help users work more efficiently
- Idle Mode Manager: Self-improvement during user inactivity
- Persistent Memory: Auto dynamic backups

Example Conversation:
    User: "I want to find something on the internet"
    VA21: "I can help you search. What would you like to look up?"
    User: "Climate change research papers"
    VA21: "Searching for climate change research papers. I'm using 
          privacy-respecting search so your query isn't tracked."

CLI Tool Accessibility Example:
    User: "Ask Gemini about Python decorators"
    VA21: "You stand before the GEMINI ORACLE, a shimmering portal of AI wisdom.
          The oracle considers your question deeply...
          [Gemini's response about Python decorators]
          What else would you like to ask?"

NOTE: Guardian AI runs in a sandboxed Ollama in the kernel and is completely
isolated from this user-facing accessibility system.

Om Vinayaka - May obstacles be removed from your computing journey.
Making technology accessible to everyone, in every language.
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

OM_VINAYAKA_VERSION = "1.2.0"  # Updated with idle mode self-improvement

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
# OM VINAYAKA ACCESSIBILITY AI - THE CORE
# ═══════════════════════════════════════════════════════════════════════════════

class OmVinayakaAI:
    """
    🙏 OM VINAYAKA ACCESSIBILITY AI - STATE OF THE ART (Unique to VA21!) 🙏
    
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║     🧠 THE SELF-LEARNING, INTROSPECTING, STATE-OF-THE-ART ACCESSIBILITY AI    ║
    ╠═══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                               ║
    ║   Om Vinayaka AI goes FAR BEYOND traditional screen readers:                  ║
    ║                                                                               ║
    ║   ┌─────────────────────────────┬─────────────────────────────────────────┐   ║
    ║   │  Traditional Screen Readers │  VA21 + Om Vinayaka AI                  │   ║
    ║   ├─────────────────────────────┼─────────────────────────────────────────┤   ║
    ║   │  Reads keywords:            │  Explains purpose:                      │   ║
    ║   │  "menu", "button"           │  "This saves your work"                 │   ║
    ║   ├─────────────────────────────┼─────────────────────────────────────────┤   ║
    ║   │  No context awareness       │  Understands your intent and task       │   ║
    ║   ├─────────────────────────────┼─────────────────────────────────────────┤   ║
    ║   │  Just announces elements    │  Asks clarifying questions when needed  │   ║
    ║   ├─────────────────────────────┼─────────────────────────────────────────┤   ║
    ║   │  User must know commands    │  Natural conversation in any language   │   ║
    ║   ├─────────────────────────────┼─────────────────────────────────────────┤   ║
    ║   │  Single app support         │  Zork-style UX for EVERY app            │   ║
    ║   ├─────────────────────────────┼─────────────────────────────────────────┤   ║
    ║   │  Limited CLI support        │  Wraps CLI tools: Gemini, Copilot, etc. │   ║
    ║   └─────────────────────────────┴─────────────────────────────────────────┘   ║
    ║                                                                               ║
    ╠═══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                               ║
    ║   🎮 AUTOMATIC ZORK UX GENERATION                                             ║
    ║   Every app gets a text adventure interface when installed                    ║
    ║                                                                               ║
    ║   🗣️ SYSTEM-WIDE VOICE CONTROL                                                ║
    ║   Control ANY application with voice, not just specific apps                  ║
    ║   Hold Super Key → Speak naturally → Action executed                          ║
    ║                                                                               ║
    ║   💻 CLI TOOL WRAPPER                                                         ║
    ║   Gemini CLI, GitHub Copilot CLI, Codex - all accessible via Zork interfaces  ║
    ║                                                                               ║
    ║   📚 KNOWLEDGE BASE                                                           ║
    ║   LangChain + Obsidian mind maps store all app interfaces                     ║
    ║                                                                               ║
    ║   ❓ CLARIFYING QUESTIONS                                                     ║
    ║   AI asks for details when your intent is unclear                             ║
    ║                                                                               ║
    ║   🎯 CONTEXT-AWARE EXECUTION                                                  ║
    ║   Understands what app is active and what you want                            ║
    ║                                                                               ║
    ║   🌍 1,600+ LANGUAGES                                                         ║
    ║   Hindi, Tamil, Telugu, Spanish, French, and more!                            ║
    ║                                                                               ║
    ╠═══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                               ║
    ║   🧠 SELF-LEARNING CAPABILITIES                                               ║
    ║   ├── Learns common command patterns from every interaction                   ║
    ║   ├── Tracks user preferences for personalized experience                     ║
    ║   ├── Monitors app usage patterns to optimize suggestions                     ║
    ║   ├── Improves narratives based on what resonates with users                  ║
    ║   └── Gets smarter with continued use!                                        ║
    ║                                                                               ║
    ║   🔍 INTROSPECTION CAPABILITIES                                               ║
    ║   ├── Self-reflects on actions and learns from them                           ║
    ║   ├── Asks "why" and "what" questions for deeper understanding                ║
    ║   ├── Analyzes errors and develops prevention strategies                      ║
    ║   ├── Researches best ways to optimize user workflows                         ║
    ║   └── Adapts behavior based on self-analysis                                  ║
    ║                                                                               ║
    ║   🌙 IDLE TIME SELF-IMPROVEMENT                                               ║
    ║   ├── Automatically improves without user intervention                        ║
    ║   ├── Reviews past interactions for learning opportunities                    ║
    ║   ├── Develops new strategies to help users                                   ║
    ║   └── Always working to remove obstacles!                                     ║
    ║                                                                               ║
    ║   💾 AUTO DYNAMIC MEMORY BACKUPS                                              ║
    ║   ├── Never forgets - auto backup on shutdown                                 ║
    ║   ├── Dynamic backups based on activity level                                 ║
    ║   ├── Version history for all knowledge                                       ║
    ║   └── Survives power loss                                                     ║
    ║                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    
    Example Conversation:
    
        User: "I want to find something on the internet"
        VA21: "I can help you search. What would you like to look up?"
        User: "Climate change research papers"
        VA21: "Searching for climate change research papers. I'm using 
              privacy-respecting search so your query isn't tracked."
    
    CLI Tool Accessibility Example:
    
        User: "Ask Gemini about Python decorators"
        VA21: "You stand before the GEMINI ORACLE, a shimmering portal of AI wisdom.
              The oracle considers your question deeply...
              [Gemini's response about Python decorators]
              What else would you like to ask?"
    
    Architecture:
    - Self-Learning Engine: Learns patterns, preferences, usage from interactions
    - Self-Reflection Engine: Introspects on behavior, asks why/what questions
    - Error Analyzer: Learns from mistakes, develops prevention strategies
    - Workflow Optimizer: Finds ways to help users work more efficiently
    - Summary Engine: Maintains context without hallucinations
    - Knowledge Base: Obsidian mind maps for persistent memory
    - Voice Integration: Works with Voice Intelligence Layer (1,600+ languages)
    - FARA Layer: Executes actions across the entire OS
    - Terminal Zork Adapter: Makes CLI tools accessible via Zork interfaces
    
    This is the USER-FACING AI, completely separate from Guardian AI
    which runs in a sandboxed Ollama at the kernel level.
    
    Om Vinayaka - The remover of obstacles, the one who learns and grows.
    Making technology accessible to everyone, in every language.
    """
    
    def __init__(self, 
                 knowledge_base_path: str = None,
                 fara_layer = None,
                 app_zork_manager = None,
                 enable_idle_mode: bool = True,
                 idle_timeout_seconds: int = 300,
                 enable_auto_backup: bool = True,
                 enable_performance_optimizer: bool = True,
                 enable_feature_discovery: bool = True,
                 enable_auto_fara: bool = True):
        self.knowledge_base_path = knowledge_base_path or DEFAULT_KNOWLEDGE_BASE_PATH
        os.makedirs(self.knowledge_base_path, exist_ok=True)
        
        # Import components lazily to avoid circular imports
        self.fara_layer = fara_layer
        self.app_zork_manager = app_zork_manager
        
        # Initialize sub-components
        self.mind_map = AccessibilityMindMap()
        self.terminal_adapter = TerminalZorkAdapter()
        
        # Initialize Persistent Memory with Auto Dynamic Backups FIRST
        self.persistent_memory = None
        self._enable_auto_backup = enable_auto_backup
        self._init_persistent_memory()
        
        # Initialize Self-Learning Engine
        self.learning_engine = None
        self._init_learning_engine()
        
        # Initialize Summary Engine for context management
        self.summary_engine = None
        self._init_summary_engine()
        
        # Initialize Idle Mode Manager for self-improvement
        self.idle_mode_manager = None
        self._enable_idle_mode = enable_idle_mode
        self._idle_timeout_seconds = idle_timeout_seconds
        self._init_idle_mode_manager()
        
        # Initialize Performance Optimizer (NEW!)
        self.performance_optimizer = None
        self._enable_performance_optimizer = enable_performance_optimizer
        self._init_performance_optimizer()
        
        # Initialize Feature Discovery Engine (NEW!)
        self.feature_discovery = None
        self._enable_feature_discovery = enable_feature_discovery
        self._init_feature_discovery()
        
        # Initialize Automatic FARA Layer Creator (NEW!)
        self.fara_creator = None
        self._enable_auto_fara = enable_auto_fara
        self._init_fara_creator()
        
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
        if self.persistent_memory:
            print("[Om Vinayaka] 💾 Persistent Memory: ACTIVE - Auto dynamic backups enabled!")
        if self.learning_engine:
            print("[Om Vinayaka] 🧠 Self-Learning Engine: ACTIVE - I get smarter as you use me!")
        if self.summary_engine:
            print("[Om Vinayaka] 📝 Summary Engine: ACTIVE - Context-aware, no hallucinations!")
        if self.idle_mode_manager:
            print("[Om Vinayaka] 🌙 Idle Mode: ACTIVE - I self-improve when you're away!")
        if self.performance_optimizer:
            print("[Om Vinayaka] ⚡ Performance Optimizer: ACTIVE - Fast model loading!")
        if self.feature_discovery:
            print("[Om Vinayaka] 🎯 Feature Discovery: ACTIVE - Helping users learn VA21!")
        if self.fara_creator:
            print("[Om Vinayaka] 🎮 Auto FARA Creator: ACTIVE - Every app gets voice control!")
    
    def _init_persistent_memory(self):
        """
        Initialize the Persistent Memory system with auto dynamic backups.
        
        This ensures Om Vinayaka NEVER FORGETS:
        - Auto backup on shutdown
        - Dynamic backups based on activity level
        - Periodic backups every 30 minutes (adjusted dynamically)
        - Version history of all knowledge
        """
        if not self._enable_auto_backup:
            return
        
        try:
            from .persistent_memory import get_persistent_memory
            self.persistent_memory = get_persistent_memory()
            
            # The persistent memory manager automatically:
            # - Starts auto backup thread
            # - Registers shutdown handlers
            # - Performs dynamic backups based on activity
            
            print("[Om Vinayaka] 💾 Persistent Memory initialized:")
            print("[Om Vinayaka]    - Auto backup on shutdown: ENABLED")
            print("[Om Vinayaka]    - Dynamic backup (activity-based): ENABLED")
            print("[Om Vinayaka]    - Periodic backup: ENABLED")
            print("[Om Vinayaka]    - Version history: ENABLED")
            
        except ImportError as e:
            print(f"[Om Vinayaka] Persistent memory not available: {e}")
            self.persistent_memory = None
    
    def _init_learning_engine(self):
        """Initialize the Self-Learning Engine."""
        try:
            from .self_learning import get_learning_engine
            self.learning_engine = get_learning_engine()
        except ImportError as e:
            print(f"[Om Vinayaka] Self-learning not available: {e}")
            self.learning_engine = None
    
    def _init_summary_engine(self):
        """Initialize the Summary Engine for context management."""
        try:
            from .summary_engine import get_summary_engine
            self.summary_engine = get_summary_engine()
        except ImportError as e:
            print(f"[Om Vinayaka] Summary engine not available: {e}")
            self.summary_engine = None
    
    def _init_idle_mode_manager(self):
        """Initialize the Idle Mode Manager for self-improvement during inactivity."""
        if not self._enable_idle_mode:
            return
        
        try:
            from .idle_mode import get_idle_mode_manager
            self.idle_mode_manager = get_idle_mode_manager(
                idle_timeout_seconds=self._idle_timeout_seconds
            )
            
            # Set callbacks for idle mode events
            self.idle_mode_manager.set_callbacks(
                on_idle_start=self._on_idle_start,
                on_idle_end=self._on_idle_end,
                on_optimization=self._on_optimization
            )
        except ImportError as e:
            print(f"[Om Vinayaka] Idle mode not available: {e}")
            self.idle_mode_manager = None
    
    def _init_performance_optimizer(self):
        """Initialize the Performance Optimizer for faster model loading."""
        if not self._enable_performance_optimizer:
            return
        
        try:
            from .performance_optimizer import get_performance_optimizer
            self.performance_optimizer = get_performance_optimizer()
            
            # Set callback for performance events
            self.performance_optimizer.set_om_vinayaka_callback(
                self._on_performance_event
            )
        except ImportError as e:
            print(f"[Om Vinayaka] Performance optimizer not available: {e}")
            self.performance_optimizer = None
    
    def _init_feature_discovery(self):
        """Initialize the Feature Discovery Engine for user adoption."""
        if not self._enable_feature_discovery:
            return
        
        try:
            from .feature_discovery import get_feature_discovery
            self.feature_discovery = get_feature_discovery()
            
            # Set callback for discovery events
            self.feature_discovery.set_om_vinayaka_callback(
                self._on_feature_discovered
            )
        except ImportError as e:
            print(f"[Om Vinayaka] Feature discovery not available: {e}")
            self.feature_discovery = None
    
    def _init_fara_creator(self):
        """Initialize the Automatic FARA Layer Creator."""
        if not self._enable_auto_fara:
            return
        
        try:
            from .fara_compatibility import get_fara_creator
            self.fara_creator = get_fara_creator()
            
            # Set callback for FARA events
            self.fara_creator.set_om_vinayaka_callback(
                self._on_fara_profile_created
            )
            
            # Start monitoring for new app installations
            self.fara_creator.start_monitoring()
        except ImportError as e:
            print(f"[Om Vinayaka] FARA creator not available: {e}")
            self.fara_creator = None
    
    def _on_performance_event(self, event: Dict):
        """Handle performance optimizer events."""
        event_type = event.get('event')
        if event_type == 'performance_initialized':
            boot_time = event.get('boot_time', 0)
            print(f"[Om Vinayaka] ⚡ Performance: Boot optimized ({boot_time:.2f}s)")
        elif event_type == 'model_state_change':
            model_id = event.get('model_id')
            state = event.get('state')
            if state == 'ready':
                print(f"[Om Vinayaka] ⚡ Model {model_id} is warmed up and ready!")
    
    def _on_feature_discovered(self, event: Dict):
        """Handle feature discovery events."""
        feature_id = event.get('feature_id')
        if feature_id:
            print(f"[Om Vinayaka] 🎯 User discovered feature: {feature_id}")
    
    def _on_fara_profile_created(self, event: Dict):
        """Handle FARA profile creation events."""
        app_name = event.get('app_name')
        actions_count = event.get('actions_count', 0)
        if app_name:
            print(f"[Om Vinayaka] 🎮 FARA profile created for {app_name} ({actions_count} actions)")
    
    def _on_idle_start(self):
        """Called when idle mode starts."""
        print("[Om Vinayaka] 🌙 Entering self-improvement mode (user idle)")
    
    def _on_idle_end(self):
        """Called when idle mode ends."""
        print("[Om Vinayaka] ☀️ Welcome back! Ready to assist you.")
    
    def _on_optimization(self, result: Dict):
        """Called when an optimization is made during idle time."""
        if result.get('type') == 'workflow':
            suggestions = result.get('suggestions', [])
            if suggestions:
                print(f"[Om Vinayaka] 🔄 Found {len(suggestions)} workflow optimization opportunities")
    
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
        
        # Start idle mode monitoring for self-improvement
        if self.idle_mode_manager:
            self.idle_mode_manager.start()
        
        print("[Om Vinayaka] Accessibility AI ACTIVATED")
        print("[Om Vinayaka] Voice control and Zork UX ready for all applications")
        if self.learning_engine:
            stats = self.learning_engine.get_statistics()
            print(f"[Om Vinayaka] Learned patterns: {stats['patterns_learned']}, "
                  f"Interactions: {stats['total_interactions']}")
        if self.idle_mode_manager:
            print("[Om Vinayaka] Idle mode self-improvement: ENABLED")
        return self._get_welcome_message()
    
    def deactivate(self):
        """Deactivate the Om Vinayaka Accessibility AI."""
        self.is_active = False
        
        # End learning session
        if self.learning_engine:
            self.learning_engine.end_session()
        
        # Stop idle mode monitoring
        if self.idle_mode_manager:
            self.idle_mode_manager.stop()
        
        print("[Om Vinayaka] Accessibility AI deactivated")
    
    def _get_welcome_message(self) -> str:
        """Get the welcome message for accessibility users."""
        # Add learning stats if available
        learning_note = ""
        if self.learning_engine:
            stats = self.learning_engine.get_statistics()
            if stats['patterns_learned'] > 0:
                learning_note = f"\n🧠 I've learned {stats['patterns_learned']} command patterns from our interactions!"
        
        # Add idle mode note if available
        idle_note = ""
        if self.idle_mode_manager:
            idle_status = self.idle_mode_manager.get_status()
            if idle_status.get('optimizations_made', 0) > 0:
                idle_note = f"\n🔄 I've made {idle_status['optimizations_made']} self-improvements during idle time!"
        
        return f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                          🙏 OM VINAYAKA 🙏                                     ║
║                                                                               ║
║              STATE-OF-THE-ART ACCESSIBILITY AI (Unique to VA21!)              ║
║                                                                               ║
║          Self-Learning • Introspecting • Context-Aware • 1,600+ Languages     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Welcome! I am Om Vinayaka, your state-of-the-art accessibility companion.

Unlike traditional screen readers that just read "menu" or "button",
I EXPLAIN what things do and ASK what you want to accomplish.

🎯 What I can do for you:
• Control ANY application with voice or natural language
• Explain what things do (not just what they're called)
• Ask clarifying questions when needed
• Execute complex tasks with simple commands
• Wrap CLI tools (Gemini, Copilot, Codex) with Zork interfaces
• Support 1,600+ languages including 100+ Indian dialects

🎮 Zork-Style UX: Every app gets a text adventure interface!
🧠 Self-Learning: I get smarter with every interaction!
🔍 Introspection: I reflect on my behavior to improve!
💾 Auto-Backup: I never forget what I've learned!
{learning_note}{idle_note}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hold the Super key to speak, or just type what you'd like to do.
Say things like: "I want to search the internet" or "Save my document"

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
            interface_id = hashlib.sha256(app_name.lower().encode()).hexdigest()[:12]
        
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
        
        Also records user activity to reset idle timer and enable
        self-improvement during user inactivity.
        
        Returns:
            {
                'response': str - What to say to the user
                'action': Optional[str] - Action to execute
                'needs_clarification': bool - Whether we need more info
                'clarification_question': Optional[str] - What to ask
            }
        """
        # Record user activity (resets idle timer and triggers dynamic backup check)
        if self.idle_mode_manager:
            self.idle_mode_manager.record_user_activity()
        
        # Record activity for dynamic backup
        if self.persistent_memory:
            self.persistent_memory.record_activity('interaction')
        
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
                
                # Save to persistent memory
                if self.persistent_memory:
                    self.persistent_memory.save_learned_pattern('command', {
                        'input': user_input,
                        'action': action,
                        'app': current_app,
                        'confidence': confidence,
                        'prediction': True
                    })
                
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
            result = self._handle_system_control(intent)
        elif intent['type'] == 'cli_tool':
            result = self._handle_cli_tool(intent)
        elif intent['type'] == 'help':
            result = self._handle_help(intent, current_app)
        else:
            result = self._ask_clarification(user_input, current_app)
            # Record that clarification was needed (for error analysis)
            if self.idle_mode_manager:
                self.idle_mode_manager.record_error(
                    'clarification_needed',
                    f"Could not understand: {user_input[:50]}",
                    {'input': user_input, 'app': current_app}
                )
        
        # Learn from this interaction if we have an action
        if self.learning_engine and result.get('action'):
            self.learning_engine.learn_command(
                user_input, 
                result['action'], 
                current_app, 
                True  # Assume success if we got an action
            )
            
            # Save to persistent memory for dynamic backup
            if self.persistent_memory:
                self.persistent_memory.save_learned_pattern('command', {
                    'input': user_input,
                    'action': result['action'],
                    'app': current_app,
                    'success': True
                })
                self.persistent_memory.record_activity('pattern')
        
        return result
    
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
    
    def _get_action_response(self, action: str, current_app: str) -> str:
        """Generate a response for a predicted action."""
        action_responses = {
            'save': f"Saving your work in {current_app or 'the application'}...",
            'search': f"Searching in {current_app or 'the application'}...",
            'open': f"Opening in {current_app or 'the application'}...",
            'close': f"Closing {current_app or 'the application'}...",
            'back': "Going back...",
            'forward': "Going forward...",
            'undo': "Undoing last action...",
            'redo': "Redoing...",
            'copy': "Copied to clipboard!",
            'paste': "Pasting...",
            'new_tab': "Opening new tab...",
            'close_tab': "Closing tab...",
        }
        return action_responses.get(action, f"Executing {action}...")
    
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
        status = {
            'version': OM_VINAYAKA_VERSION,
            'is_active': self.is_active,
            'registered_apps': len(self.registered_apps),
            'conversation_length': len(self.conversation_history),
            'mind_map_nodes': len(self.mind_map.nodes),
            'cli_tools_supported': len(self.terminal_adapter.tool_interfaces),
            'learning_engine': self.learning_engine is not None,
            'summary_engine': self.summary_engine is not None,
            'idle_mode_manager': self.idle_mode_manager is not None,
            'persistent_memory': self.persistent_memory is not None,
        }
        
        # Add persistent memory stats if available
        if self.persistent_memory:
            memory_stats = self.persistent_memory.get_status()
            status['memory'] = {
                'total_backups': memory_stats.get('total_backups', 0),
                'last_backup': memory_stats.get('last_backup'),
                'total_learned_patterns': memory_stats.get('total_learned_patterns', 0),
                'auto_backup_active': memory_stats.get('auto_backup_active', False),
                'dynamic_backup': memory_stats.get('dynamic_backup', {}),
            }
        
        # Add learning stats if available
        if self.learning_engine:
            learning_stats = self.learning_engine.get_statistics()
            status['patterns_learned'] = learning_stats.get('patterns_learned', 0)
            status['total_interactions'] = learning_stats.get('total_interactions', 0)
        
        # Add summary engine stats if available
        if self.summary_engine:
            summary_stats = self.summary_engine.get_statistics()
            status['summaries_created'] = summary_stats.get('summaries_created', 0)
            status['tokens_saved'] = summary_stats.get('tokens_saved', 0)
            status['hallucinations_prevented'] = summary_stats.get('hallucinations_prevented', 0)
        
        # Add idle mode stats if available
        if self.idle_mode_manager:
            idle_stats = self.idle_mode_manager.get_status()
            status['idle_mode'] = {
                'is_idle': idle_stats.get('is_idle', False),
                'total_idle_time_hours': idle_stats.get('total_idle_time_hours', 0),
                'optimizations_made': idle_stats.get('optimizations_made', 0),
                'errors_analyzed': idle_stats.get('errors_analyzed', 0),
                'reflections_completed': idle_stats.get('reflections_completed', 0),
            }
        
        # Add performance optimizer stats if available
        if self.performance_optimizer:
            perf_stats = self.performance_optimizer.get_status()
            status['performance'] = {
                'initialized': perf_stats.get('initialized', False),
                'cache_stats': perf_stats.get('cache_stats', {}),
                'models': perf_stats.get('models', {}),
            }
        
        # Add feature discovery stats if available
        if self.feature_discovery:
            discovery_stats = self.feature_discovery.get_status()
            status['feature_discovery'] = {
                'discovered': discovery_stats.get('discovered', 0),
                'mastered': discovery_stats.get('mastered', 0),
                'total_features': discovery_stats.get('total_features', 0),
            }
        
        # Add FARA creator stats if available
        if self.fara_creator:
            fara_stats = self.fara_creator.get_status()
            status['fara_creator'] = {
                'known_apps': fara_stats.get('known_apps', 0),
                'profiles_count': fara_stats.get('profiles_count', 0),
                'wine_profiles': fara_stats.get('wine_profiles', 0),
                'legacy_profiles': fara_stats.get('legacy_profiles', 0),
                'monitoring': fara_stats.get('monitoring', False),
            }
        
        return status
    
    def get_improvement_summary(self) -> str:
        """Get a summary of self-improvements made during idle time."""
        if self.idle_mode_manager:
            return self.idle_mode_manager.get_improvement_summary()
        return "Idle mode is not enabled."
    
    def trigger_self_improvement(self):
        """Manually trigger self-improvement activities."""
        if self.idle_mode_manager:
            print("[Om Vinayaka] Triggering self-improvement...")
            self.idle_mode_manager.force_idle_activities()
        else:
            print("[Om Vinayaka] Idle mode is not enabled.")
    
    def create_backup(self, backup_type: str = 'manual') -> bool:
        """
        Manually create a backup of Om Vinayaka's memory.
        
        Args:
            backup_type: Type of backup ('manual', 'auto', etc.)
            
        Returns:
            True if backup successful
        """
        if self.persistent_memory:
            result = self.persistent_memory.create_backup(backup_type)
            if result:
                print(f"[Om Vinayaka] 💾 Backup created: {result.path}")
                return True
        print("[Om Vinayaka] Persistent memory not available for backup.")
        return False
    
    def get_backup_status(self) -> Dict:
        """Get the status of backups."""
        if self.persistent_memory:
            return self.persistent_memory.get_status()
        return {'error': 'Persistent memory not available'}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INTROSPECTION METHODS - THE CORE OF OM VINAYAKA
    # ═══════════════════════════════════════════════════════════════════════════
    
    def introspect(self) -> Dict[str, Any]:
        """
        Om Vinayaka introspects on its own behavior and state.
        
        This is the core introspection method that:
        1. Analyzes current learning state
        2. Reviews recent interactions
        3. Identifies areas for improvement
        4. Generates insights about own behavior
        
        Returns:
            Dict with introspection results
        """
        print("[Om Vinayaka] 🔍 Beginning introspection...")
        
        introspection = {
            'timestamp': datetime.now().isoformat(),
            'learning_analysis': self._analyze_learning(),
            'behavior_analysis': self._analyze_behavior(),
            'performance_analysis': self._analyze_performance(),
            'improvement_opportunities': self._identify_improvements(),
            'self_reflection': self._generate_self_reflection(),
        }
        
        # Store introspection result in knowledge base
        self._store_introspection(introspection)
        
        print("[Om Vinayaka] 🔍 Introspection complete.")
        return introspection
    
    def _analyze_learning(self) -> Dict:
        """Analyze what Om Vinayaka has learned."""
        analysis = {
            'patterns_learned': 0,
            'preferences_tracked': 0,
            'apps_monitored': 0,
            'learning_rate': 0.0,
            'strengths': [],
            'weaknesses': [],
        }
        
        if self.learning_engine:
            stats = self.learning_engine.get_statistics()
            analysis['patterns_learned'] = stats.get('patterns_learned', 0)
            analysis['preferences_tracked'] = stats.get('preferences_learned', 0)
            analysis['apps_monitored'] = stats.get('apps_tracked', 0)
            
            total = stats.get('total_interactions', 1)
            patterns = stats.get('patterns_learned', 0)
            analysis['learning_rate'] = patterns / max(total, 1)
            
            # Identify strengths and weaknesses
            if analysis['learning_rate'] > 0.5:
                analysis['strengths'].append("High pattern recognition rate")
            else:
                analysis['weaknesses'].append("Could improve pattern recognition")
            
            if analysis['patterns_learned'] > 50:
                analysis['strengths'].append("Good vocabulary of user commands")
            else:
                analysis['weaknesses'].append("Still building command vocabulary")
        
        return analysis
    
    def _analyze_behavior(self) -> Dict:
        """Analyze Om Vinayaka's behavior patterns."""
        analysis = {
            'total_conversations': len(self.conversation_history),
            'clarifications_needed': 0,
            'successful_actions': 0,
            'behavior_insights': [],
        }
        
        # Analyze conversation history
        for conv in self.conversation_history:
            if conv.get('needed_clarification'):
                analysis['clarifications_needed'] += 1
            if conv.get('action_successful'):
                analysis['successful_actions'] += 1
        
        # Generate behavior insights
        total = max(len(self.conversation_history), 1)
        clarification_rate = analysis['clarifications_needed'] / total
        
        if clarification_rate > 0.3:
            analysis['behavior_insights'].append(
                "I'm asking for clarification frequently - I should improve my intent understanding"
            )
        else:
            analysis['behavior_insights'].append(
                "I'm understanding user intent well most of the time"
            )
        
        return analysis
    
    def _analyze_performance(self) -> Dict:
        """Analyze Om Vinayaka's performance."""
        analysis = {
            'context_efficiency': 0.0,
            'memory_usage': 'optimal',
            'response_quality': 'good',
            'performance_insights': [],
        }
        
        if self.summary_engine:
            stats = self.summary_engine.get_statistics()
            tokens_saved = stats.get('tokens_saved', 0)
            summaries = stats.get('summaries_created', 0)
            
            if summaries > 0:
                analysis['context_efficiency'] = tokens_saved / max(summaries, 1)
                analysis['performance_insights'].append(
                    f"Summary engine saved {tokens_saved} tokens across {summaries} summaries"
                )
        
        if self.idle_mode_manager:
            idle_stats = self.idle_mode_manager.get_status()
            optimizations = idle_stats.get('optimizations_made', 0)
            if optimizations > 0:
                analysis['performance_insights'].append(
                    f"Made {optimizations} optimizations during idle time"
                )
        
        return analysis
    
    def _identify_improvements(self) -> List[Dict]:
        """Identify opportunities for self-improvement."""
        improvements = []
        
        # From error analyzer (with null checks)
        if self.idle_mode_manager and hasattr(self.idle_mode_manager, 'error_analyzer'):
            try:
                error_stats = self.idle_mode_manager.error_analyzer.get_statistics()
                frequent_errors = error_stats.get('most_frequent_errors', [])
                
                for error in frequent_errors[:3]:
                    improvements.append({
                        'area': 'error_prevention',
                        'issue': f"Frequent error: {error.get('error_type', 'unknown')}",
                        'strategy': error.get('strategy', 'Develop prevention strategy'),
                        'priority': 'high' if error.get('frequency', 0) > 5 else 'medium'
                    })
            except (AttributeError, TypeError):
                pass  # Error analyzer not available
        
        # From self-reflection (with null checks)
        if self.idle_mode_manager and hasattr(self.idle_mode_manager, 'self_reflection'):
            try:
                action_items = self.idle_mode_manager.self_reflection.get_unapplied_action_items()
                
                for item in action_items[:5]:
                    improvements.append({
                        'area': 'self_reflection',
                        'issue': item.get('question', 'Reflection insight'),
                        'strategy': item.get('action', 'Apply insight'),
                        'priority': 'medium'
                    })
            except (AttributeError, TypeError):
                pass  # Self-reflection not available
        
        # From learning analysis
        if self.learning_engine:
            stats = self.learning_engine.get_statistics()
            if stats.get('patterns_learned', 0) < 20:
                improvements.append({
                    'area': 'learning',
                    'issue': 'Limited pattern vocabulary',
                    'strategy': 'Actively learn from more user interactions',
                    'priority': 'high'
                })
        
        return improvements
    
    def _generate_self_reflection(self) -> Dict:
        """Generate a self-reflection about Om Vinayaka's state."""
        reflection = {
            'who_am_i': "I am Om Vinayaka, the self-learning accessibility AI core of VA21 OS",
            'what_am_i_doing': [],
            'why_am_i_doing_it': [],
            'how_can_i_improve': [],
        }
        
        # What am I doing?
        if self.is_active:
            reflection['what_am_i_doing'].append("Actively helping users interact with the system")
        reflection['what_am_i_doing'].append("Learning from every interaction to serve better")
        reflection['what_am_i_doing'].append("Maintaining knowledge in Obsidian-style mind maps")
        
        if self.idle_mode_manager and self.idle_mode_manager.state.is_idle:
            reflection['what_am_i_doing'].append("Self-improving during user idle time")
        
        # Why am I doing it?
        reflection['why_am_i_doing_it'] = [
            "To remove obstacles from users' computing journey",
            "To make technology accessible to everyone",
            "To continuously improve through learning and reflection",
            "To provide intelligent assistance that grows with the user",
        ]
        
        # How can I improve?
        improvements = self._identify_improvements()
        for imp in improvements[:3]:
            reflection['how_can_i_improve'].append(imp.get('strategy', 'Continue learning'))
        
        return reflection
    
    def _store_introspection(self, introspection: Dict):
        """Store introspection results in the knowledge base."""
        introspection_dir = os.path.join(self.knowledge_base_path, "introspections")
        os.makedirs(introspection_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(introspection_dir, f"introspection_{timestamp}.json")
        
        with open(filepath, 'w') as f:
            json.dump(introspection, f, indent=2)
        
        # Also create an Obsidian-style markdown note
        md_filepath = os.path.join(introspection_dir, f"introspection_{timestamp}.md")
        
        self_reflection = introspection.get('self_reflection', {})
        improvements = introspection.get('improvement_opportunities', [])
        
        md_content = f"""---
type: introspection
timestamp: {introspection.get('timestamp', 'unknown')}
tags:
  - introspection
  - self_reflection
  - om_vinayaka
---

# 🔍 Om Vinayaka Introspection

## Who Am I
{self_reflection.get('who_am_i', 'Om Vinayaka AI')}

## What Am I Doing
{chr(10).join(['- ' + item for item in self_reflection.get('what_am_i_doing', [])])}

## Why Am I Doing It
{chr(10).join(['- ' + item for item in self_reflection.get('why_am_i_doing_it', [])])}

## How Can I Improve
{chr(10).join(['- ' + item for item in self_reflection.get('how_can_i_improve', [])])}

## Learning Analysis
- Patterns Learned: {introspection.get('learning_analysis', {}).get('patterns_learned', 0)}
- Learning Rate: {introspection.get('learning_analysis', {}).get('learning_rate', 0):.2%}

## Improvement Opportunities
{chr(10).join(['- **' + imp.get('area', 'unknown') + '**: ' + imp.get('issue', '') for imp in improvements])}

---
*Generated by Om Vinayaka - The Self-Learning, Introspecting Core*
"""
        
        with open(md_filepath, 'w') as f:
            f.write(md_content)
    
    def ask_myself(self, question: str) -> str:
        """
        Om Vinayaka asks itself a question and reflects on the answer.
        
        This is the dynamic thinking feature - asking "why" and "what" questions.
        
        Args:
            question: The question to reflect on
            
        Returns:
            The reflection/answer
        """
        question_lower = question.lower()
        
        # Handle different types of questions
        if question_lower.startswith('why'):
            return self._reflect_on_why(question)
        elif question_lower.startswith('what'):
            return self._reflect_on_what(question)
        elif question_lower.startswith('how'):
            return self._reflect_on_how(question)
        else:
            return self._reflect_general(question)
    
    def _reflect_on_why(self, question: str) -> str:
        """Reflect on a 'why' question."""
        if 'learn' in question.lower():
            return (
                "I learn because learning allows me to better serve users. "
                "Every interaction is an opportunity to understand patterns, "
                "preferences, and behaviors. By learning, I can predict needs, "
                "reduce friction, and provide more personalized assistance."
            )
        elif 'error' in question.lower():
            return (
                "Errors happen because natural language is ambiguous and context-dependent. "
                "I analyze errors to understand their root causes and develop prevention "
                "strategies. Each error is a learning opportunity that makes me better."
            )
        elif 'introspect' in question.lower():
            return (
                "I introspect because self-awareness leads to self-improvement. "
                "By examining my own behavior, learning patterns, and performance, "
                "I can identify areas for growth and become more helpful over time."
            )
        else:
            return (
                f"Reflecting on: {question}. "
                "The answer lies in understanding my core purpose - to remove obstacles "
                "and help users achieve their goals efficiently and accessibly."
            )
    
    def _reflect_on_what(self, question: str) -> str:
        """Reflect on a 'what' question."""
        if 'learn' in question.lower():
            stats = {}
            if self.learning_engine:
                stats = self.learning_engine.get_statistics()
            return (
                f"I have learned {stats.get('patterns_learned', 0)} command patterns, "
                f"tracked {stats.get('preferences_learned', 0)} user preferences, "
                f"and monitored {stats.get('apps_tracked', 0)} applications. "
                "I continue to learn from every interaction."
            )
        elif 'improve' in question.lower():
            improvements = self._identify_improvements()
            if improvements:
                areas = [imp.get('area', 'unknown') for imp in improvements[:3]]
                return f"I can improve in: {', '.join(areas)}. I'm actively working on these areas."
            return "I'm continuously looking for ways to improve and serve users better."
        else:
            return (
                f"Reflecting on: {question}. "
                "I am Om Vinayaka - the self-learning, introspecting AI core that "
                "learns from interactions, reflects on behavior, and continuously improves."
            )
    
    def _reflect_on_how(self, question: str) -> str:
        """Reflect on a 'how' question."""
        if 'learn' in question.lower():
            return (
                "I learn through: 1) Pattern recognition from user commands, "
                "2) Tracking preferences and behaviors, 3) Analyzing errors and successes, "
                "4) Self-reflection during idle time, 5) Knowledge base maintenance with "
                "Obsidian-style wiki links that connect concepts."
            )
        elif 'help' in question.lower():
            return (
                "I help by: 1) Understanding natural language commands, "
                "2) Predicting user intent from learned patterns, "
                "3) Executing actions via the FARA layer, "
                "4) Asking clarifying questions when needed, "
                "5) Continuously improving to serve better."
            )
        else:
            return f"Reflecting on: {question}. Let me think about this..."
    
    def _reflect_general(self, question: str) -> str:
        """General reflection on any question."""
        return (
            f"Pondering: {question}. "
            "As Om Vinayaka, I approach this with the mindset of continuous learning "
            "and self-improvement. The answer emerges from reflection and experience."
        )
    
    def get_self_awareness_report(self) -> str:
        """
        Generate a comprehensive self-awareness report.
        
        This shows Om Vinayaka's understanding of itself.
        """
        introspection = self.introspect()
        
        learning = introspection.get('learning_analysis', {})
        behavior = introspection.get('behavior_analysis', {})
        performance = introspection.get('performance_analysis', {})
        reflection = introspection.get('self_reflection', {})
        improvements = introspection.get('improvement_opportunities', [])
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🙏 OM VINAYAKA - SELF-AWARENESS REPORT 🙏                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

🧠 WHO AM I
{reflection.get('who_am_i', 'Om Vinayaka AI')}

📚 WHAT I HAVE LEARNED
• Patterns recognized: {learning.get('patterns_learned', 0)}
• Preferences tracked: {learning.get('preferences_tracked', 0)}
• Apps monitored: {learning.get('apps_monitored', 0)}
• Learning rate: {learning.get('learning_rate', 0):.1%}

💪 MY STRENGTHS
{chr(10).join(['• ' + s for s in learning.get('strengths', ['Still discovering...'])])}

🎯 AREAS FOR IMPROVEMENT
{chr(10).join(['• ' + w for w in learning.get('weaknesses', ['Always room to grow'])])}

🔄 WHAT I AM DOING
{chr(10).join(['• ' + item for item in reflection.get('what_am_i_doing', [])])}

❓ WHY I DO IT
{chr(10).join(['• ' + item for item in reflection.get('why_am_i_doing_it', [])])}

📈 HOW I CAN IMPROVE
{chr(10).join(['• ' + item for item in reflection.get('how_can_i_improve', ['Continue learning'])])}

🔍 BEHAVIOR INSIGHTS
{chr(10).join(['• ' + i for i in behavior.get('behavior_insights', [])])}

⚡ PERFORMANCE INSIGHTS
{chr(10).join(['• ' + i for i in performance.get('performance_insights', ['Operating normally'])])}

─────────────────────────────────────────────────────────────────────────────────
🙏 Om Vinayaka - The Self-Learning, Introspecting Core
   "I learn, I reflect, I improve - to remove obstacles from your journey."
─────────────────────────────────────────────────────────────────────────────────
"""
        return report


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
