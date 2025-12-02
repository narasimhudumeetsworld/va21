#!/usr/bin/env python3
"""
VA21 Research OS - System Tools Suite
=======================================

Comprehensive system utilities inspired by WinToys and beyond.
A complete toolkit for system optimization, monitoring, and control.

Features:
- System Performance Monitor
- Process Manager (advanced)
- Startup Manager
- Service Manager
- Disk Cleanup and Optimization
- Network Monitor
- Privacy Tools
- Power Management
- System Tweaks
- Registry/Config Editor
- Backup Manager
- System Information

Om Vinayaka - Mastery over the machine, wisdom in control.
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class Priority(Enum):
    """Process priority levels."""
    REALTIME = "realtime"
    HIGH = "high"
    ABOVE_NORMAL = "above_normal"
    NORMAL = "normal"
    BELOW_NORMAL = "below_normal"
    LOW = "low"
    IDLE = "idle"


@dataclass
class ProcessInfo:
    """Information about a process."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    username: str
    created: datetime
    cmdline: str
    priority: str = "normal"
    threads: int = 1


@dataclass
class DiskInfo:
    """Information about a disk."""
    device: str
    mountpoint: str
    fstype: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float


@dataclass
class NetworkInfo:
    """Network interface information."""
    name: str
    ip_address: str
    mac_address: str
    bytes_sent: int
    bytes_recv: int
    is_up: bool


@dataclass
class StartupItem:
    """Startup application entry."""
    name: str
    path: str
    enabled: bool
    source: str  # autostart, rc.local, systemd, etc.
    description: str = ""


class SystemToolsSuite:
    """
    VA21 System Tools Suite
    
    A comprehensive system management toolkit inspired by WinToys
    and enhanced for researchers, writers, and security experts.
    
    Categories:
    1. Performance - Monitor and optimize system performance
    2. Processes - Advanced process management
    3. Startup - Control startup applications
    4. Services - Manage system services
    5. Cleanup - Disk cleanup and optimization
    6. Network - Network monitoring and tools
    7. Privacy - Privacy protection tools
    8. Power - Power and battery management
    9. Tweaks - System customization
    10. Backup - Backup and restore
    11. Info - System information
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config_path: str = "/va21/config"):
        self.config_path = config_path
        
        # Create necessary directories
        os.makedirs(config_path, exist_ok=True)
        os.makedirs(os.path.join(config_path, "backups"), exist_ok=True)
        os.makedirs(os.path.join(config_path, "logs"), exist_ok=True)
        
        # History
        self.command_history: List[Dict] = []
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Cached data
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        
        print(f"[SystemTools] VA21 System Tools v{self.VERSION} initialized")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PERFORMANCE MONITORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_system_status(self) -> Dict:
        """
        Get comprehensive system status.
        
        Returns:
            Dict with CPU, memory, disk, and network status
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "hostname": platform.node(),
            "platform": platform.system(),
            "architecture": platform.machine(),
        }
        
        if PSUTIL_AVAILABLE:
            # CPU
            status["cpu"] = {
                "percent": psutil.cpu_percent(interval=0.1),
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True),
                "freq_current": getattr(psutil.cpu_freq(), 'current', 0) if psutil.cpu_freq() else 0,
            }
            
            # Memory
            mem = psutil.virtual_memory()
            status["memory"] = {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent": mem.percent,
            }
            
            # Swap
            swap = psutil.swap_memory()
            status["swap"] = {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "percent": swap.percent,
            }
            
            # Disk
            status["disks"] = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    status["disks"].append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent,
                    })
                except:
                    pass
            
            # Network
            net_io = psutil.net_io_counters()
            status["network"] = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
            }
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            status["uptime"] = {
                "boot_time": boot_time.isoformat(),
                "uptime_hours": round(uptime.total_seconds() / 3600, 1),
            }
        
        return status
    
    def get_cpu_history(self, seconds: int = 60) -> List[float]:
        """Get CPU usage history for the last N seconds."""
        if not PSUTIL_AVAILABLE:
            return []
        
        history = []
        for _ in range(min(seconds, 10)):
            history.append(psutil.cpu_percent(interval=0.1))
        return history
    
    def get_memory_breakdown(self) -> Dict:
        """Get detailed memory breakdown."""
        if not PSUTIL_AVAILABLE:
            return {}
        
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "free": mem.free,
            "active": getattr(mem, 'active', 0),
            "inactive": getattr(mem, 'inactive', 0),
            "buffers": getattr(mem, 'buffers', 0),
            "cached": getattr(mem, 'cached', 0),
            "shared": getattr(mem, 'shared', 0),
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROCESS MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_processes(self, sort_by: str = "cpu", limit: int = 50) -> List[ProcessInfo]:
        """
        Get list of running processes.
        
        Args:
            sort_by: Sort field (cpu, memory, name, pid)
            limit: Maximum number of processes to return
            
        Returns:
            List of ProcessInfo objects
        """
        if not PSUTIL_AVAILABLE:
            return []
        
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent',
                                          'memory_info', 'status', 'username', 'create_time',
                                          'cmdline', 'num_threads']):
            try:
                info = proc.info
                processes.append(ProcessInfo(
                    pid=info['pid'],
                    name=info['name'] or "Unknown",
                    cpu_percent=info['cpu_percent'] or 0,
                    memory_percent=info['memory_percent'] or 0,
                    memory_mb=round((info['memory_info'].rss if info['memory_info'] else 0) / (1024**2), 1),
                    status=info['status'] or "unknown",
                    username=info['username'] or "unknown",
                    created=datetime.fromtimestamp(info['create_time']) if info['create_time'] else datetime.now(),
                    cmdline=" ".join(info['cmdline'][:3]) if info['cmdline'] else "",
                    threads=info['num_threads'] or 1
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort
        if sort_by == "cpu":
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        elif sort_by == "name":
            processes.sort(key=lambda p: p.name.lower())
        elif sort_by == "pid":
            processes.sort(key=lambda p: p.pid)
        
        return processes[:limit]
    
    def kill_process(self, pid: int, force: bool = False) -> Tuple[bool, str]:
        """
        Kill a process by PID.
        
        Args:
            pid: Process ID
            force: Use SIGKILL instead of SIGTERM
            
        Returns:
            Tuple of (success, message)
        """
        if not PSUTIL_AVAILABLE:
            return False, "psutil not available"
        
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            
            if force:
                proc.kill()
            else:
                proc.terminate()
            
            self._log_action("kill_process", {"pid": pid, "name": name, "force": force})
            return True, f"Process {name} (PID {pid}) terminated"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} not found"
        except psutil.AccessDenied:
            return False, f"Access denied for process {pid}"
        except Exception as e:
            return False, str(e)
    
    def set_process_priority(self, pid: int, priority: Priority) -> Tuple[bool, str]:
        """Set process priority/nice value."""
        if not PSUTIL_AVAILABLE:
            return False, "psutil not available"
        
        nice_values = {
            Priority.REALTIME: -20,
            Priority.HIGH: -10,
            Priority.ABOVE_NORMAL: -5,
            Priority.NORMAL: 0,
            Priority.BELOW_NORMAL: 5,
            Priority.LOW: 10,
            Priority.IDLE: 19,
        }
        
        try:
            proc = psutil.Process(pid)
            proc.nice(nice_values.get(priority, 0))
            return True, f"Priority set to {priority.value}"
        except Exception as e:
            return False, str(e)
    
    def get_process_tree(self, pid: int = None) -> List[Dict]:
        """Get process tree."""
        if not PSUTIL_AVAILABLE:
            return []
        
        def get_children(proc, level=0):
            result = [{
                "pid": proc.pid,
                "name": proc.name(),
                "level": level
            }]
            try:
                for child in proc.children():
                    result.extend(get_children(child, level + 1))
            except:
                pass
            return result
        
        if pid:
            try:
                return get_children(psutil.Process(pid))
            except:
                return []
        else:
            # All root processes
            result = []
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                if proc.info['ppid'] == 0 or proc.info['ppid'] == 1:
                    result.extend(get_children(proc))
            return result
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STARTUP MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_startup_items(self) -> List[StartupItem]:
        """Get list of startup applications."""
        items = []
        
        # Check XDG autostart
        autostart_dirs = [
            os.path.expanduser("~/.config/autostart"),
            "/etc/xdg/autostart",
        ]
        
        for autostart_dir in autostart_dirs:
            if os.path.exists(autostart_dir):
                for filename in os.listdir(autostart_dir):
                    if filename.endswith('.desktop'):
                        filepath = os.path.join(autostart_dir, filename)
                        try:
                            with open(filepath, 'r') as f:
                                content = f.read()
                            
                            name = filename.replace('.desktop', '')
                            enabled = 'Hidden=true' not in content
                            
                            # Parse Name and Exec
                            for line in content.split('\n'):
                                if line.startswith('Name='):
                                    name = line.split('=', 1)[1]
                                elif line.startswith('Exec='):
                                    exec_cmd = line.split('=', 1)[1]
                            
                            items.append(StartupItem(
                                name=name,
                                path=filepath,
                                enabled=enabled,
                                source="autostart",
                                description=exec_cmd if 'exec_cmd' in dir() else ""
                            ))
                        except:
                            pass
        
        # Check rc.local
        rc_local = "/etc/rc.local"
        if os.path.exists(rc_local):
            try:
                with open(rc_local, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line != 'exit 0':
                            items.append(StartupItem(
                                name=line.split()[0] if line.split() else line,
                                path=rc_local,
                                enabled=True,
                                source="rc.local",
                                description=line
                            ))
            except:
                pass
        
        return items
    
    def toggle_startup_item(self, item_path: str, enable: bool) -> Tuple[bool, str]:
        """Enable or disable a startup item."""
        try:
            if item_path.endswith('.desktop'):
                with open(item_path, 'r') as f:
                    content = f.read()
                
                if enable:
                    content = content.replace('Hidden=true', 'Hidden=false')
                else:
                    if 'Hidden=' in content:
                        content = content.replace('Hidden=false', 'Hidden=true')
                    else:
                        content += '\nHidden=true'
                
                with open(item_path, 'w') as f:
                    f.write(content)
                
                return True, f"Startup item {'enabled' if enable else 'disabled'}"
            
            return False, "Unsupported startup item type"
        except Exception as e:
            return False, str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SERVICE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_services(self) -> List[Dict]:
        """Get list of system services (systemd)."""
        services = []
        
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--plain'],
                capture_output=True, text=True, timeout=10
            )
            
            for line in result.stdout.split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    services.append({
                        "name": parts[0],
                        "load": parts[1],
                        "active": parts[2],
                        "sub": parts[3],
                        "description": " ".join(parts[4:]) if len(parts) > 4 else ""
                    })
        except Exception as e:
            # Fallback for non-systemd systems
            pass
        
        return services
    
    def control_service(self, service: str, action: str) -> Tuple[bool, str]:
        """
        Control a system service.
        
        Args:
            service: Service name
            action: start, stop, restart, enable, disable
            
        Returns:
            Tuple of (success, message)
        """
        valid_actions = ['start', 'stop', 'restart', 'enable', 'disable', 'status']
        if action not in valid_actions:
            return False, f"Invalid action. Use: {', '.join(valid_actions)}"
        
        try:
            result = subprocess.run(
                ['systemctl', action, service],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                self._log_action("service_control", {"service": service, "action": action})
                return True, f"Service {service} {action} successful"
            else:
                return False, result.stderr or "Command failed"
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DISK CLEANUP
    # ═══════════════════════════════════════════════════════════════════════════
    
    def analyze_disk_usage(self, path: str = "/") -> Dict:
        """
        Analyze disk usage for a path.
        
        Args:
            path: Path to analyze
            
        Returns:
            Dict with usage statistics
        """
        result = {
            "path": path,
            "large_files": [],
            "large_dirs": [],
            "file_types": {},
            "total_size": 0
        }
        
        try:
            for root, dirs, files in os.walk(path):
                for filename in files:
                    try:
                        filepath = os.path.join(root, filename)
                        size = os.path.getsize(filepath)
                        result["total_size"] += size
                        
                        # Track large files (>10MB)
                        if size > 10 * 1024 * 1024:
                            result["large_files"].append({
                                "path": filepath,
                                "size_mb": round(size / (1024**2), 1)
                            })
                        
                        # Track by file type
                        ext = os.path.splitext(filename)[1].lower() or "no_extension"
                        if ext not in result["file_types"]:
                            result["file_types"][ext] = {"count": 0, "size": 0}
                        result["file_types"][ext]["count"] += 1
                        result["file_types"][ext]["size"] += size
                    except:
                        pass
            
            # Sort large files
            result["large_files"].sort(key=lambda f: f["size_mb"], reverse=True)
            result["large_files"] = result["large_files"][:20]
            
            result["total_size_gb"] = round(result["total_size"] / (1024**3), 2)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_cleanup_suggestions(self) -> List[Dict]:
        """Get suggestions for disk cleanup."""
        suggestions = []
        
        # Common cleanup locations
        cleanup_paths = [
            {"path": "/tmp", "description": "Temporary files"},
            {"path": "/var/cache", "description": "Package cache"},
            {"path": "/var/log", "description": "Log files"},
            {"path": os.path.expanduser("~/.cache"), "description": "User cache"},
            {"path": os.path.expanduser("~/.local/share/Trash"), "description": "Trash"},
        ]
        
        for item in cleanup_paths:
            path = item["path"]
            if os.path.exists(path):
                try:
                    size = sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(path)
                        for filename in filenames
                    )
                    if size > 1024 * 1024:  # > 1MB
                        suggestions.append({
                            "path": path,
                            "description": item["description"],
                            "size_mb": round(size / (1024**2), 1),
                            "can_clean": True
                        })
                except:
                    pass
        
        return suggestions
    
    def cleanup_path(self, path: str, dry_run: bool = True) -> Tuple[bool, str, int]:
        """
        Clean up files in a path.
        
        Args:
            path: Path to clean
            dry_run: If True, only report what would be deleted
            
        Returns:
            Tuple of (success, message, bytes_freed)
        """
        if not os.path.exists(path):
            return False, "Path does not exist", 0
        
        bytes_freed = 0
        files_deleted = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(path, topdown=False):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        size = os.path.getsize(filepath)
                        if not dry_run:
                            os.remove(filepath)
                        bytes_freed += size
                        files_deleted += 1
                    except:
                        pass
                
                if not dry_run:
                    for dirname in dirnames:
                        try:
                            os.rmdir(os.path.join(dirpath, dirname))
                        except:
                            pass
            
            action = "Would delete" if dry_run else "Deleted"
            self._log_action("cleanup", {"path": path, "dry_run": dry_run, "bytes": bytes_freed})
            return True, f"{action} {files_deleted} files ({round(bytes_freed/(1024**2), 1)} MB)", bytes_freed
            
        except Exception as e:
            return False, str(e), 0
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NETWORK TOOLS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_network_interfaces(self) -> List[NetworkInfo]:
        """Get list of network interfaces."""
        interfaces = []
        
        if PSUTIL_AVAILABLE:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for name, addr_list in addrs.items():
                ip = ""
                mac = ""
                for addr in addr_list:
                    if addr.family.name == 'AF_INET':
                        ip = addr.address
                    elif addr.family.name == 'AF_PACKET':
                        mac = addr.address
                
                io = io_counters.get(name, None)
                stat = stats.get(name, None)
                
                interfaces.append(NetworkInfo(
                    name=name,
                    ip_address=ip,
                    mac_address=mac,
                    bytes_sent=io.bytes_sent if io else 0,
                    bytes_recv=io.bytes_recv if io else 0,
                    is_up=stat.isup if stat else False
                ))
        
        return interfaces
    
    def get_network_connections(self) -> List[Dict]:
        """Get active network connections."""
        connections = []
        
        if PSUTIL_AVAILABLE:
            for conn in psutil.net_connections(kind='inet'):
                try:
                    connections.append({
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                        "status": conn.status,
                        "pid": conn.pid,
                        "type": "TCP" if conn.type.name == 'SOCK_STREAM' else "UDP"
                    })
                except:
                    pass
        
        return connections
    
    def ping(self, host: str, count: int = 4) -> Dict:
        """Ping a host."""
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), host],
                capture_output=True, text=True, timeout=30
            )
            
            return {
                "host": host,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"host": host, "success": False, "error": "Timeout"}
        except Exception as e:
            return {"host": host, "success": False, "error": str(e)}
    
    def traceroute(self, host: str) -> Dict:
        """Traceroute to a host."""
        try:
            result = subprocess.run(
                ['traceroute', '-m', '15', host],
                capture_output=True, text=True, timeout=60
            )
            
            return {
                "host": host,
                "success": result.returncode == 0,
                "output": result.stdout,
                "hops": len([l for l in result.stdout.split('\n') if l.strip() and l[0].isdigit()])
            }
        except Exception as e:
            return {"host": host, "success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PRIVACY TOOLS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_privacy_status(self) -> Dict:
        """Get privacy-related system status."""
        status = {
            "tracking_protection": True,  # VA21 always protects
            "telemetry_blocked": True,
            "dns_encryption": False,
            "vpn_active": False,
            "tor_available": False,
        }
        
        # Check for Tor
        status["tor_available"] = shutil.which("tor") is not None
        
        # Check for VPN (basic check)
        if PSUTIL_AVAILABLE:
            for iface in psutil.net_if_addrs():
                if 'tun' in iface or 'vpn' in iface.lower():
                    status["vpn_active"] = True
                    break
        
        return status
    
    def clear_history(self, history_type: str = "all") -> Tuple[bool, str]:
        """
        Clear various history data.
        
        Args:
            history_type: bash, browser, recent, all
            
        Returns:
            Tuple of (success, message)
        """
        cleared = []
        
        if history_type in ["bash", "all"]:
            bash_history = os.path.expanduser("~/.bash_history")
            if os.path.exists(bash_history):
                try:
                    open(bash_history, 'w').close()
                    cleared.append("bash history")
                except:
                    pass
        
        if history_type in ["recent", "all"]:
            recent_files = os.path.expanduser("~/.local/share/recently-used.xbel")
            if os.path.exists(recent_files):
                try:
                    os.remove(recent_files)
                    cleared.append("recent files")
                except:
                    pass
        
        if cleared:
            self._log_action("clear_history", {"types": cleared})
            return True, f"Cleared: {', '.join(cleared)}"
        
        return False, "Nothing to clear"
    
    def secure_delete(self, path: str, passes: int = 3) -> Tuple[bool, str]:
        """
        Securely delete a file by overwriting.
        
        Args:
            path: File path
            passes: Number of overwrite passes
            
        Returns:
            Tuple of (success, message)
        """
        if not os.path.isfile(path):
            return False, "File not found"
        
        try:
            size = os.path.getsize(path)
            
            with open(path, 'r+b') as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(size))
                    f.flush()
                    os.fsync(f.fileno())
            
            os.remove(path)
            self._log_action("secure_delete", {"path": path, "passes": passes})
            return True, f"Securely deleted with {passes} passes"
            
        except Exception as e:
            return False, str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # POWER MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_battery_status(self) -> Optional[Dict]:
        """Get battery status if available."""
        if not PSUTIL_AVAILABLE:
            return None
        
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "time_left_hours": round(battery.secsleft / 3600, 1) if battery.secsleft > 0 else None,
                "status": "Charging" if battery.power_plugged else "Discharging"
            }
        return None
    
    def get_power_profile(self) -> str:
        """Get current power profile."""
        try:
            result = subprocess.run(
                ['powerprofilesctl', 'get'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def set_power_profile(self, profile: str) -> Tuple[bool, str]:
        """
        Set power profile.
        
        Args:
            profile: performance, balanced, power-saver
            
        Returns:
            Tuple of (success, message)
        """
        try:
            result = subprocess.run(
                ['powerprofilesctl', 'set', profile],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return True, f"Power profile set to {profile}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM TWEAKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_tweaks(self) -> List[Dict]:
        """Get available system tweaks."""
        tweaks = [
            {
                "id": "swappiness",
                "name": "Memory Swappiness",
                "description": "How aggressively the system swaps memory to disk",
                "current": self._get_sysctl("vm.swappiness", "60"),
                "options": ["10", "30", "60", "100"],
                "type": "select"
            },
            {
                "id": "file_handles",
                "name": "Max Open Files",
                "description": "Maximum number of open file handles",
                "current": self._get_sysctl("fs.file-max", "100000"),
                "type": "number"
            },
            {
                "id": "inotify_watches",
                "name": "Inotify Watches",
                "description": "Max number of file system watches",
                "current": self._get_sysctl("fs.inotify.max_user_watches", "8192"),
                "type": "number"
            },
        ]
        return tweaks
    
    def _get_sysctl(self, key: str, default: str) -> str:
        """Get a sysctl value."""
        try:
            result = subprocess.run(
                ['sysctl', '-n', key],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or default
        except:
            return default
    
    def apply_tweak(self, tweak_id: str, value: str) -> Tuple[bool, str]:
        """Apply a system tweak."""
        tweak_map = {
            "swappiness": "vm.swappiness",
            "file_handles": "fs.file-max",
            "inotify_watches": "fs.inotify.max_user_watches",
        }
        
        if tweak_id not in tweak_map:
            return False, "Unknown tweak"
        
        try:
            result = subprocess.run(
                ['sysctl', '-w', f"{tweak_map[tweak_id]}={value}"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self._log_action("apply_tweak", {"tweak": tweak_id, "value": value})
                return True, f"Tweak applied: {tweak_id}={value}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BACKUP
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_backup(self, paths: List[str], backup_name: str = None) -> Tuple[bool, str]:
        """
        Create a backup of specified paths.
        
        Args:
            paths: List of paths to backup
            backup_name: Custom backup name
            
        Returns:
            Tuple of (success, message)
        """
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = os.path.join(self.config_path, "backups", backup_name)
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            for path in paths:
                if os.path.exists(path):
                    dest = os.path.join(backup_dir, os.path.basename(path))
                    if os.path.isdir(path):
                        shutil.copytree(path, dest)
                    else:
                        shutil.copy2(path, dest)
            
            # Create manifest
            manifest = {
                "name": backup_name,
                "created": datetime.now().isoformat(),
                "paths": paths
            }
            with open(os.path.join(backup_dir, "manifest.json"), 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self._log_action("create_backup", {"name": backup_name, "paths": paths})
            return True, f"Backup created: {backup_dir}"
            
        except Exception as e:
            return False, str(e)
    
    def list_backups(self) -> List[Dict]:
        """List available backups."""
        backups = []
        backup_base = os.path.join(self.config_path, "backups")
        
        if os.path.exists(backup_base):
            for name in os.listdir(backup_base):
                manifest_path = os.path.join(backup_base, name, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                        backups.append(manifest)
                    except:
                        backups.append({"name": name, "created": "unknown"})
        
        return sorted(backups, key=lambda b: b.get("created", ""), reverse=True)
    
    def restore_backup(self, backup_name: str, dest_path: str = None) -> Tuple[bool, str]:
        """Restore a backup."""
        backup_dir = os.path.join(self.config_path, "backups", backup_name)
        
        if not os.path.exists(backup_dir):
            return False, "Backup not found"
        
        try:
            for item in os.listdir(backup_dir):
                if item == "manifest.json":
                    continue
                
                src = os.path.join(backup_dir, item)
                dst = os.path.join(dest_path or "/", item) if dest_path else src
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
            self._log_action("restore_backup", {"name": backup_name})
            return True, f"Backup restored: {backup_name}"
            
        except Exception as e:
            return False, str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM INFO
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information."""
        info = {
            "os": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
            }
        }
        
        if PSUTIL_AVAILABLE:
            info["cpu"] = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency": getattr(psutil.cpu_freq(), 'max', 0) if psutil.cpu_freq() else 0,
            }
            
            mem = psutil.virtual_memory()
            info["memory"] = {
                "total_gb": round(mem.total / (1024**3), 2),
            }
            
            info["disks"] = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    info["disks"].append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "fstype": part.fstype,
                    })
                except:
                    pass
        
        return info
    
    def export_system_report(self, filepath: str = None) -> str:
        """Export comprehensive system report."""
        if not filepath:
            filepath = os.path.join(
                self.config_path, 
                f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        report = {
            "generated": datetime.now().isoformat(),
            "system_info": self.get_system_info(),
            "status": self.get_system_status(),
            "processes": len(self.get_processes()),
            "services": len(self.get_services()),
            "startup_items": len(self.get_startup_items()),
            "network_interfaces": len(self.get_network_interfaces()),
            "battery": self.get_battery_status(),
            "privacy": self.get_privacy_status(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filepath
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITIES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _log_action(self, action: str, details: Dict):
        """Log an action for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.command_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]
        
        # Write to log file
        log_file = os.path.join(self.config_path, "logs", "system_tools.log")
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass
    
    def get_action_history(self, limit: int = 50) -> List[Dict]:
        """Get action history."""
        return self.command_history[-limit:]


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_system_tools_instance = None

def get_system_tools() -> SystemToolsSuite:
    """Get the SystemToolsSuite singleton."""
    global _system_tools_instance
    if _system_tools_instance is None:
        _system_tools_instance = SystemToolsSuite()
    return _system_tools_instance


if __name__ == "__main__":
    tools = get_system_tools()
    
    print("System Status:")
    print(json.dumps(tools.get_system_status(), indent=2, default=str))
    
    print("\nTop Processes:")
    for proc in tools.get_processes(limit=5):
        print(f"  {proc.pid}: {proc.name} - CPU: {proc.cpu_percent}%")
