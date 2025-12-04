#!/usr/bin/env python3
"""
VA21 OS - Coding IDE with AI-Powered Development
=================================================

Om Vinayaka - May obstacles be removed from your coding journey.

A special coding IDE for VA21 OS that includes:
- AI helper integration with API key support
- FARA layer for voice assistance
- ChatGPT-style chatbox for interactive development
- Smart suggestion engine for languages and systems
- Multi-agent task distribution with dynamic context management
- Full-stack development support (frontend, backend, OS requirements)
- SearXNG integration for searching best practices

This module creates an intelligent development environment where users
can describe what they want to build, and the system:
1. Understands the idea/application concept
2. Suggests best languages based on target OS and requirements
3. Plans the development approach
4. Distributes work to specialized agents
5. Manages context dynamically to avoid overwhelming any single agent
6. Delivers complete full-stack applications

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.
"""

from .ide_core import CodingIDE, get_coding_ide
from .suggest_engine import SuggestEngine, get_suggest_engine
from .ai_helper import AIHelper, get_ai_helper
from .multi_agent import MultiAgentOrchestrator, get_orchestrator
from .project_builder import ProjectBuilder, get_project_builder

__version__ = "1.0.0"
__all__ = [
    "CodingIDE",
    "get_coding_ide",
    "SuggestEngine",
    "get_suggest_engine",
    "AIHelper",
    "get_ai_helper",
    "MultiAgentOrchestrator",
    "get_orchestrator",
    "ProjectBuilder",
    "get_project_builder",
]
