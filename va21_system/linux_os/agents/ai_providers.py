#!/usr/bin/env python3
"""
VA21 OS - AI Providers
======================

Provides abstraction for different AI backends:
1. OllamaProvider - Local AI using built-in Ollama
2. APIProvider - External APIs (OpenAI, Anthropic, etc.)

The system automatically selects the best available provider,
preferring local Ollama for privacy and offline capability.

Om Vinayaka - May wisdom flow freely.
"""

import os
import json
import time
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Ollama configuration (user-facing instance)
# These can be overridden via environment variables:
#   VA21_OLLAMA_HOST, VA21_OLLAMA_PORT, VA21_GUARDIAN_PORT

def _safe_int(value: str, default: int) -> int:
    """Safely convert string to int with default fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

DEFAULT_OLLAMA_HOST = os.environ.get("VA21_OLLAMA_HOST", "127.0.0.1")
DEFAULT_OLLAMA_PORT = _safe_int(os.environ.get("VA21_OLLAMA_PORT", "11434"), 11434)
GUARDIAN_OLLAMA_PORT = _safe_int(os.environ.get("VA21_GUARDIAN_PORT", "11435"), 11435)

# Default models for different tasks
# Can be overridden via VA21_MODEL_* environment variables
DEFAULT_MODELS = {
    'general': os.environ.get("VA21_MODEL_GENERAL", "granite3.3:2b"),
    'code': os.environ.get("VA21_MODEL_CODE", "granite-code:3b"),
    'guardian': os.environ.get("VA21_MODEL_GUARDIAN", "granite-guardian:2b"),
    'embedding': os.environ.get("VA21_MODEL_EMBEDDING", "nomic-embed-text:latest"),
}

# API endpoints for different providers
API_ENDPOINTS = {
    'openai': 'https://api.openai.com/v1/chat/completions',
    'anthropic': 'https://api.anthropic.com/v1/messages',
    'groq': 'https://api.groq.com/openai/v1/chat/completions',
    'together': 'https://api.together.xyz/v1/chat/completions',
    'openrouter': 'https://openrouter.ai/api/v1/chat/completions',
}


class ProviderType(Enum):
    """Type of AI provider."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    TOGETHER = "together"
    OPENROUTER = "openrouter"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Message:
    """A chat message."""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class CompletionResult:
    """Result from an AI completion."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    finish_reason: str = "stop"
    metadata: Dict = field(default_factory=dict)


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    provider_type: ProviderType
    host: str = DEFAULT_OLLAMA_HOST
    port: int = DEFAULT_OLLAMA_PORT
    api_key: str = ""
    model: str = ""
    timeout: int = 120
    max_retries: int = 3


# ═══════════════════════════════════════════════════════════════════════════════
# ABSTRACT BASE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    Provides a unified interface for different AI backends:
    - Local Ollama
    - OpenAI API
    - Anthropic API
    - Other compatible APIs
    """
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.is_available = False
        self._check_availability()
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """Check if the provider is available."""
        pass
    
    @abstractmethod
    def complete(self, messages: List[Message], **kwargs) -> CompletionResult:
        """Generate a completion from messages."""
        pass
    
    @abstractmethod
    def stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """Stream a completion from messages."""
        pass
    
    def get_status(self) -> Dict:
        """Get provider status."""
        return {
            'type': self.config.provider_type.value,
            'available': self.is_available,
            'model': self.config.model,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OLLAMA PROVIDER (LOCAL AI)
# ═══════════════════════════════════════════════════════════════════════════════

class OllamaProvider(AIProvider):
    """
    Local AI provider using Ollama.
    
    Ollama runs locally and provides:
    - Complete privacy (no data leaves the device)
    - Offline capability
    - Multiple model support
    - Fast inference on capable hardware
    
    VA21 OS runs two Ollama instances:
    - Port 11434: User-facing AI (Om Vinayaka, Helper AI)
    - Port 11435: Guardian AI (sandboxed, kernel-level)
    """
    
    def __init__(self, config: ProviderConfig = None, use_guardian: bool = False):
        if config is None:
            port = GUARDIAN_OLLAMA_PORT if use_guardian else DEFAULT_OLLAMA_PORT
            model = DEFAULT_MODELS['guardian'] if use_guardian else DEFAULT_MODELS['general']
            config = ProviderConfig(
                provider_type=ProviderType.OLLAMA,
                host=DEFAULT_OLLAMA_HOST,
                port=port,
                model=model
            )
        super().__init__(config)
        self.base_url = f"http://{config.host}:{config.port}"
        self.use_guardian = use_guardian
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and accessible."""
        if not REQUESTS_AVAILABLE:
            self.is_available = False
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            self.is_available = response.status_code == 200
            return self.is_available
        except Exception:
            self.is_available = False
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        if not self.is_available:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [m['name'] for m in data.get('models', [])]
        except Exception:
            pass
        return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                timeout=600  # Model pulls can take time
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def complete(self, messages: List[Message], **kwargs) -> CompletionResult:
        """Generate a completion using Ollama."""
        if not self.is_available:
            return CompletionResult(
                content="[Error: Ollama is not available]",
                model=self.config.model,
                provider="ollama",
                finish_reason="error"
            )
        
        # Convert messages to Ollama format
        ollama_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        model = kwargs.get('model', self.config.model)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": ollama_messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get('temperature', 0.7),
                        "num_predict": kwargs.get('max_tokens', 2048),
                    }
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return CompletionResult(
                    content=data.get('message', {}).get('content', ''),
                    model=model,
                    provider="ollama",
                    tokens_used=data.get('eval_count', 0) + data.get('prompt_eval_count', 0),
                    finish_reason="stop",
                    metadata={
                        'total_duration': data.get('total_duration'),
                        'load_duration': data.get('load_duration'),
                    }
                )
            else:
                return CompletionResult(
                    content=f"[Error: {response.status_code}]",
                    model=model,
                    provider="ollama",
                    finish_reason="error"
                )
        except Exception as e:
            return CompletionResult(
                content=f"[Error: {str(e)}]",
                model=model,
                provider="ollama",
                finish_reason="error"
            )
    
    def stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """Stream a completion from Ollama."""
        if not self.is_available:
            yield "[Error: Ollama is not available]"
            return
        
        ollama_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        model = kwargs.get('model', self.config.model)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": ollama_messages,
                    "stream": True,
                    "options": {
                        "temperature": kwargs.get('temperature', 0.7),
                        "num_predict": kwargs.get('max_tokens', 2048),
                    }
                },
                stream=True,
                timeout=self.config.timeout
            )
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get('message', {}).get('content', '')
                        if content:
                            yield content
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield f"[Error: {str(e)}]"
    
    def generate_embedding(self, text: str, model: str = None) -> List[float]:
        """Generate embeddings for text."""
        if not self.is_available:
            return []
        
        model = model or DEFAULT_MODELS['embedding']
        
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('embedding', [])
        except Exception:
            pass
        return []
    
    def get_status(self) -> Dict:
        """Get Ollama status."""
        status = super().get_status()
        status['base_url'] = self.base_url
        status['models'] = self.list_models() if self.is_available else []
        status['guardian_mode'] = self.use_guardian
        return status


# ═══════════════════════════════════════════════════════════════════════════════
# API PROVIDER (EXTERNAL APIS)
# ═══════════════════════════════════════════════════════════════════════════════

class APIProvider(AIProvider):
    """
    External API provider for cloud AI services.
    
    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Groq (Fast inference)
    - Together AI
    - OpenRouter (Multi-provider)
    
    API keys are stored securely and never logged.
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.endpoint = API_ENDPOINTS.get(config.provider_type.value, '')
    
    def _check_availability(self) -> bool:
        """Check if API is available (has valid key)."""
        self.is_available = bool(self.config.api_key and self.endpoint)
        return self.is_available
    
    def _get_headers(self) -> Dict:
        """Get API headers."""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config.provider_type == ProviderType.ANTHROPIC:
            headers["x-api-key"] = self.config.api_key
            headers["anthropic-version"] = "2024-01-01"
        else:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        return headers
    
    def _format_request(self, messages: List[Message], **kwargs) -> Dict:
        """Format request for the specific API."""
        formatted_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        if self.config.provider_type == ProviderType.ANTHROPIC:
            # Anthropic has different format
            system_msg = ""
            chat_msgs = []
            for m in formatted_messages:
                if m['role'] == 'system':
                    system_msg = m['content']
                else:
                    chat_msgs.append(m)
            
            return {
                "model": kwargs.get('model', self.config.model),
                "max_tokens": kwargs.get('max_tokens', 2048),
                "system": system_msg,
                "messages": chat_msgs,
            }
        else:
            # OpenAI-compatible format
            return {
                "model": kwargs.get('model', self.config.model),
                "messages": formatted_messages,
                "max_tokens": kwargs.get('max_tokens', 2048),
                "temperature": kwargs.get('temperature', 0.7),
            }
    
    def complete(self, messages: List[Message], **kwargs) -> CompletionResult:
        """Generate a completion using external API."""
        if not self.is_available:
            return CompletionResult(
                content="[Error: API not configured]",
                model=self.config.model,
                provider=self.config.provider_type.value,
                finish_reason="error"
            )
        
        if not REQUESTS_AVAILABLE:
            return CompletionResult(
                content="[Error: requests library not available]",
                model=self.config.model,
                provider=self.config.provider_type.value,
                finish_reason="error"
            )
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self._get_headers(),
                json=self._format_request(messages, **kwargs),
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response based on provider
                if self.config.provider_type == ProviderType.ANTHROPIC:
                    content = data.get('content', [{}])[0].get('text', '')
                    tokens = data.get('usage', {}).get('output_tokens', 0)
                else:
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    tokens = data.get('usage', {}).get('total_tokens', 0)
                
                return CompletionResult(
                    content=content,
                    model=self.config.model,
                    provider=self.config.provider_type.value,
                    tokens_used=tokens,
                    finish_reason="stop"
                )
            else:
                return CompletionResult(
                    content=f"[Error: {response.status_code} - {response.text[:100]}]",
                    model=self.config.model,
                    provider=self.config.provider_type.value,
                    finish_reason="error"
                )
        except Exception as e:
            return CompletionResult(
                content=f"[Error: {str(e)}]",
                model=self.config.model,
                provider=self.config.provider_type.value,
                finish_reason="error"
            )
    
    def stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """Stream a completion from external API."""
        if not self.is_available:
            yield "[Error: API not configured]"
            return
        
        if not REQUESTS_AVAILABLE:
            yield "[Error: requests library not available]"
            return
        
        request_data = self._format_request(messages, **kwargs)
        request_data['stream'] = True
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self._get_headers(),
                json=request_data,
                stream=True,
                timeout=self.config.timeout
            )
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if self.config.provider_type == ProviderType.ANTHROPIC:
                                content = data.get('delta', {}).get('text', '')
                            else:
                                content = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"[Error: {str(e)}]"


# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDER FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def get_ai_provider(
    provider_type: str = "auto",
    api_key: str = None,
    model: str = None,
    use_guardian: bool = False
) -> AIProvider:
    """
    Get the best available AI provider.
    
    Args:
        provider_type: 'auto', 'ollama', 'openai', 'anthropic', etc.
        api_key: API key for external providers
        model: Model to use
        use_guardian: Use Guardian AI Ollama instance
        
    Returns:
        Configured AIProvider instance
    
    Auto selection priority:
    1. Local Ollama (if available) - for privacy
    2. Configured external API
    3. Falls back to unavailable Ollama
    """
    
    # Check for environment variables
    if not api_key:
        api_key = os.environ.get('OPENAI_API_KEY') or \
                  os.environ.get('ANTHROPIC_API_KEY') or \
                  os.environ.get('GROQ_API_KEY')
    
    # Auto selection
    if provider_type == "auto":
        # Try Ollama first (privacy-first approach)
        ollama = OllamaProvider(use_guardian=use_guardian)
        if ollama.is_available:
            if model:
                ollama.config.model = model
            return ollama
        
        # Try external APIs if available
        for ptype in [ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.GROQ]:
            env_key = os.environ.get(f'{ptype.value.upper()}_API_KEY')
            if env_key:
                config = ProviderConfig(
                    provider_type=ptype,
                    api_key=env_key,
                    model=model or _get_default_model(ptype)
                )
                provider = APIProvider(config)
                if provider.is_available:
                    return provider
        
        # Fallback to unavailable Ollama (will show appropriate error)
        return ollama
    
    # Specific provider requested
    if provider_type == "ollama":
        return OllamaProvider(use_guardian=use_guardian)
    
    # External API provider
    try:
        ptype = ProviderType(provider_type)
        config = ProviderConfig(
            provider_type=ptype,
            api_key=api_key or "",
            model=model or _get_default_model(ptype)
        )
        return APIProvider(config)
    except ValueError:
        # Unknown provider, return Ollama
        return OllamaProvider(use_guardian=use_guardian)


def _get_default_model(provider_type: ProviderType) -> str:
    """Get default model for a provider."""
    defaults = {
        ProviderType.OPENAI: "gpt-4o-mini",
        ProviderType.ANTHROPIC: "claude-3-haiku-20240307",
        ProviderType.GROQ: "llama-3.1-8b-instant",
        ProviderType.TOGETHER: "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        ProviderType.OPENROUTER: "meta-llama/llama-3.1-8b-instruct:free",
    }
    return defaults.get(provider_type, "gpt-4o-mini")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the AI providers."""
    print("=" * 70)
    print("VA21 OS - AI Providers Test")
    print("=" * 70)
    
    # Test auto provider selection
    print("\n--- Auto Provider Selection ---")
    provider = get_ai_provider()
    print(f"Selected provider: {provider.get_status()}")
    
    # Test Ollama specifically
    print("\n--- Ollama Provider ---")
    ollama = OllamaProvider()
    print(f"Ollama available: {ollama.is_available}")
    if ollama.is_available:
        print(f"Models: {ollama.list_models()}")
        
        # Test completion
        print("\n--- Test Completion ---")
        messages = [
            Message(role="system", content="You are Om Vinayaka, a helpful assistant."),
            Message(role="user", content="What is 2+2? Answer briefly.")
        ]
        result = ollama.complete(messages)
        print(f"Response: {result.content}")
        print(f"Tokens: {result.tokens_used}")
    
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    main()
