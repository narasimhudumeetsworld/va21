"""
Backup API Socket.IO Namespace

This module provides the Socket.IO namespace for the backup manager,
handling version history, restore operations, and configuration.
"""

from flask_socketio import Namespace, emit
from auto_backup_manager import AutoBackupManager, BackupConfig


class BackupNamespace(Namespace):
    """Socket.IO namespace for backup management."""
    
    def __init__(self, namespace='/backup'):
        super().__init__(namespace)
        self.backup_manager = AutoBackupManager()
        self.backup_manager.start_auto_backup()
    
    def on_connect(self):
        """Handle client connection."""
        print(f'[Backup] Client connected')
        emit('connected', {'status': 'ok'})
    
    def on_disconnect(self):
        """Handle client disconnection."""
        print(f'[Backup] Client disconnected')
    
    def on_get_versions(self, data=None):
        """Get list of backup versions."""
        try:
            versions = self.backup_manager.export_version_list()
            emit('versions_list', versions)
        except Exception as e:
            emit('error', {'message': f'Failed to get versions: {str(e)}'})
    
    def on_get_stats(self, data=None):
        """Get backup storage statistics."""
        try:
            stats = self.backup_manager.get_storage_stats()
            emit('stats_update', stats)
        except Exception as e:
            emit('error', {'message': f'Failed to get stats: {str(e)}'})
    
    def on_get_config(self, data=None):
        """Get backup configuration."""
        try:
            config = {
                'enabled': self.backup_manager.config.enabled,
                'interval_minutes': self.backup_manager.config.interval_minutes,
                'max_versions': self.backup_manager.config.max_versions,
                'max_storage_mb': self.backup_manager.config.max_storage_mb,
                'compress_backups': self.backup_manager.config.compress_backups,
                'backup_on_startup': self.backup_manager.config.backup_on_startup,
                'backup_before_reset': self.backup_manager.config.backup_before_reset,
                'auto_cleanup': self.backup_manager.config.auto_cleanup,
                'retention_days': self.backup_manager.config.retention_days
            }
            emit('config_update', config)
        except Exception as e:
            emit('error', {'message': f'Failed to get config: {str(e)}'})
    
    def on_update_config(self, data):
        """Update backup configuration."""
        try:
            if not data:
                return
            
            config = self.backup_manager.config
            
            if 'enabled' in data:
                config.enabled = data['enabled']
                if data['enabled']:
                    self.backup_manager.start_auto_backup()
                else:
                    self.backup_manager.stop_auto_backup()
            
            if 'interval_minutes' in data:
                config.interval_minutes = max(5, min(1440, data['interval_minutes']))
            
            if 'max_versions' in data:
                config.max_versions = max(5, min(200, data['max_versions']))
            
            if 'max_storage_mb' in data:
                config.max_storage_mb = max(100, min(5000, data['max_storage_mb']))
            
            if 'compress_backups' in data:
                config.compress_backups = data['compress_backups']
            
            if 'backup_on_startup' in data:
                config.backup_on_startup = data['backup_on_startup']
            
            if 'backup_before_reset' in data:
                config.backup_before_reset = data['backup_before_reset']
            
            if 'auto_cleanup' in data:
                config.auto_cleanup = data['auto_cleanup']
            
            if 'retention_days' in data:
                config.retention_days = max(1, min(365, data['retention_days']))
            
            emit('config_update', {
                'enabled': config.enabled,
                'interval_minutes': config.interval_minutes,
                'max_versions': config.max_versions,
                'max_storage_mb': config.max_storage_mb,
                'compress_backups': config.compress_backups,
                'backup_on_startup': config.backup_on_startup,
                'backup_before_reset': config.backup_before_reset,
                'auto_cleanup': config.auto_cleanup,
                'retention_days': config.retention_days
            })
            
        except Exception as e:
            emit('error', {'message': f'Failed to update config: {str(e)}'})
    
    def on_create_backup(self, data):
        """Create a new backup."""
        try:
            description = data.get('description', '')
            backup_type = data.get('backup_type', 'manual')
            components = data.get('components')
            
            version = self.backup_manager.create_backup(
                description=description,
                backup_type=backup_type,
                components=components
            )
            
            if version:
                emit('backup_created', {
                    'version_id': version.version_id,
                    'timestamp': version.timestamp.isoformat(),
                    'description': version.description,
                    'size_bytes': version.size_bytes
                })
            else:
                emit('error', {'message': 'Failed to create backup'})
                
        except Exception as e:
            emit('error', {'message': f'Failed to create backup: {str(e)}'})
    
    def on_create_pre_reset_backup(self, data=None):
        """Create a pre-reset safety backup."""
        try:
            version = self.backup_manager.create_pre_reset_backup()
            
            if version:
                emit('backup_created', {
                    'version_id': version.version_id,
                    'timestamp': version.timestamp.isoformat(),
                    'description': version.description,
                    'size_bytes': version.size_bytes,
                    'backup_type': 'pre-reset'
                })
            else:
                emit('error', {'message': 'Failed to create pre-reset backup'})
                
        except Exception as e:
            emit('error', {'message': f'Failed to create pre-reset backup: {str(e)}'})
    
    def on_restore_backup(self, data):
        """Restore from a backup version."""
        try:
            version_id = data.get('version_id')
            components = data.get('components')
            
            if not version_id:
                emit('error', {'message': 'Version ID required'})
                return
            
            success = self.backup_manager.restore_backup(version_id, components)
            
            if success:
                emit('restore_complete', {'version_id': version_id})
            else:
                emit('error', {'message': f'Failed to restore backup {version_id}'})
                
        except Exception as e:
            emit('error', {'message': f'Failed to restore backup: {str(e)}'})
    
    def on_delete_version(self, data):
        """Delete a backup version."""
        try:
            version_id = data.get('version_id')
            
            if not version_id:
                emit('error', {'message': 'Version ID required'})
                return
            
            success = self.backup_manager.delete_version(version_id)
            
            if success:
                emit('version_deleted', {'version_id': version_id})
            else:
                emit('error', {'message': f'Failed to delete version {version_id}'})
                
        except Exception as e:
            emit('error', {'message': f'Failed to delete version: {str(e)}'})
