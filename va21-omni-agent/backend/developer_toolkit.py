"""
VA21 Developer Toolkit - GNU Tools & Development Environment

This module provides comprehensive developer tools integration including
GNU toolkit, version control, containerization, and development utilities.
"""

import subprocess
import os
import json
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolInfo:
    """Information about a development tool."""
    name: str
    command: str
    version: str
    installed: bool
    category: str
    description: str
    install_command: str


class DeveloperToolkit:
    """
    VA21 Developer Toolkit - Comprehensive development environment.
    
    Features:
    - GNU Toolkit (GCC, Make, GDB, Binutils, etc.)
    - Version Control (Git, SVN, Mercurial)
    - Containerization (Docker, Podman)
    - Languages & Runtimes (Python, Node.js, Go, Rust, Java)
    - Databases (PostgreSQL, MySQL, SQLite, Redis)
    - Build Tools (CMake, Meson, Ninja, Autotools)
    - IDE Support (VS Code, Vim, Emacs configurations)
    - API Development (curl, httpie, Postman CLI)
    """
    
    def __init__(self):
        self.tools_cache: Dict[str, ToolInfo] = {}
        self.last_scan = None
        
        # Define all tools by category
        self.tool_definitions = {
            'gnu_core': [
                {'name': 'GCC', 'command': 'gcc', 'description': 'GNU C Compiler', 'install': 'build-essential'},
                {'name': 'G++', 'command': 'g++', 'description': 'GNU C++ Compiler', 'install': 'build-essential'},
                {'name': 'Make', 'command': 'make', 'description': 'GNU Make build tool', 'install': 'make'},
                {'name': 'GDB', 'command': 'gdb', 'description': 'GNU Debugger', 'install': 'gdb'},
                {'name': 'Binutils', 'command': 'ld', 'description': 'GNU Binary Utilities', 'install': 'binutils'},
                {'name': 'Autoconf', 'command': 'autoconf', 'description': 'GNU Autoconf', 'install': 'autoconf'},
                {'name': 'Automake', 'command': 'automake', 'description': 'GNU Automake', 'install': 'automake'},
                {'name': 'Libtool', 'command': 'libtool', 'description': 'GNU Libtool', 'install': 'libtool'},
                {'name': 'Bison', 'command': 'bison', 'description': 'GNU Parser Generator', 'install': 'bison'},
                {'name': 'Flex', 'command': 'flex', 'description': 'Fast Lexical Analyzer', 'install': 'flex'},
                {'name': 'M4', 'command': 'm4', 'description': 'GNU M4 Macro Processor', 'install': 'm4'},
                {'name': 'Gettext', 'command': 'gettext', 'description': 'GNU Internationalization', 'install': 'gettext'},
                {'name': 'Patch', 'command': 'patch', 'description': 'GNU Patch', 'install': 'patch'},
                {'name': 'Diff', 'command': 'diff', 'description': 'GNU Diff', 'install': 'diffutils'},
                {'name': 'Grep', 'command': 'grep', 'description': 'GNU Grep', 'install': 'grep'},
                {'name': 'Sed', 'command': 'sed', 'description': 'GNU Stream Editor', 'install': 'sed'},
                {'name': 'Awk', 'command': 'gawk', 'description': 'GNU AWK', 'install': 'gawk'},
                {'name': 'Tar', 'command': 'tar', 'description': 'GNU Tar', 'install': 'tar'},
                {'name': 'Gzip', 'command': 'gzip', 'description': 'GNU Gzip', 'install': 'gzip'},
            ],
            'build_tools': [
                {'name': 'CMake', 'command': 'cmake', 'description': 'Cross-platform build system', 'install': 'cmake'},
                {'name': 'Ninja', 'command': 'ninja', 'description': 'Fast build system', 'install': 'ninja-build'},
                {'name': 'Meson', 'command': 'meson', 'description': 'Modern build system', 'install': 'meson'},
                {'name': 'SCons', 'command': 'scons', 'description': 'Software construction tool', 'install': 'scons'},
                {'name': 'Bazel', 'command': 'bazel', 'description': 'Google build tool', 'install': 'bazel'},
                {'name': 'Gradle', 'command': 'gradle', 'description': 'Build automation tool', 'install': 'gradle'},
                {'name': 'Maven', 'command': 'mvn', 'description': 'Apache Maven', 'install': 'maven'},
                {'name': 'Ant', 'command': 'ant', 'description': 'Apache Ant', 'install': 'ant'},
            ],
            'version_control': [
                {'name': 'Git', 'command': 'git', 'description': 'Distributed version control', 'install': 'git'},
                {'name': 'Git LFS', 'command': 'git-lfs', 'description': 'Git Large File Storage', 'install': 'git-lfs'},
                {'name': 'Subversion', 'command': 'svn', 'description': 'Centralized version control', 'install': 'subversion'},
                {'name': 'Mercurial', 'command': 'hg', 'description': 'Distributed version control', 'install': 'mercurial'},
                {'name': 'CVS', 'command': 'cvs', 'description': 'Concurrent Versions System', 'install': 'cvs'},
            ],
            'languages': [
                {'name': 'Python 3', 'command': 'python3', 'description': 'Python programming language', 'install': 'python3'},
                {'name': 'Pip', 'command': 'pip3', 'description': 'Python package manager', 'install': 'python3-pip'},
                {'name': 'Node.js', 'command': 'node', 'description': 'JavaScript runtime', 'install': 'nodejs'},
                {'name': 'NPM', 'command': 'npm', 'description': 'Node package manager', 'install': 'npm'},
                {'name': 'Go', 'command': 'go', 'description': 'Go programming language', 'install': 'golang'},
                {'name': 'Rust', 'command': 'rustc', 'description': 'Rust programming language', 'install': 'rustc'},
                {'name': 'Cargo', 'command': 'cargo', 'description': 'Rust package manager', 'install': 'cargo'},
                {'name': 'Java', 'command': 'java', 'description': 'Java runtime', 'install': 'default-jdk'},
                {'name': 'Ruby', 'command': 'ruby', 'description': 'Ruby programming language', 'install': 'ruby'},
                {'name': 'Perl', 'command': 'perl', 'description': 'Perl programming language', 'install': 'perl'},
                {'name': 'PHP', 'command': 'php', 'description': 'PHP programming language', 'install': 'php'},
                {'name': 'Lua', 'command': 'lua', 'description': 'Lua programming language', 'install': 'lua5.4'},
                {'name': 'R', 'command': 'R', 'description': 'R statistical language', 'install': 'r-base'},
                {'name': 'Julia', 'command': 'julia', 'description': 'Julia programming language', 'install': 'julia'},
                {'name': 'Haskell', 'command': 'ghc', 'description': 'Glasgow Haskell Compiler', 'install': 'ghc'},
                {'name': 'Scala', 'command': 'scala', 'description': 'Scala programming language', 'install': 'scala'},
                {'name': 'Kotlin', 'command': 'kotlin', 'description': 'Kotlin programming language', 'install': 'kotlin'},
                {'name': 'Clojure', 'command': 'clj', 'description': 'Clojure programming language', 'install': 'clojure'},
            ],
            'containers': [
                {'name': 'Docker', 'command': 'docker', 'description': 'Container platform', 'install': 'docker.io'},
                {'name': 'Docker Compose', 'command': 'docker-compose', 'description': 'Multi-container Docker', 'install': 'docker-compose'},
                {'name': 'Podman', 'command': 'podman', 'description': 'Daemonless containers', 'install': 'podman'},
                {'name': 'Buildah', 'command': 'buildah', 'description': 'Container image builder', 'install': 'buildah'},
                {'name': 'Skopeo', 'command': 'skopeo', 'description': 'Container image utility', 'install': 'skopeo'},
                {'name': 'Kubernetes CLI', 'command': 'kubectl', 'description': 'Kubernetes control', 'install': 'kubectl'},
                {'name': 'Helm', 'command': 'helm', 'description': 'Kubernetes package manager', 'install': 'helm'},
                {'name': 'Minikube', 'command': 'minikube', 'description': 'Local Kubernetes', 'install': 'minikube'},
            ],
            'databases': [
                {'name': 'PostgreSQL', 'command': 'psql', 'description': 'PostgreSQL client', 'install': 'postgresql-client'},
                {'name': 'MySQL', 'command': 'mysql', 'description': 'MySQL client', 'install': 'mysql-client'},
                {'name': 'SQLite', 'command': 'sqlite3', 'description': 'SQLite database', 'install': 'sqlite3'},
                {'name': 'Redis CLI', 'command': 'redis-cli', 'description': 'Redis client', 'install': 'redis-tools'},
                {'name': 'MongoDB', 'command': 'mongosh', 'description': 'MongoDB shell', 'install': 'mongodb-mongosh'},
                {'name': 'CouchDB', 'command': 'couchdb', 'description': 'Apache CouchDB', 'install': 'couchdb'},
            ],
            'editors': [
                {'name': 'Vim', 'command': 'vim', 'description': 'Vi IMproved', 'install': 'vim'},
                {'name': 'Neovim', 'command': 'nvim', 'description': 'Hyperextensible Vim', 'install': 'neovim'},
                {'name': 'Emacs', 'command': 'emacs', 'description': 'GNU Emacs', 'install': 'emacs'},
                {'name': 'Nano', 'command': 'nano', 'description': 'Simple text editor', 'install': 'nano'},
                {'name': 'VS Code', 'command': 'code', 'description': 'Visual Studio Code', 'install': 'code'},
                {'name': 'Sublime Text', 'command': 'subl', 'description': 'Sublime Text editor', 'install': 'sublime-text'},
            ],
            'networking': [
                {'name': 'cURL', 'command': 'curl', 'description': 'Command line URL tool', 'install': 'curl'},
                {'name': 'Wget', 'command': 'wget', 'description': 'Network downloader', 'install': 'wget'},
                {'name': 'HTTPie', 'command': 'http', 'description': 'User-friendly HTTP client', 'install': 'httpie'},
                {'name': 'Netcat', 'command': 'nc', 'description': 'Network utility', 'install': 'netcat'},
                {'name': 'Nmap', 'command': 'nmap', 'description': 'Network scanner', 'install': 'nmap'},
                {'name': 'OpenSSH', 'command': 'ssh', 'description': 'Secure shell client', 'install': 'openssh-client'},
                {'name': 'OpenSSL', 'command': 'openssl', 'description': 'SSL/TLS toolkit', 'install': 'openssl'},
                {'name': 'Wireshark CLI', 'command': 'tshark', 'description': 'Network analyzer', 'install': 'tshark'},
            ],
            'utilities': [
                {'name': 'jq', 'command': 'jq', 'description': 'JSON processor', 'install': 'jq'},
                {'name': 'yq', 'command': 'yq', 'description': 'YAML processor', 'install': 'yq'},
                {'name': 'xmllint', 'command': 'xmllint', 'description': 'XML tool', 'install': 'libxml2-utils'},
                {'name': 'ripgrep', 'command': 'rg', 'description': 'Fast grep alternative', 'install': 'ripgrep'},
                {'name': 'fd', 'command': 'fd', 'description': 'Fast find alternative', 'install': 'fd-find'},
                {'name': 'fzf', 'command': 'fzf', 'description': 'Fuzzy finder', 'install': 'fzf'},
                {'name': 'bat', 'command': 'bat', 'description': 'Cat with syntax highlighting', 'install': 'bat'},
                {'name': 'exa', 'command': 'exa', 'description': 'Modern ls replacement', 'install': 'exa'},
                {'name': 'htop', 'command': 'htop', 'description': 'Interactive process viewer', 'install': 'htop'},
                {'name': 'tmux', 'command': 'tmux', 'description': 'Terminal multiplexer', 'install': 'tmux'},
                {'name': 'screen', 'command': 'screen', 'description': 'Terminal multiplexer', 'install': 'screen'},
                {'name': 'tree', 'command': 'tree', 'description': 'Directory tree viewer', 'install': 'tree'},
                {'name': 'ncdu', 'command': 'ncdu', 'description': 'Disk usage analyzer', 'install': 'ncdu'},
                {'name': 'strace', 'command': 'strace', 'description': 'System call tracer', 'install': 'strace'},
                {'name': 'ltrace', 'command': 'ltrace', 'description': 'Library call tracer', 'install': 'ltrace'},
                {'name': 'valgrind', 'command': 'valgrind', 'description': 'Memory debugger', 'install': 'valgrind'},
            ],
            'documentation': [
                {'name': 'Man Pages', 'command': 'man', 'description': 'Manual pages', 'install': 'man-db'},
                {'name': 'Info', 'command': 'info', 'description': 'GNU Info', 'install': 'info'},
                {'name': 'Texinfo', 'command': 'makeinfo', 'description': 'Documentation system', 'install': 'texinfo'},
                {'name': 'Doxygen', 'command': 'doxygen', 'description': 'Documentation generator', 'install': 'doxygen'},
                {'name': 'Sphinx', 'command': 'sphinx-build', 'description': 'Python documentation', 'install': 'python3-sphinx'},
                {'name': 'Pandoc', 'command': 'pandoc', 'description': 'Document converter', 'install': 'pandoc'},
            ],
        }
    
    def scan_tools(self) -> Dict[str, List[ToolInfo]]:
        """Scan system for installed development tools."""
        results = {}
        
        for category, tools in self.tool_definitions.items():
            results[category] = []
            for tool in tools:
                info = self._check_tool(tool, category)
                results[category].append(info)
                self.tools_cache[tool['command']] = info
        
        self.last_scan = datetime.now()
        return results
    
    def _check_tool(self, tool: dict, category: str) -> ToolInfo:
        """Check if a tool is installed and get its version."""
        command = tool['command']
        installed = False
        version = 'Not installed'
        
        try:
            # Check if command exists
            result = subprocess.run(
                ['which', command],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                installed = True
                # Try to get version
                version = self._get_tool_version(command)
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
        
        return ToolInfo(
            name=tool['name'],
            command=command,
            version=version,
            installed=installed,
            category=category,
            description=tool['description'],
            install_command=f"sudo apt install -y {tool['install']}"
        )
    
    def _get_tool_version(self, command: str) -> str:
        """Get version string for a tool."""
        version_flags = ['--version', '-version', '-V', 'version']
        
        for flag in version_flags:
            try:
                result = subprocess.run(
                    [command, flag],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout:
                    # Return first line of version output
                    return result.stdout.strip().split('\n')[0][:50]
            except:
                continue
        
        return 'Installed'
    
    def install_tool(self, package: str, use_sudo: bool = True) -> Dict:
        """Install a development tool via apt."""
        try:
            cmd = ['pkexec', 'apt-get', 'install', '-y', package] if use_sudo else ['apt-get', 'install', '-y', package]
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=600
            )
            
            if result.returncode == 0:
                return {'success': True, 'message': f'{package} installed successfully'}
            else:
                return {'success': False, 'message': result.stderr or 'Installation failed'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Installation timed out'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def install_gnu_essentials(self) -> Dict:
        """Install all essential GNU development tools."""
        packages = [
            'build-essential', 'gdb', 'autoconf', 'automake', 'libtool',
            'bison', 'flex', 'm4', 'gettext', 'patch', 'diffutils',
            'gawk', 'texinfo'
        ]
        
        try:
            cmd = ['pkexec', 'apt-get', 'install', '-y'] + packages
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=1200
            )
            
            if result.returncode == 0:
                return {'success': True, 'message': 'GNU essentials installed successfully'}
            else:
                return {'success': False, 'message': result.stderr or 'Installation failed'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def install_developer_bundle(self, bundle: str) -> Dict:
        """Install a predefined bundle of tools."""
        bundles = {
            'web_development': [
                'nodejs', 'npm', 'git', 'curl', 'httpie', 'jq'
            ],
            'python_development': [
                'python3', 'python3-pip', 'python3-venv', 'python3-dev',
                'build-essential', 'git'
            ],
            'c_cpp_development': [
                'build-essential', 'gdb', 'cmake', 'ninja-build',
                'valgrind', 'clang', 'clang-format', 'clang-tidy'
            ],
            'rust_development': [
                'curl', 'build-essential', 'git'
            ],
            'go_development': [
                'golang', 'git', 'build-essential'
            ],
            'java_development': [
                'default-jdk', 'maven', 'gradle', 'git'
            ],
            'devops': [
                'docker.io', 'docker-compose', 'git', 'curl', 'jq',
                'openssh-client', 'ansible'
            ],
            'database': [
                'postgresql-client', 'mysql-client', 'sqlite3',
                'redis-tools'
            ],
            'full_gnu_toolkit': [
                'build-essential', 'gdb', 'autoconf', 'automake',
                'libtool', 'bison', 'flex', 'm4', 'gettext',
                'patch', 'diffutils', 'gawk', 'texinfo', 'cmake',
                'ninja-build', 'meson', 'valgrind', 'strace', 'ltrace'
            ]
        }
        
        if bundle not in bundles:
            return {'success': False, 'message': f'Unknown bundle: {bundle}'}
        
        packages = bundles[bundle]
        
        try:
            cmd = ['pkexec', 'apt-get', 'install', '-y'] + packages
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=1200
            )
            
            if result.returncode == 0:
                return {'success': True, 'message': f'{bundle} bundle installed successfully'}
            else:
                return {'success': False, 'message': result.stderr or 'Installation failed'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_installed_count(self) -> Dict[str, int]:
        """Get count of installed tools by category."""
        if not self.tools_cache:
            self.scan_tools()
        
        counts = {}
        for category in self.tool_definitions.keys():
            tools = [t for t in self.tools_cache.values() if t.category == category]
            counts[category] = {
                'installed': sum(1 for t in tools if t.installed),
                'total': len(tools)
            }
        
        return counts
    
    def export_tool_list(self) -> List[Dict]:
        """Export tool list for UI consumption."""
        if not self.tools_cache:
            self.scan_tools()
        
        return [
            {
                'name': t.name,
                'command': t.command,
                'version': t.version,
                'installed': t.installed,
                'category': t.category,
                'description': t.description,
                'install_command': t.install_command
            }
            for t in self.tools_cache.values()
        ]
    
    def get_categories(self) -> List[str]:
        """Get list of tool categories."""
        return list(self.tool_definitions.keys())


# Singleton instance
_dev_toolkit: Optional[DeveloperToolkit] = None


def get_developer_toolkit() -> DeveloperToolkit:
    """Get the singleton Developer Toolkit instance."""
    global _dev_toolkit
    if _dev_toolkit is None:
        _dev_toolkit = DeveloperToolkit()
    return _dev_toolkit
