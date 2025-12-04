#!/usr/bin/env python3
"""
VA21 OS - Agent Manager
=======================

Manages the multi-agent system:
- Creates and assigns agents automatically based on task requirements
- Ensures no feature overlap between agents
- Coordinates agent communication
- Tracks task progress and results
- Integrates with Om Vinayaka AI

Om Vinayaka - May obstacles be removed from your path.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from .agent_core import (
    Agent,
    AgentRole,
    AgentExperience,
    AgentStatus,
    AgentConfig,
    TaskContext,
    AgentResult,
    ROLE_DEFINITIONS,
    create_agent,
)
from .ai_providers import get_ai_provider, AIProvider


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Task type to role mapping (ensures right agent for right task)
TASK_ROLE_MAPPING = {
    # Development tasks
    'implement': AgentRole.CODER,
    'code': AgentRole.CODER,
    'write_code': AgentRole.CODER,
    'fix': AgentRole.DEBUGGER,
    'debug': AgentRole.DEBUGGER,
    'review': AgentRole.REVIEWER,
    'test': AgentRole.TESTER,
    'design': AgentRole.ARCHITECT,
    'architecture': AgentRole.ARCHITECT,
    
    # Research tasks
    'research': AgentRole.RESEARCHER,
    'analyze': AgentRole.ANALYST,
    'fact_check': AgentRole.FACT_CHECKER,
    
    # Documentation tasks
    'document': AgentRole.DOCUMENTATION,
    'write_docs': AgentRole.DOCUMENTATION,
    'explain': AgentRole.WRITER,
    
    # Planning tasks
    'plan': AgentRole.PLANNER,
    'breakdown': AgentRole.PLANNER,
    'estimate': AgentRole.PLANNER,
    
    # Security tasks
    'security': AgentRole.SECURITY,
    'vulnerability': AgentRole.SECURITY,
    
    # Coordination tasks
    'coordinate': AgentRole.ORCHESTRATOR,
    'manage': AgentRole.ORCHESTRATOR,
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProjectTask:
    """A task in a project."""
    task_id: str
    description: str
    task_type: str
    priority: int = 1  # 1 = highest
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    status: str = "pending"
    result: Optional[AgentResult] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Project:
    """A project being worked on by agents."""
    project_id: str
    name: str
    description: str
    goal: str  # What needs to be accomplished
    approach: str  # How to accomplish it
    tasks: List[ProjectTask] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)  # Agent IDs
    status: str = "planning"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class AgentManager:
    """
    VA21 OS Agent Manager
    
    Manages the multi-agent system:
    1. Automatically assigns agents based on task requirements
    2. Ensures no feature overlap (each agent has clear responsibilities)
    3. Coordinates work between agents
    4. Tracks progress and aggregates results
    
    Each agent receives:
    - Role with years of experience
    - Context summary of what to accomplish
    - Details on how to accomplish it
    - Clear boundaries (no overlap with other agents)
    """
    
    def __init__(self, ai_provider: AIProvider = None):
        # AI Provider (Ollama or API)
        self.ai_provider = ai_provider or get_ai_provider()
        
        # Agent pool
        self.agents: Dict[str, Agent] = {}
        self.agent_by_role: Dict[AgentRole, List[str]] = defaultdict(list)
        
        # Projects
        self.projects: Dict[str, Project] = {}
        
        # Statistics
        self.stats = {
            'agents_created': 0,
            'tasks_completed': 0,
            'projects_completed': 0,
        }
        
        # Create default agents
        self._create_default_agents()
        
        print(f"[AgentManager] Initialized with {len(self.agents)} agents")
        print(f"[AgentManager] AI Provider: {self.ai_provider.get_status()['type']}")
    
    def _create_default_agents(self):
        """Create default agent pool."""
        default_agents = [
            (AgentRole.ORCHESTRATOR, AgentExperience.EXPERT),
            (AgentRole.PLANNER, AgentExperience.SENIOR),
            (AgentRole.CODER, AgentExperience.SENIOR),
            (AgentRole.REVIEWER, AgentExperience.SENIOR),
            (AgentRole.RESEARCHER, AgentExperience.MID),
            (AgentRole.WRITER, AgentExperience.MID),
        ]
        
        for role, experience in default_agents:
            self.create_agent(role, experience)
    
    def create_agent(self, role: AgentRole, experience: AgentExperience = None, 
                     name: str = None) -> Agent:
        """
        Create a new agent.
        
        Args:
            role: The agent's role
            experience: Experience level (auto-assigned if not provided)
            name: Custom name (auto-generated if not provided)
            
        Returns:
            The created Agent
        """
        agent = create_agent(
            role=role,
            experience=experience,
            name=name,
            ai_provider=self.ai_provider
        )
        
        self.agents[agent.agent_id] = agent
        self.agent_by_role[role].append(agent.agent_id)
        self.stats['agents_created'] += 1
        
        print(f"[AgentManager] Created agent: {agent.config.name} ({agent.agent_id})")
        return agent
    
    def get_agent_for_task(self, task_type: str) -> Optional[Agent]:
        """
        Get the best available agent for a task type.
        
        Args:
            task_type: Type of task (e.g., 'code', 'review', 'research')
            
        Returns:
            Available agent or None
        """
        # Determine role needed
        role = TASK_ROLE_MAPPING.get(task_type.lower())
        
        if role and role in self.agent_by_role:
            # Find available agent with this role
            for agent_id in self.agent_by_role[role]:
                agent = self.agents.get(agent_id)
                if agent and agent.status == AgentStatus.IDLE:
                    return agent
        
        # No matching agent - create one on demand
        if role:
            return self.create_agent(role)
        
        # Default to coder for unknown tasks
        return self.create_agent(AgentRole.CODER)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROJECT MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_project(self, name: str, description: str, 
                       goal: str, approach: str) -> Project:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            goal: What needs to be accomplished
            approach: How to accomplish it
            
        Returns:
            Created Project
        """
        project_id = f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        project = Project(
            project_id=project_id,
            name=name,
            description=description,
            goal=goal,
            approach=approach
        )
        
        self.projects[project_id] = project
        print(f"[AgentManager] Created project: {name} ({project_id})")
        
        return project
    
    def plan_project(self, project_id: str) -> List[ProjectTask]:
        """
        Use the Planner agent to break down a project into tasks.
        
        Args:
            project_id: Project to plan
            
        Returns:
            List of planned tasks
        """
        project = self.projects.get(project_id)
        if not project:
            return []
        
        # Get planner agent
        planner = self.get_agent_for_task('plan')
        if not planner:
            return []
        
        # Create planning task
        planning_task = TaskContext(
            task_id=f"plan_{project_id}",
            summary=f"Plan the project: {project.name}",
            details=f"""Break down this project into concrete tasks.

Project Goal: {project.goal}

Approach: {project.approach}

Description: {project.description}

Create a list of tasks with:
1. Task description
2. Task type (code, review, test, document, etc.)
3. Priority (1-5, 1 is highest)
4. Dependencies (which tasks must complete first)

Format each task as:
TASK: [description]
TYPE: [type]
PRIORITY: [1-5]
DEPENDS: [task numbers or 'none']
""",
            requirements=["Create actionable, specific tasks", "Include all necessary steps"],
            constraints=["Keep tasks focused and single-purpose"]
        )
        
        planner.assign_task(planning_task)
        result = planner.execute()
        
        if result.success:
            # Parse tasks from result
            tasks = self._parse_planned_tasks(result.output, project_id)
            project.tasks = tasks
            project.status = "planned"
            return tasks
        
        return []
    
    def _parse_planned_tasks(self, output: str, project_id: str) -> List[ProjectTask]:
        """Parse tasks from planner output."""
        tasks = []
        lines = output.split('\n')
        
        current_task = {}
        task_num = 0
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TASK:'):
                if current_task.get('description'):
                    task_num += 1
                    tasks.append(ProjectTask(
                        task_id=f"{project_id}_task_{task_num}",
                        description=current_task.get('description', ''),
                        task_type=current_task.get('type', 'code'),
                        priority=current_task.get('priority', 3),
                        dependencies=current_task.get('dependencies', [])
                    ))
                current_task = {'description': line[5:].strip()}
            
            elif line.startswith('TYPE:'):
                current_task['type'] = line[5:].strip().lower()
            
            elif line.startswith('PRIORITY:'):
                try:
                    current_task['priority'] = int(line[9:].strip())
                except ValueError:
                    current_task['priority'] = 3
            
            elif line.startswith('DEPENDS:'):
                deps = line[8:].strip().lower()
                if deps != 'none':
                    current_task['dependencies'] = [d.strip() for d in deps.split(',')]
        
        # Don't forget last task
        if current_task.get('description'):
            task_num += 1
            tasks.append(ProjectTask(
                task_id=f"{project_id}_task_{task_num}",
                description=current_task.get('description', ''),
                task_type=current_task.get('type', 'code'),
                priority=current_task.get('priority', 3),
                dependencies=current_task.get('dependencies', [])
            ))
        
        return tasks
    
    def execute_project(self, project_id: str) -> Dict[str, AgentResult]:
        """
        Execute all tasks in a project.
        
        Args:
            project_id: Project to execute
            
        Returns:
            Dict of task_id -> AgentResult
        """
        project = self.projects.get(project_id)
        if not project or not project.tasks:
            return {}
        
        results = {}
        project.status = "executing"
        
        # Sort tasks by priority
        sorted_tasks = sorted(project.tasks, key=lambda t: t.priority)
        
        for task in sorted_tasks:
            # Check dependencies - all must be completed successfully
            deps_complete = True
            for dep in task.dependencies:
                dep_result = results.get(dep)
                if not isinstance(dep_result, AgentResult) or not dep_result.success:
                    deps_complete = False
                    break
            
            if task.dependencies and not deps_complete:
                task.status = "blocked"
                continue
            
            # Get appropriate agent
            agent = self.get_agent_for_task(task.task_type)
            if not agent:
                task.status = "failed"
                continue
            
            # Create task context
            context = TaskContext(
                task_id=task.task_id,
                summary=task.description,
                details=f"Project: {project.name}\nGoal: {project.goal}\n\n{task.description}",
                requirements=[],
                constraints=[]
            )
            
            # Execute
            task.assigned_agent = agent.agent_id
            task.status = "executing"
            
            agent.assign_task(context)
            result = agent.execute()
            
            task.result = result
            task.status = "completed" if result.success else "failed"
            results[task.task_id] = result
            
            self.stats['tasks_completed'] += 1
        
        # Check if all tasks completed
        all_complete = all(t.status == "completed" for t in project.tasks)
        project.status = "completed" if all_complete else "partial"
        
        if all_complete:
            self.stats['projects_completed'] += 1
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SINGLE TASK EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def execute_task(self, description: str, task_type: str = "code",
                     context: str = "") -> AgentResult:
        """
        Execute a single task.
        
        Args:
            description: Task description
            task_type: Type of task
            context: Additional context
            
        Returns:
            AgentResult
        """
        agent = self.get_agent_for_task(task_type)
        if not agent:
            return AgentResult(
                agent_id="none",
                task_id="single",
                success=False,
                output="",
                errors=["No agent available for this task"]
            )
        
        task = TaskContext(
            task_id=f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            summary=description,
            details=context or description,
        )
        
        agent.assign_task(task)
        result = agent.execute()
        
        self.stats['tasks_completed'] += 1
        return result
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS AND INFO
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_status(self) -> Dict:
        """Get manager status."""
        agent_status = {}
        for role in AgentRole:
            role_agents = self.agent_by_role.get(role, [])
            if role_agents:
                agent_status[role.value] = {
                    'count': len(role_agents),
                    'idle': sum(1 for aid in role_agents 
                               if self.agents.get(aid, {}).status == AgentStatus.IDLE),
                }
        
        return {
            'total_agents': len(self.agents),
            'agents_by_role': agent_status,
            'projects': len(self.projects),
            'ai_provider': self.ai_provider.get_status()['type'],
            'stats': self.stats,
        }
    
    def get_agents_info(self) -> List[Dict]:
        """Get info about all agents."""
        return [agent.get_info() for agent in self.agents.values()]
    
    def get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get status of a project."""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        return {
            'project_id': project.project_id,
            'name': project.name,
            'status': project.status,
            'goal': project.goal,
            'tasks': [
                {
                    'task_id': t.task_id,
                    'description': t.description[:50] + "...",
                    'type': t.task_type,
                    'status': t.status,
                    'agent': t.assigned_agent,
                }
                for t in project.tasks
            ],
            'progress': f"{sum(1 for t in project.tasks if t.status == 'completed')}/{len(project.tasks)}"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_agent_manager_instance = None


def get_agent_manager() -> AgentManager:
    """Get the AgentManager singleton."""
    global _agent_manager_instance
    
    if _agent_manager_instance is None:
        _agent_manager_instance = AgentManager()
    
    return _agent_manager_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the agent manager."""
    print("=" * 70)
    print("VA21 OS - Agent Manager Test")
    print("=" * 70)
    
    manager = get_agent_manager()
    
    # Show status
    print("\n--- Manager Status ---")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
    
    # Show agents
    print("\n--- Available Agents ---")
    for agent_info in manager.get_agents_info():
        print(f"  {agent_info['name']} ({agent_info['role']}, {agent_info['experience']})")
    
    # Create a project
    print("\n--- Creating Project ---")
    project = manager.create_project(
        name="Hello World App",
        description="A simple hello world application",
        goal="Create a Python application that prints 'Hello, World!'",
        approach="1. Create main.py file\n2. Add print statement\n3. Test the application"
    )
    
    # Plan the project
    print("\n--- Planning Project ---")
    tasks = manager.plan_project(project.project_id)
    print(f"Planned {len(tasks)} tasks")
    for task in tasks:
        print(f"  - {task.description[:40]}... (type: {task.task_type})")
    
    # Execute single task
    print("\n--- Executing Single Task ---")
    result = manager.execute_task(
        description="Write a simple greeting function in Python",
        task_type="code"
    )
    print(f"Success: {result.success}")
    print(f"Output preview: {result.output[:200]}...")
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
