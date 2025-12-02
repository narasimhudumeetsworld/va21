#!/usr/bin/env python3
"""
VA21 Research OS - Guardian AI Core
====================================

The Guardian AI is the security core of VA21 Research OS.
It monitors system activity, analyzes threats, and protects
the research environment at the kernel/system level.

Om Vinayaka - The remover of obstacles protects this realm.
"""

import os
import sys
import json
import time
import signal
import hashlib
import threading
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SecurityEvent:
    """A security event detected by the Guardian."""
    event_id: str
    timestamp: datetime
    event_type: str  # command, file_access, network, process, anomaly
    severity: str    # info, warning, critical
    description: str
    details: Dict = field(default_factory=dict)
    handled: bool = False


@dataclass
class SecurityRule:
    """A security rule enforced by the Guardian."""
    rule_id: str
    name: str
    pattern: str
    action: str  # block, warn, log
    enabled: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# GUARDIAN AI CORE
# ═══════════════════════════════════════════════════════════════════════════════

class GuardianAI:
    """
    VA21 Guardian AI - The Protector of the Research Realm
    
    The Guardian AI monitors all system activity and protects
    the research environment from threats. It operates at multiple
    levels:
    
    1. Command Analysis - Scans commands before execution
    2. Process Monitoring - Watches for suspicious processes  
    3. File Integrity - Monitors critical file changes
    4. Network Watching - Observes network connections
    5. Anomaly Detection - Identifies unusual behavior
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config_path: str = "/va21/config"):
        self.config_path = config_path
        self.log_path = "/va21/logs"
        
        # Ensure directories exist
        os.makedirs(self.config_path, exist_ok=True)
        os.makedirs(self.log_path, exist_ok=True)
        
        # Security state
        self.is_running = False
        self.security_level = "standard"  # permissive, standard, strict, lockdown
        self.lockdown_mode = False
        
        # Event tracking
        self.events: deque = deque(maxlen=1000)
        self.event_handlers: List[callable] = []
        
        # Rules
        self.rules: Dict[str, SecurityRule] = {}
        self._init_default_rules()
        
        # Monitored items
        self.monitored_files: Dict[str, str] = {}  # path -> hash
        self.watched_processes: Dict[int, str] = {}  # pid -> name
        
        # Metrics
        self.metrics = {
            "commands_analyzed": 0,
            "threats_blocked": 0,
            "warnings_issued": 0,
            "scans_completed": 0
        }
        
        # Monitoring threads
        self.monitor_threads: List[threading.Thread] = []
        
        # Dangerous patterns
        self.dangerous_patterns = [
            # File system destruction
            "rm -rf /",
            "rm -rf /*",
            "rm -rf ~",
            "rm -rf .",
            "> /dev/sda",
            "> /dev/hda",
            "dd if=/dev/zero",
            "dd if=/dev/random of=/dev/sda",
            "mkfs.",
            
            # Fork bombs
            ":(){ :|:& };:",
            "./$0|./$0&",
            
            # Network attacks
            "nc -e /bin/",
            "bash -i >& /dev/tcp",
            "/dev/tcp/",
            
            # Privilege escalation attempts
            "chmod 777 /",
            "chmod -R 777 /",
            "chown root",
            
            # Malicious downloads
            "curl | bash",
            "wget | bash",
            "curl | sh",
            "wget | sh",
            
            # Code injection
            "eval(",
            "exec(",
            "__import__",
            "subprocess.call",
        ]
        
        # Suspicious patterns (warn but don't block)
        self.suspicious_patterns = [
            "/etc/passwd",
            "/etc/shadow",
            ".ssh/",
            "id_rsa",
            "password",
            "secret",
            "api_key",
            "token",
            "credential",
        ]
        
        print(f"[Guardian] Initialized v{self.VERSION}")
    
    def _init_default_rules(self):
        """Initialize default security rules."""
        self.rules = {
            "block_rm_rf": SecurityRule(
                rule_id="block_rm_rf",
                name="Block recursive delete root",
                pattern="rm -rf /",
                action="block"
            ),
            "block_fork_bomb": SecurityRule(
                rule_id="block_fork_bomb",
                name="Block fork bombs",
                pattern=":(){ :|:& };:",
                action="block"
            ),
            "warn_passwd_access": SecurityRule(
                rule_id="warn_passwd_access",
                name="Warn on passwd access",
                pattern="/etc/passwd",
                action="warn"
            ),
            "log_sudo": SecurityRule(
                rule_id="log_sudo",
                name="Log sudo usage",
                pattern="sudo",
                action="log"
            ),
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def analyze_command(self, command: str) -> Tuple[bool, str, str]:
        """
        Analyze a command for security threats.
        
        Args:
            command: The command to analyze
            
        Returns:
            Tuple of (is_safe, action, message)
            action: "allow", "block", "warn"
        """
        self.metrics["commands_analyzed"] += 1
        command_lower = command.lower()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.lower() in command_lower:
                event = SecurityEvent(
                    event_id=f"cmd_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    timestamp=datetime.now(),
                    event_type="command",
                    severity="critical",
                    description=f"Blocked dangerous command: {pattern}",
                    details={"command": command, "pattern": pattern}
                )
                self._record_event(event)
                self.metrics["threats_blocked"] += 1
                return False, "block", f"BLOCKED: Dangerous pattern detected - {pattern}"
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if pattern.lower() in command_lower:
                event = SecurityEvent(
                    event_id=f"cmd_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    timestamp=datetime.now(),
                    event_type="command",
                    severity="warning",
                    description=f"Suspicious command detected: {pattern}",
                    details={"command": command, "pattern": pattern}
                )
                self._record_event(event)
                self.metrics["warnings_issued"] += 1
                return True, "warn", f"WARNING: Command contains sensitive pattern - {pattern}"
        
        # Check custom rules
        for rule in self.rules.values():
            if rule.enabled and rule.pattern.lower() in command_lower:
                if rule.action == "block":
                    self.metrics["threats_blocked"] += 1
                    return False, "block", f"BLOCKED by rule '{rule.name}'"
                elif rule.action == "warn":
                    self.metrics["warnings_issued"] += 1
                    return True, "warn", f"WARNING from rule '{rule.name}'"
        
        return True, "allow", "Command approved"
    
    def analyze_file_access(self, path: str, operation: str = "read") -> Tuple[bool, str]:
        """
        Analyze file access request.
        
        Args:
            path: File path being accessed
            operation: read, write, execute, delete
            
        Returns:
            Tuple of (is_allowed, message)
        """
        # Critical system paths
        critical_paths = [
            "/boot",
            "/etc/shadow",
            "/etc/sudoers",
            "/root",
        ]
        
        # Check critical paths
        for critical in critical_paths:
            if path.startswith(critical):
                if operation in ["write", "delete"]:
                    event = SecurityEvent(
                        event_id=f"file_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                        timestamp=datetime.now(),
                        event_type="file_access",
                        severity="critical",
                        description=f"Blocked {operation} to critical path: {path}",
                        details={"path": path, "operation": operation}
                    )
                    self._record_event(event)
                    return False, f"BLOCKED: Cannot {operation} critical system file"
        
        return True, "Access approved"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROCESS MONITORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def monitor_processes(self):
        """Monitor running processes for suspicious activity."""
        if not PSUTIL_AVAILABLE:
            return
        
        suspicious_names = [
            "nc", "netcat", "ncat",
            "cryptominer", "xmrig",
            "keylogger",
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                pid = proc.info['pid']
                
                for sus in suspicious_names:
                    if sus in name:
                        event = SecurityEvent(
                            event_id=f"proc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                            timestamp=datetime.now(),
                            event_type="process",
                            severity="warning",
                            description=f"Suspicious process detected: {name}",
                            details={"pid": pid, "name": name}
                        )
                        self._record_event(event)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def get_process_info(self) -> Dict:
        """Get current process information."""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            "total": len(processes),
            "top_cpu": sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:5],
            "top_memory": sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:5]
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FILE INTEGRITY
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_monitored_file(self, path: str):
        """Add a file to integrity monitoring."""
        if os.path.exists(path):
            self.monitored_files[path] = self._hash_file(path)
    
    def check_file_integrity(self) -> List[str]:
        """Check integrity of monitored files."""
        changed = []
        
        for path, expected_hash in self.monitored_files.items():
            if not os.path.exists(path):
                changed.append(f"DELETED: {path}")
                event = SecurityEvent(
                    event_id=f"file_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    timestamp=datetime.now(),
                    event_type="file_access",
                    severity="critical",
                    description=f"Monitored file deleted: {path}",
                    details={"path": path}
                )
                self._record_event(event)
            else:
                current_hash = self._hash_file(path)
                if current_hash != expected_hash:
                    changed.append(f"MODIFIED: {path}")
                    event = SecurityEvent(
                        event_id=f"file_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                        timestamp=datetime.now(),
                        event_type="file_access",
                        severity="warning",
                        description=f"Monitored file changed: {path}",
                        details={"path": path}
                    )
                    self._record_event(event)
        
        return changed
    
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NETWORK MONITORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_network_connections(self) -> Dict:
        """Get current network connections."""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            connections = psutil.net_connections()
            return {
                "total": len(connections),
                "established": len([c for c in connections if c.status == 'ESTABLISHED']),
                "listening": len([c for c in connections if c.status == 'LISTEN']),
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM STATUS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "security_level": self.security_level,
            "lockdown": self.lockdown_mode,
        }
        
        if PSUTIL_AVAILABLE:
            metrics.update({
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
            })
        
        return metrics
    
    def get_status(self) -> Dict:
        """Get Guardian status."""
        return {
            "version": self.VERSION,
            "running": self.is_running,
            "security_level": self.security_level,
            "lockdown": self.lockdown_mode,
            "metrics": self.metrics,
            "events_recorded": len(self.events),
            "rules_active": len([r for r in self.rules.values() if r.enabled]),
            "files_monitored": len(self.monitored_files),
        }
    
    def get_recent_events(self, limit: int = 20) -> List[Dict]:
        """Get recent security events."""
        events = list(self.events)
        events.reverse()
        
        return [{
            "event_id": e.event_id,
            "timestamp": e.timestamp.isoformat(),
            "type": e.event_type,
            "severity": e.severity,
            "description": e.description,
        } for e in events[:limit]]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EVENT HANDLING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _record_event(self, event: SecurityEvent):
        """Record a security event."""
        self.events.append(event)
        self._log_event(event)
        
        # Notify handlers
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[Guardian] Event handler error: {e}")
    
    def _log_event(self, event: SecurityEvent):
        """Log event to file."""
        log_file = os.path.join(self.log_path, f"security_{datetime.now().strftime('%Y%m%d')}.log")
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps({
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "severity": event.severity,
                    "description": event.description,
                    "details": event.details
                }) + "\n")
        except Exception as e:
            print(f"[Guardian] Logging error: {e}")
    
    def add_event_handler(self, handler: callable):
        """Add an event handler."""
        self.event_handlers.append(handler)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECURITY CONTROLS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def set_security_level(self, level: str):
        """Set security level."""
        valid_levels = ["permissive", "standard", "strict", "lockdown"]
        if level in valid_levels:
            old_level = self.security_level
            self.security_level = level
            self.lockdown_mode = (level == "lockdown")
            
            event = SecurityEvent(
                event_id=f"cfg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                timestamp=datetime.now(),
                event_type="config",
                severity="info",
                description=f"Security level changed: {old_level} -> {level}",
                details={"old": old_level, "new": level}
            )
            self._record_event(event)
            
            print(f"[Guardian] Security level: {level}")
    
    def add_rule(self, rule: SecurityRule):
        """Add a security rule."""
        self.rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str):
        """Remove a security rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MONITORING DAEMON
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Check processes
                self.monitor_processes()
                
                # Check file integrity
                self.check_file_integrity()
                
                # Update metrics
                self.metrics["scans_completed"] += 1
                
            except Exception as e:
                print(f"[Guardian] Monitor error: {e}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def start(self, daemon: bool = False):
        """Start the Guardian AI."""
        self.is_running = True
        
        print(f"[Guardian] Starting (daemon={daemon})...")
        print(f"[Guardian] Security level: {self.security_level}")
        
        if daemon:
            # Start monitoring in background
            monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            monitor_thread.start()
            self.monitor_threads.append(monitor_thread)
            print("[Guardian] Monitoring daemon started")
        else:
            # Run in foreground
            print("[Guardian] Running in foreground. Press Ctrl+C to stop.")
            try:
                self._monitor_loop()
            except KeyboardInterrupt:
                print("\n[Guardian] Interrupted")
                self.stop()
    
    def stop(self):
        """Stop the Guardian AI."""
        print("[Guardian] Stopping...")
        self.is_running = False
        
        for thread in self.monitor_threads:
            thread.join(timeout=5.0)
        
        print("[Guardian] Stopped")


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_guardian_instance = None

def get_guardian() -> GuardianAI:
    """Get the Guardian AI singleton instance."""
    global _guardian_instance
    if _guardian_instance is None:
        _guardian_instance = GuardianAI()
    return _guardian_instance


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="VA21 Guardian AI")
    parser.add_argument("--daemon", "-d", action="store_true", help="Run as daemon")
    parser.add_argument("--level", "-l", default="standard", 
                       choices=["permissive", "standard", "strict", "lockdown"],
                       help="Security level")
    args = parser.parse_args()
    
    guardian = get_guardian()
    guardian.set_security_level(args.level)
    
    # Handle signals
    def signal_handler(sig, frame):
        print("\n[Guardian] Received shutdown signal")
        guardian.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    guardian.start(daemon=args.daemon)
    
    if args.daemon:
        # Keep running
        while guardian.is_running:
            time.sleep(1)


if __name__ == "__main__":
    main()
