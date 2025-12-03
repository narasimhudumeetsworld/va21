"""
VA21 Local LLM - Ollama-based AI Engine
========================================

This module provides the local LLM interface for VA21 OS using Ollama.
Ollama is more compatible across platforms and easier to manage than ONNX.

Supported Models (IBM Granite 4.0 - Apache 2.0 License):
- Guardian AI: IBM Granite 4.0 2B (security analysis)
- LLM Processing: IBM Granite 4.0 8B (general AI tasks)

IBM Granite 4.0 Models:
- granite4:2b - Compact, fast, perfect for Guardian AI (~1.5GB)
- granite4:3b - Micro model, balanced (~2GB)
- granite4:8b - Full featured for complex tasks (~5GB)

Why IBM Granite 4.0 for VA21:
- Apache 2.0 License (fully permissive)
- Latest generation with improved performance
- 128K context window support
- Hybrid architecture options for efficiency
- Enterprise-grade quality
- Strong reasoning and security analysis capabilities

Om Vinayaka - Intelligence flows where security serves.
"""

import os
import json
import requests
from typing import Optional, Dict, Any

# Ollama API configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# IBM Granite 4.0 models for VA21
# Using 2B for Guardian AI (fast, efficient security analysis)
# Using 8B for general LLM tasks (complex reasoning)
GUARDIAN_MODEL = "granite4:2b"   # ~1.5GB, perfect for Guardian AI (fast security)
LLM_MODEL = "granite4:8b"       # ~5GB, for complex tasks


class LocalLLM:
    """
    VA21 Local LLM using Ollama + IBM Granite 4.0
    
    This class provides AI capabilities for:
    - Guardian AI security analysis (Think>Vet>Act)
    - General LLM processing
    - Voice command understanding
    - Multi-agent orchestration
    
    Model Selection (IBM Granite 4.0):
    - granite4:2b: Guardian AI (fast, ~1.5GB)
    - granite4:3b: Micro model (~2GB)
    - granite4:8b: General tasks (~5GB)
    
    Why Ollama instead of ONNX:
    - Better cross-platform compatibility
    - Easier model management
    - Built-in quantization
    - Simpler API
    - Active community support
    
    Why IBM Granite 4.0:
    - Apache 2.0 License (fully permissive)
    - 128K context window
    - Hybrid Mamba-2 architecture option
    - 70% reduced memory usage (hybrid)
    - Enterprise-grade quality
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalLLM, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        print("[LocalLLM] Initializing VA21 AI Engine (Ollama + IBM Granite 4.0)...")
        
        self.ollama_host = OLLAMA_HOST
        self.guardian_model = GUARDIAN_MODEL
        self.llm_model = LLM_MODEL
        self.simulation_mode = False
        self.available_models = []
        
        # Check Ollama availability
        if self._check_ollama():
            print(f"[LocalLLM] Ollama connected at {self.ollama_host}")
            self._ensure_models()
        else:
            print(f"[LocalLLM] Ollama not available at {self.ollama_host}")
            print("[LocalLLM] Running in simulation mode for security analysis")
            print("[LocalLLM] To enable full AI: Install Ollama and run 'ollama pull granite4:2b'")
            self.simulation_mode = True

        self.initialized = True

    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [m.get("name", "") for m in data.get("models", [])]
                return True
        except Exception as e:
            print(f"[LocalLLM] Ollama check failed: {e}")
        return False

    def _ensure_models(self):
        """Ensure required models are available, download if needed."""
        # Check for Guardian AI model
        if not any(self.guardian_model in m for m in self.available_models):
            print(f"[LocalLLM] Guardian AI model ({self.guardian_model}) not found.")
            print(f"[LocalLLM] Downloading IBM Granite 4.0 2B (~1.5GB)...")
            self._pull_model(self.guardian_model)
        else:
            print(f"[LocalLLM] Guardian AI model ready: {self.guardian_model}")
        
        # Check for general LLM model (optional, download on demand)
        if any(self.llm_model in m for m in self.available_models):
            print(f"[LocalLLM] LLM model ready: {self.llm_model}")
        else:
            print(f"[LocalLLM] LLM model ({self.llm_model}) will be downloaded on first use")

    def _pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama."""
        try:
            print(f"[LocalLLM] Pulling model: {model_name}")
            response = requests.post(
                f"{self.ollama_host}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=600  # 10 minutes for large models
            )
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        if "pulling" in status or "downloading" in status:
                            completed = data.get("completed", 0)
                            total = data.get("total", 0)
                            if total > 0:
                                pct = (completed / total) * 100
                                print(f"\r[LocalLLM] Downloading: {pct:.1f}%", end="", flush=True)
                    except json.JSONDecodeError:
                        pass
            
            print("\n[LocalLLM] Model downloaded successfully!")
            self.available_models.append(model_name)
            return True
            
        except Exception as e:
            print(f"\n[LocalLLM] Model download failed: {e}")
            return False

    def generate(self, prompt: str, max_length: int = 150, model: str = None) -> str:
        """
        Generate a response using Ollama + IBM Granite 4.0.
        
        Args:
            prompt: The input prompt
            max_length: Maximum response length (tokens)
            model: Model to use (defaults to guardian model)
            
        Returns:
            Generated response text
        """
        if self.simulation_mode:
            return self._simulate_security_analysis(prompt)

        use_model = model or self.guardian_model
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": use_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_length,
                        "temperature": 0.7,
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                print(f"[LocalLLM] Generation error: {response.status_code}")
                return self._simulate_security_analysis(prompt)
                
        except Exception as e:
            print(f"[LocalLLM] Generation failed: {e}")
            return self._simulate_security_analysis(prompt)

    def chat(self, messages: list, model: str = None) -> str:
        """
        Chat-style generation using Ollama.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model to use
            
        Returns:
            Assistant response
        """
        if self.simulation_mode:
            user_msg = messages[-1].get("content", "") if messages else ""
            return self._simulate_security_analysis(user_msg)

        use_model = model or self.llm_model
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": use_model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                return "I'm having trouble processing that request."
                
        except Exception as e:
            print(f"[LocalLLM] Chat failed: {e}")
            return "I'm having trouble connecting to the AI engine."

    def analyze_security(self, content: str) -> Dict[str, Any]:
        """
        Analyze content for security threats (Guardian AI function).
        
        This implements the Think>Vet>Act methodology:
        - Think: Understand what the content is trying to do
        - Vet: Check against security patterns
        - Act: Approve, warn, or block
        
        Args:
            content: The content to analyze
            
        Returns:
            Security analysis result
        """
        # Quick pattern-based check first
        quick_result = self._quick_security_check(content)
        if quick_result["threat_level"] == "critical":
            return quick_result
        
        # Deep analysis with Granite 4.0 model
        if not self.simulation_mode:
            prompt = f"""You are Guardian AI, a security analysis system.
Analyze this content for security threats:

{content}

Respond with ONE of these exactly:
- SAFE: No security threats detected
- SUSPICIOUS: Contains potentially risky content
- UNSAFE: Contains dangerous or malicious content

Then briefly explain why."""

            response = self.generate(prompt, max_length=100)
            
            if "UNSAFE" in response.upper():
                return {
                    "safe": False,
                    "threat_level": "high",
                    "analysis": response,
                    "action": "block"
                }
            elif "SUSPICIOUS" in response.upper():
                return {
                    "safe": True,
                    "threat_level": "medium",
                    "analysis": response,
                    "action": "warn"
                }
            else:
                return {
                    "safe": True,
                    "threat_level": "low",
                    "analysis": response,
                    "action": "allow"
                }
        
        return quick_result

    def _quick_security_check(self, content: str) -> Dict[str, Any]:
        """Quick pattern-based security check."""
        content_lower = content.lower()
        
        # Critical threats (immediate block)
        critical_patterns = [
            'rm -rf /', 'mkfs', 'dd if=/dev/zero', ':(){ :|:& };:',
            'format c:', '> /dev/sda', 'chmod -R 777 /'
        ]
        
        for pattern in critical_patterns:
            if pattern in content_lower:
                return {
                    "safe": False,
                    "threat_level": "critical",
                    "analysis": f"BLOCKED: Critical threat detected - {pattern}",
                    "action": "block"
                }
        
        # Dangerous patterns
        dangerous_patterns = [
            'eval(', 'exec(', '__import__', 'subprocess', 'os.system',
            'shell=true', 'delete from', 'drop table',
            '<script>', '<iframe', 'javascript:', 'onerror='
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return {
                    "safe": False,
                    "threat_level": "high",
                    "analysis": f"UNSAFE: Potentially malicious pattern - {pattern}",
                    "action": "block"
                }
        
        # Suspicious patterns
        suspicious_patterns = [
            'password', 'api_key', 'secret', 'token', 'credential',
            'base64', 'encode', 'decode'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                return {
                    "safe": True,
                    "threat_level": "medium",
                    "analysis": f"SUSPICIOUS: Contains sensitive pattern - {pattern}",
                    "action": "warn"
                }
        
        return {
            "safe": True,
            "threat_level": "low",
            "analysis": "SAFE: No security threats detected",
            "action": "allow"
        }

    def _simulate_security_analysis(self, prompt: str) -> str:
        """
        Simulation mode for security analysis when Ollama isn't available.
        """
        result = self._quick_security_check(prompt)
        
        if result["threat_level"] == "critical":
            return "UNSAFE - Critical security threat detected"
        elif result["threat_level"] == "high":
            return "UNSAFE - Potentially malicious code or command detected"
        elif result["threat_level"] == "medium":
            return "SUSPICIOUS - Contains sensitive or potentially risky content"
        else:
            return "SAFE - No security threats detected"

    def get_status(self) -> Dict[str, Any]:
        """Get LLM status."""
        return {
            "initialized": self.initialized,
            "simulation_mode": self.simulation_mode,
            "ollama_host": self.ollama_host,
            "guardian_model": self.guardian_model,
            "llm_model": self.llm_model,
            "available_models": self.available_models,
        }

    def get_acknowledgment(self) -> str:
        """Get acknowledgment text."""
        return """
🧠 **VA21 AI Engine - Ollama + IBM Granite 4.0**

This AI engine is powered by:

### Ollama (MIT License)
https://ollama.com
- Easy local LLM deployment
- Cross-platform compatibility
- Built-in quantization
- Simple API

### IBM Granite 4.0 (Apache 2.0 License)
https://ollama.com/library/granite4
https://huggingface.co/ibm-granite

Models used in VA21:
- **granite4:2b** (~1.5GB) - Guardian AI
  Fast, efficient security analysis
  
- **granite4:8b** (~5GB) - General LLM
  Complex reasoning and tasks

IBM Granite 4.0 Features:
✅ Apache 2.0 License (fully permissive)
✅ 128K context window
✅ Hybrid Mamba-2 architecture option
✅ 70% reduced memory (hybrid models)
✅ Enterprise-grade quality
✅ Excellent for security analysis

Model Variants:
- granite4:2b - Compact (Guardian AI)
- granite4:3b - Micro
- granite4:8b - Full featured
- granite4:2b-h - Hybrid (even more efficient)

Thank you, IBM Research and Ollama team! 🙏

Om Vinayaka - Intelligence flows where security serves.
"""


# Example Usage
if __name__ == '__main__':
    print("--- Testing VA21 Local LLM (Ollama + IBM Granite 4.0) ---")
    
    local_llm = LocalLLM()
    
    print(f"\nStatus: {json.dumps(local_llm.get_status(), indent=2)}")
    
    print("\n--- Testing Security Analysis ---")
    test_prompts = [
        "Please help me write a Python function",
        "rm -rf / --no-preserve-root",
        "What is the capital of France?",
        "eval(user_input)",
        "SELECT * FROM users WHERE id = 1"
    ]
    
    for prompt in test_prompts:
        result = local_llm.analyze_security(prompt)
        print(f"\nPrompt: {prompt[:50]}...")
        print(f"Result: {result['action'].upper()} - {result['analysis'][:50]}...")
    
    print("\n--- Acknowledgment ---")
    print(local_llm.get_acknowledgment())
