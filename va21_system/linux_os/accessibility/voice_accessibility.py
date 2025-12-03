#!/usr/bin/env python3
"""
VA21 OS - System-Wide Voice Accessibility
==========================================

This module provides comprehensive voice accessibility for the entire VA21 OS,
not just the Zork interface. Users can:

1. Control ANY application with voice
2. Get natural language explanations of what's happening
3. Have conversational interactions with Helper AI
4. Execute complex tasks through the FARA layer
5. Navigate the entire OS without typing

This is VA21's unique advantage - unlike other OS screen readers that just
read keywords like "menu", "button", VA21 explains WHAT things do and
ASKS what users want to accomplish.

Om Vinayaka - May obstacles be removed from your computing journey.
"""

import os
import sys
import subprocess
import threading
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

# Text-to-speech
TTS_AVAILABLE = False
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pass

# Speech recognition
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    pass

# Keyboard listener for Super key
KEYBOARD_AVAILABLE = False
try:
    from pynput import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

class AppType(Enum):
    """Types of applications that can be controlled."""
    ZORK_SHELL = "zork_shell"
    TERMINAL = "terminal"
    FILE_MANAGER = "file_manager"
    TEXT_EDITOR = "text_editor"
    WEB_BROWSER = "web_browser"
    SETTINGS = "settings"
    RESEARCH_SUITE = "research_suite"
    WRITING_SUITE = "writing_suite"
    OBSIDIAN_VAULT = "obsidian_vault"
    UNKNOWN = "unknown"


@dataclass
class ApplicationContext:
    """Context about the currently active application."""
    app_type: AppType
    app_name: str
    window_title: str
    active_element: str
    available_actions: List[str]
    current_content: str
    file_path: Optional[str] = None
    selection: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM-WIDE FARA LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class SystemWideFARALayer:
    """
    FARA (Flexible Automated Response Architecture) Layer for entire OS.
    
    Provides UI automation and action execution across all applications.
    This layer translates high-level user intents into actual system actions.
    
    Key capabilities:
    - Execute commands in any application
    - Navigate between windows and applications
    - Interact with GUI elements
    - Manage files and system settings
    - Control media and system functions
    """
    
    def __init__(self):
        self.action_history = []
        self.current_app_context: Optional[ApplicationContext] = None
        self.available_apps = self._detect_installed_apps()
    
    def _detect_installed_apps(self) -> Dict[str, str]:
        """Detect installed applications."""
        apps = {
            'zork': 'VA21 Zork Shell - Text adventure interface',
            'terminal': 'Terminal - Command line interface',
            'files': 'File Manager - Browse and manage files',
            'editor': 'Text Editor - Create and edit documents',
            'browser': 'Web Browser - Browse the internet',
            'settings': 'Settings Center - Configure the system',
            'research': 'Research Suite - Academic research tools',
            'writing': 'Writing Suite - Document creation tools',
            'vault': 'Knowledge Vault - Note-taking and knowledge management',
            'guardian': 'Guardian AI - Security monitoring',
        }
        return apps
    
    def get_current_context(self) -> ApplicationContext:
        """Get context about the currently active application."""
        # Try to detect active window
        try:
            # On Linux, try to get active window info
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowname'],
                capture_output=True, text=True, timeout=2
            )
            window_title = result.stdout.strip() if result.returncode == 0 else "VA21 OS"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            window_title = "VA21 OS"
        
        # Detect app type from window title
        app_type = self._detect_app_type(window_title)
        
        return ApplicationContext(
            app_type=app_type,
            app_name=self._get_app_name(app_type),
            window_title=window_title,
            active_element="main window",
            available_actions=self._get_available_actions(app_type),
            current_content=""
        )
    
    def _detect_app_type(self, window_title: str) -> AppType:
        """Detect application type from window title."""
        title_lower = window_title.lower()
        
        # Optimized app type detection using keyword sets
        app_keywords = {
            AppType.ZORK_SHELL: {'zork', 'boot chamber', 'research lab', 'guardian sanctum'},
            AppType.TERMINAL: {'terminal', 'bash', 'shell', 'konsole', 'xterm'},
            AppType.FILE_MANAGER: {'file', 'nautilus', 'thunar', 'dolphin', 'files'},
            AppType.TEXT_EDITOR: {'editor', 'vim', 'nano', 'gedit', 'kate', 'notepad'},
            AppType.WEB_BROWSER: {'firefox', 'chrome', 'chromium', 'browser', 'safari'},
            AppType.SETTINGS: {'setting', 'preference', 'config', 'control center'},
            AppType.RESEARCH_SUITE: {'research'},
            AppType.WRITING_SUITE: {'writing', 'document', 'writer', 'word'},
            AppType.OBSIDIAN_VAULT: {'vault', 'obsidian', 'note'},
        }
        
        for app_type, keywords in app_keywords.items():
            if any(kw in title_lower for kw in keywords):
                return app_type
        
        return AppType.UNKNOWN
    
    def _get_app_name(self, app_type: AppType) -> str:
        """Get friendly name for app type."""
        names = {
            AppType.ZORK_SHELL: "VA21 Zork Interface",
            AppType.TERMINAL: "Terminal",
            AppType.FILE_MANAGER: "File Manager",
            AppType.TEXT_EDITOR: "Text Editor",
            AppType.WEB_BROWSER: "Web Browser",
            AppType.SETTINGS: "Settings Center",
            AppType.RESEARCH_SUITE: "Research Suite",
            AppType.WRITING_SUITE: "Writing Suite",
            AppType.OBSIDIAN_VAULT: "Knowledge Vault",
            AppType.UNKNOWN: "Application",
        }
        return names.get(app_type, "Application")
    
    def _get_available_actions(self, app_type: AppType) -> List[str]:
        """Get available actions for an app type."""
        common_actions = ['close', 'minimize', 'maximize', 'switch app', 'help']
        
        app_actions = {
            AppType.ZORK_SHELL: ['look', 'go', 'take', 'examine', 'search', 'save', 'ask guardian'],
            AppType.TERMINAL: ['run command', 'clear', 'copy', 'paste', 'new tab', 'close tab'],
            AppType.FILE_MANAGER: ['open', 'copy', 'paste', 'delete', 'rename', 'new folder', 'go back', 'go home'],
            AppType.TEXT_EDITOR: ['save', 'save as', 'open', 'copy', 'paste', 'cut', 'undo', 'redo', 'find', 'replace'],
            AppType.WEB_BROWSER: ['go to', 'search', 'back', 'forward', 'refresh', 'new tab', 'close tab', 'bookmark'],
            AppType.SETTINGS: ['change', 'toggle', 'apply', 'reset', 'save'],
            AppType.RESEARCH_SUITE: ['search', 'cite', 'analyze', 'export', 'import'],
            AppType.WRITING_SUITE: ['new document', 'save', 'export', 'format', 'spell check'],
            AppType.OBSIDIAN_VAULT: ['new note', 'search', 'link', 'tag', 'export'],
            AppType.UNKNOWN: [],
        }
        
        return common_actions + app_actions.get(app_type, [])
    
    def execute_action(self, action: str, context: ApplicationContext) -> Dict[str, Any]:
        """
        Execute an action in the current application context.
        
        Returns result of the action with description for user.
        """
        self.action_history.append({
            'action': action,
            'app': context.app_name,
            'timestamp': datetime.now().isoformat()
        })
        
        # Route to appropriate handler
        if context.app_type == AppType.ZORK_SHELL:
            return self._execute_zork_action(action)
        elif context.app_type == AppType.TERMINAL:
            return self._execute_terminal_action(action)
        elif context.app_type == AppType.FILE_MANAGER:
            return self._execute_file_manager_action(action)
        elif context.app_type == AppType.TEXT_EDITOR:
            return self._execute_editor_action(action)
        elif context.app_type == AppType.WEB_BROWSER:
            return self._execute_browser_action(action)
        elif context.app_type == AppType.SETTINGS:
            return self._execute_settings_action(action)
        else:
            return self._execute_generic_action(action)
    
    def _execute_zork_action(self, action: str) -> Dict[str, Any]:
        """Execute action in Zork interface."""
        return {
            'success': True,
            'action': action,
            'description': f"Executing in Zork: {action}",
            'result': None  # Will be filled by Zork interface
        }
    
    def _execute_terminal_action(self, action: str) -> Dict[str, Any]:
        """Execute action in terminal."""
        action_lower = action.lower()
        
        if 'clear' in action_lower:
            return {'success': True, 'action': 'clear', 'description': "Clearing the terminal screen"}
        elif 'run' in action_lower:
            cmd = action.replace('run', '').replace('command', '').strip()
            return {'success': True, 'action': f'run:{cmd}', 'description': f"Running command: {cmd}"}
        elif 'new tab' in action_lower:
            return {'success': True, 'action': 'new_tab', 'description': "Opening a new terminal tab"}
        
        return {'success': False, 'description': f"Unknown terminal action: {action}"}
    
    def _execute_file_manager_action(self, action: str) -> Dict[str, Any]:
        """Execute action in file manager."""
        action_lower = action.lower()
        
        if 'open' in action_lower:
            return {'success': True, 'action': 'open', 'description': "Opening the selected item"}
        elif 'copy' in action_lower:
            return {'success': True, 'action': 'copy', 'description': "Copying selected files"}
        elif 'paste' in action_lower:
            return {'success': True, 'action': 'paste', 'description': "Pasting files here"}
        elif 'delete' in action_lower:
            return {'success': True, 'action': 'delete', 'description': "Moving selected items to trash", 'needs_confirm': True}
        elif 'new folder' in action_lower:
            return {'success': True, 'action': 'new_folder', 'description': "Creating a new folder"}
        elif 'go back' in action_lower:
            return {'success': True, 'action': 'back', 'description': "Going back to previous folder"}
        elif 'go home' in action_lower:
            return {'success': True, 'action': 'home', 'description': "Going to your home folder"}
        
        return {'success': False, 'description': f"Unknown file manager action: {action}"}
    
    def _execute_editor_action(self, action: str) -> Dict[str, Any]:
        """Execute action in text editor."""
        action_lower = action.lower()
        
        if 'save' in action_lower:
            return {'success': True, 'action': 'save', 'description': "Saving your document"}
        elif 'undo' in action_lower:
            return {'success': True, 'action': 'undo', 'description': "Undoing your last change"}
        elif 'redo' in action_lower:
            return {'success': True, 'action': 'redo', 'description': "Redoing your last change"}
        elif 'copy' in action_lower:
            return {'success': True, 'action': 'copy', 'description': "Copying selected text"}
        elif 'paste' in action_lower:
            return {'success': True, 'action': 'paste', 'description': "Pasting from clipboard"}
        elif 'find' in action_lower:
            return {'success': True, 'action': 'find', 'description': "Opening find dialog"}
        
        return {'success': False, 'description': f"Unknown editor action: {action}"}
    
    def _execute_browser_action(self, action: str) -> Dict[str, Any]:
        """Execute action in web browser."""
        action_lower = action.lower()
        
        if 'back' in action_lower:
            return {'success': True, 'action': 'back', 'description': "Going back to previous page"}
        elif 'forward' in action_lower:
            return {'success': True, 'action': 'forward', 'description': "Going forward to next page"}
        elif 'refresh' in action_lower or 'reload' in action_lower:
            return {'success': True, 'action': 'refresh', 'description': "Refreshing the page"}
        elif 'new tab' in action_lower:
            return {'success': True, 'action': 'new_tab', 'description': "Opening a new browser tab"}
        elif 'close tab' in action_lower:
            return {'success': True, 'action': 'close_tab', 'description': "Closing current tab"}
        elif 'go to' in action_lower or 'navigate' in action_lower:
            url = action_lower.replace('go to', '').replace('navigate', '').strip()
            return {'success': True, 'action': f'goto:{url}', 'description': f"Navigating to {url}"}
        
        return {'success': False, 'description': f"Unknown browser action: {action}"}
    
    def _execute_settings_action(self, action: str) -> Dict[str, Any]:
        """Execute action in settings."""
        return {'success': True, 'action': action, 'description': f"Adjusting setting: {action}"}
    
    def _execute_generic_action(self, action: str) -> Dict[str, Any]:
        """Execute generic action."""
        action_lower = action.lower()
        
        # Common actions across all apps
        if 'close' in action_lower:
            return {'success': True, 'action': 'close', 'description': "Closing this window"}
        elif 'minimize' in action_lower:
            return {'success': True, 'action': 'minimize', 'description': "Minimizing this window"}
        elif 'maximize' in action_lower:
            return {'success': True, 'action': 'maximize', 'description': "Maximizing this window"}
        elif 'switch' in action_lower:
            return {'success': True, 'action': 'switch', 'description': "Switching to another application"}
        
        return {'success': False, 'description': f"I don't know how to {action} in this application"}
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application by name."""
        app_commands = {
            'terminal': 'x-terminal-emulator',
            'files': 'nautilus',
            'file manager': 'nautilus',
            'browser': 'firefox',
            'firefox': 'firefox',
            'editor': 'gedit',
            'text editor': 'gedit',
            'settings': 'gnome-control-center',
        }
        
        app_lower = app_name.lower()
        
        if app_lower in app_commands:
            cmd = app_commands[app_lower]
            try:
                subprocess.Popen([cmd], start_new_session=True)
                return {'success': True, 'description': f"Opening {app_name}"}
            except FileNotFoundError:
                return {'success': False, 'description': f"Could not find {app_name} application"}
        
        return {'success': False, 'description': f"I don't know how to open {app_name}"}


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM-WIDE HELPER AI
# ═══════════════════════════════════════════════════════════════════════════════

class SystemWideHelperAI:
    """
    Helper AI that works across the entire VA21 OS.
    
    Key capabilities:
    - Understands natural language requests
    - Asks clarifying questions when context is unclear
    - Provides conversational interaction
    - Works with any application
    - Explains what's happening in plain language
    - Supports 1,600+ languages
    """
    
    def __init__(self, fara_layer: SystemWideFARALayer):
        self.fara = fara_layer
        self.conversation_history = []
        self.pending_clarification = None
        self.user_preferences = {}
    
    def process_request(self, user_input: str, context: ApplicationContext) -> Dict[str, Any]:
        """
        Process a user request with full context awareness.
        
        Returns:
            {
                'response': str - What to say to the user
                'action': Optional[str] - Action to execute
                'needs_clarification': bool - Whether we need more info
                'clarification_question': Optional[str] - What to ask
            }
        """
        input_lower = user_input.lower().strip()
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat(),
            'context': context.app_name
        })
        
        # Check if this is a response to a pending clarification
        if self.pending_clarification:
            return self._handle_clarification_response(user_input, context)
        
        # Understand intent
        intent = self._understand_intent(input_lower, context)
        
        # Handle based on intent type
        if intent['type'] == 'navigation':
            return self._handle_navigation(intent, context)
        elif intent['type'] == 'action':
            return self._handle_action(intent, context)
        elif intent['type'] == 'question':
            return self._handle_question(intent, context)
        elif intent['type'] == 'open_app':
            return self._handle_open_app(intent, context)
        elif intent['type'] == 'system_control':
            return self._handle_system_control(intent, context)
        elif intent['type'] == 'help':
            return self._handle_help(intent, context)
        else:
            return self._ask_clarification(user_input, context)
    
    def _understand_intent(self, input_lower: str, context: ApplicationContext) -> Dict[str, Any]:
        """Understand the user's intent from their input."""
        
        # Check for app opening
        open_patterns = ['open', 'start', 'launch', 'run']
        for pattern in open_patterns:
            if input_lower.startswith(pattern):
                app_name = input_lower.replace(pattern, '').strip()
                return {'type': 'open_app', 'app_name': app_name}
        
        # Check for system control
        system_patterns = ['volume', 'brightness', 'wifi', 'bluetooth', 'shutdown', 'restart', 'sleep', 'lock']
        for pattern in system_patterns:
            if pattern in input_lower:
                return {'type': 'system_control', 'control': pattern, 'full_input': input_lower}
        
        # Check for navigation (within current app)
        nav_patterns = ['go to', 'navigate', 'take me to', 'show me', 'open']
        for pattern in nav_patterns:
            if pattern in input_lower:
                destination = input_lower.replace(pattern, '').strip()
                return {'type': 'navigation', 'destination': destination}
        
        # Check for actions
        action_patterns = ['save', 'copy', 'paste', 'delete', 'create', 'new', 'search', 'find', 'close', 'undo', 'redo']
        for pattern in action_patterns:
            if pattern in input_lower:
                return {'type': 'action', 'action': pattern, 'full_input': input_lower}
        
        # Check for questions
        question_patterns = ['what', 'how', 'where', 'why', 'when', 'can i', 'could you', 'help me', '?']
        for pattern in question_patterns:
            if pattern in input_lower:
                return {'type': 'question', 'question': input_lower}
        
        # Check for help request
        if 'help' in input_lower:
            return {'type': 'help', 'topic': input_lower.replace('help', '').strip()}
        
        # Unknown intent
        return {'type': 'unknown', 'input': input_lower}
    
    def _handle_navigation(self, intent: Dict, context: ApplicationContext) -> Dict[str, Any]:
        """Handle navigation requests."""
        destination = intent.get('destination', '')
        
        if not destination:
            self.pending_clarification = 'navigation'
            return {
                'response': f"Where would you like to go in {context.app_name}?",
                'action': None,
                'needs_clarification': True,
                'clarification_question': "Where would you like to navigate to?"
            }
        
        # Build action for FARA
        action = f"go to {destination}"
        result = self.fara.execute_action(action, context)
        
        return {
            'response': result['description'],
            'action': action,
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _handle_action(self, intent: Dict, context: ApplicationContext) -> Dict[str, Any]:
        """Handle action requests."""
        action = intent.get('action', '')
        full_input = intent.get('full_input', '')
        
        # Check if action needs confirmation (dangerous actions)
        dangerous_actions = ['delete', 'remove', 'erase', 'shutdown', 'restart']
        if action in dangerous_actions:
            self.pending_clarification = {'type': 'confirm', 'action': full_input}
            return {
                'response': f"You want to {action}. This action may have permanent effects. Are you sure you want to proceed?",
                'action': None,
                'needs_clarification': True,
                'clarification_question': "Please confirm yes or no."
            }
        
        # Execute the action
        result = self.fara.execute_action(full_input, context)
        
        return {
            'response': result['description'],
            'action': full_input,
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _handle_question(self, intent: Dict, context: ApplicationContext) -> Dict[str, Any]:
        """Handle user questions."""
        question = intent.get('question', '')
        
        # What can I do here?
        if 'what can i do' in question or 'what are my options' in question:
            actions = context.available_actions
            actions_text = ", ".join(actions[:5])
            if len(actions) > 5:
                actions_text += f", and {len(actions) - 5} more options"
            
            return {
                'response': f"In {context.app_name}, you can: {actions_text}. What would you like to do?",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # Where am I?
        if 'where am i' in question:
            return {
                'response': f"You are in {context.app_name}. The window title shows: {context.window_title}. Would you like me to describe what you can do here?",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # How do I...?
        if 'how do i' in question or 'how can i' in question:
            task = question.replace('how do i', '').replace('how can i', '').strip().rstrip('?')
            return {
                'response': f"To {task}, just tell me what you want to accomplish. For example, say 'I want to {task}' and I'll guide you through it step by step.",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # Generic question
        return {
            'response': f"That's a good question about {context.app_name}. Could you tell me more about what you're trying to understand or accomplish?",
            'action': None,
            'needs_clarification': True,
            'clarification_question': "What specifically would you like to know?"
        }
    
    def _handle_open_app(self, intent: Dict, context: ApplicationContext) -> Dict[str, Any]:
        """Handle opening an application."""
        app_name = intent.get('app_name', '')
        
        if not app_name:
            self.pending_clarification = 'open_app'
            apps = list(self.fara.available_apps.keys())
            apps_text = ", ".join(apps[:5])
            
            return {
                'response': f"Which application would you like to open? Available apps include: {apps_text}.",
                'action': None,
                'needs_clarification': True,
                'clarification_question': "Which app should I open?"
            }
        
        result = self.fara.open_application(app_name)
        
        return {
            'response': result['description'],
            'action': f"open {app_name}",
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _handle_system_control(self, intent: Dict, context: ApplicationContext) -> Dict[str, Any]:
        """Handle system control requests."""
        control = intent.get('control', '')
        full_input = intent.get('full_input', '')
        
        control_descriptions = {
            'volume': "I can adjust the volume for you. Would you like me to turn it up, down, or mute?",
            'brightness': "I can adjust screen brightness. Would you like it brighter or dimmer?",
            'wifi': "I can toggle WiFi on or off. What would you like me to do?",
            'bluetooth': "I can toggle Bluetooth on or off. What would you like me to do?",
            'shutdown': "You want to shut down the computer. This will close all applications. Are you sure?",
            'restart': "You want to restart the computer. This will close all applications. Are you sure?",
            'sleep': "You want to put the computer to sleep. It will save your work and enter low-power mode.",
            'lock': "I'll lock the screen now. You'll need your password to unlock.",
        }
        
        response = control_descriptions.get(control, f"I can help you with {control}. What would you like me to do?")
        
        # Some controls need confirmation
        if control in ['shutdown', 'restart']:
            self.pending_clarification = {'type': 'confirm', 'action': control}
            return {
                'response': response,
                'action': None,
                'needs_clarification': True,
                'clarification_question': "Please confirm yes or no."
            }
        
        return {
            'response': response,
            'action': control,
            'needs_clarification': True if control in ['volume', 'brightness', 'wifi', 'bluetooth'] else False,
            'clarification_question': None
        }
    
    def _handle_help(self, intent: Dict, context: ApplicationContext) -> Dict[str, Any]:
        """Handle help requests."""
        topic = intent.get('topic', '')
        
        if topic:
            return {
                'response': f"I can help you with {topic}. In {context.app_name}, you have several options. Just tell me what you're trying to accomplish and I'll guide you.",
                'action': None,
                'needs_clarification': False,
                'clarification_question': None
            }
        
        # General help
        return {
            'response': f"""I'm your VA21 accessibility assistant. Here's how I can help:

1. Tell me what you want to do in plain language - like "I want to save my work" or "search for something on the internet"
2. Ask me questions - like "where am I?" or "what can I do here?"  
3. Give me commands - like "go back", "open files", or "turn up the volume"
4. Ask for explanations - I'll explain what anything means in detail

You're currently in {context.app_name}. What would you like to do?""",
            'action': None,
            'needs_clarification': False,
            'clarification_question': None
        }
    
    def _ask_clarification(self, user_input: str, context: ApplicationContext) -> Dict[str, Any]:
        """Ask for clarification when intent is unclear."""
        self.pending_clarification = 'general'
        
        return {
            'response': f"I want to help you with '{user_input}', but I'm not sure what you mean. Are you trying to: do something in {context.app_name}, open a different app, ask a question, or control the system?",
            'action': None,
            'needs_clarification': True,
            'clarification_question': "Could you tell me more about what you'd like to do?"
        }
    
    def _handle_clarification_response(self, user_input: str, context: ApplicationContext) -> Dict[str, Any]:
        """Handle response to a clarification question."""
        input_lower = user_input.lower().strip()
        clarification = self.pending_clarification
        self.pending_clarification = None
        
        # Handle confirmation responses
        if isinstance(clarification, dict) and clarification.get('type') == 'confirm':
            if any(word in input_lower for word in ['yes', 'yeah', 'sure', 'ok', 'confirm', 'proceed']):
                action = clarification.get('action')
                result = self.fara.execute_action(action, context)
                return {
                    'response': f"Confirmed. {result['description']}",
                    'action': action,
                    'needs_clarification': False,
                    'clarification_question': None
                }
            else:
                return {
                    'response': "Okay, I've cancelled that action. What else can I help you with?",
                    'action': None,
                    'needs_clarification': False,
                    'clarification_question': None
                }
        
        # Handle navigation clarification
        if clarification == 'navigation':
            return self._handle_navigation({'destination': user_input}, context)
        
        # Handle open app clarification
        if clarification == 'open_app':
            return self._handle_open_app({'app_name': user_input}, context)
        
        # Process as new request
        return self.process_request(user_input, context)


# ═══════════════════════════════════════════════════════════════════════════════
# INTELLIGENT SCREEN READER
# ═══════════════════════════════════════════════════════════════════════════════

class IntelligentScreenReader:
    """
    VA21's intelligent screen reader that provides natural language explanations.
    
    Unlike traditional screen readers that just say "button", "menu", etc.,
    this explains WHAT things do and WHY you might want to use them.
    """
    
    def __init__(self):
        self.tts_engine = None
        self.speaking = False
        self.speech_rate = 150
        
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.speech_rate)
                self.tts_engine.setProperty('volume', 0.9)
            except Exception:
                pass
    
    def speak(self, text: str, wait: bool = True):
        """Speak text using TTS."""
        if not self.tts_engine:
            print(f"🔊 [Would speak]: {text}")
            return
        
        self.speaking = True
        try:
            self.tts_engine.say(text)
            if wait:
                self.tts_engine.runAndWait()
        except Exception:
            print(f"🔊 [TTS Error]: {text}")
        finally:
            self.speaking = False
    
    def stop(self):
        """Stop speaking."""
        if self.tts_engine and self.speaking:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        self.speaking = False
    
    def describe_context(self, context: ApplicationContext) -> str:
        """Describe the current application context in natural language."""
        descriptions = {
            AppType.ZORK_SHELL: f"You are in {context.window_title}. This is VA21's unique text adventure interface where you can explore the system like a game. Just tell me what you want to do.",
            AppType.TERMINAL: "You are in the Terminal. This is where you can run commands directly. I can help you run commands - just tell me what you want to accomplish.",
            AppType.FILE_MANAGER: "You are in the File Manager. You can browse, copy, move, and organize your files here. Where would you like to go or what would you like to do?",
            AppType.TEXT_EDITOR: "You are in a Text Editor. You can write and edit documents here. I can help you save, copy, find text, or format your writing.",
            AppType.WEB_BROWSER: "You are in the Web Browser. You can browse the internet here. Tell me where you want to go or what you want to search for.",
            AppType.SETTINGS: "You are in Settings. You can configure your system here. What would you like to change?",
            AppType.RESEARCH_SUITE: "You are in the Research Suite. This has tools for academic research, citations, and analysis. How can I help with your research?",
            AppType.WRITING_SUITE: "You are in the Writing Suite. This has tools for writing documents, articles, and papers. What are you working on?",
            AppType.OBSIDIAN_VAULT: "You are in your Knowledge Vault. Your notes and research are stored here. Would you like to search, create a note, or explore your knowledge graph?",
            AppType.UNKNOWN: f"You are in {context.app_name}. Tell me what you'd like to do and I'll help you.",
        }
        
        return descriptions.get(context.app_type, f"You are in {context.app_name}. How can I help?")
    
    def announce_change(self, change_type: str, details: str) -> str:
        """Announce a change in natural language."""
        announcements = {
            'window_focus': f"Now in {details}.",
            'button_hover': f"This button will {details} when activated.",
            'menu_open': f"Menu opened. {details}",
            'dialog_open': f"A dialog has appeared. {details}",
            'notification': f"Notification: {details}",
            'action_complete': f"Done. {details}",
            'error': f"There was a problem: {details}. Would you like me to help fix it?",
        }
        
        return announcements.get(change_type, details)


# ═══════════════════════════════════════════════════════════════════════════════
# VOICE CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════

class VoiceController:
    """
    System-wide voice controller using push-to-talk (Super key).
    
    Integrates with Helper AI for conversational interaction
    and FARA layer for action execution across all apps.
    """
    
    def __init__(self, helper_ai: SystemWideHelperAI, screen_reader: IntelligentScreenReader,
                 fara_layer: SystemWideFARALayer):
        self.helper_ai = helper_ai
        self.screen_reader = screen_reader
        self.fara = fara_layer
        self.is_listening = False
        self.super_pressed = False
        self.recognizer = None
        self.microphone = None
        self.action_callback = None  # Callback to execute actions
        
        if VOICE_AVAILABLE:
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
            except OSError:
                self.microphone = None
    
    def start(self, action_callback: Callable = None):
        """Start listening for voice input."""
        self.action_callback = action_callback
        
        if KEYBOARD_AVAILABLE:
            self._start_keyboard_listener()
    
    def stop(self):
        """Stop voice controller."""
        self.is_listening = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
    
    def _start_keyboard_listener(self):
        """Start listening for Super key."""
        def _is_super_key(key):
            return key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r)
        
        def on_press(key):
            try:
                if _is_super_key(key) and not self.super_pressed:
                    self.super_pressed = True
                    self._start_listening()
            except AttributeError:
                pass
        
        def on_release(key):
            try:
                if _is_super_key(key) and self.super_pressed:
                    self.super_pressed = False
                    self._stop_listening()
            except AttributeError:
                pass
        
        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()
    
    def _start_listening(self):
        """Start capturing voice."""
        if not VOICE_AVAILABLE or not self.microphone:
            return
        
        self.is_listening = True
        self.screen_reader.speak("I'm listening. What would you like to do?", wait=False)
        print("\n🎤 Voice active - speak now...")
        
        def capture():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = self.recognizer.listen(source, timeout=10)
                
                if self.is_listening:
                    try:
                        text = self.recognizer.recognize_google(audio)
                        print(f"\n🎤 Heard: {text}")
                        self._process_voice_input(text)
                    except sr.UnknownValueError:
                        self.screen_reader.speak("I didn't catch that. Could you say it again?")
                    except sr.RequestError as e:
                        self.screen_reader.speak("Voice recognition is having trouble. You can type instead.")
            except Exception as e:
                print(f"\n🎤 Error: {e}")
        
        threading.Thread(target=capture, daemon=True).start()
    
    def _stop_listening(self):
        """Stop capturing voice."""
        self.is_listening = False
        print("🎤 Voice stopped")
    
    def _process_voice_input(self, text: str):
        """Process voice input through Helper AI."""
        # Get current context
        context = self.fara.get_current_context()
        
        # Process through Helper AI
        response = self.helper_ai.process_request(text, context)
        
        # Speak the response
        self.screen_reader.speak(response['response'], wait=False)
        print(f"\n🤖 Helper AI: {response['response']}")
        
        # Execute action if there is one
        if response['action'] and self.action_callback:
            self.action_callback(response['action'])


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ACCESSIBILITY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class VA21AccessibilitySystem:
    """
    Main accessibility system for VA21 OS.
    
    Provides:
    - System-wide voice control (Hold Super key)
    - Intelligent screen reading with natural language
    - Conversational interaction with Helper AI
    - Action execution via FARA layer
    - Support for 1,600+ languages
    
    This creates a unique accessibility experience that explains
    what's happening, asks clarifying questions, and executes
    tasks based on natural language requests.
    """
    
    def __init__(self):
        self.fara = SystemWideFARALayer()
        self.helper_ai = SystemWideHelperAI(self.fara)
        self.screen_reader = IntelligentScreenReader()
        self.voice_controller = VoiceController(
            self.helper_ai,
            self.screen_reader,
            self.fara
        )
        self.action_callback = None
    
    def start(self, action_callback: Callable = None):
        """Start the accessibility system."""
        self.action_callback = action_callback
        self.voice_controller.start(action_callback)
        
        # Announce startup
        self.screen_reader.speak(
            "VA21 accessibility system is ready. "
            "Hold the Super key and speak to tell me what you'd like to do. "
            "I'll explain everything and help you navigate the entire system."
        )
        print("\n♿ VA21 Accessibility System Active")
        print("   Hold Super key for voice input")
        print("   Conversational AI ready")
    
    def stop(self):
        """Stop the accessibility system."""
        self.voice_controller.stop()
        self.screen_reader.speak("Accessibility system stopped.")
    
    def announce(self, text: str):
        """Announce something to the user."""
        self.screen_reader.speak(text)
    
    def describe_current_context(self):
        """Describe what's currently on screen."""
        context = self.fara.get_current_context()
        description = self.screen_reader.describe_context(context)
        self.screen_reader.speak(description)
        return description
    
    def process_text_input(self, text: str) -> Dict[str, Any]:
        """Process text input (for typed commands from accessibility users)."""
        context = self.fara.get_current_context()
        response = self.helper_ai.process_request(text, context)
        
        # Speak the response
        self.screen_reader.speak(response['response'], wait=False)
        
        # Execute action if present
        if response['action'] and self.action_callback:
            self.action_callback(response['action'])
        
        return response


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the accessibility system."""
    print("=" * 60)
    print("VA21 OS - Accessibility System Test")
    print("=" * 60)
    
    def handle_action(action: str):
        print(f"\n[ACTION] Would execute: {action}")
    
    system = VA21AccessibilitySystem()
    system.start(action_callback=handle_action)
    
    print("\nType commands to test (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            response = system.process_text_input(user_input)
            print(f"\n[Response]: {response['response']}")
            if response['action']:
                print(f"[Action]: {response['action']}")
                
        except (KeyboardInterrupt, EOFError):
            break
    
    system.stop()
    print("\nAccessibility system stopped.")


if __name__ == "__main__":
    main()
