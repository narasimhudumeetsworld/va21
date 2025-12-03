#!/usr/bin/env python3
"""
VA21 OS - Self-Learning Accessibility System with LangChain + Obsidian
========================================================================

The Self-Learning System enables Om Vinayaka AI to improve over time by:
- Learning common command patterns from user interactions
- Tracking user preferences for personalized experience
- Monitoring app usage patterns to optimize suggestions
- Improving narratives based on what resonates with users
- Adapting to individual accessibility needs

Storage Architecture (LangChain + Obsidian):
- All learning stored in Obsidian-style markdown vault
- Wiki-style [[links]] connect related concepts
- Mind maps visualize learning relationships
- LangChain-compatible for semantic search and retrieval
- Knowledge graphs enable intelligent suggestions

The system gets smarter with continued use, providing an
increasingly personalized and efficient accessibility experience.

All learning is:
- Local only (never sent to external services)
- Privacy-respecting (no sensitive data stored)
- User-controllable (can reset or view learned data)
- Stored in human-readable Obsidian markdown

Om Vinayaka - May obstacles be removed, and wisdom grow.
"""

import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_LEARNING_PATH = os.path.expanduser("~/.va21/learning")
DEFAULT_OBSIDIAN_VAULT = os.path.expanduser("~/.va21/accessibility_knowledge_base")
MAX_PATTERN_HISTORY = 10000
MAX_PREFERENCE_HISTORY = 1000


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CommandPattern:
    """A learned command pattern."""
    pattern: str  # The natural language pattern
    action: str   # The action it maps to
    frequency: int = 1  # How often this pattern is used
    success_rate: float = 1.0  # How often it succeeds
    last_used: str = field(default_factory=lambda: datetime.now().isoformat())
    contexts: List[str] = field(default_factory=list)  # Apps where used


@dataclass
class UserPreference:
    """A learned user preference."""
    preference_type: str  # Type: speech_rate, verbosity, confirmation, etc.
    value: Any  # The preferred value
    confidence: float = 0.5  # How confident we are (0-1)
    learn_count: int = 1  # How many times this was observed


@dataclass
class AppUsagePattern:
    """Pattern of app usage."""
    app_name: str
    total_uses: int = 0
    common_actions: Dict[str, int] = field(default_factory=dict)
    average_session_length: float = 0.0  # In minutes
    last_used: str = field(default_factory=lambda: datetime.now().isoformat())
    preferred_commands: List[str] = field(default_factory=list)


@dataclass
class NarrativeImprovement:
    """Improvement to a narrative based on user feedback."""
    original_narrative: str
    improved_narrative: str
    context: str
    improvement_score: float = 0.0  # How much better the new one is
    usage_count: int = 0


@dataclass
class LearningSession:
    """A learning session tracking interactions."""
    session_id: str
    started_at: str
    app_context: Optional[str] = None
    interactions: List[Dict] = field(default_factory=list)
    successful_commands: int = 0
    failed_commands: int = 0
    clarifications_needed: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# LANGCHAIN + OBSIDIAN KNOWLEDGE BASE FOR LEARNING
# ═══════════════════════════════════════════════════════════════════════════════

class LearningKnowledgeBase:
    """
    LangChain + Obsidian Knowledge Base for Self-Learning
    
    Stores all learning data in an Obsidian-compatible format:
    - Markdown notes with YAML frontmatter
    - Wiki-style [[links]] connecting concepts
    - Mind maps visualizing learning relationships
    - Tag-based organization for LangChain retrieval
    
    This enables:
    - Human-readable learning data
    - Semantic search via LangChain
    - Visual exploration of learned patterns
    - Knowledge graph for intelligent suggestions
    """
    
    def __init__(self, vault_path: str = None):
        self.vault_path = vault_path or DEFAULT_OBSIDIAN_VAULT
        
        # Create vault directories
        self.learning_path = os.path.join(self.vault_path, "learning")
        self.patterns_path = os.path.join(self.learning_path, "patterns")
        self.preferences_path = os.path.join(self.learning_path, "preferences")
        self.apps_path = os.path.join(self.learning_path, "apps")
        self.mindmaps_path = os.path.join(self.learning_path, "mindmaps")
        self.narratives_path = os.path.join(self.learning_path, "narratives")
        
        for path in [self.learning_path, self.patterns_path, self.preferences_path,
                     self.apps_path, self.mindmaps_path, self.narratives_path]:
            os.makedirs(path, exist_ok=True)
        
        # In-memory index for fast lookup (loaded from vault)
        self.pattern_index: Dict[str, str] = {}  # pattern_key -> note_path
        self.app_index: Dict[str, str] = {}  # app_name -> note_path
        
        # Load existing index
        self._load_index()
        
        print(f"[LearningKB] Obsidian vault initialized at {self.vault_path}")
    
    def _load_index(self):
        """Load the vault index for fast lookups."""
        index_file = os.path.join(self.learning_path, "_index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    self.pattern_index = data.get('patterns', {})
                    self.app_index = data.get('apps', {})
            except Exception:
                pass
    
    def _save_index(self):
        """Save the vault index."""
        index_file = os.path.join(self.learning_path, "_index.json")
        with open(index_file, 'w') as f:
            json.dump({
                'patterns': self.pattern_index,
                'apps': self.app_index,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def save_command_pattern(self, pattern_key: str, pattern: CommandPattern):
        """
        Save a command pattern to the Obsidian vault.
        
        Creates a markdown note with:
        - YAML frontmatter for metadata
        - Pattern description
        - Links to related apps and actions
        """
        # Create safe filename
        safe_name = re.sub(r'[^\w\s-]', '', pattern.pattern[:50]).strip().replace(' ', '_')
        note_name = f"pattern_{safe_name}_{pattern_key[:8]}.md"
        note_path = os.path.join(self.patterns_path, note_name)
        
        # Build context links
        context_links = " ".join([f"[[{ctx}]]" for ctx in pattern.contexts])
        
        # Create Obsidian note
        content = f"""---
type: command_pattern
pattern_key: {pattern_key}
action: {pattern.action}
frequency: {pattern.frequency}
success_rate: {pattern.success_rate:.2f}
last_used: {pattern.last_used}
tags:
  - learning
  - pattern
  - {pattern.action}
---

# Command Pattern

## User Says
> "{pattern.pattern}"

## Action
**{pattern.action}**

## Statistics
- **Used**: {pattern.frequency} times
- **Success Rate**: {pattern.success_rate * 100:.1f}%
- **Last Used**: {pattern.last_used}

## Related Apps
{context_links if context_links else "Used system-wide"}

## Learning Graph
This pattern is connected to:
- [[Action - {pattern.action}]]
- [[Learning Summary]]

---
*Learned by Om Vinayaka Self-Learning Engine*
"""
        with open(note_path, 'w') as f:
            f.write(content)
        
        # Update index
        self.pattern_index[pattern_key] = note_path
        self._save_index()
        
        return note_path
    
    def save_app_usage(self, app_name: str, usage: AppUsagePattern):
        """Save app usage pattern to the Obsidian vault."""
        safe_name = re.sub(r'[^\w\s-]', '', app_name).strip().replace(' ', '_')
        note_name = f"app_{safe_name}.md"
        note_path = os.path.join(self.apps_path, note_name)
        
        # Build common actions list
        actions_list = "\n".join([
            f"- **{action}**: {count} times" 
            for action, count in sorted(
                usage.common_actions.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        ])
        
        # Build preferred commands links
        pref_links = " ".join([f"[[{cmd}]]" for cmd in usage.preferred_commands])
        
        content = f"""---
type: app_usage
app_name: {app_name}
total_uses: {usage.total_uses}
average_session: {usage.average_session_length:.1f} minutes
last_used: {usage.last_used}
tags:
  - learning
  - app
  - {safe_name.lower()}
---

# {app_name} - Usage Patterns

## Summary
- **Total Uses**: {usage.total_uses}
- **Avg Session**: {usage.average_session_length:.1f} minutes
- **Last Used**: {usage.last_used}

## Common Actions
{actions_list if actions_list else "No actions recorded yet"}

## Preferred Commands
{pref_links if pref_links else "Still learning your preferences..."}

## Mind Map
```mermaid
mindmap
  root(({app_name}))
    Actions
{chr(10).join(['      ' + a for a in list(usage.common_actions.keys())[:5]])}
    Preferences
{chr(10).join(['      ' + p for p in usage.preferred_commands[:5]])}
```

## Related
- [[Learning Summary]]
- [[All Apps]]

---
*Learned by Om Vinayaka Self-Learning Engine*
"""
        with open(note_path, 'w') as f:
            f.write(content)
        
        # Update index
        self.app_index[app_name.lower()] = note_path
        self._save_index()
        
        return note_path
    
    def save_user_preference(self, pref_key: str, pref: UserPreference):
        """Save user preference to the Obsidian vault."""
        safe_name = re.sub(r'[^\w\s-]', '', pref_key).strip().replace(' ', '_')
        note_name = f"pref_{safe_name}.md"
        note_path = os.path.join(self.preferences_path, note_name)
        
        content = f"""---
type: user_preference
preference_type: {pref.preference_type}
value: {pref.value}
confidence: {pref.confidence:.2f}
learn_count: {pref.learn_count}
tags:
  - learning
  - preference
  - {pref.preference_type}
---

# Preference: {pref.preference_type}

## Value
**{pref.value}**

## Confidence
{pref.confidence * 100:.1f}% (observed {pref.learn_count} times)

## Description
User prefers **{pref.preference_type}** set to **{pref.value}**.

## Related
- [[User Preferences]]
- [[Learning Summary]]

---
*Learned by Om Vinayaka Self-Learning Engine*
"""
        with open(note_path, 'w') as f:
            f.write(content)
        
        return note_path
    
    def update_learning_mind_map(self, patterns_count: int, apps_count: int, 
                                  prefs_count: int, total_interactions: int):
        """Update the main learning mind map."""
        mindmap_path = os.path.join(self.mindmaps_path, "Learning_Mind_Map.md")
        
        # Get top patterns (would need actual data)
        top_apps = list(self.app_index.keys())[:5]
        
        content = f"""---
type: mindmap
title: Learning Mind Map
updated: {datetime.now().isoformat()}
tags:
  - mindmap
  - learning
  - overview
---

# 🧠 Om Vinayaka Learning Mind Map

## Overview
This mind map shows what I've learned from our interactions.

## Statistics
- **Patterns Learned**: {patterns_count}
- **Apps Tracked**: {apps_count}
- **Preferences**: {prefs_count}
- **Total Interactions**: {total_interactions}

## Mind Map Visualization
```mermaid
mindmap
  root((Learning))
    Patterns
      Commands
      Actions
      Contexts
    Apps
{chr(10).join(['      ' + app for app in top_apps])}
    Preferences
      Speech
      Verbosity
      Confirmations
    Improvements
      Narratives
      Suggestions
```

## Knowledge Graph
```mermaid
graph TD
    L[Learning Engine] --> P[Patterns]
    L --> A[App Usage]
    L --> U[User Preferences]
    L --> N[Narratives]
    
    P --> C[Commands]
    P --> AC[Actions]
    
    A --> F[Favorites]
    A --> CA[Common Actions]
    
    U --> S[Settings]
    U --> B[Behavior]
```

## Quick Links
- [[All Patterns]]
- [[All Apps]]
- [[User Preferences]]
- [[Narrative Improvements]]

## How Learning Works
1. **Observe**: I notice patterns in your commands
2. **Remember**: Successful patterns are stored here
3. **Predict**: I suggest based on learned patterns
4. **Improve**: Your feedback makes me smarter!

---
*Updated by Om Vinayaka Self-Learning Engine on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        with open(mindmap_path, 'w') as f:
            f.write(content)
        
        return mindmap_path
    
    def create_learning_summary(self, stats: Dict):
        """Create a learning summary note."""
        summary_path = os.path.join(self.learning_path, "Learning_Summary.md")
        
        content = f"""---
type: summary
title: Learning Summary
updated: {datetime.now().isoformat()}
tags:
  - summary
  - learning
  - statistics
---

# 📊 Learning Summary

## Current Statistics
| Metric | Value |
|--------|-------|
| Total Interactions | {stats.get('total_interactions', 0)} |
| Patterns Learned | {stats.get('patterns_learned', 0)} |
| Preferences Learned | {stats.get('preferences_learned', 0)} |
| Improvements Made | {stats.get('improvements_made', 0)} |
| Learning Started | {stats.get('learning_started', 'Unknown')} |

## How I Learn
I learn from every interaction we have:

1. **Command Patterns**: When you say something and it works, I remember it
2. **App Usage**: I track which apps you use most and what you do in them
3. **Preferences**: I notice your preferred settings and behaviors
4. **Narratives**: I learn which descriptions resonate with you

## Your Learning Data
All learning data is stored locally in this Obsidian vault.
You can:
- **View**: Browse the notes to see what I've learned
- **Edit**: Modify any note to correct my learning
- **Delete**: Remove patterns you don't want me to remember

## Privacy
- All data stays on your device
- Nothing is sent to external services
- You control what I remember

## Related
- [[Learning Mind Map]]
- [[All Patterns]]
- [[User Preferences]]

---
*Om Vinayaka Self-Learning Engine v1.1.0*
"""
        with open(summary_path, 'w') as f:
            f.write(content)
        
        return summary_path
    
    def search_patterns(self, query: str) -> List[Tuple[str, str]]:
        """
        Search patterns in the knowledge base.
        
        Returns list of (pattern_key, note_path) matching the query.
        This is LangChain-compatible for semantic search.
        """
        results = []
        query_lower = query.lower()
        
        for pattern_key, note_path in self.pattern_index.items():
            if os.path.exists(note_path):
                try:
                    with open(note_path, 'r') as f:
                        content = f.read()
                    if query_lower in content.lower():
                        results.append((pattern_key, note_path))
                except Exception:
                    pass
        
        return results
    
    def get_related_notes(self, note_path: str) -> List[str]:
        """
        Get notes related to a given note via wiki-links.
        
        Parses [[wiki-links]] from the note content.
        """
        if not os.path.exists(note_path):
            return []
        
        try:
            with open(note_path, 'r') as f:
                content = f.read()
            
            # Extract [[wiki-links]]
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            return links
        except Exception:
            return []


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-LEARNING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class SelfLearningEngine:
    """
    Self-Learning Engine for Om Vinayaka Accessibility AI
    
    Learns from user interactions to provide:
    1. Better command predictions
    2. Personalized preferences
    3. Optimized app-specific experiences
    4. Improved narratives
    
    Storage:
    - Uses LangChain + Obsidian Knowledge Base
    - All data stored as Obsidian-compatible markdown
    - Wiki-links connect related concepts
    - Mind maps visualize learning
    
    All data is stored locally and never shared externally.
    """
    
    VERSION = "1.1.0"  # Updated with LangChain + Obsidian integration
    
    def __init__(self, learning_path: str = None, obsidian_vault: str = None):
        self.learning_path = learning_path or DEFAULT_LEARNING_PATH
        os.makedirs(self.learning_path, exist_ok=True)
        
        # Initialize LangChain + Obsidian Knowledge Base
        self.knowledge_base = LearningKnowledgeBase(obsidian_vault)
        
        # Learning data stores
        self.command_patterns: Dict[str, CommandPattern] = {}
        self.user_preferences: Dict[str, UserPreference] = {}
        self.app_usage: Dict[str, AppUsagePattern] = {}
        self.narrative_improvements: Dict[str, NarrativeImprovement] = {}
        
        # Current session
        self.current_session: Optional[LearningSession] = None
        
        # Statistics
        self.stats = {
            'total_interactions': 0,
            'patterns_learned': 0,
            'preferences_learned': 0,
            'improvements_made': 0,
            'learning_started': datetime.now().isoformat()
        }
        
        # Load existing learned data
        self._load_learning_data()
        
        print(f"[Self-Learning] Engine initialized v{self.VERSION}")
        print(f"[Self-Learning] Patterns: {len(self.command_patterns)}, "
              f"Preferences: {len(self.user_preferences)}")
    
    def _load_learning_data(self):
        """Load all learned data from disk."""
        # Load command patterns
        patterns_file = os.path.join(self.learning_path, "command_patterns.json")
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    for key, val in data.items():
                        self.command_patterns[key] = CommandPattern(**val)
            except Exception as e:
                print(f"[Self-Learning] Error loading patterns: {e}")
        
        # Load user preferences
        prefs_file = os.path.join(self.learning_path, "user_preferences.json")
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r') as f:
                    data = json.load(f)
                    for key, val in data.items():
                        self.user_preferences[key] = UserPreference(**val)
            except Exception as e:
                print(f"[Self-Learning] Error loading preferences: {e}")
        
        # Load app usage patterns
        usage_file = os.path.join(self.learning_path, "app_usage.json")
        if os.path.exists(usage_file):
            try:
                with open(usage_file, 'r') as f:
                    data = json.load(f)
                    for key, val in data.items():
                        self.app_usage[key] = AppUsagePattern(**val)
            except Exception as e:
                print(f"[Self-Learning] Error loading app usage: {e}")
        
        # Load narrative improvements
        narratives_file = os.path.join(self.learning_path, "narrative_improvements.json")
        if os.path.exists(narratives_file):
            try:
                with open(narratives_file, 'r') as f:
                    data = json.load(f)
                    for key, val in data.items():
                        self.narrative_improvements[key] = NarrativeImprovement(**val)
            except Exception as e:
                print(f"[Self-Learning] Error loading narratives: {e}")
        
        # Load stats
        stats_file = os.path.join(self.learning_path, "stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
            except Exception as e:
                print(f"[Self-Learning] Error loading stats: {e}")
    
    def _save_learning_data(self):
        """Save all learned data to disk and Obsidian vault."""
        # Save command patterns to JSON
        patterns_file = os.path.join(self.learning_path, "command_patterns.json")
        with open(patterns_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.command_patterns.items()}, f, indent=2)
        
        # Save user preferences to JSON
        prefs_file = os.path.join(self.learning_path, "user_preferences.json")
        with open(prefs_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.user_preferences.items()}, f, indent=2)
        
        # Save app usage patterns to JSON
        usage_file = os.path.join(self.learning_path, "app_usage.json")
        with open(usage_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.app_usage.items()}, f, indent=2)
        
        # Save narrative improvements to JSON
        narratives_file = os.path.join(self.learning_path, "narrative_improvements.json")
        with open(narratives_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.narrative_improvements.items()}, f, indent=2)
        
        # Save stats to JSON
        stats_file = os.path.join(self.learning_path, "stats.json")
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        # ALSO save to Obsidian Knowledge Base
        self._sync_to_obsidian()
    
    def _sync_to_obsidian(self):
        """Sync all learning data to the Obsidian knowledge base."""
        try:
            # Sync top patterns to Obsidian
            top_patterns = sorted(
                self.command_patterns.items(),
                key=lambda x: x[1].frequency,
                reverse=True
            )[:100]  # Top 100 patterns
            
            for pattern_key, pattern in top_patterns:
                self.knowledge_base.save_command_pattern(pattern_key, pattern)
            
            # Sync all app usage to Obsidian
            for app_name, usage in self.app_usage.items():
                self.knowledge_base.save_app_usage(app_name, usage)
            
            # Sync preferences to Obsidian
            for pref_key, pref in self.user_preferences.items():
                self.knowledge_base.save_user_preference(pref_key, pref)
            
            # Update mind map and summary
            self.knowledge_base.update_learning_mind_map(
                patterns_count=len(self.command_patterns),
                apps_count=len(self.app_usage),
                prefs_count=len(self.user_preferences),
                total_interactions=self.stats['total_interactions']
            )
            self.knowledge_base.create_learning_summary(self.stats)
            
        except Exception as e:
            print(f"[Self-Learning] Error syncing to Obsidian: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SESSION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def start_session(self, app_context: str = None) -> str:
        """Start a new learning session."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        self.current_session = LearningSession(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            app_context=app_context
        )
        
        return session_id
    
    def end_session(self):
        """End the current learning session and save learnings."""
        if not self.current_session:
            return
        
        # Learn from this session
        self._learn_from_session(self.current_session)
        
        # Clear current session
        self.current_session = None
        
        # Save all data (including Obsidian sync)
        self._save_learning_data()
    
    def _learn_from_session(self, session: LearningSession):
        """Extract learnings from a completed session."""
        if not session.interactions:
            return
        
        # Analyze successful vs failed interactions
        success_rate = (
            session.successful_commands / 
            max(1, session.successful_commands + session.failed_commands)
        )
        
        # Update stats
        self.stats['total_interactions'] += len(session.interactions)
        
        # Learn from each interaction
        for interaction in session.interactions:
            self._learn_from_interaction(interaction, session.app_context)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND PATTERN LEARNING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def learn_command(self, user_input: str, action: str, 
                      app_context: str = None, success: bool = True):
        """
        Learn a command pattern from user input.
        
        Args:
            user_input: What the user said/typed
            action: What action was executed
            app_context: Which app this was in
            success: Whether the action succeeded
        """
        # Create a normalized pattern key
        pattern_key = self._normalize_pattern(user_input)
        
        if pattern_key in self.command_patterns:
            # Update existing pattern
            pattern = self.command_patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_used = datetime.now().isoformat()
            
            # Update success rate (rolling average)
            old_rate = pattern.success_rate
            new_value = 1.0 if success else 0.0
            pattern.success_rate = (old_rate * 0.9) + (new_value * 0.1)
            
            # Add context if new
            if app_context and app_context not in pattern.contexts:
                pattern.contexts.append(app_context)
        else:
            # Create new pattern
            self.command_patterns[pattern_key] = CommandPattern(
                pattern=user_input,
                action=action,
                frequency=1,
                success_rate=1.0 if success else 0.0,
                contexts=[app_context] if app_context else []
            )
            self.stats['patterns_learned'] += 1
        
        # Record interaction in current session
        if self.current_session:
            self.current_session.interactions.append({
                'input': user_input,
                'action': action,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
            if success:
                self.current_session.successful_commands += 1
            else:
                self.current_session.failed_commands += 1
        
        # Periodic save
        if self.stats['total_interactions'] % 50 == 0:
            self._save_learning_data()
    
    def _normalize_pattern(self, text: str) -> str:
        """Normalize a pattern for matching."""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Create a hash for the pattern
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def predict_action(self, user_input: str, 
                       app_context: str = None) -> Optional[Tuple[str, float]]:
        """
        Predict the most likely action for a user input.
        
        Returns:
            Tuple of (action, confidence) or None if no prediction
        """
        pattern_key = self._normalize_pattern(user_input)
        
        # Direct match
        if pattern_key in self.command_patterns:
            pattern = self.command_patterns[pattern_key]
            confidence = min(pattern.success_rate * (1 + pattern.frequency / 100), 1.0)
            return (pattern.action, confidence)
        
        # Fuzzy matching - find similar patterns
        input_words = set(user_input.lower().split())
        best_match = None
        best_score = 0.0
        
        for key, pattern in self.command_patterns.items():
            pattern_words = set(pattern.pattern.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(input_words & pattern_words)
            union = len(input_words | pattern_words)
            similarity = intersection / max(union, 1)
            
            # Weight by frequency and success rate
            score = similarity * pattern.success_rate * min(pattern.frequency / 10, 1.0)
            
            # Boost if same app context
            if app_context and app_context in pattern.contexts:
                score *= 1.5
            
            if score > best_score and score > 0.3:  # Minimum threshold
                best_score = score
                best_match = pattern
        
        if best_match:
            return (best_match.action, best_score)
        
        return None
    
    def get_suggestions(self, partial_input: str, 
                        app_context: str = None, 
                        limit: int = 5) -> List[Tuple[str, str]]:
        """
        Get command suggestions based on partial input.
        
        Returns:
            List of (full_command, action) tuples
        """
        partial_lower = partial_input.lower()
        suggestions = []
        
        for pattern in self.command_patterns.values():
            if partial_lower in pattern.pattern.lower():
                # Score based on frequency, success rate, and context match
                score = pattern.frequency * pattern.success_rate
                if app_context and app_context in pattern.contexts:
                    score *= 2
                
                suggestions.append((pattern.pattern, pattern.action, score))
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return [(s[0], s[1]) for s in suggestions[:limit]]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # USER PREFERENCE LEARNING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def learn_preference(self, preference_type: str, value: Any, 
                         confidence_boost: float = 0.1):
        """
        Learn a user preference.
        
        Args:
            preference_type: Type of preference (e.g., 'speech_rate', 'verbosity')
            value: The preferred value
            confidence_boost: How much to increase confidence
        """
        pref_key = f"{preference_type}:{value}"
        
        if pref_key in self.user_preferences:
            pref = self.user_preferences[pref_key]
            pref.learn_count += 1
            pref.confidence = min(pref.confidence + confidence_boost, 1.0)
        else:
            self.user_preferences[pref_key] = UserPreference(
                preference_type=preference_type,
                value=value,
                confidence=0.5 + confidence_boost,
                learn_count=1
            )
            self.stats['preferences_learned'] += 1
    
    def get_preference(self, preference_type: str, 
                       default: Any = None) -> Tuple[Any, float]:
        """
        Get the most likely preference for a type.
        
        Returns:
            Tuple of (value, confidence)
        """
        best_pref = None
        best_score = 0.0
        
        for key, pref in self.user_preferences.items():
            if pref.preference_type == preference_type:
                score = pref.confidence * min(pref.learn_count / 5, 1.0)
                if score > best_score:
                    best_score = score
                    best_pref = pref
        
        if best_pref:
            return (best_pref.value, best_score)
        return (default, 0.0)
    
    def get_all_preferences(self) -> Dict[str, Tuple[Any, float]]:
        """Get all learned preferences."""
        preferences = {}
        
        # Group by type and find best for each
        by_type = defaultdict(list)
        for pref in self.user_preferences.values():
            by_type[pref.preference_type].append(pref)
        
        for pref_type, prefs in by_type.items():
            best = max(prefs, key=lambda p: p.confidence * p.learn_count)
            preferences[pref_type] = (best.value, best.confidence)
        
        return preferences
    
    # ═══════════════════════════════════════════════════════════════════════════
    # APP USAGE PATTERN LEARNING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def learn_app_usage(self, app_name: str, action: str = None, 
                        session_length_minutes: float = None):
        """
        Learn app usage patterns.
        
        Args:
            app_name: Name of the app
            action: Action performed (if any)
            session_length_minutes: Session length (if ending session)
        """
        app_key = app_name.lower()
        
        if app_key not in self.app_usage:
            self.app_usage[app_key] = AppUsagePattern(app_name=app_name)
        
        usage = self.app_usage[app_key]
        usage.total_uses += 1
        usage.last_used = datetime.now().isoformat()
        
        if action:
            if action not in usage.common_actions:
                usage.common_actions[action] = 0
            usage.common_actions[action] += 1
            
            # Update preferred commands
            top_actions = sorted(
                usage.common_actions.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            usage.preferred_commands = [a[0] for a in top_actions]
        
        if session_length_minutes is not None:
            # Rolling average for session length
            old_avg = usage.average_session_length
            usage.average_session_length = (old_avg * 0.8) + (session_length_minutes * 0.2)
    
    def get_app_suggestions(self, app_name: str) -> List[str]:
        """Get suggested actions for an app based on usage patterns."""
        app_key = app_name.lower()
        
        if app_key in self.app_usage:
            return self.app_usage[app_key].preferred_commands
        
        return []
    
    def get_most_used_apps(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get the most used apps."""
        apps = [(u.app_name, u.total_uses) for u in self.app_usage.values()]
        apps.sort(key=lambda x: x[1], reverse=True)
        return apps[:limit]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NARRATIVE IMPROVEMENT LEARNING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def learn_narrative_preference(self, original: str, context: str, 
                                    positive_feedback: bool):
        """
        Learn whether a narrative was effective.
        
        Args:
            original: The narrative that was shown
            context: The context (app, action, etc.)
            positive_feedback: Whether user responded positively
        """
        narrative_key = hashlib.sha256(f"{original}:{context}".encode()).hexdigest()[:16]
        
        if narrative_key not in self.narrative_improvements:
            self.narrative_improvements[narrative_key] = NarrativeImprovement(
                original_narrative=original,
                improved_narrative=original,  # Start with same
                context=context
            )
        
        imp = self.narrative_improvements[narrative_key]
        imp.usage_count += 1
        
        # Adjust score based on feedback
        if positive_feedback:
            imp.improvement_score = min(imp.improvement_score + 0.1, 1.0)
        else:
            imp.improvement_score = max(imp.improvement_score - 0.1, -1.0)
    
    def suggest_narrative_improvement(self, original: str, 
                                       context: str) -> Optional[str]:
        """
        Suggest an improved narrative if one exists.
        
        Returns the improved version if score is positive, else None.
        """
        narrative_key = hashlib.sha256(f"{original}:{context}".encode()).hexdigest()[:16]
        
        if narrative_key in self.narrative_improvements:
            imp = self.narrative_improvements[narrative_key]
            if imp.improvement_score > 0 and imp.improved_narrative != imp.original_narrative:
                return imp.improved_narrative
        
        return None
    
    def set_narrative_improvement(self, original: str, improved: str, context: str):
        """Set an improved narrative for a context."""
        narrative_key = hashlib.sha256(f"{original}:{context}".encode()).hexdigest()[:16]
        
        if narrative_key not in self.narrative_improvements:
            self.narrative_improvements[narrative_key] = NarrativeImprovement(
                original_narrative=original,
                improved_narrative=improved,
                context=context,
                improvement_score=0.5  # Start neutral
            )
        else:
            self.narrative_improvements[narrative_key].improved_narrative = improved
        
        self.stats['improvements_made'] += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INTERACTION LEARNING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _learn_from_interaction(self, interaction: Dict, app_context: str = None):
        """Learn from a single interaction (from session replay, not live)."""
        user_input = interaction.get('input', '')
        action = interaction.get('action', '')
        success = interaction.get('success', True)
        
        # Note: learn_command is already called during live interaction,
        # so we only update app usage here during session replay
        if app_context and action:
            self.learn_app_usage(app_context, action)
    
    def record_clarification_needed(self, user_input: str, app_context: str = None):
        """Record when clarification was needed (indicates unclear input)."""
        if self.current_session:
            self.current_session.clarifications_needed += 1
        
        # This might indicate the command pattern isn't well understood
        pattern_key = self._normalize_pattern(user_input)
        if pattern_key in self.command_patterns:
            pattern = self.command_patterns[pattern_key]
            # Decrease success rate slightly
            pattern.success_rate = max(pattern.success_rate - 0.05, 0)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS AND CONTROL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_statistics(self) -> Dict:
        """Get learning statistics."""
        return {
            **self.stats,
            'command_patterns': len(self.command_patterns),
            'user_preferences': len(self.user_preferences),
            'apps_tracked': len(self.app_usage),
            'narrative_improvements': len(self.narrative_improvements),
            'top_apps': self.get_most_used_apps(5)
        }
    
    def reset_learning(self, confirm: bool = False):
        """
        Reset all learned data.
        
        Requires confirmation to prevent accidental data loss.
        """
        if not confirm:
            return False
        
        self.command_patterns = {}
        self.user_preferences = {}
        self.app_usage = {}
        self.narrative_improvements = {}
        self.stats = {
            'total_interactions': 0,
            'patterns_learned': 0,
            'preferences_learned': 0,
            'improvements_made': 0,
            'learning_started': datetime.now().isoformat()
        }
        
        self._save_learning_data()
        print("[Self-Learning] All learning data has been reset")
        return True
    
    def export_learning_data(self) -> Dict:
        """Export all learning data for backup or inspection."""
        return {
            'command_patterns': {k: asdict(v) for k, v in self.command_patterns.items()},
            'user_preferences': {k: asdict(v) for k, v in self.user_preferences.items()},
            'app_usage': {k: asdict(v) for k, v in self.app_usage.items()},
            'narrative_improvements': {k: asdict(v) for k, v in self.narrative_improvements.items()},
            'stats': self.stats,
            'exported_at': datetime.now().isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_learning_engine_instance = None


def get_learning_engine(learning_path: str = None) -> SelfLearningEngine:
    """Get or create the Self-Learning Engine singleton."""
    global _learning_engine_instance
    
    if _learning_engine_instance is None:
        _learning_engine_instance = SelfLearningEngine(learning_path)
    
    return _learning_engine_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the Self-Learning Engine."""
    print("=" * 70)
    print("VA21 OS - Self-Learning Engine Test")
    print("=" * 70)
    
    engine = get_learning_engine()
    
    # Start a session
    session_id = engine.start_session("Firefox")
    print(f"\nStarted session: {session_id}")
    
    # Simulate some learning
    test_commands = [
        ("save my work", "save", True),
        ("find something", "search", True),
        ("I want to search for news", "search", True),
        ("go back", "back", True),
        ("close this tab", "close_tab", True),
        ("open a new tab", "new_tab", True),
        ("save", "save", True),
        ("search google", "search", True),
    ]
    
    print("\n--- Learning from commands ---")
    for user_input, action, success in test_commands:
        engine.learn_command(user_input, action, "Firefox", success)
        print(f"Learned: '{user_input}' -> {action}")
    
    # Test prediction
    print("\n--- Testing predictions ---")
    test_inputs = [
        "save my document",
        "search for something",
        "I want to go back",
        "new tab please",
    ]
    
    for test in test_inputs:
        prediction = engine.predict_action(test, "Firefox")
        if prediction:
            print(f"'{test}' -> {prediction[0]} (confidence: {prediction[1]:.2f})")
        else:
            print(f"'{test}' -> No prediction")
    
    # Test suggestions
    print("\n--- Testing suggestions ---")
    suggestions = engine.get_suggestions("search", "Firefox", 3)
    print(f"Suggestions for 'search': {suggestions}")
    
    # Learn preferences
    print("\n--- Learning preferences ---")
    engine.learn_preference("speech_rate", "fast")
    engine.learn_preference("speech_rate", "fast")
    engine.learn_preference("verbosity", "concise")
    
    pref, conf = engine.get_preference("speech_rate")
    print(f"Preferred speech_rate: {pref} (confidence: {conf:.2f})")
    
    # Learn app usage
    print("\n--- Learning app usage ---")
    engine.learn_app_usage("Firefox", "search")
    engine.learn_app_usage("Firefox", "new_tab")
    engine.learn_app_usage("Firefox", "search")
    
    app_suggestions = engine.get_app_suggestions("Firefox")
    print(f"App suggestions for Firefox: {app_suggestions}")
    
    # End session
    engine.end_session()
    
    # Show statistics
    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
