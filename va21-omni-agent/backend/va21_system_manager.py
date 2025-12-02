"""
VA21 Research OS - System Manager
Manages the overall VA21 Research OS environment, integrating
all components including kernel guardian, self-healing, and orchestrator.
"""

import os
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class OSState(Enum):
    """Operating system states."""
    SHUTDOWN = "shutdown"
    BOOTING = "booting"
    RUNNING = "running"
    DEGRADED = "degraded"
    LOCKDOWN = "lockdown"
    MAINTENANCE = "maintenance"


@dataclass
class SystemService:
    """Represents a system service."""
    name: str
    description: str
    status: str = "stopped"
    auto_start: bool = True
    critical: bool = False
    start_func: Optional[Callable] = None
    stop_func: Optional[Callable] = None


@dataclass
class Application:
    """Represents an installed application."""
    app_id: str
    name: str
    icon: str
    description: str
    category: str
    version: str
    path: str
    is_running: bool = False
    is_pinned: bool = False


class VA21SystemManager:
    """
    VA21 Research OS System Manager
    
    This class provides the central management for the VA21 Research OS,
    coordinating all system components and providing an OS-like experience.
    
    Features:
    - Boot sequence management
    - Service management (start, stop, restart)
    - Application registry
    - System state management
    - Resource monitoring integration
    - Security status dashboard
    - Desktop environment simulation
    """
    
    VERSION = "1.0.0"
    OS_NAME = "VA21 Research OS"
    
    def __init__(self, config_path: str = "data/va21_os"):
        self.config_path = config_path
        os.makedirs(config_path, exist_ok=True)
        
        # OS State
        self.state = OSState.SHUTDOWN
        self.boot_time: Optional[datetime] = None
        
        # Components
        self.kernel_guardian = None
        self.self_healing = None
        self.orchestrator = None
        self.local_llm = None
        
        # Services
        self.services: Dict[str, SystemService] = {}
        
        # Applications
        self.applications: Dict[str, Application] = {}
        
        # Desktop state
        self.desktop_config = {
            "theme": "dark",
            "wallpaper": "default",
            "show_dock": True,
            "dock_position": "bottom",
            "show_status_bar": True,
            "show_desktop_icons": True
        }
        
        # Notification queue
        self.notifications: List[Dict] = []
        
        # Event callbacks
        self.state_change_callbacks: List[Callable] = []
        
        # Initialize default applications
        self._initialize_applications()
        
        # Initialize default services
        self._initialize_services()
    
    def _initialize_applications(self):
        """Initialize the default application registry."""
        default_apps = [
            Application(
                app_id="terminal",
                name="Terminal",
                icon="💻",
                description="Sandboxed terminal emulator",
                category="System",
                version="1.0.0",
                path="/terminal",
                is_pinned=True
            ),
            Application(
                app_id="research_center",
                name="Research Center",
                icon="🔬",
                description="Research Command Center with knowledge graph",
                category="Research",
                version="1.0.0",
                path="/research",
                is_pinned=True
            ),
            Application(
                app_id="guardian_dashboard",
                name="Guardian Dashboard",
                icon="🛡️",
                description="Security monitoring and threat analysis",
                category="Security",
                version="1.0.0",
                path="/guardian",
                is_pinned=True
            ),
            Application(
                app_id="browser",
                name="Secure Browser",
                icon="🌐",
                description="Air-gapped secure web browser",
                category="Internet",
                version="1.0.0",
                path="/browser",
                is_pinned=True
            ),
            Application(
                app_id="settings",
                name="System Settings",
                icon="⚙️",
                description="VA21 OS configuration",
                category="System",
                version="1.0.0",
                path="/settings",
                is_pinned=False
            ),
            Application(
                app_id="knowledge_vault",
                name="Knowledge Vault",
                icon="📚",
                description="Obsidian-style knowledge management",
                category="Research",
                version="1.0.0",
                path="/vault",
                is_pinned=True
            ),
            Application(
                app_id="process_monitor",
                name="Process Monitor",
                icon="📊",
                description="System resource and process monitoring",
                category="System",
                version="1.0.0",
                path="/processes",
                is_pinned=False
            ),
            Application(
                app_id="threat_intel",
                name="Threat Intelligence",
                icon="🔍",
                description="Security threat intelligence feeds",
                category="Security",
                version="1.0.0",
                path="/threats",
                is_pinned=False
            ),
            Application(
                app_id="ai_orchestrator",
                name="AI Orchestrator",
                icon="🤖",
                description="Multi-agent AI coordination",
                category="AI",
                version="1.0.0",
                path="/orchestrator",
                is_pinned=True
            ),
            Application(
                app_id="workflow_engine",
                name="Workflow Engine",
                icon="⚡",
                description="Automated workflow management",
                category="Automation",
                version="1.0.0",
                path="/workflows",
                is_pinned=False
            ),
            Application(
                app_id="file_manager",
                name="File Manager",
                icon="📁",
                description="Secure file browser",
                category="System",
                version="1.0.0",
                path="/files",
                is_pinned=False
            ),
            Application(
                app_id="backup_manager",
                name="Backup Manager",
                icon="💾",
                description="System backup and recovery",
                category="System",
                version="1.0.0",
                path="/backup",
                is_pinned=False
            )
        ]
        
        for app in default_apps:
            self.applications[app.app_id] = app
    
    def _initialize_services(self):
        """Initialize default system services."""
        self.services = {
            "kernel_guardian": SystemService(
                name="Kernel Guardian",
                description="Kernel-level security protection",
                auto_start=True,
                critical=True
            ),
            "self_healing": SystemService(
                name="Self Healing",
                description="Automatic system recovery",
                auto_start=True,
                critical=True
            ),
            "orchestrator": SystemService(
                name="AI Orchestrator",
                description="Multi-agent AI coordination",
                auto_start=True,
                critical=False
            ),
            "threat_intel": SystemService(
                name="Threat Intelligence",
                description="Security feed aggregation",
                auto_start=True,
                critical=False
            ),
            "backup_service": SystemService(
                name="Backup Service",
                description="Automated backup system",
                auto_start=True,
                critical=False
            ),
            "vault_sync": SystemService(
                name="Vault Sync",
                description="Knowledge vault synchronization",
                auto_start=True,
                critical=False
            )
        }
    
    def set_components(self, kernel_guardian=None, self_healing=None, 
                       orchestrator=None, local_llm=None):
        """Set the system components."""
        self.kernel_guardian = kernel_guardian
        self.self_healing = self_healing
        self.orchestrator = orchestrator
        self.local_llm = local_llm
        
        # Update service functions
        if kernel_guardian:
            self.services["kernel_guardian"].start_func = kernel_guardian.start_monitoring
            self.services["kernel_guardian"].stop_func = kernel_guardian.stop_monitoring
        
        if self_healing:
            self.services["self_healing"].start_func = self_healing.start_monitoring
            self.services["self_healing"].stop_func = self_healing.stop_monitoring
        
        if orchestrator:
            self.services["orchestrator"].start_func = orchestrator.start
            self.services["orchestrator"].stop_func = orchestrator.stop
    
    def boot(self) -> Dict:
        """
        Boot the VA21 Research OS.
        
        Returns:
            Boot result dictionary
        """
        boot_log = []
        self.state = OSState.BOOTING
        self.boot_time = datetime.now()
        
        def log(msg: str):
            entry = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
            boot_log.append(entry)
            print(f"[VA21-OS] {entry}")
        
        log("=" * 60)
        log(f"🚀 {self.OS_NAME} v{self.VERSION}")
        log("=" * 60)
        
        try:
            # Boot kernel guardian first
            log("Initializing Kernel Guardian...")
            if self.kernel_guardian:
                success, kernel_log = self.kernel_guardian.boot()
                if success:
                    self.services["kernel_guardian"].status = "running"
                    log("✅ Kernel Guardian: ONLINE")
                else:
                    self.services["kernel_guardian"].status = "error"
                    log("❌ Kernel Guardian: FAILED")
            else:
                log("⚠️ Kernel Guardian: NOT AVAILABLE")
            
            # Start auto-start services
            log("Starting system services...")
            for service_id, service in self.services.items():
                if service.auto_start and service.start_func:
                    try:
                        service.start_func()
                        service.status = "running"
                        log(f"  ✅ {service.name}: Started")
                    except Exception as e:
                        service.status = "error"
                        log(f"  ❌ {service.name}: {str(e)}")
            
            # Initialize desktop environment
            log("Initializing desktop environment...")
            self._load_desktop_config()
            log("✅ Desktop environment ready")
            
            # System is now running
            self.state = OSState.RUNNING
            log("=" * 60)
            log(f"✅ {self.OS_NAME} boot complete!")
            log(f"Boot time: {(datetime.now() - self.boot_time).total_seconds():.2f}s")
            log("=" * 60)
            
            # Notify state change
            self._notify_state_change()
            
            return {
                "success": True,
                "state": self.state.value,
                "boot_time": self.boot_time.isoformat(),
                "log": boot_log
            }
            
        except Exception as e:
            self.state = OSState.DEGRADED
            log(f"❌ Boot failed: {str(e)}")
            return {
                "success": False,
                "state": self.state.value,
                "error": str(e),
                "log": boot_log
            }
    
    def shutdown(self) -> Dict:
        """Shutdown the VA21 Research OS."""
        shutdown_log = []
        
        def log(msg: str):
            entry = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
            shutdown_log.append(entry)
            print(f"[VA21-OS] {entry}")
        
        log("Initiating system shutdown...")
        
        # Stop all services in reverse order
        for service_id, service in reversed(list(self.services.items())):
            if service.status == "running" and service.stop_func:
                try:
                    service.stop_func()
                    service.status = "stopped"
                    log(f"✅ {service.name}: Stopped")
                except Exception as e:
                    log(f"⚠️ {service.name}: {str(e)}")
        
        # Shutdown kernel guardian
        if self.kernel_guardian:
            self.kernel_guardian.shutdown()
            log("✅ Kernel Guardian: Shutdown")
        
        # Save desktop config
        self._save_desktop_config()
        
        self.state = OSState.SHUTDOWN
        self.boot_time = None
        
        log("✅ Shutdown complete")
        
        return {
            "success": True,
            "log": shutdown_log
        }
    
    def _load_desktop_config(self):
        """Load desktop configuration."""
        config_file = os.path.join(self.config_path, "desktop.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.desktop_config.update(json.load(f))
        except Exception as e:
            print(f"[VA21-OS] Error loading desktop config: {e}")
    
    def _save_desktop_config(self):
        """Save desktop configuration."""
        config_file = os.path.join(self.config_path, "desktop.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.desktop_config, f, indent=2)
        except Exception as e:
            print(f"[VA21-OS] Error saving desktop config: {e}")
    
    def _notify_state_change(self):
        """Notify all state change callbacks."""
        for callback in self.state_change_callbacks:
            try:
                callback(self.state)
            except Exception as e:
                print(f"[VA21-OS] State change callback error: {e}")
    
    def add_state_change_callback(self, callback: Callable):
        """Add a state change callback."""
        self.state_change_callbacks.append(callback)
    
    def get_status(self) -> Dict:
        """Get current system status."""
        uptime = None
        if self.boot_time:
            uptime = (datetime.now() - self.boot_time).total_seconds()
        
        return {
            "os_name": self.OS_NAME,
            "version": self.VERSION,
            "state": self.state.value,
            "boot_time": self.boot_time.isoformat() if self.boot_time else None,
            "uptime_seconds": uptime,
            "services": {
                sid: {
                    "name": s.name,
                    "status": s.status,
                    "critical": s.critical
                }
                for sid, s in self.services.items()
            },
            "desktop_config": self.desktop_config,
            "notification_count": len(self.notifications)
        }
    
    def get_applications(self, category: str = None, pinned_only: bool = False) -> List[Dict]:
        """Get list of applications."""
        apps = list(self.applications.values())
        
        if category:
            apps = [a for a in apps if a.category == category]
        
        if pinned_only:
            apps = [a for a in apps if a.is_pinned]
        
        return [{
            "app_id": a.app_id,
            "name": a.name,
            "icon": a.icon,
            "description": a.description,
            "category": a.category,
            "version": a.version,
            "path": a.path,
            "is_running": a.is_running,
            "is_pinned": a.is_pinned
        } for a in sorted(apps, key=lambda x: x.name)]
    
    def get_app_categories(self) -> List[str]:
        """Get list of application categories."""
        return sorted(set(a.category for a in self.applications.values()))
    
    def launch_app(self, app_id: str) -> Dict:
        """Launch an application."""
        if app_id not in self.applications:
            return {"success": False, "error": "Application not found"}
        
        app = self.applications[app_id]
        app.is_running = True
        
        return {
            "success": True,
            "app": {
                "app_id": app.app_id,
                "name": app.name,
                "path": app.path
            }
        }
    
    def close_app(self, app_id: str) -> Dict:
        """Close an application."""
        if app_id not in self.applications:
            return {"success": False, "error": "Application not found"}
        
        app = self.applications[app_id]
        app.is_running = False
        
        return {"success": True}
    
    def toggle_app_pin(self, app_id: str) -> Dict:
        """Toggle an application's pinned status."""
        if app_id not in self.applications:
            return {"success": False, "error": "Application not found"}
        
        app = self.applications[app_id]
        app.is_pinned = not app.is_pinned
        
        return {"success": True, "is_pinned": app.is_pinned}
    
    def update_desktop_config(self, config: Dict) -> Dict:
        """Update desktop configuration."""
        self.desktop_config.update(config)
        self._save_desktop_config()
        return {"success": True, "config": self.desktop_config}
    
    def start_service(self, service_id: str) -> Dict:
        """Start a system service."""
        if service_id not in self.services:
            return {"success": False, "error": "Service not found"}
        
        service = self.services[service_id]
        
        if service.status == "running":
            return {"success": False, "error": "Service already running"}
        
        if service.start_func:
            try:
                service.start_func()
                service.status = "running"
                return {"success": True, "status": "running"}
            except Exception as e:
                service.status = "error"
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No start function defined"}
    
    def stop_service(self, service_id: str) -> Dict:
        """Stop a system service."""
        if service_id not in self.services:
            return {"success": False, "error": "Service not found"}
        
        service = self.services[service_id]
        
        if service.status != "running":
            return {"success": False, "error": "Service not running"}
        
        if service.critical:
            return {"success": False, "error": "Cannot stop critical service"}
        
        if service.stop_func:
            try:
                service.stop_func()
                service.status = "stopped"
                return {"success": True, "status": "stopped"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No stop function defined"}
    
    def restart_service(self, service_id: str) -> Dict:
        """Restart a system service."""
        stop_result = self.stop_service(service_id)
        if not stop_result.get("success") and "not running" not in stop_result.get("error", ""):
            return stop_result
        
        return self.start_service(service_id)
    
    def add_notification(self, title: str, message: str, 
                        notification_type: str = "info") -> Dict:
        """Add a system notification."""
        notification = {
            "id": f"notif_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        self.notifications.append(notification)
        
        # Keep only last 100 notifications
        if len(self.notifications) > 100:
            self.notifications = self.notifications[-100:]
        
        return notification
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict]:
        """Get notifications."""
        notifs = self.notifications
        if unread_only:
            notifs = [n for n in notifs if not n["read"]]
        return sorted(notifs, key=lambda x: x["timestamp"], reverse=True)
    
    def mark_notification_read(self, notification_id: str) -> Dict:
        """Mark a notification as read."""
        for notif in self.notifications:
            if notif["id"] == notification_id:
                notif["read"] = True
                return {"success": True}
        return {"success": False, "error": "Notification not found"}
    
    def clear_notifications(self) -> Dict:
        """Clear all notifications."""
        self.notifications = []
        return {"success": True}
    
    def get_resource_usage(self) -> Dict:
        """Get current resource usage from kernel guardian."""
        if self.kernel_guardian:
            return self.kernel_guardian.system_metrics
        return {}
    
    def get_security_status(self) -> Dict:
        """Get current security status."""
        status = {
            "level": "unknown",
            "guardian_active": False,
            "self_healing_active": False,
            "threats_detected": 0,
            "last_scan": None
        }
        
        if self.kernel_guardian:
            kernel_status = self.kernel_guardian.get_status()
            status["level"] = kernel_status.get("security_level", "unknown")
            status["guardian_active"] = kernel_status.get("monitoring", False)
            status["last_scan"] = kernel_status.get("last_scan")
        
        if self.self_healing:
            health = self.self_healing.get_health_status()
            status["self_healing_active"] = True
            status["overall_health"] = health.get("overall_status", "unknown")
        
        return status


# Singleton instance
_system_manager_instance = None


def get_system_manager() -> VA21SystemManager:
    """Get or create the singleton SystemManager instance."""
    global _system_manager_instance
    
    if _system_manager_instance is None:
        _system_manager_instance = VA21SystemManager()
    
    return _system_manager_instance


# Example usage
if __name__ == '__main__':
    print("Testing VA21 System Manager...")
    
    manager = VA21SystemManager()
    
    # Boot the OS
    result = manager.boot()
    print(f"\nBoot result: {json.dumps(result, indent=2)}")
    
    # Get status
    status = manager.get_status()
    print(f"\nStatus: {json.dumps(status, indent=2)}")
    
    # Get applications
    apps = manager.get_applications()
    print(f"\nApplications: {json.dumps(apps, indent=2)}")
    
    # Add notification
    notif = manager.add_notification(
        "Welcome to VA21",
        "Your secure research environment is ready!",
        "success"
    )
    print(f"\nNotification: {json.dumps(notif, indent=2)}")
    
    # Shutdown
    result = manager.shutdown()
    print(f"\nShutdown: {json.dumps(result, indent=2)}")
