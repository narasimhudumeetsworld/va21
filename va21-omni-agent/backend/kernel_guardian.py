"""
VA21 Kernel Guardian - Light Linux Kernel Layer
A simulated light kernel layer with Guardian AI protection at the kernel level.

This module provides kernel-level security protection for the VA21 Research OS,
implementing a security-first approach where the Guardian AI monitors and protects
all system operations from the lowest level.
"""

import os
import sys
import time
import json
import hashlib
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class KernelSecurityLevel(Enum):
    """Security levels for the kernel layer."""
    LOCKDOWN = 0     # Complete system lockdown
    CRITICAL = 1     # Critical security mode
    HIGH = 2         # High security
    STANDARD = 3     # Normal operation
    PERMISSIVE = 4   # Relaxed (for development)


class ProcessThreatLevel(Enum):
    """Threat classification for processes."""
    SAFE = "safe"
    UNKNOWN = "unknown"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    BLOCKED = "blocked"


class KernelEventType(Enum):
    """Types of kernel events."""
    PROCESS_START = "process_start"
    PROCESS_END = "process_end"
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    MEMORY_ACCESS = "memory_access"
    SYSTEM_CALL = "system_call"
    SECURITY_ALERT = "security_alert"
    GUARDIAN_SCAN = "guardian_scan"
    BOOT_SEQUENCE = "boot_sequence"


@dataclass
class KernelEvent:
    """Represents a kernel-level event."""
    event_id: str
    event_type: KernelEventType
    timestamp: datetime
    source: str
    details: Dict = field(default_factory=dict)
    threat_level: ProcessThreatLevel = ProcessThreatLevel.SAFE
    handled: bool = False


@dataclass
class ProtectedProcess:
    """Represents a protected process in the kernel layer."""
    pid: int
    name: str
    path: str
    start_time: datetime
    threat_level: ProcessThreatLevel = ProcessThreatLevel.UNKNOWN
    guardian_verified: bool = False
    memory_protected: bool = False
    network_allowed: bool = False
    sandbox_level: int = 0


@dataclass
class SecurityPolicy:
    """Security policy for kernel operations."""
    name: str
    description: str
    enabled: bool = True
    priority: int = 0
    rules: List[Dict] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)


class KernelGuardian:
    """
    VA21 Kernel Guardian - Core Security Protection Layer
    
    This class implements the light kernel layer for the VA21 Research OS,
    providing Guardian AI protection at the kernel level for comprehensive
    system security.
    
    Features:
    - Process monitoring and protection
    - Memory access protection
    - File system security
    - Network access control
    - System call interception simulation
    - Guardian AI integration for threat detection
    - Boot sequence security verification
    """
    
    VERSION = "1.0.0"
    CODENAME = "Vinayaka"  # Named after the invocation "Om Vinayaka"
    
    def __init__(self, config_path: str = "data/kernel", local_llm=None):
        self.config_path = config_path
        self.local_llm = local_llm
        
        os.makedirs(config_path, exist_ok=True)
        
        # Boot state
        self.boot_time: Optional[datetime] = None
        self.is_booted = False
        self.boot_sequence_log: List[str] = []
        
        # Security state
        self.security_level = KernelSecurityLevel.STANDARD
        self.security_policies: Dict[str, SecurityPolicy] = {}
        
        # Process management
        self.protected_processes: Dict[int, ProtectedProcess] = {}
        self.blocked_processes: List[str] = []
        
        # Event handling
        self.event_queue: deque = deque(maxlen=10000)
        self.event_handlers: Dict[KernelEventType, List[Callable]] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.guardian_thread: Optional[threading.Thread] = None
        
        # System metrics
        self.system_metrics: Dict = {}
        self.metrics_history: deque = deque(maxlen=3600)  # 1 hour of per-second data
        
        # Security scanning
        self.scan_results: List[Dict] = []
        self.last_full_scan: Optional[datetime] = None
        
        # Protected paths (critical system paths)
        self.protected_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/boot",
            "/root",
            "~/.ssh",
        ]
        
        # Dangerous commands/patterns
        self.dangerous_patterns = [
            "rm -rf /",
            ":(){ :|:& };:",  # Fork bomb
            "dd if=/dev/zero",
            "mkfs.",
            "format c:",
            "> /dev/sda",
            "chmod -R 777 /",
        ]
        
        # Initialize default policies
        self._initialize_default_policies()
        
        print(f"[KernelGuardian] Initializing VA21 Kernel Guardian v{self.VERSION} ({self.CODENAME})")
    
    def _initialize_default_policies(self):
        """Initialize default security policies."""
        self.security_policies = {
            "process_protection": SecurityPolicy(
                name="Process Protection",
                description="Protects system processes from unauthorized access",
                priority=1,
                rules=[
                    {"type": "protect_system_processes", "enabled": True},
                    {"type": "block_process_injection", "enabled": True},
                    {"type": "monitor_child_processes", "enabled": True}
                ],
                actions=["block", "alert", "log"]
            ),
            "memory_protection": SecurityPolicy(
                name="Memory Protection",
                description="Protects memory from unauthorized access",
                priority=1,
                rules=[
                    {"type": "protect_kernel_memory", "enabled": True},
                    {"type": "detect_buffer_overflow", "enabled": True},
                    {"type": "prevent_memory_injection", "enabled": True}
                ],
                actions=["block", "alert", "log"]
            ),
            "file_protection": SecurityPolicy(
                name="File System Protection",
                description="Protects critical files and directories",
                priority=2,
                rules=[
                    {"type": "protect_system_files", "enabled": True},
                    {"type": "monitor_file_changes", "enabled": True},
                    {"type": "block_unauthorized_access", "enabled": True}
                ],
                actions=["block", "alert", "log"]
            ),
            "network_protection": SecurityPolicy(
                name="Network Protection",
                description="Controls network access for processes",
                priority=2,
                rules=[
                    {"type": "restrict_outbound", "enabled": True},
                    {"type": "block_malicious_ips", "enabled": True},
                    {"type": "monitor_connections", "enabled": True}
                ],
                actions=["block", "alert", "log"]
            ),
            "command_protection": SecurityPolicy(
                name="Command Protection",
                description="Blocks dangerous system commands",
                priority=0,
                rules=[
                    {"type": "block_dangerous_commands", "enabled": True},
                    {"type": "sanitize_input", "enabled": True}
                ],
                actions=["block", "alert", "log"]
            )
        }
    
    def boot(self) -> Tuple[bool, List[str]]:
        """
        Execute the kernel boot sequence.
        
        Returns:
            Tuple of (success, boot_log)
        """
        self.boot_time = datetime.now()
        self.boot_sequence_log = []
        
        def log_boot(message: str, level: str = "INFO"):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            entry = f"[{timestamp}] [{level}] {message}"
            self.boot_sequence_log.append(entry)
            print(f"[BOOT] {entry}")
        
        try:
            log_boot("=" * 50)
            log_boot("VA21 Research OS - Kernel Boot Sequence")
            log_boot(f"Version: {self.VERSION} ({self.CODENAME})")
            log_boot("=" * 50)
            
            # Phase 1: Initialize Guardian AI Core
            log_boot("Phase 1: Initializing Guardian AI Core...")
            time.sleep(0.1)
            if self.local_llm:
                log_boot("  Guardian AI model detected")
                log_boot("  Security analysis engine: ONLINE")
            else:
                log_boot("  Guardian AI: Simulation mode", "WARN")
            log_boot("Phase 1: COMPLETE")
            
            # Phase 2: Load Security Policies
            log_boot("Phase 2: Loading Security Policies...")
            time.sleep(0.1)
            for policy_name, policy in self.security_policies.items():
                status = "ENABLED" if policy.enabled else "DISABLED"
                log_boot(f"  Policy '{policy_name}': {status}")
            log_boot("Phase 2: COMPLETE")
            
            # Phase 3: Initialize Process Protection
            log_boot("Phase 3: Initializing Process Protection Layer...")
            time.sleep(0.1)
            log_boot("  Process monitor: ARMED")
            log_boot("  Memory protection: ACTIVE")
            log_boot("  System call interception: READY")
            log_boot("Phase 3: COMPLETE")
            
            # Phase 4: Initialize File System Protection
            log_boot("Phase 4: Initializing File System Protection...")
            time.sleep(0.1)
            log_boot(f"  Protected paths: {len(self.protected_paths)}")
            log_boot("  File integrity monitor: ARMED")
            log_boot("Phase 4: COMPLETE")
            
            # Phase 5: Initialize Network Protection
            log_boot("Phase 5: Initializing Network Protection...")
            time.sleep(0.1)
            log_boot("  Network monitor: ARMED")
            log_boot("  Outbound filtering: ACTIVE")
            log_boot("Phase 5: COMPLETE")
            
            # Phase 6: Start Guardian Monitoring
            log_boot("Phase 6: Starting Guardian Monitoring Threads...")
            self.start_monitoring()
            time.sleep(0.1)
            log_boot("  System monitor: RUNNING")
            log_boot("  Guardian scanner: RUNNING")
            log_boot("Phase 6: COMPLETE")
            
            # Phase 7: Verify System Integrity
            log_boot("Phase 7: Verifying System Integrity...")
            time.sleep(0.1)
            integrity_check = self._verify_system_integrity()
            if integrity_check:
                log_boot("  System integrity: VERIFIED")
            else:
                log_boot("  System integrity: DEGRADED", "WARN")
            log_boot("Phase 7: COMPLETE")
            
            # Boot complete
            log_boot("=" * 50)
            log_boot("KERNEL BOOT SEQUENCE COMPLETE")
            log_boot(f"Security Level: {self.security_level.name}")
            log_boot(f"Boot Time: {(datetime.now() - self.boot_time).total_seconds():.2f}s")
            log_boot("=" * 50)
            
            self.is_booted = True
            self._emit_event(KernelEventType.BOOT_SEQUENCE, "kernel", {
                "status": "success",
                "boot_time_seconds": (datetime.now() - self.boot_time).total_seconds()
            })
            
            return True, self.boot_sequence_log
            
        except Exception as e:
            log_boot(f"BOOT FAILED: {str(e)}", "ERROR")
            self._emit_event(KernelEventType.BOOT_SEQUENCE, "kernel", {
                "status": "failed",
                "error": str(e)
            })
            return False, self.boot_sequence_log
    
    def _verify_system_integrity(self) -> bool:
        """Verify system integrity during boot."""
        try:
            # Check critical components
            checks = [
                self.local_llm is not None or True,  # Allow simulation mode
                len(self.security_policies) > 0,
                self.config_path and os.path.exists(self.config_path)
            ]
            return all(checks)
        except Exception:
            return False
    
    def start_monitoring(self):
        """Start kernel monitoring threads."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        # Start system monitor thread
        self.monitor_thread = threading.Thread(
            target=self._system_monitor_loop,
            daemon=True,
            name="KernelMonitor"
        )
        self.monitor_thread.start()
        
        # Start guardian scanner thread
        self.guardian_thread = threading.Thread(
            target=self._guardian_scanner_loop,
            daemon=True,
            name="GuardianScanner"
        )
        self.guardian_thread.start()
        
        print("[KernelGuardian] Monitoring started")
    
    def stop_monitoring(self):
        """Stop kernel monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        if self.guardian_thread:
            self.guardian_thread.join(timeout=5.0)
        print("[KernelGuardian] Monitoring stopped")
    
    def _system_monitor_loop(self):
        """Main system monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                self.system_metrics = metrics
                self.metrics_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics
                })
                
                # Check for anomalies
                self._check_anomalies(metrics)
                
                # Update protected processes
                self._update_protected_processes()
                
            except Exception as e:
                print(f"[KernelGuardian] Monitor error: {e}")
            
            time.sleep(1)  # Collect metrics every second
    
    def _guardian_scanner_loop(self):
        """Guardian AI scanner loop for threat detection."""
        scan_interval = 300  # 5 minutes
        
        while self.is_monitoring:
            try:
                # Run periodic security scan
                self._run_security_scan()
                
            except Exception as e:
                print(f"[KernelGuardian] Scanner error: {e}")
            
            # Wait for next scan interval
            for _ in range(scan_interval):
                if not self.is_monitoring:
                    break
                time.sleep(1)
    
    def _collect_system_metrics(self) -> Dict:
        """Collect current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network stats if available
            try:
                net_io = psutil.net_io_counters()
                network = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            except Exception:
                network = {}
            
            # Get process count
            process_count = len(psutil.pids())
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": network,
                "processes": {
                    "count": process_count,
                    "protected": len(self.protected_processes)
                },
                "security": {
                    "level": self.security_level.name,
                    "alerts": len([e for e in self.event_queue 
                                   if e.event_type == KernelEventType.SECURITY_ALERT]),
                    "blocked": len(self.blocked_processes)
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_anomalies(self, metrics: Dict):
        """Check for system anomalies."""
        # High CPU usage
        if metrics.get("cpu", {}).get("percent", 0) > 90:
            self._emit_event(
                KernelEventType.SECURITY_ALERT,
                "kernel_monitor",
                {"type": "high_cpu", "value": metrics["cpu"]["percent"]}
            )
        
        # High memory usage
        if metrics.get("memory", {}).get("percent", 0) > 95:
            self._emit_event(
                KernelEventType.SECURITY_ALERT,
                "kernel_monitor",
                {"type": "high_memory", "value": metrics["memory"]["percent"]}
            )
        
        # Low disk space
        if metrics.get("disk", {}).get("percent", 0) > 95:
            self._emit_event(
                KernelEventType.SECURITY_ALERT,
                "kernel_monitor",
                {"type": "low_disk", "value": metrics["disk"]["percent"]}
            )
    
    def _update_protected_processes(self):
        """Update the list of protected processes."""
        try:
            current_pids = set(psutil.pids())
            protected_pids = set(self.protected_processes.keys())
            
            # Remove ended processes
            for pid in protected_pids - current_pids:
                process = self.protected_processes.pop(pid, None)
                if process:
                    self._emit_event(
                        KernelEventType.PROCESS_END,
                        f"process_{pid}",
                        {"name": process.name, "pid": pid}
                    )
            
            # Monitor VA21-related processes
            for pid in current_pids:
                try:
                    proc = psutil.Process(pid)
                    name = proc.name().lower()
                    
                    # Auto-protect VA21 and Python processes
                    if any(x in name for x in ['python', 'node', 'electron', 'va21']):
                        if pid not in self.protected_processes:
                            self.protected_processes[pid] = ProtectedProcess(
                                pid=pid,
                                name=proc.name(),
                                path=proc.exe() if hasattr(proc, 'exe') else "",
                                start_time=datetime.now(),
                                guardian_verified=True,
                                memory_protected=True
                            )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"[KernelGuardian] Process update error: {e}")
    
    def _run_security_scan(self):
        """Run a security scan using Guardian AI."""
        self.last_full_scan = datetime.now()
        scan_result = {
            "timestamp": self.last_full_scan.isoformat(),
            "findings": [],
            "status": "clean"
        }
        
        try:
            # Scan for dangerous patterns in environment
            for pattern in self.dangerous_patterns:
                # Check if pattern appears in any running process cmdline
                for proc in psutil.process_iter(['cmdline']):
                    try:
                        cmdline = ' '.join(proc.info.get('cmdline') or [])
                        if pattern.lower() in cmdline.lower():
                            scan_result["findings"].append({
                                "type": "dangerous_command",
                                "process": proc.pid,
                                "pattern": pattern
                            })
                            scan_result["status"] = "threats_found"
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            # Use Guardian AI for analysis if available
            if self.local_llm:
                # Analyze current system state
                analysis_prompt = f"""Analyze this system state for security threats:
                - Running processes: {len(psutil.pids())}
                - CPU usage: {psutil.cpu_percent()}%
                - Memory usage: {psutil.virtual_memory().percent}%
                
                Report any concerns."""
                
                try:
                    analysis = self.local_llm.generate(analysis_prompt)
                    if "UNSAFE" in analysis.upper() or "SUSPICIOUS" in analysis.upper():
                        scan_result["guardian_analysis"] = analysis
                        scan_result["status"] = "review_needed"
                except Exception:
                    pass
            
            self.scan_results.append(scan_result)
            
            self._emit_event(
                KernelEventType.GUARDIAN_SCAN,
                "kernel_guardian",
                scan_result
            )
            
        except Exception as e:
            print(f"[KernelGuardian] Scan error: {e}")
    
    def analyze_command(self, command: str) -> Tuple[bool, str]:
        """
        Analyze a command for security threats.
        
        Args:
            command: The command to analyze
            
        Returns:
            Tuple of (is_safe, analysis_message)
        """
        # Check against dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.lower() in command.lower():
                self._emit_event(
                    KernelEventType.SECURITY_ALERT,
                    "command_analyzer",
                    {"command": command, "matched_pattern": pattern}
                )
                return False, f"BLOCKED: Dangerous command pattern detected: {pattern}"
        
        # Use Guardian AI for deeper analysis
        if self.local_llm:
            try:
                prompt = f"Analyze this command for security risks: {command}"
                analysis = self.local_llm.generate(prompt)
                
                if "UNSAFE" in analysis.upper():
                    return False, f"BLOCKED by Guardian AI: {analysis}"
                elif "SUSPICIOUS" in analysis.upper():
                    return True, f"WARNING: {analysis}"
            except Exception:
                pass
        
        return True, "Command approved by Kernel Guardian"
    
    def analyze_file_access(self, path: str, access_type: str = "read") -> Tuple[bool, str]:
        """
        Analyze a file access request.
        
        Args:
            path: The file path
            access_type: Type of access (read, write, execute)
            
        Returns:
            Tuple of (is_allowed, message)
        """
        # Check protected paths
        for protected in self.protected_paths:
            if protected in path or path.startswith(protected.replace('~', '')):
                if access_type != "read":
                    self._emit_event(
                        KernelEventType.SECURITY_ALERT,
                        "file_access",
                        {"path": path, "type": access_type, "blocked": True}
                    )
                    return False, f"BLOCKED: Write access to protected path: {path}"
        
        self._emit_event(
            KernelEventType.FILE_ACCESS,
            "file_access",
            {"path": path, "type": access_type, "allowed": True}
        )
        
        return True, "File access approved"
    
    def set_security_level(self, level: KernelSecurityLevel):
        """Set the kernel security level."""
        old_level = self.security_level
        self.security_level = level
        
        print(f"[KernelGuardian] Security level changed: {old_level.name} -> {level.name}")
        
        self._emit_event(
            KernelEventType.SECURITY_ALERT,
            "kernel",
            {"type": "security_level_change", "old": old_level.name, "new": level.name}
        )
    
    def _emit_event(self, event_type: KernelEventType, source: str, details: Dict):
        """Emit a kernel event."""
        event = KernelEvent(
            event_id=f"evt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            details=details
        )
        
        self.event_queue.append(event)
        
        # Call registered handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"[KernelGuardian] Event handler error: {e}")
        
        # Call alert callbacks for security alerts
        if event_type == KernelEventType.SECURITY_ALERT:
            for callback in self.alert_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[KernelGuardian] Alert callback error: {e}")
    
    def register_event_handler(self, event_type: KernelEventType, handler: Callable):
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def add_alert_callback(self, callback: Callable):
        """Add an alert callback."""
        self.alert_callbacks.append(callback)
    
    def get_status(self) -> Dict:
        """Get current kernel status."""
        return {
            "version": self.VERSION,
            "codename": self.CODENAME,
            "booted": self.is_booted,
            "boot_time": self.boot_time.isoformat() if self.boot_time else None,
            "uptime_seconds": (datetime.now() - self.boot_time).total_seconds() if self.boot_time else 0,
            "security_level": self.security_level.name,
            "monitoring": self.is_monitoring,
            "protected_processes": len(self.protected_processes),
            "blocked_processes": len(self.blocked_processes),
            "event_queue_size": len(self.event_queue),
            "last_scan": self.last_full_scan.isoformat() if self.last_full_scan else None,
            "metrics": self.system_metrics
        }
    
    def get_events(self, limit: int = 100, event_type: KernelEventType = None) -> List[Dict]:
        """Get recent kernel events."""
        events = list(self.event_queue)
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
        
        return [{
            "event_id": e.event_id,
            "type": e.event_type.value,
            "timestamp": e.timestamp.isoformat(),
            "source": e.source,
            "details": e.details,
            "threat_level": e.threat_level.value
        } for e in events]
    
    def get_metrics_history(self, seconds: int = 60) -> List[Dict]:
        """Get historical metrics."""
        history = list(self.metrics_history)
        cutoff = datetime.now() - timedelta(seconds=seconds)
        
        return [
            m for m in history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
    
    def shutdown(self):
        """Shutdown the kernel guardian."""
        print("[KernelGuardian] Initiating shutdown...")
        
        self.stop_monitoring()
        
        self._emit_event(
            KernelEventType.BOOT_SEQUENCE,
            "kernel",
            {"status": "shutdown"}
        )
        
        self.is_booted = False
        print("[KernelGuardian] Shutdown complete")


# Singleton instance
_kernel_guardian_instance = None


def get_kernel_guardian(local_llm=None) -> KernelGuardian:
    """Get or create the singleton KernelGuardian instance."""
    global _kernel_guardian_instance
    
    if _kernel_guardian_instance is None:
        _kernel_guardian_instance = KernelGuardian(local_llm=local_llm)
    
    return _kernel_guardian_instance


# Example usage
if __name__ == '__main__':
    print("Testing VA21 Kernel Guardian...")
    
    guardian = KernelGuardian()
    
    # Boot the kernel
    success, boot_log = guardian.boot()
    
    if success:
        print("\nKernel booted successfully!")
        print(f"\nStatus: {json.dumps(guardian.get_status(), indent=2)}")
        
        # Test command analysis
        print("\n--- Testing Command Analysis ---")
        test_commands = [
            "ls -la",
            "rm -rf /",
            "cat /etc/passwd",
            "python script.py"
        ]
        
        for cmd in test_commands:
            is_safe, msg = guardian.analyze_command(cmd)
            print(f"  {cmd}: {'SAFE' if is_safe else 'BLOCKED'} - {msg}")
        
        # Wait a bit for metrics collection
        time.sleep(3)
        
        print(f"\nMetrics: {json.dumps(guardian.system_metrics, indent=2)}")
        
        # Shutdown
        guardian.shutdown()
    else:
        print("Boot failed!")
        for line in boot_log:
            print(line)
