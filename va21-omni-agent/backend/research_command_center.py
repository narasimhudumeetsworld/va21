"""
Research Command Center Backend Extensions

This module provides Socket.IO namespaces and API endpoints for the
Research Command Center, including terminal management, vault operations,
and enhanced orchestrator integration.
"""

import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_socketio import Namespace, emit

# Import the new modules
from obsidian_vault_manager import ObsidianVaultManager
from sandboxed_terminal_manager import SandboxedTerminalManager, SandboxLevel
from enhanced_orchestrator import EnhancedOrchestrator, TaskPriority
from sensitive_info_redactor import SensitiveInfoRedactor
from advanced_self_healing import AdvancedSelfHealing

# Initialize components
vault_manager = ObsidianVaultManager()
terminal_manager = SandboxedTerminalManager(vault_manager=vault_manager)
redactor = SensitiveInfoRedactor()


def create_orchestrator(settings, ltm_manager=None, local_llm=None):
    """Create and configure the enhanced orchestrator."""
    orchestrator = EnhancedOrchestrator(
        llm_provider=local_llm,
        vault_manager=vault_manager,
        settings=settings
    )
    return orchestrator


def create_self_healing(ltm_manager=None):
    """Create and configure the self-healing system."""
    healing = AdvancedSelfHealing(
        ltm_manager=ltm_manager,
        vault_manager=vault_manager
    )
    
    # Add critical files to monitor
    critical_files = [
        "app.py",
        "local_llm.py",
        "security_prompt_manager.py",
        "threat_intelligence.py"
    ]
    
    for f in critical_files:
        if os.path.exists(f):
            healing.add_monitored_file(f)
    
    # Create initial snapshot
    healing.create_snapshot(["."], {"type": "initial"})
    
    return healing


class TerminalsNamespace(Namespace):
    """Socket.IO namespace for sandboxed terminal management."""
    
    def on_connect(self):
        print(f'[Terminals] Client connected: {request.sid}')
        # Send list of existing sessions
        sessions = terminal_manager.get_all_sessions()
        self.emit('sessions_list', sessions)
    
    def on_disconnect(self):
        print(f'[Terminals] Client disconnected: {request.sid}')
    
    def on_create_terminal(self, data):
        """Create a new sandboxed terminal session."""
        try:
            name = data.get('name', f'Terminal-{len(terminal_manager.sessions) + 1}')
            sandbox_level = data.get('sandbox_level', 'standard')
            
            level = SandboxLevel[sandbox_level.upper()] if sandbox_level else SandboxLevel.STANDARD
            
            session = terminal_manager.create_session(
                name=name,
                sandbox_level=level
            )
            
            # Register output callback for this session
            def output_callback(sid, output):
                self.emit('terminal_output', {
                    'terminal_id': session.session_id,
                    'output': output
                })
            
            terminal_manager.register_output_callback(session.session_id, output_callback)
            
            # Start the session
            terminal_manager.start_session(session.session_id)
            
            self.emit('terminal_created', {
                'id': session.session_id,
                'name': session.name,
                'sandbox_level': session.sandbox_level.value,
                'status': session.status.value
            })
            
        except Exception as e:
            print(f'[Terminals] Error creating terminal: {e}')
            self.emit('error', {'message': str(e)})
    
    def on_terminal_input(self, data):
        """Send input to a terminal session."""
        terminal_id = data.get('terminal_id')
        input_data = data.get('input', '')
        
        if terminal_id and input_data:
            # Redact sensitive information from logs
            redacted = redactor.redact(input_data)
            
            success = terminal_manager.send_input(terminal_id, input_data)
            if not success:
                self.emit('error', {
                    'terminal_id': terminal_id,
                    'message': 'Failed to send input'
                })
    
    def on_destroy_terminal(self, data):
        """Destroy a terminal session."""
        terminal_id = data.get('terminal_id')
        
        if terminal_id:
            terminal_manager.destroy_session(terminal_id)
            self.emit('terminal_destroyed', {'terminal_id': terminal_id})
    
    def on_resize_terminal(self, data):
        """Resize a terminal session."""
        terminal_id = data.get('terminal_id')
        rows = data.get('rows', 24)
        cols = data.get('cols', 80)
        
        if terminal_id:
            terminal_manager.resize_terminal(terminal_id, rows, cols)
    
    def on_get_sessions(self):
        """Get all terminal sessions."""
        sessions = terminal_manager.get_all_sessions()
        self.emit('sessions_list', sessions)


class ResearchNamespace(Namespace):
    """Socket.IO namespace for research command center operations."""
    
    def on_connect(self):
        print(f'[Research] Client connected: {request.sid}')
    
    def on_disconnect(self):
        print(f'[Research] Client disconnected: {request.sid}')
    
    def on_get_graph_data(self):
        """Get knowledge graph data."""
        try:
            graph_data = vault_manager.get_graph_data()
            self.emit('graph_data', graph_data)
        except Exception as e:
            print(f'[Research] Error getting graph data: {e}')
            self.emit('graph_data', {'nodes': [], 'edges': []})
    
    def on_get_sessions(self):
        """Get research sessions."""
        try:
            sessions = vault_manager.search_vault("", note_type="session")
            self.emit('sessions_list', sessions)
        except Exception as e:
            print(f'[Research] Error getting sessions: {e}')
            self.emit('sessions_list', [])
    
    def on_get_memories(self):
        """Get LLM memories."""
        try:
            memories = vault_manager.search_vault("", note_type="memory")
            self.emit('memories_list', memories)
        except Exception as e:
            print(f'[Research] Error getting memories: {e}')
            self.emit('memories_list', [])
    
    def on_search_vault(self, data):
        """Search the vault."""
        query = data.get('query', '')
        note_type = data.get('note_type')
        
        try:
            results = vault_manager.search_vault(query, note_type)
            self.emit('search_results', results)
        except Exception as e:
            print(f'[Research] Error searching vault: {e}')
            self.emit('search_results', [])
    
    def on_get_note(self, data):
        """Get note content."""
        path = data.get('path')
        
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Redact sensitive information
                redacted = redactor.redact(content)
                
                self.emit('note_data', {
                    'path': path,
                    'content': redacted.redacted,
                    'redactions': redacted.metadata.get('total_redactions', 0)
                })
            except Exception as e:
                print(f'[Research] Error reading note: {e}')
                self.emit('note_data', None)
        else:
            self.emit('note_data', None)
    
    def on_create_research_session(self, data):
        """Create a new research session."""
        title = data.get('title', 'Untitled Research')
        objective = data.get('objective', '')
        topics = data.get('topics', [])
        
        try:
            path = vault_manager.create_research_session(
                title=title,
                objective=objective,
                topics=topics
            )
            
            self.emit('session_created', {
                'path': path,
                'title': title
            })
            
            # Refresh sessions list
            sessions = vault_manager.search_vault("", note_type="session")
            self.emit('sessions_list', sessions)
            
        except Exception as e:
            print(f'[Research] Error creating session: {e}')
            self.emit('error', {'message': str(e)})
    
    def on_add_memory(self, data):
        """Add an LLM memory entry."""
        session_id = data.get('session_id', 'default')
        context = data.get('context', '')
        key_facts = data.get('key_facts', [])
        related_topics = data.get('related_topics', [])
        
        try:
            path = vault_manager.add_llm_memory(
                session_id=session_id,
                context=context,
                key_facts=key_facts,
                related_topics=related_topics
            )
            
            self.emit('memory_added', {'path': path})
            
        except Exception as e:
            print(f'[Research] Error adding memory: {e}')
            self.emit('error', {'message': str(e)})
    
    def on_export_data(self):
        """Export vault data."""
        try:
            # Create export with redaction
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'graph': vault_manager.get_graph_data(),
                'sessions': vault_manager.search_vault("", note_type="session"),
                'memories': vault_manager.search_vault("", note_type="memory")
            }
            
            # Redact any sensitive information
            export_json = json.dumps(export_data, indent=2)
            redacted = redactor.redact(export_json)
            
            export_path = os.path.join(
                vault_manager.vault_path,
                f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(export_path, 'w') as f:
                f.write(redacted.redacted)
            
            self.emit('export_complete', {'path': export_path})
            
        except Exception as e:
            print(f'[Research] Error exporting data: {e}')
            self.emit('error', {'message': str(e)})


class OrchestratorNamespace(Namespace):
    """Socket.IO namespace for orchestrator operations."""
    
    def __init__(self, namespace, orchestrator=None):
        super().__init__(namespace)
        self.orchestrator = orchestrator
    
    def on_connect(self):
        print(f'[Orchestrator] Client connected: {request.sid}')
        if self.orchestrator:
            self.emit('status', self.orchestrator.get_queue_status())
    
    def on_disconnect(self):
        print(f'[Orchestrator] Client disconnected: {request.sid}')
    
    def on_submit_task(self, data):
        """Submit a task to the orchestrator."""
        if not self.orchestrator:
            self.emit('error', {'message': 'Orchestrator not initialized'})
            return
        
        agent_type = data.get('agent_type', 'research')
        prompt = data.get('prompt', '')
        priority_str = data.get('priority', 'NORMAL')
        
        try:
            priority = TaskPriority[priority_str.upper()]
        except KeyError:
            priority = TaskPriority.NORMAL
        
        def callback(task):
            self.emit('task_complete', {
                'task_id': task.task_id,
                'result': task.result,
                'status': task.status.value
            })
        
        task = self.orchestrator.create_task(
            agent_type=agent_type,
            prompt=prompt,
            priority=priority,
            callback=callback
        )
        
        self.emit('task_submitted', {
            'task_id': task.task_id,
            'status': task.status.value
        })
    
    def on_get_status(self):
        """Get orchestrator status."""
        if self.orchestrator:
            self.emit('status', {
                'queue': self.orchestrator.get_queue_status(),
                'agents': self.orchestrator.get_all_agent_statuses()
            })
    
    def on_start_research(self, data):
        """Start a coordinated research session."""
        if not self.orchestrator:
            self.emit('error', {'message': 'Orchestrator not initialized'})
            return
        
        topic = data.get('topic', '')
        depth = data.get('depth', 'normal')
        
        session_id = self.orchestrator.coordinate_research_session(topic, depth)
        
        self.emit('research_started', {'session_id': session_id})


class HealthNamespace(Namespace):
    """Socket.IO namespace for self-healing system operations."""
    
    def __init__(self, namespace, healing=None):
        super().__init__(namespace)
        self.healing = healing
    
    def on_connect(self):
        print(f'[Health] Client connected: {request.sid}')
        if self.healing:
            self.emit('health_status', self.healing.get_health_status())
    
    def on_disconnect(self):
        print(f'[Health] Client disconnected: {request.sid}')
    
    def on_get_health(self):
        """Get current health status."""
        if self.healing:
            self.emit('health_status', self.healing.get_health_status())
    
    def on_get_recovery_history(self, data):
        """Get recovery history."""
        limit = data.get('limit', 10)
        if self.healing:
            history = self.healing.get_recovery_history(limit)
            self.emit('recovery_history', history)
    
    def on_force_recovery(self, data):
        """Force a recovery action."""
        check_name = data.get('check_name')
        if self.healing and check_name:
            success = self.healing.force_recovery(check_name)
            self.emit('recovery_result', {
                'check_name': check_name,
                'success': success
            })
    
    def on_create_snapshot(self):
        """Create a system snapshot."""
        if self.healing:
            snapshot = self.healing.create_snapshot(["."])
            self.emit('snapshot_created', {
                'snapshot_id': snapshot.snapshot_id
            })


# API Blueprint for REST endpoints
research_api = Blueprint('research_api', __name__, url_prefix='/api/research')


@research_api.route('/vault/search', methods=['GET'])
def search_vault():
    """Search the vault via REST API."""
    query = request.args.get('q', '')
    note_type = request.args.get('type')
    
    results = vault_manager.search_vault(query, note_type)
    return jsonify(results)


@research_api.route('/vault/graph', methods=['GET'])
def get_graph():
    """Get knowledge graph data via REST API."""
    graph_data = vault_manager.get_graph_data()
    return jsonify(graph_data)


@research_api.route('/vault/session', methods=['POST'])
def create_session():
    """Create a research session via REST API."""
    data = request.get_json()
    
    path = vault_manager.create_research_session(
        title=data.get('title', 'Untitled'),
        objective=data.get('objective', ''),
        topics=data.get('topics', [])
    )
    
    return jsonify({'path': path, 'status': 'created'})


@research_api.route('/terminals', methods=['GET'])
def get_terminals():
    """Get all terminal sessions via REST API."""
    sessions = terminal_manager.get_all_sessions()
    return jsonify(sessions)


@research_api.route('/redact', methods=['POST'])
def redact_text():
    """Redact sensitive information from text."""
    data = request.get_json()
    text = data.get('text', '')
    categories = data.get('categories')
    
    result = redactor.redact(text, categories=categories)
    
    return jsonify({
        'redacted': result.redacted,
        'redaction_count': len(result.redactions)
    })


@research_api.route('/health', methods=['GET'])
def get_health():
    """Get system health status."""
    return jsonify({'status': 'healthy'})


def register_namespaces(socketio, settings=None, ltm_manager=None, local_llm=None):
    """Register all Socket.IO namespaces."""
    
    # Create orchestrator and healing system
    orchestrator = create_orchestrator(settings or {}, ltm_manager, local_llm)
    healing = create_self_healing(ltm_manager)
    
    # Start systems
    orchestrator.start()
    healing.start_monitoring()
    
    # Register namespaces
    socketio.on_namespace(TerminalsNamespace('/terminals'))
    socketio.on_namespace(ResearchNamespace('/research'))
    socketio.on_namespace(OrchestratorNamespace('/orchestrator', orchestrator))
    socketio.on_namespace(HealthNamespace('/health', healing))
    
    print("[ResearchCenter] All namespaces registered")
    
    return orchestrator, healing


def cleanup():
    """Cleanup resources on shutdown."""
    terminal_manager.cleanup()
    print("[ResearchCenter] Cleanup complete")
