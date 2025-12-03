#!/usr/bin/env python3
"""
VA21 OS - Context-Aware Summary Engine
========================================

The Summary Engine prevents AI context overflow and hallucinations by:
- Monitoring context size and automatically summarizing when needed
- Using a custom context-aware algorithm for intelligent summarization
- Preserving full knowledge in the knowledge base while sending summaries to AI
- Managing context for Helper AI, Accessibility AI, and Orchestration AI

This ensures AI systems don't get overloaded and maintain accuracy.

Architecture:
- Context Monitor: Tracks current context size vs limits
- Summarizer: Compresses context while preserving meaning
- Knowledge Preserver: Keeps full data in Obsidian vault
- Priority Ranker: Decides what's most important to keep

Algorithm:
1. Monitor context token count
2. When approaching limit, identify low-priority content
3. Summarize low-priority content using extractive + abstractive methods
4. Preserve full content in knowledge base
5. Send summarized context to AI
6. Maintain conversation coherence

License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav

Om Vinayaka - May obstacles be removed and clarity prevail.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Token limits for different AI systems
AI_CONTEXT_LIMITS = {
    'helper_ai': 8000,          # Helper AI context limit (tokens)
    'accessibility_ai': 8000,   # Om Vinayaka Accessibility AI
    'orchestration_ai': 16000,  # Orchestration AI (larger context)
    'guardian_ai': 4000,        # Guardian AI (kernel-level, smaller)
    'default': 8000,
}

# When to start summarizing (percentage of limit)
SUMMARIZE_THRESHOLD = 0.75  # Start summarizing at 75% capacity

# Average characters per token (approximation)
CHARS_PER_TOKEN = 4

# Summary compression ratios
COMPRESSION_RATIOS = {
    'aggressive': 0.2,   # Keep 20% - for very long content
    'moderate': 0.4,     # Keep 40% - default
    'light': 0.6,        # Keep 60% - for important content
    'minimal': 0.8,      # Keep 80% - for critical content
}

# Priority levels for content
PRIORITY_LEVELS = {
    'critical': 5,    # Never summarize (user intent, current action)
    'high': 4,        # Minimal summarization (recent context)
    'medium': 3,      # Moderate summarization (background info)
    'low': 2,         # Aggressive summarization (old history)
    'archive': 1,     # Can be removed from context entirely
}

DEFAULT_KNOWLEDGE_BASE_PATH = os.path.expanduser("~/.va21/accessibility_knowledge_base")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContextItem:
    """An item in the AI context."""
    item_id: str
    content: str
    item_type: str  # 'user_input', 'ai_response', 'system', 'knowledge'
    priority: int
    timestamp: str
    token_count: int
    metadata: Dict = field(default_factory=dict)
    is_summarized: bool = False
    original_content: Optional[str] = None


@dataclass
class SummaryResult:
    """Result of a summarization operation."""
    original_tokens: int
    summarized_tokens: int
    compression_ratio: float
    summary: str
    preserved_in_kb: bool
    kb_reference: Optional[str] = None


@dataclass
class ContextState:
    """Current state of the context."""
    total_tokens: int
    limit: int
    usage_percent: float
    items_count: int
    needs_summarization: bool
    items_by_priority: Dict[int, int]


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT-AWARE SUMMARIZATION ALGORITHM
# ═══════════════════════════════════════════════════════════════════════════════

class ContextAwareSummarizer:
    """
    Custom context-aware summarization algorithm.
    
    The algorithm:
    1. Identifies key sentences using TF-IDF-like scoring
    2. Preserves named entities and important terms
    3. Maintains conversation flow and coherence
    4. Uses extractive summarization (no hallucination risk)
    5. Falls back to truncation if needed
    """
    
    def __init__(self):
        # Important words to preserve
        self.preserve_patterns = [
            r'\b(?:user|you|I|we)\b',  # Personal pronouns
            r'\b(?:save|open|close|search|help|create|delete)\b',  # Actions
            r'\b(?:error|warning|success|failed)\b',  # Status words
            r'\b(?:please|want|need|would like)\b',  # Intent words
        ]
        
        # Stop words to ignore in scoring
        self.stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 's', 't', 'just', 'don', 'now',
        }
    
    def summarize(self, text: str, target_ratio: float = 0.4) -> str:
        """
        Summarize text to target ratio while preserving meaning.
        
        Args:
            text: Text to summarize
            target_ratio: Target size as ratio of original (0.4 = 40%)
            
        Returns:
            Summarized text
        """
        if not text or len(text) < 100:
            return text
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 2:
            return text
        
        # Score sentences
        scored_sentences = self._score_sentences(sentences)
        
        # Calculate how many sentences to keep
        target_count = max(1, int(len(sentences) * target_ratio))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = scored_sentences[:target_count]
        
        # Re-sort by original order to maintain coherence
        top_sentences.sort(key=lambda x: x[2])
        
        # Join selected sentences
        summary = ' '.join([s[0] for s in top_sentences])
        
        return summary
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences: List[str]) -> List[Tuple[str, float, int]]:
        """
        Score sentences for importance.
        
        Returns list of (sentence, score, original_index)
        """
        # Build word frequency (TF)
        word_freq = defaultdict(int)
        for sentence in sentences:
            words = self._tokenize(sentence)
            for word in words:
                if word not in self.stop_words:
                    word_freq[word] += 1
        
        # Score each sentence
        scored = []
        for idx, sentence in enumerate(sentences):
            score = self._calculate_sentence_score(sentence, word_freq, idx, len(sentences))
            scored.append((sentence, score, idx))
        
        return scored
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def _calculate_sentence_score(self, sentence: str, word_freq: Dict[str, int],
                                   position: int, total_sentences: int) -> float:
        """Calculate importance score for a sentence."""
        score = 0.0
        words = self._tokenize(sentence)
        
        if not words:
            return 0.0
        
        # Word frequency score
        freq_score = sum(word_freq.get(w, 0) for w in words if w not in self.stop_words)
        score += freq_score / len(words)
        
        # Position score (first and last sentences more important)
        if position == 0:
            score *= 1.5  # First sentence bonus
        elif position == total_sentences - 1:
            score *= 1.3  # Last sentence bonus
        elif position < total_sentences * 0.2:
            score *= 1.2  # Early sentences bonus
        
        # Length score (prefer medium-length sentences)
        if 10 <= len(words) <= 30:
            score *= 1.1
        
        # Preserve pattern bonus
        for pattern in self.preserve_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                score *= 1.3
                break
        
        return score
    
    def create_context_summary(self, items: List[ContextItem], 
                                target_tokens: int) -> str:
        """
        Create a coherent summary from multiple context items.
        
        Args:
            items: List of context items to summarize
            target_tokens: Target token count for summary
            
        Returns:
            Coherent summary string
        """
        if not items:
            return ""
        
        # Sort by timestamp
        sorted_items = sorted(items, key=lambda x: x.timestamp)
        
        # Group by type for structured summary
        by_type = defaultdict(list)
        for item in sorted_items:
            by_type[item.item_type].append(item.content)
        
        # Build structured summary
        parts = []
        
        # Recent conversation
        if 'user_input' in by_type or 'ai_response' in by_type:
            conv_text = " ".join(
                by_type.get('user_input', [])[-3:] + 
                by_type.get('ai_response', [])[-3:]
            )
            if conv_text:
                conv_summary = self.summarize(conv_text, 0.5)
                parts.append(f"Recent: {conv_summary}")
        
        # System context
        if 'system' in by_type:
            sys_text = " ".join(by_type['system'][-2:])
            parts.append(f"Context: {sys_text}")
        
        # Knowledge
        if 'knowledge' in by_type:
            know_text = " ".join(by_type['knowledge'])
            know_summary = self.summarize(know_text, 0.3)
            if know_summary:
                parts.append(f"Knowledge: {know_summary}")
        
        summary = " | ".join(parts)
        
        # Ensure we don't exceed target
        current_tokens = len(summary) // CHARS_PER_TOKEN
        if current_tokens > target_tokens:
            # Truncate with ellipsis
            target_chars = target_tokens * CHARS_PER_TOKEN
            summary = summary[:target_chars - 3] + "..."
        
        return summary


# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class SummaryEngine:
    """
    Context-Aware Summary Engine for VA21 AI Systems.
    
    Prevents AI context overflow and hallucinations by:
    1. Monitoring context size vs limits
    2. Automatically summarizing when approaching limits
    3. Preserving full content in knowledge base
    4. Sending optimized summaries to AI
    5. Maintaining conversation coherence
    
    Used by:
    - Helper AI
    - Om Vinayaka Accessibility AI
    - Orchestration AI
    
    License: Om Vinayaka Prayaga Vaibhav Inventions License
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, knowledge_base_path: str = None):
        self.knowledge_base_path = knowledge_base_path or DEFAULT_KNOWLEDGE_BASE_PATH
        self.summaries_path = os.path.join(self.knowledge_base_path, "summaries")
        os.makedirs(self.summaries_path, exist_ok=True)
        
        # Initialize summarizer
        self.summarizer = ContextAwareSummarizer()
        
        # Context tracking per AI system
        self.contexts: Dict[str, List[ContextItem]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            'summaries_created': 0,
            'tokens_saved': 0,
            'contexts_managed': 0,
            'hallucinations_prevented': 0,  # Estimated
        }
        
        print(f"[SummaryEngine] Initialized v{self.VERSION}")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        if not text:
            return 0
        return max(1, len(text) // CHARS_PER_TOKEN)
    
    def add_to_context(self, ai_system: str, content: str, 
                       item_type: str = 'user_input',
                       priority: int = PRIORITY_LEVELS['medium'],
                       metadata: Dict = None) -> ContextItem:
        """
        Add content to an AI system's context.
        
        Args:
            ai_system: Which AI system ('helper_ai', 'accessibility_ai', etc.)
            content: The content to add
            item_type: Type of content
            priority: Priority level (1-5)
            metadata: Additional metadata
            
        Returns:
            The created ContextItem
        """
        item_id = hashlib.sha256(
            f"{ai_system}:{content}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        item = ContextItem(
            item_id=item_id,
            content=content,
            item_type=item_type,
            priority=priority,
            timestamp=datetime.now().isoformat(),
            token_count=self.estimate_tokens(content),
            metadata=metadata or {}
        )
        
        self.contexts[ai_system].append(item)
        
        # Check if we need to summarize
        state = self.get_context_state(ai_system)
        if state.needs_summarization:
            self._auto_summarize(ai_system)
        
        return item
    
    def get_context_state(self, ai_system: str) -> ContextState:
        """Get the current state of an AI system's context."""
        items = self.contexts.get(ai_system, [])
        limit = AI_CONTEXT_LIMITS.get(ai_system, AI_CONTEXT_LIMITS['default'])
        
        total_tokens = sum(item.token_count for item in items)
        usage_percent = total_tokens / limit if limit > 0 else 0
        
        # Count by priority
        items_by_priority = defaultdict(int)
        for item in items:
            items_by_priority[item.priority] += 1
        
        return ContextState(
            total_tokens=total_tokens,
            limit=limit,
            usage_percent=usage_percent,
            items_count=len(items),
            needs_summarization=usage_percent >= SUMMARIZE_THRESHOLD,
            items_by_priority=dict(items_by_priority)
        )
    
    def _auto_summarize(self, ai_system: str):
        """Automatically summarize context when approaching limits."""
        items = self.contexts.get(ai_system, [])
        if not items:
            return
        
        limit = AI_CONTEXT_LIMITS.get(ai_system, AI_CONTEXT_LIMITS['default'])
        target_tokens = int(limit * 0.5)  # Target 50% usage after summarization
        
        # Sort items by priority and timestamp
        items.sort(key=lambda x: (x.priority, x.timestamp), reverse=True)
        
        # Identify items to keep as-is (critical and high priority)
        keep_items = []
        summarize_items = []
        
        current_tokens = 0
        for item in items:
            if item.priority >= PRIORITY_LEVELS['high']:
                keep_items.append(item)
                current_tokens += item.token_count
            else:
                summarize_items.append(item)
        
        if not summarize_items:
            return  # Nothing to summarize
        
        # Calculate how much space we have for summarized content
        remaining_tokens = target_tokens - current_tokens
        
        if remaining_tokens <= 0:
            # Even critical items exceed limit, need to summarize some
            remaining_tokens = int(limit * 0.3)
        
        # Summarize low-priority items
        result = self._summarize_items(summarize_items, remaining_tokens, ai_system)
        
        if result:
            # Create a new summarized item
            summary_item = ContextItem(
                item_id=f"summary_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                content=result.summary,
                item_type='summary',
                priority=PRIORITY_LEVELS['medium'],
                timestamp=datetime.now().isoformat(),
                token_count=result.summarized_tokens,
                is_summarized=True,
                metadata={'kb_reference': result.kb_reference}
            )
            
            # Replace context with keep_items + summary
            self.contexts[ai_system] = keep_items + [summary_item]
            
            # Update stats
            self.stats['summaries_created'] += 1
            self.stats['tokens_saved'] += result.original_tokens - result.summarized_tokens
            self.stats['hallucinations_prevented'] += 1  # Estimate
            
            print(f"[SummaryEngine] Summarized {ai_system} context: "
                  f"{result.original_tokens} → {result.summarized_tokens} tokens "
                  f"({result.compression_ratio:.1%} compression)")
    
    def _summarize_items(self, items: List[ContextItem], 
                         target_tokens: int, 
                         ai_system: str) -> Optional[SummaryResult]:
        """Summarize a list of context items."""
        if not items:
            return None
        
        original_tokens = sum(item.token_count for item in items)
        
        # Calculate compression ratio needed
        if original_tokens <= target_tokens:
            # No compression needed
            combined = " ".join(item.content for item in items)
            return SummaryResult(
                original_tokens=original_tokens,
                summarized_tokens=original_tokens,
                compression_ratio=1.0,
                summary=combined,
                preserved_in_kb=False
            )
        
        target_ratio = target_tokens / original_tokens
        
        # Save full content to knowledge base
        kb_ref = self._save_to_knowledge_base(items, ai_system)
        
        # Create summary
        summary = self.summarizer.create_context_summary(items, target_tokens)
        summarized_tokens = self.estimate_tokens(summary)
        
        return SummaryResult(
            original_tokens=original_tokens,
            summarized_tokens=summarized_tokens,
            compression_ratio=summarized_tokens / original_tokens,
            summary=summary,
            preserved_in_kb=True,
            kb_reference=kb_ref
        )
    
    def _save_to_knowledge_base(self, items: List[ContextItem], 
                                 ai_system: str) -> str:
        """Save full content to Obsidian knowledge base."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"context_{ai_system}_{timestamp}.md"
        filepath = os.path.join(self.summaries_path, filename)
        
        # Build markdown content
        content = f"""---
type: context_archive
ai_system: {ai_system}
timestamp: {datetime.now().isoformat()}
items_count: {len(items)}
total_tokens: {sum(item.token_count for item in items)}
tags:
  - context
  - archive
  - {ai_system}
---

# Context Archive: {ai_system}

Archived: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
This is a preserved context archive. The AI received a summarized version
to prevent context overflow and hallucinations.

## Full Context Items

"""
        for item in items:
            content += f"""### {item.item_type.upper()} ({item.timestamp})
Priority: {item.priority} | Tokens: {item.token_count}

{item.content}

---

"""
        
        content += f"""
## Related
- [[Learning Summary]]
- [[Context Management]]

---
*Preserved by Om Vinayaka Summary Engine*
"""
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def get_optimized_context(self, ai_system: str) -> str:
        """
        Get optimized context string for an AI system.
        
        This is what should be sent to the AI - it's either the full context
        if within limits, or a summarized version if too large.
        
        Returns:
            Optimized context string ready for AI consumption
        """
        items = self.contexts.get(ai_system, [])
        if not items:
            return ""
        
        # Sort by priority (high first) then timestamp (recent first)
        sorted_items = sorted(
            items, 
            key=lambda x: (-x.priority, x.timestamp),
            reverse=True
        )
        
        # Build context string
        parts = []
        for item in sorted_items:
            if item.is_summarized:
                parts.append(f"[Summary] {item.content}")
            elif item.item_type == 'user_input':
                parts.append(f"User: {item.content}")
            elif item.item_type == 'ai_response':
                parts.append(f"Assistant: {item.content}")
            elif item.item_type == 'system':
                parts.append(f"[System] {item.content}")
            else:
                parts.append(item.content)
        
        return "\n".join(parts)
    
    def clear_context(self, ai_system: str):
        """Clear the context for an AI system."""
        if ai_system in self.contexts:
            # Save to KB before clearing
            items = self.contexts[ai_system]
            if items:
                self._save_to_knowledge_base(items, ai_system)
            self.contexts[ai_system] = []
            self.stats['contexts_managed'] += 1
    
    def get_statistics(self) -> Dict:
        """Get summary engine statistics."""
        context_stats = {}
        for ai_system in self.contexts:
            state = self.get_context_state(ai_system)
            context_stats[ai_system] = {
                'tokens': state.total_tokens,
                'limit': state.limit,
                'usage': f"{state.usage_percent:.1%}",
                'items': state.items_count,
            }
        
        return {
            **self.stats,
            'contexts': context_stats,
            'version': self.VERSION,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ResourceCalculator:
    """
    Calculates real RAM and CPU requirements for VA21 OS.
    
    Components tracked:
    - Guardian AI (sandboxed Ollama)
    - User-facing Ollama
    - Om Vinayaka Accessibility AI
    - Helper AI
    - Orchestration AI
    - Voice recognition
    - Text-to-speech
    - Summary Engine
    """
    
    # RAM requirements in MB
    RAM_REQUIREMENTS = {
        'base_os': 512,               # Debian base
        'desktop_environment': 256,   # Zork-style DE
        'guardian_ai_ollama': 2048,   # Sandboxed Ollama (granite-guardian:2b)
        'user_ollama': 2048,          # User-facing Ollama
        'om_vinayaka_ai': 256,        # Accessibility AI runtime
        'helper_ai': 128,             # Helper AI runtime
        'orchestration_ai': 128,      # Orchestration runtime
        'voice_recognition': 512,     # Whisper/MMS models
        'tts': 256,                   # Piper/Kokoro TTS
        'summary_engine': 64,         # Summary Engine
        'obsidian_vault': 64,         # Knowledge base
        'system_overhead': 256,       # General overhead
    }
    
    # CPU requirements (cores recommended)
    CPU_REQUIREMENTS = {
        'minimum': 2,       # Absolute minimum
        'recommended': 4,   # Recommended for smooth operation
        'optimal': 8,       # For best performance with AI
    }
    
    @classmethod
    def calculate_ram(cls, include_all_ai: bool = True) -> Dict:
        """Calculate RAM requirements."""
        total = 0
        breakdown = {}
        
        for component, ram in cls.RAM_REQUIREMENTS.items():
            breakdown[component] = ram
            total += ram
        
        # If running without all AI, reduce
        if not include_all_ai:
            total -= (cls.RAM_REQUIREMENTS['guardian_ai_ollama'] + 
                     cls.RAM_REQUIREMENTS['user_ollama'])
        
        return {
            'minimum_mb': 4096,
            'recommended_mb': 8192,
            'optimal_mb': 16384,
            'calculated_mb': total,
            'breakdown': breakdown,
        }
    
    @classmethod
    def calculate_cpu(cls) -> Dict:
        """Calculate CPU requirements."""
        return cls.CPU_REQUIREMENTS
    
    @classmethod
    def get_full_requirements(cls) -> str:
        """Get formatted system requirements."""
        ram = cls.calculate_ram()
        cpu = cls.calculate_cpu()
        
        return f"""
## VA21 OS System Requirements

### Minimum Requirements
- **RAM**: 4 GB
- **CPU**: 2 cores
- **Storage**: 20 GB
- **Note**: AI features will be limited

### Recommended Requirements
- **RAM**: 8 GB
- **CPU**: 4 cores
- **Storage**: 40 GB
- **Note**: Full AI experience

### Optimal Requirements
- **RAM**: 16 GB
- **CPU**: 8 cores
- **Storage**: 80 GB
- **GPU**: Optional (NVIDIA with CUDA for faster AI)
- **Note**: Best performance with all features

### RAM Breakdown (Full Installation)
| Component | RAM (MB) |
|-----------|----------|
| Base OS (Debian) | {ram['breakdown']['base_os']} |
| Desktop Environment | {ram['breakdown']['desktop_environment']} |
| Guardian AI (Sandboxed Ollama) | {ram['breakdown']['guardian_ai_ollama']} |
| User-facing Ollama | {ram['breakdown']['user_ollama']} |
| Om Vinayaka AI | {ram['breakdown']['om_vinayaka_ai']} |
| Voice Recognition | {ram['breakdown']['voice_recognition']} |
| Text-to-Speech | {ram['breakdown']['tts']} |
| Summary Engine | {ram['breakdown']['summary_engine']} |
| **Total Calculated** | **{ram['calculated_mb']} MB** |

### CPU Usage by Component
- **AI Inference**: 2-4 cores during active use
- **Voice Processing**: 1-2 cores during recognition
- **Background Services**: 0.5-1 core
- **Summary Engine**: Minimal (burst usage)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_summary_engine_instance = None


def get_summary_engine(knowledge_base_path: str = None) -> SummaryEngine:
    """Get or create the Summary Engine singleton."""
    global _summary_engine_instance
    
    if _summary_engine_instance is None:
        _summary_engine_instance = SummaryEngine(knowledge_base_path)
    
    return _summary_engine_instance


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the Summary Engine."""
    print("=" * 70)
    print("VA21 OS - Summary Engine Test")
    print("=" * 70)
    
    engine = get_summary_engine()
    
    # Test adding context
    print("\n--- Adding Context Items ---")
    
    # Simulate conversation
    engine.add_to_context('helper_ai', "Hello, I need help with my files", 
                          'user_input', PRIORITY_LEVELS['high'])
    engine.add_to_context('helper_ai', "I can help you with files. What would you like to do?",
                          'ai_response', PRIORITY_LEVELS['high'])
    engine.add_to_context('helper_ai', "I want to organize my photos",
                          'user_input', PRIORITY_LEVELS['high'])
    
    # Add some lower priority context
    for i in range(10):
        engine.add_to_context('helper_ai', 
                              f"Background information item {i}: Lorem ipsum dolor sit amet...",
                              'knowledge', PRIORITY_LEVELS['low'])
    
    # Check state
    state = engine.get_context_state('helper_ai')
    print(f"Context state: {state.total_tokens} tokens, {state.usage_percent:.1%} usage")
    print(f"Needs summarization: {state.needs_summarization}")
    
    # Get optimized context
    print("\n--- Optimized Context ---")
    context = engine.get_optimized_context('helper_ai')
    print(f"Context length: {len(context)} chars")
    print(f"Preview: {context[:200]}...")
    
    # Test summarizer directly
    print("\n--- Testing Summarizer ---")
    summarizer = ContextAwareSummarizer()
    long_text = """
    The VA21 Operating System is a revolutionary research platform designed for 
    privacy-conscious users. It features an intelligent accessibility system called 
    Om Vinayaka that provides natural language interaction with all applications.
    The system uses Zork-style text adventure interfaces to make computing accessible.
    Users can control any application with voice commands in over 1,600 languages.
    The Guardian AI provides security at the kernel level, completely isolated from 
    user-facing AI systems. All data is stored locally and never sent to external 
    services without explicit user consent.
    """
    
    summary = summarizer.summarize(long_text, 0.4)
    print(f"Original: {len(long_text)} chars")
    print(f"Summary: {len(summary)} chars")
    print(f"Summary text: {summary}")
    
    # Show statistics
    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # Show system requirements
    print("\n--- System Requirements ---")
    print(ResourceCalculator.get_full_requirements())
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
