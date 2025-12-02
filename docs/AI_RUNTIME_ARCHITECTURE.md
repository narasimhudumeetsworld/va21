# VA21 AI Runtime Architecture

*Om Vinayaka - First Alpha Release (v1.0.0-alpha.1)*

## Overview

VA21 OS uses a dual-runtime AI architecture to balance security requirements with model availability:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VA21 OS AI Layer                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────┐       ┌─────────────────────────────────┐  │
│  │   GUARDIAN AI       │       │        HELPER AI                 │  │
│  │   (Security Core)   │       │    (User Assistant)              │  │
│  │                     │       │                                  │  │
│  │  Runtime: ONNX      │       │  Runtime: Ollama/Transformers   │  │
│  │  License: MIT       │       │  License: MIT/Apache 2.0        │  │
│  │                     │       │                                  │  │
│  │  Features:          │       │  Features:                       │  │
│  │  - Security scan    │       │  - IBM Granite support          │  │
│  │  - Threat detection │       │  - Llama 3 support              │  │
│  │  - Code analysis    │       │  - Phi-3 support                │  │
│  │  - Always active    │       │  - Multi-model switching        │  │
│  └─────────────────────┘       └─────────────────────────────────┘  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                  ANTI-HALLUCINATION SYSTEM                       ││
│  │  - Timestamped IDs    - Cross-validation    - Confidence scores ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    SYNCED MEMORY SYSTEM                          ││
│  │  - Shared across Helper AI instances    - Verified storage      ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Why Two Runtimes?

### Guardian AI → ONNX Runtime

The Guardian AI security core uses Microsoft's ONNX Runtime because:

1. **Fast Inference**: ONNX is optimized for real-time security checks
2. **Small Footprint**: Quantized models run efficiently with minimal RAM
3. **Always-On**: Must be reliable and lightweight for continuous monitoring
4. **Enterprise-Grade**: Microsoft's production-quality runtime

### Helper AI → Ollama/Transformers

The Helper AI uses Ollama or Hugging Face Transformers because:

1. **IBM Granite Support**: Granite models don't have official ONNX versions
2. **Wide Model Selection**: Access to thousands of models
3. **Permissive Licensing**: MIT and Apache 2.0 licenses
4. **Easy Updates**: Simple model switching and updates

## Supported Models

### Guardian AI (ONNX)
| Model | Purpose | Size |
|-------|---------|------|
| Guardian Security Core | Threat detection | ~384MB |
| Phi-3 ONNX | Security analysis | ~768MB |

### Helper AI (Ollama/Transformers)
| Model | Provider | License | Size |
|-------|----------|---------|------|
| IBM Granite 4.0 Micro | Transformers | Apache 2.0 | ~768MB |
| IBM Granite 4.0 Dense 2B | Transformers | Apache 2.0 | ~512MB |
| IBM Granite 4.0 Dense 8B | Transformers | Apache 2.0 | ~2GB |
| Llama 3 8B | Ollama | Meta License | ~2GB |
| Phi-3 Mini | Ollama | MIT | ~1GB |
| Code Llama | Ollama | Meta License | ~2GB |

## Anti-Hallucination System

VA21 includes a built-in anti-hallucination system to ensure AI responses are accurate:

### Features
- **Timestamped Unique IDs**: Every AI-generated ID includes creation timestamp and checksum
- **Cross-Validation**: Multiple verification layers check consistency
- **Obsidian Integration**: Visual mind maps for verification
- **Confidence Scoring**: Know how reliable each response is (0.0 - 1.0)
- **Alert System**: Automatic notification when hallucinations are detected

### How It Works
1. When Helper AI generates a response, it's assigned a unique ID
2. The ID includes: `{type}_{date}_{time}_{random}_{checksum}`
3. Each response is validated against stored knowledge
4. Confidence score is calculated and returned with the response
5. Low-confidence or unverifiable responses trigger alerts

### Example ID Format
```
backup_20241202_081500_a1b2c3d4_f9e8d7c6
│       │        │       │        │
│       │        │       │        └─ Checksum (8 chars)
│       │        │       └─ Random component (8 chars)
│       │        └─ Time (HHMMSS)
│       └─ Date (YYYYMMDD)
└─ Component type
```

## Synced Memory System

Helper AI instances share knowledge through a synchronized memory system:

### Features
- **Cross-Instance Sharing**: All Helper AI instances access the same knowledge base
- **Anti-Hallucination Verification**: Memory entries are cryptographically verified
- **Persistence**: Memory survives application restarts
- **Integrity Validation**: Checksum-based integrity checks

### API Example
```python
from helper_ai import get_helper_ai

helper = get_helper_ai()

# Store verified memory
result = helper.sync_memory("user_preference", {"theme": "dark"})
# Returns: {"success": True, "memory_id": "...", "verified": True}

# Recall with validation
memory = helper.recall_memory("user_preference")
# Returns: {"success": True, "value": {...}, "ah_valid": True}
```

## Configuration

### Runtime Selection

By default, VA21 selects the optimal runtime automatically. You can check the current configuration:

```python
from ai_runtime_config import get_runtime_manager

manager = get_runtime_manager()
status = manager.get_status()
print(status)
```

### Memory Limits

| Scenario | RAM Required | Description |
|----------|--------------|-------------|
| Minimal | ~3GB | Guardian AI only |
| Standard | ~5GB | Guardian + one Helper model |
| Heavy | ~7GB | Guardian + multiple models |
| Maximum | ~9GB | All features active |

## Acknowledgments

This architecture is made possible by:

- **IBM Research** - Granite models (Apache 2.0)
- **Microsoft** - ONNX Runtime (MIT)
- **Ollama Project** - Local LLM deployment (MIT)
- **Hugging Face** - Transformers library (Apache 2.0)
- **Meta AI** - LLaMA models and PyTorch

---

*Om Vinayaka - May this alpha release mark the beginning of a new era in secure, intelligent computing.* 🛡️🐧
