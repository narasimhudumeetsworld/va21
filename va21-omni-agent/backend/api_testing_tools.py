"""
VA21 API Testing Tools - Comprehensive API Development Suite

This module provides tools for API testing, development, and debugging
with full request/response history and environment management.
"""

import json
import os
import time
import uuid
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from urllib.parse import urlparse, urlencode
import subprocess


@dataclass
class APIRequest:
    """Represents an API request."""
    request_id: str
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str]
    query_params: Dict[str, str]
    created_at: datetime
    name: str = ""
    description: str = ""
    folder: str = "Default"
    auth_type: str = "none"
    auth_data: Dict = field(default_factory=dict)


@dataclass
class APIResponse:
    """Represents an API response."""
    response_id: str
    request_id: str
    status_code: int
    status_text: str
    headers: Dict[str, str]
    body: str
    response_time_ms: float
    size_bytes: int
    timestamp: datetime


@dataclass
class APIEnvironment:
    """Environment variables for API testing."""
    env_id: str
    name: str
    variables: Dict[str, str]
    is_active: bool = False


class APITestingTools:
    """
    VA21 API Testing Tools - Full API development environment.
    
    Features:
    - HTTP request builder (GET, POST, PUT, DELETE, PATCH, etc.)
    - Request/Response history with search
    - Environment variables management
    - Request collections and folders
    - Authentication support (Basic, Bearer, API Key)
    - Request chaining with variable extraction
    - cURL import/export
    - Response validation
    """
    
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    
    def __init__(self, data_dir: str = "data/api_testing"):
        self.data_dir = data_dir
        self.requests_file = os.path.join(data_dir, "requests.json")
        self.history_file = os.path.join(data_dir, "history.json")
        self.environments_file = os.path.join(data_dir, "environments.json")
        
        self.requests: Dict[str, APIRequest] = {}
        self.history: List[tuple] = []  # (request, response)
        self.environments: Dict[str, APIEnvironment] = {}
        self.active_environment: Optional[str] = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the API testing tools."""
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_data()
    
    def _load_data(self):
        """Load saved data from disk."""
        # Load requests
        if os.path.exists(self.requests_file):
            try:
                with open(self.requests_file, 'r') as f:
                    data = json.load(f)
                    for r in data.get('requests', []):
                        self.requests[r['request_id']] = APIRequest(
                            request_id=r['request_id'],
                            method=r['method'],
                            url=r['url'],
                            headers=r.get('headers', {}),
                            body=r.get('body'),
                            query_params=r.get('query_params', {}),
                            created_at=datetime.fromisoformat(r['created_at']),
                            name=r.get('name', ''),
                            description=r.get('description', ''),
                            folder=r.get('folder', 'Default'),
                            auth_type=r.get('auth_type', 'none'),
                            auth_data=r.get('auth_data', {})
                        )
            except Exception as e:
                print(f"[APITools] Error loading requests: {e}")
        
        # Load environments
        if os.path.exists(self.environments_file):
            try:
                with open(self.environments_file, 'r') as f:
                    data = json.load(f)
                    for e in data.get('environments', []):
                        self.environments[e['env_id']] = APIEnvironment(
                            env_id=e['env_id'],
                            name=e['name'],
                            variables=e['variables'],
                            is_active=e.get('is_active', False)
                        )
                        if e.get('is_active'):
                            self.active_environment = e['env_id']
            except Exception as e:
                print(f"[APITools] Error loading environments: {e}")
    
    def _save_requests(self):
        """Save requests to disk."""
        data = {
            'requests': [
                {
                    'request_id': r.request_id,
                    'method': r.method,
                    'url': r.url,
                    'headers': r.headers,
                    'body': r.body,
                    'query_params': r.query_params,
                    'created_at': r.created_at.isoformat(),
                    'name': r.name,
                    'description': r.description,
                    'folder': r.folder,
                    'auth_type': r.auth_type,
                    'auth_data': r.auth_data
                }
                for r in self.requests.values()
            ]
        }
        with open(self.requests_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_environments(self):
        """Save environments to disk."""
        data = {
            'environments': [
                {
                    'env_id': e.env_id,
                    'name': e.name,
                    'variables': e.variables,
                    'is_active': e.is_active
                }
                for e in self.environments.values()
            ]
        }
        with open(self.environments_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    # ==================== REQUEST MANAGEMENT ====================
    
    def create_request(self, method: str, url: str, name: str = "",
                      headers: Dict[str, str] = None,
                      body: str = None, query_params: Dict[str, str] = None,
                      folder: str = "Default") -> APIRequest:
        """Create a new API request."""
        request_id = str(uuid.uuid4())[:12]
        
        request = APIRequest(
            request_id=request_id,
            method=method.upper(),
            url=url,
            headers=headers or {},
            body=body,
            query_params=query_params or {},
            created_at=datetime.now(),
            name=name or f"{method} {urlparse(url).path}",
            folder=folder
        )
        
        self.requests[request_id] = request
        self._save_requests()
        
        return request
    
    def update_request(self, request_id: str, **kwargs) -> Optional[APIRequest]:
        """Update an existing request."""
        if request_id not in self.requests:
            return None
        
        request = self.requests[request_id]
        
        for key, value in kwargs.items():
            if hasattr(request, key):
                setattr(request, key, value)
        
        self._save_requests()
        return request
    
    def delete_request(self, request_id: str) -> bool:
        """Delete a request."""
        if request_id in self.requests:
            del self.requests[request_id]
            self._save_requests()
            return True
        return False
    
    def get_requests_by_folder(self, folder: str = None) -> List[APIRequest]:
        """Get requests grouped by folder."""
        if folder:
            return [r for r in self.requests.values() if r.folder == folder]
        return list(self.requests.values())
    
    def get_folders(self) -> List[str]:
        """Get all folders."""
        folders = set()
        for r in self.requests.values():
            folders.add(r.folder)
        return sorted(list(folders))
    
    # ==================== REQUEST EXECUTION ====================
    
    def execute_request(self, request: APIRequest) -> APIResponse:
        """
        Execute an API request using curl.
        
        Args:
            request: The request to execute
        
        Returns:
            APIResponse with the result
        """
        # Apply environment variables
        url = self._apply_variables(request.url)
        headers = {k: self._apply_variables(v) for k, v in request.headers.items()}
        body = self._apply_variables(request.body) if request.body else None
        
        # Build curl command
        curl_cmd = self._build_curl_command(
            method=request.method,
            url=url,
            headers=headers,
            body=body,
            query_params=request.query_params,
            auth_type=request.auth_type,
            auth_data=request.auth_data
        )
        
        # Execute
        start_time = time.time()
        try:
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000
            
            # Parse response
            response = self._parse_curl_response(
                request.request_id,
                result.stdout,
                result.stderr,
                response_time
            )
            
            # Add to history
            self.history.append((request, response))
            
            return response
            
        except subprocess.TimeoutExpired:
            return APIResponse(
                response_id=str(uuid.uuid4())[:12],
                request_id=request.request_id,
                status_code=0,
                status_text='Timeout',
                headers={},
                body='Request timed out after 30 seconds',
                response_time_ms=30000,
                size_bytes=0,
                timestamp=datetime.now()
            )
        except Exception as e:
            return APIResponse(
                response_id=str(uuid.uuid4())[:12],
                request_id=request.request_id,
                status_code=0,
                status_text='Error',
                headers={},
                body=str(e),
                response_time_ms=0,
                size_bytes=0,
                timestamp=datetime.now()
            )
    
    def _build_curl_command(self, method: str, url: str,
                           headers: Dict[str, str], body: str = None,
                           query_params: Dict[str, str] = None,
                           auth_type: str = "none",
                           auth_data: Dict = None) -> List[str]:
        """Build a curl command."""
        cmd = ['curl', '-s', '-w', '\n%{http_code}', '-X', method]
        
        # Add query params to URL
        if query_params:
            url += '?' + urlencode(query_params)
        
        cmd.append(url)
        
        # Add headers
        for key, value in headers.items():
            cmd.extend(['-H', f'{key}: {value}'])
        
        # Add authentication
        if auth_type == 'basic' and auth_data:
            username = auth_data.get('username', '')
            password = auth_data.get('password', '')
            cmd.extend(['-u', f'{username}:{password}'])
        elif auth_type == 'bearer' and auth_data:
            token = auth_data.get('token', '')
            cmd.extend(['-H', f'Authorization: Bearer {token}'])
        elif auth_type == 'api_key' and auth_data:
            key_name = auth_data.get('key_name', 'X-API-Key')
            key_value = auth_data.get('key_value', '')
            cmd.extend(['-H', f'{key_name}: {key_value}'])
        
        # Add body
        if body:
            cmd.extend(['-d', body])
        
        # Include headers in output
        cmd.append('-i')
        
        return cmd
    
    def _parse_curl_response(self, request_id: str, stdout: str,
                            stderr: str, response_time: float) -> APIResponse:
        """Parse curl output into APIResponse."""
        response_id = str(uuid.uuid4())[:12]
        
        # Default values
        status_code = 0
        status_text = 'Unknown'
        headers = {}
        body = ''
        
        if stdout:
            lines = stdout.split('\n')
            
            # Last line is status code
            if lines:
                try:
                    status_code = int(lines[-1].strip())
                except ValueError:
                    pass
            
            # Parse headers and body
            header_end = False
            body_lines = []
            
            for line in lines[:-1]:  # Exclude status code line
                if line.startswith('HTTP/'):
                    parts = line.split(' ', 2)
                    if len(parts) >= 2:
                        status_text = parts[2] if len(parts) > 2 else ''
                elif not header_end and ': ' in line:
                    key, value = line.split(': ', 1)
                    headers[key] = value.strip()
                elif not header_end and line.strip() == '':
                    header_end = True
                elif header_end:
                    body_lines.append(line)
            
            body = '\n'.join(body_lines)
        
        return APIResponse(
            response_id=response_id,
            request_id=request_id,
            status_code=status_code,
            status_text=status_text,
            headers=headers,
            body=body,
            response_time_ms=response_time,
            size_bytes=len(body.encode()),
            timestamp=datetime.now()
        )
    
    def _apply_variables(self, text: str) -> str:
        """Apply environment variables to text."""
        if not text or not self.active_environment:
            return text
        
        env = self.environments.get(self.active_environment)
        if not env:
            return text
        
        # Replace {{variable}} with values
        for var, value in env.variables.items():
            text = text.replace(f"{{{{{var}}}}}", value)
        
        return text
    
    # ==================== ENVIRONMENT MANAGEMENT ====================
    
    def create_environment(self, name: str, variables: Dict[str, str] = None) -> APIEnvironment:
        """Create a new environment."""
        env_id = str(uuid.uuid4())[:12]
        
        env = APIEnvironment(
            env_id=env_id,
            name=name,
            variables=variables or {}
        )
        
        self.environments[env_id] = env
        self._save_environments()
        
        return env
    
    def update_environment(self, env_id: str, **kwargs) -> Optional[APIEnvironment]:
        """Update an environment."""
        if env_id not in self.environments:
            return None
        
        env = self.environments[env_id]
        
        for key, value in kwargs.items():
            if hasattr(env, key):
                setattr(env, key, value)
        
        self._save_environments()
        return env
    
    def delete_environment(self, env_id: str) -> bool:
        """Delete an environment."""
        if env_id in self.environments:
            del self.environments[env_id]
            if self.active_environment == env_id:
                self.active_environment = None
            self._save_environments()
            return True
        return False
    
    def set_active_environment(self, env_id: str) -> bool:
        """Set the active environment."""
        if env_id not in self.environments:
            return False
        
        # Deactivate current
        if self.active_environment:
            self.environments[self.active_environment].is_active = False
        
        self.environments[env_id].is_active = True
        self.active_environment = env_id
        self._save_environments()
        
        return True
    
    def get_environments(self) -> List[APIEnvironment]:
        """Get all environments."""
        return list(self.environments.values())
    
    # ==================== CURL IMPORT/EXPORT ====================
    
    def import_curl(self, curl_command: str) -> Optional[APIRequest]:
        """Import a curl command into a request."""
        try:
            # Parse method
            method = 'GET'
            method_match = re.search(r'-X\s+(\w+)', curl_command)
            if method_match:
                method = method_match.group(1).upper()
            
            # Parse URL
            url_match = re.search(r"curl\s+(?:-[^\s]+\s+)*['\"]?([^'\"\s]+)", curl_command)
            if not url_match:
                return None
            url = url_match.group(1)
            
            # Parse headers
            headers = {}
            header_matches = re.findall(r"-H\s+['\"]([^:]+):\s*([^'\"]+)['\"]", curl_command)
            for key, value in header_matches:
                headers[key] = value
            
            # Parse data
            body = None
            data_match = re.search(r"-d\s+['\"]([^'\"]+)['\"]", curl_command)
            if data_match:
                body = data_match.group(1)
            
            return self.create_request(
                method=method,
                url=url,
                headers=headers,
                body=body,
                name=f"Imported: {method} {urlparse(url).path}"
            )
            
        except Exception as e:
            print(f"[APITools] Error importing curl: {e}")
            return None
    
    def export_curl(self, request: APIRequest) -> str:
        """Export a request as curl command."""
        parts = ['curl', '-X', request.method]
        
        for key, value in request.headers.items():
            parts.append(f"-H '{key}: {value}'")
        
        if request.body:
            parts.append(f"-d '{request.body}'")
        
        url = request.url
        if request.query_params:
            url += '?' + urlencode(request.query_params)
        
        parts.append(f"'{url}'")
        
        return ' '.join(parts)
    
    # ==================== HISTORY ====================
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get request history."""
        history_items = []
        
        for request, response in self.history[-limit:]:
            history_items.append({
                'request': {
                    'id': request.request_id,
                    'method': request.method,
                    'url': request.url,
                    'name': request.name
                },
                'response': {
                    'id': response.response_id,
                    'status_code': response.status_code,
                    'response_time_ms': response.response_time_ms,
                    'size_bytes': response.size_bytes,
                    'timestamp': response.timestamp.isoformat()
                }
            })
        
        return list(reversed(history_items))
    
    def clear_history(self):
        """Clear request history."""
        self.history = []
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict:
        """Get API testing statistics."""
        return {
            'total_requests': len(self.requests),
            'total_environments': len(self.environments),
            'history_count': len(self.history),
            'folders': self.get_folders(),
            'active_environment': self.active_environment,
            'methods_used': list(set(r.method for r in self.requests.values()))
        }


# Singleton
_api_tools: Optional[APITestingTools] = None


def get_api_testing_tools() -> APITestingTools:
    """Get the singleton API Testing Tools instance."""
    global _api_tools
    if _api_tools is None:
        _api_tools = APITestingTools()
    return _api_tools
