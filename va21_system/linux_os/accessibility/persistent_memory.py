#!/usr/bin/env python3
"""
VA21 OS - Persistent Memory System
===================================

Om Vinayaka - The remover of obstacles.

This module ensures VA21 OS NEVER FORGETS:
- Auto backup before shutdown
- Periodic backups every 30 minutes
- Version history of all backups
- LangChain + Obsidian mind maps for persistent storage
- Survives shutdown, reboot, and even power loss

The OS remembers:
- All learned command patterns
- User preferences
- App usage patterns
- Conversation history
- Knowledge base content
- Agent task history

Storage Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                    PERSISTENT MEMORY SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────┤
│  📁 ~/.va21/                                                            │
│  ├── knowledge_base/          # Obsidian-style vault                    │
│  │   ├── mind_maps/           # Visual knowledge graphs                 │
│  │   ├── learned_patterns/    # Command patterns                        │
│  │   ├── user_preferences/    # User settings & habits                  │
│  │   └── app_interfaces/      # Zork interfaces for apps                │
│  ├── backups/                 # Version history                         │
│  │   ├── auto_YYYYMMDD_HHMMSS.tar.gz                                   │
│  │   └── shutdown_YYYYMMDD_HHMMSS.tar.gz                               │
│  ├── state/                   # Current system state                    │
│  │   ├── learning_state.json                                           │
│  │   ├── context_state.json                                            │
│  │   └── agent_state.json                                              │
│  └── config/                  # Configuration files                     │
└─────────────────────────────────────────────────────────────────────────┘

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav
"""

import os
import sys
import json
import shutil
import tarfile
import atexit
import signal
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Base paths
VA21_HOME = os.path.expanduser("~/.va21")
KNOWLEDGE_BASE_PATH = os.path.join(VA21_HOME, "knowledge_base")
BACKUPS_PATH = os.path.join(VA21_HOME, "backups")
STATE_PATH = os.path.join(VA21_HOME, "state")
CONFIG_PATH = os.path.join(VA21_HOME, "config")

# Backup settings (base values - adjusted dynamically based on load)
BACKUP_INTERVAL_MINUTES = 30  # Default: Backup every 30 minutes
MIN_BACKUP_INTERVAL_MINUTES = 5  # Minimum: 5 minutes during high load
MAX_BACKUP_INTERVAL_MINUTES = 60  # Maximum: 1 hour during low load
MAX_BACKUPS_TO_KEEP = 96  # Keep 48 hours of backups
BACKUP_ON_SHUTDOWN = True

# Dynamic backup thresholds
HIGH_ACTIVITY_THRESHOLD = 50  # Interactions per interval = high activity
MEDIUM_ACTIVITY_THRESHOLD = 20  # Interactions per interval = medium activity
CRITICAL_KNOWLEDGE_THRESHOLD = 10  # New patterns = critical backup needed

# State files
LEARNING_STATE_FILE = os.path.join(STATE_PATH, "learning_state.json")
CONTEXT_STATE_FILE = os.path.join(STATE_PATH, "context_state.json")
AGENT_STATE_FILE = os.path.join(STATE_PATH, "agent_state.json")
MEMORY_STATE_FILE = os.path.join(STATE_PATH, "memory_state.json")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BackupInfo:
    """Information about a backup."""
    backup_id: str
    timestamp: str
    backup_type: str  # 'auto', 'shutdown', 'manual', 'dynamic'
    path: str
    size_bytes: int
    components: List[str]
    activity_level: str = "normal"  # 'low', 'normal', 'high', 'critical'


@dataclass
class MemoryState:
    """Current state of persistent memory."""
    last_backup: Optional[str] = None
    last_restore: Optional[str] = None
    total_backups: int = 0
    total_learned_patterns: int = 0
    total_preferences: int = 0
    uptime_seconds: float = 0
    startup_time: str = field(default_factory=lambda: datetime.now().isoformat())
    # Activity tracking for dynamic backups
    interactions_since_backup: int = 0
    patterns_since_backup: int = 0
    current_backup_interval: int = BACKUP_INTERVAL_MINUTES
    activity_level: str = "normal"


@dataclass
class ActivityMetrics:
    """Tracks system activity for dynamic backup decisions."""
    interactions_count: int = 0
    patterns_learned: int = 0
    preferences_changed: int = 0
    agent_tasks_completed: int = 0
    errors_encountered: int = 0
    last_reset: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# PERSISTENT MEMORY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class PersistentMemoryManager:
    """
    Manages persistent memory for VA21 OS.
    
    Ensures the OS NEVER FORGETS:
    - Auto backup before shutdown
    - Dynamic backups based on system load (more frequent during high activity)
    - Periodic backups every 30 minutes (adjusted dynamically)
    - Version history
    - LangChain + Obsidian integration
    - Survives power loss
    
    Dynamic Backup Strategy:
    - Low activity: Backup every 60 minutes
    - Normal activity: Backup every 30 minutes
    - High activity: Backup every 15 minutes
    - Critical (many new patterns): Backup every 5 minutes
    
    Om Vinayaka - May your knowledge persist eternally.
    """
    
    VERSION = "1.1.0"  # Updated for dynamic backups
    
    def __init__(self):
        # Create directory structure
        self._create_directories()
        
        # Memory state
        self.state = self._load_state()
        
        # Activity tracking for dynamic backups
        self.activity = ActivityMetrics()
        self._activity_lock = threading.Lock()
        
        # Backup thread
        self._backup_thread: Optional[threading.Thread] = None
        self._stop_backup_thread = threading.Event()
        
        # Dynamic backup interval (adjusted based on activity)
        self._current_interval_minutes = BACKUP_INTERVAL_MINUTES
        
        # Track if we've registered shutdown handlers
        self._shutdown_handlers_registered = False
        
        print(f"[PersistentMemory] Initialized v{self.VERSION}")
        print(f"[PersistentMemory] Knowledge base: {KNOWLEDGE_BASE_PATH}")
        print(f"[PersistentMemory] Backups: {BACKUPS_PATH}")
        print(f"[PersistentMemory] Dynamic backup: ENABLED (adjusts to activity)")
    
    def _create_directories(self):
        """Create all necessary directories."""
        directories = [
            VA21_HOME,
            KNOWLEDGE_BASE_PATH,
            os.path.join(KNOWLEDGE_BASE_PATH, "mind_maps"),
            os.path.join(KNOWLEDGE_BASE_PATH, "learned_patterns"),
            os.path.join(KNOWLEDGE_BASE_PATH, "user_preferences"),
            os.path.join(KNOWLEDGE_BASE_PATH, "app_interfaces"),
            os.path.join(KNOWLEDGE_BASE_PATH, "conversation_history"),
            os.path.join(KNOWLEDGE_BASE_PATH, "agent_history"),
            BACKUPS_PATH,
            STATE_PATH,
            CONFIG_PATH,
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _load_state(self) -> MemoryState:
        """Load memory state from disk."""
        if os.path.exists(MEMORY_STATE_FILE):
            try:
                with open(MEMORY_STATE_FILE, 'r') as f:
                    data = json.load(f)
                # Handle missing fields from older versions
                valid_fields = {f.name for f in MemoryState.__dataclass_fields__.values()}
                filtered_data = {k: v for k, v in data.items() if k in valid_fields}
                return MemoryState(**filtered_data)
            except Exception as e:
                print(f"[PersistentMemory] Warning: Could not load state: {e}")
        
        return MemoryState()
    
    def _save_state(self):
        """Save memory state to disk."""
        try:
            self.state.uptime_seconds = (
                datetime.now() - datetime.fromisoformat(self.state.startup_time)
            ).total_seconds()
            
            with open(MEMORY_STATE_FILE, 'w') as f:
                json.dump(asdict(self.state), f, indent=2)
        except Exception as e:
            print(f"[PersistentMemory] Warning: Could not save state: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BACKUP SYSTEM
    # ═══════════════════════════════════════════════════════════════════════════
    
    def start_auto_backup(self):
        """Start the automatic backup thread with dynamic intervals."""
        if self._backup_thread and self._backup_thread.is_alive():
            return
        
        self._stop_backup_thread.clear()
        self._backup_thread = threading.Thread(
            target=self._backup_loop,
            daemon=True,
            name="VA21-DynamicBackup"
        )
        self._backup_thread.start()
        
        print(f"[PersistentMemory] Dynamic backup started (base: {BACKUP_INTERVAL_MINUTES} min, adjusts to activity)")
    
    def stop_auto_backup(self):
        """Stop the automatic backup thread."""
        self._stop_backup_thread.set()
        if self._backup_thread:
            self._backup_thread.join(timeout=5)
        print("[PersistentMemory] Auto backup stopped")
    
    def _backup_loop(self):
        """
        Background thread that performs dynamic backups.
        
        Adjusts backup frequency based on system activity:
        - Low activity: Every 60 minutes
        - Normal activity: Every 30 minutes  
        - High activity: Every 15 minutes
        - Critical (many new patterns): Every 5 minutes
        """
        while not self._stop_backup_thread.is_set():
            # Calculate dynamic interval based on activity
            self._update_backup_interval()
            interval_seconds = self._current_interval_minutes * 60
            
            # Wait for interval (or until stopped)
            if self._stop_backup_thread.wait(timeout=interval_seconds):
                break
            
            try:
                # Determine backup type based on activity
                activity_level = self._get_activity_level()
                backup_type = 'dynamic' if activity_level in ['high', 'critical'] else 'auto'
                
                self.create_backup(backup_type=backup_type)
                
                # Reset activity counters after backup
                self._reset_activity_counters()
                
            except Exception as e:
                print(f"[PersistentMemory] Auto backup failed: {e}")
    
    def _update_backup_interval(self):
        """Update backup interval based on current activity level."""
        activity_level = self._get_activity_level()
        
        if activity_level == 'critical':
            self._current_interval_minutes = MIN_BACKUP_INTERVAL_MINUTES
        elif activity_level == 'high':
            self._current_interval_minutes = 15
        elif activity_level == 'low':
            self._current_interval_minutes = MAX_BACKUP_INTERVAL_MINUTES
        else:  # normal
            self._current_interval_minutes = BACKUP_INTERVAL_MINUTES
        
        # Update state
        self.state.current_backup_interval = self._current_interval_minutes
        self.state.activity_level = activity_level
    
    def _get_activity_level(self) -> str:
        """
        Determine current activity level.
        
        Returns:
            'low', 'normal', 'high', or 'critical'
        """
        with self._activity_lock:
            interactions = self.activity.interactions_count
            patterns = self.activity.patterns_learned
        
        # Critical: Many new patterns learned (knowledge at risk)
        if patterns >= CRITICAL_KNOWLEDGE_THRESHOLD:
            return 'critical'
        
        # High: Lots of interactions
        if interactions >= HIGH_ACTIVITY_THRESHOLD:
            return 'high'
        
        # Medium: Moderate activity
        if interactions >= MEDIUM_ACTIVITY_THRESHOLD:
            return 'normal'
        
        # Low: Little activity
        return 'low'
    
    def _reset_activity_counters(self):
        """Reset activity counters after a backup."""
        with self._activity_lock:
            self.activity.interactions_count = 0
            self.activity.patterns_learned = 0
            self.activity.preferences_changed = 0
            self.activity.agent_tasks_completed = 0
            self.activity.last_reset = datetime.now().isoformat()
        
        self.state.interactions_since_backup = 0
        self.state.patterns_since_backup = 0
    
    def record_activity(self, activity_type: str):
        """
        Record an activity for dynamic backup calculation.
        
        Args:
            activity_type: 'interaction', 'pattern', 'preference', 'agent_task', 'error'
        """
        with self._activity_lock:
            if activity_type == 'interaction':
                self.activity.interactions_count += 1
                self.state.interactions_since_backup += 1
            elif activity_type == 'pattern':
                self.activity.patterns_learned += 1
                self.state.patterns_since_backup += 1
            elif activity_type == 'preference':
                self.activity.preferences_changed += 1
            elif activity_type == 'agent_task':
                self.activity.agent_tasks_completed += 1
            elif activity_type == 'error':
                self.activity.errors_encountered += 1
        
        # Check if we need an immediate backup (critical knowledge)
        if self._get_activity_level() == 'critical':
            # Trigger immediate backup in a separate thread
            threading.Thread(
                target=self._critical_backup,
                daemon=True,
                name="VA21-CriticalBackup"
            ).start()
    
    def _critical_backup(self):
        """Perform an immediate backup when critical knowledge threshold is reached."""
        print("[PersistentMemory] ⚠ Critical knowledge threshold - immediate backup!")
        self.create_backup(backup_type='critical')
        self._reset_activity_counters()
    
    def create_backup(self, backup_type: str = 'manual') -> Optional[BackupInfo]:
        """
        Create a backup of all VA21 knowledge.
        
        Args:
            backup_type: 'auto', 'shutdown', 'manual', 'dynamic', 'critical'
            
        Returns:
            BackupInfo or None if failed
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        activity_level = self._get_activity_level()
        backup_name = f"{backup_type}_{activity_level}_{timestamp}.tar.gz"
        backup_path = os.path.join(BACKUPS_PATH, backup_name)
        
        print(f"[PersistentMemory] Creating {backup_type} backup (activity: {activity_level})...")
        
        try:
            # Save current state first
            self._save_state()
            
            # Create compressed backup
            with tarfile.open(backup_path, "w:gz") as tar:
                # Backup knowledge base
                if os.path.exists(KNOWLEDGE_BASE_PATH):
                    tar.add(KNOWLEDGE_BASE_PATH, arcname="knowledge_base")
                
                # Backup state
                if os.path.exists(STATE_PATH):
                    tar.add(STATE_PATH, arcname="state")
                
                # Backup config
                if os.path.exists(CONFIG_PATH):
                    tar.add(CONFIG_PATH, arcname="config")
            
            # Get backup size
            size_bytes = os.path.getsize(backup_path)
            
            # Update state
            self.state.last_backup = timestamp
            self.state.total_backups += 1
            self._save_state()
            
            # Clean old backups
            self._cleanup_old_backups()
            
            backup_info = BackupInfo(
                backup_id=f"backup_{timestamp}",
                timestamp=datetime.now().isoformat(),
                backup_type=backup_type,
                path=backup_path,
                size_bytes=size_bytes,
                components=['knowledge_base', 'state', 'config'],
                activity_level=activity_level
            )
            
            print(f"[PersistentMemory] Backup created: {backup_name} ({size_bytes / 1024:.1f} KB)")
            return backup_info
            
        except Exception as e:
            print(f"[PersistentMemory] Backup failed: {e}")
            return None
    
    def restore_backup(self, backup_path: str = None) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup_path: Path to backup file (or latest if None)
            
        Returns:
            True if successful
        """
        if not backup_path:
            # Find latest backup
            backup_path = self._get_latest_backup()
            if not backup_path:
                print("[PersistentMemory] No backups found")
                return False
        
        if not os.path.exists(backup_path):
            print(f"[PersistentMemory] Backup not found: {backup_path}")
            return False
        
        print(f"[PersistentMemory] Restoring from: {backup_path}")
        
        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                # Extract to VA21 home
                tar.extractall(VA21_HOME)
            
            # Reload state
            self.state = self._load_state()
            self.state.last_restore = datetime.now().isoformat()
            self._save_state()
            
            print("[PersistentMemory] Restore complete!")
            return True
            
        except Exception as e:
            print(f"[PersistentMemory] Restore failed: {e}")
            return False
    
    def _get_latest_backup(self) -> Optional[str]:
        """Get the path to the latest backup."""
        if not os.path.exists(BACKUPS_PATH):
            return None
        
        backups = [
            os.path.join(BACKUPS_PATH, f)
            for f in os.listdir(BACKUPS_PATH)
            if f.endswith('.tar.gz')
        ]
        
        if not backups:
            return None
        
        return max(backups, key=os.path.getmtime)
    
    def _cleanup_old_backups(self):
        """Remove old backups to save space."""
        if not os.path.exists(BACKUPS_PATH):
            return
        
        backups = sorted([
            os.path.join(BACKUPS_PATH, f)
            for f in os.listdir(BACKUPS_PATH)
            if f.endswith('.tar.gz')
        ], key=os.path.getmtime)
        
        # Keep only the most recent backups
        while len(backups) > MAX_BACKUPS_TO_KEEP:
            old_backup = backups.pop(0)
            try:
                os.remove(old_backup)
                print(f"[PersistentMemory] Cleaned old backup: {os.path.basename(old_backup)}")
            except Exception:
                pass
    
    def list_backups(self) -> List[BackupInfo]:
        """List all available backups."""
        backups = []
        
        if not os.path.exists(BACKUPS_PATH):
            return backups
        
        for filename in os.listdir(BACKUPS_PATH):
            if not filename.endswith('.tar.gz'):
                continue
            
            filepath = os.path.join(BACKUPS_PATH, filename)
            
            # Parse backup type from filename
            parts = filename.replace('.tar.gz', '').split('_')
            backup_type = parts[0] if parts else 'unknown'
            
            backups.append(BackupInfo(
                backup_id=filename.replace('.tar.gz', ''),
                timestamp=datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                backup_type=backup_type,
                path=filepath,
                size_bytes=os.path.getsize(filepath),
                components=['knowledge_base', 'state', 'config']
            ))
        
        return sorted(backups, key=lambda b: b.timestamp, reverse=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SHUTDOWN HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def register_shutdown_handlers(self):
        """Register handlers for graceful shutdown with backup."""
        if self._shutdown_handlers_registered:
            return
        
        # Register atexit handler
        atexit.register(self._on_shutdown)
        
        # Register signal handlers
        for sig in [signal.SIGTERM, signal.SIGINT]:
            try:
                signal.signal(sig, self._signal_handler)
            except Exception:
                pass  # Some signals may not be available
        
        self._shutdown_handlers_registered = True
        print("[PersistentMemory] Shutdown handlers registered (auto backup on exit)")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n[PersistentMemory] Received signal {signum}, performing shutdown backup...")
        self._on_shutdown()
        sys.exit(0)
    
    def _on_shutdown(self):
        """Called when the system is shutting down."""
        if BACKUP_ON_SHUTDOWN:
            print("[PersistentMemory] Performing shutdown backup...")
            self.create_backup(backup_type='shutdown')
        
        self.stop_auto_backup()
        self._save_state()
        print("[PersistentMemory] Shutdown complete. Knowledge preserved!")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # KNOWLEDGE PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def save_learned_pattern(self, pattern_type: str, pattern_data: Dict):
        """
        Save a learned pattern to persistent storage.
        
        Args:
            pattern_type: Type of pattern (command, preference, usage)
            pattern_data: Pattern data to save
        """
        patterns_dir = os.path.join(KNOWLEDGE_BASE_PATH, "learned_patterns")
        os.makedirs(patterns_dir, exist_ok=True)
        
        filename = f"{pattern_type}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(patterns_dir, filename)
        
        # Load existing patterns
        patterns = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    patterns = json.load(f)
            except Exception:
                patterns = []
        
        # Add new pattern
        pattern_data['timestamp'] = datetime.now().isoformat()
        patterns.append(pattern_data)
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        self.state.total_learned_patterns += 1
        
        # Record activity for dynamic backup
        self.record_activity('pattern')
    
    def save_user_preference(self, preference_key: str, preference_value: Any):
        """
        Save a user preference to persistent storage.
        
        Args:
            preference_key: Preference identifier
            preference_value: Preference value
        """
        prefs_file = os.path.join(KNOWLEDGE_BASE_PATH, "user_preferences", "preferences.json")
        os.makedirs(os.path.dirname(prefs_file), exist_ok=True)
        
        # Load existing preferences
        preferences = {}
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r') as f:
                    preferences = json.load(f)
            except Exception:
                preferences = {}
        
        # Update preference
        preferences[preference_key] = {
            'value': preference_value,
            'updated': datetime.now().isoformat()
        }
        
        # Save
        with open(prefs_file, 'w') as f:
            json.dump(preferences, f, indent=2)
        
        self.state.total_preferences += 1
        
        # Record activity for dynamic backup
        self.record_activity('preference')
    
    def get_user_preferences(self) -> Dict:
        """Get all user preferences."""
        prefs_file = os.path.join(KNOWLEDGE_BASE_PATH, "user_preferences", "preferences.json")
        
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {}
    
    def save_conversation_history(self, conversation: List[Dict]):
        """Save conversation history for context preservation."""
        history_dir = os.path.join(KNOWLEDGE_BASE_PATH, "conversation_history")
        os.makedirs(history_dir, exist_ok=True)
        
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(history_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'messages': conversation
            }, f, indent=2)
    
    def create_mind_map(self, topic: str, connections: Dict):
        """
        Create an Obsidian-style mind map.
        
        Args:
            topic: Central topic
            connections: Dict of connected topics and relationships
        """
        mind_maps_dir = os.path.join(KNOWLEDGE_BASE_PATH, "mind_maps")
        os.makedirs(mind_maps_dir, exist_ok=True)
        
        # Create Obsidian-compatible markdown
        safe_topic = topic.replace(' ', '_').replace('/', '_')
        filepath = os.path.join(mind_maps_dir, f"{safe_topic}.md")
        
        content = f"""---
type: mind_map
topic: {topic}
created: {datetime.now().isoformat()}
tags:
  - mind_map
  - knowledge
  - om_vinayaka
---

# {topic}

## Connections

"""
        for connected_topic, relationship in connections.items():
            safe_connected = connected_topic.replace(' ', '_')
            content += f"- [[{safe_connected}]] - {relationship}\n"
        
        content += f"""

---
*Created by Om Vinayaka AI - Persistent Memory System*
"""
        
        with open(filepath, 'w') as f:
            f.write(content)
    
    def get_status(self) -> Dict:
        """Get persistent memory status including dynamic backup info."""
        backups = self.list_backups()
        activity_level = self._get_activity_level()
        
        with self._activity_lock:
            current_activity = {
                'interactions': self.activity.interactions_count,
                'patterns_learned': self.activity.patterns_learned,
                'preferences_changed': self.activity.preferences_changed,
                'agent_tasks': self.activity.agent_tasks_completed,
            }
        
        return {
            'version': self.VERSION,
            'knowledge_base_path': KNOWLEDGE_BASE_PATH,
            'backups_path': BACKUPS_PATH,
            'total_backups': len(backups),
            'last_backup': self.state.last_backup,
            'last_restore': self.state.last_restore,
            'total_learned_patterns': self.state.total_learned_patterns,
            'total_preferences': self.state.total_preferences,
            # Dynamic backup info
            'dynamic_backup': {
                'enabled': True,
                'current_interval_minutes': self._current_interval_minutes,
                'base_interval_minutes': BACKUP_INTERVAL_MINUTES,
                'min_interval_minutes': MIN_BACKUP_INTERVAL_MINUTES,
                'max_interval_minutes': MAX_BACKUP_INTERVAL_MINUTES,
                'activity_level': activity_level,
                'current_activity': current_activity,
                'thresholds': {
                    'high_activity': HIGH_ACTIVITY_THRESHOLD,
                    'medium_activity': MEDIUM_ACTIVITY_THRESHOLD,
                    'critical_knowledge': CRITICAL_KNOWLEDGE_THRESHOLD,
                },
            },
            'auto_backup_active': self._backup_thread and self._backup_thread.is_alive(),
            'recent_backups': [asdict(b) for b in backups[:5]],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_persistent_memory_instance = None


def get_persistent_memory() -> PersistentMemoryManager:
    """Get the PersistentMemoryManager singleton."""
    global _persistent_memory_instance
    
    if _persistent_memory_instance is None:
        _persistent_memory_instance = PersistentMemoryManager()
        _persistent_memory_instance.register_shutdown_handlers()
        _persistent_memory_instance.start_auto_backup()
    
    return _persistent_memory_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the persistent memory system."""
    print("=" * 70)
    print("VA21 OS - Persistent Memory System Test")
    print("Om Vinayaka - May your knowledge persist eternally")
    print("=" * 70)
    
    memory = get_persistent_memory()
    
    # Show status
    print("\n--- Memory Status ---")
    status = memory.get_status()
    print(json.dumps(status, indent=2))
    
    # Test saving a learned pattern
    print("\n--- Testing Pattern Learning ---")
    memory.save_learned_pattern('command', {
        'input': 'open browser',
        'action': 'launch_app',
        'app': 'firefox',
        'success': True
    })
    print("✓ Saved learned pattern")
    
    # Test saving a preference
    print("\n--- Testing Preferences ---")
    memory.save_user_preference('theme', 'dark')
    memory.save_user_preference('language', 'en')
    print("✓ Saved preferences")
    
    # Test mind map
    print("\n--- Testing Mind Map ---")
    memory.create_mind_map('VA21 OS', {
        'Om Vinayaka AI': 'Core controller',
        'Self-Learning': 'Pattern recognition',
        'Summary Engine': 'Context preservation',
        'Guardian AI': 'Security (isolated)',
    })
    print("✓ Created mind map")
    
    # Create manual backup
    print("\n--- Testing Backup ---")
    backup = memory.create_backup(backup_type='manual')
    if backup:
        print(f"✓ Backup created: {backup.path}")
    
    # List backups
    print("\n--- Available Backups ---")
    for backup in memory.list_backups()[:5]:
        print(f"  {backup.backup_type}: {backup.timestamp} ({backup.size_bytes / 1024:.1f} KB)")
    
    print("\n" + "=" * 70)
    print("Test complete! Memory will persist across restarts.")
    print("=" * 70)


if __name__ == "__main__":
    main()
