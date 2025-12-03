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

Unlike traditional screen readers that just read keywords,
VA21 explains what things do, asks clarifying questions,
and executes actions based on natural language.

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
]
