"""
VA21 AI Runtime Configuration - Alpha Release
===============================================

Om Vinayaka - First Alpha Release

This module defines the runtime configuration for VA21's AI systems:

1. Guardian AI (Security Core)
   - Runtime: ONNX Runtime (Microsoft)
   - License: MIT License
   - Always active for security analysis
   - Runs locally, no external API calls
   
2. Helper AI (User Assistant)
   - Runtime: Ollama or Hugging Face Transformers
   - License: MIT (Ollama) / Apache 2.0 (Transformers)
   - Supports IBM Granite, Llama, Phi models
   - Permissive open-source runtimes

Why This Architecture:
- IBM Granite and many advanced models don't have official ONNX versions
- ONNX is ideal for the Guardian AI due to:
  - Fast inference for real-time security checks
  - Small model size for always-on operation
  - Microsoft's enterprise-grade runtime
- Ollama/Transformers are ideal for Helper AI due to:
  - Wide model support (IBM Granite, Llama, Phi, etc.)
  - Permissive open-source licenses
  - Easy model switching and updates
  - Community-driven development

Acknowledgments:
- IBM Research for Granite models (Apache License 2.0)
  https://huggingface.co/collections/ibm-granite/granite-40-language-models
- Microsoft for ONNX Runtime (MIT License)
  https://github.com/microsoft/onnxruntime
- Ollama Project (MIT License)
  https://github.com/ollama/ollama
- Hugging Face for Transformers (Apache License 2.0)
  https://github.com/huggingface/transformers
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import os
import json


class RuntimeType(Enum):
    """Supported AI runtime types."""
    ONNX = "onnx"                    # Microsoft ONNX Runtime
    OLLAMA = "ollama"                # Ollama local inference
    TRANSFORMERS = "transformers"   # Hugging Face Transformers
    API = "api"                      # External API (Gemini, etc.)


class AISystemType(Enum):
    """Types of AI systems in VA21."""
    GUARDIAN = "guardian"   # Security analysis (ONNX only)
    HELPER = "helper"       # User assistance (Ollama/Transformers)
    FARA = "fara"          # UI automation agent


@dataclass
class RuntimeConfig:
    """Configuration for an AI runtime."""
    runtime_type: RuntimeType
    name: str
    description: str
    license: str
    license_url: str
    is_local: bool
    supported_models: List[str]
    min_memory_mb: int
    recommended_memory_mb: int
    config: Dict = field(default_factory=dict)


# Pre-defined runtime configurations
RUNTIME_CONFIGS: Dict[RuntimeType, RuntimeConfig] = {
    RuntimeType.ONNX: RuntimeConfig(
        runtime_type=RuntimeType.ONNX,
        name="ONNX Runtime",
        description="Microsoft's cross-platform inference accelerator for ML models",
        license="MIT License",
        license_url="https://github.com/microsoft/onnxruntime/blob/main/LICENSE",
        is_local=True,
        supported_models=[
            "Guardian AI Security Core",
            "Phi-3 Mini ONNX",
            "Custom ONNX models"
        ],
        min_memory_mb=384,
        recommended_memory_mb=768,
        config={
            "provider": "CPUExecutionProvider",
            "intra_op_num_threads": 4
        }
    ),
    RuntimeType.OLLAMA: RuntimeConfig(
        runtime_type=RuntimeType.OLLAMA,
        name="Ollama",
        description="Run large language models locally with ease",
        license="MIT License",
        license_url="https://github.com/ollama/ollama/blob/main/LICENSE",
        is_local=True,
        supported_models=[
            "llama3",
            "llama3:8b",
            "codellama",
            "phi3",
            "phi3:mini",
            "mistral",
            "gemma2"
        ],
        min_memory_mb=1024,
        recommended_memory_mb=4096,
        config={
            "base_url": "http://localhost:11434",
            "timeout": 60
        }
    ),
    RuntimeType.TRANSFORMERS: RuntimeConfig(
        runtime_type=RuntimeType.TRANSFORMERS,
        name="Hugging Face Transformers",
        description="State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX",
        license="Apache License 2.0",
        license_url="https://github.com/huggingface/transformers/blob/main/LICENSE",
        is_local=True,
        supported_models=[
            "ibm-granite/granite-4.0-tiny-preview",
            "ibm-granite/granite-4.0-dense-2b-preview",
            "ibm-granite/granite-4.0-dense-8b-preview",
            "ibm-granite/granite-4.0-moe-preview",
            "microsoft/phi-3-mini-4k-instruct",
            "meta-llama/Llama-3-8b-hf"
        ],
        min_memory_mb=2048,
        recommended_memory_mb=8192,
        config={
            "device": "auto",
            "torch_dtype": "auto",
            "load_in_8bit": True
        }
    )
}


@dataclass
class AISystemRuntimeSpec:
    """Specification for an AI system's runtime configuration."""
    system_type: AISystemType
    primary_runtime: RuntimeType
    fallback_runtimes: List[RuntimeType]
    required_capabilities: List[str]
    description: str


# AI System to Runtime Mapping
AI_SYSTEM_SPECS: Dict[AISystemType, AISystemRuntimeSpec] = {
    AISystemType.GUARDIAN: AISystemRuntimeSpec(
        system_type=AISystemType.GUARDIAN,
        primary_runtime=RuntimeType.ONNX,
        fallback_runtimes=[],  # No fallback - Guardian must use ONNX
        required_capabilities=["security_analysis", "threat_detection", "code_analysis"],
        description="Guardian AI runs exclusively on ONNX Runtime for fast, reliable security analysis"
    ),
    AISystemType.HELPER: AISystemRuntimeSpec(
        system_type=AISystemType.HELPER,
        primary_runtime=RuntimeType.OLLAMA,
        fallback_runtimes=[RuntimeType.TRANSFORMERS, RuntimeType.API],
        required_capabilities=["chat", "reasoning", "assistance"],
        description="Helper AI runs on Ollama/Transformers for wide model support"
    ),
    AISystemType.FARA: AISystemRuntimeSpec(
        system_type=AISystemType.FARA,
        primary_runtime=RuntimeType.OLLAMA,
        fallback_runtimes=[RuntimeType.TRANSFORMERS],
        required_capabilities=["ui_automation", "screenshot_analysis", "action_planning"],
        description="FARA agent uses Ollama/Transformers for UI automation tasks"
    )
}


class AIRuntimeManager:
    """
    VA21 AI Runtime Manager
    
    Manages the runtime configuration and selection for all AI systems.
    
    Om Vinayaka - First Alpha Release
    """
    
    VERSION = "1.0.0-alpha.1"
    CODENAME = "Vinayaka"
    
    def __init__(self, config_path: str = "data/ai_runtime"):
        self.config_path = config_path
        self.config_file = os.path.join(config_path, "runtime_config.json")
        
        # Active runtimes
        self.active_runtimes: Dict[AISystemType, RuntimeType] = {}
        
        # Runtime health status
        self.runtime_status: Dict[RuntimeType, Dict] = {}
        
        os.makedirs(config_path, exist_ok=True)
        self._initialize()
    
    def _initialize(self):
        """Initialize runtime configuration."""
        # Set default runtime assignments
        for system_type, spec in AI_SYSTEM_SPECS.items():
            self.active_runtimes[system_type] = spec.primary_runtime
        
        # Check runtime availability
        self._check_runtime_availability()
        
        print(f"[AIRuntimeManager] Initialized v{self.VERSION} ({self.CODENAME})")
        print(f"[AIRuntimeManager] Guardian AI: {self.active_runtimes[AISystemType.GUARDIAN].value}")
        print(f"[AIRuntimeManager] Helper AI: {self.active_runtimes[AISystemType.HELPER].value}")
    
    def _check_runtime_availability(self):
        """Check which runtimes are available on this system."""
        # Check ONNX
        try:
            import onnxruntime
            self.runtime_status[RuntimeType.ONNX] = {
                "available": True,
                "version": onnxruntime.__version__,
                "providers": onnxruntime.get_available_providers()
            }
        except ImportError:
            self.runtime_status[RuntimeType.ONNX] = {
                "available": False,
                "error": "onnxruntime not installed"
            }
        
        # Check Ollama
        # Security: Only check for 'ollama' executable, don't run arbitrary commands
        try:
            import subprocess
            import shutil
            
            # First verify ollama exists in PATH using shutil.which (safe)
            ollama_path = shutil.which('ollama')
            if ollama_path is None:
                self.runtime_status[RuntimeType.OLLAMA] = {
                    "available": False,
                    "error": "ollama not found in PATH"
                }
            else:
                # Ollama found, run version check with explicit path
                result = subprocess.run(
                    [ollama_path, '--version'],
                    capture_output=True, text=True, timeout=5,
                    env={"PATH": ""}  # Clear PATH to prevent injection
                )
                self.runtime_status[RuntimeType.OLLAMA] = {
                    "available": result.returncode == 0,
                    "version": result.stdout.strip() if result.returncode == 0 else None,
                    "error": result.stderr if result.returncode != 0 else None,
                    "path": ollama_path
                }
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            self.runtime_status[RuntimeType.OLLAMA] = {
                "available": False,
                "error": f"ollama check failed: {str(e)}"
            }
        
        # Check Transformers
        try:
            import transformers
            self.runtime_status[RuntimeType.TRANSFORMERS] = {
                "available": True,
                "version": transformers.__version__
            }
        except ImportError:
            self.runtime_status[RuntimeType.TRANSFORMERS] = {
                "available": False,
                "error": "transformers not installed"
            }
    
    def get_runtime_for_system(self, system_type: AISystemType) -> RuntimeType:
        """Get the active runtime for an AI system."""
        return self.active_runtimes.get(system_type, RuntimeType.OLLAMA)
    
    def get_runtime_config(self, runtime_type: RuntimeType) -> RuntimeConfig:
        """Get the configuration for a runtime type."""
        return RUNTIME_CONFIGS.get(runtime_type)
    
    def get_system_spec(self, system_type: AISystemType) -> AISystemRuntimeSpec:
        """Get the specification for an AI system."""
        return AI_SYSTEM_SPECS.get(system_type)
    
    def is_runtime_available(self, runtime_type: RuntimeType) -> bool:
        """Check if a runtime is available."""
        status = self.runtime_status.get(runtime_type, {})
        return status.get("available", False)
    
    def set_runtime_for_system(self, system_type: AISystemType, 
                                runtime_type: RuntimeType) -> Dict[str, Any]:
        """
        Set the runtime for an AI system.
        
        Note: Guardian AI cannot be changed from ONNX.
        """
        spec = AI_SYSTEM_SPECS.get(system_type)
        
        if not spec:
            return {
                "success": False,
                "error": f"Unknown system type: {system_type.value}"
            }
        
        # Guardian AI must use ONNX
        if system_type == AISystemType.GUARDIAN and runtime_type != RuntimeType.ONNX:
            return {
                "success": False,
                "error": "Guardian AI must use ONNX Runtime for security"
            }
        
        # Check if runtime is available
        if not self.is_runtime_available(runtime_type):
            return {
                "success": False,
                "error": f"Runtime {runtime_type.value} is not available"
            }
        
        # Check if runtime supports required capabilities
        if runtime_type not in [spec.primary_runtime] + spec.fallback_runtimes:
            return {
                "success": False,
                "error": f"Runtime {runtime_type.value} does not support {system_type.value}"
            }
        
        self.active_runtimes[system_type] = runtime_type
        return {
            "success": True,
            "system": system_type.value,
            "runtime": runtime_type.value
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive runtime status."""
        return {
            "version": self.VERSION,
            "codename": self.CODENAME,
            "active_runtimes": {
                s.value: r.value for s, r in self.active_runtimes.items()
            },
            "runtime_availability": {
                r.value: self.runtime_status.get(r, {})
                for r in RuntimeType
            },
            "system_specs": {
                s.value: {
                    "primary_runtime": spec.primary_runtime.value,
                    "fallback_runtimes": [r.value for r in spec.fallback_runtimes],
                    "description": spec.description
                }
                for s, spec in AI_SYSTEM_SPECS.items()
            }
        }
    
    def get_runtime_info_markdown(self) -> str:
        """Get runtime information as markdown for documentation."""
        status = self.get_status()
        
        md = f"""# VA21 AI Runtime Configuration

**Version**: {status['version']} ({status['codename']})

## Om Vinayaka - First Alpha Release

### Runtime Architecture

| AI System | Runtime | Status |
|-----------|---------|--------|
| Guardian AI | ONNX Runtime | {self._status_emoji(RuntimeType.ONNX)} |
| Helper AI | Ollama/Transformers | {self._status_emoji(RuntimeType.OLLAMA)} |
| FARA Agent | Ollama/Transformers | {self._status_emoji(RuntimeType.OLLAMA)} |

### Guardian AI (Security Core)
- **Runtime**: ONNX Runtime (Microsoft)
- **License**: MIT License
- **Purpose**: Security analysis and threat detection
- **Status**: Always active, cannot be changed

### Helper AI (User Assistant)
- **Runtime**: Ollama or Hugging Face Transformers
- **License**: MIT / Apache 2.0
- **Supported Models**:
  - IBM Granite 4.0 (via Transformers)
  - Llama 3 (via Ollama)
  - Phi-3 (via Ollama)
  - Code Llama (via Ollama)

### Why This Architecture?
- IBM Granite and many advanced models don't have official ONNX versions
- ONNX is ideal for Guardian AI: fast inference, small model size
- Ollama/Transformers ideal for Helper AI: wide model support

### Acknowledgments
- IBM Research for Granite models (Apache License 2.0)
- Microsoft for ONNX Runtime (MIT License)
- Ollama Project (MIT License)
- Hugging Face for Transformers (Apache License 2.0)
"""
        return md
    
    def _status_emoji(self, runtime_type: RuntimeType) -> str:
        """Get status emoji for a runtime."""
        if self.is_runtime_available(runtime_type):
            return "🟢 Available"
        return "🔴 Not Available"


# Singleton instance
_runtime_manager: Optional[AIRuntimeManager] = None


def get_runtime_manager() -> AIRuntimeManager:
    """Get the singleton AI Runtime Manager instance."""
    global _runtime_manager
    if _runtime_manager is None:
        _runtime_manager = AIRuntimeManager()
    return _runtime_manager


if __name__ == "__main__":
    # Test the runtime manager
    manager = get_runtime_manager()
    
    print("\n=== AI Runtime Status ===")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
    
    print("\n=== Runtime Documentation ===")
    print(manager.get_runtime_info_markdown())
