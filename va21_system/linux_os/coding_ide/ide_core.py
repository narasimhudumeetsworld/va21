#!/usr/bin/env python3
"""
VA21 OS - Coding IDE Core
==========================

Om Vinayaka - The heart of intelligent development.

The IDE Core provides:
- ChatGPT-style chatbox interface for interactive development
- FARA layer integration for voice assistance
- Summary Engine integration to prevent context overflow
- Integration with all coding IDE components
- Integration with VA21 OS components (Obsidian, Writing Suite, Research Suite)
- Project management and workflow orchestration
- SearXNG integration for research
- Full-stack development workflow

This is the main entry point for the VA21 Coding IDE, providing
a conversational interface where users can describe what they
want to build and receive intelligent guidance and generated code.

Integrated VA21 OS Components:
- Summary Engine: Prevents AI context overflow and hallucinations
- Obsidian Vault: Knowledge storage and wiki-style notes
- Writing Suite: Documentation and article generation
- Research Suite: Literature management and citations
- SearXNG: Privacy-respecting web search
- FARA Layer: Voice assistance and UI automation
- Om Vinayaka AI: Accessibility and natural language understanding

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.
"""

import os
import sys
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.progress import Progress
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Context limit for AI systems (managed by Summary Engine)
AI_CONTEXT_SYSTEM = 'coding_ide'
AI_CONTEXT_LIMIT = 16000  # tokens


class IDEState(Enum):
    """States of the IDE."""
    IDLE = "idle"
    GATHERING_REQUIREMENTS = "gathering_requirements"
    SUGGESTING = "suggesting"
    PLANNING = "planning"
    BUILDING = "building"
    REVIEWING = "reviewing"


@dataclass
class ChatMessage:
    """A message in the chat interface."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    message_type: str = "text"  # "text", "code", "suggestion", "plan", "progress"


@dataclass
class ProjectContext:
    """Current project context."""
    name: Optional[str] = None
    description: Optional[str] = None
    requirements: Dict = field(default_factory=dict)
    suggestions: Dict = field(default_factory=dict)
    build_plan: Optional[str] = None
    project_path: Optional[str] = None
    language: Optional[str] = None
    stack: Optional[str] = None
    status: str = "not_started"


class CodingIDE:
    """
    VA21 Coding IDE - Main Interface
    
    A conversational coding environment that:
    
    1. Receives user's app/idea description in natural language
    2. Asks clarifying questions about:
       - Target systems/platforms
       - Preferred programming languages
       - Features and requirements
    3. Suggests best languages and technologies using SuggestEngine
    4. Plans the development approach
    5. Distributes work to specialized agents
    6. Manages context dynamically
    7. Delivers complete full-stack applications
    
    Integration points:
    - SuggestEngine: Language and stack recommendations
    - AIHelper: AI-powered assistance with API key support
    - MultiAgentOrchestrator: Task distribution and coordination
    - ProjectBuilder: Project scaffolding and file generation
    - SearXNG: Web search for best practices
    - FARA Layer: Voice assistance and accessibility
    
    The chatbox interface provides a ChatGPT-like experience
    specifically designed for software development tasks.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize the Coding IDE."""
        self.console = Console() if RICH_AVAILABLE else None
        
        # State management
        self.state = IDEState.IDLE
        self.project_context = ProjectContext()
        self.chat_history: List[ChatMessage] = []
        self.clarification_needed: List[str] = []
        
        # Initialize components (lazy loading)
        self._suggest_engine = None
        self._ai_helper = None
        self._orchestrator = None
        self._project_builder = None
        self._searxng = None
        self._fara_layer = None
        self._om_vinayaka = None
        
        # New VA21 OS integrations
        self._summary_engine = None      # Context management to prevent overflow
        self._obsidian_vault = None      # Knowledge storage
        self._writing_suite = None       # Documentation generation
        self._research_suite = None      # Research and citations
        self._zork_manager = None        # Zork UX generator for assistive users
        self._zork_interface = None      # Current Zork interface for IDE
        
        # Callbacks for UI integration
        self.on_message: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
        
        # Add system welcome message
        self._add_system_message(self._get_welcome_message())
        
        print(f"[CodingIDE] Initialized v{self.VERSION}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LAZY LOADING OF COMPONENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def suggest_engine(self):
        """Lazy load SuggestEngine."""
        if self._suggest_engine is None:
            try:
                from .suggest_engine import get_suggest_engine
                self._suggest_engine = get_suggest_engine(
                    searxng_client=self.searxng,
                    ai_helper=self.ai_helper
                )
            except ImportError as e:
                print(f"[CodingIDE] SuggestEngine not available: {e}")
        return self._suggest_engine
    
    @property
    def ai_helper(self):
        """Lazy load AIHelper."""
        if self._ai_helper is None:
            try:
                from .ai_helper import get_ai_helper
                self._ai_helper = get_ai_helper()
            except ImportError as e:
                print(f"[CodingIDE] AIHelper not available: {e}")
        return self._ai_helper
    
    @property
    def orchestrator(self):
        """Lazy load MultiAgentOrchestrator."""
        if self._orchestrator is None:
            try:
                from .multi_agent import get_orchestrator
                self._orchestrator = get_orchestrator(self.ai_helper)
            except ImportError as e:
                print(f"[CodingIDE] Orchestrator not available: {e}")
        return self._orchestrator
    
    @property
    def project_builder(self):
        """Lazy load ProjectBuilder."""
        if self._project_builder is None:
            try:
                from .project_builder import get_project_builder
                self._project_builder = get_project_builder()
            except ImportError as e:
                print(f"[CodingIDE] ProjectBuilder not available: {e}")
        return self._project_builder
    
    @property
    def searxng(self):
        """Lazy load SearXNG client."""
        if self._searxng is None:
            try:
                from ..searxng.searxng_client import get_searxng
                self._searxng = get_searxng()
            except ImportError:
                pass
        return self._searxng
    
    @property
    def fara_layer(self):
        """Lazy load FARA layer."""
        if self._fara_layer is None:
            try:
                from ..zork_shell.zork_interface import FARALayer
                self._fara_layer = FARALayer()
            except ImportError:
                pass
        return self._fara_layer
    
    @property
    def om_vinayaka(self):
        """Lazy load Om Vinayaka AI for voice assistance."""
        if self._om_vinayaka is None:
            try:
                from ..accessibility.om_vinayaka_ai import get_om_vinayaka
                self._om_vinayaka = get_om_vinayaka(
                    fara_layer=self.fara_layer
                )
            except ImportError:
                pass
        return self._om_vinayaka
    
    @property
    def summary_engine(self):
        """
        Lazy load Summary Engine for context management.
        
        The Summary Engine prevents AI context overflow by:
        - Monitoring context size vs limits
        - Automatically summarizing when approaching limits
        - Preserving full content in knowledge base
        - Sending optimized summaries to AI
        """
        if self._summary_engine is None:
            try:
                from ..accessibility.summary_engine import get_summary_engine
                self._summary_engine = get_summary_engine()
                print("[CodingIDE] Summary Engine loaded - context overflow protection enabled")
            except ImportError as e:
                print(f"[CodingIDE] Summary Engine not available: {e}")
        return self._summary_engine
    
    @property
    def obsidian_vault(self):
        """
        Lazy load Obsidian Vault Manager for knowledge storage.
        
        Provides wiki-style knowledge storage for:
        - Project documentation
        - Code snippets
        - Research notes
        - Mind maps
        """
        if self._obsidian_vault is None:
            try:
                from ..obsidian.vault_manager import get_vault_manager
                self._obsidian_vault = get_vault_manager()
                print("[CodingIDE] Obsidian Vault connected for knowledge storage")
            except ImportError as e:
                print(f"[CodingIDE] Obsidian Vault not available: {e}")
        return self._obsidian_vault
    
    @property
    def writing_suite(self):
        """
        Lazy load Writing Suite for documentation generation.
        
        Enables:
        - README generation
        - API documentation
        - User guides
        - Technical documentation
        """
        if self._writing_suite is None:
            try:
                from ..writing.writing_suite import get_writing_suite
                self._writing_suite = get_writing_suite()
                print("[CodingIDE] Writing Suite loaded for documentation")
            except ImportError as e:
                print(f"[CodingIDE] Writing Suite not available: {e}")
        return self._writing_suite
    
    @property
    def research_suite(self):
        """
        Lazy load Research Suite for research tools.
        
        Provides:
        - Literature management
        - Citation generation
        - Reference tracking
        - Research organization
        """
        if self._research_suite is None:
            try:
                from ..research_suite.research_tools import get_research_suite
                self._research_suite = get_research_suite()
                print("[CodingIDE] Research Suite loaded")
            except ImportError as e:
                print(f"[CodingIDE] Research Suite not available: {e}")
        return self._research_suite
    
    @property
    def zork_manager(self):
        """
        Lazy load Zork UX Generator/Manager for assistive users.
        
        The Zork layer provides:
        - Text adventure style interface
        - Natural language command processing
        - Room-based navigation metaphor
        - Accessibility for voice users
        """
        if self._zork_manager is None:
            try:
                from ..accessibility.app_zork_generator import AppZorkManager
                self._zork_manager = AppZorkManager()
                # Register the Coding IDE itself as an app
                self._zork_interface = self._create_ide_zork_interface()
                print("[CodingIDE] Zork UX layer enabled for assistive users")
            except ImportError as e:
                print(f"[CodingIDE] Zork Manager not available: {e}")
        return self._zork_manager
    
    def _create_ide_zork_interface(self):
        """Create a Zork interface specifically for the Coding IDE."""
        try:
            from ..accessibility.app_zork_generator import (
                AppZorkInterface, ZorkRoom
            )
            
            rooms = {
                'entrance': ZorkRoom(
                    room_id='entrance',
                    name='IDE Entrance',
                    description='You stand at the entrance of the VA21 Coding IDE.',
                    long_description='You stand at the entrance of the VA21 Coding IDE. '
                                     'A warm glow emanates from within. The spirit of Om Vinayaka '
                                     'welcomes developers of all abilities.',
                    exits={'forward': 'main_hall'},
                    items=['help', 'status'],
                    ui_mapping={}
                ),
                'main_hall': ZorkRoom(
                    room_id='main_hall',
                    name='Main Development Hall',
                    description='You are in the main development hall.',
                    long_description='You are in the main development hall. Code flows like '
                                     'rivers through channels of light. Multiple workstations '
                                     'await your creative commands.',
                    exits={'back': 'entrance', 'north': 'suggestion_chamber', 
                           'east': 'build_workshop', 'west': 'research_library'},
                    items=['new_project', 'describe_idea', 'chat', 'voice_command'],
                    ui_mapping={}
                ),
                'suggestion_chamber': ZorkRoom(
                    room_id='suggestion_chamber',
                    name='Suggestion Chamber',
                    description='You enter the Suggestion Chamber.',
                    long_description='You enter the Suggestion Chamber where the Suggest Engine '
                                     'analyzes your ideas and recommends the best technologies, '
                                     'languages, and architectures for your project.',
                    exits={'south': 'main_hall'},
                    items=['suggest_language', 'suggest_stack', 'compare_options'],
                    ui_mapping={}
                ),
                'build_workshop': ZorkRoom(
                    room_id='build_workshop',
                    name='Build Workshop',
                    description='You enter the Build Workshop.',
                    long_description='You enter the Build Workshop where multiple AI agents '
                                     'collaborate to construct your application. Each agent '
                                     'specializes in different aspects: frontend, backend, '
                                     'database, testing, and more.',
                    exits={'west': 'main_hall'},
                    items=['start_build', 'check_progress', 'view_agents', 'review_code'],
                    ui_mapping={}
                ),
                'research_library': ZorkRoom(
                    room_id='research_library',
                    name='Research Library',
                    description='You enter the Research Library.',
                    long_description='You enter the Research Library where you can search for '
                                     'documentation, best practices, and learn from the vast '
                                     'knowledge stored in the Obsidian vault.',
                    exits={'east': 'main_hall'},
                    items=['search', 'add_reference', 'view_notes', 'generate_docs'],
                    ui_mapping={}
                ),
            }
            
            return AppZorkInterface(
                app_id='va21_coding_ide',
                app_name='VA21 Coding IDE',
                app_description='The Intelligent Development Sanctuary',
                rooms=rooms,
                items={
                    'new_project': 'Begin creating a new software project',
                    'describe_idea': 'Describe your application idea in natural language',
                    'chat': 'Have a conversation with the AI assistant',
                    'voice_command': 'Speak your commands aloud',
                    'suggest_language': 'Get language recommendations',
                    'suggest_stack': 'Get technology stack suggestions',
                    'compare_options': 'Compare different technology choices',
                    'start_build': 'Begin the automated build process',
                    'check_progress': 'Check the current build progress',
                    'view_agents': 'See what each AI agent is working on',
                    'review_code': 'Review the generated code',
                    'search': 'Search for documentation and best practices',
                    'add_reference': 'Add a reference to your research',
                    'view_notes': 'View your project notes',
                    'generate_docs': 'Generate documentation for your project',
                    'help': 'Get help using the IDE',
                    'status': 'Check the current IDE status',
                },
                commands={
                    'build': 'start_build', 'create': 'new_project', 
                    'describe': 'describe_idea', 'suggest': 'suggest_language',
                    'search': 'search', 'help': 'help', 'status': 'status',
                    'agents': 'view_agents', 'progress': 'check_progress',
                    'docs': 'generate_docs', 'notes': 'view_notes',
                },
                welcome_message=self._get_zork_welcome(),
                created_at=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"[CodingIDE] Error creating Zork interface: {e}")
            return None
    
    def _get_zork_welcome(self) -> str:
        """Get Zork-style welcome message."""
        return """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          Welcome to the VA21 Coding IDE Sanctuary                 ║
║                     (Om Vinayaka)                                 ║
║                                                                   ║
║   Where ideas transform into applications through the power       ║
║   of artificial intelligence and collaborative agents.            ║
║                                                                   ║
║   Your accessibility assistant is ready to guide you.             ║
║   Speak naturally or type what you'd like to build.               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

You are at the entrance of the IDE. Say 'enter' to proceed, 
'help' for guidance, or describe what you'd like to create.
"""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CHAT INTERFACE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _get_welcome_message(self) -> str:
        """Get the welcome message for the IDE."""
        return """
🙏 **Om Vinayaka - VA21 Coding IDE**

Welcome to the VA21 Coding IDE! I'm your AI-powered development assistant.

**What I can help you with:**
• 🎯 Describe your app idea and I'll help you plan and build it
• 🔧 Get suggestions for the best languages and technologies
• 📦 Generate complete project structures
• 🤖 Coordinate multiple specialized agents for complex tasks
• 🔍 Search for best practices and documentation
• 🎤 Voice commands (hold Super key to speak)

**To get started:**
Tell me what you want to build! For example:
- "I want to create a task management web app"
- "Build me a CLI tool for file processing"
- "Help me make a mobile app for fitness tracking"

What would you like to create today?
"""
    
    def _add_system_message(self, content: str):
        """Add a system message to chat history."""
        msg = ChatMessage(
            role="system",
            content=content,
            message_type="text"
        )
        self.chat_history.append(msg)
        if self.on_message:
            self.on_message(msg)
    
    def _add_assistant_message(self, content: str, message_type: str = "text",
                               metadata: Dict = None):
        """Add an assistant message to chat history and Summary Engine."""
        msg = ChatMessage(
            role="assistant",
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        self.chat_history.append(msg)
        
        # Add to Summary Engine for context management
        if self.summary_engine:
            self.summary_engine.add_to_context(
                ai_system=AI_CONTEXT_SYSTEM,
                content=content,
                item_type='ai_response',
                priority=3,  # Medium priority for AI responses
                metadata={"message_type": message_type}
            )
        
        if self.on_message:
            self.on_message(msg)
        return msg
    
    def _add_user_message(self, content: str):
        """Add a user message to chat history."""
        msg = ChatMessage(
            role="user",
            content=content
        )
        self.chat_history.append(msg)
        if self.on_message:
            self.on_message(msg)
        return msg
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and return response.
        
        This is the main entry point for the chatbox interface.
        Uses Summary Engine for context management to prevent overflow.
        
        Args:
            user_input: The user's message
            
        Returns:
            The assistant's response
        """
        # Add user message to history
        self._add_user_message(user_input)
        
        # Add to Summary Engine context for overflow prevention
        if self.summary_engine:
            self.summary_engine.add_to_context(
                ai_system=AI_CONTEXT_SYSTEM,
                content=user_input,
                item_type='user_input',
                priority=4,  # High priority for user input
                metadata={"state": self.state.value}
            )
        
        # Handle based on current state
        if self.state == IDEState.IDLE:
            response = self._handle_idle_state(user_input)
        elif self.state == IDEState.GATHERING_REQUIREMENTS:
            response = self._handle_gathering_state(user_input)
        elif self.state == IDEState.SUGGESTING:
            response = self._handle_suggesting_state(user_input)
        elif self.state == IDEState.PLANNING:
            response = self._handle_planning_state(user_input)
        elif self.state == IDEState.BUILDING:
            response = self._handle_building_state(user_input)
        elif self.state == IDEState.REVIEWING:
            response = self._handle_reviewing_state(user_input)
        else:
            response = self._handle_idle_state(user_input)
        
        # Add assistant response
        self._add_assistant_message(response)
        
        return response
    
    def _handle_idle_state(self, user_input: str) -> str:
        """Handle input when IDE is idle."""
        input_lower = user_input.lower()
        
        # Check for commands
        if input_lower in ["help", "?", "/help"]:
            return self._get_help_message()
        
        if input_lower in ["status", "/status"]:
            return self._get_status()
        
        if input_lower.startswith("/api "):
            return self._handle_api_key_command(user_input)
        
        if input_lower in ["clear", "/clear"]:
            self.chat_history = []
            return "Chat history cleared. What would you like to build?"
        
        # Assume this is a project description
        self.project_context.description = user_input
        self.state = IDEState.GATHERING_REQUIREMENTS
        
        if self.on_state_change:
            self.on_state_change(self.state)
        
        # Parse initial requirements
        if self.suggest_engine:
            requirements = self.suggest_engine.parse_requirements(user_input)
            self.project_context.requirements = {
                "app_type": requirements.app_type.value if requirements.app_type else None,
                "target_os": [os.value for os in requirements.target_os],
                "priorities": [p.value for p in requirements.priorities],
                "features": requirements.features,
                "constraints": requirements.constraints
            }
        
        # Generate clarifying questions
        return self._generate_clarifying_questions()
    
    def _generate_clarifying_questions(self) -> str:
        """Generate clarifying questions based on current context."""
        questions = []
        req = self.project_context.requirements
        
        # Ask about target platforms if not clear
        if not req.get("target_os") or "cross_platform" in req.get("target_os", []):
            questions.append("**Target Platforms:**")
            questions.append("Which platforms should this run on?")
            questions.append("- Web browser")
            questions.append("- Windows/macOS/Linux desktop")
            questions.append("- Android/iOS mobile")
            questions.append("- All of the above (cross-platform)")
        
        # Ask about language preference
        questions.append("\n**Programming Language:**")
        questions.append("Do you have a preferred programming language?")
        questions.append("(I can suggest the best one if you're not sure)")
        
        # Ask about features
        if not req.get("features"):
            questions.append("\n**Key Features:**")
            questions.append("What are the main features you need?")
            questions.append("(e.g., user authentication, database, real-time updates)")
        
        self.clarification_needed = ["platforms", "language", "features"]
        
        response = f"""
Great idea! Let me understand your requirements better.

**I understood:**
- Type: {req.get('app_type', 'application')}
- Description: {self.project_context.description[:100]}...

**I need a few more details:**

{chr(10).join(questions)}

(You can answer all at once or one by one. Say "suggest" when you're ready for recommendations!)
"""
        return response
    
    def _handle_gathering_state(self, user_input: str) -> str:
        """Handle input during requirements gathering."""
        input_lower = user_input.lower()
        
        # Check if user wants suggestions now
        if input_lower in ["suggest", "recommend", "ready", "done", "ok"]:
            self.state = IDEState.SUGGESTING
            return self._generate_suggestions()
        
        # Parse the user's answers
        self._parse_clarification_answers(user_input)
        
        # Check if we have enough information
        if self._has_enough_requirements():
            self.state = IDEState.SUGGESTING
            return self._generate_suggestions()
        
        # Ask for more info
        return self._ask_next_question()
    
    def _parse_clarification_answers(self, user_input: str):
        """Parse user's answers to clarifying questions."""
        input_lower = user_input.lower()
        req = self.project_context.requirements
        
        # Detect platforms
        platforms = []
        if any(w in input_lower for w in ["web", "browser", "chrome", "firefox"]):
            platforms.append("web")
        if any(w in input_lower for w in ["windows", "mac", "linux", "desktop"]):
            platforms.extend(["windows", "macos", "linux"])
        if any(w in input_lower for w in ["android", "mobile", "phone"]):
            platforms.append("android")
        if any(w in input_lower for w in ["ios", "iphone", "ipad"]):
            platforms.append("ios")
        if any(w in input_lower for w in ["all", "cross", "everywhere"]):
            platforms.append("cross_platform")
        
        if platforms:
            req["target_os"] = platforms
            if "platforms" in self.clarification_needed:
                self.clarification_needed.remove("platforms")
        
        # Detect language preference
        languages = ["python", "javascript", "typescript", "java", "kotlin", 
                     "swift", "go", "rust", "c#", "php", "ruby"]
        for lang in languages:
            if lang in input_lower:
                self.project_context.language = lang
                if "language" in self.clarification_needed:
                    self.clarification_needed.remove("language")
                break
        
        # Detect features
        features = []
        feature_keywords = [
            ("authentication", ["login", "auth", "user", "signup", "account"]),
            ("database", ["database", "db", "storage", "data"]),
            ("api", ["api", "rest", "backend"]),
            ("realtime", ["realtime", "live", "websocket", "chat"]),
            ("payments", ["payment", "stripe", "checkout", "billing"]),
            ("notifications", ["notification", "push", "alert"]),
        ]
        
        for feature, keywords in feature_keywords:
            if any(kw in input_lower for kw in keywords):
                features.append(feature)
        
        if features:
            req["features"] = req.get("features", []) + features
            if "features" in self.clarification_needed:
                self.clarification_needed.remove("features")
    
    def _has_enough_requirements(self) -> bool:
        """Check if we have enough requirements to proceed."""
        req = self.project_context.requirements
        return (
            req.get("target_os") and
            (self.project_context.language or not self.clarification_needed)
        )
    
    def _ask_next_question(self) -> str:
        """Ask the next clarifying question."""
        if "platforms" in self.clarification_needed:
            return "Which platforms should this run on? (web, desktop, mobile, or all)"
        
        if "language" in self.clarification_needed:
            return "Do you have a preferred programming language? (or say 'suggest' for my recommendation)"
        
        if "features" in self.clarification_needed:
            return "What key features do you need? (e.g., user accounts, database, real-time updates)"
        
        # Ready to suggest
        self.state = IDEState.SUGGESTING
        return self._generate_suggestions()
    
    def _handle_suggesting_state(self, user_input: str) -> str:
        """Handle input during suggestion phase."""
        input_lower = user_input.lower()
        
        # Check for acceptance
        if any(w in input_lower for w in ["yes", "ok", "good", "accept", "proceed", "continue"]):
            self.state = IDEState.PLANNING
            return self._generate_plan()
        
        # Check for changes
        if any(w in input_lower for w in ["no", "different", "change", "other"]):
            return "What would you like to change? (language, framework, or stack)"
        
        # Parse specific changes
        if "language" in input_lower:
            self._parse_clarification_answers(user_input)
            return self._generate_suggestions()
        
        # Re-explain suggestions
        return "Would you like to proceed with these suggestions? (say 'yes' to continue or tell me what to change)"
    
    def _generate_suggestions(self) -> str:
        """Generate technology suggestions."""
        if not self.suggest_engine:
            return "Suggestion engine not available. Please proceed with your preferred technologies."
        
        # Get full suggestion report
        report = self.suggest_engine.get_suggestion_report(
            self.project_context.description or ""
        )
        
        self.project_context.suggestions = report
        
        # Get top language
        top_lang = report["language_suggestions"][0] if report["language_suggestions"] else None
        top_stack = report["stack_suggestions"][0] if report["stack_suggestions"] else None
        
        if top_lang:
            self.project_context.language = top_lang["language"]
        if top_stack:
            self.project_context.stack = top_stack["name"]
        
        # Format response
        response = f"""
## 🎯 Technology Recommendations

Based on your requirements, here are my suggestions:

### Recommended Language: **{top_lang['language'] if top_lang else 'Python'}**
"""
        
        if top_lang:
            response += f"""
**Why {top_lang['language']}?**
{chr(10).join(['- ' + r for r in top_lang['reasons'][:3]])}

**Pros:** {', '.join(top_lang['pros'][:3])}
**Frameworks:** {', '.join(top_lang['frameworks'][:3])}
**Learning Curve:** {top_lang['learning_curve']}
"""
        
        if top_stack:
            response += f"""
### Recommended Stack: **{top_stack['name']}**

- **Frontend:** {top_stack.get('frontend', 'N/A')}
- **Backend:** {top_stack.get('backend', 'N/A')}
- **Database:** {top_stack.get('database', 'N/A')}

{top_stack.get('reasoning', '')}
"""
        
        # Other options
        if len(report["language_suggestions"]) > 1:
            other_langs = [l["language"] for l in report["language_suggestions"][1:3]]
            response += f"""
### Alternative Languages
You could also consider: {', '.join(other_langs)}
"""
        
        response += """
---
**Would you like to proceed with these recommendations?**
(Say 'yes' to continue, or tell me what you'd like to change)
"""
        
        return response
    
    def _handle_planning_state(self, user_input: str) -> str:
        """Handle input during planning phase."""
        input_lower = user_input.lower()
        
        if any(w in input_lower for w in ["yes", "ok", "build", "start", "create"]):
            self.state = IDEState.BUILDING
            return self._start_building()
        
        if any(w in input_lower for w in ["no", "back", "change"]):
            self.state = IDEState.SUGGESTING
            return "What would you like to change about the plan?"
        
        return "Would you like me to start building the project? (say 'yes' to begin)"
    
    def _generate_plan(self) -> str:
        """Generate a development plan."""
        if not self.orchestrator:
            return "Planning system not available. Proceeding with basic project creation."
        
        # Create a build plan
        requirements = {
            "app_type": self.project_context.requirements.get("app_type", "web_app"),
            "features": self.project_context.requirements.get("features", []),
            "stack": self.project_context.suggestions.get("stack_suggestions", [{}])[0]
        }
        
        plan_name = self.project_context.description[:50] if self.project_context.description else "New Project"
        
        plan = self.orchestrator.create_build_plan(
            name=plan_name,
            description=self.project_context.description or "",
            requirements=requirements
        )
        
        self.project_context.build_plan = plan.id
        
        # Format plan
        response = f"""
## 📋 Development Plan

I've created a plan with **{len(plan.tasks)} tasks**:

"""
        
        for i, task in enumerate(plan.tasks, 1):
            deps = f" *(after: {len(task.dependencies)} tasks)*" if task.dependencies else ""
            response += f"{i}. **{task.title}** - {task.task_type.value}{deps}\n"
        
        response += f"""
---

### Agents Assigned:
"""
        
        agents_used = set(task.task_type.value for task in plan.tasks)
        for agent_type in agents_used:
            response += f"- 🤖 {agent_type.replace('_', ' ').title()} Agent\n"
        
        response += """
---
**Ready to build?** (say 'yes' to start, or 'change' to modify the plan)
"""
        
        return response
    
    def _handle_building_state(self, user_input: str) -> str:
        """Handle input during building phase."""
        input_lower = user_input.lower()
        
        if "status" in input_lower:
            return self._get_build_status()
        
        if any(w in input_lower for w in ["stop", "cancel", "abort"]):
            self.state = IDEState.IDLE
            return "Build cancelled. What else would you like to do?"
        
        return "Building in progress... Say 'status' to check progress."
    
    def _start_building(self) -> str:
        """Start the build process."""
        response = "## 🚀 Building Your Project\n\n"
        
        # First, create the project structure
        if self.project_builder:
            try:
                from .project_builder import ProjectConfig, ProjectType
                
                config = ProjectConfig(
                    name=self.project_context.description[:30] if self.project_context.description else "My App",
                    description=self.project_context.description or "A VA21 project",
                    project_type=ProjectType.WEB_FULLSTACK,
                    language=self.project_context.language or "Python",
                    framework=self.project_context.stack,
                    database="PostgreSQL",
                    features=self.project_context.requirements.get("features", []),
                    target_os=self.project_context.requirements.get("target_os", ["cross_platform"])
                )
                
                structure = self.project_builder.create_project(config)
                self.project_context.project_path = structure.root_path
                
                response += f"""
### ✅ Project Structure Created

**Location:** `{structure.root_path}`
**Files created:** {len(structure.files)}
**Directories:** {len(structure.directories)}

"""
            except Exception as e:
                response += f"⚠️ Could not create project structure: {e}\n\n"
        
        # Execute the build plan if available
        if self.orchestrator and self.project_context.build_plan:
            response += "### 🔧 Executing Build Plan\n\n"
            
            try:
                results = self.orchestrator.execute_plan(
                    self.project_context.build_plan,
                    callback=self._build_progress_callback
                )
                
                response += f"""
**Tasks Completed:** {len(results.get('tasks_completed', []))}
**Tasks Failed:** {len(results.get('tasks_failed', []))}
**Progress:** {results.get('final_progress', 0):.0f}%

"""
                
                if results.get('tasks_completed'):
                    response += "### Generated Content:\n\n"
                    for task_id in results['tasks_completed'][:3]:
                        output = results.get('outputs', {}).get(task_id, '')
                        if output:
                            response += f"```\n{output[:500]}...\n```\n\n"
                
            except Exception as e:
                response += f"⚠️ Build execution error: {e}\n\n"
        
        self.state = IDEState.REVIEWING
        
        response += """
---
### 🎉 Build Complete!

Your project has been created. What would you like to do next?
- Say **"view"** to see the generated files
- Say **"run"** to start the development server
- Say **"improve"** to make changes
- Say **"new"** to start a new project
"""
        
        return response
    
    def _build_progress_callback(self, update: Dict):
        """Callback for build progress updates."""
        if self.on_progress:
            self.on_progress(update)
        
        print(f"[Build] {update.get('progress', 0):.0f}% - {update.get('current_task', '')}")
    
    def _handle_reviewing_state(self, user_input: str) -> str:
        """Handle input during review phase."""
        input_lower = user_input.lower()
        
        if "view" in input_lower or "show" in input_lower:
            return self._show_project_files()
        
        if "run" in input_lower or "start" in input_lower:
            return self._run_project()
        
        if "improve" in input_lower or "change" in input_lower:
            return "What would you like to improve or change?"
        
        if "new" in input_lower:
            self.state = IDEState.IDLE
            self.project_context = ProjectContext()
            return "Starting fresh! What would you like to build?"
        
        # Treat as improvement request
        if self.ai_helper:
            response = self.ai_helper.chat(
                user_input,
                context=f"Project: {self.project_context.description}\nPath: {self.project_context.project_path}",
                task_type="code_generation"
            )
            return response.content if response.success else f"Error: {response.error}"
        
        return "What would you like to do with your project?"
    
    def _show_project_files(self) -> str:
        """Show the project files."""
        if not self.project_context.project_path:
            return "No project created yet."
        
        path = self.project_context.project_path
        if not os.path.exists(path):
            return f"Project path not found: {path}"
        
        response = f"## 📁 Project Files\n\n**Location:** `{path}`\n\n"
        
        for root, dirs, files in os.walk(path):
            # Skip hidden and vendor directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            level = root.replace(path, '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root) or os.path.basename(path)
            response += f"{indent}📁 {folder_name}/\n"
            
            subindent = '  ' * (level + 1)
            for file in files[:10]:  # Limit files shown
                response += f"{subindent}📄 {file}\n"
            
            if len(files) > 10:
                response += f"{subindent}... and {len(files) - 10} more files\n"
        
        return response
    
    def _run_project(self) -> str:
        """Run the project."""
        if not self.project_context.project_path:
            return "No project created yet."
        
        if not self.project_builder:
            return "Project builder not available."
        
        try:
            self.project_builder.install_dependencies(self.project_context.project_path)
            return f"""
## 🚀 Running Project

Project is starting at: `{self.project_context.project_path}`

To run manually:
```bash
cd {self.project_context.project_path}
# For Node.js: npm run dev
# For Python: uvicorn src.main:app --reload
```

The development server should be starting. Check your terminal for output.
"""
        except Exception as e:
            return f"Error running project: {e}"
    
    def _get_build_status(self) -> str:
        """Get the current build status."""
        if not self.orchestrator or not self.project_context.build_plan:
            return "No active build."
        
        status = self.orchestrator.get_plan_status(self.project_context.build_plan)
        if not status:
            return "Build plan not found."
        
        plan = status["plan"]
        return f"""
## Build Status

**Project:** {plan['name']}
**Progress:** {plan['progress']}
**Status:** {plan['status']}
**Tasks:** {plan['completed_tasks']}/{plan['total_tasks']}
"""
    
    def _get_help_message(self) -> str:
        """Get help message."""
        return """
## 📚 VA21 Coding IDE Help

### Commands
- `/help` - Show this help message
- `/status` - Show IDE status
- `/api <provider> <key>` - Set AI API key
- `/clear` - Clear chat history

### Workflow
1. **Describe** your app idea in natural language
2. **Answer** my clarifying questions about platforms and features
3. **Review** my technology suggestions
4. **Approve** the development plan
5. **Build** - I'll create your project!

### Voice Commands
Hold the **Super key** and speak to use voice input.

### Examples
- "Build a task management web app with user authentication"
- "Create a Python CLI tool for processing CSV files"
- "Make a mobile app for tracking fitness goals"

### AI Providers
- **Ollama** (default): Local, no API key needed
- **OpenAI**: Set with `/api openai <your-key>`
- **Anthropic**: Set with `/api anthropic <your-key>`
- **Google**: Set with `/api google <your-key>`
"""
    
    def _get_status(self) -> str:
        """Get IDE status with all VA21 OS integrations."""
        status = f"""
## IDE Status

**State:** {self.state.value}
**Chat Messages:** {len(self.chat_history)}

### Project Context
- **Description:** {self.project_context.description[:50] if self.project_context.description else 'None'}...
- **Language:** {self.project_context.language or 'Not selected'}
- **Stack:** {self.project_context.stack or 'Not selected'}
- **Project Path:** {self.project_context.project_path or 'Not created'}

### Core Components
- **SuggestEngine:** {'✅' if self.suggest_engine else '❌'}
- **AIHelper:** {'✅' if self.ai_helper else '❌'}
- **Orchestrator:** {'✅' if self.orchestrator else '❌'}
- **ProjectBuilder:** {'✅' if self.project_builder else '❌'}

### VA21 OS Integrations
- **Summary Engine:** {'✅ (Context overflow protection)' if self.summary_engine else '❌'}
- **Obsidian Vault:** {'✅ (Knowledge storage)' if self.obsidian_vault else '❌'}
- **Writing Suite:** {'✅ (Documentation)' if self.writing_suite else '❌'}
- **Research Suite:** {'✅ (Citations & references)' if self.research_suite else '❌'}
- **SearXNG:** {'✅ (Web search)' if self.searxng else '❌'}
- **Zork Manager:** {'✅ (Assistive UX)' if self.zork_manager else '❌'}
- **FARA Layer:** {'✅ (Voice control)' if self.fara_layer else '❌'}
- **Om Vinayaka AI:** {'✅ (Accessibility)' if self.om_vinayaka else '❌'}
"""
        
        # Summary Engine stats
        if self.summary_engine:
            summary_stats = self.summary_engine.get_statistics()
            context_state = self.summary_engine.get_context_state(AI_CONTEXT_SYSTEM)
            status += f"""
### Summary Engine Stats
- **Context Usage:** {context_state.usage_percent:.1%} ({context_state.total_tokens}/{context_state.limit} tokens)
- **Summaries Created:** {summary_stats.get('summaries_created', 0)}
- **Tokens Saved:** {summary_stats.get('tokens_saved', 0)}
- **Hallucinations Prevented:** {summary_stats.get('hallucinations_prevented', 0)}
"""
        
        if self.ai_helper:
            ai_status = self.ai_helper.get_status()
            status += f"""
### AI Provider
- **Active:** {ai_status.get('active_provider', 'None')}
- **Providers:** {ai_status.get('providers_configured', 0)} configured
"""
        
        return status
    
    def _handle_api_key_command(self, user_input: str) -> str:
        """Handle API key command."""
        parts = user_input.split()
        if len(parts) < 3:
            return "Usage: /api <provider> <api-key>\nProviders: openai, anthropic, google"
        
        provider_name = parts[1].lower()
        api_key = parts[2]
        
        if not self.ai_helper:
            return "AI Helper not available."
        
        from .ai_helper import AIProvider
        
        provider_map = {
            "openai": AIProvider.OPENAI,
            "anthropic": AIProvider.ANTHROPIC,
            "google": AIProvider.GOOGLE,
        }
        
        provider = provider_map.get(provider_name)
        if not provider:
            return f"Unknown provider: {provider_name}. Available: openai, anthropic, google"
        
        success = self.ai_helper.set_api_key(provider, api_key)
        if success:
            self.ai_helper.set_active_provider(provider)
            return f"✅ API key set for {provider_name}. Now using {provider_name} as the AI provider."
        else:
            return f"❌ Failed to set API key for {provider_name}."
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VOICE INTEGRATION (FARA Layer)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def process_voice_input(self, voice_text: str) -> str:
        """
        Process voice input through FARA layer.
        
        Args:
            voice_text: Transcribed voice input
            
        Returns:
            Response text
        """
        # Use Om Vinayaka AI if available for better voice understanding
        if self.om_vinayaka:
            result = self.om_vinayaka.process_user_input(
                voice_text,
                current_app="VA21 Coding IDE"
            )
            
            if result.get("action"):
                # Execute the action through the IDE
                return self.process_input(result["action"])
            
            return result.get("response", self.process_input(voice_text))
        
        # Fallback to regular processing
        return self.process_input(voice_text)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CLI INTERFACE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def run_cli(self):
        """Run the IDE in CLI mode."""
        print("\n" + "=" * 60)
        print("VA21 Coding IDE - Command Line Interface")
        print("=" * 60)
        
        # Print welcome
        if self.console and RICH_AVAILABLE:
            self.console.print(Markdown(self._get_welcome_message()))
        else:
            print(self._get_welcome_message())
        
        while True:
            try:
                # Get input
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("\n🙏 Om Vinayaka! May your coding journey be blessed.")
                    break
                
                # Process input
                response = self.process_input(user_input)
                
                # Print response
                print("\n🤖 IDE:")
                if self.console and RICH_AVAILABLE:
                    self.console.print(Markdown(response))
                else:
                    print(response)
                
            except KeyboardInterrupt:
                print("\n\n🙏 Goodbye!")
                break
            except EOFError:
                break


# Singleton instance
_coding_ide_instance = None


def get_coding_ide() -> CodingIDE:
    """Get or create the CodingIDE singleton."""
    global _coding_ide_instance
    if _coding_ide_instance is None:
        _coding_ide_instance = CodingIDE()
    return _coding_ide_instance


# CLI entry point
def main():
    """Main entry point for the Coding IDE."""
    ide = get_coding_ide()
    ide.run_cli()


if __name__ == "__main__":
    main()
