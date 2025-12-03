"""
VA21 Dynamic Quantization System - Adaptive AI Model Quantization

This module provides dynamic quantization (4-bit, 5-bit, 8-bit) for all AI models
based on available system memory. It enables VA21 to run efficiently on a wide
range of hardware while maintaining optimal performance.

Features:
- Dynamic quantization level selection based on system memory
- Automatic switching between 4-bit, 5-bit, and 8-bit quantization
- Memory-aware model loading and unloading
- Performance monitoring and optimization
- Support for multiple AI backends (Granite, Ollama, ONNX)

Om Vinayaka - Intelligence adapts to the vessel that holds it.
"""

import os
import sys
import json
import threading
import time
import gc
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class QuantizationLevel(Enum):
    """Quantization levels for AI models."""
    Q4 = "4-bit"    # Highest compression, lowest memory
    Q5 = "5-bit"    # Balanced compression
    Q8 = "8-bit"    # Standard quantization
    FP16 = "fp16"   # Half precision (for high-memory systems)
    FP32 = "fp32"   # Full precision (development only)


@dataclass
class QuantizationConfig:
    """Configuration for a quantization level."""
    level: QuantizationLevel
    memory_multiplier: float  # Relative to FP32 size
    quality_score: float      # 0-1, higher is better
    min_ram_gb: float         # Minimum RAM to use this level
    max_ram_gb: float         # Maximum RAM (use lower quantization above)
    description: str


@dataclass
class ModelQuantizationState:
    """Current quantization state of a model."""
    model_id: str
    current_level: QuantizationLevel
    base_size_mb: int          # Size at FP32
    current_size_mb: int       # Size at current quantization
    quality_score: float
    loaded: bool
    last_updated: datetime


class DynamicQuantizationSystem:
    """
    VA21 Dynamic Quantization System
    
    Automatically selects the optimal quantization level for AI models based on:
    - Available system memory
    - Model requirements
    - Performance/quality tradeoffs
    - Current system load
    
    Quantization Levels:
    - 4-bit: ~25% of FP32 size, good for very low memory (<8GB)
    - 5-bit: ~31% of FP32 size, balanced for moderate memory (8-12GB)
    - 8-bit: ~50% of FP32 size, high quality for good memory (12-16GB)
    - FP16: ~50% of FP32 size, highest quality for high memory (>16GB)
    
    The system monitors memory pressure and can dynamically re-quantize models
    to maintain optimal performance.
    """
    
    # Quantization configurations
    QUANTIZATION_CONFIGS = {
        QuantizationLevel.Q4: QuantizationConfig(
            level=QuantizationLevel.Q4,
            memory_multiplier=0.25,
            quality_score=0.80,
            min_ram_gb=4.0,
            max_ram_gb=8.0,
            description="4-bit quantization - Maximum compression for low memory systems"
        ),
        QuantizationLevel.Q5: QuantizationConfig(
            level=QuantizationLevel.Q5,
            memory_multiplier=0.31,
            quality_score=0.88,
            min_ram_gb=6.0,
            max_ram_gb=12.0,
            description="5-bit quantization - Balanced compression and quality"
        ),
        QuantizationLevel.Q8: QuantizationConfig(
            level=QuantizationLevel.Q8,
            memory_multiplier=0.50,
            quality_score=0.95,
            min_ram_gb=8.0,
            max_ram_gb=16.0,
            description="8-bit quantization - High quality for modern systems"
        ),
        QuantizationLevel.FP16: QuantizationConfig(
            level=QuantizationLevel.FP16,
            memory_multiplier=0.50,
            quality_score=0.99,
            min_ram_gb=12.0,
            max_ram_gb=32.0,
            description="Half precision - Near-full quality for high memory systems"
        ),
        QuantizationLevel.FP32: QuantizationConfig(
            level=QuantizationLevel.FP32,
            memory_multiplier=1.0,
            quality_score=1.0,
            min_ram_gb=24.0,
            max_ram_gb=999.0,
            description="Full precision - Development and testing only"
        ),
    }
    
    # Memory thresholds for quantization selection (in GB)
    MEMORY_THRESHOLDS = {
        4: QuantizationLevel.Q4,
        6: QuantizationLevel.Q4,
        8: QuantizationLevel.Q5,
        10: QuantizationLevel.Q5,
        12: QuantizationLevel.Q8,
        16: QuantizationLevel.Q8,
        24: QuantizationLevel.FP16,
        32: QuantizationLevel.FP16,
    }
    
    def __init__(self, data_dir: str = "data/quantization"):
        """Initialize the Dynamic Quantization System."""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # System state
        self.total_ram_gb = self._get_total_ram_gb()
        self.available_ram_gb = self._get_available_ram_gb()
        
        # Determine default quantization level
        self.default_level = self._determine_default_level()
        self.current_level = self.default_level
        
        # Model states
        self.model_states: Dict[str, ModelQuantizationState] = {}
        
        # Memory management
        self.memory_budget_gb = min(self.available_ram_gb * 0.7, self.total_ram_gb * 0.8)
        self.memory_used_gb = 0.0
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Metrics
        self.metrics = {
            'level_changes': 0,
            'models_quantized': 0,
            'memory_saved_mb': 0,
            'quality_score_avg': 0.0,
        }
        
        # Load saved state
        self._load_state()
        
        print(f"[DynamicQuantization] Initialized")
        print(f"[DynamicQuantization] Total RAM: {self.total_ram_gb:.1f}GB")
        print(f"[DynamicQuantization] Available RAM: {self.available_ram_gb:.1f}GB")
        print(f"[DynamicQuantization] Default Level: {self.default_level.value}")
        print(f"[DynamicQuantization] Memory Budget: {self.memory_budget_gb:.1f}GB")
    
    def _get_total_ram_gb(self) -> float:
        """Get total system RAM in GB."""
        if PSUTIL_AVAILABLE:
            return psutil.virtual_memory().total / (1024 ** 3)
        return 8.0  # Default assumption
    
    def _get_available_ram_gb(self) -> float:
        """Get available system RAM in GB."""
        if PSUTIL_AVAILABLE:
            return psutil.virtual_memory().available / (1024 ** 3)
        return 4.0  # Default assumption
    
    def _determine_default_level(self) -> QuantizationLevel:
        """Determine the default quantization level based on system RAM."""
        ram_gb = self.total_ram_gb
        
        # Find the appropriate level
        for threshold, level in sorted(self.MEMORY_THRESHOLDS.items(), reverse=True):
            if ram_gb >= threshold:
                return level
        
        # Very low memory - use 4-bit
        return QuantizationLevel.Q4
    
    def get_optimal_level(self, model_size_mb: int = None) -> QuantizationLevel:
        """
        Get the optimal quantization level based on current conditions.
        
        Args:
            model_size_mb: Optional model size to consider
            
        Returns:
            Optimal QuantizationLevel
        """
        with self._lock:
            # Update available memory
            self.available_ram_gb = self._get_available_ram_gb()
            
            # Calculate remaining budget
            remaining_budget_gb = self.memory_budget_gb - self.memory_used_gb
            
            # If a specific model size is provided, check if it fits
            if model_size_mb:
                model_size_gb = model_size_mb / 1024
                
                # Try each level from highest quality to lowest
                for level in [QuantizationLevel.FP16, QuantizationLevel.Q8, 
                             QuantizationLevel.Q5, QuantizationLevel.Q4]:
                    config = self.QUANTIZATION_CONFIGS[level]
                    quantized_size_gb = model_size_gb * config.memory_multiplier
                    
                    if quantized_size_gb <= remaining_budget_gb:
                        # Also check against system limits
                        if self.total_ram_gb >= config.min_ram_gb:
                            return level
                
                # Cannot fit - return lowest
                return QuantizationLevel.Q4
            
            # No specific model - return default based on memory
            return self.default_level
    
    def quantize_model(self, model_id: str, base_size_mb: int,
                       preferred_level: QuantizationLevel = None) -> ModelQuantizationState:
        """
        Quantize a model to the optimal level.
        
        Args:
            model_id: Unique model identifier
            base_size_mb: Model size at FP32
            preferred_level: Optional preferred quantization level
            
        Returns:
            ModelQuantizationState with quantization details
        """
        with self._lock:
            # Determine optimal level
            level = preferred_level or self.get_optimal_level(base_size_mb)
            config = self.QUANTIZATION_CONFIGS[level]
            
            # Calculate quantized size
            quantized_size_mb = int(base_size_mb * config.memory_multiplier)
            
            # Create state
            state = ModelQuantizationState(
                model_id=model_id,
                current_level=level,
                base_size_mb=base_size_mb,
                current_size_mb=quantized_size_mb,
                quality_score=config.quality_score,
                loaded=False,
                last_updated=datetime.now()
            )
            
            # Update tracking
            self.model_states[model_id] = state
            self.metrics['models_quantized'] += 1
            self.metrics['memory_saved_mb'] += (base_size_mb - quantized_size_mb)
            
            # Update average quality score
            total_quality = sum(s.quality_score for s in self.model_states.values())
            self.metrics['quality_score_avg'] = total_quality / len(self.model_states)
            
            self._save_state()
            
            print(f"[DynamicQuantization] Quantized {model_id}: {level.value}")
            print(f"[DynamicQuantization] Size: {base_size_mb}MB -> {quantized_size_mb}MB")
            
            return state
    
    def mark_model_loaded(self, model_id: str) -> bool:
        """Mark a model as loaded and update memory tracking."""
        with self._lock:
            if model_id not in self.model_states:
                return False
            
            state = self.model_states[model_id]
            if not state.loaded:
                state.loaded = True
                self.memory_used_gb += state.current_size_mb / 1024
            
            return True
    
    def mark_model_unloaded(self, model_id: str) -> bool:
        """Mark a model as unloaded and update memory tracking."""
        with self._lock:
            if model_id not in self.model_states:
                return False
            
            state = self.model_states[model_id]
            if state.loaded:
                state.loaded = False
                self.memory_used_gb -= state.current_size_mb / 1024
                self.memory_used_gb = max(0, self.memory_used_gb)  # Safety
            
            return True
    
    def requantize_model(self, model_id: str, new_level: QuantizationLevel) -> Optional[ModelQuantizationState]:
        """
        Re-quantize a model to a different level.
        
        This may be needed when memory pressure changes.
        """
        with self._lock:
            if model_id not in self.model_states:
                return None
            
            old_state = self.model_states[model_id]
            was_loaded = old_state.loaded
            
            if was_loaded:
                self.mark_model_unloaded(model_id)
            
            # Re-quantize
            new_state = self.quantize_model(
                model_id,
                old_state.base_size_mb,
                new_level
            )
            
            if was_loaded:
                self.mark_model_loaded(model_id)
            
            self.metrics['level_changes'] += 1
            
            return new_state
    
    def adapt_to_memory_pressure(self) -> List[str]:
        """
        Adapt quantization levels based on current memory pressure.
        
        Returns list of models that were re-quantized.
        """
        with self._lock:
            self.available_ram_gb = self._get_available_ram_gb()
            changes = []
            
            # Check if we're under memory pressure
            if self.available_ram_gb < 1.0:  # Less than 1GB available
                print("[DynamicQuantization] Memory pressure detected!")
                
                # Find loaded models that can be downgraded
                for model_id, state in self.model_states.items():
                    if state.loaded:
                        # Try to downgrade
                        if state.current_level == QuantizationLevel.FP16:
                            self.requantize_model(model_id, QuantizationLevel.Q8)
                            changes.append(model_id)
                        elif state.current_level == QuantizationLevel.Q8:
                            self.requantize_model(model_id, QuantizationLevel.Q5)
                            changes.append(model_id)
                        elif state.current_level == QuantizationLevel.Q5:
                            self.requantize_model(model_id, QuantizationLevel.Q4)
                            changes.append(model_id)
                        
                        # Check if pressure is relieved
                        self.available_ram_gb = self._get_available_ram_gb()
                        if self.available_ram_gb >= 2.0:
                            break
            
            return changes
    
    def get_quantization_info(self, model_id: str) -> Optional[Dict]:
        """Get quantization information for a model."""
        if model_id not in self.model_states:
            return None
        
        state = self.model_states[model_id]
        config = self.QUANTIZATION_CONFIGS[state.current_level]
        
        return {
            'model_id': model_id,
            'level': state.current_level.value,
            'base_size_mb': state.base_size_mb,
            'current_size_mb': state.current_size_mb,
            'compression_ratio': f"{(1 - config.memory_multiplier) * 100:.0f}%",
            'quality_score': f"{state.quality_score * 100:.0f}%",
            'loaded': state.loaded,
            'description': config.description,
        }
    
    def get_system_status(self) -> Dict:
        """Get current system and quantization status."""
        self.available_ram_gb = self._get_available_ram_gb()
        
        return {
            'system': {
                'total_ram_gb': round(self.total_ram_gb, 1),
                'available_ram_gb': round(self.available_ram_gb, 1),
                'memory_budget_gb': round(self.memory_budget_gb, 1),
                'memory_used_gb': round(self.memory_used_gb, 1),
            },
            'quantization': {
                'default_level': self.default_level.value,
                'current_level': self.current_level.value,
                'models_tracked': len(self.model_states),
                'models_loaded': len([s for s in self.model_states.values() if s.loaded]),
            },
            'metrics': self.metrics,
            'levels_available': {
                level.value: {
                    'memory_multiplier': config.memory_multiplier,
                    'quality_score': config.quality_score,
                    'description': config.description,
                }
                for level, config in self.QUANTIZATION_CONFIGS.items()
            },
        }
    
    def get_recommendation(self) -> Dict:
        """Get quantization recommendation based on current state."""
        self.available_ram_gb = self._get_available_ram_gb()
        
        optimal = self.get_optimal_level()
        config = self.QUANTIZATION_CONFIGS[optimal]
        
        return {
            'recommended_level': optimal.value,
            'reason': self._get_recommendation_reason(optimal),
            'expected_quality': f"{config.quality_score * 100:.0f}%",
            'memory_efficiency': f"{(1 - config.memory_multiplier) * 100:.0f}% reduction",
            'alternative': self._get_alternative(optimal),
        }
    
    def _get_recommendation_reason(self, level: QuantizationLevel) -> str:
        """Get human-readable reason for recommendation."""
        if level == QuantizationLevel.Q4:
            return f"4-bit quantization recommended due to limited RAM ({self.total_ram_gb:.1f}GB). Maximum memory efficiency."
        elif level == QuantizationLevel.Q5:
            return f"5-bit quantization provides good balance for your system ({self.total_ram_gb:.1f}GB RAM)."
        elif level == QuantizationLevel.Q8:
            return f"8-bit quantization recommended for your RAM capacity ({self.total_ram_gb:.1f}GB). Good quality."
        elif level == QuantizationLevel.FP16:
            return f"Half precision available with your abundant RAM ({self.total_ram_gb:.1f}GB). Near-optimal quality."
        else:
            return f"Full precision available for development ({self.total_ram_gb:.1f}GB RAM)."
    
    def _get_alternative(self, current: QuantizationLevel) -> Optional[Dict]:
        """Get alternative quantization option."""
        alternatives = {
            QuantizationLevel.Q4: QuantizationLevel.Q5,
            QuantizationLevel.Q5: QuantizationLevel.Q8,
            QuantizationLevel.Q8: QuantizationLevel.Q5,
            QuantizationLevel.FP16: QuantizationLevel.Q8,
        }
        
        alt = alternatives.get(current)
        if alt:
            config = self.QUANTIZATION_CONFIGS[alt]
            return {
                'level': alt.value,
                'trade_off': 'Higher quality but more memory' if config.quality_score > self.QUANTIZATION_CONFIGS[current].quality_score else 'Lower memory but slightly reduced quality'
            }
        return None
    
    def _save_state(self):
        """Save current state to disk."""
        try:
            state_file = os.path.join(self.data_dir, "quantization_state.json")
            state = {
                'default_level': self.default_level.value,
                'current_level': self.current_level.value,
                'metrics': self.metrics,
                'model_states': {
                    model_id: {
                        'model_id': s.model_id,
                        'current_level': s.current_level.value,
                        'base_size_mb': s.base_size_mb,
                        'current_size_mb': s.current_size_mb,
                        'quality_score': s.quality_score,
                        'loaded': s.loaded,
                        'last_updated': s.last_updated.isoformat(),
                    }
                    for model_id, s in self.model_states.items()
                },
                'saved_at': datetime.now().isoformat(),
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"[DynamicQuantization] Error saving state: {e}")
    
    def _load_state(self):
        """Load saved state from disk."""
        try:
            state_file = os.path.join(self.data_dir, "quantization_state.json")
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    
                    self.metrics = state.get('metrics', self.metrics)
                    
                    # Restore model states (but mark as unloaded)
                    for model_id, ms in state.get('model_states', {}).items():
                        level = QuantizationLevel(ms['current_level'])
                        self.model_states[model_id] = ModelQuantizationState(
                            model_id=ms['model_id'],
                            current_level=level,
                            base_size_mb=ms['base_size_mb'],
                            current_size_mb=ms['current_size_mb'],
                            quality_score=ms['quality_score'],
                            loaded=False,  # Mark as unloaded on restart
                            last_updated=datetime.fromisoformat(ms['last_updated'])
                        )
        except Exception as e:
            print(f"[DynamicQuantization] Error loading state: {e}")


# =========================================================================
# SINGLETON
# =========================================================================

_quantization_system: Optional[DynamicQuantizationSystem] = None


def get_quantization_system() -> DynamicQuantizationSystem:
    """Get the Dynamic Quantization System singleton instance."""
    global _quantization_system
    if _quantization_system is None:
        _quantization_system = DynamicQuantizationSystem()
    return _quantization_system


if __name__ == "__main__":
    # Test the system
    print("\n=== Dynamic Quantization System Test ===")
    
    system = get_quantization_system()
    
    print("\n--- System Status ---")
    print(json.dumps(system.get_system_status(), indent=2))
    
    print("\n--- Recommendation ---")
    print(json.dumps(system.get_recommendation(), indent=2))
    
    print("\n--- Quantizing Test Models ---")
    
    # Test with different model sizes
    test_models = [
        ("granite-4.0-micro", 3072),
        ("granite-4.0-dense-8b", 8192),
        ("guardian-ai", 768),
    ]
    
    for model_id, size_mb in test_models:
        state = system.quantize_model(model_id, size_mb)
        info = system.get_quantization_info(model_id)
        print(f"\n{model_id}:")
        print(json.dumps(info, indent=2))
    
    print("\n--- Final Status ---")
    print(json.dumps(system.get_system_status(), indent=2))
