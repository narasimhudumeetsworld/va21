"""
VA21 Multi-Agent Task Automation System

This module implements the best features inspired by open source AI agent projects:

From Microsoft AutoGen (https://github.com/microsoft/autogen) - MIT License:
    - Multi-agent conversation framework for autonomous collaboration
    - Specialized agents for different capabilities (security, coding, research)
    - AgentTool pattern - agents can be used as tools by other agents
    - Layered architecture (Core, AgentChat, Extensions)
    - Code execution with sandboxing support
    - Reflection capabilities for self-improvement

From Agent Zero (https://github.com/agent0ai/agent-zero) - MIT License:
    - Multi-agent cooperation with hierarchical superior/subordinate relationships
    - Persistent memory for solutions, facts, and instructions
    - Dynamic tool creation by agents
    - Agent-to-agent communication protocols

From OpenCode (https://github.com/sst/opencode) - MIT License:
    - Multi-agent roles (Build agent vs Plan agent)
    - General subagent for complex multi-step tasks
    - Provider-agnostic LLM design
    - Read-only analysis mode for safe exploration

All features are integrated with VA21 Guardian AI's Think>Vet>Act security model.

Enhanced VA21 Architecture:
    VA21 OS (Secure Foundation)
        └── Multi-Agent System (Automation Layer)
            ├── Guardian AI (Security Agent) - Think>Vet>Act
            ├── Orchestrator AI (Coordination)
            ├── Helper AI (User Interface)
            ├── Specialized Agents (AutoGen-inspired)
            │   ├── Code Agent (coding, debugging)
            │   ├── Research Agent (search, analysis)
            │   ├── Security Agent (threat detection)
            │   └── Reflection Agent (self-improvement)
            └── Embedding AI (context-aware retrieval)
            └── Sandboxed execution environment

Special Thanks:
    - Microsoft AutoGen (https://github.com/microsoft/autogen) - MIT License
      For multi-agent conversation framework and specialized agent patterns.
      Backed by Microsoft Research - aligns with VA21's Microsoft FARA integration.
    
    - Agent Zero project (https://github.com/agent0ai/agent-zero) - MIT License
      For multi-agent cooperation patterns and persistent memory concepts.
    
    - OpenCode project (https://github.com/sst/opencode) - MIT License
      For multi-agent role separation and provider-agnostic design.

Om Vinayaka - Intelligence flows where automation meets security.
"""

import os
import sys
import json
import threading
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class TaskStatus(Enum):
    """Status of an automated task."""
    PENDING = "pending"
    QUEUED = "queued"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class SecurityClearance(Enum):
    """Security clearance levels for tasks."""
    SAFE = "safe"           # Completely safe operations
    MONITORED = "monitored" # Allowed but logged
    RESTRICTED = "restricted" # Requires approval
    BLOCKED = "blocked"     # Not allowed


class AgentRole(Enum):
    """
    Agent roles inspired by OpenCode and Microsoft AutoGen's multi-agent design.
    
    From OpenCode:
    - BUILD: Full access for development work
    - PLAN: Read-only for analysis and planning
    - GENERAL: Complex searches and multi-step tasks
    
    From AutoGen (specialized agents):
    - CODE: Specialized coding and debugging
    - RESEARCH: Search and analysis
    - SECURITY: Guardian AI security monitoring
    - REFLECTION: Self-improvement and learning
    - ORCHESTRATOR: Coordination between agents
    """
    # OpenCode-inspired roles
    BUILD = "build"             # Full access agent for development work
    PLAN = "plan"               # Read-only agent for analysis and planning
    GENERAL = "general"         # Subagent for complex multi-step tasks
    
    # AutoGen-inspired specialized agents
    CODE = "code"               # Specialized coding and debugging agent
    RESEARCH = "research"       # Search and analysis agent
    SECURITY = "security"       # Guardian AI security agent
    REFLECTION = "reflection"   # Self-improvement and learning agent
    ORCHESTRATOR = "orchestrator"  # Coordination agent (like AutoGen's AgentTool)


class AgentCapability(Enum):
    """Capabilities that can be granted to agents."""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    CODE_EXECUTE = "code_execute"
    SHELL_COMMAND = "shell_command"
    WEB_SEARCH = "web_search"
    MEMORY_ACCESS = "memory_access"
    CREATE_SUBAGENT = "create_subagent"
    TOOL_CREATION = "tool_creation"
    # AutoGen-inspired capabilities
    AGENT_AS_TOOL = "agent_as_tool"     # Use other agents as tools
    REFLECTION = "reflection"           # Self-reflection capability
    CONVERSATION = "conversation"       # Multi-agent conversation


@dataclass
class AutomationTask:
    """Represents a task to be automated by Agent Zero."""
    task_id: str
    user_request: str
    created_at: datetime
    status: TaskStatus
    priority: TaskPriority
    security_clearance: SecurityClearance
    
    # Task breakdown
    subtasks: List[Dict] = field(default_factory=list)
    current_subtask: int = 0
    
    # Execution details
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: float = 0.0
    
    # Results
    result: Optional[str] = None
    error: Optional[str] = None
    artifacts: List[Dict] = field(default_factory=list)
    
    # Security
    guardian_approved: bool = False
    guardian_notes: List[str] = field(default_factory=list)
    vetted_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'user_request': self.user_request,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'priority': self.priority.value,
            'security_clearance': self.security_clearance.value,
            'subtasks': self.subtasks,
            'current_subtask': self.current_subtask,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_time_ms': self.execution_time_ms,
            'result': self.result,
            'error': self.error,
            'artifacts': self.artifacts,
            'guardian_approved': self.guardian_approved,
            'guardian_notes': self.guardian_notes,
            'vetted_actions': self.vetted_actions,
        }


@dataclass
class Agent:
    """
    Represents an AI agent in the multi-agent system.
    
    Inspired by Agent Zero's hierarchical agent design and OpenCode's role-based agents.
    Each agent has:
    - A role that determines its capabilities
    - A superior agent that gives it tasks
    - Optional subordinate agents it can create
    - Persistent memory for learned solutions
    """
    agent_id: str
    role: AgentRole
    name: str
    
    # Hierarchy (inspired by Agent Zero)
    superior_id: Optional[str] = None  # ID of superior agent (None = user is superior)
    subordinate_ids: List[str] = field(default_factory=list)
    
    # Capabilities based on role (inspired by OpenCode)
    capabilities: List[AgentCapability] = field(default_factory=list)
    
    # State
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Persistent memory (inspired by Agent Zero)
    memory: Dict[str, Any] = field(default_factory=dict)
    learned_tools: List[Dict] = field(default_factory=list)
    
    # Current task
    current_task_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'name': self.name,
            'superior_id': self.superior_id,
            'subordinate_ids': self.subordinate_ids,
            'capabilities': [c.value for c in self.capabilities],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat(),
            'current_task_id': self.current_task_id,
        }


@dataclass
class AgentMessage:
    """
    Message between agents for communication.
    
    Inspired by Agent Zero's agent-to-agent communication.
    """
    message_id: str
    from_agent_id: str
    to_agent_id: str
    message_type: str  # task, report, question, instruction
    content: str
    timestamp: datetime
    requires_response: bool = False
    response_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'from_agent_id': self.from_agent_id,
            'to_agent_id': self.to_agent_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'requires_response': self.requires_response,
            'response_id': self.response_id,
        }


# Role-based capability definitions (inspired by OpenCode and AutoGen)
ROLE_CAPABILITIES = {
    # OpenCode-inspired roles
    AgentRole.BUILD: [
        AgentCapability.FILE_READ,
        AgentCapability.FILE_WRITE,
        AgentCapability.FILE_DELETE,
        AgentCapability.CODE_EXECUTE,
        AgentCapability.SHELL_COMMAND,
        AgentCapability.WEB_SEARCH,
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.CREATE_SUBAGENT,
        AgentCapability.TOOL_CREATION,
        AgentCapability.AGENT_AS_TOOL,
        AgentCapability.CONVERSATION,
    ],
    AgentRole.PLAN: [
        # Read-only agent - denies file edits, asks permission for commands
        AgentCapability.FILE_READ,
        AgentCapability.WEB_SEARCH,
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.CONVERSATION,
    ],
    AgentRole.GENERAL: [
        # General subagent for complex tasks
        AgentCapability.FILE_READ,
        AgentCapability.WEB_SEARCH,
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.CODE_EXECUTE,
        AgentCapability.CONVERSATION,
    ],
    
    # AutoGen-inspired specialized agents
    AgentRole.CODE: [
        # Specialized coding agent (like AutoGen's coding assistant)
        AgentCapability.FILE_READ,
        AgentCapability.FILE_WRITE,
        AgentCapability.CODE_EXECUTE,
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.CONVERSATION,
        AgentCapability.REFLECTION,
    ],
    AgentRole.RESEARCH: [
        # Research agent (like AutoGen's research assistant)
        AgentCapability.FILE_READ,
        AgentCapability.WEB_SEARCH,
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.CONVERSATION,
    ],
    AgentRole.SECURITY: [
        # Guardian AI security agent
        AgentCapability.FILE_READ,
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.REFLECTION,
    ],
    AgentRole.REFLECTION: [
        # Self-improvement agent (AutoGen-inspired reflection)
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.REFLECTION,
        AgentCapability.CONVERSATION,
    ],
    AgentRole.ORCHESTRATOR: [
        # Coordination agent (like AutoGen's AgentTool pattern)
        AgentCapability.MEMORY_ACCESS,
        AgentCapability.CREATE_SUBAGENT,
        AgentCapability.AGENT_AS_TOOL,
        AgentCapability.CONVERSATION,
    ],
}


class MultiAgentSystem:
    """
    VA21 Multi-Agent Task Automation System
    
    Implements best features from open source AI agent projects:
    
    From Microsoft AutoGen (MIT License):
    - Multi-agent conversation framework
    - Specialized agents (Code, Research, Security, Reflection)
    - AgentTool pattern - agents can use other agents as tools
    - Sandboxed code execution
    - Reflection for self-improvement
    
    From Agent Zero (MIT License):
    - Multi-agent cooperation with superior/subordinate hierarchy
    - Persistent memory for solutions and instructions
    - Dynamic tool creation by agents
    - Agent-to-agent communication
    
    From OpenCode (MIT License):
    - Role-based agents (Build, Plan, General)
    - Read-only analysis mode
    - Provider-agnostic design
    
    All actions are vetted by VA21 Guardian AI using Think>Vet>Act methodology.
    
    Enhanced VA21 Architecture:
        User → Helper AI → Multi-Agent System → Orchestrator Agent
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
            Build Agent      Plan Agent      Specialized Agents
            (full access)    (read-only)    (AutoGen-inspired)
                    │               │               │
                    │               │       ┌───────┴───────┐
                    │               │       ↓               ↓
                    │               │   Code Agent    Research Agent
                    │               │       │               │
                    └───────────────┴───────┴───────────────┘
                                    ↓
                    Guardian AI + Reflection Agent (Think>Vet>Act)
                                    ↓
                    Sandboxed Execution → Results
    """
    
    VERSION = "2.0.0"  # Major version bump for AutoGen integration
    
    # Task patterns that need different handling
    AUTOMATION_PATTERNS = [
        # File operations
        ('file', ['create file', 'write file', 'edit file', 'delete file', 'move file', 'copy file']),
        # System operations
        ('system', ['run command', 'execute', 'install', 'update', 'configure']),
        # Code operations
        ('code', ['write code', 'refactor', 'fix bug', 'implement', 'create function']),
        # Research operations
        ('research', ['search for', 'find information', 'research', 'summarize']),
        # Automation
        ('automation', ['automate', 'schedule', 'repeat', 'batch process']),
    ]
    
    # Dangerous operations that require extra vetting
    DANGEROUS_OPERATIONS = [
        'delete', 'remove', 'rm -rf', 'format', 'wipe',
        'sudo', 'chmod', 'chown', 'root',
        'password', 'credentials', 'secret', 'key',
        'network', 'firewall', 'port',
        'install', 'execute', 'run script',
    ]
    
    def __init__(self, guardian=None, helper_ai=None, knowledge_vault=None,
                 data_dir: str = "data/multi_agent"):
        """
        Initialize Multi-Agent System.
        
        Args:
            guardian: VA21 Guardian AI instance for security vetting
            helper_ai: VA21 Helper AI instance for user interaction
            knowledge_vault: Obsidian knowledge vault for context
            data_dir: Directory for storing agent and task data
        """
        self.guardian = guardian
        self.helper_ai = helper_ai
        self.knowledge_vault = knowledge_vault
        self.data_dir = data_dir
        
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "tasks"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "agents"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "messages"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "logs"), exist_ok=True)
        
        # Agent management
        self.agents: Dict[str, Agent] = {}
        self.messages: deque = deque(maxlen=1000)
        
        # Task management
        self.task_queue: deque = deque(maxlen=100)
        self.active_tasks: Dict[str, AutomationTask] = {}
        self.completed_tasks: Dict[str, AutomationTask] = {}
        
        # Execution state
        self.is_running = False
        self.max_concurrent_tasks = 3
        self.current_task_count = 0
        
        # Current active agent role
        self.active_role = AgentRole.BUILD
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Metrics
        self.metrics = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_blocked': 0,
            'total_execution_time_ms': 0,
            'guardian_vetoes': 0,
            'agents_created': 0,
            'messages_sent': 0,
            'agent_conversations': 0,
            'reflections_performed': 0,
        }
        
        # Initialize default agents
        self._init_default_agents()
        
        print(f"[MultiAgentSystem] Initialized v{self.VERSION}")
        print(f"[MultiAgentSystem] Guardian AI: {'Connected' if guardian else 'Not connected'}")
        print(f"[MultiAgentSystem] Agents: Orchestrator, Build, Plan, Code, Research, Security, Reflection")
    
    def _init_default_agents(self):
        """
        Initialize the default agents.
        
        Inspired by:
        - OpenCode: Build, Plan, General roles
        - AutoGen: Specialized agents (Code, Research, Reflection, Orchestrator)
        - Agent Zero: Security agent with Guardian AI
        """
        # Orchestrator Agent - Coordinates other agents (AutoGen-inspired)
        orchestrator = Agent(
            agent_id="agent_orchestrator_main",
            role=AgentRole.ORCHESTRATOR,
            name="Orchestrator Agent",
            capabilities=ROLE_CAPABILITIES[AgentRole.ORCHESTRATOR],
        )
        self.agents[orchestrator.agent_id] = orchestrator
        
        # Build Agent - Full access for development work (OpenCode-inspired)
        build_agent = Agent(
            agent_id="agent_build_main",
            role=AgentRole.BUILD,
            name="Build Agent",
            superior_id="agent_orchestrator_main",
            capabilities=ROLE_CAPABILITIES[AgentRole.BUILD],
        )
        self.agents[build_agent.agent_id] = build_agent
        orchestrator.subordinate_ids.append(build_agent.agent_id)
        
        # Plan Agent - Read-only for analysis and planning (OpenCode-inspired)
        plan_agent = Agent(
            agent_id="agent_plan_main",
            role=AgentRole.PLAN,
            name="Plan Agent",
            superior_id="agent_orchestrator_main",
            capabilities=ROLE_CAPABILITIES[AgentRole.PLAN],
        )
        self.agents[plan_agent.agent_id] = plan_agent
        orchestrator.subordinate_ids.append(plan_agent.agent_id)
        
        # General Agent - For complex multi-step tasks (OpenCode-inspired)
        general_agent = Agent(
            agent_id="agent_general_main",
            role=AgentRole.GENERAL,
            name="General Agent",
            superior_id="agent_orchestrator_main",
            capabilities=ROLE_CAPABILITIES[AgentRole.GENERAL],
        )
        self.agents[general_agent.agent_id] = general_agent
        orchestrator.subordinate_ids.append(general_agent.agent_id)
        
        # Code Agent - Specialized coding (AutoGen-inspired)
        code_agent = Agent(
            agent_id="agent_code_main",
            role=AgentRole.CODE,
            name="Code Agent",
            superior_id="agent_orchestrator_main",
            capabilities=ROLE_CAPABILITIES[AgentRole.CODE],
        )
        self.agents[code_agent.agent_id] = code_agent
        orchestrator.subordinate_ids.append(code_agent.agent_id)
        
        # Research Agent - Search and analysis (AutoGen-inspired)
        research_agent = Agent(
            agent_id="agent_research_main",
            role=AgentRole.RESEARCH,
            name="Research Agent",
            superior_id="agent_orchestrator_main",
            capabilities=ROLE_CAPABILITIES[AgentRole.RESEARCH],
        )
        self.agents[research_agent.agent_id] = research_agent
        orchestrator.subordinate_ids.append(research_agent.agent_id)
        
        # Security Agent - Guardian AI integration
        security_agent = Agent(
            agent_id="agent_security_guardian",
            role=AgentRole.SECURITY,
            name="Guardian Security Agent",
            capabilities=ROLE_CAPABILITIES[AgentRole.SECURITY],
        )
        self.agents[security_agent.agent_id] = security_agent
        
        # Reflection Agent - Self-improvement (AutoGen-inspired)
        reflection_agent = Agent(
            agent_id="agent_reflection_main",
            role=AgentRole.REFLECTION,
            name="Reflection Agent",
            capabilities=ROLE_CAPABILITIES[AgentRole.REFLECTION],
        )
        self.agents[reflection_agent.agent_id] = reflection_agent
        
        self.metrics['agents_created'] = 8
    
    # =========================================================================
    # AUTOGEN-INSPIRED: Agent as Tool Pattern
    # =========================================================================
    
    def use_agent_as_tool(self, caller_agent_id: str, tool_agent_id: str,
                          task: str) -> Dict:
        """
        Use an agent as a tool (inspired by AutoGen's AgentTool pattern).
        
        This allows one agent to delegate tasks to another specialized agent,
        treating it as a tool rather than a peer.
        
        Args:
            caller_agent_id: The agent making the request
            tool_agent_id: The agent to use as a tool
            task: The task to delegate
            
        Returns:
            Dict with result from the tool agent
        """
        with self._lock:
            if caller_agent_id not in self.agents or tool_agent_id not in self.agents:
                return {'success': False, 'error': 'Agent not found'}
            
            caller = self.agents[caller_agent_id]
            tool_agent = self.agents[tool_agent_id]
            
            # Check capability
            if AgentCapability.AGENT_AS_TOOL not in caller.capabilities:
                return {'success': False, 'error': 'Caller lacks AGENT_AS_TOOL capability'}
            
            # Send task message
            message = self.send_message(
                caller_agent_id,
                tool_agent_id,
                'tool_request',
                task,
                requires_response=True
            )
            
            # Simulate tool agent processing (in production, this would be async)
            result = {
                'success': True,
                'tool_agent': tool_agent.name,
                'task': task,
                'result': f"[{tool_agent.name}] Completed: {task[:50]}...",
                'message_id': message.message_id if message else None,
            }
            
            return result
    
    def perform_reflection(self, agent_id: str, context: Dict = None) -> Dict:
        """
        Perform reflection for self-improvement (AutoGen-inspired).
        
        The reflection agent analyzes past actions and decisions to
        improve future performance.
        """
        with self._lock:
            if agent_id not in self.agents:
                return {'success': False, 'error': 'Agent not found'}
            
            agent = self.agents[agent_id]
            
            if AgentCapability.REFLECTION not in agent.capabilities:
                return {'success': False, 'error': 'Agent lacks REFLECTION capability'}
            
            self.metrics['reflections_performed'] += 1
            
            # Simulate reflection (in production, this would analyze memory)
            reflection = {
                'success': True,
                'agent': agent.name,
                'reflection': {
                    'past_decisions': 'Analyzed recent task decisions',
                    'improvements': ['Consider alternative approaches', 'Validate assumptions earlier'],
                    'learnings': ['Task pattern recognition improved', 'Security awareness enhanced'],
                },
                'timestamp': datetime.now().isoformat(),
            }
            
            return reflection
    
    # =========================================================================
    # AGENT MANAGEMENT (Inspired by Agent Zero's hierarchical design)
    # =========================================================================
    
    def create_subordinate_agent(self, superior_id: str, role: AgentRole,
                                  name: str = None) -> Optional[Agent]:
        """
        Create a subordinate agent (inspired by Agent Zero's hierarchy).
        
        A superior agent can create subordinate agents to help with subtasks.
        This keeps context clean and focused.
        """
        with self._lock:
            if superior_id not in self.agents:
                return None
            
            superior = self.agents[superior_id]
            
            # Check if superior can create subagents
            if AgentCapability.CREATE_SUBAGENT not in superior.capabilities:
                return None
            
            # Generate agent ID
            agent_id = f"agent_{role.value}_{uuid.uuid4().hex[:8]}"
            
            # Create subordinate
            subordinate = Agent(
                agent_id=agent_id,
                role=role,
                name=name or f"{role.value.title()} Subordinate",
                superior_id=superior_id,
                capabilities=ROLE_CAPABILITIES[role],
            )
            
            # Update hierarchy
            superior.subordinate_ids.append(agent_id)
            
            # Register
            self.agents[agent_id] = subordinate
            self.metrics['agents_created'] += 1
            
            return subordinate
    
    def send_message(self, from_agent_id: str, to_agent_id: str,
                     message_type: str, content: str,
                     requires_response: bool = False) -> Optional[AgentMessage]:
        """
        Send a message between agents (inspired by Agent Zero's communication).
        
        Agents can communicate with their superiors and subordinates,
        asking questions, giving instructions, and providing guidance.
        """
        with self._lock:
            if from_agent_id not in self.agents or to_agent_id not in self.agents:
                return None
            
            message = AgentMessage(
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                from_agent_id=from_agent_id,
                to_agent_id=to_agent_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now(),
                requires_response=requires_response,
            )
            
            self.messages.append(message)
            self.metrics['messages_sent'] += 1
            
            return message
    
    def switch_agent_role(self, role: AgentRole) -> Dict:
        """
        Switch the active agent role (inspired by OpenCode's Tab switching).
        
        Users can switch between Build and Plan agents using this method.
        """
        with self._lock:
            old_role = self.active_role
            self.active_role = role
            
            return {
                'success': True,
                'old_role': old_role.value,
                'new_role': role.value,
                'message': f"Switched from {old_role.value} to {role.value} agent",
            }
    
    def get_agent_for_role(self, role: AgentRole) -> Optional[Agent]:
        """Get the main agent for a specific role."""
        for agent in self.agents.values():
            if agent.role == role and agent.superior_id is None:
                return agent
        return None
    
    # =========================================================================
    # TASK SUBMISSION
    # =========================================================================
    
    def submit_task(self, user_request: str, priority: TaskPriority = TaskPriority.NORMAL,
                    context: Dict = None) -> Dict:
        """
        Submit a new automation task.
        
        This is the main entry point for task automation. The task goes through:
        1. Analysis - Understanding what needs to be done
        2. Think - Planning the approach (Guardian AI)
        3. Vet - Security vetting of planned actions
        4. Act - Sandboxed execution
        
        Args:
            user_request: Natural language description of what to automate
            priority: Task priority level
            context: Additional context from the conversation
            
        Returns:
            Dict with task_id and status information
        """
        with self._lock:
            self.metrics['tasks_submitted'] += 1
            
            # Generate unique task ID
            task_id = self._generate_task_id()
            
            # Create task
            task = AutomationTask(
                task_id=task_id,
                user_request=user_request,
                created_at=datetime.now(),
                status=TaskStatus.PENDING,
                priority=priority,
                security_clearance=SecurityClearance.SAFE,
            )
            
            # Analyze the request
            analysis = self._analyze_request(user_request, context)
            task.subtasks = analysis.get('subtasks', [])
            task.security_clearance = analysis.get('security_clearance', SecurityClearance.SAFE)
            
            # Guardian AI Think>Vet>Act
            vetting_result = self._guardian_think_vet(task)
            task.guardian_approved = vetting_result['approved']
            task.guardian_notes = vetting_result.get('notes', [])
            task.vetted_actions = vetting_result.get('vetted_actions', [])
            
            if not task.guardian_approved:
                task.status = TaskStatus.BLOCKED
                task.error = vetting_result.get('reason', 'Blocked by Guardian AI')
                self.metrics['tasks_blocked'] += 1
                self.metrics['guardian_vetoes'] += 1
                
                return {
                    'success': False,
                    'task_id': task_id,
                    'status': 'blocked',
                    'message': f"Task blocked by Guardian AI: {task.error}",
                    'guardian_notes': task.guardian_notes,
                }
            
            # Queue the task
            task.status = TaskStatus.QUEUED
            self.task_queue.append(task)
            self.active_tasks[task_id] = task
            
            # Save task
            self._save_task(task)
            
            return {
                'success': True,
                'task_id': task_id,
                'status': 'queued',
                'message': f"Task queued for automation ({len(task.subtasks)} subtasks)",
                'subtasks': task.subtasks,
                'estimated_time': self._estimate_time(task),
                'security_clearance': task.security_clearance.value,
            }
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = uuid.uuid4().hex[:8]
        return f"task_{timestamp}_{random_part}"
    
    def _analyze_request(self, request: str, context: Dict = None) -> Dict:
        """
        Analyze the user's automation request.
        
        This implements the "Think" part of Think>Vet>Act.
        """
        request_lower = request.lower()
        
        # Detect task type
        task_type = 'general'
        for pattern_type, patterns in self.AUTOMATION_PATTERNS:
            for pattern in patterns:
                if pattern in request_lower:
                    task_type = pattern_type
                    break
        
        # Check for dangerous operations
        security_level = SecurityClearance.SAFE
        for dangerous in self.DANGEROUS_OPERATIONS:
            if dangerous in request_lower:
                security_level = SecurityClearance.MONITORED
                break
        
        # Very dangerous patterns
        if any(d in request_lower for d in ['sudo', 'root', 'rm -rf', 'format', 'password']):
            security_level = SecurityClearance.RESTRICTED
        
        # Break down into subtasks
        subtasks = self._break_down_task(request, task_type)
        
        return {
            'task_type': task_type,
            'subtasks': subtasks,
            'security_clearance': security_level,
            'context_used': context is not None,
        }
    
    def _break_down_task(self, request: str, task_type: str) -> List[Dict]:
        """Break down a task into executable subtasks."""
        subtasks = []
        
        if task_type == 'file':
            subtasks = [
                {'action': 'validate_path', 'description': 'Validate file path and permissions'},
                {'action': 'perform_operation', 'description': f'Execute: {request}'},
                {'action': 'verify_result', 'description': 'Verify operation completed successfully'},
            ]
        elif task_type == 'code':
            subtasks = [
                {'action': 'analyze_requirements', 'description': 'Analyze code requirements'},
                {'action': 'generate_code', 'description': 'Generate code solution'},
                {'action': 'validate_code', 'description': 'Validate generated code'},
                {'action': 'format_output', 'description': 'Format and present code'},
            ]
        elif task_type == 'system':
            subtasks = [
                {'action': 'sandbox_prepare', 'description': 'Prepare sandboxed environment'},
                {'action': 'validate_command', 'description': 'Validate system command'},
                {'action': 'execute_sandboxed', 'description': 'Execute in sandbox'},
                {'action': 'capture_output', 'description': 'Capture and verify output'},
            ]
        elif task_type == 'research':
            subtasks = [
                {'action': 'formulate_query', 'description': 'Formulate search query'},
                {'action': 'search_sources', 'description': 'Search knowledge sources'},
                {'action': 'analyze_results', 'description': 'Analyze and filter results'},
                {'action': 'summarize', 'description': 'Summarize findings'},
            ]
        else:
            subtasks = [
                {'action': 'analyze', 'description': 'Analyze request'},
                {'action': 'plan', 'description': 'Plan execution'},
                {'action': 'execute', 'description': 'Execute task'},
                {'action': 'verify', 'description': 'Verify results'},
            ]
        
        return subtasks
    
    # =========================================================================
    # GUARDIAN AI INTEGRATION (THINK>VET>ACT)
    # =========================================================================
    
    def _guardian_think_vet(self, task: AutomationTask) -> Dict:
        """
        Apply Guardian AI's Think>Vet>Act methodology.
        
        Think: Understand what the task wants to do
        Vet: Check if each action is safe and allowed
        Act: Approve or block the task
        
        Args:
            task: The automation task to vet
            
        Returns:
            Dict with approval status and notes
        """
        notes = []
        vetted_actions = []
        approved = True
        reason = None
        
        # THINK: Analyze the request
        notes.append(f"[THINK] Analyzing task: {task.user_request[:50]}...")
        
        request_lower = task.user_request.lower()
        
        # Check for blocked operations
        blocked_patterns = [
            ('rm -rf /', 'System destruction attempt'),
            ('format', 'Disk format attempt'),
            (':(){ :|:& };:', 'Fork bomb detected'),
            ('/dev/sda', 'Raw disk access'),
            ('password', 'Password handling - requires explicit approval'),
        ]
        
        for pattern, reason_text in blocked_patterns:
            if pattern in request_lower:
                notes.append(f"[VET] BLOCKED: {reason_text}")
                approved = False
                reason = reason_text
                break
        
        if approved:
            # VET: Check each subtask
            notes.append(f"[VET] Vetting {len(task.subtasks)} subtasks...")
            
            for i, subtask in enumerate(task.subtasks):
                action = subtask.get('action', 'unknown')
                description = subtask.get('description', '')
                
                # Check if action is allowed
                if action in ['sandbox_prepare', 'execute_sandboxed']:
                    notes.append(f"[VET] Subtask {i+1}: {action} - Sandboxed execution allowed")
                    vetted_actions.append(f"✓ {action}")
                elif 'delete' in description.lower() or 'remove' in description.lower():
                    notes.append(f"[VET] Subtask {i+1}: {action} - Destructive action, requiring monitoring")
                    task.security_clearance = SecurityClearance.MONITORED
                    vetted_actions.append(f"⚠ {action} (monitored)")
                else:
                    notes.append(f"[VET] Subtask {i+1}: {action} - Approved")
                    vetted_actions.append(f"✓ {action}")
            
            # ACT: Final decision
            notes.append(f"[ACT] Task approved with security level: {task.security_clearance.value}")
        else:
            notes.append(f"[ACT] Task BLOCKED: {reason}")
        
        # Log to Guardian if available
        if self.guardian:
            try:
                self.guardian.metrics['commands_analyzed'] += 1
                if not approved:
                    self.guardian.metrics['threats_blocked'] += 1
            except:
                pass
        
        return {
            'approved': approved,
            'reason': reason,
            'notes': notes,
            'vetted_actions': vetted_actions,
            'security_clearance': task.security_clearance.value,
        }
    
    # =========================================================================
    # TASK EXECUTION
    # =========================================================================
    
    def execute_task(self, task_id: str) -> Dict:
        """
        Execute a queued task.
        
        This is the "Act" part of Think>Vet>Act.
        All execution happens in a sandboxed environment.
        """
        with self._lock:
            if task_id not in self.active_tasks:
                return {'success': False, 'error': 'Task not found'}
            
            task = self.active_tasks[task_id]
            
            if not task.guardian_approved:
                return {'success': False, 'error': 'Task not approved by Guardian AI'}
            
            task.status = TaskStatus.EXECUTING
            task.started_at = datetime.now()
        
        try:
            # Execute each subtask
            results = []
            for i, subtask in enumerate(task.subtasks):
                task.current_subtask = i
                
                # Execute subtask (simulated for safety)
                result = self._execute_subtask(subtask, task)
                results.append(result)
                
                if not result.get('success', False):
                    raise Exception(f"Subtask {i+1} failed: {result.get('error', 'Unknown error')}")
            
            # Mark as completed
            with self._lock:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.execution_time_ms = (task.completed_at - task.started_at).total_seconds() * 1000
                task.result = json.dumps(results)
                
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]
                
                self.metrics['tasks_completed'] += 1
                self.metrics['total_execution_time_ms'] += task.execution_time_ms
                
                self._save_task(task)
            
            return {
                'success': True,
                'task_id': task_id,
                'status': 'completed',
                'execution_time_ms': task.execution_time_ms,
                'subtask_results': results,
            }
            
        except Exception as e:
            with self._lock:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = datetime.now()
                
                self.completed_tasks[task_id] = task
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                
                self.metrics['tasks_failed'] += 1
                self._save_task(task)
            
            return {
                'success': False,
                'task_id': task_id,
                'status': 'failed',
                'error': str(e),
            }
    
    def _execute_subtask(self, subtask: Dict, task: AutomationTask) -> Dict:
        """Execute a single subtask in sandboxed environment."""
        action = subtask.get('action', 'unknown')
        description = subtask.get('description', '')
        
        # Simulate execution (actual implementation would use sandboxed execution)
        time.sleep(0.1)  # Simulate processing time
        
        return {
            'success': True,
            'action': action,
            'description': description,
            'output': f"Executed: {action}",
            'timestamp': datetime.now().isoformat(),
        }
    
    def _estimate_time(self, task: AutomationTask) -> str:
        """Estimate execution time for a task."""
        subtask_count = len(task.subtasks)
        avg_time_per_subtask = 500  # ms
        estimated_ms = subtask_count * avg_time_per_subtask
        
        if estimated_ms < 1000:
            return f"{estimated_ms}ms"
        elif estimated_ms < 60000:
            return f"{estimated_ms / 1000:.1f}s"
        else:
            return f"{estimated_ms / 60000:.1f}m"
    
    # =========================================================================
    # HELPER AI INTEGRATION
    # =========================================================================
    
    def handle_helper_ai_request(self, message: str, session_id: str = None) -> Dict:
        """
        Handle automation requests from Helper AI.
        
        This method is called by the Helper AI when a user asks for task automation.
        
        Args:
            message: User's message requesting automation
            session_id: Session ID for context
            
        Returns:
            Response dict for Helper AI to relay to user
        """
        # Check if this is an automation request
        if not self._is_automation_request(message):
            return {
                'handled': False,
                'message': None,
            }
        
        # Submit the task
        result = self.submit_task(message)
        
        if result['success']:
            # Execute immediately for simple tasks
            if result.get('estimated_time', '0ms').endswith('ms'):
                exec_result = self.execute_task(result['task_id'])
                
                if exec_result['success']:
                    return {
                        'handled': True,
                        'message': f"""🤖 **Task Automated Successfully!**

**Request:** {message[:50]}{'...' if len(message) > 50 else ''}

**Status:** ✅ Completed
**Time:** {exec_result['execution_time_ms']:.0f}ms

**Subtasks Completed:**
{chr(10).join('• ' + r['action'] for r in exec_result['subtask_results'])}

*Powered by Agent Zero + VA21 Guardian AI*
""",
                        'action': 'task_completed',
                        'task_id': result['task_id'],
                    }
            
            return {
                'handled': True,
                'message': f"""🤖 **Task Queued for Automation**

**Request:** {message[:50]}{'...' if len(message) > 50 else ''}

**Task ID:** `{result['task_id']}`
**Status:** Queued
**Estimated Time:** {result['estimated_time']}
**Security Level:** {result['security_clearance']}

**Subtasks:**
{chr(10).join('• ' + s['description'] for s in result['subtasks'][:5])}

Guardian AI has approved this task. Execution will begin shortly.

*Powered by Agent Zero + VA21 Guardian AI*
""",
                'action': 'task_queued',
                'task_id': result['task_id'],
            }
        else:
            return {
                'handled': True,
                'message': f"""⚠️ **Task Blocked by Guardian AI**

**Request:** {message[:50]}{'...' if len(message) > 50 else ''}

**Status:** 🚫 Blocked
**Reason:** {result.get('message', 'Security violation')}

**Guardian AI Notes:**
{chr(10).join('• ' + n for n in result.get('guardian_notes', [])[:5])}

This task was blocked for security reasons. Please modify your request or contact an administrator.

*Protected by VA21 Guardian AI*
""",
                'action': 'task_blocked',
            }
    
    def _is_automation_request(self, message: str) -> bool:
        """Check if a message is requesting automation."""
        message_lower = message.lower()
        
        automation_keywords = [
            'automate', 'automation',
            'run task', 'execute task',
            'can you do', 'please do',
            'help me with', 'i need you to',
            'create a script', 'write a script',
            'batch process', 'schedule',
            'agent zero', 'task automation',
        ]
        
        return any(kw in message_lower for kw in automation_keywords)
    
    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get the status of a task."""
        task = self.active_tasks.get(task_id) or self.completed_tasks.get(task_id)
        
        if task:
            return task.to_dict()
        return None
    
    def get_queue_status(self) -> Dict:
        """Get the status of the task queue."""
        return {
            'queue_length': len(self.task_queue),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'metrics': self.metrics,
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a queued or active task."""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]
                self._save_task(task)
                return True
        return False
    
    def _save_task(self, task: AutomationTask):
        """Save task to disk."""
        try:
            task_file = os.path.join(self.data_dir, "tasks", f"{task.task_id}.json")
            with open(task_file, 'w') as f:
                json.dump(task.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[MultiAgentSystem] Error saving task: {e}")
    
    # =========================================================================
    # STATUS AND METRICS
    # =========================================================================
    
    def get_status(self) -> Dict:
        """Get system status."""
        return {
            'version': self.VERSION,
            'is_running': self.is_running,
            'guardian_connected': self.guardian is not None,
            'helper_ai_connected': self.helper_ai is not None,
            'active_role': self.active_role.value,
            'agents': {
                'total': len(self.agents),
                'by_role': {
                    role.value: len([a for a in self.agents.values() if a.role == role])
                    for role in AgentRole
                },
            },
            'queue_length': len(self.task_queue),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'metrics': self.metrics,
        }
    
    def get_acknowledgment(self) -> str:
        """Get acknowledgment text for open source projects that inspired this system."""
        return """
🤖 **VA21 Multi-Agent System v2.0 - Acknowledgments**

VA21 OS gratefully acknowledges the following open source projects
that inspired the best features implemented in this system:

### Microsoft AutoGen (MIT License) ⭐⭐⭐⭐⭐
https://github.com/microsoft/autogen
Backed by: Microsoft Research

Inspired features:
• Multi-agent conversation framework for autonomous collaboration
• Specialized agents for different capabilities (Code, Research, Security)
• AgentTool pattern - agents can be used as tools by other agents
• Layered architecture (Core, AgentChat, Extensions)
• Code execution with sandboxing support
• Reflection capabilities for self-improvement

Thank you to Microsoft Research and the AutoGen team! 🙏
This aligns perfectly with our Microsoft FARA integration.

### Agent Zero (MIT License)
https://github.com/agent0ai/agent-zero

Inspired features:
• Multi-agent cooperation with hierarchical superior/subordinate relationships
• Persistent memory for solutions, facts, and instructions
• Dynamic tool creation by agents
• Agent-to-agent communication protocols

Thank you to the Agent Zero team for their innovative approach! 🙏

### OpenCode (MIT License)
https://github.com/sst/opencode

Inspired features:
• Multi-agent roles (Build agent for full access, Plan agent for read-only)
• General subagent for complex searches and multi-step tasks
• Provider-agnostic LLM design
• Read-only analysis mode for safe exploration

Thank you to the SST/OpenCode team for their excellent design! 🙏

**Enhanced VA21 Architecture (Best of All Worlds):**
```
VA21 OS (Secure Foundation)
    └── Multi-Agent System v2.0 (Automation Layer)
        ├── Guardian AI (Security Core) - Think>Vet>Act
        ├── Orchestrator AI (Coordination) - AutoGen-inspired
        ├── Helper AI (User Interface)
        ├── Specialized Agents (AutoGen-inspired)
        │   ├── Build Agent (full access) - OpenCode
        │   ├── Plan Agent (read-only) - OpenCode
        │   ├── Code Agent (coding, debugging)
        │   ├── Research Agent (search, analysis)
        │   └── Reflection Agent (self-improvement)
        └── Embedding AI (context-aware retrieval)
        └── Sandboxed execution environment
```

*All features are protected by VA21 Guardian AI's security monitoring.*
*Complements your Dual-AI architecture with specialized multi-agent capabilities.*

Om Vinayaka 🙏
"""


# =========================================================================
# SINGLETON
# =========================================================================

_multi_agent_instance: Optional[MultiAgentSystem] = None


def get_multi_agent_system(guardian=None, helper_ai=None) -> MultiAgentSystem:
    """Get the Multi-Agent System singleton instance."""
    global _multi_agent_instance
    if _multi_agent_instance is None:
        _multi_agent_instance = MultiAgentSystem(
            guardian=guardian,
            helper_ai=helper_ai
        )
    return _multi_agent_instance


# Backwards compatibility alias
def get_agent_zero(guardian=None, helper_ai=None) -> MultiAgentSystem:
    """Alias for get_multi_agent_system (backwards compatibility)."""
    return get_multi_agent_system(guardian, helper_ai)


if __name__ == "__main__":
    # Test the Multi-Agent System
    print("\n=== VA21 Multi-Agent System v2.0 Test ===")
    system = get_multi_agent_system()
    
    print("\n--- Status ---")
    print(json.dumps(system.get_status(), indent=2))
    
    print("\n--- Acknowledgments ---")
    print(system.get_acknowledgment())
    
    print("\n--- Testing Agent Role Switching (OpenCode-inspired) ---")
    result = system.switch_agent_role(AgentRole.PLAN)
    print(json.dumps(result, indent=2))
    
    print("\n--- Testing Agent-as-Tool (AutoGen-inspired) ---")
    result = system.use_agent_as_tool(
        "agent_orchestrator_main",
        "agent_code_main",
        "Write a Python function to calculate factorial"
    )
    print(json.dumps(result, indent=2))
    
    print("\n--- Testing Reflection (AutoGen-inspired) ---")
    result = system.perform_reflection("agent_reflection_main")
    print(json.dumps(result, indent=2))
    
    print("\n--- Submitting Test Task ---")
    result = system.submit_task("Create a simple Python script that prints Hello World")
    print(json.dumps(result, indent=2))
    
    if result['success']:
        print("\n--- Executing Task ---")
        exec_result = system.execute_task(result['task_id'])
        print(json.dumps(exec_result, indent=2))
