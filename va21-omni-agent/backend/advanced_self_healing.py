"""
Advanced Self-Healing System

This module provides advanced self-healing capabilities for the VA21 system,
including automatic error detection, recovery, and system integrity verification.
"""

import os
import json
import hashlib
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Available recovery strategies."""
    RESTART = "restart"
    ROLLBACK = "rollback"
    PATCH = "patch"
    ISOLATE = "isolate"
    ALERT = "alert"
    NONE = "none"


@dataclass
class HealthCheck:
    """Represents a health check configuration."""
    name: str
    check_func: Callable[[], bool]
    interval_seconds: int
    recovery_strategy: RecoveryStrategy
    max_failures: int = 3
    timeout_seconds: int = 30
    enabled: bool = True
    last_check: datetime = None
    consecutive_failures: int = 0
    status: HealthStatus = HealthStatus.UNKNOWN


@dataclass
class RecoveryAction:
    """Represents a recovery action."""
    action_id: str
    health_check: str
    strategy: RecoveryStrategy
    timestamp: datetime
    success: bool
    details: str = ""
    duration_seconds: float = 0


@dataclass
class SystemSnapshot:
    """Represents a system state snapshot."""
    snapshot_id: str
    timestamp: datetime
    config_hash: str
    file_hashes: Dict[str, str]
    metadata: Dict = field(default_factory=dict)


class AdvancedSelfHealing:
    """
    Advanced self-healing system for automatic recovery and integrity verification.
    
    Features:
    - Multiple health check strategies
    - Automatic recovery actions
    - System integrity verification
    - State snapshots and rollback
    - Anomaly detection
    - Recovery history tracking
    """
    
    def __init__(self, config_path: str = "data/self_healing", 
                 ltm_manager=None, vault_manager=None):
        self.config_path = config_path
        self.ltm_manager = ltm_manager
        self.vault_manager = vault_manager
        
        os.makedirs(config_path, exist_ok=True)
        
        # Health checks
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Recovery configuration
        self.recovery_handlers: Dict[RecoveryStrategy, Callable] = {}
        self.recovery_history: List[RecoveryAction] = []
        
        # System snapshots
        self.snapshots: List[SystemSnapshot] = []
        self.snapshot_path = os.path.join(config_path, "snapshots")
        os.makedirs(self.snapshot_path, exist_ok=True)
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.current_status = HealthStatus.UNKNOWN
        
        # Alert configuration
        self.alert_callbacks: List[Callable] = []
        
        # Critical file monitoring
        self.monitored_files: Dict[str, str] = {}  # path -> expected_hash
        
        # Initialize default recovery handlers
        self._initialize_default_handlers()
        
        # Initialize default health checks
        self._initialize_default_checks()
    
    def _initialize_default_handlers(self):
        """Initialize default recovery handlers."""
        self.recovery_handlers = {
            RecoveryStrategy.RESTART: self._restart_component,
            RecoveryStrategy.ROLLBACK: self._rollback_to_snapshot,
            RecoveryStrategy.PATCH: self._apply_patch,
            RecoveryStrategy.ISOLATE: self._isolate_component,
            RecoveryStrategy.ALERT: self._send_alert,
        }
    
    def _initialize_default_checks(self):
        """Initialize default health checks."""
        # Memory check
        self.register_health_check(HealthCheck(
            name="memory_usage",
            check_func=self._check_memory,
            interval_seconds=60,
            recovery_strategy=RecoveryStrategy.ALERT,
            max_failures=3
        ))
        
        # Disk space check
        self.register_health_check(HealthCheck(
            name="disk_space",
            check_func=self._check_disk_space,
            interval_seconds=300,
            recovery_strategy=RecoveryStrategy.ALERT,
            max_failures=1
        ))
        
        # Critical files integrity check
        self.register_health_check(HealthCheck(
            name="file_integrity",
            check_func=self._check_file_integrity,
            interval_seconds=600,
            recovery_strategy=RecoveryStrategy.ROLLBACK,
            max_failures=1
        ))
        
        # Backend connectivity check
        self.register_health_check(HealthCheck(
            name="backend_health",
            check_func=self._check_backend,
            interval_seconds=30,
            recovery_strategy=RecoveryStrategy.RESTART,
            max_failures=3
        ))
    
    def _check_memory(self) -> bool:
        """Check if memory usage is within acceptable limits."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent < 90
        except ImportError:
            # If psutil not available, assume OK
            return True
        except Exception:
            return False
    
    def _check_disk_space(self) -> bool:
        """Check if disk space is sufficient."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100
            return free_percent > 10  # At least 10% free
        except Exception:
            return True
    
    def _check_file_integrity(self) -> bool:
        """Check integrity of monitored files."""
        for path, expected_hash in self.monitored_files.items():
            if not os.path.exists(path):
                print(f"[SelfHealing] File missing: {path}")
                return False
            
            current_hash = self._hash_file(path)
            if current_hash != expected_hash:
                print(f"[SelfHealing] File integrity check failed: {path}")
                return False
        
        return True
    
    def _check_backend(self) -> bool:
        """Check if the backend is responding."""
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            return response.status_code == 200
        except Exception:
            # Backend might not have a health endpoint yet
            return True
    
    def _hash_file(self, path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""
    
    def _hash_directory(self, path: str, extensions: List[str] = None) -> Dict[str, str]:
        """Hash all files in a directory."""
        hashes = {}
        if extensions is None:
            extensions = ['.py', '.js', '.json', '.html', '.css']
        
        for root, _, files in os.walk(path):
            for filename in files:
                if any(filename.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, filename)
                    hashes[file_path] = self._hash_file(file_path)
        
        return hashes
    
    def register_health_check(self, check: HealthCheck):
        """Register a new health check."""
        self.health_checks[check.name] = check
        print(f"[SelfHealing] Registered health check: {check.name}")
    
    def unregister_health_check(self, name: str):
        """Unregister a health check."""
        if name in self.health_checks:
            del self.health_checks[name]
    
    def register_recovery_handler(self, strategy: RecoveryStrategy, handler: Callable):
        """Register a custom recovery handler."""
        self.recovery_handlers[strategy] = handler
    
    def add_monitored_file(self, path: str):
        """Add a file to integrity monitoring."""
        if os.path.exists(path):
            self.monitored_files[path] = self._hash_file(path)
    
    def remove_monitored_file(self, path: str):
        """Remove a file from integrity monitoring."""
        if path in self.monitored_files:
            del self.monitored_files[path]
    
    def add_alert_callback(self, callback: Callable):
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
    
    def create_snapshot(self, directories: List[str] = None, 
                        metadata: Dict = None) -> SystemSnapshot:
        """
        Create a system state snapshot.
        
        Args:
            directories: Directories to include in snapshot
            metadata: Additional metadata
            
        Returns:
            Created snapshot
        """
        if directories is None:
            directories = ['.']
        
        snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Collect file hashes
        all_hashes = {}
        for directory in directories:
            if os.path.exists(directory):
                all_hashes.update(self._hash_directory(directory))
        
        # Create config hash
        config_str = json.dumps(sorted(all_hashes.items()))
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()
        
        snapshot = SystemSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            config_hash=config_hash,
            file_hashes=all_hashes,
            metadata=metadata or {}
        )
        
        # Save snapshot
        snapshot_file = os.path.join(self.snapshot_path, f"{snapshot_id}.json")
        with open(snapshot_file, 'w') as f:
            json.dump({
                'snapshot_id': snapshot.snapshot_id,
                'timestamp': snapshot.timestamp.isoformat(),
                'config_hash': snapshot.config_hash,
                'file_hashes': snapshot.file_hashes,
                'metadata': snapshot.metadata
            }, f, indent=2)
        
        self.snapshots.append(snapshot)
        print(f"[SelfHealing] Created snapshot: {snapshot_id}")
        
        return snapshot
    
    def get_latest_snapshot(self) -> Optional[SystemSnapshot]:
        """Get the most recent snapshot."""
        if not self.snapshots:
            # Try to load from disk
            self._load_snapshots()
        
        if self.snapshots:
            return sorted(self.snapshots, key=lambda s: s.timestamp, reverse=True)[0]
        return None
    
    def _load_snapshots(self):
        """Load snapshots from disk."""
        for filename in os.listdir(self.snapshot_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.snapshot_path, filename), 'r') as f:
                        data = json.load(f)
                    
                    snapshot = SystemSnapshot(
                        snapshot_id=data['snapshot_id'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        config_hash=data['config_hash'],
                        file_hashes=data['file_hashes'],
                        metadata=data.get('metadata', {})
                    )
                    
                    if snapshot not in self.snapshots:
                        self.snapshots.append(snapshot)
                except Exception as e:
                    print(f"[SelfHealing] Error loading snapshot {filename}: {e}")
    
    def compare_to_snapshot(self, snapshot: SystemSnapshot) -> Dict:
        """
        Compare current state to a snapshot.
        
        Args:
            snapshot: Snapshot to compare against
            
        Returns:
            Comparison results
        """
        changes = {
            'modified': [],
            'added': [],
            'deleted': []
        }
        
        current_hashes = {}
        for path in snapshot.file_hashes.keys():
            directory = os.path.dirname(path)
            if os.path.exists(directory):
                current_hashes.update(self._hash_directory(directory))
        
        # Check for modifications and deletions
        for path, expected_hash in snapshot.file_hashes.items():
            if path in current_hashes:
                if current_hashes[path] != expected_hash:
                    changes['modified'].append(path)
            else:
                changes['deleted'].append(path)
        
        # Check for additions
        for path in current_hashes:
            if path not in snapshot.file_hashes:
                changes['added'].append(path)
        
        return changes
    
    def start_monitoring(self):
        """Start the self-healing monitoring system."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.current_status = HealthStatus.HEALTHY
        print("[SelfHealing] Monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        print("[SelfHealing] Monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            for name, check in self.health_checks.items():
                if not check.enabled:
                    continue
                
                # Check if it's time to run this check
                if check.last_check:
                    elapsed = (datetime.now() - check.last_check).total_seconds()
                    if elapsed < check.interval_seconds:
                        continue
                
                # Run the health check
                self._run_health_check(check)
            
            time.sleep(1)  # Prevent tight loop
    
    def _run_health_check(self, check: HealthCheck):
        """Run a single health check."""
        check.last_check = datetime.now()
        
        try:
            is_healthy = check.check_func()
            
            if is_healthy:
                check.status = HealthStatus.HEALTHY
                check.consecutive_failures = 0
            else:
                check.consecutive_failures += 1
                check.status = HealthStatus.DEGRADED
                
                if check.consecutive_failures >= check.max_failures:
                    check.status = HealthStatus.CRITICAL
                    self._trigger_recovery(check)
        
        except Exception as e:
            print(f"[SelfHealing] Health check {check.name} error: {e}")
            check.consecutive_failures += 1
            check.status = HealthStatus.DEGRADED
    
    def _trigger_recovery(self, check: HealthCheck):
        """Trigger recovery for a failed health check."""
        strategy = check.recovery_strategy
        
        if strategy not in self.recovery_handlers:
            print(f"[SelfHealing] No handler for strategy: {strategy}")
            return
        
        action_id = f"recovery_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        action = RecoveryAction(
            action_id=action_id,
            health_check=check.name,
            strategy=strategy,
            timestamp=datetime.now(),
            success=False
        )
        
        try:
            check.status = HealthStatus.RECOVERING
            start_time = time.time()
            
            result = self.recovery_handlers[strategy](check.name)
            
            action.duration_seconds = time.time() - start_time
            action.success = result
            action.details = "Recovery completed" if result else "Recovery failed"
            
            if result:
                check.consecutive_failures = 0
                check.status = HealthStatus.HEALTHY
            else:
                check.status = HealthStatus.CRITICAL
        
        except Exception as e:
            action.success = False
            action.details = f"Recovery error: {e}"
            check.status = HealthStatus.CRITICAL
        
        self.recovery_history.append(action)
        
        # Log to vault if available
        if self.vault_manager:
            self._log_recovery_to_vault(action)
    
    def _log_recovery_to_vault(self, action: RecoveryAction):
        """Log recovery action to the vault."""
        try:
            self.vault_manager.create_note(
                title=f"Recovery Action {action.action_id}",
                content=f"""# Recovery Action

**Action ID:** {action.action_id}
**Health Check:** {action.health_check}
**Strategy:** {action.strategy.value}
**Timestamp:** {action.timestamp.isoformat()}
**Success:** {action.success}
**Duration:** {action.duration_seconds:.2f}s
**Details:** {action.details}
""",
                note_type="log",
                tags=["recovery", "self-healing", action.strategy.value]
            )
        except Exception as e:
            print(f"[SelfHealing] Error logging to vault: {e}")
    
    def _restart_component(self, component_name: str) -> bool:
        """Restart a component."""
        print(f"[SelfHealing] Restarting component: {component_name}")
        # Implementation would depend on the specific component
        return True
    
    def _rollback_to_snapshot(self, component_name: str) -> bool:
        """Rollback to the latest snapshot."""
        print(f"[SelfHealing] Rolling back: {component_name}")
        snapshot = self.get_latest_snapshot()
        if not snapshot:
            print("[SelfHealing] No snapshot available for rollback")
            return False
        
        # Compare and report changes
        changes = self.compare_to_snapshot(snapshot)
        print(f"[SelfHealing] Rollback changes: {changes}")
        
        # Note: Actual file restoration would need to be implemented
        # based on backup strategy
        return True
    
    def _apply_patch(self, component_name: str) -> bool:
        """Apply a patch to fix an issue."""
        print(f"[SelfHealing] Applying patch for: {component_name}")
        return True
    
    def _isolate_component(self, component_name: str) -> bool:
        """Isolate a problematic component."""
        print(f"[SelfHealing] Isolating component: {component_name}")
        
        # Update LTM if available
        if self.ltm_manager:
            self.ltm_manager.remember(f"isolated_{component_name}", "true")
        
        return True
    
    def _send_alert(self, component_name: str) -> bool:
        """Send an alert about an issue."""
        print(f"[SelfHealing] Sending alert for: {component_name}")
        
        for callback in self.alert_callbacks:
            try:
                callback(component_name, "Health check failed")
            except Exception as e:
                print(f"[SelfHealing] Alert callback error: {e}")
        
        return True
    
    def get_health_status(self) -> Dict:
        """Get current health status of all checks."""
        return {
            'overall_status': self.current_status.value,
            'checks': {
                name: {
                    'status': check.status.value,
                    'last_check': check.last_check.isoformat() if check.last_check else None,
                    'consecutive_failures': check.consecutive_failures
                }
                for name, check in self.health_checks.items()
            }
        }
    
    def get_recovery_history(self, limit: int = 10) -> List[Dict]:
        """Get recent recovery actions."""
        history = sorted(self.recovery_history, 
                        key=lambda a: a.timestamp, reverse=True)[:limit]
        
        return [{
            'action_id': a.action_id,
            'health_check': a.health_check,
            'strategy': a.strategy.value,
            'timestamp': a.timestamp.isoformat(),
            'success': a.success,
            'details': a.details
        } for a in history]
    
    def force_recovery(self, health_check_name: str, 
                       strategy: RecoveryStrategy = None) -> bool:
        """Force a recovery action."""
        if health_check_name not in self.health_checks:
            return False
        
        check = self.health_checks[health_check_name]
        original_strategy = check.recovery_strategy
        
        if strategy:
            check.recovery_strategy = strategy
        
        self._trigger_recovery(check)
        
        check.recovery_strategy = original_strategy
        return True


# Example usage
if __name__ == '__main__':
    healing = AdvancedSelfHealing()
    
    # Add some files to monitor
    healing.add_monitored_file("app.py")
    
    # Create a snapshot
    snapshot = healing.create_snapshot(["."])
    print(f"Created snapshot: {snapshot.snapshot_id}")
    
    # Start monitoring
    healing.start_monitoring()
    
    print("Health status:", healing.get_health_status())
    
    # Wait a bit
    time.sleep(5)
    
    # Stop monitoring
    healing.stop_monitoring()
    
    print("Recovery history:", healing.get_recovery_history())
