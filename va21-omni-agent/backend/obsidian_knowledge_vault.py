"""
VA21 OS - Obsidian Knowledge Vault with Mind Map
Anti-hallucination system with timestamps, unique IDs, and cross-validation

Om Vinayaka - Divine guidance for clarity and truth
"""

import os
import json
import hashlib
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import gzip
import shutil
from pathlib import Path


class NodeType(Enum):
    """Types of knowledge nodes in the vault"""
    CONCEPT = "concept"
    FACT = "fact"
    PROCEDURE = "procedure"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    EVENT = "event"
    CODE = "code"
    SYSTEM_STATE = "system_state"
    USER_ACTION = "user_action"
    AI_RESPONSE = "ai_response"


class ValidationStatus(Enum):
    """Validation status for anti-hallucination"""
    VERIFIED = "verified"
    PENDING = "pending"
    CONFLICT = "conflict"
    STALE = "stale"
    ARCHIVED = "archived"


@dataclass
class UniqueIdentifier:
    """Unique identifier with timestamp for anti-hallucination"""
    uid: str  # Random unique ID
    timestamp: str  # ISO format timestamp
    epoch_ms: int  # Millisecond precision epoch
    checksum: str  # SHA-256 checksum of uid + timestamp
    sequence: int  # Sequential number for ordering
    
    @classmethod
    def generate(cls, sequence: int = 0) -> 'UniqueIdentifier':
        """Generate a new unique identifier with timestamp"""
        uid = f"VA21-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}"
        now = datetime.now()
        timestamp = now.isoformat()
        epoch_ms = int(now.timestamp() * 1000)
        
        # Create checksum for validation
        checksum_data = f"{uid}:{timestamp}:{epoch_ms}"
        checksum = hashlib.sha256(checksum_data.encode()).hexdigest()[:16]
        
        return cls(
            uid=uid,
            timestamp=timestamp,
            epoch_ms=epoch_ms,
            checksum=checksum,
            sequence=sequence
        )
    
    def validate(self) -> bool:
        """Validate the identifier hasn't been tampered with"""
        checksum_data = f"{self.uid}:{self.timestamp}:{self.epoch_ms}"
        expected_checksum = hashlib.sha256(checksum_data.encode()).hexdigest()[:16]
        return self.checksum == expected_checksum
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeNode:
    """A node in the knowledge vault with full traceability"""
    id: UniqueIdentifier
    node_type: NodeType
    title: str
    content: str
    tags: List[str]
    links: List[str]  # UIDs of linked nodes
    metadata: Dict[str, Any]
    version: int
    version_history: List[Dict]  # Previous versions
    validation_status: ValidationStatus
    created_at: str
    updated_at: str
    accessed_at: str
    access_count: int
    source: str  # Where this knowledge came from
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id.to_dict(),
            'node_type': self.node_type.value,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'links': self.links,
            'metadata': self.metadata,
            'version': self.version,
            'version_history': self.version_history,
            'validation_status': self.validation_status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'accessed_at': self.accessed_at,
            'access_count': self.access_count,
            'source': self.source,
            'confidence': self.confidence
        }


@dataclass
class MindMapNode:
    """Node for the mind map visualization"""
    uid: str
    label: str
    node_type: str
    x: float
    y: float
    connections: List[str]
    color: str
    size: float
    metadata: Dict[str, Any]


class ObsidianKnowledgeVault:
    """
    Obsidian-style knowledge vault with mind mapping
    Features anti-hallucination through unique IDs and timestamp validation
    """
    
    def __init__(self, vault_path: str = None):
        self.vault_path = vault_path or os.path.expanduser("~/.va21/knowledge_vault")
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.mind_map: Dict[str, MindMapNode] = {}
        self.sequence_counter = 0
        self.lock = threading.RLock()
        
        # Index structures for fast lookup
        self.tag_index: Dict[str, List[str]] = {}
        self.type_index: Dict[NodeType, List[str]] = {}
        self.timestamp_index: List[Tuple[int, str]] = []  # (epoch_ms, uid)
        
        # Validation cache
        self.validation_cache: Dict[str, Tuple[bool, str]] = {}
        
        # Initialize vault
        self._initialize_vault()
    
    def _initialize_vault(self):
        """Initialize the knowledge vault directory structure"""
        Path(self.vault_path).mkdir(parents=True, exist_ok=True)
        Path(f"{self.vault_path}/nodes").mkdir(exist_ok=True)
        Path(f"{self.vault_path}/mind_maps").mkdir(exist_ok=True)
        Path(f"{self.vault_path}/archives").mkdir(exist_ok=True)
        Path(f"{self.vault_path}/indexes").mkdir(exist_ok=True)
        
        # Load existing nodes
        self._load_nodes()
    
    def _load_nodes(self):
        """Load existing nodes from disk"""
        nodes_path = Path(f"{self.vault_path}/nodes")
        if nodes_path.exists():
            for node_file in nodes_path.glob("*.json"):
                try:
                    with open(node_file, 'r') as f:
                        data = json.load(f)
                        node = self._dict_to_node(data)
                        if node:
                            self.nodes[node.id.uid] = node
                            self._index_node(node)
                except Exception as e:
                    print(f"Error loading node {node_file}: {e}")
    
    def _dict_to_node(self, data: Dict) -> Optional[KnowledgeNode]:
        """Convert dictionary to KnowledgeNode"""
        try:
            uid = UniqueIdentifier(**data['id'])
            return KnowledgeNode(
                id=uid,
                node_type=NodeType(data['node_type']),
                title=data['title'],
                content=data['content'],
                tags=data['tags'],
                links=data['links'],
                metadata=data['metadata'],
                version=data['version'],
                version_history=data['version_history'],
                validation_status=ValidationStatus(data['validation_status']),
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                accessed_at=data['accessed_at'],
                access_count=data['access_count'],
                source=data['source'],
                confidence=data['confidence']
            )
        except Exception:
            return None
    
    def _index_node(self, node: KnowledgeNode):
        """Add node to indexes"""
        uid = node.id.uid
        
        # Tag index
        for tag in node.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            if uid not in self.tag_index[tag]:
                self.tag_index[tag].append(uid)
        
        # Type index
        if node.node_type not in self.type_index:
            self.type_index[node.node_type] = []
        if uid not in self.type_index[node.node_type]:
            self.type_index[node.node_type].append(uid)
        
        # Timestamp index
        self.timestamp_index.append((node.id.epoch_ms, uid))
        self.timestamp_index.sort(key=lambda x: x[0])
    
    def create_node(
        self,
        node_type: NodeType,
        title: str,
        content: str,
        tags: List[str] = None,
        links: List[str] = None,
        metadata: Dict[str, Any] = None,
        source: str = "user",
        confidence: float = 1.0
    ) -> KnowledgeNode:
        """Create a new knowledge node with unique ID and timestamp"""
        with self.lock:
            self.sequence_counter += 1
            uid = UniqueIdentifier.generate(self.sequence_counter)
            now = datetime.now().isoformat()
            
            node = KnowledgeNode(
                id=uid,
                node_type=node_type,
                title=title,
                content=content,
                tags=tags or [],
                links=links or [],
                metadata=metadata or {},
                version=1,
                version_history=[],
                validation_status=ValidationStatus.VERIFIED,
                created_at=now,
                updated_at=now,
                accessed_at=now,
                access_count=1,
                source=source,
                confidence=confidence
            )
            
            self.nodes[uid.uid] = node
            self._index_node(node)
            self._save_node(node)
            
            # Update mind map
            self._update_mind_map(node)
            
            return node
    
    def _save_node(self, node: KnowledgeNode):
        """Save node to disk"""
        node_path = Path(f"{self.vault_path}/nodes/{node.id.uid}.json")
        with open(node_path, 'w') as f:
            json.dump(node.to_dict(), f, indent=2)
    
    def update_node(
        self,
        uid: str,
        title: str = None,
        content: str = None,
        tags: List[str] = None,
        links: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[KnowledgeNode]:
        """Update a node with version history"""
        with self.lock:
            if uid not in self.nodes:
                return None
            
            node = self.nodes[uid]
            
            # Save current state to version history
            version_snapshot = {
                'version': node.version,
                'title': node.title,
                'content': node.content,
                'tags': node.tags.copy(),
                'links': node.links.copy(),
                'metadata': node.metadata.copy(),
                'updated_at': node.updated_at,
                'snapshot_id': UniqueIdentifier.generate().to_dict()
            }
            node.version_history.append(version_snapshot)
            
            # Update fields
            if title is not None:
                node.title = title
            if content is not None:
                node.content = content
            if tags is not None:
                node.tags = tags
            if links is not None:
                node.links = links
            if metadata is not None:
                node.metadata.update(metadata)
            
            node.version += 1
            node.updated_at = datetime.now().isoformat()
            
            self._save_node(node)
            self._update_mind_map(node)
            
            return node
    
    def get_node(self, uid: str, validate: bool = True) -> Optional[KnowledgeNode]:
        """Get a node by UID with optional validation"""
        with self.lock:
            if uid not in self.nodes:
                return None
            
            node = self.nodes[uid]
            
            if validate:
                # Validate the node's ID hasn't been tampered with
                if not node.id.validate():
                    node.validation_status = ValidationStatus.CONFLICT
                    self._save_node(node)
                    return None
            
            # Update access tracking
            node.accessed_at = datetime.now().isoformat()
            node.access_count += 1
            
            return node
    
    def search_nodes(
        self,
        query: str = None,
        node_type: NodeType = None,
        tags: List[str] = None,
        since: datetime = None,
        until: datetime = None
    ) -> List[KnowledgeNode]:
        """Search nodes with various filters"""
        results = []
        
        for node in self.nodes.values():
            # Type filter
            if node_type and node.node_type != node_type:
                continue
            
            # Tag filter
            if tags and not any(tag in node.tags for tag in tags):
                continue
            
            # Time range filter
            if since:
                node_time = datetime.fromisoformat(node.created_at)
                if node_time < since:
                    continue
            if until:
                node_time = datetime.fromisoformat(node.created_at)
                if node_time > until:
                    continue
            
            # Query filter (search in title and content)
            if query:
                query_lower = query.lower()
                if query_lower not in node.title.lower() and query_lower not in node.content.lower():
                    continue
            
            results.append(node)
        
        return results
    
    def _update_mind_map(self, node: KnowledgeNode):
        """Update the mind map with node information"""
        # Simple radial layout based on node type
        type_colors = {
            NodeType.CONCEPT: "#4CAF50",
            NodeType.FACT: "#2196F3",
            NodeType.PROCEDURE: "#FF9800",
            NodeType.ENTITY: "#9C27B0",
            NodeType.RELATIONSHIP: "#00BCD4",
            NodeType.EVENT: "#F44336",
            NodeType.CODE: "#607D8B",
            NodeType.SYSTEM_STATE: "#795548",
            NodeType.USER_ACTION: "#3F51B5",
            NodeType.AI_RESPONSE: "#E91E63"
        }
        
        # Calculate position based on existing nodes
        count = len(self.mind_map)
        angle = (count * 0.618033988749895) * 2 * 3.14159  # Golden ratio for distribution
        radius = 100 + (count // 10) * 50
        
        mind_node = MindMapNode(
            uid=node.id.uid,
            label=node.title[:30] + "..." if len(node.title) > 30 else node.title,
            node_type=node.node_type.value,
            x=radius * (1 if count % 2 == 0 else -1) * abs(hash(node.id.uid) % 100) / 100,
            y=radius * (1 if count % 3 == 0 else -1) * abs(hash(node.id.uid + "y") % 100) / 100,
            connections=node.links,
            color=type_colors.get(node.node_type, "#9E9E9E"),
            size=20 + min(node.access_count * 2, 50),
            metadata={
                'version': node.version,
                'confidence': node.confidence,
                'created_at': node.created_at
            }
        )
        
        self.mind_map[node.id.uid] = mind_node
        self._save_mind_map()
    
    def _save_mind_map(self):
        """Save mind map to disk"""
        mind_map_data = {
            uid: asdict(node) for uid, node in self.mind_map.items()
        }
        with open(f"{self.vault_path}/mind_maps/main.json", 'w') as f:
            json.dump(mind_map_data, f, indent=2)
    
    def get_mind_map(self) -> Dict[str, MindMapNode]:
        """Get the current mind map"""
        return self.mind_map
    
    def validate_all_nodes(self) -> Dict[str, Any]:
        """Validate all nodes for anti-hallucination"""
        results = {
            'total': len(self.nodes),
            'verified': 0,
            'conflicts': [],
            'stale': [],
            'validated_at': datetime.now().isoformat()
        }
        
        for uid, node in self.nodes.items():
            if node.id.validate():
                results['verified'] += 1
            else:
                results['conflicts'].append({
                    'uid': uid,
                    'title': node.title,
                    'issue': 'checksum_mismatch'
                })
                node.validation_status = ValidationStatus.CONFLICT
            
            # Check for stale nodes (not accessed in 30 days)
            last_access = datetime.fromisoformat(node.accessed_at)
            if datetime.now() - last_access > timedelta(days=30):
                results['stale'].append(uid)
                node.validation_status = ValidationStatus.STALE
        
        return results
    
    def archive_old_versions(self, keep_versions: int = 5):
        """Archive old version history to save memory"""
        archived = 0
        
        for uid, node in self.nodes.items():
            if len(node.version_history) > keep_versions:
                # Archive old versions
                old_versions = node.version_history[:-keep_versions]
                
                archive_file = f"{self.vault_path}/archives/{uid}_versions.json.gz"
                
                # Load existing archive if any
                existing = []
                if os.path.exists(archive_file):
                    with gzip.open(archive_file, 'rt') as f:
                        existing = json.load(f)
                
                existing.extend(old_versions)
                
                # Save compressed archive
                with gzip.open(archive_file, 'wt') as f:
                    json.dump(existing, f)
                
                # Keep only recent versions in memory
                node.version_history = node.version_history[-keep_versions:]
                archived += len(old_versions)
                
                self._save_node(node)
        
        return archived
    
    def delete_old_versions(self, older_than_days: int = 90) -> int:
        """Delete version history older than specified days"""
        deleted = 0
        cutoff = datetime.now() - timedelta(days=older_than_days)
        
        for uid, node in self.nodes.items():
            new_history = []
            for version in node.version_history:
                version_time = datetime.fromisoformat(version['updated_at'])
                if version_time >= cutoff:
                    new_history.append(version)
                else:
                    deleted += 1
            
            if len(new_history) != len(node.version_history):
                node.version_history = new_history
                self._save_node(node)
        
        return deleted
    
    def cross_validate(self, uid1: str, uid2: str) -> Dict[str, Any]:
        """Cross-validate two nodes for consistency (anti-hallucination)"""
        node1 = self.nodes.get(uid1)
        node2 = self.nodes.get(uid2)
        
        if not node1 or not node2:
            return {'valid': False, 'error': 'Node not found'}
        
        result = {
            'valid': True,
            'uid1': uid1,
            'uid2': uid2,
            'checks': []
        }
        
        # Check 1: Both IDs are valid
        if not node1.id.validate():
            result['valid'] = False
            result['checks'].append({'check': 'uid1_validation', 'passed': False})
        else:
            result['checks'].append({'check': 'uid1_validation', 'passed': True})
        
        if not node2.id.validate():
            result['valid'] = False
            result['checks'].append({'check': 'uid2_validation', 'passed': False})
        else:
            result['checks'].append({'check': 'uid2_validation', 'passed': True})
        
        # Check 2: Temporal consistency (if linked, newer should reference older)
        if uid2 in node1.links:
            if node1.id.epoch_ms < node2.id.epoch_ms:
                result['checks'].append({
                    'check': 'temporal_consistency',
                    'passed': False,
                    'warning': 'Node1 references Node2 but was created before it'
                })
            else:
                result['checks'].append({'check': 'temporal_consistency', 'passed': True})
        
        # Check 3: Sequence consistency
        if node1.id.sequence > 0 and node2.id.sequence > 0:
            if node1.id.sequence > node2.id.sequence and node1.id.epoch_ms < node2.id.epoch_ms:
                result['valid'] = False
                result['checks'].append({
                    'check': 'sequence_consistency',
                    'passed': False,
                    'error': 'Sequence numbers do not match temporal order'
                })
            else:
                result['checks'].append({'check': 'sequence_consistency', 'passed': True})
        
        return result
    
    def generate_obsidian_markdown(self, uid: str) -> str:
        """Generate Obsidian-compatible markdown for a node"""
        node = self.nodes.get(uid)
        if not node:
            return ""
        
        md = f"""---
uid: {node.id.uid}
timestamp: {node.id.timestamp}
checksum: {node.id.checksum}
type: {node.node_type.value}
version: {node.version}
confidence: {node.confidence}
validation: {node.validation_status.value}
tags: [{', '.join(node.tags)}]
created: {node.created_at}
updated: {node.updated_at}
---

# {node.title}

{node.content}

## Links
"""
        for link in node.links:
            linked_node = self.nodes.get(link)
            if linked_node:
                md += f"- [[{linked_node.title}]] ({link})\n"
        
        md += f"""
## Metadata
- Source: {node.source}
- Access Count: {node.access_count}
- Version History: {len(node.version_history)} versions

## Validation Info
- UID: `{node.id.uid}`
- Checksum: `{node.id.checksum}`
- Epoch: `{node.id.epoch_ms}`
- Status: **{node.validation_status.value.upper()}**
"""
        return md
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        return {
            'total_nodes': len(self.nodes),
            'by_type': {
                t.value: len(uids) for t, uids in self.type_index.items()
            },
            'total_tags': len(self.tag_index),
            'total_links': sum(len(n.links) for n in self.nodes.values()),
            'total_versions': sum(len(n.version_history) for n in self.nodes.values()),
            'mind_map_nodes': len(self.mind_map),
            'sequence_counter': self.sequence_counter
        }


class AntiHallucinationValidator:
    """
    Validator to prevent AI hallucinations using the knowledge vault
    Cross-references all information with stored, timestamped data
    """
    
    def __init__(self, vault: ObsidianKnowledgeVault):
        self.vault = vault
        self.validation_log: List[Dict] = []
    
    def validate_claim(
        self,
        claim: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate a claim against the knowledge vault"""
        validation_id = UniqueIdentifier.generate()
        
        result = {
            'validation_id': validation_id.to_dict(),
            'claim': claim,
            'validated': False,
            'confidence': 0.0,
            'supporting_nodes': [],
            'conflicts': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Search for relevant nodes
        relevant = self.vault.search_nodes(query=claim)
        
        if relevant:
            result['validated'] = True
            result['confidence'] = max(n.confidence for n in relevant)
            result['supporting_nodes'] = [
                {
                    'uid': n.id.uid,
                    'title': n.title,
                    'confidence': n.confidence,
                    'validation_status': n.validation_status.value
                }
                for n in relevant[:5]  # Top 5 matches
            ]
            
            # Check for conflicts
            for node in relevant:
                if node.validation_status == ValidationStatus.CONFLICT:
                    result['conflicts'].append({
                        'uid': node.id.uid,
                        'issue': 'validation_conflict'
                    })
                    result['confidence'] *= 0.5  # Reduce confidence on conflict
        
        self.validation_log.append(result)
        return result
    
    def record_ai_response(
        self,
        query: str,
        response: str,
        source_nodes: List[str] = None
    ) -> KnowledgeNode:
        """Record an AI response for future validation"""
        return self.vault.create_node(
            node_type=NodeType.AI_RESPONSE,
            title=f"AI Response: {query[:50]}...",
            content=response,
            tags=['ai_response', 'auto_generated'],
            links=source_nodes or [],
            metadata={
                'query': query,
                'response_length': len(response)
            },
            source='ai',
            confidence=0.8  # AI responses have lower default confidence
        )
    
    def get_validation_history(self, limit: int = 100) -> List[Dict]:
        """Get recent validation history"""
        return self.validation_log[-limit:]


# Global instance for use across the system
_vault_instance = None


def get_vault() -> ObsidianKnowledgeVault:
    """Get the global knowledge vault instance"""
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = ObsidianKnowledgeVault()
    return _vault_instance


def get_validator() -> AntiHallucinationValidator:
    """Get an anti-hallucination validator"""
    return AntiHallucinationValidator(get_vault())
