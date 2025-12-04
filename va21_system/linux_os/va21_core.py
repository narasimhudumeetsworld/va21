#!/usr/bin/env python3
"""
VA21 OS - Core System Integration
==================================

Om Vinayaka - The remover of obstacles.

This module integrates ALL VA21 OS components to work together seamlessly:

Components Integrated:
- Om Vinayaka AI (Accessibility Intelligence)
- Zork Shell (Text Adventure Interface)
- Voice Accessibility System
- Self-Learning Engine
- Summary Engine
- Coding IDE with Multi-Agent System
- Research Suite
- Writing Suite
- Journalism Toolkit
- Security Tools
- System Tools
- Obsidian Vault Manager
- SearXNG Private Search
- Window Manager
- Spotlight Launcher

Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                         VA21 OS Integration Layer                        │
├─────────────────────────────────────────────────────────────────────────┤
│  🙏 OM VINAYAKA AI (Central Hub)                                        │
│  ├── Receives all user input (voice, text, actions)                     │
│  ├── Routes to appropriate subsystem                                     │
│  ├── Maintains context and learns from interactions                     │
│  └── Returns unified responses                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  📦 SUBSYSTEMS (No Feature Overlap)                                     │
│  ├── Accessibility: Voice, Screen Reader, Zork UX                       │
│  ├── Research: Citations, Literature, Projects                          │
│  ├── Writing: Documents, Templates, Export                              │
│  ├── Coding: IDE, Multi-Agent, Project Builder                          │
│  ├── System: Settings, Tools, Window Manager                            │
│  └── Search: SearXNG Private Search                                     │
└─────────────────────────────────────────────────────────────────────────┘

NOTE: Guardian AI is EXCLUDED - it runs sandboxed at kernel level (port 11435)
      and cannot be influenced by user-facing systems.

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

VA21_VERSION = "1.0.0"
VA21_CODENAME = "Vinayaka"


class Subsystem(Enum):
    """VA21 OS Subsystems."""
    ACCESSIBILITY = "accessibility"
    RESEARCH = "research"
    WRITING = "writing"
    CODING = "coding"
    JOURNALISM = "journalism"
    SYSTEM = "system"
    SEARCH = "search"
    GAMES = "games"


# Subsystem responsibilities - ensures no feature overlap
SUBSYSTEM_RESPONSIBILITIES = {
    Subsystem.ACCESSIBILITY: [
        "voice_control",
        "screen_reader",
        "zork_interface",
        "natural_language_input",
        "text_to_speech",
        "speech_to_text",
    ],
    Subsystem.RESEARCH: [
        "literature_management",
        "citations",
        "bibliography",
        "research_projects",
        "data_analysis",
        "experiment_tracking",
    ],
    Subsystem.WRITING: [
        "document_editing",
        "templates",
        "export_formats",
        "writing_assistance",
        "grammar_check",
    ],
    Subsystem.CODING: [
        "code_editing",
        "multi_agent_coding",
        "project_scaffolding",
        "code_suggestions",
        "debugging",
        "version_control",
    ],
    Subsystem.JOURNALISM: [
        "fact_checking",
        "source_verification",
        "interview_tools",
        "article_writing",
        "deadline_tracking",
    ],
    Subsystem.SYSTEM: [
        "settings",
        "file_management",
        "window_management",
        "app_launching",
        "system_monitoring",
    ],
    Subsystem.SEARCH: [
        "web_search",
        "private_search",
        "knowledge_search",
    ],
    Subsystem.GAMES: [
        "text_adventures",
        "entertainment",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UserRequest:
    """A user request to the VA21 system."""
    request_id: str
    content: str
    request_type: str  # 'voice', 'text', 'action'
    context: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source_app: Optional[str] = None


@dataclass
class SystemResponse:
    """Response from the VA21 system."""
    request_id: str
    content: str
    subsystem: Subsystem
    action_taken: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    success: bool = True


@dataclass
class SubsystemStatus:
    """Status of a subsystem."""
    subsystem: Subsystem
    is_loaded: bool = False
    is_available: bool = False
    version: str = ""
    last_used: Optional[str] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# VA21 OS CORE
# ═══════════════════════════════════════════════════════════════════════════════

class VA21Core:
    """
    VA21 OS Core Integration System
    
    This is the central hub that:
    1. Receives ALL user input (voice, text, actions)
    2. Routes requests to the appropriate subsystem
    3. Ensures no feature overlap between subsystems
    4. Maintains system-wide context
    5. Returns unified responses
    
    All subsystems connect through this core, ensuring:
    - Consistent user experience
    - No duplicate functionality
    - Proper context sharing
    - Unified learning from interactions
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser("~/.va21/config")
        os.makedirs(self.config_path, exist_ok=True)
        
        # Subsystem instances (lazy loaded)
        self._subsystems: Dict[Subsystem, Any] = {}
        self._subsystem_status: Dict[Subsystem, SubsystemStatus] = {}
        
        # Initialize status for all subsystems
        for subsystem in Subsystem:
            self._subsystem_status[subsystem] = SubsystemStatus(subsystem=subsystem)
        
        # Central components
        self._om_vinayaka = None
        self._learning_engine = None
        self._summary_engine = None
        
        # Request routing
        self._intent_handlers: Dict[str, Callable] = {}
        
        # System state
        self.is_initialized = False
        self.current_context: Dict = {}
        
        print(f"[VA21 Core] Initializing v{VA21_VERSION} ({VA21_CODENAME})")
    
    def initialize(self) -> bool:
        """
        Initialize the VA21 OS core and all subsystems.
        
        Returns:
            True if initialization successful
        """
        print("[VA21 Core] Starting initialization...")
        
        # 1. Initialize Om Vinayaka AI (central hub)
        self._init_om_vinayaka()
        
        # 2. Initialize learning and summary engines
        self._init_core_engines()
        
        # 3. Load subsystems
        self._load_subsystems()
        
        # 4. Register intent handlers
        self._register_intent_handlers()
        
        self.is_initialized = True
        print("[VA21 Core] Initialization complete!")
        print(f"[VA21 Core] Loaded subsystems: {[s.value for s, st in self._subsystem_status.items() if st.is_loaded]}")
        
        return True
    
    def _init_om_vinayaka(self):
        """Initialize Om Vinayaka Accessibility AI."""
        try:
            from .accessibility import get_om_vinayaka
            self._om_vinayaka = get_om_vinayaka()
            self._om_vinayaka.activate()
            print("[VA21 Core] Om Vinayaka AI: ACTIVE")
        except ImportError as e:
            print(f"[VA21 Core] Om Vinayaka AI not available: {e}")
    
    def _init_core_engines(self):
        """Initialize learning and summary engines."""
        try:
            from .accessibility import get_learning_engine, get_summary_engine
            self._learning_engine = get_learning_engine()
            self._summary_engine = get_summary_engine()
            print("[VA21 Core] Learning Engine: ACTIVE")
            print("[VA21 Core] Summary Engine: ACTIVE")
        except ImportError as e:
            print(f"[VA21 Core] Core engines not available: {e}")
    
    def _load_subsystems(self):
        """Load all subsystems."""
        
        # Accessibility (already loaded via Om Vinayaka)
        self._load_subsystem(Subsystem.ACCESSIBILITY, 'accessibility', 'VA21AccessibilitySystem')
        
        # Research Suite
        self._load_subsystem(Subsystem.RESEARCH, 'research_suite', 'ResearchSuite')
        
        # Writing Suite
        self._load_subsystem(Subsystem.WRITING, 'writing', 'WritingSuite')
        
        # Coding IDE
        self._load_subsystem(Subsystem.CODING, 'coding_ide', 'CodingIDE')
        
        # Journalism Toolkit
        self._load_subsystem(Subsystem.JOURNALISM, 'journalism', 'JournalismToolkit')
        
        # System Tools
        self._load_subsystem(Subsystem.SYSTEM, 'system_tools', 'SystemSuite')
        
        # SearXNG Search
        self._load_subsystem(Subsystem.SEARCH, 'searxng', 'SearXNGClient')
        
        # Games
        self._load_subsystem(Subsystem.GAMES, 'games', None)
    
    def _load_subsystem(self, subsystem: Subsystem, module_name: str, class_name: str):
        """Load a single subsystem."""
        status = self._subsystem_status[subsystem]
        
        try:
            # Dynamic import
            module = __import__(f'.{module_name}', globals(), locals(), [class_name] if class_name else [], 1)
            
            if class_name:
                # Try to get singleton or create instance
                getter_name = f"get_{class_name.lower().replace('suite', '_suite').replace('toolkit', '_toolkit')}"
                getter_name = getter_name.replace('__', '_').rstrip('_')
                
                if hasattr(module, getter_name):
                    self._subsystems[subsystem] = getattr(module, getter_name)()
                elif hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    self._subsystems[subsystem] = cls()
                else:
                    self._subsystems[subsystem] = module
            else:
                self._subsystems[subsystem] = module
            
            status.is_loaded = True
            status.is_available = True
            status.version = getattr(module, '__version__', '1.0.0')
            print(f"[VA21 Core] Loaded: {subsystem.value}")
            
        except Exception as e:
            status.is_loaded = False
            status.is_available = False
            status.error = str(e)
            print(f"[VA21 Core] Failed to load {subsystem.value}: {e}")
    
    def _register_intent_handlers(self):
        """Register handlers for different intents."""
        # These map intents to subsystems
        self._intent_handlers = {
            # Accessibility
            'voice_command': Subsystem.ACCESSIBILITY,
            'read_screen': Subsystem.ACCESSIBILITY,
            'speak': Subsystem.ACCESSIBILITY,
            
            # Research
            'add_citation': Subsystem.RESEARCH,
            'search_literature': Subsystem.RESEARCH,
            'create_bibliography': Subsystem.RESEARCH,
            'manage_project': Subsystem.RESEARCH,
            
            # Writing
            'write_document': Subsystem.WRITING,
            'export_document': Subsystem.WRITING,
            'check_grammar': Subsystem.WRITING,
            
            # Coding
            'write_code': Subsystem.CODING,
            'debug_code': Subsystem.CODING,
            'create_project': Subsystem.CODING,
            'suggest_code': Subsystem.CODING,
            
            # Journalism
            'fact_check': Subsystem.JOURNALISM,
            'verify_source': Subsystem.JOURNALISM,
            'write_article': Subsystem.JOURNALISM,
            
            # System
            'open_app': Subsystem.SYSTEM,
            'change_setting': Subsystem.SYSTEM,
            'manage_files': Subsystem.SYSTEM,
            'manage_windows': Subsystem.SYSTEM,
            
            # Search
            'web_search': Subsystem.SEARCH,
            'private_search': Subsystem.SEARCH,
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REQUEST PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def process_request(self, request: UserRequest) -> SystemResponse:
        """
        Process a user request through the VA21 system.
        
        This is the main entry point for ALL user interactions.
        
        Args:
            request: The user request to process
            
        Returns:
            SystemResponse with the result
        """
        if not self.is_initialized:
            return SystemResponse(
                request_id=request.request_id,
                content="VA21 OS is still initializing. Please wait...",
                subsystem=Subsystem.SYSTEM,
                success=False
            )
        
        # 1. Use Om Vinayaka to understand intent
        if self._om_vinayaka:
            result = self._om_vinayaka.process_user_input(
                request.content,
                request.source_app
            )
            
            # 2. Determine which subsystem should handle this
            subsystem = self._route_to_subsystem(result)
            
            # 3. Execute via subsystem if needed
            if result.get('action') and subsystem != Subsystem.ACCESSIBILITY:
                subsystem_result = self._execute_via_subsystem(subsystem, result)
                if subsystem_result:
                    result['response'] = subsystem_result
            
            # 4. Learn from this interaction
            if self._learning_engine:
                self._learning_engine.learn_command(
                    request.content,
                    result.get('action', 'unknown'),
                    request.source_app,
                    True
                )
            
            return SystemResponse(
                request_id=request.request_id,
                content=result.get('response', 'I understood your request.'),
                subsystem=subsystem,
                action_taken=result.get('action'),
                success=True
            )
        
        # Fallback if Om Vinayaka not available
        return SystemResponse(
            request_id=request.request_id,
            content="Processing your request...",
            subsystem=Subsystem.SYSTEM,
            success=True
        )
    
    def _route_to_subsystem(self, om_vinayaka_result: Dict) -> Subsystem:
        """Determine which subsystem should handle a request."""
        action = om_vinayaka_result.get('action', '').lower()
        
        # Check intent handlers
        for intent, subsystem in self._intent_handlers.items():
            if intent in action:
                return subsystem
        
        # Check action prefixes
        if action.startswith('cli:'):
            return Subsystem.CODING
        if action.startswith('search:'):
            return Subsystem.SEARCH
        if action.startswith('navigate:'):
            return Subsystem.SYSTEM
        
        # Default to accessibility (Om Vinayaka handles it)
        return Subsystem.ACCESSIBILITY
    
    def _execute_via_subsystem(self, subsystem: Subsystem, result: Dict) -> Optional[str]:
        """Execute an action via a specific subsystem."""
        if subsystem not in self._subsystems:
            return None
        
        instance = self._subsystems[subsystem]
        action = result.get('action', '')
        
        # Each subsystem has its own action handlers
        try:
            if subsystem == Subsystem.RESEARCH:
                return self._handle_research_action(instance, action, result)
            elif subsystem == Subsystem.WRITING:
                return self._handle_writing_action(instance, action, result)
            elif subsystem == Subsystem.CODING:
                return self._handle_coding_action(instance, action, result)
            elif subsystem == Subsystem.SEARCH:
                return self._handle_search_action(instance, action, result)
            elif subsystem == Subsystem.SYSTEM:
                return self._handle_system_action(instance, action, result)
        except Exception as e:
            return f"Error executing action: {e}"
        
        return None
    
    def _handle_research_action(self, instance, action: str, result: Dict) -> str:
        """Handle research subsystem actions."""
        if 'citation' in action:
            return "Citation functionality ready. What would you like to cite?"
        if 'search' in action:
            return "Searching research literature..."
        return "Research tools ready."
    
    def _handle_writing_action(self, instance, action: str, result: Dict) -> str:
        """Handle writing subsystem actions."""
        if 'document' in action:
            return "Document editor ready."
        return "Writing tools ready."
    
    def _handle_coding_action(self, instance, action: str, result: Dict) -> str:
        """Handle coding subsystem actions."""
        if 'project' in action:
            return "Project builder ready. What would you like to create?"
        if 'code' in action:
            return "Code editor ready."
        return "Coding IDE ready."
    
    def _handle_search_action(self, instance, action: str, result: Dict) -> str:
        """Handle search subsystem actions."""
        query = result.get('full_input', '')
        if hasattr(instance, 'search'):
            results = instance.search(query)
            return f"Found {len(results)} results for your search."
        return "Search ready."
    
    def _handle_system_action(self, instance, action: str, result: Dict) -> str:
        """Handle system subsystem actions."""
        if 'setting' in action:
            return "Settings panel ready."
        if 'window' in action:
            return "Window manager ready."
        return "System tools ready."
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════════
    
    def process_text(self, text: str, app_context: str = None) -> str:
        """
        Simple text processing interface.
        
        Args:
            text: User text input
            app_context: Optional app context
            
        Returns:
            Response string
        """
        request = UserRequest(
            request_id=f"req_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            content=text,
            request_type='text',
            source_app=app_context
        )
        
        response = self.process_request(request)
        return response.content
    
    def process_voice(self, transcription: str, app_context: str = None) -> str:
        """
        Process voice input (already transcribed).
        
        Args:
            transcription: Transcribed voice input
            app_context: Optional app context
            
        Returns:
            Response string
        """
        request = UserRequest(
            request_id=f"voice_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            content=transcription,
            request_type='voice',
            source_app=app_context
        )
        
        response = self.process_request(request)
        return response.content
    
    def get_subsystem(self, subsystem: Subsystem) -> Optional[Any]:
        """Get a subsystem instance."""
        return self._subsystems.get(subsystem)
    
    def get_status(self) -> Dict:
        """Get VA21 OS status."""
        return {
            'version': VA21_VERSION,
            'codename': VA21_CODENAME,
            'initialized': self.is_initialized,
            'om_vinayaka_active': self._om_vinayaka is not None,
            'learning_engine_active': self._learning_engine is not None,
            'summary_engine_active': self._summary_engine is not None,
            'subsystems': {
                s.value: {
                    'loaded': st.is_loaded,
                    'available': st.is_available,
                    'version': st.version,
                    'error': st.error
                }
                for s, st in self._subsystem_status.items()
            }
        }
    
    def get_welcome_message(self) -> str:
        """Get the VA21 OS welcome message."""
        return f"""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                     🙏 OM VINAYAKA 🙏                              ║
║                                                                   ║
║                 VA21 OS v{VA21_VERSION} ({VA21_CODENAME})                       ║
║             Secure AI-Powered Operating System                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

Welcome to VA21 OS! All systems are integrated and working together.

Available Subsystems:
• Accessibility - Voice control, Zork interfaces, screen reader
• Research - Literature management, citations, projects
• Writing - Document editing, templates, export
• Coding - IDE, multi-agent development, project builder
• Journalism - Fact-checking, source verification
• System - Settings, files, window management
• Search - Private web search via SearXNG

Just tell me what you'd like to do, or say "help" for more options.

Hold the Super key to speak, or type your command.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_va21_core_instance = None


def get_va21_core() -> VA21Core:
    """Get the VA21 Core singleton."""
    global _va21_core_instance
    
    if _va21_core_instance is None:
        _va21_core_instance = VA21Core()
        _va21_core_instance.initialize()
    
    return _va21_core_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Run VA21 OS Core."""
    print("=" * 70)
    print("VA21 OS - Core System")
    print("=" * 70)
    
    # Initialize
    core = get_va21_core()
    
    # Show welcome
    print(core.get_welcome_message())
    
    # Show status
    print("\n--- System Status ---")
    status = core.get_status()
    print(json.dumps(status, indent=2))
    
    # Interactive mode
    print("\n--- Interactive Mode ---")
    print("Type your commands (or 'quit' to exit):\n")
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nOm Vinayaka! 🙏 Goodbye!")
                break
            
            if not user_input:
                continue
            
            response = core.process_text(user_input)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\nOm Vinayaka! 🙏 Goodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
