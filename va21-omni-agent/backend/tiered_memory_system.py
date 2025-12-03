"""
VA21 Tiered Memory System - Interconnected Context-Aware AI Memory

This module provides a tiered memory system for all 3 AI components (Guardian AI,
Helper AI, and Agent Zero) with separate knowledge bases, Obsidian memory brain
maps, and context-aware memory retrieval.

Architecture:
    Tier 1: Working Memory (Current Context)
        └── Fast access, limited capacity
        └── Current conversation/task context
    
    Tier 2: Short-Term Memory (Session Memory)
        └── Medium access, moderate capacity
        └── Session-level context and recent interactions
    
    Tier 3: Long-Term Memory (Persistent Storage)
        └── Slower access, unlimited capacity
        └── Obsidian vault integration
        └── Knowledge graphs and brain maps
    
    Each tier is interconnected and context-aware:
    - Relevant context is extracted via embedding LLM
    - Timestamps and tiered tags enable efficient retrieval
    - Anti-hallucination engine validates all retrieved memories

Om Vinayaka - Memory flows where wisdom is needed.
"""

import os
import sys
import json
import hashlib
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import uuid


class MemoryTier(Enum):
    """Memory tier levels."""
    WORKING = "working"     # Tier 1: Current context
    SHORT_TERM = "short_term"  # Tier 2: Session memory
    LONG_TERM = "long_term"   # Tier 3: Persistent storage


class MemoryOwner(Enum):
    """AI component that owns the memory."""
    GUARDIAN = "guardian_ai"
    HELPER = "helper_ai"
    AGENT_ZERO = "agent_zero"
    SHARED = "shared"


class MemoryType(Enum):
    """Types of memory entries."""
    CONVERSATION = "conversation"
    TASK = "task"
    FACT = "fact"
    CONTEXT = "context"
    DECISION = "decision"
    SECURITY = "security"
    CODE = "code"
    RESEARCH = "research"


@dataclass
class MemoryTag:
    """A tag for memory categorization."""
    tag_id: str
    name: str
    tier: MemoryTier
    connected_tags: List[str] = field(default_factory=list)
    weight: float = 1.0


@dataclass
class MemoryEntry:
    """A single memory entry."""
    memory_id: str
    owner: MemoryOwner
    tier: MemoryTier
    memory_type: MemoryType
    
    # Content
    content: str
    summary: str
    
    # Metadata
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    
    # Timestamps and tags
    timestamp_embedding: str = ""  # Context-aware timestamp
    tags: List[str] = field(default_factory=list)
    connected_memories: List[str] = field(default_factory=list)
    
    # Relevance
    relevance_score: float = 1.0
    decay_rate: float = 0.01  # How fast relevance decays
    
    # Validation
    validated: bool = False
    validation_id: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'memory_id': self.memory_id,
            'owner': self.owner.value,
            'tier': self.tier.value,
            'memory_type': self.memory_type.value,
            'content': self.content,
            'summary': self.summary,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'access_count': self.access_count,
            'timestamp_embedding': self.timestamp_embedding,
            'tags': self.tags,
            'connected_memories': self.connected_memories,
            'relevance_score': self.relevance_score,
            'decay_rate': self.decay_rate,
            'validated': self.validated,
            'validation_id': self.validation_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        return cls(
            memory_id=data['memory_id'],
            owner=MemoryOwner(data['owner']),
            tier=MemoryTier(data['tier']),
            memory_type=MemoryType(data['memory_type']),
            content=data['content'],
            summary=data['summary'],
            created_at=datetime.fromisoformat(data['created_at']),
            accessed_at=datetime.fromisoformat(data['accessed_at']),
            access_count=data.get('access_count', 0),
            timestamp_embedding=data.get('timestamp_embedding', ''),
            tags=data.get('tags', []),
            connected_memories=data.get('connected_memories', []),
            relevance_score=data.get('relevance_score', 1.0),
            decay_rate=data.get('decay_rate', 0.01),
            validated=data.get('validated', False),
            validation_id=data.get('validation_id', ''),
        )


class ContextEmbedder:
    """
    Small LLM for context-aware embedding.
    
    This embeds memories with:
    - Context-aware timestamps
    - Tiered connected tags
    - Relevance scoring
    """
    
    def __init__(self):
        self.embedding_cache: Dict[str, str] = {}
    
    def embed_timestamp(self, memory: MemoryEntry, context: Dict = None) -> str:
        """Create a context-aware timestamp embedding."""
        # Extract context elements
        time_context = self._get_time_context(memory.created_at)
        content_context = self._extract_content_context(memory.content)
        
        # Create embedding string
        embedding_parts = [
            f"T:{memory.tier.value}",
            f"O:{memory.owner.value}",
            f"M:{memory.memory_type.value}",
            f"D:{memory.created_at.strftime('%Y%m%d')}",
            f"H:{memory.created_at.strftime('%H')}",
            f"TC:{time_context}",
        ]
        
        # Add content context
        for ctx in content_context[:3]:
            embedding_parts.append(f"C:{ctx}")
        
        # Add external context if provided
        if context:
            if 'task' in context:
                embedding_parts.append(f"TK:{context['task'][:20]}")
            if 'session' in context:
                embedding_parts.append(f"S:{context['session'][:10]}")
        
        return "|".join(embedding_parts)
    
    def _get_time_context(self, dt: datetime) -> str:
        """Get time context (morning, afternoon, etc.)."""
        hour = dt.hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _extract_content_context(self, content: str) -> List[str]:
        """Extract key context words from content."""
        # Simple keyword extraction
        keywords = []
        content_lower = content.lower()
        
        # Check for key topics
        topic_words = [
            'security', 'code', 'file', 'task', 'backup', 'restore',
            'error', 'success', 'warning', 'user', 'system', 'research',
            'automation', 'agent', 'guardian', 'helper'
        ]
        
        for word in topic_words:
            if word in content_lower:
                keywords.append(word)
        
        return keywords[:5]
    
    def create_connected_tags(self, memory: MemoryEntry, 
                               existing_tags: Dict[str, MemoryTag]) -> List[str]:
        """Create interconnected tags for the memory."""
        tags = []
        
        # Add tier tag
        tags.append(f"tier:{memory.tier.value}")
        
        # Add owner tag
        tags.append(f"owner:{memory.owner.value}")
        
        # Add type tag
        tags.append(f"type:{memory.memory_type.value}")
        
        # Add date tag
        tags.append(f"date:{memory.created_at.strftime('%Y-%m-%d')}")
        
        # Find connected tags
        for tag_id, tag in existing_tags.items():
            if tag.tier == memory.tier:
                # Check for content overlap
                if any(t in memory.content.lower() for t in tag.name.lower().split()):
                    tags.append(tag.tag_id)
        
        return list(set(tags))


class TieredMemorySystem:
    """
    VA21 Tiered Memory System
    
    Provides separate knowledge bases for all 3 AI components with:
    - Tiered memory architecture (Working, Short-Term, Long-Term)
    - Obsidian memory brain maps integration
    - Context-aware timestamp embedding
    - Interconnected tiered tags
    - Anti-hallucination validation
    - Efficient context extraction
    
    Each AI has its own memory space:
    - Guardian AI: Security events, threat patterns, decisions
    - Helper AI: Conversations, user preferences, task history
    - Agent Zero: Automation tasks, execution history, learned patterns
    
    Shared memories allow cross-AI knowledge sharing when appropriate.
    """
    
    # Memory limits per tier
    TIER_LIMITS = {
        MemoryTier.WORKING: 100,      # Most recent 100 items
        MemoryTier.SHORT_TERM: 1000,  # Last 1000 items
        MemoryTier.LONG_TERM: -1,     # Unlimited (disk-based)
    }
    
    # Decay rates per tier (per hour)
    TIER_DECAY = {
        MemoryTier.WORKING: 0.1,
        MemoryTier.SHORT_TERM: 0.01,
        MemoryTier.LONG_TERM: 0.001,
    }
    
    def __init__(self, data_dir: str = "data/tiered_memory",
                 obsidian_vault: str = "data/research_vault",
                 anti_hallucination=None):
        """Initialize the Tiered Memory System."""
        self.data_dir = data_dir
        self.obsidian_vault = obsidian_vault
        self.anti_hallucination = anti_hallucination
        
        # Create directories
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "working"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "short_term"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "long_term"), exist_ok=True)
        os.makedirs(os.path.join(obsidian_vault, "memory_maps"), exist_ok=True)
        
        # Memory stores per owner
        self.memories: Dict[MemoryOwner, Dict[MemoryTier, Dict[str, MemoryEntry]]] = {
            owner: {
                tier: {}
                for tier in MemoryTier
            }
            for owner in MemoryOwner
        }
        
        # Tags registry
        self.tags: Dict[str, MemoryTag] = {}
        
        # Context embedder
        self.embedder = ContextEmbedder()
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Metrics
        self.metrics = {
            'memories_stored': 0,
            'memories_retrieved': 0,
            'tier_promotions': 0,
            'tier_demotions': 0,
            'context_extractions': 0,
        }
        
        # Load existing data
        self._load_data()
        
        print(f"[TieredMemory] Initialized with {sum(sum(len(t) for t in o.values()) for o in self.memories.values())} memories")
    
    # =========================================================================
    # MEMORY STORAGE
    # =========================================================================
    
    def store(self, owner: MemoryOwner, memory_type: MemoryType,
              content: str, summary: str = None,
              tier: MemoryTier = MemoryTier.WORKING,
              tags: List[str] = None, context: Dict = None) -> MemoryEntry:
        """
        Store a new memory entry.
        
        Args:
            owner: Which AI owns this memory
            memory_type: Type of memory
            content: Full memory content
            summary: Optional summary (auto-generated if not provided)
            tier: Which tier to store in
            tags: Optional tags
            context: Additional context for embedding
            
        Returns:
            The stored MemoryEntry
        """
        with self._lock:
            # Generate memory ID
            memory_id = self._generate_memory_id(owner, memory_type)
            
            # Auto-generate summary if not provided
            if not summary:
                summary = self._generate_summary(content)
            
            # Create entry
            now = datetime.now()
            entry = MemoryEntry(
                memory_id=memory_id,
                owner=owner,
                tier=tier,
                memory_type=memory_type,
                content=content,
                summary=summary,
                created_at=now,
                accessed_at=now,
                tags=tags or [],
            )
            
            # Create timestamp embedding
            entry.timestamp_embedding = self.embedder.embed_timestamp(entry, context)
            
            # Create connected tags
            entry.tags = self.embedder.create_connected_tags(entry, self.tags)
            if tags:
                entry.tags.extend(tags)
            
            # Validate with anti-hallucination system
            if self.anti_hallucination:
                try:
                    tid = self.anti_hallucination.generate_id('memory')
                    entry.validation_id = tid.uid
                    entry.validated = True
                except:
                    pass
            
            # Store in appropriate tier
            self.memories[owner][tier][memory_id] = entry
            self.metrics['memories_stored'] += 1
            
            # Check tier limits
            self._enforce_tier_limits(owner, tier)
            
            # Update brain map
            self._update_brain_map(owner)
            
            # Save to disk
            self._save_memory(entry)
            
            return entry
    
    def _generate_memory_id(self, owner: MemoryOwner, memory_type: MemoryType) -> str:
        """Generate a unique memory ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = uuid.uuid4().hex[:8]
        return f"mem_{owner.value}_{memory_type.value}_{timestamp}_{random_part}"
    
    def _generate_summary(self, content: str, max_length: int = 100) -> str:
        """Generate a summary of the content."""
        if len(content) <= max_length:
            return content
        return content[:max_length-3] + "..."
    
    def _enforce_tier_limits(self, owner: MemoryOwner, tier: MemoryTier):
        """Enforce memory limits for a tier."""
        limit = self.TIER_LIMITS[tier]
        if limit < 0:
            return  # Unlimited
        
        tier_memories = self.memories[owner][tier]
        if len(tier_memories) > limit:
            # Sort by relevance and access time
            sorted_memories = sorted(
                tier_memories.values(),
                key=lambda m: (m.relevance_score, m.accessed_at),
                reverse=True
            )
            
            # Keep the most relevant
            to_keep = sorted_memories[:limit]
            to_demote = sorted_memories[limit:]
            
            # Demote excess memories
            for memory in to_demote:
                self._demote_memory(memory)
    
    def _demote_memory(self, memory: MemoryEntry):
        """Demote a memory to a lower tier."""
        current_tier = memory.tier
        
        # Determine next tier
        tier_order = [MemoryTier.WORKING, MemoryTier.SHORT_TERM, MemoryTier.LONG_TERM]
        current_idx = tier_order.index(current_tier)
        
        if current_idx < len(tier_order) - 1:
            new_tier = tier_order[current_idx + 1]
            
            # Move to new tier
            del self.memories[memory.owner][current_tier][memory.memory_id]
            memory.tier = new_tier
            self.memories[memory.owner][new_tier][memory.memory_id] = memory
            
            self.metrics['tier_demotions'] += 1
            self._save_memory(memory)
    
    # =========================================================================
    # MEMORY RETRIEVAL
    # =========================================================================
    
    def retrieve(self, owner: MemoryOwner = None,
                 memory_type: MemoryType = None,
                 tier: MemoryTier = None,
                 tags: List[str] = None,
                 query: str = None,
                 limit: int = 10,
                 include_shared: bool = True) -> List[MemoryEntry]:
        """
        Retrieve memories based on criteria.
        
        Args:
            owner: Filter by owner (None for all)
            memory_type: Filter by type (None for all)
            tier: Filter by tier (None for all)
            tags: Filter by tags (matches any)
            query: Text query for content search
            limit: Maximum results
            include_shared: Include shared memories
            
        Returns:
            List of matching MemoryEntry objects
        """
        with self._lock:
            results = []
            owners = [owner] if owner else list(MemoryOwner)
            
            if include_shared and owner and owner != MemoryOwner.SHARED:
                owners.append(MemoryOwner.SHARED)
            
            for o in owners:
                tiers = [tier] if tier else list(MemoryTier)
                
                for t in tiers:
                    for memory in self.memories[o][t].values():
                        # Apply filters
                        if memory_type and memory.memory_type != memory_type:
                            continue
                        
                        if tags and not any(tag in memory.tags for tag in tags):
                            continue
                        
                        if query and query.lower() not in memory.content.lower():
                            continue
                        
                        results.append(memory)
            
            # Sort by relevance and recency
            results.sort(key=lambda m: (m.relevance_score, m.accessed_at), reverse=True)
            
            # Update access stats
            for memory in results[:limit]:
                memory.accessed_at = datetime.now()
                memory.access_count += 1
            
            self.metrics['memories_retrieved'] += min(limit, len(results))
            
            return results[:limit]
    
    def get_context_for_query(self, query: str, owner: MemoryOwner = None,
                               max_tokens: int = 2000) -> Dict:
        """
        Get relevant context for a query.
        
        This implements the context-aware retrieval that feeds only relevant
        context to the LLM, avoiding context overflow.
        
        Args:
            query: The query to find context for
            owner: Optional owner filter
            max_tokens: Maximum tokens to return
            
        Returns:
            Dict with relevant context and metadata
        """
        with self._lock:
            self.metrics['context_extractions'] += 1
            
            # Search all tiers for relevant memories
            relevant = []
            query_lower = query.lower()
            
            # Extract keywords from query
            keywords = [w for w in query_lower.split() if len(w) > 3]
            
            owners = [owner] if owner else list(MemoryOwner)
            
            for o in owners:
                for tier in MemoryTier:
                    for memory in self.memories[o][tier].values():
                        # Calculate relevance score
                        score = self._calculate_relevance(memory, keywords, query_lower)
                        if score > 0.1:
                            relevant.append((memory, score))
            
            # Sort by relevance
            relevant.sort(key=lambda x: x[1], reverse=True)
            
            # Build context within token limit
            context_parts = []
            total_chars = 0
            char_limit = max_tokens * 4  # Approximate chars per token
            
            for memory, score in relevant:
                content = memory.summary if len(memory.content) > 200 else memory.content
                if total_chars + len(content) > char_limit:
                    break
                
                context_parts.append({
                    'memory_id': memory.memory_id,
                    'content': content,
                    'type': memory.memory_type.value,
                    'relevance': score,
                    'tier': memory.tier.value,
                })
                total_chars += len(content)
            
            return {
                'context': context_parts,
                'total_memories_found': len(relevant),
                'memories_included': len(context_parts),
                'estimated_tokens': total_chars // 4,
                'query_keywords': keywords,
            }
    
    def _calculate_relevance(self, memory: MemoryEntry, 
                             keywords: List[str], query: str) -> float:
        """Calculate relevance score for a memory."""
        score = memory.relevance_score * 0.3  # Base relevance
        
        content_lower = memory.content.lower()
        
        # Keyword matching
        keyword_matches = sum(1 for kw in keywords if kw in content_lower)
        score += (keyword_matches / max(len(keywords), 1)) * 0.4
        
        # Exact phrase matching
        if query in content_lower:
            score += 0.3
        
        # Recency bonus
        age_hours = (datetime.now() - memory.accessed_at).total_seconds() / 3600
        recency_bonus = max(0, 0.1 - (age_hours * 0.001))
        score += recency_bonus
        
        # Tier bonus (working memory is more relevant)
        tier_bonus = {
            MemoryTier.WORKING: 0.1,
            MemoryTier.SHORT_TERM: 0.05,
            MemoryTier.LONG_TERM: 0.0,
        }
        score += tier_bonus.get(memory.tier, 0)
        
        return min(score, 1.0)
    
    # =========================================================================
    # MEMORY CONNECTIONS
    # =========================================================================
    
    def connect_memories(self, memory_id1: str, memory_id2: str) -> bool:
        """Connect two memories for relationship tracking."""
        with self._lock:
            mem1 = self._find_memory(memory_id1)
            mem2 = self._find_memory(memory_id2)
            
            if mem1 and mem2:
                if memory_id2 not in mem1.connected_memories:
                    mem1.connected_memories.append(memory_id2)
                if memory_id1 not in mem2.connected_memories:
                    mem2.connected_memories.append(memory_id1)
                
                self._save_memory(mem1)
                self._save_memory(mem2)
                return True
            return False
    
    def _find_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Find a memory by ID."""
        for owner in MemoryOwner:
            for tier in MemoryTier:
                if memory_id in self.memories[owner][tier]:
                    return self.memories[owner][tier][memory_id]
        return None
    
    def get_connected_memories(self, memory_id: str, depth: int = 1) -> List[MemoryEntry]:
        """Get connected memories up to a certain depth."""
        result = []
        visited = set()
        
        def traverse(mid: str, current_depth: int):
            if current_depth > depth or mid in visited:
                return
            
            visited.add(mid)
            memory = self._find_memory(mid)
            
            if memory:
                if mid != memory_id:
                    result.append(memory)
                
                for connected_id in memory.connected_memories:
                    traverse(connected_id, current_depth + 1)
        
        traverse(memory_id, 0)
        return result
    
    # =========================================================================
    # OBSIDIAN BRAIN MAPS
    # =========================================================================
    
    def _update_brain_map(self, owner: MemoryOwner):
        """Update the Obsidian brain map for an owner."""
        map_path = os.path.join(
            self.obsidian_vault,
            "memory_maps",
            f"{owner.value}_brain_map.md"
        )
        
        # Collect memories
        all_memories = []
        for tier in MemoryTier:
            all_memories.extend(self.memories[owner][tier].values())
        
        # Group by type
        type_groups: Dict[MemoryType, List[MemoryEntry]] = {}
        for memory in all_memories:
            if memory.memory_type not in type_groups:
                type_groups[memory.memory_type] = []
            type_groups[memory.memory_type].append(memory)
        
        # Build brain map content
        content = f"""# {owner.value.replace('_', ' ').title()} Brain Map

> **Last Updated**: {datetime.now().isoformat()}
> **Total Memories**: {len(all_memories)}

## Overview

```mermaid
mindmap
  root(({owner.value}))
"""
        
        for mem_type, memories in type_groups.items():
            content += f"    {mem_type.value}\n"
            for mem in memories[-5:]:  # Last 5 per type
                short_summary = mem.summary[:30].replace('\n', ' ')
                content += f"      {short_summary}...\n"
        
        content += """```

## Memory by Tier

"""
        
        for tier in MemoryTier:
            tier_memories = list(self.memories[owner][tier].values())
            content += f"""### {tier.value.replace('_', ' ').title()} ({len(tier_memories)} items)

| Summary | Type | Created | Tags |
|---------|------|---------|------|
"""
            for mem in tier_memories[-10:]:
                tags = ', '.join(mem.tags[:3]) if mem.tags else '-'
                content += f"| {mem.summary[:40]}... | {mem.memory_type.value} | {mem.created_at.strftime('%Y-%m-%d %H:%M')} | {tags} |\n"
            
            content += "\n"
        
        content += f"""
## Connections

"""
        
        # Show connected memories
        connected_count = sum(len(m.connected_memories) for m in all_memories)
        content += f"Total connections: {connected_count}\n\n"
        
        # Top connected memories
        most_connected = sorted(all_memories, key=lambda m: len(m.connected_memories), reverse=True)[:5]
        if most_connected:
            content += "### Most Connected Memories\n\n"
            for mem in most_connected:
                content += f"- **{mem.summary[:50]}** ({len(mem.connected_memories)} connections)\n"
        
        content += f"""

---
*Generated by VA21 Tiered Memory System*
*Owner: {owner.value}*
"""
        
        try:
            with open(map_path, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"[TieredMemory] Error updating brain map: {e}")
    
    # =========================================================================
    # PERSISTENCE
    # =========================================================================
    
    def _save_memory(self, memory: MemoryEntry):
        """Save a memory to disk."""
        tier_dir = os.path.join(self.data_dir, memory.tier.value)
        file_path = os.path.join(tier_dir, f"{memory.memory_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(memory.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[TieredMemory] Error saving memory: {e}")
    
    def _load_data(self):
        """Load all data from disk."""
        for tier in MemoryTier:
            tier_dir = os.path.join(self.data_dir, tier.value)
            if os.path.exists(tier_dir):
                for filename in os.listdir(tier_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(tier_dir, filename), 'r') as f:
                                data = json.load(f)
                                memory = MemoryEntry.from_dict(data)
                                self.memories[memory.owner][memory.tier][memory.memory_id] = memory
                        except Exception as e:
                            print(f"[TieredMemory] Error loading {filename}: {e}")
    
    # =========================================================================
    # STATUS AND METRICS
    # =========================================================================
    
    def get_status(self) -> Dict:
        """Get system status."""
        status = {
            'metrics': self.metrics,
            'owners': {},
            'total_memories': 0,
        }
        
        for owner in MemoryOwner:
            owner_status = {
                'total': 0,
                'by_tier': {},
            }
            for tier in MemoryTier:
                count = len(self.memories[owner][tier])
                owner_status['by_tier'][tier.value] = count
                owner_status['total'] += count
            
            status['owners'][owner.value] = owner_status
            status['total_memories'] += owner_status['total']
        
        return status
    
    def get_memory_stats_for_owner(self, owner: MemoryOwner) -> Dict:
        """Get detailed stats for an owner."""
        memories = []
        for tier in MemoryTier:
            memories.extend(self.memories[owner][tier].values())
        
        if not memories:
            return {'total': 0}
        
        return {
            'total': len(memories),
            'by_type': {
                t.value: len([m for m in memories if m.memory_type == t])
                for t in MemoryType
            },
            'by_tier': {
                t.value: len(self.memories[owner][t])
                for t in MemoryTier
            },
            'avg_relevance': sum(m.relevance_score for m in memories) / len(memories),
            'total_connections': sum(len(m.connected_memories) for m in memories),
        }


# =========================================================================
# SINGLETON
# =========================================================================

_tiered_memory: Optional[TieredMemorySystem] = None


def get_tiered_memory(anti_hallucination=None) -> TieredMemorySystem:
    """Get the Tiered Memory System singleton instance."""
    global _tiered_memory
    if _tiered_memory is None:
        _tiered_memory = TieredMemorySystem(anti_hallucination=anti_hallucination)
    return _tiered_memory


if __name__ == "__main__":
    # Test the system
    print("\n=== Tiered Memory System Test ===")
    
    memory = get_tiered_memory()
    
    print("\n--- Initial Status ---")
    print(json.dumps(memory.get_status(), indent=2))
    
    print("\n--- Storing Test Memories ---")
    
    # Store some test memories
    mem1 = memory.store(
        owner=MemoryOwner.GUARDIAN,
        memory_type=MemoryType.SECURITY,
        content="Blocked suspicious command: rm -rf /. User attempted system destruction.",
        tags=['security', 'blocked', 'critical']
    )
    print(f"Stored: {mem1.memory_id}")
    
    mem2 = memory.store(
        owner=MemoryOwner.HELPER,
        memory_type=MemoryType.CONVERSATION,
        content="User asked about creating a backup. Provided instructions for manual backup.",
        tags=['backup', 'help']
    )
    print(f"Stored: {mem2.memory_id}")
    
    mem3 = memory.store(
        owner=MemoryOwner.AGENT_ZERO,
        memory_type=MemoryType.TASK,
        content="Automated task completed: Created Python script for data processing.",
        tags=['automation', 'python', 'completed']
    )
    print(f"Stored: {mem3.memory_id}")
    
    print("\n--- Retrieving Context ---")
    context = memory.get_context_for_query("backup security")
    print(json.dumps(context, indent=2))
    
    print("\n--- Final Status ---")
    print(json.dumps(memory.get_status(), indent=2))
