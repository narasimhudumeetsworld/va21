#!/usr/bin/env python3
"""
VA21 OS - Multi-Agent System
============================

Om Vinayaka Multi-Agent System provides intelligent AI agents that can:
- Use local AI via built-in Ollama
- Use external APIs (OpenAI, Anthropic, etc.)
- Get automatically assigned roles with experience and context
- Work together without feature overlap
- Integrate seamlessly with Om Vinayaka AI

Agent Architecture:
- Each agent has a defined role (Researcher, Coder, Writer, etc.)
- Agents are assigned experience levels (Junior, Mid, Senior, Expert)
- Agents receive context summaries of what they need to accomplish
- The Orchestrator ensures no feature overlap between agents

Om Vinayaka - May obstacles be removed from your path.
"""

from .agent_manager import (
    AgentManager,
    get_agent_manager,
)
from .agent_core import (
    Agent,
    AgentRole,
    AgentConfig,
    AgentExperience,
)
from .ai_providers import (
    AIProvider,
    OllamaProvider,
    APIProvider,
    get_ai_provider,
)

__all__ = [
    'AgentManager',
    'get_agent_manager',
    'Agent',
    'AgentRole',
    'AgentConfig',
    'AgentExperience',
    'AIProvider',
    'OllamaProvider',
    'APIProvider',
    'get_ai_provider',
]
