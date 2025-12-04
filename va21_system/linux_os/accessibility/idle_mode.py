#!/usr/bin/env python3
"""
VA21 OS - Om Vinayaka Idle Mode Self-Improvement System
========================================================

Om Vinayaka - The remover of obstacles.

During idle time (when no user activity), Om Vinayaka AI automatically:
- Researches best ways to optimize user workflows
- Adapts system components to enhance performance
- Self-reflects on what it's doing and learns from that
- Uses dynamic thinking (why and what) for continuous improvement
- Analyzes errors and learns to avoid them in the future

This module implements the idle-time self-improvement capabilities that make
Om Vinayaka a truly intelligent, adaptive AI assistant.

Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                    IDLE MODE SELF-IMPROVEMENT SYSTEM                    │
├─────────────────────────────────────────────────────────────────────────┤
│  🕐 IdleModeManager                                                     │
│  ├── Detects user inactivity (configurable timeout)                     │
│  ├── Triggers self-improvement routines during idle                     │
│  ├── Gracefully pauses when user activity resumes                       │
│  └── Manages resource usage during background operations                │
├─────────────────────────────────────────────────────────────────────────┤
│  🔄 WorkflowOptimizer                                                   │
│  ├── Analyzes learned patterns to find optimization opportunities       │
│  ├── Identifies common user workflows                                   │
│  ├── Suggests improvements to streamline tasks                          │
│  └── Adapts system components for better performance                    │
├─────────────────────────────────────────────────────────────────────────┤
│  🔍 ErrorAnalyzer                                                       │
│  ├── Reviews past errors and failures                                   │
│  ├── Identifies patterns in errors                                      │
│  ├── Develops strategies to avoid similar errors                        │
│  └── Updates learning models to prevent recurrence                      │
├─────────────────────────────────────────────────────────────────────────┤
│  🧠 SelfReflectionEngine                                                │
│  ├── Analyzes own performance and decision-making                       │
│  ├── Dynamic thinking: asks "why" and "what" questions                  │
│  ├── Identifies areas for improvement                                   │
│  └── Generates insights for continuous learning                         │
└─────────────────────────────────────────────────────────────────────────┘

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pathlib import Path
import hashlib


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

IDLE_MODE_VERSION = "1.0.0"

# Default paths
DEFAULT_IDLE_DATA_PATH = os.path.expanduser("~/.va21/idle_mode")
DEFAULT_LEARNING_PATH = os.path.expanduser("~/.va21/learning")

# Idle mode settings
DEFAULT_IDLE_TIMEOUT_SECONDS = 300  # 5 minutes of inactivity triggers idle mode
MIN_IDLE_TIMEOUT_SECONDS = 60  # Minimum 1 minute
MAX_IDLE_TIMEOUT_SECONDS = 3600  # Maximum 1 hour

# Self-improvement intervals during idle
WORKFLOW_ANALYSIS_INTERVAL = 60  # Analyze workflows every 60 seconds during idle
ERROR_ANALYSIS_INTERVAL = 120  # Analyze errors every 120 seconds during idle
SELF_REFLECTION_INTERVAL = 180  # Self-reflect every 180 seconds during idle

# Resource limits during idle mode (reserved for future resource monitoring)
# MAX_CPU_PERCENT_IDLE = 25  # Don't use more than 25% CPU during idle
MAX_ANALYSIS_DURATION = 30  # Each analysis task max 30 seconds


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IdleModeState:
    """Current state of idle mode."""
    is_idle: bool = False
    idle_start_time: Optional[str] = None
    last_user_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    total_idle_time_seconds: float = 0
    optimizations_made: int = 0
    errors_analyzed: int = 0
    reflections_completed: int = 0


@dataclass
class WorkflowPattern:
    """A detected user workflow pattern."""
    pattern_id: str
    name: str
    steps: List[str]
    frequency: int = 1
    average_duration_seconds: float = 0
    optimization_suggestions: List[str] = field(default_factory=list)
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ErrorRecord:
    """Record of an error for analysis."""
    error_id: str
    error_type: str
    error_message: str
    context: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    analyzed: bool = False
    prevention_strategy: Optional[str] = None


@dataclass
class SelfReflectionInsight:
    """An insight from self-reflection."""
    insight_id: str
    category: str  # 'performance', 'learning', 'behavior', 'improvement'
    question: str  # The "why" or "what" question asked
    insight: str  # The answer/insight gained
    action_items: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    applied: bool = False


@dataclass
class OptimizationResult:
    """Result of a workflow optimization."""
    optimization_id: str
    workflow_pattern_id: str
    optimization_type: str
    description: str
    expected_improvement: str
    applied: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

class WorkflowOptimizer:
    """
    Analyzes and optimizes user workflows.
    
    During idle time, this component:
    1. Analyzes learned command patterns to identify workflows
    2. Finds common sequences of actions
    3. Identifies optimization opportunities
    4. Suggests and applies improvements
    
    Om Vinayaka - Helping users work more efficiently.
    """
    
    def __init__(self, learning_path: str = None, data_path: str = None):
        self.learning_path = learning_path or DEFAULT_LEARNING_PATH
        self.data_path = data_path or DEFAULT_IDLE_DATA_PATH
        
        os.makedirs(self.data_path, exist_ok=True)
        
        # Detected workflow patterns
        self.workflow_patterns: Dict[str, WorkflowPattern] = {}
        
        # Optimization results
        self.optimizations: List[OptimizationResult] = []
        
        # Load existing data
        self._load_data()
        
        print(f"[WorkflowOptimizer] Initialized - ready to optimize user workflows")
    
    def _load_data(self):
        """Load existing workflow patterns and optimizations."""
        patterns_file = os.path.join(self.data_path, "workflow_patterns.json")
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    for pid, pdata in data.items():
                        self.workflow_patterns[pid] = WorkflowPattern(**pdata)
            except Exception as e:
                print(f"[WorkflowOptimizer] Error loading patterns: {e}")
        
        optimizations_file = os.path.join(self.data_path, "optimizations.json")
        if os.path.exists(optimizations_file):
            try:
                with open(optimizations_file, 'r') as f:
                    data = json.load(f)
                    self.optimizations = [OptimizationResult(**o) for o in data]
            except Exception as e:
                print(f"[WorkflowOptimizer] Error loading optimizations: {e}")
    
    def _save_data(self):
        """Save workflow patterns and optimizations."""
        patterns_file = os.path.join(self.data_path, "workflow_patterns.json")
        with open(patterns_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.workflow_patterns.items()}, f, indent=2)
        
        optimizations_file = os.path.join(self.data_path, "optimizations.json")
        with open(optimizations_file, 'w') as f:
            json.dump([asdict(o) for o in self.optimizations], f, indent=2)
    
    def analyze_workflows(self, learned_patterns: Dict = None) -> List[WorkflowPattern]:
        """
        Analyze learned patterns to identify user workflows.
        
        Args:
            learned_patterns: Dict of learned command patterns (from SelfLearningEngine)
            
        Returns:
            List of detected workflow patterns
        """
        if not learned_patterns:
            learned_patterns = self._load_learned_patterns()
        
        if not learned_patterns:
            return []
        
        # Group patterns by context/app to find related actions
        patterns_by_context = defaultdict(list)
        for pattern_key, pattern_data in learned_patterns.items():
            contexts = pattern_data.get('contexts', [])
            if contexts:
                for ctx in contexts:
                    patterns_by_context[ctx].append(pattern_data)
            else:
                patterns_by_context['global'].append(pattern_data)
        
        # Identify workflow patterns (sequences of related actions)
        new_workflows = []
        for context, patterns in patterns_by_context.items():
            workflow = self._identify_workflow_in_context(context, patterns)
            if workflow:
                new_workflows.append(workflow)
                self.workflow_patterns[workflow.pattern_id] = workflow
        
        self._save_data()
        return new_workflows
    
    def _load_learned_patterns(self) -> Dict:
        """Load learned patterns from the learning engine."""
        patterns_file = os.path.join(self.learning_path, "command_patterns.json")
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"[WorkflowOptimizer] Could not load patterns from {patterns_file}: {e}. Starting with empty patterns.")
        return {}
    
    def _identify_workflow_in_context(self, context: str, 
                                       patterns: List[Dict]) -> Optional[WorkflowPattern]:
        """Identify a workflow pattern within a specific context."""
        if len(patterns) < 2:
            return None
        
        # Sort patterns by frequency
        sorted_patterns = sorted(patterns, key=lambda p: p.get('frequency', 0), reverse=True)
        
        # Take top frequent patterns as workflow steps
        top_patterns = sorted_patterns[:5]
        steps = [p.get('pattern', p.get('action', 'unknown')) for p in top_patterns]
        
        # Generate pattern ID
        pattern_id = hashlib.sha256(
            f"{context}:{':'.join(steps)}".encode()
        ).hexdigest()[:12]
        
        # Check if we already have this workflow
        if pattern_id in self.workflow_patterns:
            # Update frequency
            existing = self.workflow_patterns[pattern_id]
            existing.frequency += 1
            existing.last_seen = datetime.now().isoformat()
            return existing
        
        # Create new workflow pattern
        workflow = WorkflowPattern(
            pattern_id=pattern_id,
            name=f"{context}_workflow",
            steps=steps,
            frequency=1,
            average_duration_seconds=0,
            optimization_suggestions=[]
        )
        
        # Generate optimization suggestions
        workflow.optimization_suggestions = self._generate_optimizations(workflow)
        
        return workflow
    
    def _generate_optimizations(self, workflow: WorkflowPattern) -> List[str]:
        """Generate optimization suggestions for a workflow."""
        suggestions = []
        
        # Check for repeated patterns
        if len(workflow.steps) != len(set(workflow.steps)):
            suggestions.append("Consider combining repeated actions into a single command")
        
        # Check for long workflows
        if len(workflow.steps) >= 4:
            suggestions.append("This workflow has many steps - consider creating a shortcut macro")
        
        # Check for common optimization opportunities
        for step in workflow.steps:
            step_lower = step.lower()
            if 'search' in step_lower and 'save' not in ''.join(workflow.steps).lower():
                suggestions.append("Add auto-save after search operations for better data preservation")
            if 'open' in step_lower:
                suggestions.append("Consider using quick-access shortcuts for frequently opened items")
        
        # General suggestions based on frequency
        if workflow.frequency > 5:
            suggestions.append("This is a frequent workflow - create a voice command shortcut")
        
        return suggestions
    
    def get_optimization_suggestions(self, limit: int = 10) -> List[Dict]:
        """Get top optimization suggestions across all workflows."""
        suggestions = []
        
        for workflow in sorted(
            self.workflow_patterns.values(),
            key=lambda w: w.frequency,
            reverse=True
        )[:limit]:
            for suggestion in workflow.optimization_suggestions:
                suggestions.append({
                    'workflow': workflow.name,
                    'workflow_id': workflow.pattern_id,
                    'suggestion': suggestion,
                    'frequency': workflow.frequency,
                })
        
        return suggestions
    
    def apply_optimization(self, optimization_id: str) -> bool:
        """Mark an optimization as applied (for tracking)."""
        for opt in self.optimizations:
            if opt.optimization_id == optimization_id:
                opt.applied = True
                self._save_data()
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get workflow optimizer statistics."""
        return {
            'workflows_detected': len(self.workflow_patterns),
            'total_optimizations_suggested': sum(
                len(w.optimization_suggestions) for w in self.workflow_patterns.values()
            ),
            'optimizations_applied': sum(1 for o in self.optimizations if o.applied),
            'top_workflows': [
                {'name': w.name, 'frequency': w.frequency}
                for w in sorted(
                    self.workflow_patterns.values(),
                    key=lambda x: x.frequency,
                    reverse=True
                )[:5]
            ]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

class ErrorAnalyzer:
    """
    Analyzes errors and learns to avoid them.
    
    During idle time, this component:
    1. Reviews past errors and failures
    2. Identifies patterns in errors
    3. Develops strategies to prevent similar errors
    4. Updates learning models to avoid recurrence
    
    Om Vinayaka - Learning from mistakes to remove obstacles.
    """
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path or DEFAULT_IDLE_DATA_PATH
        os.makedirs(self.data_path, exist_ok=True)
        
        # Error records
        self.errors: Dict[str, ErrorRecord] = {}
        
        # Prevention strategies (error_type -> strategy)
        self.prevention_strategies: Dict[str, str] = {}
        
        # Error pattern frequencies
        self.error_frequencies: Dict[str, int] = defaultdict(int)
        
        # Load existing data
        self._load_data()
        
        print(f"[ErrorAnalyzer] Initialized - ready to learn from errors")
    
    def _load_data(self):
        """Load existing error records and strategies."""
        errors_file = os.path.join(self.data_path, "errors.json")
        if os.path.exists(errors_file):
            try:
                with open(errors_file, 'r') as f:
                    data = json.load(f)
                    for eid, edata in data.items():
                        self.errors[eid] = ErrorRecord(**edata)
            except Exception as e:
                print(f"[ErrorAnalyzer] Error loading errors: {e}")
        
        strategies_file = os.path.join(self.data_path, "prevention_strategies.json")
        if os.path.exists(strategies_file):
            try:
                with open(strategies_file, 'r') as f:
                    self.prevention_strategies = json.load(f)
            except Exception as e:
                print(f"[ErrorAnalyzer] Error loading strategies: {e}")
    
    def _save_data(self):
        """Save error records and strategies."""
        errors_file = os.path.join(self.data_path, "errors.json")
        with open(errors_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.errors.items()}, f, indent=2)
        
        strategies_file = os.path.join(self.data_path, "prevention_strategies.json")
        with open(strategies_file, 'w') as f:
            json.dump(self.prevention_strategies, f, indent=2)
    
    def record_error(self, error_type: str, error_message: str, 
                     context: Dict = None) -> ErrorRecord:
        """
        Record an error for later analysis.
        
        Args:
            error_type: Type of error (e.g., 'command_failed', 'clarification_needed')
            error_message: Error message or description
            context: Additional context about the error
            
        Returns:
            ErrorRecord object
        """
        error_id = hashlib.sha256(
            f"{error_type}:{error_message}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        error = ErrorRecord(
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            context=context or {}
        )
        
        self.errors[error_id] = error
        self.error_frequencies[error_type] += 1
        
        self._save_data()
        return error
    
    def analyze_errors(self) -> List[Dict]:
        """
        Analyze unanalyzed errors and develop prevention strategies.
        
        Returns:
            List of analysis results
        """
        analysis_results = []
        
        # Get unanalyzed errors
        unanalyzed = [e for e in self.errors.values() if not e.analyzed]
        
        for error in unanalyzed:
            result = self._analyze_single_error(error)
            if result:
                analysis_results.append(result)
                error.analyzed = True
        
        self._save_data()
        return analysis_results
    
    def _analyze_single_error(self, error: ErrorRecord) -> Optional[Dict]:
        """Analyze a single error and develop prevention strategy."""
        error_type = error.error_type.lower()
        
        # Develop prevention strategy based on error type
        strategy = None
        
        if 'clarification' in error_type or 'unclear' in error_type:
            strategy = self._strategy_for_clarification_error(error)
        elif 'command' in error_type or 'action' in error_type:
            strategy = self._strategy_for_command_error(error)
        elif 'timeout' in error_type or 'slow' in error_type:
            strategy = self._strategy_for_performance_error(error)
        elif 'permission' in error_type or 'access' in error_type:
            strategy = self._strategy_for_permission_error(error)
        else:
            strategy = self._strategy_generic(error)
        
        if strategy:
            error.prevention_strategy = strategy
            self.prevention_strategies[error.error_type] = strategy
            
            return {
                'error_id': error.error_id,
                'error_type': error.error_type,
                'strategy': strategy,
                'frequency': self.error_frequencies.get(error.error_type, 1)
            }
        
        return None
    
    def _strategy_for_clarification_error(self, error: ErrorRecord) -> str:
        """Develop strategy for clarification-related errors."""
        return (
            "When similar ambiguous input is detected, proactively ask specific "
            "clarifying questions before attempting action. Consider providing "
            "examples of valid inputs to guide the user."
        )
    
    def _strategy_for_command_error(self, error: ErrorRecord) -> str:
        """Develop strategy for command execution errors."""
        context = error.context
        if 'app' in context:
            return (
                f"For {context.get('app', 'this app')}, verify the action is available "
                "before attempting. If the action fails, suggest alternative approaches "
                "and learn the correct command mapping."
            )
        return (
            "Validate commands before execution. If a command fails, learn the "
            "correct format and suggest it for similar inputs in the future."
        )
    
    def _strategy_for_performance_error(self, error: ErrorRecord) -> str:
        """Develop strategy for performance-related errors."""
        return (
            "Monitor response times and preemptively notify the user if an operation "
            "may take longer than expected. Consider caching frequent operations and "
            "optimizing resource usage during idle time."
        )
    
    def _strategy_for_permission_error(self, error: ErrorRecord) -> str:
        """Develop strategy for permission-related errors."""
        return (
            "Before attempting restricted operations, check permissions first and "
            "inform the user if elevated access is needed. Provide clear guidance "
            "on how to grant necessary permissions."
        )
    
    def _strategy_generic(self, error: ErrorRecord) -> str:
        """Develop generic strategy for unknown error types."""
        return (
            f"When encountering '{error.error_type}' errors, log the context for "
            "future analysis. If this error type becomes frequent, develop a "
            "specialized prevention strategy."
        )
    
    def get_prevention_strategy(self, error_type: str) -> Optional[str]:
        """Get the prevention strategy for an error type."""
        return self.prevention_strategies.get(error_type)
    
    def get_frequent_errors(self, limit: int = 10) -> List[Dict]:
        """Get the most frequent error types."""
        sorted_errors = sorted(
            self.error_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {
                'error_type': error_type,
                'frequency': freq,
                'strategy': self.prevention_strategies.get(error_type)
            }
            for error_type, freq in sorted_errors
        ]
    
    def get_statistics(self) -> Dict:
        """Get error analyzer statistics."""
        total_errors = len(self.errors)
        analyzed_errors = sum(1 for e in self.errors.values() if e.analyzed)
        
        return {
            'total_errors_recorded': total_errors,
            'errors_analyzed': analyzed_errors,
            'prevention_strategies': len(self.prevention_strategies),
            'most_frequent_errors': self.get_frequent_errors(5),
            'analysis_coverage': analyzed_errors / max(1, total_errors)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-REFLECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class SelfReflectionEngine:
    """
    Self-reflection and dynamic thinking engine.
    
    During idle time, this component:
    1. Analyzes own performance and decision-making
    2. Asks "why" and "what" questions for deeper understanding
    3. Identifies areas for improvement
    4. Generates actionable insights for continuous learning
    
    This makes Om Vinayaka truly self-aware and continuously improving.
    
    Om Vinayaka - Reflecting inward to better serve outward.
    """
    
    def __init__(self, data_path: str = None, learning_path: str = None):
        self.data_path = data_path or DEFAULT_IDLE_DATA_PATH
        self.learning_path = learning_path or DEFAULT_LEARNING_PATH
        os.makedirs(self.data_path, exist_ok=True)
        
        # Self-reflection insights
        self.insights: List[SelfReflectionInsight] = []
        
        # Performance metrics to reflect on
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Reflection questions (dynamic thinking)
        self.reflection_questions = [
            # WHY questions (understanding)
            ("why", "Why did certain commands succeed while others needed clarification?"),
            ("why", "Why do users frequently use certain workflows?"),
            ("why", "Why did some predictions have low confidence?"),
            ("why", "Why are certain apps used more than others?"),
            
            # WHAT questions (improvement)
            ("what", "What patterns in user behavior can inform better suggestions?"),
            ("what", "What improvements would most benefit users?"),
            ("what", "What errors are most impactful and how can they be prevented?"),
            ("what", "What new capabilities would help users achieve their goals?"),
            
            # HOW questions (implementation)
            ("how", "How can response times be improved?"),
            ("how", "How can predictions be made more accurate?"),
            ("how", "How can the user experience be made more intuitive?"),
            
            # WHEN questions (timing)
            ("when", "When do users most need assistance?"),
            ("when", "When is the best time to offer suggestions?"),
        ]
        
        # Load existing data
        self._load_data()
        
        print(f"[SelfReflectionEngine] Initialized - ready for dynamic thinking")
    
    def _load_data(self):
        """Load existing insights."""
        insights_file = os.path.join(self.data_path, "self_reflection_insights.json")
        if os.path.exists(insights_file):
            try:
                with open(insights_file, 'r') as f:
                    data = json.load(f)
                    self.insights = [SelfReflectionInsight(**i) for i in data]
            except Exception as e:
                print(f"[SelfReflectionEngine] Error loading insights: {e}")
    
    def _save_data(self):
        """Save insights."""
        insights_file = os.path.join(self.data_path, "self_reflection_insights.json")
        with open(insights_file, 'w') as f:
            json.dump([asdict(i) for i in self.insights], f, indent=2)
    
    def reflect(self, learning_stats: Dict = None, 
                error_stats: Dict = None) -> List[SelfReflectionInsight]:
        """
        Perform self-reflection and generate insights.
        
        Args:
            learning_stats: Statistics from learning engine
            error_stats: Statistics from error analyzer
            
        Returns:
            List of new insights generated
        """
        new_insights = []
        
        # Load stats if not provided
        if not learning_stats:
            learning_stats = self._load_learning_stats()
        
        # Select questions to reflect on (rotate through them)
        num_questions = min(3, len(self.reflection_questions))
        question_indices = [
            (len(self.insights) + i) % len(self.reflection_questions)
            for i in range(num_questions)
        ]
        
        for idx in question_indices:
            q_type, question = self.reflection_questions[idx]
            
            insight = self._answer_reflection_question(
                q_type, question, learning_stats, error_stats
            )
            
            if insight:
                self.insights.append(insight)
                new_insights.append(insight)
        
        self._save_data()
        return new_insights
    
    def _load_learning_stats(self) -> Dict:
        """Load learning statistics."""
        stats_file = os.path.join(self.learning_path, "stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"[SelfReflectionEngine] Could not load stats from {stats_file}: {e}. Operating with default stats.")
        return {}
    
    def _answer_reflection_question(self, q_type: str, question: str,
                                     learning_stats: Dict,
                                     error_stats: Dict) -> Optional[SelfReflectionInsight]:
        """Generate an insight by answering a reflection question."""
        insight_text = ""
        action_items = []
        
        # Generate insight based on question type and available data
        if "commands succeed" in question.lower():
            insight_text, action_items = self._reflect_on_success_patterns(learning_stats)
        elif "workflows" in question.lower():
            insight_text, action_items = self._reflect_on_workflows(learning_stats)
        elif "predictions" in question.lower():
            insight_text, action_items = self._reflect_on_predictions(learning_stats)
        elif "errors" in question.lower():
            insight_text, action_items = self._reflect_on_errors(error_stats)
        elif "behavior" in question.lower():
            insight_text, action_items = self._reflect_on_user_behavior(learning_stats)
        elif "improvements" in question.lower():
            insight_text, action_items = self._reflect_on_improvements(learning_stats, error_stats)
        elif "response times" in question.lower():
            insight_text, action_items = self._reflect_on_performance()
        else:
            insight_text, action_items = self._reflect_generic(question, learning_stats)
        
        if not insight_text:
            return None
        
        insight_id = hashlib.sha256(
            f"{question}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        return SelfReflectionInsight(
            insight_id=insight_id,
            category=q_type,
            question=question,
            insight=insight_text,
            action_items=action_items
        )
    
    def _reflect_on_success_patterns(self, stats: Dict) -> tuple:
        """Reflect on why certain commands succeed."""
        patterns_learned = stats.get('patterns_learned', 0)
        total_interactions = stats.get('total_interactions', 0)
        
        if patterns_learned == 0:
            return ("No patterns learned yet. Need more user interactions to analyze.", [])
        
        success_rate = patterns_learned / max(1, total_interactions)
        
        if success_rate > 0.7:
            insight = (
                f"High pattern recognition ({success_rate:.1%}) suggests commands are being "
                "understood well. Success comes from matching user input patterns to known actions."
            )
            actions = ["Continue learning new patterns", "Expand vocabulary for actions"]
        else:
            insight = (
                f"Pattern recognition at {success_rate:.1%} indicates room for improvement. "
                "Commands succeed when they closely match learned patterns."
            )
            actions = [
                "Improve fuzzy matching for similar commands",
                "Add more synonym mappings for common actions",
                "Provide better feedback when commands are unclear"
            ]
        
        return (insight, actions)
    
    def _reflect_on_workflows(self, stats: Dict) -> tuple:
        """Reflect on user workflow patterns."""
        patterns = stats.get('patterns_learned', 0)
        
        insight = (
            "Users develop consistent workflows because they optimize for their specific needs. "
            "Frequent workflows represent the core value proposition of the system."
        )
        actions = [
            "Identify and optimize the most frequent workflows",
            "Create shortcuts for common workflow sequences",
            "Suggest workflow improvements during idle time"
        ]
        
        return (insight, actions)
    
    def _reflect_on_predictions(self, stats: Dict) -> tuple:
        """Reflect on prediction accuracy."""
        insight = (
            "Prediction confidence depends on pattern frequency and context matching. "
            "Low confidence predictions often occur with novel inputs or ambiguous contexts."
        )
        actions = [
            "Require higher confidence threshold before auto-executing",
            "Ask for confirmation on medium-confidence predictions",
            "Learn from rejected predictions to improve accuracy"
        ]
        
        return (insight, actions)
    
    def _reflect_on_errors(self, error_stats: Dict) -> tuple:
        """Reflect on error patterns."""
        if not error_stats:
            return ("No error data available for reflection.", [])
        
        total_errors = error_stats.get('total_errors_recorded', 0)
        strategies = error_stats.get('prevention_strategies', 0)
        
        insight = (
            f"With {total_errors} errors recorded and {strategies} prevention strategies developed, "
            "the system is actively learning from mistakes. Most impactful errors are those that "
            "interrupt user workflows."
        )
        actions = [
            "Prioritize prevention strategies for workflow-interrupting errors",
            "Implement proactive error detection",
            "Provide helpful recovery suggestions when errors occur"
        ]
        
        return (insight, actions)
    
    def _reflect_on_user_behavior(self, stats: Dict) -> tuple:
        """Reflect on user behavior patterns."""
        insight = (
            "User behavior reveals preferences through repeated actions and choices. "
            "Patterns in timing, app usage, and command styles provide optimization opportunities."
        )
        actions = [
            "Track temporal patterns in user activity",
            "Personalize suggestions based on observed preferences",
            "Adapt response verbosity to user style"
        ]
        
        return (insight, actions)
    
    def _reflect_on_improvements(self, learning_stats: Dict, error_stats: Dict) -> tuple:
        """Reflect on what improvements would most benefit users."""
        actions = []
        
        # Analyze learning stats
        if learning_stats.get('patterns_learned', 0) < 50:
            actions.append("Focus on expanding pattern recognition coverage")
        
        # Analyze error stats
        if error_stats and error_stats.get('total_errors_recorded', 0) > 10:
            actions.append("Implement top prevention strategies to reduce errors")
        
        actions.append("Optimize response times for common operations")
        actions.append("Improve natural language understanding for edge cases")
        
        insight = (
            "The most impactful improvements are those that reduce friction in daily workflows. "
            "Focus areas: faster responses, better understanding, fewer errors."
        )
        
        return (insight, actions)
    
    def _reflect_on_performance(self) -> tuple:
        """Reflect on performance optimization opportunities."""
        insight = (
            "Response times can be improved through: caching frequent patterns, "
            "preloading common resources, and optimizing pattern matching algorithms."
        )
        actions = [
            "Implement pattern caching for frequent commands",
            "Preload resources for predicted next actions",
            "Optimize context summarization for faster processing"
        ]
        
        return (insight, actions)
    
    def _reflect_generic(self, question: str, stats: Dict) -> tuple:
        """Generic reflection for unhandled questions."""
        insight = (
            f"Reflecting on: {question}. "
            "This requires ongoing observation and data collection to develop meaningful insights."
        )
        actions = ["Continue collecting relevant data", "Revisit this question in future reflections"]
        
        return (insight, actions)
    
    def get_recent_insights(self, limit: int = 10) -> List[SelfReflectionInsight]:
        """Get the most recent insights."""
        return sorted(self.insights, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_unapplied_action_items(self) -> List[Dict]:
        """Get action items from insights that haven't been applied."""
        items = []
        for insight in self.insights:
            if not insight.applied and insight.action_items:
                for action in insight.action_items:
                    items.append({
                        'insight_id': insight.insight_id,
                        'category': insight.category,
                        'question': insight.question,
                        'action': action
                    })
        return items
    
    def mark_insight_applied(self, insight_id: str) -> bool:
        """Mark an insight's actions as applied."""
        for insight in self.insights:
            if insight.insight_id == insight_id:
                insight.applied = True
                self._save_data()
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get self-reflection statistics."""
        total_insights = len(self.insights)
        applied_insights = sum(1 for i in self.insights if i.applied)
        
        by_category = defaultdict(int)
        for insight in self.insights:
            by_category[insight.category] += 1
        
        return {
            'total_insights': total_insights,
            'applied_insights': applied_insights,
            'unapplied_action_items': len(self.get_unapplied_action_items()),
            'insights_by_category': dict(by_category),
            'recent_insights': [
                {'question': i.question, 'insight': i.insight[:100] + '...'}
                for i in self.get_recent_insights(3)
            ]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# IDLE MODE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class IdleModeManager:
    """
    Manages idle mode and triggers self-improvement activities.
    
    When no user activity is detected for a configurable period:
    1. Enters idle mode
    2. Runs workflow optimization
    3. Analyzes errors
    4. Performs self-reflection
    5. Gracefully exits when user activity resumes
    
    Om Vinayaka - Always improving, even when at rest.
    """
    
    VERSION = IDLE_MODE_VERSION
    
    def __init__(self, 
                 idle_timeout_seconds: int = DEFAULT_IDLE_TIMEOUT_SECONDS,
                 data_path: str = None,
                 learning_path: str = None):
        """
        Initialize the IdleModeManager.
        
        Args:
            idle_timeout_seconds: Seconds of inactivity before entering idle mode
            data_path: Path for storing idle mode data
            learning_path: Path to learning engine data
        """
        self.idle_timeout = max(
            MIN_IDLE_TIMEOUT_SECONDS,
            min(idle_timeout_seconds, MAX_IDLE_TIMEOUT_SECONDS)
        )
        
        self.data_path = data_path or DEFAULT_IDLE_DATA_PATH
        self.learning_path = learning_path or DEFAULT_LEARNING_PATH
        
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize state
        self.state = IdleModeState()
        
        # Initialize components
        self.workflow_optimizer = WorkflowOptimizer(self.learning_path, self.data_path)
        self.error_analyzer = ErrorAnalyzer(self.data_path)
        self.self_reflection = SelfReflectionEngine(self.data_path, self.learning_path)
        
        # Thread management
        self._idle_thread: Optional[threading.Thread] = None
        self._stop_idle = threading.Event()
        self._activity_lock = threading.Lock()
        
        # Callbacks
        self._on_idle_start_callback: Optional[Callable] = None
        self._on_idle_end_callback: Optional[Callable] = None
        self._on_optimization_callback: Optional[Callable[[Dict], None]] = None
        
        # Load state
        self._load_state()
        
        print(f"[IdleModeManager] Initialized v{self.VERSION}")
        print(f"[IdleModeManager] Idle timeout: {self.idle_timeout} seconds")
        print(f"[IdleModeManager] Components: WorkflowOptimizer, ErrorAnalyzer, SelfReflectionEngine")
    
    def _load_state(self):
        """Load idle mode state."""
        state_file = os.path.join(self.data_path, "idle_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    # Only load persistent stats, not current state
                    self.state.total_idle_time_seconds = data.get('total_idle_time_seconds', 0)
                    self.state.optimizations_made = data.get('optimizations_made', 0)
                    self.state.errors_analyzed = data.get('errors_analyzed', 0)
                    self.state.reflections_completed = data.get('reflections_completed', 0)
            except Exception:
                pass
    
    def _save_state(self):
        """Save idle mode state."""
        state_file = os.path.join(self.data_path, "idle_state.json")
        with open(state_file, 'w') as f:
            json.dump(asdict(self.state), f, indent=2)
    
    def start(self):
        """Start monitoring for idle mode."""
        if self._idle_thread and self._idle_thread.is_alive():
            return
        
        self._stop_idle.clear()
        self._idle_thread = threading.Thread(
            target=self._idle_monitor_loop,
            daemon=True,
            name="VA21-IdleMode"
        )
        self._idle_thread.start()
        
        print("[IdleModeManager] Started monitoring for idle mode")
    
    def stop(self):
        """Stop idle mode monitoring."""
        self._stop_idle.set()
        if self._idle_thread:
            self._idle_thread.join(timeout=5)
        
        if self.state.is_idle:
            self._exit_idle_mode()
        
        self._save_state()
        print("[IdleModeManager] Stopped idle mode monitoring")
    
    def record_user_activity(self):
        """Record user activity (resets idle timer)."""
        with self._activity_lock:
            self.state.last_user_activity = datetime.now().isoformat()
            
            # If we're in idle mode, exit it
            if self.state.is_idle:
                self._exit_idle_mode()
    
    def _idle_monitor_loop(self):
        """Background thread that monitors for idle mode."""
        while not self._stop_idle.is_set():
            # Check every 10 seconds
            if self._stop_idle.wait(timeout=10):
                break
            
            # Calculate time since last activity
            with self._activity_lock:
                last_activity = datetime.fromisoformat(self.state.last_user_activity)
                idle_seconds = (datetime.now() - last_activity).total_seconds()
            
            # Check if we should enter/stay in idle mode
            if idle_seconds >= self.idle_timeout:
                if not self.state.is_idle:
                    self._enter_idle_mode()
                else:
                    # Continue self-improvement activities
                    self._run_idle_activities()
            elif self.state.is_idle:
                self._exit_idle_mode()
    
    def _enter_idle_mode(self):
        """Enter idle mode and start self-improvement."""
        self.state.is_idle = True
        self.state.idle_start_time = datetime.now().isoformat()
        
        print("[IdleModeManager] 🌙 Entering idle mode - starting self-improvement")
        
        if self._on_idle_start_callback:
            self._on_idle_start_callback()
        
        # Run initial activities
        self._run_idle_activities()
    
    def _exit_idle_mode(self):
        """Exit idle mode."""
        if not self.state.is_idle:
            return
        
        # Calculate idle duration
        if self.state.idle_start_time:
            start_time = datetime.fromisoformat(self.state.idle_start_time)
            idle_duration = (datetime.now() - start_time).total_seconds()
            self.state.total_idle_time_seconds += idle_duration
        
        self.state.is_idle = False
        self.state.idle_start_time = None
        
        self._save_state()
        
        print("[IdleModeManager] ☀️ Exiting idle mode - user activity detected")
        
        if self._on_idle_end_callback:
            self._on_idle_end_callback()
    
    def _run_idle_activities(self):
        """Run self-improvement activities during idle time."""
        if not self.state.is_idle:
            return
        
        # Run activities based on their intervals
        current_time = datetime.now()
        
        # Workflow analysis
        try:
            workflows = self.workflow_optimizer.analyze_workflows()
            if workflows:
                self.state.optimizations_made += len(workflows)
                print(f"[IdleModeManager] 🔄 Analyzed {len(workflows)} workflow patterns")
                
                if self._on_optimization_callback:
                    self._on_optimization_callback({
                        'type': 'workflow',
                        'count': len(workflows),
                        'suggestions': self.workflow_optimizer.get_optimization_suggestions(3)
                    })
        except Exception as e:
            print(f"[IdleModeManager] Workflow analysis error: {e}")
        
        # Error analysis
        try:
            error_results = self.error_analyzer.analyze_errors()
            if error_results:
                self.state.errors_analyzed += len(error_results)
                print(f"[IdleModeManager] 🔍 Analyzed {len(error_results)} errors")
        except Exception as e:
            print(f"[IdleModeManager] Error analysis error: {e}")
        
        # Self-reflection
        try:
            learning_stats = self._get_learning_stats()
            error_stats = self.error_analyzer.get_statistics()
            
            insights = self.self_reflection.reflect(learning_stats, error_stats)
            if insights:
                self.state.reflections_completed += len(insights)
                print(f"[IdleModeManager] 🧠 Generated {len(insights)} self-reflection insights")
                
                for insight in insights[:2]:  # Log first 2 insights
                    print(f"[IdleModeManager]    💡 {insight.question[:50]}...")
        except Exception as e:
            print(f"[IdleModeManager] Self-reflection error: {e}")
        
        self._save_state()
    
    def _get_learning_stats(self) -> Dict:
        """Get learning statistics."""
        stats_file = os.path.join(self.learning_path, "stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"[IdleModeManager] Could not load stats from {stats_file}: {e}. Operating with default stats.")
        return {}
    
    def record_error(self, error_type: str, error_message: str, 
                     context: Dict = None) -> ErrorRecord:
        """Record an error for analysis."""
        return self.error_analyzer.record_error(error_type, error_message, context)
    
    def set_callbacks(self, 
                      on_idle_start: Callable = None,
                      on_idle_end: Callable = None,
                      on_optimization: Callable[[Dict], None] = None):
        """Set callbacks for idle mode events."""
        self._on_idle_start_callback = on_idle_start
        self._on_idle_end_callback = on_idle_end
        self._on_optimization_callback = on_optimization
    
    def force_idle_activities(self):
        """Manually trigger idle activities (for testing/immediate optimization)."""
        print("[IdleModeManager] 🔧 Forcing idle activities...")
        
        # Temporarily set idle flag
        was_idle = self.state.is_idle
        self.state.is_idle = True
        
        self._run_idle_activities()
        
        # Restore state
        self.state.is_idle = was_idle
    
    def get_status(self) -> Dict:
        """Get idle mode status."""
        with self._activity_lock:
            last_activity = self.state.last_user_activity
        
        return {
            'version': self.VERSION,
            'is_idle': self.state.is_idle,
            'idle_timeout_seconds': self.idle_timeout,
            'last_user_activity': last_activity,
            'total_idle_time_hours': self.state.total_idle_time_seconds / 3600,
            'optimizations_made': self.state.optimizations_made,
            'errors_analyzed': self.state.errors_analyzed,
            'reflections_completed': self.state.reflections_completed,
            'workflow_optimizer': self.workflow_optimizer.get_statistics(),
            'error_analyzer': self.error_analyzer.get_statistics(),
            'self_reflection': self.self_reflection.get_statistics(),
        }
    
    def get_improvement_summary(self) -> str:
        """Get a human-readable summary of self-improvements made."""
        workflow_stats = self.workflow_optimizer.get_statistics()
        error_stats = self.error_analyzer.get_statistics()
        reflection_stats = self.self_reflection.get_statistics()
        
        summary = f"""
╔═══════════════════════════════════════════════════════════════════╗
║           🙏 OM VINAYAKA - SELF-IMPROVEMENT SUMMARY 🙏             ║
╚═══════════════════════════════════════════════════════════════════╝

📊 STATISTICS
• Total idle time: {self.state.total_idle_time_seconds / 3600:.1f} hours
• Optimizations made: {self.state.optimizations_made}
• Errors analyzed: {self.state.errors_analyzed}
• Reflections completed: {self.state.reflections_completed}

🔄 WORKFLOW OPTIMIZATION
• Workflows detected: {workflow_stats['workflows_detected']}
• Optimization suggestions: {workflow_stats['total_optimizations_suggested']}

🔍 ERROR LEARNING
• Errors recorded: {error_stats['total_errors_recorded']}
• Prevention strategies: {error_stats['prevention_strategies']}
• Analysis coverage: {error_stats['analysis_coverage']:.1%}

🧠 SELF-REFLECTION
• Total insights: {reflection_stats['total_insights']}
• Action items pending: {reflection_stats['unapplied_action_items']}

"""
        
        # Add recent insights
        recent_insights = self.self_reflection.get_recent_insights(3)
        if recent_insights:
            summary += "💡 RECENT INSIGHTS\n"
            for insight in recent_insights:
                summary += f"• {insight.insight[:80]}...\n"
        
        # Add top optimization suggestions
        suggestions = self.workflow_optimizer.get_optimization_suggestions(3)
        if suggestions:
            summary += "\n🎯 TOP OPTIMIZATION SUGGESTIONS\n"
            for s in suggestions:
                summary += f"• [{s['workflow']}] {s['suggestion'][:60]}...\n"
        
        summary += "\n─────────────────────────────────────────────────────────────────\n"
        summary += "Om Vinayaka - Always learning, always improving!\n"
        
        return summary


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_idle_mode_manager_instance = None


def get_idle_mode_manager(idle_timeout_seconds: int = DEFAULT_IDLE_TIMEOUT_SECONDS,
                          data_path: str = None,
                          learning_path: str = None) -> IdleModeManager:
    """Get or create the IdleModeManager singleton."""
    global _idle_mode_manager_instance
    
    if _idle_mode_manager_instance is None:
        _idle_mode_manager_instance = IdleModeManager(
            idle_timeout_seconds=idle_timeout_seconds,
            data_path=data_path,
            learning_path=learning_path
        )
    
    return _idle_mode_manager_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the idle mode system."""
    print("=" * 70)
    print("VA21 OS - Om Vinayaka Idle Mode Self-Improvement Test")
    print("Om Vinayaka - The remover of obstacles")
    print("=" * 70)
    
    # Get the idle mode manager
    manager = get_idle_mode_manager(idle_timeout_seconds=10)  # Short timeout for testing
    
    # Set callbacks
    def on_idle_start():
        print("🌙 Callback: Entered idle mode")
    
    def on_idle_end():
        print("☀️ Callback: Exited idle mode")
    
    def on_optimization(result):
        print(f"🔧 Callback: Optimization - {result}")
    
    manager.set_callbacks(on_idle_start, on_idle_end, on_optimization)
    
    # Test error recording
    print("\n--- Recording Test Errors ---")
    manager.record_error("command_failed", "Unknown command: xyz", {"input": "xyz"})
    manager.record_error("clarification_needed", "Ambiguous input", {"input": "do thing"})
    manager.record_error("command_failed", "App not found", {"app": "unknown_app"})
    print("✓ Recorded 3 test errors")
    
    # Force idle activities (instead of waiting)
    print("\n--- Running Idle Activities ---")
    manager.force_idle_activities()
    
    # Show status
    print("\n--- Status ---")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
    
    # Show improvement summary
    print("\n--- Improvement Summary ---")
    print(manager.get_improvement_summary())
    
    # Test starting actual monitoring (briefly)
    print("\n--- Testing Idle Mode Monitoring (10 seconds) ---")
    manager.start()
    
    # Simulate user activity
    print("Simulating user activity...")
    manager.record_user_activity()
    
    time.sleep(2)
    
    # Stop monitoring
    manager.stop()
    
    print("\n" + "=" * 70)
    print("Test complete! Om Vinayaka is ready to improve during idle time.")
    print("=" * 70)


if __name__ == "__main__":
    main()
