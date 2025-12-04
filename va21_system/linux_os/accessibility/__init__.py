#!/usr/bin/env python3
"""
VA21 OS - Accessibility Module
==============================

Provides system-wide accessibility features including:
- Intelligent screen reader with natural language explanations
- Voice control for all applications via FARA layer
- Helper AI with conversational interaction
- Push-to-talk voice input (Hold Super key)
- Support for 1,600+ languages
- Zork-style interface for EVERY application
- Om Vinayaka Accessibility Knowledge Base AI
- Self-Learning System with LangChain + Obsidian integration
- Context-Aware Summary Engine to prevent AI hallucinations
- Idle Mode Self-Improvement System (NEW!)

Unlike traditional screen readers that just read keywords,
VA21 explains what things do, asks clarifying questions,
and executes actions based on natural language.

Om Vinayaka Architecture:
- Automatically activated when accessibility/voice features are used
- Creates Zork-style UX for every app when installed
- Enables voice users to interact with ANY app in the full OS
- Uses LangChain + Obsidian mind maps for knowledge storage
- Self-learning system that gets smarter over time
- Context-aware summary engine prevents AI overload
- FARA layer executes actions across the entire OS
- Idle mode self-improvement during user inactivity (NEW!)

Idle Mode Self-Improvement Features (NEW!):
- Researches best ways to optimize user workflows during idle time
- Adapts system components to enhance performance
- Self-reflects on actions and learns from them (dynamic thinking)
- Analyzes errors and develops prevention strategies
- Always helping, even when at rest!

Guardian AI Note:
Guardian AI runs in a sandboxed Ollama at the kernel level,
completely isolated from this user-facing accessibility system.

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav

Om Vinayaka - May obstacles be removed from your computing journey.
"""

from .voice_accessibility import (
    VA21AccessibilitySystem,
    SystemWideHelperAI,
    SystemWideFARALayer,
    VoiceController,
    IntelligentScreenReader
)

from .app_zork_generator import (
    AppZorkManager,
    AccessibilityKnowledgeBase,
    ZorkInterfaceGenerator,
    AppAnalyzer,
    AppZorkInterface
)

from .om_vinayaka_ai import (
    OmVinayakaAI,
    TerminalZorkAdapter,
    AccessibilityMindMap,
    CLIToolInterface,
    get_om_vinayaka,
    OM_VINAYAKA_VERSION,
)

from .self_learning import (
    SelfLearningEngine,
    LearningKnowledgeBase,
    CommandPattern,
    UserPreference,
    AppUsagePattern,
    get_learning_engine,
)

from .summary_engine import (
    SummaryEngine,
    ContextAwareSummarizer,
    ResourceCalculator,
    get_summary_engine,
    AI_CONTEXT_LIMITS,
    PRIORITY_LEVELS,
)

from .idle_mode import (
    IdleModeManager,
    WorkflowOptimizer,
    ErrorAnalyzer,
    SelfReflectionEngine,
    get_idle_mode_manager,
    IDLE_MODE_VERSION,
)

from .persistent_memory import (
    PersistentMemoryManager,
    get_persistent_memory,
)

__all__ = [
    # Main accessibility system
    'VA21AccessibilitySystem',
    'SystemWideHelperAI', 
    'SystemWideFARALayer',
    'VoiceController',
    'IntelligentScreenReader',
    
    # App Zork interface generator
    'AppZorkManager',
    'AccessibilityKnowledgeBase',
    'ZorkInterfaceGenerator',
    'AppAnalyzer',
    'AppZorkInterface',
    
    # Om Vinayaka Accessibility Knowledge Base AI - THE CORE
    'OmVinayakaAI',
    'TerminalZorkAdapter',
    'AccessibilityMindMap',
    'CLIToolInterface',
    'get_om_vinayaka',
    'OM_VINAYAKA_VERSION',
    
    # Self-Learning with LangChain + Obsidian
    'SelfLearningEngine',
    'LearningKnowledgeBase',
    'CommandPattern',
    'UserPreference',
    'AppUsagePattern',
    'get_learning_engine',
    
    # Context-Aware Summary Engine
    'SummaryEngine',
    'ContextAwareSummarizer',
    'ResourceCalculator',
    'get_summary_engine',
    'AI_CONTEXT_LIMITS',
    'PRIORITY_LEVELS',
    
    # Idle Mode Self-Improvement System
    'IdleModeManager',
    'WorkflowOptimizer',
    'ErrorAnalyzer',
    'SelfReflectionEngine',
    'get_idle_mode_manager',
    'IDLE_MODE_VERSION',
    
    # Persistent Memory with Auto Dynamic Backups
    'PersistentMemoryManager',
    'get_persistent_memory',
]
