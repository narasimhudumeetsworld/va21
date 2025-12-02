"""
System Stats Socket.IO Namespace

This module provides the Socket.IO namespace for system statistics,
health monitoring, and dashboard data.
"""

import os
import time
import importlib.util
from datetime import datetime
from flask_socketio import Namespace, emit

# Check if psutil is available
HAS_PSUTIL = importlib.util.find_spec("psutil") is not None
if HAS_PSUTIL:
    import psutil


class StatsNamespace(Namespace):
    """Socket.IO namespace for system statistics."""
    
    def __init__(self, namespace='/stats', orchestrator=None, self_healing=None, backup_manager=None):
        super().__init__(namespace)
        self.orchestrator = orchestrator
        self.self_healing = self_healing
        self.backup_manager = backup_manager
        self.start_time = time.time()
        self.request_count = 0
    
    def on_connect(self):
        """Handle client connection."""
        print(f'[Stats] Client connected')
        emit('connected', {'status': 'ok'})
    
    def on_disconnect(self):
        """Handle client disconnection."""
        print(f'[Stats] Client disconnected')
    
    def on_get_all_stats(self, data=None):
        """Get all system statistics."""
        self._emit_system_stats()
        self._emit_health_status()
        self._emit_backup_stats()
        self._emit_agent_status()
        self._emit_security_alerts()
    
    def _emit_system_stats(self):
        """Emit system resource statistics."""
        try:
            if HAS_PSUTIL:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                stats = {
                    'cpu_percent': cpu_percent,
                    'memory': {
                        'percent': memory.percent,
                        'used_gb': round(memory.used / (1024**3), 2),
                        'total_gb': round(memory.total / (1024**3), 2),
                        'available_gb': round(memory.available / (1024**3), 2)
                    },
                    'disk': {
                        'percent': round((disk.used / disk.total) * 100, 1),
                        'used_gb': round(disk.used / (1024**3), 0),
                        'total_gb': round(disk.total / (1024**3), 0),
                        'free_gb': round(disk.free / (1024**3), 0)
                    },
                    'uptime_hours': round((time.time() - self.start_time) / 3600, 2),
                    'active_sessions': self._count_active_sessions(),
                    'requests_per_minute': self._calculate_rpm()
                }
            else:
                # Fallback when psutil is not available
                stats = {
                    'cpu_percent': 0,
                    'memory': {'percent': 0, 'used_gb': 0, 'total_gb': 0, 'available_gb': 0},
                    'disk': {'percent': 0, 'used_gb': 0, 'total_gb': 0, 'free_gb': 0},
                    'uptime_hours': round((time.time() - self.start_time) / 3600, 2),
                    'active_sessions': 0,
                    'requests_per_minute': 0
                }
            
            emit('system_stats', stats)
            
        except Exception as e:
            print(f'[Stats] Error getting system stats: {e}')
            emit('system_stats', {})
    
    def _emit_health_status(self):
        """Emit health check status."""
        try:
            if self.self_healing:
                status = self.self_healing.get_health_status()
            else:
                # Default healthy status
                status = {
                    'overall_status': 'healthy',
                    'checks': {
                        'memory_usage': {'status': 'healthy', 'last_check': datetime.now().isoformat(), 'consecutive_failures': 0},
                        'disk_space': {'status': 'healthy', 'last_check': datetime.now().isoformat(), 'consecutive_failures': 0},
                        'backend_health': {'status': 'healthy', 'last_check': datetime.now().isoformat(), 'consecutive_failures': 0},
                        'file_integrity': {'status': 'healthy', 'last_check': datetime.now().isoformat(), 'consecutive_failures': 0}
                    }
                }
            
            emit('health_status', status)
            
        except Exception as e:
            print(f'[Stats] Error getting health status: {e}')
            emit('health_status', {'overall_status': 'unknown', 'checks': {}})
    
    def _emit_backup_stats(self):
        """Emit backup statistics."""
        try:
            if self.backup_manager:
                stats = self.backup_manager.get_storage_stats()
            else:
                stats = {
                    'total_versions': 0,
                    'total_size_mb': 0,
                    'max_storage_mb': 500,
                    'storage_used_percent': 0,
                    'auto_backup_enabled': True,
                    'newest_backup': None
                }
            
            emit('backup_stats', stats)
            
        except Exception as e:
            print(f'[Stats] Error getting backup stats: {e}')
            emit('backup_stats', {})
    
    def _emit_agent_status(self):
        """Emit AI agent status."""
        try:
            if self.orchestrator:
                agents = self.orchestrator.get_all_agent_statuses()
            else:
                # Default agent status
                agents = [
                    {'agent_id': 'guardian', 'type': 'security', 'status': 'idle', 'current_task': None},
                    {'agent_id': 'researcher', 'type': 'research', 'status': 'idle', 'current_task': None},
                    {'agent_id': 'coder', 'type': 'coding', 'status': 'idle', 'current_task': None},
                    {'agent_id': 'planner', 'type': 'planning', 'status': 'idle', 'current_task': None}
                ]
            
            emit('agent_status', agents)
            
        except Exception as e:
            print(f'[Stats] Error getting agent status: {e}')
            emit('agent_status', [])
    
    def _emit_security_alerts(self):
        """Emit security alerts."""
        try:
            # In a real implementation, this would fetch from a security log
            alerts = []
            
            emit('security_alerts', alerts)
            
        except Exception as e:
            print(f'[Stats] Error getting security alerts: {e}')
            emit('security_alerts', [])
    
    def _count_active_sessions(self):
        """Count active WebSocket sessions."""
        return 1  # Placeholder
    
    def _calculate_rpm(self):
        """Calculate requests per minute."""
        return 0  # Placeholder
    
    def increment_request_count(self):
        """Increment the request counter."""
        self.request_count += 1
