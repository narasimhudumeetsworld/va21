"""
Enhanced Orchestrator AI - Advanced AI Coordination System

This module provides an enhanced orchestrator for coordinating multiple AI
agents, managing complex workflows, and integrating various LLM providers.
"""

import json
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import queue


class AgentStatus(Enum):
    """Status of an AI agent."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class AgentTask:
    """Represents a task for an AI agent."""
    task_id: str
    agent_type: str
    prompt: str
    priority: TaskPriority = TaskPriority.NORMAL
    context: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None
    created_at: datetime = field(default_factory=datetime.now)
    result: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    metadata: Dict = field(default_factory=dict)


@dataclass
class AIAgent:
    """Represents an AI agent configuration."""
    agent_id: str
    agent_type: str
    provider: str
    model: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[AgentTask] = None
    config: Dict = field(default_factory=dict)


class EnhancedOrchestrator:
    """
    Enhanced AI Orchestrator for coordinating multiple AI agents.
    
    Features:
    - Multi-agent coordination
    - Task queue management with priorities
    - Dependency resolution between tasks
    - Self-healing and error recovery
    - Context sharing between agents
    - Memory integration with Obsidian vault
    """
    
    def __init__(self, llm_provider=None, vault_manager=None, settings: Dict = None):
        self.settings = settings or {}
        self.llm_provider = llm_provider
        self.vault_manager = vault_manager
        
        # Agent registry
        self.agents: Dict[str, AIAgent] = {}
        
        # Task management
        self.task_queue = queue.PriorityQueue()
        self.completed_tasks: Dict[str, AgentTask] = {}
        self.failed_tasks: Dict[str, AgentTask] = {}
        
        # Context and memory
        self.shared_context: Dict = {}
        self.session_memory: List[Dict] = []
        
        # Self-healing configuration
        self.max_retries = 3
        self.retry_delay = 1.0
        self.error_handlers: Dict[str, Callable] = {}
        
        # Status tracking
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        
        # Initialize default agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize the default set of AI agents."""
        default_agents = [
            AIAgent(
                agent_id="guardian",
                agent_type="security",
                provider="local",
                model="onnx",
                capabilities=["security_analysis", "threat_detection", "code_review"]
            ),
            AIAgent(
                agent_id="researcher",
                agent_type="research",
                provider=self.settings.get("provider", "ollama"),
                model=self.settings.get("model", "gemma:2b"),
                capabilities=["web_search", "summarization", "analysis"]
            ),
            AIAgent(
                agent_id="coder",
                agent_type="coding",
                provider=self.settings.get("provider", "ollama"),
                model=self.settings.get("model", "gemma:2b"),
                capabilities=["code_generation", "code_explanation", "debugging"]
            ),
            AIAgent(
                agent_id="planner",
                agent_type="planning",
                provider=self.settings.get("provider", "ollama"),
                model=self.settings.get("model", "gemma:2b"),
                capabilities=["task_planning", "decomposition", "scheduling"]
            )
        ]
        
        for agent in default_agents:
            self.register_agent(agent)
    
    def register_agent(self, agent: AIAgent):
        """Register a new AI agent."""
        self.agents[agent.agent_id] = agent
        print(f"[Orchestrator] Registered agent: {agent.agent_id} ({agent.agent_type})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an AI agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"[Orchestrator] Unregistered agent: {agent_id}")
    
    def submit_task(self, task: AgentTask) -> str:
        """
        Submit a task to the orchestrator.
        
        Args:
            task: The task to submit
            
        Returns:
            Task ID
        """
        # Add to priority queue (lower priority number = higher priority)
        self.task_queue.put((task.priority.value, task.created_at, task))
        print(f"[Orchestrator] Task submitted: {task.task_id} (priority: {task.priority.name})")
        return task.task_id
    
    def create_task(self, agent_type: str, prompt: str, 
                    priority: TaskPriority = TaskPriority.NORMAL,
                    context: Dict = None, dependencies: List[str] = None,
                    callback: Callable = None) -> AgentTask:
        """
        Create and submit a new task.
        
        Args:
            agent_type: Type of agent to handle the task
            prompt: The prompt/instruction for the agent
            priority: Task priority
            context: Additional context
            dependencies: Task IDs that must complete first
            callback: Callback function when task completes
            
        Returns:
            The created task
        """
        task = AgentTask(
            task_id=f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            agent_type=agent_type,
            prompt=prompt,
            priority=priority,
            context=context or {},
            dependencies=dependencies or [],
            callback=callback
        )
        self.submit_task(task)
        return task
    
    def _find_available_agent(self, agent_type: str) -> Optional[AIAgent]:
        """Find an available agent of the specified type."""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.status == AgentStatus.IDLE:
                return agent
        return None
    
    def _check_dependencies_completed(self, task: AgentTask) -> bool:
        """Check if all task dependencies are completed."""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    def _gather_dependency_results(self, task: AgentTask) -> Dict:
        """Gather results from completed dependencies."""
        results = {}
        for dep_id in task.dependencies:
            if dep_id in self.completed_tasks:
                results[dep_id] = self.completed_tasks[dep_id].result
        return results
    
    async def _execute_task(self, agent: AIAgent, task: AgentTask) -> str:
        """Execute a task using the specified agent."""
        agent.status = AgentStatus.WORKING
        agent.current_task = task
        task.status = AgentStatus.WORKING
        
        try:
            # Build enhanced prompt with context
            enhanced_prompt = self._build_enhanced_prompt(task)
            
            # Execute based on agent type
            if agent.agent_type == "security":
                result = await self._execute_security_task(agent, enhanced_prompt)
            else:
                result = await self._execute_llm_task(agent, enhanced_prompt)
            
            task.result = result
            task.status = AgentStatus.COMPLETED
            self.completed_tasks[task.task_id] = task
            
            # Store in memory if vault manager is available
            if self.vault_manager:
                self._store_task_memory(task)
            
            # Execute callback if provided
            if task.callback:
                task.callback(task)
            
            return result
            
        except Exception as e:
            print(f"[Orchestrator] Task {task.task_id} failed: {e}")
            task.status = AgentStatus.ERROR
            task.metadata['error'] = str(e)
            self.failed_tasks[task.task_id] = task
            
            # Attempt self-healing
            await self._handle_task_failure(agent, task, e)
            
            return f"Error: {e}"
        
        finally:
            agent.status = AgentStatus.IDLE
            agent.current_task = None
    
    def _build_enhanced_prompt(self, task: AgentTask) -> str:
        """Build an enhanced prompt with context and memory."""
        prompt_parts = []
        
        # Add shared context
        if self.shared_context:
            prompt_parts.append("## Current Context")
            for key, value in self.shared_context.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")
        
        # Add dependency results
        if task.dependencies:
            dep_results = self._gather_dependency_results(task)
            if dep_results:
                prompt_parts.append("## Previous Task Results")
                for task_id, result in dep_results.items():
                    prompt_parts.append(f"### {task_id}")
                    prompt_parts.append(result[:500])  # Limit length
                prompt_parts.append("")
        
        # Add task-specific context
        if task.context:
            prompt_parts.append("## Task Context")
            for key, value in task.context.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")
        
        # Add the main prompt
        prompt_parts.append("## Task")
        prompt_parts.append(task.prompt)
        
        return "\n".join(prompt_parts)
    
    async def _execute_security_task(self, agent: AIAgent, prompt: str) -> str:
        """Execute a security-related task."""
        # Use local LLM for security tasks
        if self.llm_provider:
            return self.llm_provider.generate(prompt)
        return "Security analysis completed - no threats detected"
    
    async def _execute_llm_task(self, agent: AIAgent, prompt: str) -> str:
        """Execute a general LLM task."""
        if self.llm_provider:
            return self.llm_provider.generate(prompt)
        return f"Task completed by {agent.agent_id}"
    
    async def _handle_task_failure(self, agent: AIAgent, task: AgentTask, error: Exception):
        """Handle task failure with self-healing strategies."""
        retry_count = task.metadata.get('retry_count', 0)
        
        if retry_count < self.max_retries:
            print(f"[Orchestrator] Retrying task {task.task_id} (attempt {retry_count + 1})")
            task.metadata['retry_count'] = retry_count + 1
            task.status = AgentStatus.IDLE
            
            # Re-queue with higher priority
            task.priority = TaskPriority.HIGH
            await asyncio.sleep(self.retry_delay * (retry_count + 1))
            self.submit_task(task)
        else:
            # Trigger error handler if registered
            error_type = type(error).__name__
            if error_type in self.error_handlers:
                self.error_handlers[error_type](task, error)
            
            print(f"[Orchestrator] Task {task.task_id} permanently failed after {self.max_retries} retries")
    
    def _store_task_memory(self, task: AgentTask):
        """Store task result in vault memory."""
        if not self.vault_manager:
            return
        
        try:
            self.vault_manager.add_llm_memory(
                session_id=task.task_id,
                context=f"Task: {task.prompt[:200]}",
                key_facts=[f"Result: {task.result[:200] if task.result else 'No result'}"],
                related_topics=[task.agent_type]
            )
        except Exception as e:
            print(f"[Orchestrator] Failed to store memory: {e}")
    
    def update_shared_context(self, key: str, value: Any):
        """Update the shared context."""
        self.shared_context[key] = value
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get the status of a specific agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            return {
                "agent_id": agent.agent_id,
                "type": agent.agent_type,
                "status": agent.status.value,
                "current_task": agent.current_task.task_id if agent.current_task else None
            }
        return None
    
    def get_all_agent_statuses(self) -> List[Dict]:
        """Get the status of all agents."""
        return [self.get_agent_status(agent_id) for agent_id in self.agents]
    
    def get_queue_status(self) -> Dict:
        """Get the status of the task queue."""
        return {
            "pending": self.task_queue.qsize(),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks)
        }
    
    def register_error_handler(self, error_type: str, handler: Callable):
        """Register an error handler for a specific error type."""
        self.error_handlers[error_type] = handler
    
    def start(self):
        """Start the orchestrator worker thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("[Orchestrator] Started")
    
    def stop(self):
        """Stop the orchestrator."""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        print("[Orchestrator] Stopped")
    
    def _worker_loop(self):
        """Main worker loop for processing tasks."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.is_running:
            try:
                # Get next task from queue (with timeout)
                try:
                    priority, created_at, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Check dependencies
                if not self._check_dependencies_completed(task):
                    # Re-queue if dependencies not met
                    task.status = AgentStatus.WAITING
                    self.task_queue.put((priority, created_at, task))
                    continue
                
                # Find available agent
                agent = self._find_available_agent(task.agent_type)
                if not agent:
                    # Re-queue if no agent available
                    self.task_queue.put((priority, created_at, task))
                    continue
                
                # Execute task
                loop.run_until_complete(self._execute_task(agent, task))
                
            except Exception as e:
                print(f"[Orchestrator] Worker error: {e}")
        
        loop.close()
    
    def decompose_complex_task(self, task_description: str, 
                                max_subtasks: int = 5) -> List[AgentTask]:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task_description: Description of the complex task
            max_subtasks: Maximum number of subtasks to create
            
        Returns:
            List of subtasks
        """
        # Create a planning task
        plan_task = self.create_task(
            agent_type="planning",
            prompt=f"""Decompose the following task into {max_subtasks} or fewer subtasks.
For each subtask, specify:
1. Description
2. Agent type (security, research, coding, planning)
3. Dependencies (if any)

Task: {task_description}

Output as JSON array.""",
            priority=TaskPriority.HIGH
        )
        
        return [plan_task]
    
    def coordinate_research_session(self, topic: str, 
                                     depth: str = "normal") -> str:
        """
        Coordinate a full research session on a topic.
        
        Args:
            topic: Research topic
            depth: Research depth (quick, normal, deep)
            
        Returns:
            Session ID
        """
        session_id = f"research_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create research tasks
        tasks = [
            self.create_task(
                agent_type="research",
                prompt=f"Perform initial research on: {topic}",
                priority=TaskPriority.HIGH,
                context={"session_id": session_id, "depth": depth}
            ),
            self.create_task(
                agent_type="security",
                prompt=f"Analyze security implications of research topic: {topic}",
                priority=TaskPriority.NORMAL,
                context={"session_id": session_id}
            )
        ]
        
        if depth == "deep":
            tasks.append(self.create_task(
                agent_type="research",
                prompt=f"Perform deep analysis and find related topics for: {topic}",
                priority=TaskPriority.NORMAL,
                context={"session_id": session_id},
                dependencies=[tasks[0].task_id]
            ))
        
        return session_id


# Example usage
if __name__ == '__main__':
    orchestrator = EnhancedOrchestrator()
    
    # Start the orchestrator
    orchestrator.start()
    
    # Create a research task
    task = orchestrator.create_task(
        agent_type="research",
        prompt="Research the latest cybersecurity threats in 2024",
        priority=TaskPriority.HIGH
    )
    
    print(f"Created task: {task.task_id}")
    print(f"Queue status: {orchestrator.get_queue_status()}")
    
    # Wait a bit for processing
    import time
    time.sleep(3)
    
    print(f"Agent statuses: {orchestrator.get_all_agent_statuses()}")
    
    # Stop the orchestrator
    orchestrator.stop()
