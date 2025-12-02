"""
VA21 Code Snippets Manager - Intelligent Code Snippet Library

This module provides a comprehensive code snippets management system
with version history, tagging, and intelligent search.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re


@dataclass
class CodeSnippet:
    """Represents a code snippet."""
    snippet_id: str
    title: str
    description: str
    language: str
    code: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    version: int
    author: str
    is_favorite: bool = False
    usage_count: int = 0
    metadata: Dict = field(default_factory=dict)


@dataclass
class SnippetVersion:
    """Represents a version of a snippet."""
    version_id: str
    snippet_id: str
    version_number: int
    code: str
    change_description: str
    timestamp: datetime


class SnippetsManager:
    """
    VA21 Code Snippets Manager - Your personal code library.
    
    Features:
    - Organize snippets by language and tags
    - Version history for each snippet
    - Intelligent search with syntax awareness
    - Import/Export functionality
    - Template variables support
    - Syntax highlighting metadata
    - Usage tracking
    - Favorites system
    """
    
    # Supported languages with file extensions
    LANGUAGES = {
        'python': {'extensions': ['.py'], 'comment': '#'},
        'javascript': {'extensions': ['.js', '.jsx'], 'comment': '//'},
        'typescript': {'extensions': ['.ts', '.tsx'], 'comment': '//'},
        'java': {'extensions': ['.java'], 'comment': '//'},
        'c': {'extensions': ['.c', '.h'], 'comment': '//'},
        'cpp': {'extensions': ['.cpp', '.hpp', '.cc'], 'comment': '//'},
        'csharp': {'extensions': ['.cs'], 'comment': '//'},
        'go': {'extensions': ['.go'], 'comment': '//'},
        'rust': {'extensions': ['.rs'], 'comment': '//'},
        'ruby': {'extensions': ['.rb'], 'comment': '#'},
        'php': {'extensions': ['.php'], 'comment': '//'},
        'swift': {'extensions': ['.swift'], 'comment': '//'},
        'kotlin': {'extensions': ['.kt'], 'comment': '//'},
        'scala': {'extensions': ['.scala'], 'comment': '//'},
        'shell': {'extensions': ['.sh', '.bash'], 'comment': '#'},
        'powershell': {'extensions': ['.ps1'], 'comment': '#'},
        'sql': {'extensions': ['.sql'], 'comment': '--'},
        'html': {'extensions': ['.html', '.htm'], 'comment': '<!--'},
        'css': {'extensions': ['.css'], 'comment': '/*'},
        'scss': {'extensions': ['.scss', '.sass'], 'comment': '//'},
        'json': {'extensions': ['.json'], 'comment': None},
        'yaml': {'extensions': ['.yaml', '.yml'], 'comment': '#'},
        'xml': {'extensions': ['.xml'], 'comment': '<!--'},
        'markdown': {'extensions': ['.md'], 'comment': None},
        'dockerfile': {'extensions': ['Dockerfile'], 'comment': '#'},
        'makefile': {'extensions': ['Makefile'], 'comment': '#'},
        'lua': {'extensions': ['.lua'], 'comment': '--'},
        'r': {'extensions': ['.r', '.R'], 'comment': '#'},
        'perl': {'extensions': ['.pl'], 'comment': '#'},
        'haskell': {'extensions': ['.hs'], 'comment': '--'},
        'elixir': {'extensions': ['.ex', '.exs'], 'comment': '#'},
        'clojure': {'extensions': ['.clj'], 'comment': ';'},
    }
    
    def __init__(self, data_dir: str = "data/snippets"):
        self.data_dir = data_dir
        self.snippets_file = os.path.join(data_dir, "snippets.json")
        self.versions_dir = os.path.join(data_dir, "versions")
        
        self.snippets: Dict[str, CodeSnippet] = {}
        self.versions: Dict[str, List[SnippetVersion]] = {}
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the snippets manager."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)
        self._load_snippets()
    
    def _load_snippets(self):
        """Load snippets from disk."""
        if os.path.exists(self.snippets_file):
            try:
                with open(self.snippets_file, 'r') as f:
                    data = json.load(f)
                    for s in data.get('snippets', []):
                        snippet = CodeSnippet(
                            snippet_id=s['snippet_id'],
                            title=s['title'],
                            description=s['description'],
                            language=s['language'],
                            code=s['code'],
                            tags=s['tags'],
                            created_at=datetime.fromisoformat(s['created_at']),
                            updated_at=datetime.fromisoformat(s['updated_at']),
                            version=s['version'],
                            author=s.get('author', 'Anonymous'),
                            is_favorite=s.get('is_favorite', False),
                            usage_count=s.get('usage_count', 0),
                            metadata=s.get('metadata', {})
                        )
                        self.snippets[snippet.snippet_id] = snippet
            except Exception as e:
                print(f"[Snippets] Error loading snippets: {e}")
    
    def _save_snippets(self):
        """Save snippets to disk."""
        try:
            data = {
                'snippets': [
                    {
                        'snippet_id': s.snippet_id,
                        'title': s.title,
                        'description': s.description,
                        'language': s.language,
                        'code': s.code,
                        'tags': s.tags,
                        'created_at': s.created_at.isoformat(),
                        'updated_at': s.updated_at.isoformat(),
                        'version': s.version,
                        'author': s.author,
                        'is_favorite': s.is_favorite,
                        'usage_count': s.usage_count,
                        'metadata': s.metadata
                    }
                    for s in self.snippets.values()
                ]
            }
            with open(self.snippets_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Snippets] Error saving snippets: {e}")
    
    def create_snippet(self, title: str, code: str, language: str,
                      description: str = "", tags: List[str] = None,
                      author: str = "Anonymous") -> CodeSnippet:
        """Create a new code snippet."""
        snippet_id = hashlib.sha256(
            f"{title}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        snippet = CodeSnippet(
            snippet_id=snippet_id,
            title=title,
            description=description,
            language=language.lower(),
            code=code,
            tags=tags or [],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            author=author
        )
        
        self.snippets[snippet_id] = snippet
        
        # Save initial version
        self._save_version(snippet, "Initial version")
        
        self._save_snippets()
        
        return snippet
    
    def update_snippet(self, snippet_id: str, code: str = None,
                      title: str = None, description: str = None,
                      tags: List[str] = None, change_description: str = "") -> Optional[CodeSnippet]:
        """Update an existing snippet."""
        if snippet_id not in self.snippets:
            return None
        
        snippet = self.snippets[snippet_id]
        
        # Check if code changed
        code_changed = code is not None and code != snippet.code
        
        if code is not None:
            snippet.code = code
        if title is not None:
            snippet.title = title
        if description is not None:
            snippet.description = description
        if tags is not None:
            snippet.tags = tags
        
        snippet.updated_at = datetime.now()
        
        if code_changed:
            snippet.version += 1
            self._save_version(snippet, change_description or f"Updated to version {snippet.version}")
        
        self._save_snippets()
        
        return snippet
    
    def _save_version(self, snippet: CodeSnippet, change_description: str):
        """Save a version of a snippet."""
        version = SnippetVersion(
            version_id=f"{snippet.snippet_id}_v{snippet.version}",
            snippet_id=snippet.snippet_id,
            version_number=snippet.version,
            code=snippet.code,
            change_description=change_description,
            timestamp=datetime.now()
        )
        
        if snippet.snippet_id not in self.versions:
            self.versions[snippet.snippet_id] = []
        self.versions[snippet.snippet_id].append(version)
        
        # Save to file
        version_file = os.path.join(self.versions_dir, f"{snippet.snippet_id}.json")
        versions_data = [
            {
                'version_id': v.version_id,
                'version_number': v.version_number,
                'code': v.code,
                'change_description': v.change_description,
                'timestamp': v.timestamp.isoformat()
            }
            for v in self.versions[snippet.snippet_id]
        ]
        
        with open(version_file, 'w') as f:
            json.dump(versions_data, f, indent=2)
    
    def get_snippet(self, snippet_id: str) -> Optional[CodeSnippet]:
        """Get a snippet by ID."""
        return self.snippets.get(snippet_id)
    
    def get_snippet_versions(self, snippet_id: str) -> List[SnippetVersion]:
        """Get version history for a snippet."""
        if snippet_id in self.versions:
            return self.versions[snippet_id]
        
        # Try to load from file
        version_file = os.path.join(self.versions_dir, f"{snippet_id}.json")
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    data = json.load(f)
                    versions = [
                        SnippetVersion(
                            version_id=v['version_id'],
                            snippet_id=snippet_id,
                            version_number=v['version_number'],
                            code=v['code'],
                            change_description=v['change_description'],
                            timestamp=datetime.fromisoformat(v['timestamp'])
                        )
                        for v in data
                    ]
                    self.versions[snippet_id] = versions
                    return versions
            except Exception:
                pass
        
        return []
    
    def restore_version(self, snippet_id: str, version_number: int) -> Optional[CodeSnippet]:
        """Restore a snippet to a previous version."""
        versions = self.get_snippet_versions(snippet_id)
        
        for v in versions:
            if v.version_number == version_number:
                return self.update_snippet(
                    snippet_id,
                    code=v.code,
                    change_description=f"Restored to version {version_number}"
                )
        
        return None
    
    def delete_snippet(self, snippet_id: str) -> bool:
        """Delete a snippet."""
        if snippet_id not in self.snippets:
            return False
        
        del self.snippets[snippet_id]
        
        # Delete versions
        if snippet_id in self.versions:
            del self.versions[snippet_id]
        
        version_file = os.path.join(self.versions_dir, f"{snippet_id}.json")
        if os.path.exists(version_file):
            os.remove(version_file)
        
        self._save_snippets()
        
        return True
    
    def search_snippets(self, query: str = None, language: str = None,
                       tags: List[str] = None, favorites_only: bool = False) -> List[CodeSnippet]:
        """Search for snippets."""
        results = list(self.snippets.values())
        
        if language:
            results = [s for s in results if s.language == language.lower()]
        
        if favorites_only:
            results = [s for s in results if s.is_favorite]
        
        if tags:
            results = [s for s in results if any(t in s.tags for t in tags)]
        
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if query_lower in s.title.lower()
                or query_lower in s.description.lower()
                or query_lower in s.code.lower()
                or any(query_lower in tag.lower() for tag in s.tags)
            ]
        
        # Sort by usage count, then updated_at
        results.sort(key=lambda s: (s.usage_count, s.updated_at), reverse=True)
        
        return results
    
    def get_by_language(self, language: str) -> List[CodeSnippet]:
        """Get all snippets for a language."""
        return [s for s in self.snippets.values() if s.language == language.lower()]
    
    def get_by_tag(self, tag: str) -> List[CodeSnippet]:
        """Get all snippets with a tag."""
        return [s for s in self.snippets.values() if tag in s.tags]
    
    def get_favorites(self) -> List[CodeSnippet]:
        """Get favorite snippets."""
        return [s for s in self.snippets.values() if s.is_favorite]
    
    def toggle_favorite(self, snippet_id: str) -> bool:
        """Toggle favorite status."""
        if snippet_id not in self.snippets:
            return False
        
        self.snippets[snippet_id].is_favorite = not self.snippets[snippet_id].is_favorite
        self._save_snippets()
        
        return True
    
    def increment_usage(self, snippet_id: str):
        """Increment usage count when a snippet is used."""
        if snippet_id in self.snippets:
            self.snippets[snippet_id].usage_count += 1
            self._save_snippets()
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        tags = set()
        for snippet in self.snippets.values():
            tags.update(snippet.tags)
        return sorted(list(tags))
    
    def get_all_languages(self) -> List[str]:
        """Get all languages used."""
        languages = set()
        for snippet in self.snippets.values():
            languages.add(snippet.language)
        return sorted(list(languages))
    
    def get_stats(self) -> Dict:
        """Get snippet library statistics."""
        return {
            'total_snippets': len(self.snippets),
            'total_favorites': len(self.get_favorites()),
            'languages': len(self.get_all_languages()),
            'tags': len(self.get_all_tags()),
            'most_used': self._get_most_used(5),
            'recently_updated': self._get_recently_updated(5)
        }
    
    def _get_most_used(self, limit: int) -> List[Dict]:
        """Get most used snippets."""
        sorted_snippets = sorted(
            self.snippets.values(),
            key=lambda s: s.usage_count,
            reverse=True
        )[:limit]
        
        return [
            {'id': s.snippet_id, 'title': s.title, 'usage': s.usage_count}
            for s in sorted_snippets
        ]
    
    def _get_recently_updated(self, limit: int) -> List[Dict]:
        """Get recently updated snippets."""
        sorted_snippets = sorted(
            self.snippets.values(),
            key=lambda s: s.updated_at,
            reverse=True
        )[:limit]
        
        return [
            {'id': s.snippet_id, 'title': s.title, 'updated': s.updated_at.isoformat()}
            for s in sorted_snippets
        ]
    
    def export_snippet(self, snippet_id: str) -> Optional[Dict]:
        """Export a snippet for sharing."""
        snippet = self.get_snippet(snippet_id)
        if not snippet:
            return None
        
        return {
            'title': snippet.title,
            'description': snippet.description,
            'language': snippet.language,
            'code': snippet.code,
            'tags': snippet.tags,
            'author': snippet.author,
            'version': snippet.version,
            'exported_at': datetime.now().isoformat()
        }
    
    def import_snippet(self, data: Dict, author: str = None) -> Optional[CodeSnippet]:
        """Import a snippet from exported data."""
        try:
            return self.create_snippet(
                title=data['title'],
                code=data['code'],
                language=data['language'],
                description=data.get('description', ''),
                tags=data.get('tags', []),
                author=author or data.get('author', 'Imported')
            )
        except KeyError:
            return None
    
    def create_from_template(self, title: str, template_code: str,
                            language: str, variables: Dict[str, str]) -> CodeSnippet:
        """Create a snippet from a template with variable substitution."""
        # Replace {{variable}} with values
        code = template_code
        for var, value in variables.items():
            code = code.replace(f"{{{{{var}}}}}", value)
        
        return self.create_snippet(
            title=title,
            code=code,
            language=language,
            tags=['from-template']
        )
    
    def export_all(self) -> Dict:
        """Export all snippets."""
        return {
            'exported_at': datetime.now().isoformat(),
            'count': len(self.snippets),
            'snippets': [self.export_snippet(sid) for sid in self.snippets.keys()]
        }


# Singleton instance
_snippets_manager: Optional[SnippetsManager] = None


def get_snippets_manager() -> SnippetsManager:
    """Get the singleton Snippets Manager instance."""
    global _snippets_manager
    if _snippets_manager is None:
        _snippets_manager = SnippetsManager()
    return _snippets_manager
