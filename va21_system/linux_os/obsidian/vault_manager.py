#!/usr/bin/env python3
"""
VA21 Research OS - Obsidian Knowledge Base Integration
========================================================

Integrates Obsidian-style knowledge management with the VA21 Research OS.
Provides wiki-style linking, knowledge graphs, and AI-assisted research
with privacy-first design.

Features:
- Markdown-based notes with [[wiki-links]]
- Knowledge graph visualization
- AI-assisted note taking and research
- Sensitive content marking and protection
- Local-only research (never exposed to internet)

Om Vinayaka - Knowledge flows like the Ganges, pure and protected.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class SensitivityLevel(Enum):
    """Sensitivity levels for content."""
    PUBLIC = "public"           # Can be shared, searched
    INTERNAL = "internal"       # For personal use, not shared
    SENSITIVE = "sensitive"     # Marked sensitive by user
    CONFIDENTIAL = "confidential"  # AI-detected or user-marked confidential
    REDACTED = "redacted"       # Content is redacted/hidden


@dataclass
class Note:
    """Represents a note in the knowledge base."""
    id: str
    title: str
    content: str
    path: str
    tags: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)  # [[wiki-links]]
    backlinks: List[str] = field(default_factory=list)
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    is_ai_generated: bool = False
    author: str = "researcher"


@dataclass
class ResearchSession:
    """Represents a research session."""
    session_id: str
    title: str
    objective: str
    notes: List[str] = field(default_factory=list)  # Note IDs
    keywords: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, completed, archived


class ObsidianVault:
    """
    VA21 Obsidian-Style Knowledge Vault
    
    A privacy-first knowledge management system integrated with VA21 Research OS.
    Provides Obsidian-compatible markdown notes with wiki-style linking,
    knowledge graphs, and AI-assisted research capabilities.
    
    Privacy Features:
    - All data stored locally
    - Sensitive content marking
    - Research never exposed to internet
    - Keyword-only external search
    
    AI Integration:
    - Automatic content summarization
    - Link suggestions
    - Sensitive content detection
    - Research assistance
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, vault_path: str = "/va21/vault", helper_ai=None):
        self.vault_path = vault_path
        self.helper_ai = helper_ai
        
        # Directories
        self.notes_path = os.path.join(vault_path, "notes")
        self.research_path = os.path.join(vault_path, "research")
        self.templates_path = os.path.join(vault_path, "templates")
        self.attachments_path = os.path.join(vault_path, "attachments")
        self.sensitive_path = os.path.join(vault_path, ".sensitive")
        
        # Create directories
        for path in [self.notes_path, self.research_path, self.templates_path,
                     self.attachments_path, self.sensitive_path]:
            os.makedirs(path, exist_ok=True)
        
        # Index
        self.notes_index: Dict[str, Note] = {}
        self.tags_index: Dict[str, Set[str]] = {}  # tag -> note_ids
        self.links_graph: Dict[str, Set[str]] = {}  # note_id -> linked_note_ids
        
        # Research sessions
        self.research_sessions: Dict[str, ResearchSession] = {}
        
        # Sensitive patterns for AI detection (improved patterns)
        self.sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN format XXX-XX-XXXX
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b',  # Credit card with optional separators
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',  # Email (fixed)
            r'password\s*[:=]\s*\S+',   # Passwords
            r'api[_-]?key\s*[:=]\s*\S+',  # API keys
            r'secret\s*[:=]\s*\S+',     # Secrets
            r'token\s*[:=]\s*\S+',      # Tokens
            r'private[_-]?key\s*[:=]',  # Private keys
            r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',  # PEM private keys
        ]
        
        # Load existing notes
        self._load_vault()
        
        print(f"[Obsidian] Vault initialized at {vault_path}")
        print(f"[Obsidian] {len(self.notes_index)} notes loaded")
    
    def _load_vault(self):
        """Load all notes from the vault."""
        for root, dirs, files in os.walk(self.notes_path):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    self._load_note(filepath)
    
    def _load_note(self, filepath: str) -> Optional[Note]:
        """Load a single note from file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter if present
            metadata = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        # Simple YAML-like parsing
                        for line in parts[1].strip().split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()
                        content = parts[2].strip()
                    except:
                        pass
            
            # Extract title from filename or first heading
            title = os.path.basename(filepath).replace('.md', '')
            if content.startswith('# '):
                title = content.split('\n')[0][2:].strip()
            
            # Extract links
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            
            # Extract tags
            tags = re.findall(r'#(\w+)', content)
            if 'tags' in metadata:
                tags.extend(metadata['tags'].replace('[', '').replace(']', '').split(','))
            
            # Determine sensitivity
            sensitivity = SensitivityLevel.INTERNAL
            if metadata.get('sensitivity'):
                try:
                    sensitivity = SensitivityLevel(metadata['sensitivity'])
                except:
                    pass
            
            note_id = hashlib.md5(filepath.encode()).hexdigest()[:12]
            
            note = Note(
                id=note_id,
                title=title,
                content=content,
                path=filepath,
                tags=[t.strip().lower() for t in tags],
                links=links,
                sensitivity=sensitivity,
                metadata=metadata
            )
            
            self.notes_index[note_id] = note
            
            # Update indices
            for tag in note.tags:
                if tag not in self.tags_index:
                    self.tags_index[tag] = set()
                self.tags_index[tag].add(note_id)
            
            self.links_graph[note_id] = set()
            for link in links:
                self.links_graph[note_id].add(link)
            
            return note
            
        except Exception as e:
            print(f"[Obsidian] Error loading {filepath}: {e}")
            return None
    
    def create_note(self, title: str, content: str = "", 
                    tags: List[str] = None, sensitivity: SensitivityLevel = None,
                    template: str = None) -> Note:
        """
        Create a new note in the vault.
        
        Args:
            title: Note title
            content: Note content (markdown)
            tags: List of tags
            sensitivity: Sensitivity level
            template: Template name to use
            
        Returns:
            Created Note object
        """
        # Generate filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        filename = f"{safe_title}.md"
        filepath = os.path.join(self.notes_path, filename)
        
        # Handle duplicate filenames
        counter = 1
        while os.path.exists(filepath):
            filename = f"{safe_title}_{counter}.md"
            filepath = os.path.join(self.notes_path, filename)
            counter += 1
        
        # Load template if specified
        if template:
            template_content = self._load_template(template)
            if template_content:
                content = template_content.replace('{{title}}', title)
                content = content.replace('{{date}}', datetime.now().strftime('%Y-%m-%d'))
        
        # Add frontmatter
        if tags is None:
            tags = []
        
        if sensitivity is None:
            # Check for sensitive content
            sensitivity = self._detect_sensitivity(content)
        
        frontmatter = f"""---
title: {title}
created: {datetime.now().isoformat()}
tags: [{', '.join(tags)}]
sensitivity: {sensitivity.value}
---

"""
        
        full_content = frontmatter + f"# {title}\n\n" + content
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # Create note object
        note_id = hashlib.md5(filepath.encode()).hexdigest()[:12]
        note = Note(
            id=note_id,
            title=title,
            content=content,
            path=filepath,
            tags=tags,
            links=re.findall(r'\[\[([^\]]+)\]\]', content),
            sensitivity=sensitivity
        )
        
        self.notes_index[note_id] = note
        
        # Update indices
        for tag in tags:
            if tag not in self.tags_index:
                self.tags_index[tag] = set()
            self.tags_index[tag].add(note_id)
        
        print(f"[Obsidian] Created note: {title}")
        return note
    
    def _load_template(self, template_name: str) -> Optional[str]:
        """Load a template file."""
        template_path = os.path.join(self.templates_path, f"{template_name}.md")
        try:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except:
            pass
        return None
    
    def _detect_sensitivity(self, content: str) -> SensitivityLevel:
        """Detect if content contains sensitive information."""
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return SensitivityLevel.SENSITIVE
        
        # Use AI helper if available
        if self.helper_ai:
            try:
                analysis = self.helper_ai.analyze_sensitivity(content)
                if "CONFIDENTIAL" in analysis.upper():
                    return SensitivityLevel.CONFIDENTIAL
                elif "SENSITIVE" in analysis.upper():
                    return SensitivityLevel.SENSITIVE
            except:
                pass
        
        return SensitivityLevel.INTERNAL
    
    def mark_sensitive(self, note_id: str, level: SensitivityLevel = SensitivityLevel.SENSITIVE,
                       reason: str = "") -> bool:
        """
        Mark a note as sensitive.
        
        Args:
            note_id: Note ID
            level: Sensitivity level
            reason: Reason for marking (optional)
            
        Returns:
            Success status
        """
        if note_id not in self.notes_index:
            return False
        
        note = self.notes_index[note_id]
        note.sensitivity = level
        note.metadata['sensitivity_reason'] = reason
        note.metadata['marked_sensitive_at'] = datetime.now().isoformat()
        
        # Update file
        self._save_note(note)
        
        print(f"[Obsidian] Marked '{note.title}' as {level.value}")
        return True
    
    def _save_note(self, note: Note):
        """Save a note to file."""
        frontmatter = f"""---
title: {note.title}
created: {note.created_at.isoformat() if isinstance(note.created_at, datetime) else note.created_at}
modified: {datetime.now().isoformat()}
tags: [{', '.join(note.tags)}]
sensitivity: {note.sensitivity.value}
"""
        for key, value in note.metadata.items():
            if key not in ['title', 'created', 'modified', 'tags', 'sensitivity']:
                frontmatter += f"{key}: {value}\n"
        frontmatter += "---\n\n"
        
        full_content = frontmatter + f"# {note.title}\n\n" + note.content
        
        with open(note.path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    
    def search(self, query: str, include_sensitive: bool = False) -> List[Note]:
        """
        Search notes by content and title.
        
        Args:
            query: Search query
            include_sensitive: Include sensitive notes in results
            
        Returns:
            List of matching notes
        """
        results = []
        query_lower = query.lower()
        
        for note in self.notes_index.values():
            # Skip sensitive content if not requested
            if not include_sensitive and note.sensitivity in [
                SensitivityLevel.SENSITIVE, 
                SensitivityLevel.CONFIDENTIAL,
                SensitivityLevel.REDACTED
            ]:
                continue
            
            # Search in title and content
            if (query_lower in note.title.lower() or 
                query_lower in note.content.lower() or
                any(query_lower in tag for tag in note.tags)):
                results.append(note)
        
        return results
    
    def search_by_tag(self, tag: str) -> List[Note]:
        """Search notes by tag."""
        tag = tag.lower().lstrip('#')
        if tag in self.tags_index:
            return [self.notes_index[nid] for nid in self.tags_index[tag] 
                    if nid in self.notes_index]
        return []
    
    def get_keywords_for_external_search(self, note_id: str) -> List[str]:
        """
        Extract keywords from a note for external search.
        This is the ONLY way research can interact with external services.
        Content itself is never shared.
        
        Args:
            note_id: Note ID
            
        Returns:
            List of keywords (not sensitive content)
        """
        if note_id not in self.notes_index:
            return []
        
        note = self.notes_index[note_id]
        
        # Extract keywords from tags and title only
        keywords = list(note.tags)
        
        # Add words from title (excluding common words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                      'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                      'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                      'through', 'during', 'before', 'after', 'above', 'below',
                      'between', 'under', 'again', 'further', 'then', 'once'}
        
        title_words = re.findall(r'\b\w+\b', note.title.lower())
        keywords.extend([w for w in title_words if w not in stop_words and len(w) > 2])
        
        # Remove duplicates and sensitive terms
        keywords = list(set(keywords))
        
        # Filter out any potentially sensitive keywords
        filtered = []
        for kw in keywords:
            is_sensitive = False
            for pattern in self.sensitive_patterns:
                if re.search(pattern, kw, re.IGNORECASE):
                    is_sensitive = True
                    break
            if not is_sensitive:
                filtered.append(kw)
        
        return filtered[:10]  # Limit to 10 keywords
    
    def get_linked_notes(self, note_id: str) -> List[Note]:
        """Get notes linked from this note."""
        if note_id not in self.notes_index:
            return []
        
        note = self.notes_index[note_id]
        linked = []
        
        for link_title in note.links:
            # Find note by title
            for n in self.notes_index.values():
                if n.title.lower() == link_title.lower():
                    linked.append(n)
                    break
        
        return linked
    
    def get_backlinks(self, note_id: str) -> List[Note]:
        """Get notes that link to this note."""
        if note_id not in self.notes_index:
            return []
        
        note = self.notes_index[note_id]
        backlinks = []
        
        for other_note in self.notes_index.values():
            if note.title.lower() in [l.lower() for l in other_note.links]:
                backlinks.append(other_note)
        
        return backlinks
    
    def get_knowledge_graph(self) -> Dict:
        """
        Get the knowledge graph structure.
        
        Returns:
            Dict with nodes and edges for visualization
        """
        nodes = []
        edges = []
        
        for note_id, note in self.notes_index.items():
            # Skip highly sensitive notes
            if note.sensitivity in [SensitivityLevel.CONFIDENTIAL, SensitivityLevel.REDACTED]:
                continue
            
            nodes.append({
                "id": note_id,
                "title": note.title,
                "tags": note.tags,
                "sensitivity": note.sensitivity.value
            })
            
            # Add edges for links
            for link_title in note.links:
                for target_note in self.notes_index.values():
                    if target_note.title.lower() == link_title.lower():
                        edges.append({
                            "source": note_id,
                            "target": target_note.id
                        })
                        break
        
        return {"nodes": nodes, "edges": edges}
    
    def start_research_session(self, title: str, objective: str, 
                                keywords: List[str] = None) -> ResearchSession:
        """
        Start a new research session.
        
        Args:
            title: Session title
            objective: Research objective
            keywords: Initial keywords
            
        Returns:
            ResearchSession object
        """
        session_id = f"research_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        session = ResearchSession(
            session_id=session_id,
            title=title,
            objective=objective,
            keywords=keywords or []
        )
        
        self.research_sessions[session_id] = session
        
        # Create session note
        self.create_note(
            title=f"Research: {title}",
            content=f"""## Objective
{objective}

## Keywords
{', '.join(keywords or [])}

## Findings
(Add your findings here)

## Notes
(Add notes as you research)
""",
            tags=['research', 'session'] + (keywords or [])
        )
        
        print(f"[Obsidian] Started research session: {title}")
        return session
    
    def ai_summarize(self, note_id: str) -> str:
        """
        Use AI to summarize a note.
        
        Args:
            note_id: Note ID
            
        Returns:
            AI-generated summary
        """
        if not self.helper_ai:
            return "AI helper not available for summarization."
        
        if note_id not in self.notes_index:
            return "Note not found."
        
        note = self.notes_index[note_id]
        
        try:
            summary = self.helper_ai.summarize(note.content)
            return summary
        except Exception as e:
            return f"Summarization failed: {e}"
    
    def ai_suggest_links(self, note_id: str) -> List[str]:
        """
        Use AI to suggest related notes to link.
        
        Args:
            note_id: Note ID
            
        Returns:
            List of suggested note titles to link
        """
        if note_id not in self.notes_index:
            return []
        
        note = self.notes_index[note_id]
        suggestions = []
        
        # Simple keyword-based suggestions
        note_words = set(re.findall(r'\b\w+\b', note.content.lower()))
        
        for other_note in self.notes_index.values():
            if other_note.id == note_id:
                continue
            if other_note.title.lower() in [l.lower() for l in note.links]:
                continue  # Already linked
            
            other_words = set(re.findall(r'\b\w+\b', other_note.title.lower()))
            other_words.update(other_note.tags)
            
            # Check for word overlap
            overlap = note_words.intersection(other_words)
            if len(overlap) >= 2:
                suggestions.append(other_note.title)
        
        return suggestions[:5]
    
    def get_stats(self) -> Dict:
        """Get vault statistics."""
        sensitivity_counts = {}
        for level in SensitivityLevel:
            sensitivity_counts[level.value] = len([
                n for n in self.notes_index.values() 
                if n.sensitivity == level
            ])
        
        return {
            "total_notes": len(self.notes_index),
            "total_tags": len(self.tags_index),
            "research_sessions": len(self.research_sessions),
            "sensitivity": sensitivity_counts
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_TEMPLATES = {
    "research": """# {{title}}

Created: {{date}}

## Objective


## Background


## Methodology


## Findings


## Conclusions


## References

""",
    
    "daily": """# {{title}}

Date: {{date}}

## Today's Goals
- [ ] 

## Notes


## Accomplishments


## Tomorrow's Plans

""",
    
    "meeting": """# {{title}}

Date: {{date}}
Attendees: 

## Agenda
1. 

## Discussion Notes


## Action Items
- [ ] 

## Next Steps

""",
    
    "article": """# {{title}}

Created: {{date}}
Author: 
Status: Draft

## Abstract


## Introduction


## Main Content


## Conclusion


## References

""",
}


def create_default_templates(vault: ObsidianVault):
    """Create default note templates."""
    for name, content in DEFAULT_TEMPLATES.items():
        template_path = os.path.join(vault.templates_path, f"{name}.md")
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[Obsidian] Created template: {name}")


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_vault_instance = None

def get_vault(helper_ai=None) -> ObsidianVault:
    """Get the Obsidian vault singleton."""
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = ObsidianVault(helper_ai=helper_ai)
        create_default_templates(_vault_instance)
    return _vault_instance


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for Obsidian vault."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VA21 Obsidian Vault")
    parser.add_argument("action", choices=["create", "search", "list", "graph", "stats"],
                       help="Action to perform")
    parser.add_argument("--title", "-t", help="Note title")
    parser.add_argument("--content", "-c", help="Note content")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--tag", help="Tag to search")
    parser.add_argument("--template", help="Template to use")
    
    args = parser.parse_args()
    
    vault = get_vault()
    
    if args.action == "create":
        if not args.title:
            print("Error: --title required for create")
            return
        note = vault.create_note(
            title=args.title,
            content=args.content or "",
            template=args.template
        )
        print(f"Created: {note.path}")
        
    elif args.action == "search":
        query = args.query or args.tag or ""
        if args.tag:
            results = vault.search_by_tag(args.tag)
        else:
            results = vault.search(query)
        print(f"Found {len(results)} notes:")
        for note in results:
            print(f"  - {note.title} ({note.sensitivity.value})")
            
    elif args.action == "list":
        for note in vault.notes_index.values():
            print(f"  - {note.title} [{', '.join(note.tags)}]")
            
    elif args.action == "graph":
        graph = vault.get_knowledge_graph()
        print(f"Nodes: {len(graph['nodes'])}")
        print(f"Edges: {len(graph['edges'])}")
        
    elif args.action == "stats":
        stats = vault.get_stats()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
