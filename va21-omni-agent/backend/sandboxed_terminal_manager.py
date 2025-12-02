"""
Sandboxed Terminal Manager - Multiple Sandboxed Terminal Support

This module provides management for multiple sandboxed terminal sessions,
including isolation, security controls, and session logging.

Note: PTY-based terminal functionality requires Unix-like systems (Linux, macOS).
Windows users should use alternative terminal solutions.
"""

import os
import sys
import select
import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable
from enum import Enum
import signal

# Platform-specific imports
IS_UNIX = sys.platform != 'win32'
if IS_UNIX:
    import pty


class TerminalStatus(Enum):
    """Status of a terminal session."""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class SandboxLevel(Enum):
    """Isolation level for sandbox."""
    MINIMAL = "minimal"  # Basic process isolation
    STANDARD = "standard"  # Network restrictions + process isolation
    STRICT = "strict"  # Full isolation including filesystem


@dataclass
class TerminalSession:
    """Represents a sandboxed terminal session."""
    session_id: str
    name: str
    sandbox_level: SandboxLevel
    pid: Optional[int] = None
    master_fd: Optional[int] = None
    status: TerminalStatus = TerminalStatus.STOPPED
    created_at: datetime = field(default_factory=datetime.now)
    command_history: List[Dict] = field(default_factory=list)
    output_buffer: str = ""
    working_directory: str = field(default_factory=lambda: os.getcwd())
    environment: Dict[str, str] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


class SandboxedTerminalManager:
    """
    Manages multiple sandboxed terminal sessions.
    
    Features:
    - Multiple concurrent terminal sessions
    - Configurable sandbox isolation levels
    - Session logging and history
    - Security controls and command filtering
    - Output callbacks for real-time updates
    """
    
    def __init__(self, vault_manager=None, max_sessions: int = 10):
        self.vault_manager = vault_manager
        self.max_sessions = max_sessions
        self.sessions: Dict[str, TerminalSession] = {}
        self.read_threads: Dict[str, threading.Thread] = {}
        self.output_callbacks: Dict[str, List[Callable]] = {}
        
        # Security configuration
        self.blocked_commands = [
            'rm -rf /',
            'dd if=',
            'mkfs',
            ':(){ :|:& };:',  # Fork bomb
        ]
        
        self.restricted_paths = [
            '/etc/passwd',
            '/etc/shadow',
            '/root',
        ]
    
    def create_session(self, name: str = None, 
                       sandbox_level: SandboxLevel = SandboxLevel.STANDARD,
                       working_directory: str = None,
                       environment: Dict[str, str] = None) -> TerminalSession:
        """
        Create a new sandboxed terminal session.
        
        Args:
            name: Session name (auto-generated if not provided)
            sandbox_level: Level of sandbox isolation
            working_directory: Initial working directory
            environment: Additional environment variables
            
        Returns:
            The created terminal session
        """
        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError(f"Maximum sessions ({self.max_sessions}) reached")
        
        session_id = str(uuid.uuid4())[:8]
        session = TerminalSession(
            session_id=session_id,
            name=name or f"Terminal-{session_id}",
            sandbox_level=sandbox_level,
            working_directory=working_directory or os.getcwd(),
            environment=environment or {}
        )
        
        self.sessions[session_id] = session
        self.output_callbacks[session_id] = []
        
        print(f"[TerminalManager] Created session: {session.name} ({session_id})")
        return session
    
    def start_session(self, session_id: str) -> bool:
        """
        Start a terminal session.
        
        Args:
            session_id: Session to start
            
        Returns:
            True if started successfully
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.sessions[session_id]
        
        if session.status == TerminalStatus.RUNNING:
            return True
        
        # Check platform compatibility
        if not IS_UNIX:
            print(f"[TerminalManager] PTY terminals not supported on Windows. Session {session_id} will run in limited mode.")
            session.status = TerminalStatus.ERROR
            session.metadata['error'] = 'Platform not supported'
            return False
        
        try:
            # Create a pseudo-terminal
            master_fd, slave_fd = pty.openpty()
            
            # Prepare environment
            env = os.environ.copy()
            env.update(session.environment)
            env['TERM'] = 'xterm-256color'
            env['VA21_SESSION_ID'] = session_id
            env['VA21_SANDBOX_LEVEL'] = session.sandbox_level.value
            
            # Fork a new process
            pid = os.fork()
            
            if pid == 0:
                # Child process
                os.close(master_fd)
                os.setsid()
                os.dup2(slave_fd, 0)
                os.dup2(slave_fd, 1)
                os.dup2(slave_fd, 2)
                os.close(slave_fd)
                
                # Change to working directory
                os.chdir(session.working_directory)
                
                # Apply sandbox restrictions
                self._apply_sandbox(session.sandbox_level)
                
                # Execute shell
                os.execvpe('/bin/bash', ['/bin/bash', '--norc'], env)
            else:
                # Parent process
                os.close(slave_fd)
                session.pid = pid
                session.master_fd = master_fd
                session.status = TerminalStatus.RUNNING
                
                # Start read thread
                read_thread = threading.Thread(
                    target=self._read_output,
                    args=(session_id,),
                    daemon=True
                )
                read_thread.start()
                self.read_threads[session_id] = read_thread
                
                print(f"[TerminalManager] Started session: {session.name} (PID: {pid})")
                return True
                
        except Exception as e:
            print(f"[TerminalManager] Failed to start session: {e}")
            session.status = TerminalStatus.ERROR
            return False
    
    def _apply_sandbox(self, level: SandboxLevel):
        """Apply sandbox restrictions to the child process."""
        if level == SandboxLevel.MINIMAL:
            # Basic process isolation - just new session
            pass
        elif level == SandboxLevel.STANDARD:
            # Restrict network access (if possible without root)
            try:
                # Set resource limits
                import resource
                # Limit CPU time to 3600 seconds
                resource.setrlimit(resource.RLIMIT_CPU, (3600, 3600))
                # Limit memory to 1GB
                resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
                # Limit file size to 100MB
                resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))
            except Exception:
                pass
        elif level == SandboxLevel.STRICT:
            try:
                import resource
                # Stricter limits
                resource.setrlimit(resource.RLIMIT_CPU, (1800, 1800))
                resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, 50 * 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
            except Exception:
                pass
    
    def _read_output(self, session_id: str):
        """Read output from terminal and notify callbacks."""
        session = self.sessions.get(session_id)
        if not session or session.master_fd is None:
            return
        
        try:
            while session.status == TerminalStatus.RUNNING:
                # Use select to check for available data
                ready, _, _ = select.select([session.master_fd], [], [], 0.1)
                if ready:
                    try:
                        data = os.read(session.master_fd, 4096)
                        if data:
                            output = data.decode('utf-8', errors='replace')
                            session.output_buffer += output
                            
                            # Notify callbacks
                            for callback in self.output_callbacks.get(session_id, []):
                                try:
                                    callback(session_id, output)
                                except Exception as e:
                                    print(f"[TerminalManager] Callback error: {e}")
                    except OSError:
                        break
        except Exception as e:
            print(f"[TerminalManager] Read error for {session_id}: {e}")
        finally:
            session.status = TerminalStatus.STOPPED
    
    def send_input(self, session_id: str, data: str) -> bool:
        """
        Send input to a terminal session.
        
        Args:
            session_id: Target session
            data: Input data to send
            
        Returns:
            True if sent successfully
        """
        session = self.sessions.get(session_id)
        if not session or session.status != TerminalStatus.RUNNING:
            return False
        
        # Security check
        if self._is_command_blocked(data):
            print(f"[TerminalManager] Blocked dangerous command: {data[:50]}")
            return False
        
        try:
            os.write(session.master_fd, data.encode('utf-8'))
            
            # Log command if it looks like a command (ends with newline)
            if data.endswith('\n') or data.endswith('\r'):
                session.command_history.append({
                    'command': data.strip(),
                    'timestamp': datetime.now().isoformat()
                })
            
            return True
        except Exception as e:
            print(f"[TerminalManager] Send error: {e}")
            return False
    
    def _is_command_blocked(self, command: str) -> bool:
        """Check if a command should be blocked."""
        command_lower = command.lower().strip()
        
        for blocked in self.blocked_commands:
            if blocked.lower() in command_lower:
                return True
        
        for path in self.restricted_paths:
            if path in command:
                return True
        
        return False
    
    def stop_session(self, session_id: str) -> bool:
        """
        Stop a terminal session.
        
        Args:
            session_id: Session to stop
            
        Returns:
            True if stopped successfully
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        try:
            if session.pid:
                os.kill(session.pid, signal.SIGTERM)
                os.waitpid(session.pid, 0)
            
            if session.master_fd:
                os.close(session.master_fd)
            
            session.status = TerminalStatus.STOPPED
            
            # Log session to vault
            if self.vault_manager and session.command_history:
                self.vault_manager.log_terminal_session(
                    terminal_id=session_id,
                    commands=session.command_history
                )
            
            print(f"[TerminalManager] Stopped session: {session.name}")
            return True
            
        except Exception as e:
            print(f"[TerminalManager] Stop error: {e}")
            session.status = TerminalStatus.ERROR
            return False
    
    def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a terminal session completely.
        
        Args:
            session_id: Session to destroy
            
        Returns:
            True if destroyed successfully
        """
        self.stop_session(session_id)
        
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.output_callbacks:
            del self.output_callbacks[session_id]
        if session_id in self.read_threads:
            del self.read_threads[session_id]
        
        return True
    
    def register_output_callback(self, session_id: str, callback: Callable):
        """Register a callback for terminal output."""
        if session_id in self.output_callbacks:
            self.output_callbacks[session_id].append(callback)
    
    def unregister_output_callback(self, session_id: str, callback: Callable):
        """Unregister an output callback."""
        if session_id in self.output_callbacks:
            self.output_callbacks[session_id] = [
                cb for cb in self.output_callbacks[session_id] if cb != callback
            ]
    
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get a terminal session by ID."""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[Dict]:
        """Get information about all sessions."""
        return [
            {
                'session_id': s.session_id,
                'name': s.name,
                'status': s.status.value,
                'sandbox_level': s.sandbox_level.value,
                'created_at': s.created_at.isoformat(),
                'command_count': len(s.command_history)
            }
            for s in self.sessions.values()
        ]
    
    def get_session_output(self, session_id: str, 
                           lines: int = None) -> Optional[str]:
        """
        Get the output buffer for a session.
        
        Args:
            session_id: Target session
            lines: Number of lines to return (None for all)
            
        Returns:
            Output buffer content
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if lines:
            output_lines = session.output_buffer.split('\n')
            return '\n'.join(output_lines[-lines:])
        
        return session.output_buffer
    
    def resize_terminal(self, session_id: str, rows: int, cols: int) -> bool:
        """
        Resize a terminal session.
        
        Args:
            session_id: Target session
            rows: Number of rows
            cols: Number of columns
            
        Returns:
            True if resized successfully
        """
        session = self.sessions.get(session_id)
        if not session or session.master_fd is None:
            return False
        
        try:
            import fcntl
            import struct
            import termios
            
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(session.master_fd, termios.TIOCSWINSZ, winsize)
            return True
        except Exception as e:
            print(f"[TerminalManager] Resize error: {e}")
            return False
    
    def cleanup(self):
        """Clean up all terminal sessions."""
        for session_id in list(self.sessions.keys()):
            self.destroy_session(session_id)
        print("[TerminalManager] Cleaned up all sessions")


# Example usage
if __name__ == '__main__':
    import time
    
    manager = SandboxedTerminalManager()
    
    # Create and start a session
    session = manager.create_session(name="Test Terminal")
    manager.start_session(session.session_id)
    
    # Register output callback
    def output_handler(sid, data):
        print(f"[{sid}] {data}", end='')
    
    manager.register_output_callback(session.session_id, output_handler)
    
    # Send some commands
    time.sleep(0.5)
    manager.send_input(session.session_id, "echo 'Hello from sandbox!'\n")
    time.sleep(0.5)
    manager.send_input(session.session_id, "pwd\n")
    time.sleep(0.5)
    
    # Get session info
    print("\nAll sessions:", manager.get_all_sessions())
    
    # Cleanup
    manager.cleanup()
