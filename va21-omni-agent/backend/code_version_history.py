"""
VA21 Code Version History - Local Version Control for All Code Work

This module provides comprehensive version history for all code work,
independent of Git, with intelligent diff tracking and easy restoration.
"""

import os
import json
import hashlib
import difflib
import shutil
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import threading
import time


@dataclass
class CodeVersion:
    """Represents a version of a code file."""
    version_id: str
    file_path: str
    timestamp: datetime
    content_hash: str
    size_bytes: int
    lines_added: int
    lines_removed: int
    change_type: str  # 'create', 'modify', 'rename', 'delete'
    description: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class CodeProject:
    """Represents a code project with version history."""
    project_id: str
    name: str
    root_path: str
    created_at: datetime
    last_modified: datetime
    file_count: int
    total_versions: int


class CodeVersionHistory:
    """
    VA21 Code Version History - Comprehensive code versioning system.
    
    Features:
    - Automatic version tracking for all code changes
    - Line-by-line diff viewing
    - Point-in-time restoration
    - Project-based organization
    - Tag-based version marking
    - Intelligent change detection
    - Compression for storage efficiency
    - Search across version history
    - Integration with Helper AI
    """
    
    def __init__(self, history_dir: str = "data/code_history"):
        self.history_dir = history_dir
        self.versions_dir = os.path.join(history_dir, "versions")
        self.projects_file = os.path.join(history_dir, "projects.json")
        self.index_file = os.path.join(history_dir, "index.json")
        
        # In-memory caches
        self.projects: Dict[str, CodeProject] = {}
        self.file_index: Dict[str, List[str]] = {}  # file_path -> [version_ids]
        self.versions_cache: Dict[str, CodeVersion] = {}
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes
        self.max_versions_per_file = 100
        self.max_storage_mb = 1000
        
        # File watchers
        self.watched_paths: List[str] = []
        self.is_watching = False
        self._watch_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the version history system."""
        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)
        self._load_index()
        self._load_projects()
    
    def _load_index(self):
        """Load file index from disk."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.file_index = data.get('files', {})
            except Exception as e:
                print(f"[CodeHistory] Error loading index: {e}")
    
    def _save_index(self):
        """Save file index to disk."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump({'files': self.file_index}, f, indent=2)
        except Exception as e:
            print(f"[CodeHistory] Error saving index: {e}")
    
    def _load_projects(self):
        """Load projects from disk."""
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r') as f:
                    data = json.load(f)
                    for p in data.get('projects', []):
                        project = CodeProject(
                            project_id=p['project_id'],
                            name=p['name'],
                            root_path=p['root_path'],
                            created_at=datetime.fromisoformat(p['created_at']),
                            last_modified=datetime.fromisoformat(p['last_modified']),
                            file_count=p['file_count'],
                            total_versions=p['total_versions']
                        )
                        self.projects[project.project_id] = project
            except Exception as e:
                print(f"[CodeHistory] Error loading projects: {e}")
    
    def _save_projects(self):
        """Save projects to disk."""
        try:
            data = {
                'projects': [
                    {
                        'project_id': p.project_id,
                        'name': p.name,
                        'root_path': p.root_path,
                        'created_at': p.created_at.isoformat(),
                        'last_modified': p.last_modified.isoformat(),
                        'file_count': p.file_count,
                        'total_versions': p.total_versions
                    }
                    for p in self.projects.values()
                ]
            }
            with open(self.projects_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[CodeHistory] Error saving projects: {e}")
    
    def save_version(self, file_path: str, content: str, 
                     description: str = "", tags: List[str] = None,
                     change_type: str = "modify") -> Optional[CodeVersion]:
        """
        Save a new version of a file.
        
        Args:
            file_path: Path to the file
            content: File content
            description: Description of changes
            tags: Optional tags for this version
            change_type: Type of change (create, modify, rename, delete)
        
        Returns:
            CodeVersion object if successful
        """
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Calculate diff stats
        lines_added, lines_removed = 0, 0
        previous_version = self.get_latest_version(file_path)
        
        if previous_version:
            prev_content = self.get_version_content(previous_version.version_id)
            if prev_content:
                lines_added, lines_removed = self._calculate_diff_stats(prev_content, content)
                
                # Skip if content hasn't changed
                if content_hash == previous_version.content_hash:
                    return previous_version
        else:
            lines_added = len(content.split('\n'))
            change_type = "create"
        
        # Save content
        version_path = os.path.join(self.versions_dir, f"{version_id}.gz")
        try:
            with gzip.open(version_path, 'wt', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"[CodeHistory] Error saving version: {e}")
            return None
        
        # Create version object
        version = CodeVersion(
            version_id=version_id,
            file_path=file_path,
            timestamp=datetime.now(),
            content_hash=content_hash,
            size_bytes=len(content.encode()),
            lines_added=lines_added,
            lines_removed=lines_removed,
            change_type=change_type,
            description=description or f"Auto-saved at {datetime.now().strftime('%H:%M:%S')}",
            tags=tags or [],
            metadata={'original_path': file_path}
        )
        
        # Save version metadata
        meta_path = os.path.join(self.versions_dir, f"{version_id}.json")
        with open(meta_path, 'w') as f:
            json.dump({
                'version_id': version.version_id,
                'file_path': version.file_path,
                'timestamp': version.timestamp.isoformat(),
                'content_hash': version.content_hash,
                'size_bytes': version.size_bytes,
                'lines_added': version.lines_added,
                'lines_removed': version.lines_removed,
                'change_type': version.change_type,
                'description': version.description,
                'tags': version.tags,
                'metadata': version.metadata
            }, f, indent=2)
        
        # Update index
        if file_path not in self.file_index:
            self.file_index[file_path] = []
        self.file_index[file_path].append(version_id)
        
        # Enforce version limit
        self._enforce_version_limit(file_path)
        
        # Save index
        self._save_index()
        
        # Cache version
        self.versions_cache[version_id] = version
        
        print(f"[CodeHistory] Saved version {version_id} for {file_path} (+{lines_added}/-{lines_removed})")
        
        return version
    
    def _calculate_diff_stats(self, old_content: str, new_content: str) -> Tuple[int, int]:
        """Calculate lines added and removed."""
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
        
        added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        return added, removed
    
    def get_version(self, version_id: str) -> Optional[CodeVersion]:
        """Get a specific version."""
        if version_id in self.versions_cache:
            return self.versions_cache[version_id]
        
        meta_path = os.path.join(self.versions_dir, f"{version_id}.json")
        if not os.path.exists(meta_path):
            return None
        
        try:
            with open(meta_path, 'r') as f:
                data = json.load(f)
                version = CodeVersion(
                    version_id=data['version_id'],
                    file_path=data['file_path'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    content_hash=data['content_hash'],
                    size_bytes=data['size_bytes'],
                    lines_added=data['lines_added'],
                    lines_removed=data['lines_removed'],
                    change_type=data['change_type'],
                    description=data['description'],
                    tags=data.get('tags', []),
                    metadata=data.get('metadata', {})
                )
                self.versions_cache[version_id] = version
                return version
        except Exception as e:
            print(f"[CodeHistory] Error loading version {version_id}: {e}")
            return None
    
    def get_version_content(self, version_id: str) -> Optional[str]:
        """Get content of a specific version."""
        version_path = os.path.join(self.versions_dir, f"{version_id}.gz")
        
        if not os.path.exists(version_path):
            return None
        
        try:
            with gzip.open(version_path, 'rt', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[CodeHistory] Error reading version {version_id}: {e}")
            return None
    
    def get_latest_version(self, file_path: str) -> Optional[CodeVersion]:
        """Get the latest version of a file."""
        if file_path not in self.file_index or not self.file_index[file_path]:
            return None
        
        latest_id = self.file_index[file_path][-1]
        return self.get_version(latest_id)
    
    def get_file_history(self, file_path: str, limit: int = 50) -> List[CodeVersion]:
        """Get version history for a file."""
        if file_path not in self.file_index:
            return []
        
        version_ids = self.file_index[file_path][-limit:][::-1]  # Latest first
        versions = []
        
        for vid in version_ids:
            version = self.get_version(vid)
            if version:
                versions.append(version)
        
        return versions
    
    def get_diff(self, version_id_old: str, version_id_new: str, 
                 context_lines: int = 3) -> List[str]:
        """Get diff between two versions."""
        old_content = self.get_version_content(version_id_old) or ""
        new_content = self.get_version_content(version_id_new) or ""
        
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"version {version_id_old}",
            tofile=f"version {version_id_new}",
            lineterm='',
            n=context_lines
        ))
        
        return diff
    
    def restore_version(self, version_id: str, target_path: str = None) -> Dict:
        """
        Restore a file to a specific version.
        
        Args:
            version_id: Version to restore
            target_path: Optional different path to restore to
        
        Returns:
            Result dict with success status
        """
        version = self.get_version(version_id)
        if not version:
            return {'success': False, 'message': 'Version not found'}
        
        content = self.get_version_content(version_id)
        if content is None:
            return {'success': False, 'message': 'Version content not found'}
        
        target = target_path or version.file_path
        
        # Save current version before restoring
        if os.path.exists(target):
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                self.save_version(
                    target, current_content,
                    description=f"Pre-restore backup (before restoring to {version_id})",
                    tags=['pre-restore']
                )
            except Exception:
                pass
        
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'message': f'Restored to version {version_id}',
                'version': version
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def tag_version(self, version_id: str, tag: str) -> bool:
        """Add a tag to a version."""
        version = self.get_version(version_id)
        if not version:
            return False
        
        if tag not in version.tags:
            version.tags.append(tag)
            
            # Update metadata file
            meta_path = os.path.join(self.versions_dir, f"{version_id}.json")
            try:
                with open(meta_path, 'r') as f:
                    data = json.load(f)
                data['tags'] = version.tags
                with open(meta_path, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
            except Exception:
                return False
        
        return True
    
    def search_versions(self, query: str = None, file_pattern: str = None,
                       tag: str = None, date_from: datetime = None,
                       date_to: datetime = None, limit: int = 100) -> List[CodeVersion]:
        """Search across version history."""
        results = []
        
        for file_path, version_ids in self.file_index.items():
            if file_pattern and file_pattern not in file_path:
                continue
            
            for vid in version_ids[-limit:]:
                version = self.get_version(vid)
                if not version:
                    continue
                
                # Filter by date
                if date_from and version.timestamp < date_from:
                    continue
                if date_to and version.timestamp > date_to:
                    continue
                
                # Filter by tag
                if tag and tag not in version.tags:
                    continue
                
                # Filter by query in description
                if query and query.lower() not in version.description.lower():
                    content = self.get_version_content(vid)
                    if not content or query.lower() not in content.lower():
                        continue
                
                results.append(version)
        
        # Sort by timestamp, newest first
        results.sort(key=lambda v: v.timestamp, reverse=True)
        
        return results[:limit]
    
    def get_versions_by_tag(self, tag: str) -> List[CodeVersion]:
        """Get all versions with a specific tag."""
        return self.search_versions(tag=tag)
    
    def _enforce_version_limit(self, file_path: str):
        """Enforce maximum versions per file."""
        if file_path not in self.file_index:
            return
        
        versions = self.file_index[file_path]
        
        while len(versions) > self.max_versions_per_file:
            old_version_id = versions.pop(0)
            
            # Don't delete tagged versions
            version = self.get_version(old_version_id)
            if version and version.tags:
                continue
            
            # Delete old version files
            version_path = os.path.join(self.versions_dir, f"{old_version_id}.gz")
            meta_path = os.path.join(self.versions_dir, f"{old_version_id}.json")
            
            try:
                if os.path.exists(version_path):
                    os.remove(version_path)
                if os.path.exists(meta_path):
                    os.remove(meta_path)
            except Exception:
                pass
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a specific version."""
        version = self.get_version(version_id)
        if not version:
            return False
        
        # Remove from index
        if version.file_path in self.file_index:
            try:
                self.file_index[version.file_path].remove(version_id)
            except ValueError:
                pass
        
        # Delete files
        version_path = os.path.join(self.versions_dir, f"{version_id}.gz")
        meta_path = os.path.join(self.versions_dir, f"{version_id}.json")
        
        try:
            if os.path.exists(version_path):
                os.remove(version_path)
            if os.path.exists(meta_path):
                os.remove(meta_path)
            
            # Remove from cache
            if version_id in self.versions_cache:
                del self.versions_cache[version_id]
            
            self._save_index()
            return True
        except Exception as e:
            print(f"[CodeHistory] Error deleting version {version_id}: {e}")
            return False
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        total_size = 0
        total_versions = 0
        
        for file_path, version_ids in self.file_index.items():
            total_versions += len(version_ids)
            for vid in version_ids:
                version_path = os.path.join(self.versions_dir, f"{vid}.gz")
                if os.path.exists(version_path):
                    total_size += os.path.getsize(version_path)
        
        return {
            'total_files': len(self.file_index),
            'total_versions': total_versions,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_storage_mb': self.max_storage_mb,
            'max_versions_per_file': self.max_versions_per_file
        }
    
    def export_history_summary(self, file_path: str) -> Dict:
        """Export version history summary for a file."""
        versions = self.get_file_history(file_path, limit=20)
        
        return {
            'file_path': file_path,
            'total_versions': len(self.file_index.get(file_path, [])),
            'versions': [
                {
                    'version_id': v.version_id,
                    'timestamp': v.timestamp.isoformat(),
                    'description': v.description,
                    'lines_added': v.lines_added,
                    'lines_removed': v.lines_removed,
                    'change_type': v.change_type,
                    'tags': v.tags,
                    'size_bytes': v.size_bytes,
                    'age': self._format_age(v.timestamp)
                }
                for v in versions
            ]
        }
    
    def _format_age(self, timestamp: datetime) -> str:
        """Format age in human-readable form."""
        delta = datetime.now() - timestamp
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    
    def get_recent_changes(self, limit: int = 20) -> List[CodeVersion]:
        """Get most recent changes across all files."""
        all_versions = []
        
        for file_path, version_ids in self.file_index.items():
            for vid in version_ids[-5:]:  # Last 5 per file
                version = self.get_version(vid)
                if version:
                    all_versions.append(version)
        
        # Sort by timestamp, newest first
        all_versions.sort(key=lambda v: v.timestamp, reverse=True)
        
        return all_versions[:limit]
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict:
        """Compare two versions and return detailed diff info."""
        v1 = self.get_version(version_id_1)
        v2 = self.get_version(version_id_2)
        
        if not v1 or not v2:
            return {'error': 'Version not found'}
        
        content1 = self.get_version_content(version_id_1) or ""
        content2 = self.get_version_content(version_id_2) or ""
        
        diff_lines = self.get_diff(version_id_1, version_id_2)
        added, removed = self._calculate_diff_stats(content1, content2)
        
        return {
            'version_1': {
                'id': v1.version_id,
                'timestamp': v1.timestamp.isoformat(),
                'description': v1.description,
                'size': v1.size_bytes
            },
            'version_2': {
                'id': v2.version_id,
                'timestamp': v2.timestamp.isoformat(),
                'description': v2.description,
                'size': v2.size_bytes
            },
            'diff': diff_lines,
            'lines_added': added,
            'lines_removed': removed,
            'size_change': v2.size_bytes - v1.size_bytes
        }


# Singleton instance
_code_history: Optional[CodeVersionHistory] = None


def get_code_history() -> CodeVersionHistory:
    """Get the singleton Code Version History instance."""
    global _code_history
    if _code_history is None:
        _code_history = CodeVersionHistory()
    return _code_history
