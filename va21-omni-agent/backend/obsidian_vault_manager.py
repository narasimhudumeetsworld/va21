"""
Obsidian Vault Manager - Knowledge Graph and LLM Memory System

This module provides an Obsidian-compatible vault system for organizing research,
creating knowledge graphs, and providing persistent memory for LLM interactions.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any

class ObsidianVaultManager:
    """
    Manages an Obsidian-compatible vault for research organization and LLM memory.
    
    Features:
    - Markdown note creation with wiki-style links
    - Knowledge graph generation via backlinks
    - Tag-based organization
    - LLM conversation memory storage
    - Research log management
    - Sensitive information redaction tracking
    """
    
    def __init__(self, vault_path: str = "data/research_vault"):
        self.vault_path = vault_path
        self.notes_path = os.path.join(vault_path, "notes")
        self.memory_path = os.path.join(vault_path, "llm_memory")
        self.research_path = os.path.join(vault_path, "research")
        self.logs_path = os.path.join(vault_path, "logs")
        self.graph_path = os.path.join(vault_path, "graph")
        self.templates_path = os.path.join(vault_path, "templates")
        
        self._initialize_vault()
    
    def _initialize_vault(self):
        """Initialize the vault directory structure."""
        directories = [
            self.vault_path,
            self.notes_path,
            self.memory_path,
            self.research_path,
            self.logs_path,
            self.graph_path,
            self.templates_path,
            os.path.join(self.research_path, "sessions"),
            os.path.join(self.research_path, "topics"),
            os.path.join(self.logs_path, "terminal"),
            os.path.join(self.logs_path, "chat"),
            os.path.join(self.logs_path, "workflow"),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Create default templates
        self._create_default_templates()
        
        # Initialize graph index
        self._initialize_graph_index()
    
    def _create_default_templates(self):
        """Create default note templates."""
        templates = {
            "research_session.md": """---
title: {{title}}
date: {{date}}
type: research_session
tags: [research, session]
---

# {{title}}

## Objective
{{objective}}

## Notes


## Findings


## Related Topics
- [[]]

## References

""",
            "topic.md": """---
title: {{title}}
date: {{date}}
type: topic
tags: [topic]
---

# {{title}}

## Overview


## Key Concepts


## Related Notes
- [[]]

## Sources

""",
            "llm_memory.md": """---
title: LLM Memory Entry
date: {{date}}
type: llm_memory
session_id: {{session_id}}
tags: [memory, llm]
---

# Memory Entry

## Context
{{context}}

## Key Facts


## Related Memories
- [[]]

"""
        }
        
        for filename, content in templates.items():
            template_path = os.path.join(self.templates_path, filename)
            if not os.path.exists(template_path):
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def _initialize_graph_index(self):
        """Initialize the graph index file."""
        index_path = os.path.join(self.graph_path, "index.json")
        if not os.path.exists(index_path):
            initial_index = {
                "nodes": [],
                "edges": [],
                "last_updated": datetime.now().isoformat()
            }
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(initial_index, f, indent=2)
    
    def create_note(self, title: str, content: str, note_type: str = "note",
                    tags: List[str] = None, metadata: Dict = None) -> str:
        """
        Create a new note in the vault.
        
        Args:
            title: Note title
            content: Note content (markdown)
            note_type: Type of note (note, research, topic, etc.)
            tags: List of tags
            metadata: Additional metadata
        
        Returns:
            Path to the created note
        """
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}
        
        # Sanitize title for filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        filename = f"{safe_title}.md"
        
        # Determine path based on type
        if note_type == "research":
            note_path = os.path.join(self.research_path, "topics", filename)
        elif note_type == "session":
            note_path = os.path.join(self.research_path, "sessions", filename)
        elif note_type == "memory":
            note_path = os.path.join(self.memory_path, filename)
        else:
            note_path = os.path.join(self.notes_path, filename)
        
        # Build frontmatter
        frontmatter = {
            "title": title,
            "date": datetime.now().isoformat(),
            "type": note_type,
            "tags": tags,
            **metadata
        }
        
        # Create note content
        full_content = f"""---
{self._dict_to_yaml(frontmatter)}
---

{content}
"""
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # Update graph index
        self._update_graph_index(title, note_path, tags)
        
        return note_path
    
    def _dict_to_yaml(self, d: Dict) -> str:
        """Simple dict to YAML-like string conversion."""
        lines = []
        for key, value in d.items():
            if isinstance(value, list):
                lines.append(f"{key}: [{', '.join(str(v) for v in value)}]")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        return '\n'.join(lines)
    
    def _update_graph_index(self, title: str, path: str, tags: List[str]):
        """Update the graph index with a new node."""
        index_path = os.path.join(self.graph_path, "index.json")
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        # Generate node ID
        node_id = hashlib.md5(path.encode()).hexdigest()[:8]
        
        # Add node if not exists
        existing_ids = [n['id'] for n in index['nodes']]
        if node_id not in existing_ids:
            index['nodes'].append({
                "id": node_id,
                "title": title,
                "path": path,
                "tags": tags
            })
        
        index['last_updated'] = datetime.now().isoformat()
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
    
    def add_llm_memory(self, session_id: str, context: str, 
                       key_facts: List[str], related_topics: List[str] = None) -> str:
        """
        Add a memory entry for LLM context persistence.
        
        Args:
            session_id: Unique session identifier
            context: The context or conversation summary
            key_facts: List of key facts to remember
            related_topics: Related topic links
        
        Returns:
            Path to the memory file
        """
        if related_topics is None:
            related_topics = []
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = f"Memory_{session_id}_{timestamp}"
        
        # Build content
        facts_md = "\n".join(f"- {fact}" for fact in key_facts)
        topics_md = "\n".join(f"- [[{topic}]]" for topic in related_topics)
        
        content = f"""# Memory Entry

## Context
{context}

## Key Facts
{facts_md}

## Related Topics
{topics_md}
"""
        
        return self.create_note(
            title=title,
            content=content,
            note_type="memory",
            tags=["memory", "llm", session_id],
            metadata={"session_id": session_id}
        )
    
    def log_terminal_session(self, terminal_id: str, commands: List[Dict]) -> str:
        """
        Log a terminal session to the vault.
        
        Args:
            terminal_id: Unique terminal identifier
            commands: List of command dictionaries with 'command' and 'output' keys
        
        Returns:
            Path to the log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"terminal_{terminal_id}_{timestamp}.md"
        log_path = os.path.join(self.logs_path, "terminal", filename)
        
        # Build log content
        commands_md = ""
        for cmd in commands:
            commands_md += f"\n### Command\n```bash\n{cmd.get('command', '')}\n```\n"
            if cmd.get('output'):
                commands_md += f"\n### Output\n```\n{cmd.get('output', '')}\n```\n"
        
        content = f"""---
title: Terminal Session {terminal_id}
date: {datetime.now().isoformat()}
type: terminal_log
terminal_id: {terminal_id}
tags: [log, terminal]
---

# Terminal Session Log

**Terminal ID:** {terminal_id}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Commands
{commands_md}
"""
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return log_path
    
    def log_chat_session(self, session_id: str, messages: List[Dict]) -> str:
        """
        Log a chat session to the vault.
        
        Args:
            session_id: Unique session identifier
            messages: List of message dictionaries with 'role' and 'content' keys
        
        Returns:
            Path to the log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{session_id}_{timestamp}.md"
        log_path = os.path.join(self.logs_path, "chat", filename)
        
        # Build chat content
        messages_md = ""
        for msg in messages:
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')
            messages_md += f"\n**{role}:**\n{content}\n"
        
        content = f"""---
title: Chat Session {session_id}
date: {datetime.now().isoformat()}
type: chat_log
session_id: {session_id}
tags: [log, chat]
---

# Chat Session Log

**Session ID:** {session_id}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Conversation
{messages_md}
"""
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return log_path
    
    def search_vault(self, query: str, note_type: str = None) -> List[Dict]:
        """
        Search the vault for notes matching a query.
        
        Args:
            query: Search query
            note_type: Optional filter by note type
        
        Returns:
            List of matching note metadata
        """
        results = []
        query_lower = query.lower()
        
        # Search all markdown files
        for root, _, files in os.walk(self.vault_path):
            for filename in files:
                if not filename.endswith('.md'):
                    continue
                
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract frontmatter
                    metadata = self._extract_frontmatter(content)
                    
                    # Filter by type if specified
                    if note_type and metadata.get('type') != note_type:
                        continue
                    
                    # Search in title and content
                    if query_lower in content.lower():
                        results.append({
                            "path": file_path,
                            "title": metadata.get('title', filename),
                            "type": metadata.get('type', 'unknown'),
                            "tags": metadata.get('tags', []),
                            "date": metadata.get('date')
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        return results
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """Extract frontmatter from markdown content."""
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}
        
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Parse lists
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                
                frontmatter[key] = value
        
        return frontmatter
    
    def get_graph_data(self) -> Dict:
        """
        Get the knowledge graph data for visualization.
        
        Returns:
            Graph data with nodes and edges
        """
        index_path = os.path.join(self.graph_path, "index.json")
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        # Build edges from wiki-links
        self._build_graph_edges(index)
        
        return index
    
    def _build_graph_edges(self, index: Dict):
        """Build edges from wiki-links in notes."""
        edges = []
        node_titles = {n['title']: n['id'] for n in index['nodes']}
        
        for node in index['nodes']:
            try:
                with open(node['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find wiki-links [[link]]
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                
                for link in links:
                    if link in node_titles:
                        edges.append({
                            "source": node['id'],
                            "target": node_titles[link]
                        })
            except Exception:
                continue
        
        index['edges'] = edges
    
    def get_memory_context(self, session_id: str, limit: int = 5) -> List[str]:
        """
        Retrieve memory context for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of memory entries to retrieve
        
        Returns:
            List of memory contexts
        """
        memories = []
        
        # Search for memory files matching the session
        for filename in os.listdir(self.memory_path):
            if not filename.endswith('.md'):
                continue
            
            file_path = os.path.join(self.memory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                metadata = self._extract_frontmatter(content)
                if session_id in metadata.get('tags', []) or \
                   metadata.get('session_id') == session_id:
                    # Extract context section
                    context_match = re.search(r'## Context\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                    if context_match:
                        memories.append(context_match.group(1).strip())
            except Exception:
                continue
        
        return memories[:limit]
    
    def create_research_session(self, title: str, objective: str, 
                                  topics: List[str] = None) -> str:
        """
        Create a new research session.
        
        Args:
            title: Session title
            objective: Research objective
            topics: Related topics
        
        Returns:
            Path to the session note
        """
        if topics is None:
            topics = []
        
        topics_md = "\n".join(f"- [[{topic}]]" for topic in topics)
        
        content = f"""# {title}

## Objective
{objective}

## Notes


## Findings


## Related Topics
{topics_md}

## References

"""
        
        return self.create_note(
            title=title,
            content=content,
            note_type="session",
            tags=["research", "session"] + topics
        )


# Example usage
if __name__ == '__main__':
    vault = ObsidianVaultManager()
    
    # Create a research session
    session_path = vault.create_research_session(
        title="Security Research Session 1",
        objective="Investigate new threat intelligence feeds",
        topics=["threat_intelligence", "rss_feeds"]
    )
    print(f"Created research session: {session_path}")
    
    # Add LLM memory
    memory_path = vault.add_llm_memory(
        session_id="test_session",
        context="User asked about threat intelligence integration",
        key_facts=["User wants RSS feeds", "Focus on security blogs"],
        related_topics=["threat_intelligence"]
    )
    print(f"Created memory: {memory_path}")
    
    # Search vault
    results = vault.search_vault("threat")
    print(f"Search results: {results}")
