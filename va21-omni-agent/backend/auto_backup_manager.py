"""
Auto Backup Manager with Version History

This module provides automatic backup functionality with version control,
allowing users to easily restore their work at any point.
"""

import os
import json
import shutil
import hashlib
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import threading
import time


@dataclass
class BackupVersion:
    """Represents a single backup version."""
    version_id: str
    timestamp: datetime
    description: str
    size_bytes: int
    checksum: str
    backup_type: str  # 'auto', 'manual', 'pre-reset'
    components: List[str]  # List of backed up components
    metadata: Dict = field(default_factory=dict)


@dataclass
class BackupConfig:
    """Configuration for auto backup."""
    enabled: bool = True
    interval_minutes: int = 30
    max_versions: int = 50
    max_storage_mb: int = 500
    compress_backups: bool = True
    backup_on_startup: bool = True
    backup_before_reset: bool = True
    auto_cleanup: bool = True
    retention_days: int = 30


class AutoBackupManager:
    """
    Manages automatic backups with version history for easy restoration.
    
    Features:
    - Automatic periodic backups
    - Manual backup triggers
    - Pre-reset safety backups
    - Version history with metadata
    - Easy point-in-time restoration
    - Incremental backup support
    - Compression for storage efficiency
    - Automatic cleanup of old versions
    """
    
    def __init__(self, backup_dir: str = "data/backups", config: BackupConfig = None):
        self.backup_dir = backup_dir
        self.config = config or BackupConfig()
        self.versions_file = os.path.join(backup_dir, "versions.json")
        self.versions: List[BackupVersion] = []
        
        # Components to backup
        self.backup_sources: Dict[str, str] = {
            'chat_history': 'data/chat_history',
            'research_vault': 'data/research_vault',
            'settings': 'data/settings.json',
            'memory': 'data/long_term_memory',
            'workflows': 'workflows',
            'knowledge_graph': 'data/research_vault/graph',
        }
        
        # Auto backup thread
        self.is_running = False
        self.backup_thread: Optional[threading.Thread] = None
        self.last_backup_time: Optional[datetime] = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize backup directory and load version history."""
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "versions"), exist_ok=True)
        self._load_versions()
        
        if self.config.backup_on_startup and self.config.enabled:
            self.create_backup("Startup backup", backup_type="auto")
    
    def _load_versions(self):
        """Load version history from disk."""
        if os.path.exists(self.versions_file):
            try:
                with open(self.versions_file, 'r') as f:
                    data = json.load(f)
                    self.versions = [
                        BackupVersion(
                            version_id=v['version_id'],
                            timestamp=datetime.fromisoformat(v['timestamp']),
                            description=v['description'],
                            size_bytes=v['size_bytes'],
                            checksum=v['checksum'],
                            backup_type=v['backup_type'],
                            components=v['components'],
                            metadata=v.get('metadata', {})
                        )
                        for v in data.get('versions', [])
                    ]
            except Exception as e:
                print(f"[AutoBackup] Error loading versions: {e}")
                self.versions = []
    
    def _save_versions(self):
        """Save version history to disk."""
        try:
            data = {
                'versions': [
                    {
                        'version_id': v.version_id,
                        'timestamp': v.timestamp.isoformat(),
                        'description': v.description,
                        'size_bytes': v.size_bytes,
                        'checksum': v.checksum,
                        'backup_type': v.backup_type,
                        'components': v.components,
                        'metadata': v.metadata
                    }
                    for v in self.versions
                ],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.versions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[AutoBackup] Error saving versions: {e}")
    
    def add_backup_source(self, name: str, path: str):
        """Add a new source to be backed up."""
        self.backup_sources[name] = path
    
    def remove_backup_source(self, name: str):
        """Remove a backup source."""
        if name in self.backup_sources:
            del self.backup_sources[name]
    
    def create_backup(self, description: str = "", backup_type: str = "manual",
                      components: List[str] = None) -> Optional[BackupVersion]:
        """
        Create a new backup version.
        
        Args:
            description: Human-readable description of the backup
            backup_type: Type of backup ('auto', 'manual', 'pre-reset')
            components: List of components to backup (None = all)
        
        Returns:
            BackupVersion object if successful, None otherwise
        """
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        version_dir = os.path.join(self.backup_dir, "versions", version_id)
        
        try:
            os.makedirs(version_dir, exist_ok=True)
            
            # Determine components to backup
            if components is None:
                components = list(self.backup_sources.keys())
            
            total_size = 0
            backed_up_components = []
            checksums = {}
            
            for component in components:
                if component not in self.backup_sources:
                    continue
                
                source_path = self.backup_sources[component]
                if not os.path.exists(source_path):
                    continue
                
                dest_path = os.path.join(version_dir, component)
                
                if os.path.isfile(source_path):
                    # Backup single file
                    if self.config.compress_backups:
                        dest_path += ".gz"
                        with open(source_path, 'rb') as f_in:
                            with gzip.open(dest_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    else:
                        shutil.copy2(source_path, dest_path)
                    
                    total_size += os.path.getsize(dest_path)
                    checksums[component] = self._calculate_checksum(dest_path)
                    backed_up_components.append(component)
                
                elif os.path.isdir(source_path):
                    # Backup directory
                    if self.config.compress_backups:
                        archive_path = dest_path + ".tar.gz"
                        shutil.make_archive(dest_path, 'gztar', source_path)
                        if os.path.exists(archive_path):
                            total_size += os.path.getsize(archive_path)
                            checksums[component] = self._calculate_checksum(archive_path)
                    else:
                        shutil.copytree(source_path, dest_path)
                        total_size += self._get_dir_size(dest_path)
                        checksums[component] = self._calculate_dir_checksum(dest_path)
                    
                    backed_up_components.append(component)
            
            # Create combined checksum
            combined_checksum = hashlib.sha256(
                ''.join(sorted(checksums.values())).encode()
            ).hexdigest()[:16]
            
            # Create version object
            version = BackupVersion(
                version_id=version_id,
                timestamp=datetime.now(),
                description=description or f"{backup_type.capitalize()} backup",
                size_bytes=total_size,
                checksum=combined_checksum,
                backup_type=backup_type,
                components=backed_up_components,
                metadata={
                    'checksums': checksums,
                    'source_paths': {k: self.backup_sources[k] for k in backed_up_components}
                }
            )
            
            # Save version metadata
            version_meta_path = os.path.join(version_dir, "version.json")
            with open(version_meta_path, 'w') as f:
                json.dump({
                    'version_id': version.version_id,
                    'timestamp': version.timestamp.isoformat(),
                    'description': version.description,
                    'size_bytes': version.size_bytes,
                    'checksum': version.checksum,
                    'backup_type': version.backup_type,
                    'components': version.components,
                    'metadata': version.metadata
                }, f, indent=2)
            
            # Add to versions list
            self.versions.append(version)
            self._save_versions()
            
            # Update last backup time
            self.last_backup_time = datetime.now()
            
            # Auto cleanup if enabled
            if self.config.auto_cleanup:
                self._cleanup_old_versions()
            
            print(f"[AutoBackup] Created backup {version_id}: {len(backed_up_components)} components, {total_size / 1024:.1f} KB")
            
            return version
            
        except Exception as e:
            print(f"[AutoBackup] Error creating backup: {e}")
            # Cleanup failed backup
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir, ignore_errors=True)
            return None
    
    def create_pre_reset_backup(self) -> Optional[BackupVersion]:
        """Create a safety backup before system reset."""
        return self.create_backup(
            description="Pre-reset safety backup",
            backup_type="pre-reset"
        )
    
    def restore_backup(self, version_id: str, components: List[str] = None) -> bool:
        """
        Restore from a backup version.
        
        Args:
            version_id: ID of the version to restore
            components: List of components to restore (None = all)
        
        Returns:
            True if successful, False otherwise
        """
        version = self.get_version(version_id)
        if not version:
            print(f"[AutoBackup] Version not found: {version_id}")
            return False
        
        version_dir = os.path.join(self.backup_dir, "versions", version_id)
        if not os.path.exists(version_dir):
            print(f"[AutoBackup] Backup directory not found: {version_dir}")
            return False
        
        # Create pre-restore backup for safety
        self.create_backup(
            description=f"Pre-restore backup (before restoring {version_id})",
            backup_type="pre-reset"
        )
        
        try:
            # Determine components to restore
            if components is None:
                components = version.components
            
            restored = []
            for component in components:
                if component not in version.components:
                    continue
                
                source_paths = version.metadata.get('source_paths', self.backup_sources)
                dest_path = source_paths.get(component, self.backup_sources.get(component))
                
                if not dest_path:
                    continue
                
                # Find backup file
                backup_file = None
                for ext in ['.gz', '.tar.gz', '']:
                    candidate = os.path.join(version_dir, component + ext)
                    if os.path.exists(candidate):
                        backup_file = candidate
                        break
                
                if not backup_file:
                    continue
                
                # Restore based on file type
                if backup_file.endswith('.tar.gz'):
                    # Remove existing directory
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    os.makedirs(dest_path, exist_ok=True)
                    shutil.unpack_archive(backup_file, dest_path)
                elif backup_file.endswith('.gz'):
                    # Decompress and restore file
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with gzip.open(backup_file, 'rb') as f_in:
                        with open(dest_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    # Direct copy
                    if os.path.isdir(backup_file):
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(backup_file, dest_path)
                    else:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(backup_file, dest_path)
                
                restored.append(component)
            
            print(f"[AutoBackup] Restored {len(restored)} components from {version_id}")
            return True
            
        except Exception as e:
            print(f"[AutoBackup] Error restoring backup: {e}")
            return False
    
    def get_version(self, version_id: str) -> Optional[BackupVersion]:
        """Get a specific backup version."""
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def get_versions(self, backup_type: str = None, limit: int = None) -> List[BackupVersion]:
        """
        Get backup versions, optionally filtered by type.
        
        Args:
            backup_type: Filter by backup type
            limit: Maximum number of versions to return
        
        Returns:
            List of BackupVersion objects, sorted by timestamp (newest first)
        """
        versions = sorted(self.versions, key=lambda v: v.timestamp, reverse=True)
        
        if backup_type:
            versions = [v for v in versions if v.backup_type == backup_type]
        
        if limit:
            versions = versions[:limit]
        
        return versions
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a specific backup version."""
        version = self.get_version(version_id)
        if not version:
            return False
        
        version_dir = os.path.join(self.backup_dir, "versions", version_id)
        
        try:
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir)
            
            self.versions = [v for v in self.versions if v.version_id != version_id]
            self._save_versions()
            
            print(f"[AutoBackup] Deleted version {version_id}")
            return True
        except Exception as e:
            print(f"[AutoBackup] Error deleting version: {e}")
            return False
    
    def _cleanup_old_versions(self):
        """Clean up old versions based on retention policy."""
        # Remove versions exceeding max count
        while len(self.versions) > self.config.max_versions:
            # Keep pre-reset backups longer, remove oldest auto backups first
            auto_backups = [v for v in self.versions if v.backup_type == 'auto']
            if auto_backups:
                oldest = min(auto_backups, key=lambda v: v.timestamp)
                self.delete_version(oldest.version_id)
            else:
                oldest = min(self.versions, key=lambda v: v.timestamp)
                self.delete_version(oldest.version_id)
        
        # Remove versions older than retention period
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
        old_versions = [v for v in self.versions 
                       if v.timestamp < cutoff_date and v.backup_type == 'auto']
        
        for version in old_versions:
            self.delete_version(version.version_id)
        
        # Check storage limit
        self._enforce_storage_limit()
    
    def _enforce_storage_limit(self):
        """Enforce maximum storage limit."""
        total_size = sum(v.size_bytes for v in self.versions)
        max_size = self.config.max_storage_mb * 1024 * 1024
        
        while total_size > max_size and len(self.versions) > 1:
            # Remove oldest auto backup
            auto_backups = sorted(
                [v for v in self.versions if v.backup_type == 'auto'],
                key=lambda v: v.timestamp
            )
            
            if auto_backups:
                self.delete_version(auto_backups[0].version_id)
                total_size = sum(v.size_bytes for v in self.versions)
            else:
                break
    
    def _calculate_checksum(self, path: str) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()[:16]
        except Exception:
            return ""
    
    def _calculate_dir_checksum(self, path: str) -> str:
        """Calculate combined checksum of all files in a directory."""
        checksums = []
        for root, _, files in os.walk(path):
            for filename in sorted(files):
                file_path = os.path.join(root, filename)
                checksums.append(self._calculate_checksum(file_path))
        
        return hashlib.sha256(''.join(checksums).encode()).hexdigest()[:16]
    
    def _get_dir_size(self, path: str) -> int:
        """Get total size of a directory in bytes."""
        total = 0
        for root, _, files in os.walk(path):
            for filename in files:
                total += os.path.getsize(os.path.join(root, filename))
        return total
    
    def start_auto_backup(self):
        """Start automatic backup scheduler."""
        if self.is_running or not self.config.enabled:
            return
        
        self.is_running = True
        self.backup_thread = threading.Thread(target=self._auto_backup_loop, daemon=True)
        self.backup_thread.start()
        print(f"[AutoBackup] Started auto backup (interval: {self.config.interval_minutes} minutes)")
    
    def stop_auto_backup(self):
        """Stop automatic backup scheduler."""
        self.is_running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=5.0)
        print("[AutoBackup] Stopped auto backup")
    
    def _auto_backup_loop(self):
        """Main loop for automatic backups."""
        while self.is_running:
            try:
                # Check if it's time for a backup
                if self.last_backup_time:
                    elapsed = (datetime.now() - self.last_backup_time).total_seconds() / 60
                    if elapsed >= self.config.interval_minutes:
                        self.create_backup("Scheduled auto backup", backup_type="auto")
                else:
                    # First backup
                    self.create_backup("Initial auto backup", backup_type="auto")
                
                # Sleep for a minute before checking again
                time.sleep(60)
                
            except Exception as e:
                print(f"[AutoBackup] Error in auto backup loop: {e}")
                time.sleep(60)
    
    def get_storage_stats(self) -> Dict:
        """Get backup storage statistics."""
        total_size = sum(v.size_bytes for v in self.versions)
        
        return {
            'total_versions': len(self.versions),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_storage_mb': self.config.max_storage_mb,
            'storage_used_percent': round((total_size / (self.config.max_storage_mb * 1024 * 1024)) * 100, 1),
            'oldest_backup': self.versions[-1].timestamp.isoformat() if self.versions else None,
            'newest_backup': self.versions[0].timestamp.isoformat() if self.versions else None,
            'auto_backup_enabled': self.config.enabled,
            'backup_interval_minutes': self.config.interval_minutes,
            'versions_by_type': {
                'auto': len([v for v in self.versions if v.backup_type == 'auto']),
                'manual': len([v for v in self.versions if v.backup_type == 'manual']),
                'pre-reset': len([v for v in self.versions if v.backup_type == 'pre-reset'])
            }
        }
    
    def export_version_list(self) -> List[Dict]:
        """Export version list for API/UI consumption."""
        return [
            {
                'version_id': v.version_id,
                'timestamp': v.timestamp.isoformat(),
                'description': v.description,
                'size_bytes': v.size_bytes,
                'size_formatted': self._format_size(v.size_bytes),
                'checksum': v.checksum,
                'backup_type': v.backup_type,
                'components': v.components,
                'age': self._format_age(v.timestamp)
            }
            for v in sorted(self.versions, key=lambda v: v.timestamp, reverse=True)
        ]
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _format_age(self, timestamp: datetime) -> str:
        """Format age in human-readable form."""
        delta = datetime.now() - timestamp
        
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


# Singleton instance
_backup_manager: Optional[AutoBackupManager] = None


def get_backup_manager() -> AutoBackupManager:
    """Get the singleton backup manager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = AutoBackupManager()
    return _backup_manager


# Example usage
if __name__ == '__main__':
    manager = AutoBackupManager()
    
    # Create a manual backup
    version = manager.create_backup("Test backup", backup_type="manual")
    if version:
        print(f"Created backup: {version.version_id}")
    
    # List versions
    print("\nBackup versions:")
    for v in manager.get_versions(limit=5):
        print(f"  - {v.version_id}: {v.description} ({v.backup_type})")
    
    # Get stats
    stats = manager.get_storage_stats()
    print(f"\nStorage stats: {stats}")
