"""
VA21 Docker Manager - Container Management System

This module provides comprehensive Docker container management
with support for images, containers, networks, and volumes.
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Container:
    """Represents a Docker container."""
    container_id: str
    name: str
    image: str
    status: str
    state: str
    created: str
    ports: List[str]
    networks: List[str]


@dataclass
class Image:
    """Represents a Docker image."""
    image_id: str
    repository: str
    tag: str
    size: str
    created: str


class DockerManager:
    """
    VA21 Docker Manager - Full container management.
    
    Features:
    - Container lifecycle management
    - Image management (pull, build, remove)
    - Network management
    - Volume management
    - Docker Compose support
    - Real-time container stats
    - Log viewing
    """
    
    def __init__(self):
        self.docker_available = self._check_docker()
        self.compose_available = self._check_compose()
    
    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ['docker', 'version', '--format', 'json'],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_compose(self) -> bool:
        """Check if Docker Compose is available."""
        try:
            result = subprocess.run(
                ['docker-compose', 'version'],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except:
            try:
                result = subprocess.run(
                    ['docker', 'compose', 'version'],
                    capture_output=True, text=True, timeout=10
                )
                return result.returncode == 0
            except:
                return False
    
    def _run_docker(self, *args, timeout: int = 60) -> tuple:
        """Run a Docker command."""
        try:
            result = subprocess.run(
                ['docker'] + list(args),
                capture_output=True, text=True, timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, '', 'Command timed out'
        except Exception as e:
            return False, '', str(e)
    
    # ==================== CONTAINERS ====================
    
    def list_containers(self, all_containers: bool = True) -> List[Container]:
        """List Docker containers."""
        if not self.docker_available:
            return []
        
        args = ['ps', '--format', 'json']
        if all_containers:
            args.append('-a')
        
        success, output, _ = self._run_docker(*args)
        
        if not success:
            return []
        
        containers = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            try:
                data = json.loads(line)
                containers.append(Container(
                    container_id=data.get('ID', ''),
                    name=data.get('Names', ''),
                    image=data.get('Image', ''),
                    status=data.get('Status', ''),
                    state=data.get('State', ''),
                    created=data.get('CreatedAt', ''),
                    ports=data.get('Ports', '').split(',') if data.get('Ports') else [],
                    networks=data.get('Networks', '').split(',') if data.get('Networks') else []
                ))
            except:
                continue
        
        return containers
    
    def start_container(self, container_id: str) -> Dict:
        """Start a container."""
        success, output, error = self._run_docker('start', container_id)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def stop_container(self, container_id: str) -> Dict:
        """Stop a container."""
        success, output, error = self._run_docker('stop', container_id)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def restart_container(self, container_id: str) -> Dict:
        """Restart a container."""
        success, output, error = self._run_docker('restart', container_id)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def remove_container(self, container_id: str, force: bool = False) -> Dict:
        """Remove a container."""
        args = ['rm']
        if force:
            args.append('-f')
        args.append(container_id)
        
        success, output, error = self._run_docker(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def get_container_logs(self, container_id: str, lines: int = 100) -> str:
        """Get container logs."""
        success, output, error = self._run_docker(
            'logs', '--tail', str(lines), container_id
        )
        return output if success else error
    
    def get_container_stats(self, container_id: str) -> Dict:
        """Get container resource stats."""
        success, output, _ = self._run_docker(
            'stats', '--no-stream', '--format', 'json', container_id
        )
        
        if not success:
            return {}
        
        try:
            return json.loads(output)
        except:
            return {}
    
    def exec_in_container(self, container_id: str, command: str) -> Dict:
        """Execute a command in a container."""
        success, output, error = self._run_docker(
            'exec', container_id, 'sh', '-c', command
        )
        return {
            'success': success,
            'output': output,
            'error': error
        }
    
    def run_container(self, image: str, name: str = None,
                     ports: Dict[str, str] = None,
                     volumes: Dict[str, str] = None,
                     env: Dict[str, str] = None,
                     detach: bool = True,
                     network: str = None) -> Dict:
        """Run a new container."""
        args = ['run']
        
        if detach:
            args.append('-d')
        
        if name:
            args.extend(['--name', name])
        
        if network:
            args.extend(['--network', network])
        
        if ports:
            for host_port, container_port in ports.items():
                args.extend(['-p', f'{host_port}:{container_port}'])
        
        if volumes:
            for host_path, container_path in volumes.items():
                args.extend(['-v', f'{host_path}:{container_path}'])
        
        if env:
            for key, value in env.items():
                args.extend(['-e', f'{key}={value}'])
        
        args.append(image)
        
        success, output, error = self._run_docker(*args)
        return {
            'success': success,
            'container_id': output.strip() if success else None,
            'message': output if success else error
        }
    
    # ==================== IMAGES ====================
    
    def list_images(self) -> List[Image]:
        """List Docker images."""
        if not self.docker_available:
            return []
        
        success, output, _ = self._run_docker('images', '--format', 'json')
        
        if not success:
            return []
        
        images = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            try:
                data = json.loads(line)
                images.append(Image(
                    image_id=data.get('ID', ''),
                    repository=data.get('Repository', ''),
                    tag=data.get('Tag', ''),
                    size=data.get('Size', ''),
                    created=data.get('CreatedAt', '')
                ))
            except:
                continue
        
        return images
    
    def pull_image(self, image: str) -> Dict:
        """Pull an image from registry."""
        success, output, error = self._run_docker('pull', image, timeout=300)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def remove_image(self, image_id: str, force: bool = False) -> Dict:
        """Remove an image."""
        args = ['rmi']
        if force:
            args.append('-f')
        args.append(image_id)
        
        success, output, error = self._run_docker(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def build_image(self, path: str, tag: str,
                   dockerfile: str = None) -> Dict:
        """Build an image from Dockerfile."""
        args = ['build', '-t', tag]
        
        if dockerfile:
            args.extend(['-f', dockerfile])
        
        args.append(path)
        
        success, output, error = self._run_docker(*args, timeout=600)
        return {
            'success': success,
            'message': output if success else error
        }
    
    # ==================== NETWORKS ====================
    
    def list_networks(self) -> List[Dict]:
        """List Docker networks."""
        success, output, _ = self._run_docker('network', 'ls', '--format', 'json')
        
        if not success:
            return []
        
        networks = []
        for line in output.strip().split('\n'):
            if line:
                try:
                    networks.append(json.loads(line))
                except:
                    continue
        
        return networks
    
    def create_network(self, name: str, driver: str = 'bridge') -> Dict:
        """Create a network."""
        success, output, error = self._run_docker(
            'network', 'create', '--driver', driver, name
        )
        return {
            'success': success,
            'message': output if success else error
        }
    
    def remove_network(self, network_id: str) -> Dict:
        """Remove a network."""
        success, output, error = self._run_docker('network', 'rm', network_id)
        return {
            'success': success,
            'message': output if success else error
        }
    
    # ==================== VOLUMES ====================
    
    def list_volumes(self) -> List[Dict]:
        """List Docker volumes."""
        success, output, _ = self._run_docker('volume', 'ls', '--format', 'json')
        
        if not success:
            return []
        
        volumes = []
        for line in output.strip().split('\n'):
            if line:
                try:
                    volumes.append(json.loads(line))
                except:
                    continue
        
        return volumes
    
    def create_volume(self, name: str) -> Dict:
        """Create a volume."""
        success, output, error = self._run_docker('volume', 'create', name)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def remove_volume(self, volume_name: str) -> Dict:
        """Remove a volume."""
        success, output, error = self._run_docker('volume', 'rm', volume_name)
        return {
            'success': success,
            'message': output if success else error
        }
    
    # ==================== DOCKER COMPOSE ====================
    
    def compose_up(self, path: str, detach: bool = True) -> Dict:
        """Start Docker Compose services."""
        args = ['-f', path, 'up']
        if detach:
            args.append('-d')
        
        try:
            result = subprocess.run(
                ['docker-compose'] + args,
                capture_output=True, text=True, timeout=300
            )
            return {
                'success': result.returncode == 0,
                'message': result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def compose_down(self, path: str, volumes: bool = False) -> Dict:
        """Stop Docker Compose services."""
        args = ['-f', path, 'down']
        if volumes:
            args.append('-v')
        
        try:
            result = subprocess.run(
                ['docker-compose'] + args,
                capture_output=True, text=True, timeout=120
            )
            return {
                'success': result.returncode == 0,
                'message': result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def compose_ps(self, path: str) -> List[Dict]:
        """List Docker Compose services."""
        try:
            result = subprocess.run(
                ['docker-compose', '-f', path, 'ps', '--format', 'json'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            services = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        services.append(json.loads(line))
                    except:
                        continue
            
            return services
        except:
            return []
    
    # ==================== SYSTEM ====================
    
    def get_system_info(self) -> Dict:
        """Get Docker system information."""
        success, output, _ = self._run_docker('system', 'info', '--format', 'json')
        
        if not success:
            return {}
        
        try:
            return json.loads(output)
        except:
            return {}
    
    def get_disk_usage(self) -> Dict:
        """Get Docker disk usage."""
        success, output, _ = self._run_docker('system', 'df', '--format', 'json')
        
        if not success:
            return {}
        
        try:
            return json.loads(output)
        except:
            return {}
    
    def prune_system(self, all_unused: bool = False) -> Dict:
        """Prune unused Docker resources."""
        args = ['system', 'prune', '-f']
        if all_unused:
            args.append('-a')
        
        success, output, error = self._run_docker(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def get_stats(self) -> Dict:
        """Get Docker manager statistics."""
        return {
            'docker_available': self.docker_available,
            'compose_available': self.compose_available,
            'containers': len(self.list_containers()),
            'running_containers': len([c for c in self.list_containers() if c.state == 'running']),
            'images': len(self.list_images()),
            'networks': len(self.list_networks()),
            'volumes': len(self.list_volumes())
        }


# Singleton
_docker_manager: Optional[DockerManager] = None


def get_docker_manager() -> DockerManager:
    """Get the singleton Docker Manager instance."""
    global _docker_manager
    if _docker_manager is None:
        _docker_manager = DockerManager()
    return _docker_manager
