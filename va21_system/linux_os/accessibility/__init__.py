#!/usr/bin/env python3
"""
VA21 OS - Accessibility Module
==============================

🙏 STATE-OF-THE-ART ACCESSIBILITY (Unique to VA21!) 🙏

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

Provides system-wide accessibility features including:
- Intelligent screen reader with natural language explanations
- Voice control for all applications via FARA layer
- Helper AI with conversational interaction
- Push-to-talk voice input (Hold Super key)
- Support for 1,600+ languages including 100+ Indian dialects
- Zork-style interface for EVERY application
- Om Vinayaka Accessibility Knowledge Base AI (THE CORE)
- Self-Learning System with LangChain + Obsidian integration
- Self-Reflection & Introspection (dynamic thinking)
- Context-Aware Summary Engine to prevent AI hallucinations
- Idle Mode Self-Improvement System
- Auto Dynamic Memory Backups

Om Vinayaka AI Features:
- Automatic Zork UX Generation: Every app gets a text adventure interface
- System-Wide Voice Control: Control ANY application with voice
- CLI Tool Wrapper: Gemini CLI, GitHub Copilot CLI, Codex accessible
- Knowledge Base: LangChain + Obsidian mind maps store all interfaces
- Clarifying Questions: AI asks for details when intent is unclear
- Context-Aware Execution: Understands active app and user intent
- Self-Learning: Gets smarter with every interaction
- Introspection: Reflects on behavior, asks why/what questions
- Idle Self-Improvement: Optimizes workflows, learns from errors
- Auto Backup: Never forgets, survives power loss

Example Conversation:
    User: "I want to find something on the internet"
    VA21: "I can help you search. What would you like to look up?"
    User: "Climate change research papers"
    VA21: "Searching for climate change research papers."

CLI Tool Accessibility Example:
    User: "Ask Gemini about Python decorators"
    VA21: "You stand before the GEMINI ORACLE..."

Guardian AI Note:
Guardian AI runs in a sandboxed Ollama at the kernel level,
completely isolated from this user-facing accessibility system.

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav

Om Vinayaka - May obstacles be removed from your computing journey.
Making technology accessible to everyone, in every language.
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

from .fara_compatibility import (
    AutomaticFARALayerCreator,
    FARAKnowledgeBase,
    FARAProfile,
    FARAAction,
    UIElementDetector,
    ActionGenerator,
    AppFramework,
    AppCategory,
    get_fara_creator,
    FARA_VERSION,
)

from .performance_optimizer import (
    PerformanceOptimizer,
    ModelPreloader,
    WarmUpEngine,
    ResponseCache,
    ModelPriority,
    ModelState,
    get_performance_optimizer,
    OPTIMIZER_VERSION,
)

from .feature_discovery import (
    FeatureDiscoveryEngine,
    FeatureDatabase,
    Feature,
    UserProgress,
    UserExperience,
    FeatureCategory,
    get_feature_discovery,
    DISCOVERY_VERSION,
)

from .unified_app_knowledge import (
    UnifiedAppCreator,
    UnifiedAppKnowledgeBase,
    UnifiedAppProfile,
    get_unified_creator,
    UNIFIED_KNOWLEDGE_VERSION,
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
    
    # Automatic FARA Layer Creator (Unique to VA21!)
    'AutomaticFARALayerCreator',
    'FARAKnowledgeBase',
    'FARAProfile',
    'FARAAction',
    'UIElementDetector',
    'ActionGenerator',
    'AppFramework',
    'AppCategory',
    'get_fara_creator',
    'FARA_VERSION',
    
    # Performance Optimizer
    'PerformanceOptimizer',
    'ModelPreloader',
    'WarmUpEngine',
    'ResponseCache',
    'ModelPriority',
    'ModelState',
    'get_performance_optimizer',
    'OPTIMIZER_VERSION',
    
    # Feature Discovery & User Adoption
    'FeatureDiscoveryEngine',
    'FeatureDatabase',
    'Feature',
    'UserProgress',
    'UserExperience',
    'FeatureCategory',
    'get_feature_discovery',
    'DISCOVERY_VERSION',
    
    # Unified FARA + Zork Knowledge System
    'UnifiedAppCreator',
    'UnifiedAppKnowledgeBase',
    'UnifiedAppProfile',
    'get_unified_creator',
    'UNIFIED_KNOWLEDGE_VERSION',
]
