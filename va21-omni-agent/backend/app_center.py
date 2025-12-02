"""
VA21 App Center - Flathub & Debian Package Integration

This module provides integration with Flathub (Flatpak) and Debian
repositories for easy application installation.
"""

import subprocess
import json
import os
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AppInfo:
    """Information about an application."""
    id: str
    name: str
    summary: str
    description: str
    icon_url: str
    version: str
    source: str  # 'flatpak' or 'debian'
    category: str
    developer: str
    installed: bool = False
    size: str = ""


class AppCenter:
    """
    VA21 App Center for managing application installation.
    
    Features:
    - Flathub integration for Flatpak apps
    - Debian repository integration
    - App search and preview
    - One-click installation
    - Installation progress tracking
    """
    
    def __init__(self):
        self.flatpak_available = self._check_flatpak()
        self.apt_available = self._check_apt()
        self.app_cache: Dict[str, AppInfo] = {}
        self.installation_queue: List[str] = []
        self.installing: Dict[str, float] = {}  # app_id -> progress
        
        # Popular apps for quick access
        self.featured_apps = [
            {
                'id': 'org.mozilla.firefox',
                'name': 'Firefox',
                'summary': 'Fast, Private & Safe Web Browser',
                'icon': '🦊',
                'category': 'Internet',
                'source': 'flatpak'
            },
            {
                'id': 'com.visualstudio.code',
                'name': 'Visual Studio Code',
                'summary': 'Code editing. Redefined.',
                'icon': '💻',
                'category': 'Development',
                'source': 'flatpak'
            },
            {
                'id': 'org.videolan.VLC',
                'name': 'VLC Media Player',
                'summary': 'The universal media player',
                'icon': '🎬',
                'category': 'Multimedia',
                'source': 'flatpak'
            },
            {
                'id': 'org.gimp.GIMP',
                'name': 'GIMP',
                'summary': 'GNU Image Manipulation Program',
                'icon': '🎨',
                'category': 'Graphics',
                'source': 'flatpak'
            },
            {
                'id': 'org.libreoffice.LibreOffice',
                'name': 'LibreOffice',
                'summary': 'Free office suite',
                'icon': '📝',
                'category': 'Office',
                'source': 'flatpak'
            },
            {
                'id': 'com.spotify.Client',
                'name': 'Spotify',
                'summary': 'Music for everyone',
                'icon': '🎵',
                'category': 'Audio',
                'source': 'flatpak'
            },
            {
                'id': 'org.telegram.desktop',
                'name': 'Telegram Desktop',
                'summary': 'Fast and secure messaging',
                'icon': '💬',
                'category': 'Communication',
                'source': 'flatpak'
            },
            {
                'id': 'com.discordapp.Discord',
                'name': 'Discord',
                'summary': 'Chat for communities and friends',
                'icon': '🎮',
                'category': 'Communication',
                'source': 'flatpak'
            },
            {
                'id': 'org.blender.Blender',
                'name': 'Blender',
                'summary': '3D creation suite',
                'icon': '🎬',
                'category': 'Graphics',
                'source': 'flatpak'
            },
            {
                'id': 'org.kde.kdenlive',
                'name': 'Kdenlive',
                'summary': 'Video editor',
                'icon': '🎥',
                'category': 'Multimedia',
                'source': 'flatpak'
            }
        ]
        
        self.categories = [
            'All',
            'Internet',
            'Development',
            'Multimedia',
            'Graphics',
            'Office',
            'Games',
            'Utilities',
            'Communication',
            'Audio'
        ]
    
    def _check_flatpak(self) -> bool:
        """Check if Flatpak is available."""
        try:
            result = subprocess.run(['flatpak', '--version'], 
                                   capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _check_apt(self) -> bool:
        """Check if APT is available."""
        try:
            result = subprocess.run(['apt', '--version'], 
                                   capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def search_apps(self, query: str, source: str = 'all', 
                    category: str = 'All') -> List[Dict]:
        """
        Search for applications.
        
        Args:
            query: Search query
            source: 'flatpak', 'debian', or 'all'
            category: Filter by category
            
        Returns:
            List of matching apps
        """
        results = []
        query_lower = query.lower()
        
        # Search in featured apps first (always available)
        for app in self.featured_apps:
            if query_lower in app['name'].lower() or query_lower in app.get('summary', '').lower():
                if category == 'All' or category == app.get('category'):
                    if source == 'all' or source == app.get('source'):
                        results.append({
                            **app,
                            'installed': self._is_installed(app['id'], app['source'])
                        })
        
        # Search Flatpak repository
        if source in ['all', 'flatpak'] and self.flatpak_available:
            flatpak_results = self._search_flatpak(query)
            for app in flatpak_results:
                if category == 'All' or category == app.get('category', 'Utilities'):
                    results.append(app)
        
        # Search Debian packages
        if source in ['all', 'debian'] and self.apt_available:
            debian_results = self._search_debian(query)
            for app in debian_results:
                if category == 'All' or category == app.get('category', 'Utilities'):
                    results.append(app)
        
        return results[:20]  # Limit results
    
    def _search_flatpak(self, query: str) -> List[Dict]:
        """Search Flatpak/Flathub repository."""
        try:
            result = subprocess.run(
                ['flatpak', 'search', query],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            apps = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 3:
                    app_id = parts[2] if len(parts) > 2 else parts[0]
                    apps.append({
                        'id': app_id,
                        'name': parts[0],
                        'summary': parts[1] if len(parts) > 1 else '',
                        'icon': '📦',
                        'source': 'flatpak',
                        'category': 'Utilities',
                        'installed': self._is_flatpak_installed(app_id)
                    })
            
            return apps[:10]
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return []
    
    def _search_debian(self, query: str) -> List[Dict]:
        """Search Debian packages."""
        try:
            result = subprocess.run(
                ['apt-cache', 'search', query],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            apps = []
            for line in result.stdout.strip().split('\n')[:10]:
                if not line:
                    continue
                
                parts = line.split(' - ', 1)
                if len(parts) >= 1:
                    pkg_name = parts[0].strip()
                    description = parts[1] if len(parts) > 1 else ''
                    apps.append({
                        'id': pkg_name,
                        'name': pkg_name,
                        'summary': description[:100],
                        'icon': '🐧',
                        'source': 'debian',
                        'category': 'Utilities',
                        'installed': self._is_debian_installed(pkg_name)
                    })
            
            return apps
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return []
    
    def _is_installed(self, app_id: str, source: str) -> bool:
        """Check if an app is installed."""
        if source == 'flatpak':
            return self._is_flatpak_installed(app_id)
        elif source == 'debian':
            return self._is_debian_installed(app_id)
        return False
    
    def _is_flatpak_installed(self, app_id: str) -> bool:
        """Check if a Flatpak app is installed."""
        try:
            result = subprocess.run(
                ['flatpak', 'info', app_id],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return False
    
    def _is_debian_installed(self, package: str) -> bool:
        """Check if a Debian package is installed."""
        try:
            result = subprocess.run(
                ['dpkg', '-s', package],
                capture_output=True, text=True, timeout=10
            )
            return 'Status: install ok installed' in result.stdout
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return False
    
    def install_app(self, app_id: str, source: str, callback=None) -> Dict:
        """
        Install an application.
        
        Args:
            app_id: Application identifier
            source: 'flatpak' or 'debian'
            callback: Optional callback for progress updates
            
        Returns:
            Result dict with success status and message
        """
        if source == 'flatpak':
            return self._install_flatpak(app_id, callback)
        elif source == 'debian':
            return self._install_debian(app_id, callback)
        else:
            return {'success': False, 'message': 'Unknown source'}
    
    def _install_flatpak(self, app_id: str, callback=None) -> Dict:
        """Install a Flatpak app."""
        if not self.flatpak_available:
            return {'success': False, 'message': 'Flatpak is not available'}
        
        try:
            self.installing[app_id] = 0
            
            # Add Flathub remote if not exists
            subprocess.run(
                ['flatpak', 'remote-add', '--if-not-exists', 'flathub',
                 'https://flathub.org/repo/flathub.flatpakrepo'],
                capture_output=True, timeout=30
            )
            
            # Install the app
            result = subprocess.run(
                ['flatpak', 'install', '-y', 'flathub', app_id],
                capture_output=True, text=True, timeout=600
            )
            
            del self.installing[app_id]
            
            if result.returncode == 0:
                return {'success': True, 'message': f'{app_id} installed successfully'}
            else:
                return {'success': False, 'message': result.stderr or 'Installation failed'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Installation timed out'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _install_debian(self, package: str, callback=None) -> Dict:
        """Install a Debian package."""
        if not self.apt_available:
            return {'success': False, 'message': 'APT is not available'}
        
        try:
            self.installing[package] = 0
            
            # Install the package (requires sudo)
            result = subprocess.run(
                ['pkexec', 'apt-get', 'install', '-y', package],
                capture_output=True, text=True, timeout=600
            )
            
            del self.installing[package]
            
            if result.returncode == 0:
                return {'success': True, 'message': f'{package} installed successfully'}
            else:
                return {'success': False, 'message': result.stderr or 'Installation failed'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Installation timed out'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def uninstall_app(self, app_id: str, source: str) -> Dict:
        """Uninstall an application."""
        if source == 'flatpak':
            return self._uninstall_flatpak(app_id)
        elif source == 'debian':
            return self._uninstall_debian(app_id)
        else:
            return {'success': False, 'message': 'Unknown source'}
    
    def _uninstall_flatpak(self, app_id: str) -> Dict:
        """Uninstall a Flatpak app."""
        try:
            result = subprocess.run(
                ['flatpak', 'uninstall', '-y', app_id],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                return {'success': True, 'message': f'{app_id} uninstalled successfully'}
            else:
                return {'success': False, 'message': result.stderr or 'Uninstall failed'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _uninstall_debian(self, package: str) -> Dict:
        """Uninstall a Debian package."""
        try:
            result = subprocess.run(
                ['pkexec', 'apt-get', 'remove', '-y', package],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                return {'success': True, 'message': f'{package} uninstalled successfully'}
            else:
                return {'success': False, 'message': result.stderr or 'Uninstall failed'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_featured_apps(self) -> List[Dict]:
        """Get featured apps with installation status."""
        return [
            {
                **app,
                'installed': self._is_installed(app['id'], app['source'])
            }
            for app in self.featured_apps
        ]
    
    def get_categories(self) -> List[str]:
        """Get available categories."""
        return self.categories
    
    def get_system_info(self) -> Dict:
        """Get system package manager info."""
        return {
            'flatpak_available': self.flatpak_available,
            'apt_available': self.apt_available,
            'flatpak_version': self._get_flatpak_version(),
            'debian_version': self._get_debian_version()
        }
    
    def _get_flatpak_version(self) -> str:
        """Get Flatpak version."""
        try:
            result = subprocess.run(['flatpak', '--version'], 
                                   capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else 'N/A'
        except:
            return 'N/A'
    
    def _get_debian_version(self) -> str:
        """Get Debian version."""
        try:
            with open('/etc/debian_version', 'r') as f:
                return f.read().strip()
        except:
            return 'N/A'


# Singleton instance
_app_center: Optional[AppCenter] = None


def get_app_center() -> AppCenter:
    """Get the singleton App Center instance."""
    global _app_center
    if _app_center is None:
        _app_center = AppCenter()
    return _app_center
