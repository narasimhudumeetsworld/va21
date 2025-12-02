#!/usr/bin/env python3
"""
VA21 Dynamic Context-Aware AI Resource Manager
================================================

Provides intelligent, dynamic management of multiple AI/LLM backends with:
- Automatic model switching based on load and availability
- Context-aware activation of appropriate models
- Resource-efficient operation with memory pressure handling
- Support for multiple LLM providers including IBM Granite models

Supported LLM Backends:
- IBM Granite 4.0 (Micro, Dense, Hybrid variants) - Apache License 2.0
- Ollama (local models) - MIT License
- ONNX Runtime (Guardian AI) - MIT License
- Gemini API
- Custom local models

Om Vinayaka - Intelligence flows where it is needed most.

Acknowledgments and Licenses:
- IBM Research for Granite models (Apache License 2.0)
  https://huggingface.co/collections/ibm-granite/granite-40-language-models
- Microsoft for ONNX Runtime (MIT License)
  https://github.com/microsoft/onnxruntime
- Microsoft for FARA technology (MIT License)
  https://github.com/microsoft/fara
- Hugging Face for model hosting
- Ollama project (MIT License)
"""

import os
import sys
import json
import threading
import time
import gc
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
from abc import ABC, abstractmethod
import random


class LLMProvider(Enum):
    """Supported LLM providers."""
    GRANITE_MICRO = "granite_micro"       # IBM Granite 4.0 Maverick Micro (3B)
    GRANITE_DENSE = "granite_dense"       # IBM Granite 4.0 Dense (2B/8B)
    GRANITE_HYBRID = "granite_hybrid"     # IBM Granite 4.0 Hybrid MoE
    OLLAMA = "ollama"                     # Local Ollama models
    ONNX_GUARDIAN = "onnx_guardian"       # ONNX Guardian AI
    GEMINI = "gemini"                     # Google Gemini API
    LOCAL_CUSTOM = "local_custom"         # Custom local models


class ModelState(Enum):
    """State of a model in the resource manager."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    COOLDOWN = "cooldown"


class ContextType(Enum):
    """Types of contexts for AI activation."""
    IDLE = "idle"
    SECURITY = "security"
    CHAT = "chat"
    CODING = "coding"
    RESEARCH = "research"
    LEGACY_APP = "legacy_app"
    UI_AUTOMATION = "ui_automation"
    BACKUP = "backup"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class LLMConfig:
    """Configuration for an LLM backend."""
    model_id: str
    provider: LLMProvider
    name: str
    description: str
    size_mb: int
    compressed_size_mb: int
    context_window: int
    capabilities: List[str]
    priority: int  # Higher = more preferred
    contexts: List[ContextType]
    quantization: str = "int8"
    min_ram_mb: int = 512
    max_concurrent: int = 1
    timeout_seconds: int = 60
    fallback_model: Optional[str] = None
    huggingface_id: Optional[str] = None
    api_endpoint: Optional[str] = None


@dataclass
class ModelMetrics:
    """Metrics for model performance tracking."""
    model_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0
    last_used: Optional[datetime] = None
    uptime_seconds: float = 0.0
    memory_usage_mb: int = 0


@dataclass
class ResourceStatus:
    """Current status of AI resources."""
    total_ram_available_mb: int
    total_ram_used_mb: int
    models_loaded: List[str]
    models_available: List[str]
    current_context: ContextType
    active_requests: int
    queue_depth: int


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""
    
    @abstractmethod
    def load(self) -> bool:
        """Load the model into memory."""
        pass
    
    @abstractmethod
    def unload(self) -> bool:
        """Unload the model from memory."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if model is ready for inference."""
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> int:
        """Get current memory usage in MB."""
        pass


class GraniteBackend(LLMBackend):
    """IBM Granite model backend."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.state = ModelState.UNLOADED
        self.memory_used_mb = 0
        
    def load(self) -> bool:
        """Load IBM Granite model."""
        try:
            self.state = ModelState.LOADING
            print(f"[GraniteBackend] Loading {self.config.name}...")
            
            # In production, this would use transformers or similar
            # For now, simulate loading
            self.memory_used_mb = self.config.compressed_size_mb
            self.state = ModelState.READY
            
            print(f"[GraniteBackend] {self.config.name} loaded ({self.memory_used_mb}MB)")
            return True
            
        except Exception as e:
            print(f"[GraniteBackend] Error loading {self.config.name}: {e}")
            self.state = ModelState.ERROR
            return False
    
    def unload(self) -> bool:
        """Unload IBM Granite model."""
        try:
            self.model = None
            self.tokenizer = None
            self.memory_used_mb = 0
            self.state = ModelState.UNLOADED
            gc.collect()
            print(f"[GraniteBackend] {self.config.name} unloaded")
            return True
        except Exception as e:
            print(f"[GraniteBackend] Error unloading: {e}")
            return False
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate text using Granite model."""
        if self.state != ModelState.READY:
            return f"[Error: Model {self.config.name} not ready]"
        
        try:
            self.state = ModelState.BUSY
            # Simulate generation (in production, use actual model)
            time.sleep(0.1)  # Simulate latency
            response = f"[{self.config.name}] Response to: {prompt[:50]}..."
            self.state = ModelState.READY
            return response
        except Exception as e:
            self.state = ModelState.ERROR
            return f"[Error: {e}]"
    
    def is_ready(self) -> bool:
        return self.state == ModelState.READY
    
    def get_memory_usage(self) -> int:
        return self.memory_used_mb


class OllamaBackend(LLMBackend):
    """Ollama local model backend."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.state = ModelState.UNLOADED
        self.memory_used_mb = 0
        self.base_url = config.api_endpoint or "http://localhost:11434"
        
    def load(self) -> bool:
        try:
            self.state = ModelState.LOADING
            # Check if Ollama is available
            import subprocess
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.memory_used_mb = self.config.compressed_size_mb
                self.state = ModelState.READY
                print(f"[OllamaBackend] {self.config.name} ready")
                return True
            else:
                self.state = ModelState.ERROR
                return False
        except Exception as e:
            print(f"[OllamaBackend] Error: {e}")
            self.state = ModelState.UNLOADED
            return False
    
    def unload(self) -> bool:
        self.memory_used_mb = 0
        self.state = ModelState.UNLOADED
        return True
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if self.state != ModelState.READY:
            return f"[Error: Ollama not ready]"
        
        try:
            import subprocess
            result = subprocess.run(
                ['ollama', 'run', self.config.model_id, prompt],
                capture_output=True, text=True, timeout=self.config.timeout_seconds
            )
            return result.stdout.strip()
        except Exception as e:
            return f"[Ollama Error: {e}]"
    
    def is_ready(self) -> bool:
        return self.state == ModelState.READY
    
    def get_memory_usage(self) -> int:
        return self.memory_used_mb


class DynamicAIResourceManager:
    """
    Dynamic Context-Aware AI Resource Manager
    
    Manages multiple LLM backends with intelligent switching based on:
    - Current context/task type
    - Model availability and load
    - Memory pressure and system resources
    - Model capabilities and performance metrics
    
    Features:
    - Auto-switching between models based on availability
    - Load balancing for concurrent requests
    - Memory-aware model loading/unloading
    - Context-driven model selection
    - Fallback chains for reliability
    """
    
    # Memory targets (MB)
    RAM_MIN_MB = 7168   # 7GB minimum
    RAM_MAX_MB = 10240  # 10GB maximum
    
    def __init__(self, config_path: str = "data/ai_manager"):
        self.config_path = config_path
        os.makedirs(config_path, exist_ok=True)
        
        # Model registry
        self.models: Dict[str, LLMConfig] = {}
        self.backends: Dict[str, LLMBackend] = {}
        self.metrics: Dict[str, ModelMetrics] = {}
        
        # Resource tracking
        self.total_memory_used_mb = 0
        self.memory_limit_mb = self.RAM_MIN_MB - 768  # Reserve for OS
        
        # Context management
        self.current_context = ContextType.IDLE
        self.context_history: deque = deque(maxlen=100)
        
        # Request management
        self.request_queue: deque = deque(maxlen=1000)
        self.active_requests: Dict[str, dict] = {}
        
        # Model selection cache
        self.context_model_cache: Dict[ContextType, str] = {}
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Initialize default models
        self._init_default_models()
        
        print(f"[DynamicAIResourceManager] Initialized with {self.memory_limit_mb}MB budget")
    
    def _init_default_models(self):
        """Initialize default model configurations including IBM Granite."""
        
        default_models = [
            # IBM Granite 4.0 Models
            LLMConfig(
                model_id="granite-4.0-micro",
                provider=LLMProvider.GRANITE_MICRO,
                name="Granite 4.0 Maverick Micro",
                description="IBM Granite 3B hybrid model for ultra-light and concurrent agents",
                size_mb=1536,
                compressed_size_mb=768,
                context_window=8192,
                capabilities=["chat", "reasoning", "coding", "agents"],
                priority=85,
                contexts=[ContextType.CHAT, ContextType.CODING, ContextType.RESEARCH],
                quantization="int8",
                min_ram_mb=768,
                max_concurrent=4,
                timeout_seconds=30,
                huggingface_id="ibm-granite/granite-4.0-tiny-preview",
                fallback_model="granite-4.0-dense-2b",
            ),
            LLMConfig(
                model_id="granite-4.0-dense-2b",
                provider=LLMProvider.GRANITE_DENSE,
                name="Granite 4.0 Dense 2B",
                description="IBM Granite 2B dense model for efficient inference",
                size_mb=1024,
                compressed_size_mb=512,
                context_window=8192,
                capabilities=["chat", "reasoning"],
                priority=75,
                contexts=[ContextType.CHAT, ContextType.IDLE],
                quantization="int8",
                min_ram_mb=512,
                max_concurrent=3,
                timeout_seconds=30,
                huggingface_id="ibm-granite/granite-4.0-dense-2b-preview",
                fallback_model="ollama-phi3",
            ),
            LLMConfig(
                model_id="granite-4.0-dense-8b",
                provider=LLMProvider.GRANITE_DENSE,
                name="Granite 4.0 Dense 8B",
                description="IBM Granite 8B dense model for complex reasoning",
                size_mb=4096,
                compressed_size_mb=2048,
                context_window=16384,
                capabilities=["chat", "reasoning", "coding", "analysis"],
                priority=90,
                contexts=[ContextType.CODING, ContextType.RESEARCH, ContextType.SYSTEM_ADMIN],
                quantization="int8",
                min_ram_mb=2048,
                max_concurrent=2,
                timeout_seconds=60,
                huggingface_id="ibm-granite/granite-4.0-dense-8b-preview",
                fallback_model="granite-4.0-micro",
            ),
            LLMConfig(
                model_id="granite-4.0-hybrid-moe",
                provider=LLMProvider.GRANITE_HYBRID,
                name="Granite 4.0 Hybrid MoE",
                description="IBM Granite Mixture-of-Experts for specialized tasks",
                size_mb=6144,
                compressed_size_mb=3072,
                context_window=32768,
                capabilities=["chat", "reasoning", "coding", "analysis", "agents", "research"],
                priority=95,
                contexts=[ContextType.RESEARCH, ContextType.CODING],
                quantization="int8",
                min_ram_mb=3072,
                max_concurrent=1,
                timeout_seconds=90,
                huggingface_id="ibm-granite/granite-4.0-moe-preview",
                fallback_model="granite-4.0-dense-8b",
            ),
            
            # Guardian AI (always loaded)
            LLMConfig(
                model_id="guardian-ai",
                provider=LLMProvider.ONNX_GUARDIAN,
                name="Guardian AI Security Core",
                description="ONNX-based security analysis model",
                size_mb=768,
                compressed_size_mb=384,
                context_window=2048,
                capabilities=["security", "threat_detection", "code_analysis"],
                priority=100,  # Highest priority
                contexts=[ContextType.SECURITY],
                quantization="int8",
                min_ram_mb=384,
                max_concurrent=10,
                timeout_seconds=5,
            ),
            
            # Ollama models
            LLMConfig(
                model_id="ollama-phi3",
                provider=LLMProvider.OLLAMA,
                name="Phi-3 Mini (Ollama)",
                description="Microsoft Phi-3 via Ollama",
                size_mb=2048,
                compressed_size_mb=1024,
                context_window=4096,
                capabilities=["chat", "reasoning"],
                priority=60,
                contexts=[ContextType.CHAT, ContextType.IDLE],
                quantization="int4",
                min_ram_mb=1024,
                max_concurrent=2,
                timeout_seconds=45,
                fallback_model="granite-4.0-dense-2b",
            ),
            LLMConfig(
                model_id="ollama-codellama",
                provider=LLMProvider.OLLAMA,
                name="Code Llama (Ollama)",
                description="Meta Code Llama via Ollama",
                size_mb=4096,
                compressed_size_mb=2048,
                context_window=8192,
                capabilities=["coding", "code_analysis"],
                priority=70,
                contexts=[ContextType.CODING],
                quantization="int4",
                min_ram_mb=2048,
                max_concurrent=1,
                timeout_seconds=60,
                fallback_model="granite-4.0-micro",
            ),
            LLMConfig(
                model_id="ollama-llama3",
                provider=LLMProvider.OLLAMA,
                name="Llama 3 8B (Ollama)",
                description="Meta Llama 3 8B via Ollama",
                size_mb=4096,
                compressed_size_mb=2048,
                context_window=8192,
                capabilities=["chat", "reasoning", "coding"],
                priority=80,
                contexts=[ContextType.CHAT, ContextType.RESEARCH],
                quantization="int4",
                min_ram_mb=2048,
                max_concurrent=1,
                timeout_seconds=60,
                fallback_model="granite-4.0-dense-8b",
            ),
            
            # FARA Agent
            LLMConfig(
                model_id="fara-agent",
                provider=LLMProvider.GRANITE_MICRO,
                name="FARA UI Agent",
                description="FARA-inspired UI automation agent based on Granite",
                size_mb=1024,
                compressed_size_mb=512,
                context_window=4096,
                capabilities=["ui_automation", "legacy_app", "screenshot_analysis"],
                priority=80,
                contexts=[ContextType.LEGACY_APP, ContextType.UI_AUTOMATION],
                quantization="int8",
                min_ram_mb=512,
                max_concurrent=2,
                timeout_seconds=30,
                fallback_model="granite-4.0-micro",
            ),
        ]
        
        for config in default_models:
            self.models[config.model_id] = config
            self.metrics[config.model_id] = ModelMetrics(model_id=config.model_id)
    
    def set_context(self, context: ContextType) -> List[str]:
        """
        Set the current context and prepare appropriate models.
        
        Returns list of actions taken (models loaded/unloaded).
        """
        with self._lock:
            actions = []
            old_context = self.current_context
            self.current_context = context
            
            self.context_history.append({
                "context": context.value,
                "timestamp": datetime.now().isoformat(),
            })
            
            # Determine best models for this context
            context_models = self._get_models_for_context(context)
            
            # Ensure at least one suitable model is loaded
            loaded_suitable = [
                m for m in context_models 
                if m in self.backends and self.backends[m].is_ready()
            ]
            
            if not loaded_suitable and context_models:
                # Load the highest priority model for this context
                best_model = context_models[0]
                if self._load_model(best_model):
                    actions.append(f"loaded:{best_model}")
            
            # Unload models not needed for current context (if memory pressure)
            if self.total_memory_used_mb > self.memory_limit_mb * 0.8:
                for model_id in list(self.backends.keys()):
                    if model_id not in context_models:
                        config = self.models.get(model_id)
                        if config and config.priority < 100:  # Don't unload guardian
                            if self._unload_model(model_id):
                                actions.append(f"unloaded:{model_id}")
            
            return actions
    
    def _get_models_for_context(self, context: ContextType) -> List[str]:
        """Get models suitable for a context, sorted by priority."""
        suitable = []
        for model_id, config in self.models.items():
            if context in config.contexts:
                suitable.append((model_id, config.priority))
        
        suitable.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in suitable]
    
    def _load_model(self, model_id: str) -> bool:
        """Load a model, creating appropriate backend."""
        if model_id not in self.models:
            return False
        
        config = self.models[model_id]
        
        # Check memory
        if self.total_memory_used_mb + config.compressed_size_mb > self.memory_limit_mb:
            if not self._free_memory(config.compressed_size_mb):
                print(f"[DynamicAIResourceManager] Cannot load {model_id}: insufficient memory")
                return False
        
        # Create backend
        if config.provider in [LLMProvider.GRANITE_MICRO, LLMProvider.GRANITE_DENSE, 
                               LLMProvider.GRANITE_HYBRID]:
            backend = GraniteBackend(config)
        elif config.provider == LLMProvider.OLLAMA:
            backend = OllamaBackend(config)
        else:
            # Default simulation backend
            backend = GraniteBackend(config)
        
        if backend.load():
            self.backends[model_id] = backend
            self.total_memory_used_mb += config.compressed_size_mb
            return True
        
        return False
    
    def _unload_model(self, model_id: str) -> bool:
        """Unload a model and free memory."""
        if model_id not in self.backends:
            return False
        
        config = self.models.get(model_id)
        if config and config.priority >= 100:
            return False  # Don't unload critical models
        
        backend = self.backends[model_id]
        if backend.unload():
            del self.backends[model_id]
            self.total_memory_used_mb -= config.compressed_size_mb if config else 0
            gc.collect()
            return True
        
        return False
    
    def _free_memory(self, required_mb: int) -> bool:
        """Free memory by unloading low-priority models."""
        freed = 0
        
        # Sort by priority (lowest first)
        sortable = [
            (mid, self.models[mid].priority)
            for mid in self.backends
            if self.models[mid].priority < 100
        ]
        sortable.sort(key=lambda x: x[1])
        
        for model_id, _ in sortable:
            if freed >= required_mb:
                break
            config = self.models.get(model_id)
            if config and self._unload_model(model_id):
                freed += config.compressed_size_mb
        
        return freed >= required_mb
    
    def generate(self, prompt: str, context: ContextType = None, 
                 preferred_model: str = None, max_tokens: int = 512) -> Dict:
        """
        Generate text using the best available model.
        
        Automatically selects model based on:
        1. Preferred model (if specified and available)
        2. Context-appropriate models
        3. Fallback chain if primary fails
        """
        if context:
            self.set_context(context)
        
        context = context or self.current_context
        
        # Determine model to use
        model_id = preferred_model
        if not model_id or model_id not in self.backends or not self.backends[model_id].is_ready():
            model_id = self._select_best_model(context)
        
        if not model_id:
            return {
                "success": False,
                "error": "No suitable model available",
                "model": None,
            }
        
        # Generate
        start_time = time.time()
        try:
            backend = self.backends[model_id]
            response = backend.generate(prompt, max_tokens)
            latency_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            self._update_metrics(model_id, success=True, latency_ms=latency_ms)
            
            return {
                "success": True,
                "response": response,
                "model": model_id,
                "latency_ms": latency_ms,
            }
            
        except Exception as e:
            self._update_metrics(model_id, success=False)
            
            # Try fallback
            config = self.models.get(model_id)
            if config and config.fallback_model:
                return self.generate(prompt, context, config.fallback_model, max_tokens)
            
            return {
                "success": False,
                "error": str(e),
                "model": model_id,
            }
    
    def _select_best_model(self, context: ContextType) -> Optional[str]:
        """Select the best available model for the context."""
        context_models = self._get_models_for_context(context)
        
        # Check loaded models first
        for model_id in context_models:
            if model_id in self.backends and self.backends[model_id].is_ready():
                return model_id
        
        # Try to load highest priority
        for model_id in context_models:
            if self._load_model(model_id):
                return model_id
        
        # Fallback to any ready model
        for model_id, backend in self.backends.items():
            if backend.is_ready():
                return model_id
        
        return None
    
    def _update_metrics(self, model_id: str, success: bool, latency_ms: float = 0):
        """Update model metrics."""
        if model_id not in self.metrics:
            self.metrics[model_id] = ModelMetrics(model_id=model_id)
        
        m = self.metrics[model_id]
        m.total_requests += 1
        if success:
            m.successful_requests += 1
            # Running average for latency
            m.avg_latency_ms = (m.avg_latency_ms * (m.successful_requests - 1) + latency_ms) / m.successful_requests
        else:
            m.failed_requests += 1
        m.last_used = datetime.now()
    
    def get_status(self) -> Dict:
        """Get comprehensive status of AI resources."""
        return {
            "memory": {
                "limit_mb": self.memory_limit_mb,
                "used_mb": self.total_memory_used_mb,
                "available_mb": self.memory_limit_mb - self.total_memory_used_mb,
            },
            "context": self.current_context.value,
            "models_loaded": list(self.backends.keys()),
            "models_ready": [m for m, b in self.backends.items() if b.is_ready()],
            "models_available": list(self.models.keys()),
            "metrics": {
                m: {
                    "total_requests": self.metrics[m].total_requests,
                    "success_rate": (self.metrics[m].successful_requests / max(1, self.metrics[m].total_requests)) * 100,
                    "avg_latency_ms": round(self.metrics[m].avg_latency_ms, 2),
                }
                for m in self.metrics
                if self.metrics[m].total_requests > 0
            },
            "ibm_granite_models": [
                m for m, c in self.models.items() 
                if c.provider in [LLMProvider.GRANITE_MICRO, LLMProvider.GRANITE_DENSE, LLMProvider.GRANITE_HYBRID]
            ],
        }
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get detailed info about a specific model."""
        if model_id not in self.models:
            return None
        
        config = self.models[model_id]
        metrics = self.metrics.get(model_id, ModelMetrics(model_id=model_id))
        
        return {
            "model_id": config.model_id,
            "name": config.name,
            "provider": config.provider.value,
            "description": config.description,
            "huggingface_id": config.huggingface_id,
            "capabilities": config.capabilities,
            "contexts": [c.value for c in config.contexts],
            "memory_mb": config.compressed_size_mb,
            "priority": config.priority,
            "is_loaded": model_id in self.backends,
            "is_ready": model_id in self.backends and self.backends[model_id].is_ready(),
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "avg_latency_ms": metrics.avg_latency_ms,
            },
        }
    
    def list_ibm_granite_models(self) -> List[Dict]:
        """List all IBM Granite models with details."""
        granite_models = []
        for model_id, config in self.models.items():
            if config.provider in [LLMProvider.GRANITE_MICRO, LLMProvider.GRANITE_DENSE, LLMProvider.GRANITE_HYBRID]:
                granite_models.append({
                    "model_id": model_id,
                    "name": config.name,
                    "description": config.description,
                    "huggingface_id": config.huggingface_id,
                    "size_mb": config.compressed_size_mb,
                    "capabilities": config.capabilities,
                    "loaded": model_id in self.backends,
                })
        return granite_models


# Singleton instance
_ai_manager: Optional[DynamicAIResourceManager] = None


def get_ai_manager() -> DynamicAIResourceManager:
    """Get the singleton AI Resource Manager instance."""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = DynamicAIResourceManager()
    return _ai_manager


if __name__ == "__main__":
    # Test the AI Resource Manager
    manager = get_ai_manager()
    
    print("\n=== AI Resource Manager Status ===")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
    
    print("\n=== IBM Granite Models ===")
    granite = manager.list_ibm_granite_models()
    print(json.dumps(granite, indent=2))
    
    print("\n=== Testing Context Switch ===")
    actions = manager.set_context(ContextType.CODING)
    print(f"Actions taken: {actions}")
    
    print("\n=== Status After Context Switch ===")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
