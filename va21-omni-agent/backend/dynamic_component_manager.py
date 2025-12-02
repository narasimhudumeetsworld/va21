"""
VA21 Dynamic Component Manager - Unique ID System & Memory Optimization

This module provides a centralized system for managing component IDs,
preventing AI hallucinations through cross-validation, and optimizing
memory usage through dynamic service activation/deactivation.
"""

import uuid
import hashlib
import json
import os
import threading
import time
import gc
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict
import gzip


class ComponentState(Enum):
    """State of a component in the system."""
    ACTIVE = "active"           # Fully loaded and running
    DORMANT = "dormant"         # Registered but not in memory
    SUSPENDED = "suspended"     # Temporarily paused
    ARCHIVED = "archived"       # Compressed and stored


@dataclass
class ComponentID:
    """Unique identifier for any system component."""
    uid: str                    # Unique random ID (UUID4)
    short_id: str              # Short 8-char ID for display
    component_type: str        # Type: 'backup', 'code', 'snippet', 'service', etc.
    created_at: datetime
    version: int
    checksum: str              # SHA256 checksum for validation
    parent_id: Optional[str] = None  # Parent component if hierarchical
    
    def to_dict(self) -> Dict:
        return {
            'uid': self.uid,
            'short_id': self.short_id,
            'component_type': self.component_type,
            'created_at': self.created_at.isoformat(),
            'version': self.version,
            'checksum': self.checksum,
            'parent_id': self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ComponentID':
        return cls(
            uid=data['uid'],
            short_id=data['short_id'],
            component_type=data['component_type'],
            created_at=datetime.fromisoformat(data['created_at']),
            version=data['version'],
            checksum=data['checksum'],
            parent_id=data.get('parent_id')
        )


@dataclass
class ComponentMetadata:
    """Metadata for tracking component state and usage."""
    component_id: ComponentID
    state: ComponentState
    last_accessed: datetime
    access_count: int
    memory_bytes: int
    dependencies: List[str]    # List of dependent component UIDs
    tags: List[str]
    data_path: Optional[str]   # Path to stored data if archived


@dataclass
class VersionHistoryEntry:
    """Entry in version history with correlation ID."""
    entry_id: str              # Unique entry ID
    component_uid: str         # Related component UID
    version: int
    timestamp: datetime
    action: str                # 'create', 'modify', 'archive', 'delete'
    description: str
    checksum: str              # Checksum at this version
    size_bytes: int
    correlation_id: str        # Links related entries across components


class DynamicComponentManager:
    """
    Centralized manager for all VA21 components with:
    - Unique ID generation and tracking
    - Anti-hallucination validation
    - Dynamic memory management
    - Smart history compression and archival
    """
    
    # Memory thresholds
    MAX_MEMORY_PERCENT = 70        # Start deactivating at 70% memory
    TARGET_MEMORY_PERCENT = 50     # Target memory usage
    DORMANT_TIMEOUT_MINUTES = 30   # Deactivate after 30 min of inactivity
    
    # Archive thresholds
    ARCHIVE_AGE_DAYS = 30          # Archive versions older than 30 days
    MAX_ACTIVE_VERSIONS = 20       # Keep only 20 active versions per component
    
    def __init__(self, data_dir: str = "data/component_manager"):
        self.data_dir = data_dir
        self.registry_file = os.path.join(data_dir, "registry.json")
        self.history_file = os.path.join(data_dir, "history.json")
        self.archive_dir = os.path.join(data_dir, "archives")
        
        # Component registry
        self.components: Dict[str, ComponentMetadata] = {}
        self.id_index: Dict[str, str] = {}  # short_id -> uid mapping
        self.type_index: Dict[str, List[str]] = {}  # type -> [uids]
        
        # Version history
        self.history: OrderedDict[str, VersionHistoryEntry] = OrderedDict()
        self.correlation_map: Dict[str, List[str]] = {}  # correlation_id -> [entry_ids]
        
        # Active services
        self.active_services: Dict[str, Any] = {}
        self.service_factories: Dict[str, Callable] = {}
        
        # Management thread
        self.is_running = False
        self._stop_event = threading.Event()
        self._manager_thread: Optional[threading.Thread] = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the component manager."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        self._load_registry()
        self._load_history()
    
    def _load_registry(self):
        """Load component registry from disk."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for uid, comp_data in data.get('components', {}).items():
                        self.components[uid] = ComponentMetadata(
                            component_id=ComponentID.from_dict(comp_data['id']),
                            state=ComponentState(comp_data['state']),
                            last_accessed=datetime.fromisoformat(comp_data['last_accessed']),
                            access_count=comp_data['access_count'],
                            memory_bytes=comp_data['memory_bytes'],
                            dependencies=comp_data['dependencies'],
                            tags=comp_data['tags'],
                            data_path=comp_data.get('data_path')
                        )
                        # Update indexes
                        self.id_index[self.components[uid].component_id.short_id] = uid
                        comp_type = self.components[uid].component_id.component_type
                        if comp_type not in self.type_index:
                            self.type_index[comp_type] = []
                        self.type_index[comp_type].append(uid)
            except Exception as e:
                print(f"[ComponentManager] Error loading registry: {e}")
    
    def _save_registry(self):
        """Save component registry to disk."""
        try:
            data = {
                'components': {
                    uid: {
                        'id': comp.component_id.to_dict(),
                        'state': comp.state.value,
                        'last_accessed': comp.last_accessed.isoformat(),
                        'access_count': comp.access_count,
                        'memory_bytes': comp.memory_bytes,
                        'dependencies': comp.dependencies,
                        'tags': comp.tags,
                        'data_path': comp.data_path
                    }
                    for uid, comp in self.components.items()
                },
                'saved_at': datetime.now().isoformat()
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ComponentManager] Error saving registry: {e}")
    
    def _load_history(self):
        """Load version history from disk."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get('entries', []):
                        entry = VersionHistoryEntry(
                            entry_id=entry_data['entry_id'],
                            component_uid=entry_data['component_uid'],
                            version=entry_data['version'],
                            timestamp=datetime.fromisoformat(entry_data['timestamp']),
                            action=entry_data['action'],
                            description=entry_data['description'],
                            checksum=entry_data['checksum'],
                            size_bytes=entry_data['size_bytes'],
                            correlation_id=entry_data['correlation_id']
                        )
                        self.history[entry.entry_id] = entry
                        
                        # Update correlation map
                        if entry.correlation_id not in self.correlation_map:
                            self.correlation_map[entry.correlation_id] = []
                        self.correlation_map[entry.correlation_id].append(entry.entry_id)
            except Exception as e:
                print(f"[ComponentManager] Error loading history: {e}")
    
    def _save_history(self):
        """Save version history to disk."""
        try:
            data = {
                'entries': [
                    {
                        'entry_id': e.entry_id,
                        'component_uid': e.component_uid,
                        'version': e.version,
                        'timestamp': e.timestamp.isoformat(),
                        'action': e.action,
                        'description': e.description,
                        'checksum': e.checksum,
                        'size_bytes': e.size_bytes,
                        'correlation_id': e.correlation_id
                    }
                    for e in self.history.values()
                ],
                'saved_at': datetime.now().isoformat()
            }
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ComponentManager] Error saving history: {e}")
    
    # ==================== ID GENERATION ====================
    
    def generate_id(self, component_type: str, content: Any = None,
                   parent_id: str = None) -> ComponentID:
        """
        Generate a unique ID for a component.
        
        Args:
            component_type: Type of component
            content: Optional content for checksum calculation
            parent_id: Optional parent component UID
        
        Returns:
            ComponentID with unique identifiers
        """
        uid = str(uuid.uuid4())
        short_id = uid[:8].upper()
        
        # Generate checksum
        checksum_data = f"{uid}{component_type}{datetime.now().isoformat()}"
        if content:
            checksum_data += str(content)[:1000]  # Limit content for checksum
        checksum = hashlib.sha256(checksum_data.encode()).hexdigest()[:16]
        
        component_id = ComponentID(
            uid=uid,
            short_id=short_id,
            component_type=component_type,
            created_at=datetime.now(),
            version=1,
            checksum=checksum,
            parent_id=parent_id
        )
        
        return component_id
    
    def register_component(self, component_id: ComponentID, 
                          memory_bytes: int = 0,
                          dependencies: List[str] = None,
                          tags: List[str] = None) -> str:
        """
        Register a new component in the system.
        
        Returns:
            Component UID
        """
        metadata = ComponentMetadata(
            component_id=component_id,
            state=ComponentState.ACTIVE,
            last_accessed=datetime.now(),
            access_count=1,
            memory_bytes=memory_bytes,
            dependencies=dependencies or [],
            tags=tags or [],
            data_path=None
        )
        
        self.components[component_id.uid] = metadata
        self.id_index[component_id.short_id] = component_id.uid
        
        if component_id.component_type not in self.type_index:
            self.type_index[component_id.component_type] = []
        self.type_index[component_id.component_type].append(component_id.uid)
        
        # Add to history
        self._add_history_entry(
            component_uid=component_id.uid,
            version=component_id.version,
            action='create',
            description=f"Created {component_id.component_type} component",
            checksum=component_id.checksum,
            size_bytes=memory_bytes
        )
        
        self._save_registry()
        
        return component_id.uid
    
    # ==================== VALIDATION (Anti-Hallucination) ====================
    
    def validate_component(self, uid: str, expected_checksum: str = None,
                          expected_version: int = None) -> Dict:
        """
        Validate a component exists and matches expected values.
        This prevents AI hallucinations by cross-checking IDs and versions.
        
        Returns:
            Validation result with details
        """
        result = {
            'valid': False,
            'exists': False,
            'checksum_match': None,
            'version_match': None,
            'details': {}
        }
        
        if uid not in self.components:
            # Try short_id
            if uid in self.id_index:
                uid = self.id_index[uid]
            else:
                result['details']['error'] = 'Component not found'
                return result
        
        component = self.components[uid]
        result['exists'] = True
        result['details']['component_type'] = component.component_id.component_type
        result['details']['state'] = component.state.value
        result['details']['version'] = component.component_id.version
        result['details']['checksum'] = component.component_id.checksum
        
        # Validate checksum
        if expected_checksum:
            result['checksum_match'] = (
                component.component_id.checksum == expected_checksum
            )
        
        # Validate version
        if expected_version:
            result['version_match'] = (
                component.component_id.version == expected_version
            )
        
        # Component is valid if it exists and all checks pass
        result['valid'] = result['exists']
        if result['checksum_match'] is not None and not result['checksum_match']:
            result['valid'] = False
        if result['version_match'] is not None and not result['version_match']:
            result['valid'] = False
        
        return result
    
    def cross_validate_history(self, component_uid: str, 
                              version: int) -> Dict:
        """
        Cross-validate component with its history.
        Double-checks that component state matches recorded history.
        """
        result = {
            'valid': False,
            'component_exists': False,
            'history_exists': False,
            'matches': False,
            'discrepancies': []
        }
        
        # Check component exists
        if component_uid not in self.components:
            return result
        
        result['component_exists'] = True
        component = self.components[component_uid]
        
        # Find matching history entry
        matching_entries = [
            e for e in self.history.values()
            if e.component_uid == component_uid and e.version == version
        ]
        
        if not matching_entries:
            result['discrepancies'].append(
                f"No history entry for version {version}"
            )
            return result
        
        result['history_exists'] = True
        latest_entry = max(matching_entries, key=lambda e: e.timestamp)
        
        # Check for discrepancies
        if latest_entry.checksum != component.component_id.checksum:
            result['discrepancies'].append(
                f"Checksum mismatch: history={latest_entry.checksum}, "
                f"component={component.component_id.checksum}"
            )
        
        result['matches'] = len(result['discrepancies']) == 0
        result['valid'] = result['matches']
        
        return result
    
    def verify_correlation(self, correlation_id: str) -> Dict:
        """
        Verify all entries in a correlation chain are consistent.
        Used to validate related operations across components.
        """
        if correlation_id not in self.correlation_map:
            return {'valid': False, 'error': 'Correlation ID not found'}
        
        entry_ids = self.correlation_map[correlation_id]
        entries = [self.history[eid] for eid in entry_ids if eid in self.history]
        
        return {
            'valid': True,
            'correlation_id': correlation_id,
            'entry_count': len(entries),
            'entries': [
                {
                    'entry_id': e.entry_id,
                    'component_uid': e.component_uid,
                    'action': e.action,
                    'timestamp': e.timestamp.isoformat()
                }
                for e in entries
            ]
        }
    
    # ==================== DYNAMIC MEMORY MANAGEMENT ====================
    
    def start_memory_manager(self):
        """Start the background memory management thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        self._manager_thread = threading.Thread(
            target=self._memory_management_loop,
            daemon=True
        )
        self._manager_thread.start()
        print("[ComponentManager] Memory manager started")
    
    def stop_memory_manager(self):
        """Stop the memory management thread."""
        self.is_running = False
        self._stop_event.set()
        if self._manager_thread:
            self._manager_thread.join(timeout=5.0)
        print("[ComponentManager] Memory manager stopped")
    
    def _memory_management_loop(self):
        """Background loop for memory management."""
        while self.is_running:
            try:
                self._check_memory_usage()
                self._deactivate_dormant_components()
                self._archive_old_versions()
                
                # Wait 60 seconds or until stop
                if self._stop_event.wait(timeout=60):
                    break
                    
            except Exception as e:
                print(f"[ComponentManager] Error in memory loop: {e}")
                if self._stop_event.wait(timeout=60):
                    break
    
    def _check_memory_usage(self):
        """Check and manage system memory usage."""
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent > self.MAX_MEMORY_PERCENT:
            print(f"[ComponentManager] High memory usage: {memory_percent}%")
            self._free_memory(target_percent=self.TARGET_MEMORY_PERCENT)
    
    def _free_memory(self, target_percent: float):
        """Free memory by deactivating components."""
        # Sort components by last access time
        active_components = [
            (uid, comp) for uid, comp in self.components.items()
            if comp.state == ComponentState.ACTIVE
        ]
        active_components.sort(key=lambda x: x[1].last_accessed)
        
        for uid, comp in active_components:
            # Skip essential services
            if 'essential' in comp.tags:
                continue
            
            self.deactivate_component(uid)
            
            # Check if we've freed enough
            memory = psutil.virtual_memory()
            if memory.percent <= target_percent:
                break
        
        # Force garbage collection
        gc.collect()
    
    def _deactivate_dormant_components(self):
        """Deactivate components that haven't been used recently."""
        now = datetime.now()
        dormant_threshold = timedelta(minutes=self.DORMANT_TIMEOUT_MINUTES)
        
        for uid, comp in list(self.components.items()):
            if comp.state != ComponentState.ACTIVE:
                continue
            
            if 'essential' in comp.tags:
                continue
            
            if now - comp.last_accessed > dormant_threshold:
                self.deactivate_component(uid)
    
    def deactivate_component(self, uid: str) -> bool:
        """Deactivate a component to free memory."""
        if uid not in self.components:
            return False
        
        comp = self.components[uid]
        
        if comp.state != ComponentState.ACTIVE:
            return True  # Already inactive
        
        # Remove from active services if present
        if uid in self.active_services:
            del self.active_services[uid]
        
        comp.state = ComponentState.DORMANT
        
        # Add history entry
        self._add_history_entry(
            component_uid=uid,
            version=comp.component_id.version,
            action='deactivate',
            description='Component deactivated for memory optimization',
            checksum=comp.component_id.checksum,
            size_bytes=0
        )
        
        self._save_registry()
        print(f"[ComponentManager] Deactivated component: {comp.component_id.short_id}")
        
        return True
    
    def activate_component(self, uid: str) -> bool:
        """Activate a dormant component."""
        if uid not in self.components:
            # Try short_id
            if uid in self.id_index:
                uid = self.id_index[uid]
            else:
                return False
        
        comp = self.components[uid]
        
        if comp.state == ComponentState.ACTIVE:
            return True  # Already active
        
        if comp.state == ComponentState.ARCHIVED:
            # Need to unarchive first
            self._unarchive_component(uid)
        
        comp.state = ComponentState.ACTIVE
        comp.last_accessed = datetime.now()
        comp.access_count += 1
        
        self._save_registry()
        print(f"[ComponentManager] Activated component: {comp.component_id.short_id}")
        
        return True
    
    # ==================== HISTORY & ARCHIVE MANAGEMENT ====================
    
    def _add_history_entry(self, component_uid: str, version: int,
                          action: str, description: str,
                          checksum: str, size_bytes: int,
                          correlation_id: str = None) -> str:
        """Add an entry to the version history."""
        entry_id = str(uuid.uuid4())[:12]
        
        if not correlation_id:
            correlation_id = str(uuid.uuid4())[:8]
        
        entry = VersionHistoryEntry(
            entry_id=entry_id,
            component_uid=component_uid,
            version=version,
            timestamp=datetime.now(),
            action=action,
            description=description,
            checksum=checksum,
            size_bytes=size_bytes,
            correlation_id=correlation_id
        )
        
        self.history[entry_id] = entry
        
        if correlation_id not in self.correlation_map:
            self.correlation_map[correlation_id] = []
        self.correlation_map[correlation_id].append(entry_id)
        
        self._save_history()
        
        return entry_id
    
    def _archive_old_versions(self):
        """Archive old version history entries."""
        now = datetime.now()
        archive_threshold = timedelta(days=self.ARCHIVE_AGE_DAYS)
        
        # Group entries by component
        component_entries: Dict[str, List[VersionHistoryEntry]] = {}
        for entry in self.history.values():
            if entry.component_uid not in component_entries:
                component_entries[entry.component_uid] = []
            component_entries[entry.component_uid].append(entry)
        
        archived_count = 0
        
        for component_uid, entries in component_entries.items():
            # Sort by timestamp (newest first)
            entries.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Keep only MAX_ACTIVE_VERSIONS recent entries
            if len(entries) > self.MAX_ACTIVE_VERSIONS:
                to_archive = entries[self.MAX_ACTIVE_VERSIONS:]
                
                for entry in to_archive:
                    if now - entry.timestamp > archive_threshold:
                        self._archive_entry(entry)
                        archived_count += 1
        
        if archived_count > 0:
            print(f"[ComponentManager] Archived {archived_count} old entries")
    
    def _archive_entry(self, entry: VersionHistoryEntry):
        """Archive a history entry to compressed storage."""
        archive_file = os.path.join(
            self.archive_dir,
            f"{entry.component_uid}_{entry.entry_id}.json.gz"
        )
        
        try:
            with gzip.open(archive_file, 'wt', encoding='utf-8') as f:
                json.dump({
                    'entry_id': entry.entry_id,
                    'component_uid': entry.component_uid,
                    'version': entry.version,
                    'timestamp': entry.timestamp.isoformat(),
                    'action': entry.action,
                    'description': entry.description,
                    'checksum': entry.checksum,
                    'size_bytes': entry.size_bytes,
                    'correlation_id': entry.correlation_id,
                    'archived_at': datetime.now().isoformat()
                }, f)
            
            # Remove from active history
            if entry.entry_id in self.history:
                del self.history[entry.entry_id]
            
        except Exception as e:
            print(f"[ComponentManager] Error archiving entry: {e}")
    
    def _unarchive_component(self, uid: str):
        """Unarchive a component's data."""
        if uid not in self.components:
            return
        
        comp = self.components[uid]
        
        if comp.data_path and os.path.exists(comp.data_path):
            try:
                with gzip.open(comp.data_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
                    # Restore component data (implementation depends on type)
                    print(f"[ComponentManager] Unarchived: {comp.component_id.short_id}")
            except Exception as e:
                print(f"[ComponentManager] Error unarchiving: {e}")
    
    def delete_old_versions(self, component_uid: str = None,
                           older_than_days: int = None,
                           keep_count: int = 5) -> Dict:
        """
        Delete old versions per user request.
        
        Args:
            component_uid: Specific component or None for all
            older_than_days: Delete versions older than this
            keep_count: Always keep at least this many versions
        
        Returns:
            Summary of deleted entries
        """
        deleted = []
        now = datetime.now()
        
        # Get entries to consider
        entries = list(self.history.values())
        if component_uid:
            entries = [e for e in entries if e.component_uid == component_uid]
        
        # Group by component
        by_component: Dict[str, List[VersionHistoryEntry]] = {}
        for entry in entries:
            if entry.component_uid not in by_component:
                by_component[entry.component_uid] = []
            by_component[entry.component_uid].append(entry)
        
        for comp_uid, comp_entries in by_component.items():
            # Sort by timestamp (newest first)
            comp_entries.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Keep at least keep_count
            deletable = comp_entries[keep_count:]
            
            for entry in deletable:
                if older_than_days:
                    if (now - entry.timestamp).days < older_than_days:
                        continue
                
                # Delete from history
                if entry.entry_id in self.history:
                    del self.history[entry.entry_id]
                    deleted.append({
                        'entry_id': entry.entry_id,
                        'component_uid': entry.component_uid,
                        'version': entry.version,
                        'timestamp': entry.timestamp.isoformat()
                    })
        
        self._save_history()
        
        return {
            'deleted_count': len(deleted),
            'deleted': deleted
        }
    
    # ==================== SERVICE MANAGEMENT ====================
    
    def register_service_factory(self, service_type: str, 
                                factory: Callable) -> None:
        """Register a factory function for creating services on demand."""
        self.service_factories[service_type] = factory
    
    def get_service(self, service_type: str) -> Optional[Any]:
        """
        Get a service, activating it if dormant.
        Services are created on-demand to save memory.
        """
        # Check if already active
        for uid, comp in self.components.items():
            if (comp.component_id.component_type == service_type and 
                comp.state == ComponentState.ACTIVE):
                comp.last_accessed = datetime.now()
                comp.access_count += 1
                return self.active_services.get(uid)
        
        # Try to create the service
        if service_type in self.service_factories:
            service = self.service_factories[service_type]()
            
            # Register as component
            component_id = self.generate_id(service_type)
            uid = self.register_component(
                component_id,
                tags=['service'],
                memory_bytes=1024  # Estimate
            )
            
            self.active_services[uid] = service
            return service
        
        return None
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict:
        """Get component manager statistics."""
        active_count = sum(
            1 for c in self.components.values() 
            if c.state == ComponentState.ACTIVE
        )
        dormant_count = sum(
            1 for c in self.components.values() 
            if c.state == ComponentState.DORMANT
        )
        archived_count = sum(
            1 for c in self.components.values() 
            if c.state == ComponentState.ARCHIVED
        )
        
        total_memory = sum(
            c.memory_bytes for c in self.components.values()
            if c.state == ComponentState.ACTIVE
        )
        
        memory = psutil.virtual_memory()
        
        return {
            'total_components': len(self.components),
            'active_components': active_count,
            'dormant_components': dormant_count,
            'archived_components': archived_count,
            'total_history_entries': len(self.history),
            'active_memory_bytes': total_memory,
            'active_memory_mb': round(total_memory / (1024 * 1024), 2),
            'system_memory_percent': memory.percent,
            'component_types': list(self.type_index.keys()),
            'is_running': self.is_running
        }


# Singleton instance
_component_manager: Optional[DynamicComponentManager] = None


def get_component_manager() -> DynamicComponentManager:
    """Get the singleton Component Manager instance."""
    global _component_manager
    if _component_manager is None:
        _component_manager = DynamicComponentManager()
    return _component_manager
