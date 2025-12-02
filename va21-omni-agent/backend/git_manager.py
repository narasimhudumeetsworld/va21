"""
VA21 Git Manager - Comprehensive Git Integration

This module provides a complete Git integration for VA21 OS,
including repository management, commit history, branching, and more.
"""

import subprocess
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GitCommit:
    """Represents a Git commit."""
    hash: str
    short_hash: str
    author: str
    email: str
    date: str
    message: str
    branch: str


@dataclass
class GitBranch:
    """Represents a Git branch."""
    name: str
    is_current: bool
    is_remote: bool
    last_commit: str
    ahead: int = 0
    behind: int = 0


@dataclass
class GitStatus:
    """Represents Git repository status."""
    branch: str
    is_clean: bool
    staged: List[str]
    modified: List[str]
    untracked: List[str]
    conflicts: List[str]
    ahead: int
    behind: int


class GitManager:
    """
    VA21 Git Manager - Complete Git integration.
    
    Features:
    - Repository status and info
    - Commit history browsing
    - Branch management
    - Staging and committing
    - Push/Pull operations
    - Stash management
    - Diff viewing
    - Merge/Rebase support
    """
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()
        self._validate_git()
    
    def _validate_git(self) -> bool:
        """Check if Git is installed."""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _run_git(self, *args, cwd: str = None) -> tuple:
        """Run a Git command and return (success, output)."""
        try:
            result = subprocess.run(
                ['git'] + list(args),
                cwd=cwd or self.repo_path,
                capture_output=True, text=True, timeout=60
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, '', 'Command timed out'
        except Exception as e:
            return False, '', str(e)
    
    def is_repo(self, path: str = None) -> bool:
        """Check if path is a Git repository."""
        success, _, _ = self._run_git('rev-parse', '--git-dir', cwd=path or self.repo_path)
        return success
    
    def get_status(self) -> Optional[GitStatus]:
        """Get repository status."""
        if not self.is_repo():
            return None
        
        # Get current branch
        success, branch, _ = self._run_git('branch', '--show-current')
        if not success:
            branch = 'HEAD'
        
        # Get porcelain status
        success, status_output, _ = self._run_git('status', '--porcelain=v1')
        
        staged = []
        modified = []
        untracked = []
        conflicts = []
        
        for line in status_output.split('\n'):
            if not line:
                continue
            
            index_status = line[0]
            worktree_status = line[1]
            filename = line[3:]
            
            if 'U' in line[:2]:
                conflicts.append(filename)
            elif index_status in 'MADRC':
                staged.append(filename)
            elif worktree_status == 'M':
                modified.append(filename)
            elif index_status == '?':
                untracked.append(filename)
        
        # Get ahead/behind counts
        ahead, behind = 0, 0
        success, tracking, _ = self._run_git('rev-list', '--left-right', '--count', f'{branch}...@{{u}}')
        if success and tracking:
            parts = tracking.split('\t')
            if len(parts) == 2:
                ahead, behind = int(parts[0]), int(parts[1])
        
        return GitStatus(
            branch=branch,
            is_clean=len(staged) == 0 and len(modified) == 0 and len(untracked) == 0,
            staged=staged,
            modified=modified,
            untracked=untracked,
            conflicts=conflicts,
            ahead=ahead,
            behind=behind
        )
    
    def get_log(self, count: int = 50, branch: str = None) -> List[GitCommit]:
        """Get commit log."""
        if not self.is_repo():
            return []
        
        format_str = '%H|%h|%an|%ae|%ai|%s'
        args = ['log', f'--format={format_str}', f'-n{count}']
        
        if branch:
            args.append(branch)
        
        success, output, _ = self._run_git(*args)
        
        if not success:
            return []
        
        commits = []
        current_branch = self.get_current_branch()
        
        for line in output.split('\n'):
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 6:
                commits.append(GitCommit(
                    hash=parts[0],
                    short_hash=parts[1],
                    author=parts[2],
                    email=parts[3],
                    date=parts[4],
                    message='|'.join(parts[5:]),  # Message might contain |
                    branch=current_branch
                ))
        
        return commits
    
    def get_branches(self, include_remote: bool = True) -> List[GitBranch]:
        """Get list of branches."""
        if not self.is_repo():
            return []
        
        args = ['branch', '-v']
        if include_remote:
            args.append('-a')
        
        success, output, _ = self._run_git(*args)
        
        if not success:
            return []
        
        branches = []
        for line in output.split('\n'):
            if not line:
                continue
            
            is_current = line.startswith('*')
            line = line.lstrip('* ').strip()
            
            # Parse branch info
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                is_remote = name.startswith('remotes/')
                
                branches.append(GitBranch(
                    name=name.replace('remotes/', ''),
                    is_current=is_current,
                    is_remote=is_remote,
                    last_commit=parts[1] if len(parts) > 1 else ''
                ))
        
        return branches
    
    def get_current_branch(self) -> str:
        """Get current branch name."""
        success, branch, _ = self._run_git('branch', '--show-current')
        return branch if success else 'HEAD'
    
    def checkout(self, branch: str, create: bool = False) -> Dict:
        """Checkout a branch."""
        args = ['checkout']
        if create:
            args.append('-b')
        args.append(branch)
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def create_branch(self, name: str, start_point: str = None) -> Dict:
        """Create a new branch."""
        args = ['branch', name]
        if start_point:
            args.append(start_point)
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': f'Branch {name} created' if success else error
        }
    
    def delete_branch(self, name: str, force: bool = False) -> Dict:
        """Delete a branch."""
        args = ['branch', '-D' if force else '-d', name]
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': f'Branch {name} deleted' if success else error
        }
    
    def stage(self, files: List[str] = None) -> Dict:
        """Stage files for commit."""
        args = ['add']
        if files:
            args.extend(files)
        else:
            args.append('-A')
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': 'Files staged' if success else error
        }
    
    def unstage(self, files: List[str] = None) -> Dict:
        """Unstage files."""
        args = ['reset', 'HEAD']
        if files:
            args.extend(files)
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': 'Files unstaged' if success else error
        }
    
    def commit(self, message: str, amend: bool = False) -> Dict:
        """Create a commit."""
        args = ['commit', '-m', message]
        if amend:
            args.append('--amend')
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def push(self, remote: str = 'origin', branch: str = None, force: bool = False) -> Dict:
        """Push to remote."""
        args = ['push', remote]
        if branch:
            args.append(branch)
        if force:
            args.append('--force')
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def pull(self, remote: str = 'origin', branch: str = None, rebase: bool = False) -> Dict:
        """Pull from remote."""
        args = ['pull']
        if rebase:
            args.append('--rebase')
        args.append(remote)
        if branch:
            args.append(branch)
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def fetch(self, remote: str = 'origin', all_remotes: bool = False) -> Dict:
        """Fetch from remote."""
        args = ['fetch']
        if all_remotes:
            args.append('--all')
        else:
            args.append(remote)
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': 'Fetched successfully' if success else error
        }
    
    def diff(self, file: str = None, staged: bool = False, commit: str = None) -> str:
        """Get diff output."""
        args = ['diff']
        if staged:
            args.append('--staged')
        if commit:
            args.append(commit)
        if file:
            args.extend(['--', file])
        
        success, output, _ = self._run_git(*args)
        return output if success else ''
    
    def stash(self, message: str = None) -> Dict:
        """Stash changes."""
        args = ['stash', 'push']
        if message:
            args.extend(['-m', message])
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def stash_pop(self) -> Dict:
        """Pop stashed changes."""
        success, output, error = self._run_git('stash', 'pop')
        return {
            'success': success,
            'message': output if success else error
        }
    
    def stash_list(self) -> List[Dict]:
        """Get stash list."""
        success, output, _ = self._run_git('stash', 'list')
        
        if not success:
            return []
        
        stashes = []
        for line in output.split('\n'):
            if line:
                stashes.append({'entry': line})
        
        return stashes
    
    def merge(self, branch: str, no_ff: bool = False) -> Dict:
        """Merge a branch."""
        args = ['merge']
        if no_ff:
            args.append('--no-ff')
        args.append(branch)
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def rebase(self, branch: str, interactive: bool = False) -> Dict:
        """Rebase onto a branch."""
        args = ['rebase']
        if interactive:
            args.append('-i')
        args.append(branch)
        
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def reset(self, mode: str = 'mixed', commit: str = 'HEAD') -> Dict:
        """Reset to a commit."""
        args = ['reset', f'--{mode}', commit]
        success, output, error = self._run_git(*args)
        return {
            'success': success,
            'message': output if success else error
        }
    
    def clone(self, url: str, directory: str = None, depth: int = None) -> Dict:
        """Clone a repository."""
        args = ['clone', url]
        if directory:
            args.append(directory)
        if depth:
            args.extend(['--depth', str(depth)])
        
        success, output, error = self._run_git(*args, cwd=os.path.dirname(directory) if directory else None)
        return {
            'success': success,
            'message': 'Repository cloned' if success else error
        }
    
    def init(self, path: str = None) -> Dict:
        """Initialize a new repository."""
        success, output, error = self._run_git('init', cwd=path or self.repo_path)
        return {
            'success': success,
            'message': 'Repository initialized' if success else error
        }
    
    def get_remotes(self) -> List[Dict]:
        """Get list of remotes."""
        success, output, _ = self._run_git('remote', '-v')
        
        if not success:
            return []
        
        remotes = {}
        for line in output.split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    remotes[name] = {'name': name, 'url': url}
        
        return list(remotes.values())
    
    def add_remote(self, name: str, url: str) -> Dict:
        """Add a remote."""
        success, output, error = self._run_git('remote', 'add', name, url)
        return {
            'success': success,
            'message': f'Remote {name} added' if success else error
        }
    
    def get_file_history(self, file: str, count: int = 20) -> List[GitCommit]:
        """Get commit history for a specific file."""
        format_str = '%H|%h|%an|%ae|%ai|%s'
        success, output, _ = self._run_git(
            'log', f'--format={format_str}', f'-n{count}', '--', file
        )
        
        if not success:
            return []
        
        commits = []
        for line in output.split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 6:
                    commits.append(GitCommit(
                        hash=parts[0],
                        short_hash=parts[1],
                        author=parts[2],
                        email=parts[3],
                        date=parts[4],
                        message='|'.join(parts[5:]),
                        branch=''
                    ))
        
        return commits
    
    def blame(self, file: str) -> List[Dict]:
        """Get blame information for a file."""
        success, output, _ = self._run_git('blame', '--line-porcelain', file)
        
        if not success:
            return []
        
        # Parse blame output (simplified)
        lines = []
        current = {}
        
        for line in output.split('\n'):
            if line.startswith('\t'):
                current['content'] = line[1:]
                lines.append(current)
                current = {}
            elif ' ' in line:
                parts = line.split(' ', 1)
                key = parts[0]
                value = parts[1] if len(parts) > 1 else ''
                current[key] = value
        
        return lines
    
    def export_status_summary(self) -> Dict:
        """Export status summary for UI."""
        status = self.get_status()
        if not status:
            return {'is_repo': False}
        
        return {
            'is_repo': True,
            'branch': status.branch,
            'is_clean': status.is_clean,
            'staged_count': len(status.staged),
            'modified_count': len(status.modified),
            'untracked_count': len(status.untracked),
            'conflicts_count': len(status.conflicts),
            'ahead': status.ahead,
            'behind': status.behind,
            'staged': status.staged,
            'modified': status.modified,
            'untracked': status.untracked,
            'conflicts': status.conflicts
        }


# Factory function
def get_git_manager(repo_path: str = None) -> GitManager:
    """Get a Git manager for a repository."""
    return GitManager(repo_path)
