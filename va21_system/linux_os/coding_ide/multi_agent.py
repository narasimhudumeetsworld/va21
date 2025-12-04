#!/usr/bin/env python3
"""
VA21 OS - Multi-Agent Orchestrator for Coding IDE
==================================================

Om Vinayaka - Coordinated intelligence for complex development tasks.

This module integrates with the existing VA21 OS orchestration architecture
(inspired by OpenManus) that is already integrated with the OS through
Om Vinayaka AI, Self-Learning Engine, and Summary Engine.

The Multi-Agent Orchestrator provides:
- Dynamic task distribution across specialized agents
- Context management using Summary Engine (no context overflow!)
- Integration with Om Vinayaka AI for accessibility
- Self-learning from development patterns
- Work coordination and result aggregation
- Progress tracking and reporting

Integration Points:
- Om Vinayaka AI: Central orchestrator for accessibility
- Summary Engine: Context management and summarization
- Self-Learning Engine: Pattern recognition and improvement
- FARA Layer: UI action execution
- Obsidian Vault: Knowledge storage

This component enables the Coding IDE to tackle complex full-stack
development tasks by breaking them into manageable pieces and
distributing them to specialized agents, while leveraging the
existing VA21 OS infrastructure.

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.
"""

import os
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue


class AgentType(Enum):
    """Types of specialized agents."""
    ORCHESTRATOR = "orchestrator"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEVOPS = "devops"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    UI_UX = "ui_ux"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentContext:
    """Context window for an agent."""
    agent_id: str
    agent_type: AgentType
    max_tokens: int = 8000
    current_tokens: int = 0
    context_items: List[Dict] = field(default_factory=list)
    
    def can_add(self, tokens: int) -> bool:
        """Check if tokens can be added to context."""
        return self.current_tokens + tokens <= self.max_tokens
    
    def add_context(self, content: str, metadata: Dict = None):
        """Add content to context."""
        # Estimate tokens (rough: 4 chars per token)
        estimated_tokens = len(content) // 4
        
        if not self.can_add(estimated_tokens):
            # Summarize old context to make room
            self._compress_context(estimated_tokens)
        
        self.context_items.append({
            "content": content,
            "tokens": estimated_tokens,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        self.current_tokens += estimated_tokens
    
    def _compress_context(self, needed_tokens: int):
        """Compress context to make room for new content."""
        # Remove oldest items until we have space
        while self.context_items and self.current_tokens + needed_tokens > self.max_tokens:
            removed = self.context_items.pop(0)
            self.current_tokens -= removed["tokens"]
    
    def get_context(self) -> str:
        """Get current context as string."""
        return "\n\n".join([item["content"] for item in self.context_items])
    
    def clear(self):
        """Clear the context."""
        self.context_items = []
        self.current_tokens = 0


@dataclass
class Task:
    """A development task."""
    id: str
    title: str
    description: str
    task_type: AgentType
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    parent_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    context: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "dependencies": self.dependencies,
            "assigned_agent": self.assigned_agent,
            "result": self.result[:200] + "..." if self.result and len(self.result) > 200 else self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class Agent:
    """A specialized development agent."""
    id: str
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[str]
    context: AgentContext
    busy: bool = False
    current_task: Optional[str] = None
    tasks_completed: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.agent_type.value,
            "name": self.name,
            "capabilities": self.capabilities,
            "busy": self.busy,
            "current_task": self.current_task,
            "tasks_completed": self.tasks_completed,
            "context_usage": f"{self.context.current_tokens}/{self.context.max_tokens}"
        }


@dataclass
class BuildPlan:
    """A complete build plan for a project."""
    id: str
    name: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def update_progress(self):
        """Update progress based on completed tasks."""
        if not self.tasks:
            self.progress = 0.0
            return
        
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        self.progress = (completed / len(self.tasks)) * 100
        
        if all(t.status == TaskStatus.COMPLETED for t in self.tasks):
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "progress": f"{self.progress:.1f}%",
            "total_tasks": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED),
            "created_at": self.created_at.isoformat(),
        }


# Agent definitions with their specializations
AGENT_DEFINITIONS = {
    AgentType.ORCHESTRATOR: {
        "name": "Build Orchestrator",
        "description": "Coordinates the entire build process and delegates tasks",
        "capabilities": [
            "project_planning", "task_distribution", "dependency_management",
            "progress_tracking", "result_aggregation"
        ]
    },
    AgentType.FRONTEND: {
        "name": "Frontend Agent",
        "description": "Specializes in UI/frontend development",
        "capabilities": [
            "html", "css", "javascript", "typescript", "react", "vue",
            "angular", "svelte", "responsive_design", "accessibility"
        ]
    },
    AgentType.BACKEND: {
        "name": "Backend Agent",
        "description": "Specializes in server-side development",
        "capabilities": [
            "api_design", "rest", "graphql", "python", "node", "java",
            "go", "rust", "authentication", "authorization"
        ]
    },
    AgentType.DATABASE: {
        "name": "Database Agent",
        "description": "Specializes in database design and queries",
        "capabilities": [
            "schema_design", "sql", "nosql", "postgresql", "mongodb",
            "mysql", "redis", "migrations", "optimization"
        ]
    },
    AgentType.TESTING: {
        "name": "Testing Agent",
        "description": "Specializes in writing and running tests",
        "capabilities": [
            "unit_testing", "integration_testing", "e2e_testing",
            "test_coverage", "mocking", "fixtures"
        ]
    },
    AgentType.DOCUMENTATION: {
        "name": "Documentation Agent",
        "description": "Specializes in writing documentation",
        "capabilities": [
            "api_docs", "readme", "tutorials", "code_comments",
            "architecture_docs", "user_guides"
        ]
    },
    AgentType.DEVOPS: {
        "name": "DevOps Agent",
        "description": "Specializes in deployment and infrastructure",
        "capabilities": [
            "docker", "kubernetes", "ci_cd", "github_actions",
            "terraform", "monitoring", "logging"
        ]
    },
    AgentType.SECURITY: {
        "name": "Security Agent",
        "description": "Specializes in security review and hardening",
        "capabilities": [
            "security_audit", "vulnerability_scanning", "input_validation",
            "authentication", "encryption", "secure_coding"
        ]
    },
    AgentType.ARCHITECTURE: {
        "name": "Architecture Agent",
        "description": "Specializes in system design and architecture",
        "capabilities": [
            "system_design", "microservices", "monolith", "event_driven",
            "design_patterns", "scalability"
        ]
    },
    AgentType.UI_UX: {
        "name": "UI/UX Agent",
        "description": "Specializes in user interface and experience design",
        "capabilities": [
            "wireframing", "prototyping", "user_flows", "design_systems",
            "accessibility", "usability"
        ]
    }
}


class MultiAgentOrchestrator:
    """
    VA21 Coding IDE Multi-Agent Orchestrator
    
    Integrates with the existing VA21 OS orchestration architecture
    (inspired by OpenManus) through:
    - Om Vinayaka AI for accessibility and coordination
    - Summary Engine for context management (no overflow!)
    - Self-Learning Engine for pattern recognition
    - FARA Layer for UI action execution
    
    Coordinates multiple specialized agents to tackle complex
    development tasks:
    
    1. Receives high-level project requirements
    2. Breaks down into specialized tasks
    3. Assigns tasks to appropriate agents
    4. Manages context via Summary Engine (no context overwhelm!)
    5. Coordinates dependencies between tasks
    6. Aggregates results into cohesive output
    7. Learns from successful builds to improve!
    
    Each agent has:
    - Specialized capabilities
    - Context managed by Summary Engine
    - Task queue
    
    The orchestrator ensures no agent is overwhelmed and
    context is managed efficiently using VA21 OS infrastructure.
    """
    
    VERSION = "1.1.0"  # Updated to use VA21 OS integration
    
    def __init__(self, ai_helper=None):
        """
        Initialize the orchestrator with VA21 OS integration.
        
        Args:
            ai_helper: Optional AI helper for agent intelligence
        """
        self.ai_helper = ai_helper
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.build_plans: Dict[str, BuildPlan] = {}
        self.task_queue: Queue = Queue()
        self.results: Dict[str, Any] = {}
        self.lock = threading.Lock()
        
        # VA21 OS Integration - Lazy loaded
        self._summary_engine = None
        self._learning_engine = None
        self._om_vinayaka = None
        
        # Initialize agents
        self._init_agents()
        
        print(f"[MultiAgentOrchestrator] Initialized v{self.VERSION}")
        print(f"[MultiAgentOrchestrator] Agents available: {len(self.agents)}")
        print(f"[MultiAgentOrchestrator] VA21 OS integration: Enabled")
    
    @property
    def summary_engine(self):
        """Lazy load Summary Engine for context management."""
        if self._summary_engine is None:
            try:
                from ..accessibility.summary_engine import get_summary_engine
                self._summary_engine = get_summary_engine()
                print("[MultiAgentOrchestrator] Summary Engine connected - context overflow protection active")
            except ImportError:
                pass
        return self._summary_engine
    
    @property
    def learning_engine(self):
        """Lazy load Self-Learning Engine for pattern recognition."""
        if self._learning_engine is None:
            try:
                from ..accessibility.self_learning import get_learning_engine
                self._learning_engine = get_learning_engine()
                print("[MultiAgentOrchestrator] Self-Learning Engine connected - will improve over time")
            except ImportError:
                pass
        return self._learning_engine
    
    @property
    def om_vinayaka(self):
        """Lazy load Om Vinayaka AI for accessibility integration."""
        if self._om_vinayaka is None:
            try:
                from ..accessibility.om_vinayaka_ai import get_om_vinayaka
                self._om_vinayaka = get_om_vinayaka()
            except ImportError:
                pass
        return self._om_vinayaka
    
    def _init_agents(self):
        """Initialize all specialized agents."""
        for agent_type, definition in AGENT_DEFINITIONS.items():
            agent_id = f"agent_{agent_type.value}_{uuid.uuid4().hex[:8]}"
            
            self.agents[agent_id] = Agent(
                id=agent_id,
                agent_type=agent_type,
                name=definition["name"],
                description=definition["description"],
                capabilities=definition["capabilities"],
                context=AgentContext(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    max_tokens=8000
                )
            )
    
    def get_agent_by_type(self, agent_type: AgentType) -> Optional[Agent]:
        """Get an agent by type."""
        for agent in self.agents.values():
            if agent.agent_type == agent_type:
                return agent
        return None
    
    def create_build_plan(self, name: str, description: str,
                          requirements: Dict) -> BuildPlan:
        """
        Create a build plan from requirements.
        
        Args:
            name: Project name
            description: Project description
            requirements: Parsed project requirements
            
        Returns:
            BuildPlan with tasks
        """
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        
        plan = BuildPlan(
            id=plan_id,
            name=name,
            description=description
        )
        
        # Generate tasks based on requirements
        tasks = self._generate_tasks(plan_id, requirements)
        plan.tasks = tasks
        
        # Add tasks to global task registry
        for task in tasks:
            self.tasks[task.id] = task
        
        self.build_plans[plan_id] = plan
        
        print(f"[Orchestrator] Created build plan: {name}")
        print(f"[Orchestrator] Total tasks: {len(tasks)}")
        
        return plan
    
    def _generate_tasks(self, plan_id: str, requirements: Dict) -> List[Task]:
        """Generate tasks from requirements."""
        tasks = []
        
        # Get app type and features from requirements
        app_type = requirements.get("app_type", "web_app")
        features = requirements.get("features", [])
        stack = requirements.get("stack", {})
        
        # Architecture task (first, no dependencies)
        arch_task = Task(
            id=f"task_{uuid.uuid4().hex[:12]}",
            title="Design System Architecture",
            description=f"Design the architecture for {app_type}",
            task_type=AgentType.ARCHITECTURE,
            priority=TaskPriority.CRITICAL,
            context={"requirements": requirements}
        )
        tasks.append(arch_task)
        
        # Database design (depends on architecture)
        if any(f in features for f in ["database", "authentication", "users", "data"]):
            db_task = Task(
                id=f"task_{uuid.uuid4().hex[:12]}",
                title="Design Database Schema",
                description="Design database schema and relationships",
                task_type=AgentType.DATABASE,
                priority=TaskPriority.HIGH,
                dependencies=[arch_task.id],
                context={"database": stack.get("database", "postgresql")}
            )
            tasks.append(db_task)
        
        # Backend development (depends on architecture, maybe database)
        if stack.get("backend"):
            backend_deps = [arch_task.id]
            if any(t.task_type == AgentType.DATABASE for t in tasks):
                backend_deps.append([t.id for t in tasks if t.task_type == AgentType.DATABASE][0])
            
            backend_task = Task(
                id=f"task_{uuid.uuid4().hex[:12]}",
                title="Develop Backend API",
                description=f"Implement backend using {stack.get('backend', 'Node.js')}",
                task_type=AgentType.BACKEND,
                priority=TaskPriority.HIGH,
                dependencies=backend_deps,
                context={"backend": stack.get("backend"), "features": features}
            )
            tasks.append(backend_task)
        
        # Frontend development (depends on architecture)
        if stack.get("frontend"):
            frontend_task = Task(
                id=f"task_{uuid.uuid4().hex[:12]}",
                title="Develop Frontend UI",
                description=f"Implement frontend using {stack.get('frontend', 'React')}",
                task_type=AgentType.FRONTEND,
                priority=TaskPriority.HIGH,
                dependencies=[arch_task.id],
                context={"frontend": stack.get("frontend"), "features": features}
            )
            tasks.append(frontend_task)
        
        # Security review (depends on backend and frontend)
        security_deps = [arch_task.id]
        for t in tasks:
            if t.task_type in [AgentType.BACKEND, AgentType.FRONTEND]:
                security_deps.append(t.id)
        
        security_task = Task(
            id=f"task_{uuid.uuid4().hex[:12]}",
            title="Security Review",
            description="Review code for security vulnerabilities",
            task_type=AgentType.SECURITY,
            priority=TaskPriority.MEDIUM,
            dependencies=security_deps
        )
        tasks.append(security_task)
        
        # Testing (depends on implementation tasks)
        test_deps = [t.id for t in tasks if t.task_type in 
                     [AgentType.BACKEND, AgentType.FRONTEND]]
        if test_deps:
            testing_task = Task(
                id=f"task_{uuid.uuid4().hex[:12]}",
                title="Write Tests",
                description="Write unit and integration tests",
                task_type=AgentType.TESTING,
                priority=TaskPriority.MEDIUM,
                dependencies=test_deps
            )
            tasks.append(testing_task)
        
        # Documentation (depends on everything else)
        doc_deps = [t.id for t in tasks]
        docs_task = Task(
            id=f"task_{uuid.uuid4().hex[:12]}",
            title="Write Documentation",
            description="Create README, API docs, and user guides",
            task_type=AgentType.DOCUMENTATION,
            priority=TaskPriority.LOW,
            dependencies=doc_deps
        )
        tasks.append(docs_task)
        
        # DevOps (depends on backend and testing)
        devops_deps = [t.id for t in tasks if t.task_type in 
                       [AgentType.BACKEND, AgentType.TESTING]]
        if devops_deps:
            devops_task = Task(
                id=f"task_{uuid.uuid4().hex[:12]}",
                title="Setup CI/CD and Deployment",
                description="Configure deployment pipeline",
                task_type=AgentType.DEVOPS,
                priority=TaskPriority.MEDIUM,
                dependencies=devops_deps
            )
            tasks.append(devops_task)
        
        return tasks
    
    def execute_plan(self, plan_id: str, callback: Callable = None) -> Dict:
        """
        Execute a build plan.
        
        Args:
            plan_id: ID of the build plan
            callback: Optional callback for progress updates
            
        Returns:
            Execution results
        """
        if plan_id not in self.build_plans:
            return {"error": f"Plan {plan_id} not found"}
        
        plan = self.build_plans[plan_id]
        plan.status = TaskStatus.IN_PROGRESS
        
        results = {
            "plan_id": plan_id,
            "tasks_completed": [],
            "tasks_failed": [],
            "outputs": {}
        }
        
        # Execute tasks in dependency order
        while True:
            # Find next executable task
            next_task = self._find_next_task(plan)
            if not next_task:
                break
            
            # Execute task
            print(f"[Orchestrator] Executing: {next_task.title}")
            success = self._execute_task(next_task)
            
            if success:
                results["tasks_completed"].append(next_task.id)
                results["outputs"][next_task.id] = next_task.result
            else:
                results["tasks_failed"].append(next_task.id)
            
            # Update progress
            plan.update_progress()
            
            if callback:
                callback({
                    "plan_id": plan_id,
                    "progress": plan.progress,
                    "current_task": next_task.title,
                    "status": "completed" if success else "failed"
                })
        
        # Final update
        plan.update_progress()
        
        results["final_progress"] = plan.progress
        results["plan_status"] = plan.status.value
        
        return results
    
    def _find_next_task(self, plan: BuildPlan) -> Optional[Task]:
        """Find the next task that can be executed."""
        for task in plan.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            deps_completed = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if dep_task is None:
                    # Missing dependency - log warning and skip
                    print(f"[Orchestrator] Warning: Dependency {dep_id} not found for task {task.id}")
                    deps_completed = False
                    break
                if dep_task.status != TaskStatus.COMPLETED:
                    deps_completed = False
                    break
            
            if deps_completed:
                return task
        
        return None
    
    def _execute_task(self, task: Task) -> bool:
        """Execute a single task with Summary Engine context management."""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        # Get the appropriate agent
        agent = self.get_agent_by_type(task.task_type)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"No agent available for {task.task_type.value}"
            return False
        
        # Assign task to agent
        agent.busy = True
        agent.current_task = task.id
        task.assigned_agent = agent.id
        
        # Use Summary Engine for context management if available
        # This prevents context overflow and hallucinations!
        task_context = f"Task: {task.title}\n{task.description}\nContext: {json.dumps(task.context)}"
        
        if self.summary_engine:
            # Add to Summary Engine context (it will auto-summarize if needed)
            ai_system = f"agent_{agent.agent_type.value}"
            self.summary_engine.add_to_context(
                ai_system=ai_system,
                content=task_context,
                item_type='task',
                priority=4 if task.priority == TaskPriority.CRITICAL else 3,
                metadata={"task_id": task.id, "agent_id": agent.id}
            )
        else:
            # Fallback to local agent context
            agent.context.add_context(
                task_context,
                metadata={"task_id": task.id}
            )
        
        try:
            # Execute task (simulated or via AI helper)
            result = self._agent_execute(agent, task)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            agent.tasks_completed += 1
            
            # Learn from successful execution if learning engine available
            if self.learning_engine:
                self.learning_engine.learn_command(
                    f"build_{task.task_type.value}",
                    task.title,
                    "coding_ide",
                    True
                )
            
            return True
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return False
            
        finally:
            agent.busy = False
            agent.current_task = None
    
    def _agent_execute(self, agent: Agent, task: Task) -> str:
        """
        Have an agent execute a task.
        
        Integrates with:
        - AI helper for intelligent execution
        - Summary Engine for optimized context (no overflow!)
        - Self-Learning Engine for pattern improvement
        """
        # Get optimized context from Summary Engine if available
        if self.summary_engine:
            ai_system = f"agent_{agent.agent_type.value}"
            optimized_context = self.summary_engine.get_optimized_context(ai_system)
        else:
            optimized_context = agent.context.get_context()
        
        if self.ai_helper:
            # Use AI helper for intelligent execution
            prompt = f"""
You are a {agent.name} specializing in {agent.description}.

Task: {task.title}
Description: {task.description}
Context: {json.dumps(task.context, indent=2)}

Previous context (optimized by Summary Engine):
{optimized_context}

Please complete this task. Provide detailed, implementable output.
"""
            response = self.ai_helper.chat(
                prompt,
                task_type="code_generation" if task.task_type in 
                    [AgentType.FRONTEND, AgentType.BACKEND, AgentType.DATABASE, AgentType.TESTING]
                    else "architecture"
            )
            
            if response.success:
                return response.content
            else:
                raise Exception(response.error or "AI execution failed")
        
        # Simulated execution (for testing without AI)
        return self._simulated_execution(agent, task)
    
    def _simulated_execution(self, agent: Agent, task: Task) -> str:
        """Provide simulated task execution result."""
        results = {
            AgentType.ARCHITECTURE: f"""
# Architecture Design for {task.context.get('requirements', {}).get('app_type', 'Application')}

## Overview
- Three-tier architecture: Presentation, Business Logic, Data
- Microservices-ready design with API gateway
- Event-driven communication where appropriate

## Components
1. **Frontend**: SPA with component-based architecture
2. **Backend**: RESTful API with authentication middleware
3. **Database**: Relational with caching layer

## Technology Stack
- Frontend: {task.context.get('stack', {}).get('frontend', 'React')}
- Backend: {task.context.get('stack', {}).get('backend', 'Node.js')}
- Database: {task.context.get('stack', {}).get('database', 'PostgreSQL')}
""",
            AgentType.DATABASE: f"""
# Database Schema Design

## Tables
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP
);
```

## Indexes
- users(email) - for authentication lookups
- sessions(token) - for session validation
""",
            AgentType.BACKEND: """
# Backend API Implementation

## Project Structure
```
src/
├── controllers/
├── models/
├── routes/
├── middleware/
├── services/
└── utils/
```

## Sample Route
```javascript
// routes/users.js
const express = require('express');
const router = express.Router();

router.post('/register', async (req, res) => {
    // Implementation
});

router.post('/login', async (req, res) => {
    // Implementation
});

module.exports = router;
```
""",
            AgentType.FRONTEND: """
# Frontend Implementation

## Component Structure
```
src/
├── components/
│   ├── common/
│   ├── layout/
│   └── features/
├── pages/
├── hooks/
├── services/
└── utils/
```

## Sample Component
```jsx
// components/Login.jsx
import React, { useState } from 'react';

export const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        // Login logic
    };
    
    return (
        <form onSubmit={handleSubmit}>
            {/* Form fields */}
        </form>
    );
};
```
""",
            AgentType.TESTING: """
# Test Suite

## Unit Tests
```javascript
describe('User Authentication', () => {
    test('should register new user', async () => {
        // Test implementation
    });
    
    test('should login existing user', async () => {
        // Test implementation
    });
});
```

## Integration Tests
- API endpoint tests
- Database integration tests
- Authentication flow tests
""",
            AgentType.SECURITY: """
# Security Review Report

## Findings
1. ✅ Input validation implemented
2. ✅ Password hashing with bcrypt
3. ⚠️ Rate limiting recommended
4. ✅ CORS configuration proper

## Recommendations
- Add rate limiting to authentication endpoints
- Implement CSRF protection
- Add security headers
""",
            AgentType.DOCUMENTATION: """
# Project Documentation

## README.md
Project description, setup instructions, and usage guide.

## API Documentation
OpenAPI/Swagger specification for all endpoints.

## User Guide
Step-by-step instructions for end users.

## Developer Guide
Architecture overview and contribution guidelines.
""",
            AgentType.DEVOPS: """
# DevOps Configuration

## Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## CI/CD Pipeline
```yaml
name: CI/CD
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm test
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t app .
```
"""
        }
        
        return results.get(agent.agent_type, f"Task '{task.title}' completed by {agent.name}")
    
    def get_plan_status(self, plan_id: str) -> Optional[Dict]:
        """Get the status of a build plan."""
        if plan_id not in self.build_plans:
            return None
        
        plan = self.build_plans[plan_id]
        return {
            "plan": plan.to_dict(),
            "tasks": [task.to_dict() for task in plan.tasks]
        }
    
    def get_agents_status(self) -> List[Dict]:
        """Get status of all agents."""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """Get the result of a specific task."""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            "task": task.to_dict(),
            "full_result": task.result
        }
    
    def cleanup_completed_plans(self):
        """Clean up completed build plans to free memory."""
        completed = [
            plan_id for plan_id, plan in self.build_plans.items()
            if plan.status == TaskStatus.COMPLETED
        ]
        
        for plan_id in completed:
            plan = self.build_plans[plan_id]
            for task in plan.tasks:
                if task.id in self.tasks:
                    del self.tasks[task.id]
            del self.build_plans[plan_id]
        
        # Clear agent contexts
        for agent in self.agents.values():
            agent.context.clear()
        
        print(f"[Orchestrator] Cleaned up {len(completed)} completed plans")


# Singleton instance
_orchestrator_instance = None


def get_orchestrator(ai_helper=None) -> MultiAgentOrchestrator:
    """Get or create the MultiAgentOrchestrator singleton."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = MultiAgentOrchestrator(ai_helper)
    return _orchestrator_instance


# CLI interface
def main():
    """CLI interface for testing the orchestrator."""
    orchestrator = get_orchestrator()
    
    print("=" * 60)
    print("VA21 Coding IDE - Multi-Agent Orchestrator")
    print("=" * 60)
    
    # Show agents
    print("\n📋 Available Agents:")
    for agent in orchestrator.get_agents_status():
        print(f"  • {agent['name']} ({agent['type']})")
        print(f"    Capabilities: {', '.join(agent['capabilities'][:3])}...")
    
    # Create a test plan
    print("\n" + "=" * 60)
    print("Creating test build plan...")
    print("=" * 60)
    
    requirements = {
        "app_type": "web_app",
        "features": ["authentication", "database", "api"],
        "stack": {
            "frontend": "React",
            "backend": "Node.js/Express",
            "database": "PostgreSQL"
        }
    }
    
    plan = orchestrator.create_build_plan(
        name="Test Web Application",
        description="A sample web application with authentication",
        requirements=requirements
    )
    
    print(f"\n📦 Plan created: {plan.name}")
    print(f"   Tasks: {len(plan.tasks)}")
    
    for task in plan.tasks:
        deps = f" (depends on: {len(task.dependencies)})" if task.dependencies else ""
        print(f"   • [{task.task_type.value}] {task.title}{deps}")
    
    # Execute plan
    print("\n" + "=" * 60)
    print("Executing build plan...")
    print("=" * 60)
    
    def progress_callback(update):
        print(f"  [{update['progress']:.0f}%] {update['current_task']} - {update['status']}")
    
    results = orchestrator.execute_plan(plan.id, callback=progress_callback)
    
    print(f"\n✅ Plan completed: {results['final_progress']:.0f}%")
    print(f"   Tasks completed: {len(results['tasks_completed'])}")
    print(f"   Tasks failed: {len(results['tasks_failed'])}")


if __name__ == "__main__":
    main()
