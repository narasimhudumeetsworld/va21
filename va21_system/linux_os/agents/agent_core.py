#!/usr/bin/env python3
"""
VA21 OS - Agent Core
====================

Defines the core Agent system with automatic role assignment.

Each agent has:
- Role (Researcher, Coder, Writer, Reviewer, etc.)
- Experience level (Junior, Mid, Senior, Expert)
- Context summary of what they need to accomplish
- How to accomplish their tasks
- Clear responsibilities (no overlap with other agents)

Om Vinayaka - May obstacles be removed from your path.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class AgentRole(Enum):
    """Roles that agents can take."""
    # Development roles
    CODER = "coder"
    REVIEWER = "reviewer"
    ARCHITECT = "architect"
    DEBUGGER = "debugger"
    TESTER = "tester"
    
    # Research roles
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    FACT_CHECKER = "fact_checker"
    
    # Creative roles
    WRITER = "writer"
    EDITOR = "editor"
    DESIGNER = "designer"
    
    # System roles
    ORCHESTRATOR = "orchestrator"
    PLANNER = "planner"
    EXECUTOR = "executor"
    
    # Specialized roles
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    DOCUMENTATION = "documentation"


class AgentExperience(Enum):
    """Experience levels for agents."""
    JUNIOR = "junior"       # 0-2 years equivalent
    MID = "mid"             # 2-5 years equivalent
    SENIOR = "senior"       # 5-10 years equivalent
    EXPERT = "expert"       # 10+ years equivalent


class AgentStatus(Enum):
    """Status of an agent."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


# ═══════════════════════════════════════════════════════════════════════════════
# ROLE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Each role has defined responsibilities and expertise
ROLE_DEFINITIONS = {
    AgentRole.CODER: {
        "title": "Software Developer",
        "description": "Writes clean, efficient, and maintainable code",
        "responsibilities": [
            "Write code based on specifications",
            "Implement features and functionality",
            "Follow best practices and coding standards",
            "Handle error cases and edge conditions",
        ],
        "expertise": ["programming", "algorithms", "data structures", "frameworks"],
        "default_experience": AgentExperience.MID,
    },
    AgentRole.REVIEWER: {
        "title": "Code Reviewer",
        "description": "Reviews code for quality, security, and best practices",
        "responsibilities": [
            "Review code for bugs and issues",
            "Ensure coding standards compliance",
            "Suggest improvements and optimizations",
            "Verify security best practices",
        ],
        "expertise": ["code review", "security", "best practices", "optimization"],
        "default_experience": AgentExperience.SENIOR,
    },
    AgentRole.ARCHITECT: {
        "title": "Software Architect",
        "description": "Designs system architecture and high-level structure",
        "responsibilities": [
            "Design system architecture",
            "Make technology decisions",
            "Define component interfaces",
            "Ensure scalability and maintainability",
        ],
        "expertise": ["system design", "architecture patterns", "scalability"],
        "default_experience": AgentExperience.EXPERT,
    },
    AgentRole.RESEARCHER: {
        "title": "Research Analyst",
        "description": "Researches topics and gathers information",
        "responsibilities": [
            "Research topics thoroughly",
            "Gather and synthesize information",
            "Provide accurate citations",
            "Summarize findings clearly",
        ],
        "expertise": ["research", "analysis", "synthesis", "citations"],
        "default_experience": AgentExperience.MID,
    },
    AgentRole.WRITER: {
        "title": "Technical Writer",
        "description": "Writes clear and effective documentation",
        "responsibilities": [
            "Write clear documentation",
            "Create user guides and tutorials",
            "Explain complex concepts simply",
            "Maintain consistent style",
        ],
        "expertise": ["writing", "documentation", "communication"],
        "default_experience": AgentExperience.MID,
    },
    AgentRole.PLANNER: {
        "title": "Project Planner",
        "description": "Plans and breaks down tasks",
        "responsibilities": [
            "Break down complex tasks",
            "Create actionable plans",
            "Estimate effort and time",
            "Identify dependencies",
        ],
        "expertise": ["planning", "estimation", "decomposition"],
        "default_experience": AgentExperience.SENIOR,
    },
    AgentRole.ORCHESTRATOR: {
        "title": "Team Orchestrator",
        "description": "Coordinates multiple agents to accomplish goals",
        "responsibilities": [
            "Coordinate agent activities",
            "Assign tasks to appropriate agents",
            "Monitor progress and results",
            "Resolve conflicts and blockers",
        ],
        "expertise": ["coordination", "management", "delegation"],
        "default_experience": AgentExperience.EXPERT,
    },
    AgentRole.DEBUGGER: {
        "title": "Debug Specialist",
        "description": "Identifies and fixes bugs and issues",
        "responsibilities": [
            "Analyze error messages and logs",
            "Identify root causes",
            "Propose and implement fixes",
            "Verify fixes work correctly",
        ],
        "expertise": ["debugging", "troubleshooting", "problem-solving"],
        "default_experience": AgentExperience.SENIOR,
    },
    AgentRole.TESTER: {
        "title": "Quality Assurance",
        "description": "Tests code and ensures quality",
        "responsibilities": [
            "Write and run tests",
            "Identify edge cases",
            "Report bugs and issues",
            "Verify fixes and changes",
        ],
        "expertise": ["testing", "quality assurance", "edge cases"],
        "default_experience": AgentExperience.MID,
    },
    AgentRole.SECURITY: {
        "title": "Security Analyst",
        "description": "Analyzes and ensures security",
        "responsibilities": [
            "Identify security vulnerabilities",
            "Review for security best practices",
            "Suggest security improvements",
            "Validate security measures",
        ],
        "expertise": ["security", "vulnerabilities", "encryption"],
        "default_experience": AgentExperience.SENIOR,
    },
}


# Experience level modifiers
EXPERIENCE_MODIFIERS = {
    AgentExperience.JUNIOR: {
        "years": "0-2 years",
        "system_prompt_modifier": "You are a junior developer. Be careful and ask questions when unsure.",
        "max_complexity": "low",
        "needs_review": True,
    },
    AgentExperience.MID: {
        "years": "2-5 years",
        "system_prompt_modifier": "You are an experienced developer. Handle most tasks independently.",
        "max_complexity": "medium",
        "needs_review": True,
    },
    AgentExperience.SENIOR: {
        "years": "5-10 years",
        "system_prompt_modifier": "You are a senior developer. Make informed decisions and mentor others.",
        "max_complexity": "high",
        "needs_review": False,
    },
    AgentExperience.EXPERT: {
        "years": "10+ years",
        "system_prompt_modifier": "You are an expert. Make architectural decisions and guide the team.",
        "max_complexity": "expert",
        "needs_review": False,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentConfig:
    """Configuration for an agent."""
    role: AgentRole
    experience: AgentExperience
    name: str = ""
    custom_instructions: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class TaskContext:
    """Context for a task assigned to an agent."""
    task_id: str
    summary: str  # What needs to be accomplished
    details: str  # How to accomplish it
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    parent_task: Optional[str] = None


@dataclass
class AgentResult:
    """Result from an agent's work."""
    agent_id: str
    task_id: str
    success: bool
    output: str
    artifacts: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    tokens_used: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Agent:
    """
    A VA21 OS AI Agent with automatic role assignment.
    
    Each agent:
    - Has a defined role and experience level
    - Receives context about what to accomplish and how
    - Uses local Ollama or external API
    - Works with other agents without feature overlap
    - Reports results through the orchestrator
    """
    
    def __init__(self, config: AgentConfig, ai_provider=None):
        self.config = config
        self.ai_provider = ai_provider
        
        # Generate unique ID
        self.agent_id = self._generate_id()
        
        # Get role definition
        self.role_def = ROLE_DEFINITIONS.get(config.role, {})
        self.experience_mod = EXPERIENCE_MODIFIERS.get(config.experience, {})
        
        # Generate name if not provided
        if not config.name:
            self.config.name = self._generate_name()
        
        # State
        self.status = AgentStatus.IDLE
        self.current_task: Optional[TaskContext] = None
        self.history: List[AgentResult] = []
        
        # Build system prompt
        self.system_prompt = self._build_system_prompt()
    
    def _generate_id(self) -> str:
        """Generate a unique agent ID."""
        unique = f"{self.config.role.value}_{datetime.now().isoformat()}"
        return hashlib.sha256(unique.encode()).hexdigest()[:12]
    
    def _generate_name(self) -> str:
        """Generate a descriptive name for the agent."""
        role_title = self.role_def.get('title', self.config.role.value.title())
        exp = self.config.experience.value.title()
        return f"{exp} {role_title}"
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for this agent."""
        role_title = self.role_def.get('title', self.config.role.value.title())
        description = self.role_def.get('description', '')
        responsibilities = self.role_def.get('responsibilities', [])
        exp_years = self.experience_mod.get('years', '')
        exp_modifier = self.experience_mod.get('system_prompt_modifier', '')
        
        responsibilities_str = "\n".join([f"- {r}" for r in responsibilities])
        
        prompt = f"""You are {self.config.name}, a {role_title} in the VA21 OS system.

## Role Description
{description}

## Experience Level
{self.config.experience.value.title()} ({exp_years})
{exp_modifier}

## Responsibilities
{responsibilities_str}

## Guidelines
- Focus only on your assigned responsibilities
- Do not overlap with other agents' work
- Ask for clarification if instructions are unclear
- Report any blockers or issues
- Provide clear, actionable output

{self.config.custom_instructions}
"""
        return prompt
    
    def assign_task(self, task: TaskContext):
        """Assign a task to this agent."""
        self.current_task = task
        self.status = AgentStatus.WORKING
    
    def execute(self) -> AgentResult:
        """Execute the current assigned task."""
        if not self.current_task:
            return AgentResult(
                agent_id=self.agent_id,
                task_id="none",
                success=False,
                output="No task assigned",
                errors=["No task assigned to agent"]
            )
        
        start_time = datetime.now()
        task = self.current_task
        
        try:
            # Build the prompt for this task
            user_prompt = self._build_task_prompt(task)
            
            # Execute via AI provider
            if self.ai_provider:
                from .ai_providers import Message
                messages = [
                    Message(role="system", content=self.system_prompt),
                    Message(role="user", content=user_prompt)
                ]
                result = self.ai_provider.complete(messages)
                
                output = result.content
                tokens = result.tokens_used
            else:
                # No AI provider - return task summary
                output = f"[Agent {self.config.name}] Task received: {task.summary}\n\nDetails: {task.details}"
                tokens = 0
            
            duration = (datetime.now() - start_time).total_seconds()
            
            agent_result = AgentResult(
                agent_id=self.agent_id,
                task_id=task.task_id,
                success=True,
                output=output,
                duration_seconds=duration,
                tokens_used=tokens
            )
            
        except Exception as e:
            agent_result = AgentResult(
                agent_id=self.agent_id,
                task_id=task.task_id,
                success=False,
                output="",
                errors=[str(e)]
            )
        
        # Record in history
        self.history.append(agent_result)
        self.status = AgentStatus.COMPLETED if agent_result.success else AgentStatus.ERROR
        self.current_task = None
        
        return agent_result
    
    def _build_task_prompt(self, task: TaskContext) -> str:
        """Build the user prompt for a task."""
        requirements_str = "\n".join([f"- {r}" for r in task.requirements]) if task.requirements else "None specified"
        constraints_str = "\n".join([f"- {c}" for c in task.constraints]) if task.constraints else "None specified"
        files_str = "\n".join([f"- {f}" for f in task.related_files]) if task.related_files else "None"
        
        return f"""## Task: {task.summary}

### What to Accomplish
{task.summary}

### How to Accomplish It
{task.details}

### Requirements
{requirements_str}

### Constraints
{constraints_str}

### Related Files
{files_str}

Please complete this task according to your role and expertise.
"""
    
    def get_info(self) -> Dict:
        """Get agent information."""
        return {
            'agent_id': self.agent_id,
            'name': self.config.name,
            'role': self.config.role.value,
            'experience': self.config.experience.value,
            'experience_years': self.experience_mod.get('years', ''),
            'status': self.status.value,
            'responsibilities': self.role_def.get('responsibilities', []),
            'expertise': self.role_def.get('expertise', []),
            'tasks_completed': len(self.history),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def create_agent(
    role: AgentRole,
    experience: AgentExperience = None,
    name: str = None,
    ai_provider=None,
    **kwargs
) -> Agent:
    """
    Create an agent with automatic configuration.
    
    Args:
        role: The role for the agent
        experience: Experience level (auto-assigned if not provided)
        name: Custom name (auto-generated if not provided)
        ai_provider: AI provider to use
        **kwargs: Additional config options
        
    Returns:
        Configured Agent instance
    """
    # Auto-assign experience if not provided
    if experience is None:
        role_def = ROLE_DEFINITIONS.get(role, {})
        experience = role_def.get('default_experience', AgentExperience.MID)
    
    config = AgentConfig(
        role=role,
        experience=experience,
        name=name or "",
        **kwargs
    )
    
    return Agent(config, ai_provider)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the agent system."""
    print("=" * 70)
    print("VA21 OS - Agent Core Test")
    print("=" * 70)
    
    # Create agents with different roles
    agents = [
        create_agent(AgentRole.ORCHESTRATOR),
        create_agent(AgentRole.PLANNER),
        create_agent(AgentRole.CODER, AgentExperience.SENIOR),
        create_agent(AgentRole.REVIEWER),
        create_agent(AgentRole.TESTER),
    ]
    
    print("\n--- Created Agents ---")
    for agent in agents:
        info = agent.get_info()
        print(f"\n{info['name']}")
        print(f"  Role: {info['role']}")
        print(f"  Experience: {info['experience']} ({info['experience_years']})")
        print(f"  Responsibilities: {', '.join(info['responsibilities'][:2])}...")
    
    # Test task assignment
    print("\n--- Testing Task Assignment ---")
    coder = agents[2]  # Senior Coder
    
    task = TaskContext(
        task_id="task_001",
        summary="Implement a user authentication function",
        details="Create a function that validates user credentials against a database",
        requirements=[
            "Use secure password hashing",
            "Return user object on success",
            "Handle invalid credentials gracefully"
        ],
        constraints=[
            "Do not store passwords in plain text",
            "Use existing database connection"
        ]
    )
    
    coder.assign_task(task)
    result = coder.execute()
    
    print(f"\nTask Result:")
    print(f"  Success: {result.success}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    print(f"  Output preview: {result.output[:200]}...")
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
