# VA21 Obsidian Package
"""
VA21 Obsidian Integration - Knowledge management for VA21 Research OS.

Features:
- Markdown-based notes with [[wiki-links]]
- Knowledge graph
- AI-assisted research
- Sensitive content protection
"""

from .vault_manager import ObsidianVault, get_vault, Note, SensitivityLevel

__version__ = "1.0.0"
