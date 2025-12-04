#!/usr/bin/env python3
"""
VA21 OS - AI Helper Integration for Coding IDE
================================================

Om Vinayaka - AI assistance for your development journey.

The AI Helper provides:
- Integration with multiple AI providers (OpenAI, Anthropic, local Ollama)
- API key management with secure storage
- Context-aware code assistance
- Natural language to code translation
- Code explanation and documentation
- FARA layer integration for voice commands
- Integration with Helper AI and SearXNG

This component serves as the intelligence layer for the Coding IDE,
enabling users to describe what they want to build and get intelligent
guidance throughout the development process.

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.
"""

import os
import json
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class AIProvider(Enum):
    """Supported AI providers."""
    OLLAMA = "ollama"  # Local, no API key needed
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


@dataclass
class AIConfig:
    """Configuration for an AI provider."""
    provider: AIProvider
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    enabled: bool = True


@dataclass
class ConversationMessage:
    """A message in the conversation history."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    provider: AIProvider
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


# Default configuration path
CONFIG_PATH = os.path.expanduser("~/.va21/coding_ide/ai_config.json")
KEYS_PATH = os.path.expanduser("~/.va21/coding_ide/api_keys.enc")


class AIHelper:
    """
    VA21 Coding IDE AI Helper
    
    Provides AI-powered assistance for coding tasks:
    - Natural language to code translation
    - Code explanation and documentation
    - Architecture suggestions
    - Debug assistance
    - Code review
    
    Supports multiple AI providers with fallback capabilities.
    Integrates with FARA layer for voice-activated assistance.
    """
    
    VERSION = "1.0.0"
    
    # Default system prompts for different tasks
    SYSTEM_PROMPTS = {
        "general": """You are an expert software developer assistant in the VA21 Coding IDE. 
You help users build applications by providing clear, concise guidance and code.
Always explain your reasoning and suggest best practices.""",
        
        "code_generation": """You are a code generation expert in the VA21 Coding IDE.
When asked to generate code:
1. First understand the requirements completely
2. Ask clarifying questions if needed
3. Generate clean, well-documented code
4. Include error handling
5. Follow language-specific best practices
Always provide complete, runnable code when possible.""",
        
        "code_explanation": """You are a code explanation expert in the VA21 Coding IDE.
When explaining code:
1. Break down the code into logical sections
2. Explain what each part does in simple terms
3. Highlight important patterns and concepts
4. Note any potential issues or improvements
Be thorough but accessible to developers of all levels.""",
        
        "architecture": """You are a software architecture expert in the VA21 Coding IDE.
When discussing architecture:
1. Consider scalability, maintainability, and security
2. Suggest appropriate design patterns
3. Recommend technology choices with reasoning
4. Provide diagrams or structure descriptions
5. Consider the target platform and constraints
Focus on practical, implementable solutions.""",
        
        "debug": """You are a debugging expert in the VA21 Coding IDE.
When helping debug:
1. Analyze the error message carefully
2. Ask for relevant code context if needed
3. Identify potential causes systematically
4. Suggest solutions in order of likelihood
5. Explain why the error occurred
Be methodical and help users learn from the debugging process.""",
    }
    
    def __init__(self, config_path: str = None):
        """
        Initialize the AI Helper.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or CONFIG_PATH
        self.providers: Dict[AIProvider, AIConfig] = {}
        self.active_provider: Optional[AIProvider] = None
        self.conversation_history: List[ConversationMessage] = []
        self.max_history = 50
        
        # FARA layer integration
        self.fara_layer = None
        
        # SearXNG integration for searching documentation
        self.searxng = None
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Load configuration
        self._load_config()
        
        # Set up default Ollama (local) provider
        self._setup_default_providers()
        
        print(f"[AIHelper] Initialized v{self.VERSION}")
        if self.active_provider:
            print(f"[AIHelper] Active provider: {self.active_provider.value}")
    
    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                for provider_name, provider_config in config.get("providers", {}).items():
                    try:
                        provider = AIProvider(provider_name)
                        self.providers[provider] = AIConfig(
                            provider=provider,
                            api_key=provider_config.get("api_key"),
                            endpoint=provider_config.get("endpoint"),
                            model=provider_config.get("model", "gpt-3.5-turbo"),
                            max_tokens=provider_config.get("max_tokens", 2048),
                            temperature=provider_config.get("temperature", 0.7),
                            enabled=provider_config.get("enabled", True)
                        )
                    except ValueError:
                        continue
                
                active = config.get("active_provider")
                if active:
                    try:
                        self.active_provider = AIProvider(active)
                    except ValueError:
                        pass
            except Exception as e:
                print(f"[AIHelper] Error loading config: {e}")
    
    def _save_config(self):
        """Save configuration to file."""
        config = {
            "providers": {},
            "active_provider": self.active_provider.value if self.active_provider else None
        }
        
        for provider, provider_config in self.providers.items():
            config["providers"][provider.value] = {
                "endpoint": provider_config.endpoint,
                "model": provider_config.model,
                "max_tokens": provider_config.max_tokens,
                "temperature": provider_config.temperature,
                "enabled": provider_config.enabled,
                # Don't save API key in plain text
            }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[AIHelper] Error saving config: {e}")
    
    def _setup_default_providers(self):
        """Set up default providers."""
        # Always add Ollama as a local option (no API key needed)
        if AIProvider.OLLAMA not in self.providers:
            self.providers[AIProvider.OLLAMA] = AIConfig(
                provider=AIProvider.OLLAMA,
                endpoint="http://localhost:11434",
                model="granite3.3:2b",  # Default to Granite model for VA21
                max_tokens=2048,
                temperature=0.7,
                enabled=True
            )
        
        # Set Ollama as default if no active provider
        if not self.active_provider:
            self.active_provider = AIProvider.OLLAMA
    
    def set_api_key(self, provider: AIProvider, api_key: str) -> bool:
        """
        Set API key for a provider.
        
        Args:
            provider: The AI provider
            api_key: The API key
            
        Returns:
            True if successful
        """
        if provider not in self.providers:
            # Create new provider config
            if provider == AIProvider.OPENAI:
                self.providers[provider] = AIConfig(
                    provider=provider,
                    api_key=api_key,
                    endpoint="https://api.openai.com/v1",
                    model="gpt-3.5-turbo",
                )
            elif provider == AIProvider.ANTHROPIC:
                self.providers[provider] = AIConfig(
                    provider=provider,
                    api_key=api_key,
                    endpoint="https://api.anthropic.com/v1",
                    model="claude-3-haiku-20240307",
                )
            elif provider == AIProvider.GOOGLE:
                self.providers[provider] = AIConfig(
                    provider=provider,
                    api_key=api_key,
                    endpoint="https://generativelanguage.googleapis.com/v1beta",
                    model="gemini-pro",
                )
            else:
                return False
        else:
            self.providers[provider].api_key = api_key
        
        self._save_config()
        # Store encrypted key
        self._save_api_key(provider, api_key)
        
        print(f"[AIHelper] API key set for {provider.value}")
        return True
    
    def _save_api_key(self, provider: AIProvider, api_key: str):
        """Save API key with basic encoding (not true encryption)."""
        keys = {}
        if os.path.exists(KEYS_PATH):
            try:
                with open(KEYS_PATH, 'r') as f:
                    keys = json.load(f)
            except Exception:
                pass
        
        # Note: Base64 is for obfuscation only, not security.
        # For production use, implement proper encryption with the
        # cryptography library or use system keyring (keyring package).
        # This is a development/testing implementation.
        encoded = base64.b64encode(api_key.encode()).decode()
        keys[provider.value] = encoded
        
        os.makedirs(os.path.dirname(KEYS_PATH), exist_ok=True)
        with open(KEYS_PATH, 'w') as f:
            json.dump(keys, f)
    
    def _load_api_key(self, provider: AIProvider) -> Optional[str]:
        """Load API key for a provider."""
        if not os.path.exists(KEYS_PATH):
            return None
        
        try:
            with open(KEYS_PATH, 'r') as f:
                keys = json.load(f)
            
            encoded = keys.get(provider.value)
            if encoded:
                return base64.b64decode(encoded.encode()).decode()
        except Exception:
            pass
        
        return None
    
    def set_active_provider(self, provider: AIProvider) -> bool:
        """
        Set the active AI provider.
        
        Args:
            provider: The provider to activate
            
        Returns:
            True if successful
        """
        if provider not in self.providers:
            print(f"[AIHelper] Provider {provider.value} not configured")
            return False
        
        if not self.providers[provider].enabled:
            print(f"[AIHelper] Provider {provider.value} is disabled")
            return False
        
        # Check if API key is needed and available
        if provider != AIProvider.OLLAMA:
            api_key = self._load_api_key(provider)
            if not api_key and not self.providers[provider].api_key:
                print(f"[AIHelper] Provider {provider.value} requires an API key")
                return False
            if api_key:
                self.providers[provider].api_key = api_key
        
        self.active_provider = provider
        self._save_config()
        print(f"[AIHelper] Active provider set to: {provider.value}")
        return True
    
    def get_available_providers(self) -> List[Dict]:
        """Get list of available providers with their status."""
        providers = []
        for provider, config in self.providers.items():
            has_key = bool(config.api_key or self._load_api_key(provider))
            providers.append({
                "provider": provider.value,
                "model": config.model,
                "enabled": config.enabled,
                "has_api_key": has_key or provider == AIProvider.OLLAMA,
                "is_active": provider == self.active_provider,
                "requires_api_key": provider != AIProvider.OLLAMA,
            })
        return providers
    
    def chat(self, message: str, context: str = None, 
             task_type: str = "general") -> AIResponse:
        """
        Send a message to the AI and get a response.
        
        Args:
            message: The user's message
            context: Optional context (code, error message, etc.)
            task_type: Type of task (general, code_generation, code_explanation, etc.)
            
        Returns:
            AIResponse with the AI's response
        """
        if not self.active_provider:
            return AIResponse(
                content="No AI provider is configured. Please set up an API key or enable Ollama.",
                provider=AIProvider.OLLAMA,
                model="none",
                success=False,
                error="No active provider"
            )
        
        # Build the message with context
        full_message = message
        if context:
            full_message = f"Context:\n```\n{context}\n```\n\nQuestion/Request: {message}"
        
        # Add to conversation history
        self.conversation_history.append(ConversationMessage(
            role="user",
            content=full_message,
            metadata={"task_type": task_type}
        ))
        
        # Get system prompt for task type
        system_prompt = self.SYSTEM_PROMPTS.get(task_type, self.SYSTEM_PROMPTS["general"])
        
        # Call the appropriate provider
        config = self.providers[self.active_provider]
        
        try:
            if self.active_provider == AIProvider.OLLAMA:
                response = self._call_ollama(full_message, system_prompt, config)
            elif self.active_provider == AIProvider.OPENAI:
                response = self._call_openai(full_message, system_prompt, config)
            elif self.active_provider == AIProvider.ANTHROPIC:
                response = self._call_anthropic(full_message, system_prompt, config)
            elif self.active_provider == AIProvider.GOOGLE:
                response = self._call_google(full_message, system_prompt, config)
            else:
                response = AIResponse(
                    content="Provider not implemented",
                    provider=self.active_provider,
                    model=config.model,
                    success=False,
                    error="Provider not implemented"
                )
        except Exception as e:
            response = AIResponse(
                content=f"Error communicating with AI: {str(e)}",
                provider=self.active_provider,
                model=config.model,
                success=False,
                error=str(e)
            )
        
        # Add response to history
        if response.success:
            self.conversation_history.append(ConversationMessage(
                role="assistant",
                content=response.content,
                metadata={"provider": response.provider.value, "model": response.model}
            ))
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        return response
    
    def _call_ollama(self, message: str, system_prompt: str, 
                     config: AIConfig) -> AIResponse:
        """Call local Ollama instance."""
        import time
        start_time = time.time()
        
        if not REQUESTS_AVAILABLE:
            return AIResponse(
                content="Requests library not available for API calls.",
                provider=AIProvider.OLLAMA,
                model=config.model,
                success=False,
                error="requests not installed"
            )
        
        try:
            response = requests.post(
                f"{config.endpoint}/api/generate",
                json={
                    "model": config.model,
                    "prompt": message,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": config.temperature,
                        "num_predict": config.max_tokens,
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                latency = (time.time() - start_time) * 1000
                
                return AIResponse(
                    content=data.get("response", ""),
                    provider=AIProvider.OLLAMA,
                    model=config.model,
                    tokens_used=data.get("eval_count", 0),
                    latency_ms=latency,
                    success=True
                )
            else:
                return AIResponse(
                    content=f"Ollama returned error: {response.status_code}",
                    provider=AIProvider.OLLAMA,
                    model=config.model,
                    success=False,
                    error=f"HTTP {response.status_code}"
                )
        except requests.exceptions.ConnectionError:
            return AIResponse(
                content="Could not connect to Ollama. Make sure Ollama is running locally.",
                provider=AIProvider.OLLAMA,
                model=config.model,
                success=False,
                error="Connection refused"
            )
    
    def _call_openai(self, message: str, system_prompt: str,
                     config: AIConfig) -> AIResponse:
        """Call OpenAI API."""
        import time
        start_time = time.time()
        
        if not config.api_key:
            return AIResponse(
                content="OpenAI API key not configured.",
                provider=AIProvider.OPENAI,
                model=config.model,
                success=False,
                error="No API key"
            )
        
        try:
            response = requests.post(
                f"{config.endpoint}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                latency = (time.time() - start_time) * 1000
                
                return AIResponse(
                    content=data["choices"][0]["message"]["content"],
                    provider=AIProvider.OPENAI,
                    model=config.model,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                    latency_ms=latency,
                    success=True
                )
            else:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                return AIResponse(
                    content=f"OpenAI error: {error_msg}",
                    provider=AIProvider.OPENAI,
                    model=config.model,
                    success=False,
                    error=error_msg
                )
        except Exception as e:
            return AIResponse(
                content=f"OpenAI API error: {str(e)}",
                provider=AIProvider.OPENAI,
                model=config.model,
                success=False,
                error=str(e)
            )
    
    def _call_anthropic(self, message: str, system_prompt: str,
                        config: AIConfig) -> AIResponse:
        """Call Anthropic (Claude) API."""
        import time
        start_time = time.time()
        
        if not config.api_key:
            return AIResponse(
                content="Anthropic API key not configured.",
                provider=AIProvider.ANTHROPIC,
                model=config.model,
                success=False,
                error="No API key"
            )
        
        try:
            response = requests.post(
                f"{config.endpoint}/messages",
                headers={
                    "x-api-key": config.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model,
                    "max_tokens": config.max_tokens,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": message}
                    ]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                latency = (time.time() - start_time) * 1000
                
                content = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        content += block.get("text", "")
                
                return AIResponse(
                    content=content,
                    provider=AIProvider.ANTHROPIC,
                    model=config.model,
                    tokens_used=data.get("usage", {}).get("input_tokens", 0) + 
                               data.get("usage", {}).get("output_tokens", 0),
                    latency_ms=latency,
                    success=True
                )
            else:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                return AIResponse(
                    content=f"Anthropic error: {error_msg}",
                    provider=AIProvider.ANTHROPIC,
                    model=config.model,
                    success=False,
                    error=error_msg
                )
        except Exception as e:
            return AIResponse(
                content=f"Anthropic API error: {str(e)}",
                provider=AIProvider.ANTHROPIC,
                model=config.model,
                success=False,
                error=str(e)
            )
    
    def _call_google(self, message: str, system_prompt: str,
                     config: AIConfig) -> AIResponse:
        """Call Google (Gemini) API."""
        import time
        start_time = time.time()
        
        if not config.api_key:
            return AIResponse(
                content="Google API key not configured.",
                provider=AIProvider.GOOGLE,
                model=config.model,
                success=False,
                error="No API key"
            )
        
        try:
            full_prompt = f"{system_prompt}\n\nUser: {message}"
            
            response = requests.post(
                f"{config.endpoint}/models/{config.model}:generateContent?key={config.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [
                        {"parts": [{"text": full_prompt}]}
                    ],
                    "generationConfig": {
                        "temperature": config.temperature,
                        "maxOutputTokens": config.max_tokens
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                latency = (time.time() - start_time) * 1000
                
                content = ""
                for candidate in data.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        content += part.get("text", "")
                
                return AIResponse(
                    content=content,
                    provider=AIProvider.GOOGLE,
                    model=config.model,
                    latency_ms=latency,
                    success=True
                )
            else:
                return AIResponse(
                    content=f"Google API error: {response.status_code}",
                    provider=AIProvider.GOOGLE,
                    model=config.model,
                    success=False,
                    error=f"HTTP {response.status_code}"
                )
        except Exception as e:
            return AIResponse(
                content=f"Google API error: {str(e)}",
                provider=AIProvider.GOOGLE,
                model=config.model,
                success=False,
                error=str(e)
            )
    
    # Convenience methods for specific tasks
    
    def generate_code(self, description: str, language: str = None,
                      context: str = None) -> AIResponse:
        """
        Generate code from a description.
        
        Args:
            description: What the code should do
            language: Target programming language
            context: Optional context (existing code, requirements)
            
        Returns:
            AIResponse with generated code
        """
        prompt = description
        if language:
            prompt = f"Generate {language} code that: {description}"
        
        return self.chat(prompt, context=context, task_type="code_generation")
    
    def explain_code(self, code: str, question: str = None) -> AIResponse:
        """
        Explain what code does.
        
        Args:
            code: The code to explain
            question: Optional specific question about the code
            
        Returns:
            AIResponse with explanation
        """
        prompt = "Please explain this code in detail."
        if question:
            prompt = f"About this code: {question}"
        
        return self.chat(prompt, context=code, task_type="code_explanation")
    
    def debug_code(self, code: str, error: str = None,
                   description: str = None) -> AIResponse:
        """
        Help debug code.
        
        Args:
            code: The problematic code
            error: Error message if any
            description: Description of the problem
            
        Returns:
            AIResponse with debugging help
        """
        context = code
        if error:
            context = f"Code:\n{code}\n\nError:\n{error}"
        
        prompt = description or "Please help debug this code."
        return self.chat(prompt, context=context, task_type="debug")
    
    def suggest_architecture(self, requirements: str) -> AIResponse:
        """
        Suggest architecture for a project.
        
        Args:
            requirements: Project requirements description
            
        Returns:
            AIResponse with architecture suggestions
        """
        return self.chat(
            f"Please suggest an architecture for this project: {requirements}",
            task_type="architecture"
        )
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("[AIHelper] Conversation history cleared")
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get recent conversation history."""
        history = self.conversation_history[-limit:]
        return [
            {
                "role": msg.role,
                "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in history
        ]
    
    def get_status(self) -> Dict:
        """Get AI Helper status."""
        return {
            "version": self.VERSION,
            "active_provider": self.active_provider.value if self.active_provider else None,
            "providers_configured": len(self.providers),
            "conversation_length": len(self.conversation_history),
            "available_providers": self.get_available_providers(),
        }


# Singleton instance
_ai_helper_instance = None


def get_ai_helper(config_path: str = None) -> AIHelper:
    """Get or create the AIHelper singleton."""
    global _ai_helper_instance
    if _ai_helper_instance is None:
        _ai_helper_instance = AIHelper(config_path)
    return _ai_helper_instance


# CLI interface
def main():
    """CLI interface for testing the AI Helper."""
    helper = get_ai_helper()
    
    print("=" * 60)
    print("VA21 Coding IDE - AI Helper")
    print("=" * 60)
    print(f"\nStatus: {json.dumps(helper.get_status(), indent=2)}")
    
    print("\n" + "=" * 60)
    print("Interactive AI Chat (type 'quit' to exit)")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n> You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if not user_input:
                continue
            
            print("\n🤖 AI: ", end="")
            response = helper.chat(user_input)
            
            if response.success:
                print(response.content)
                print(f"\n[{response.provider.value}/{response.model}, {response.latency_ms:.0f}ms]")
            else:
                print(f"Error: {response.error}")
                print(f"Message: {response.content}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
