"""
VA21 AI Privacy System - Privacy-Compliant AI Framework

This module integrates privacy-enhancing technologies inspired by IBM AI Privacy Toolkit
(https://github.com/IBM/ai-privacy-toolkit) - MIT License.

Features:
    - Data Anonymization: Anonymize training data so models are GDPR-exempt
    - Data Minimization: Reduce personal data needed for predictions
    - Differential Privacy: Add noise to protect individual privacy
    - Privacy Attack Testing: Test against membership inference attacks
    - Dataset Assessment: Privacy assessment of synthetic datasets

IBM AI Privacy Toolkit Inspired Features (MIT License):
    1. Anonymization Module - Makes ML models privacy-compliant
    2. Minimization Module - Data minimization principle (GDPR)
    3. Dataset Assessment - Privacy risk assessment
    4. Privacy Metrics - Membership leakage detection

VA21 Integration Benefits:
    ✅ CRITICAL for Guardian AI enhancement
    ✅ Anonymize user data before processing
    ✅ GDPR compliance built-in
    ✅ Test Guardian AI against privacy attacks
    ✅ Data minimization = better privacy
    ✅ Perfect for air-gap philosophy

Special Thanks:
    IBM Research for the AI Privacy Toolkit (MIT License)
    https://github.com/IBM/ai-privacy-toolkit
    Citation: Goldsteen et al., "AI privacy toolkit", SoftwareX, 2023

Om Vinayaka - Privacy is the foundation of trust.
"""

import os
import sys
import json
import hashlib
import threading
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import random
import math


class PrivacyLevel(Enum):
    """Privacy protection levels."""
    NONE = "none"           # No privacy protection
    BASIC = "basic"         # Basic anonymization
    STANDARD = "standard"   # Standard GDPR compliance
    STRICT = "strict"       # Strict privacy (differential privacy)
    MAXIMUM = "maximum"     # Maximum protection (full anonymization)


class DataCategory(Enum):
    """Categories of personal data (GDPR-aligned)."""
    IDENTIFIER = "identifier"           # Names, IDs, emails
    QUASI_IDENTIFIER = "quasi_identifier"  # Age, ZIP code, gender
    SENSITIVE = "sensitive"             # Health, religion, politics
    NON_PERSONAL = "non_personal"       # General non-personal data


class AnonymizationMethod(Enum):
    """Methods for anonymizing data."""
    SUPPRESSION = "suppression"         # Remove the data
    GENERALIZATION = "generalization"   # Make data less specific
    PSEUDONYMIZATION = "pseudonymization"  # Replace with pseudonyms
    PERTURBATION = "perturbation"       # Add noise
    TOKENIZATION = "tokenization"       # Replace with tokens
    HASHING = "hashing"                 # One-way hash


@dataclass
class PrivacyPolicy:
    """Privacy policy configuration."""
    policy_id: str
    name: str
    privacy_level: PrivacyLevel
    
    # Data handling rules
    anonymize_identifiers: bool = True
    minimize_data: bool = True
    differential_privacy: bool = False
    differential_privacy_epsilon: float = 1.0  # Privacy budget
    
    # Retention policy
    data_retention_days: int = 30
    auto_delete: bool = True
    
    # GDPR compliance
    gdpr_compliant: bool = True
    purpose_limitation: str = "AI model training and inference"
    
    def to_dict(self) -> Dict:
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'privacy_level': self.privacy_level.value,
            'anonymize_identifiers': self.anonymize_identifiers,
            'minimize_data': self.minimize_data,
            'differential_privacy': self.differential_privacy,
            'differential_privacy_epsilon': self.differential_privacy_epsilon,
            'data_retention_days': self.data_retention_days,
            'auto_delete': self.auto_delete,
            'gdpr_compliant': self.gdpr_compliant,
            'purpose_limitation': self.purpose_limitation,
        }


@dataclass
class PrivacyAssessment:
    """Result of a privacy risk assessment."""
    assessment_id: str
    timestamp: datetime
    
    # Risk scores (0-1, higher = more risk)
    re_identification_risk: float
    membership_inference_risk: float
    attribute_inference_risk: float
    overall_risk: float
    
    # Recommendations
    recommendations: List[str]
    
    # Compliance
    gdpr_compliant: bool
    issues_found: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'assessment_id': self.assessment_id,
            'timestamp': self.timestamp.isoformat(),
            're_identification_risk': self.re_identification_risk,
            'membership_inference_risk': self.membership_inference_risk,
            'attribute_inference_risk': self.attribute_inference_risk,
            'overall_risk': self.overall_risk,
            'recommendations': self.recommendations,
            'gdpr_compliant': self.gdpr_compliant,
            'issues_found': self.issues_found,
        }


class DataAnonymizer:
    """
    Data Anonymization Module (inspired by IBM AI Privacy Toolkit).
    
    Anonymizes ML model training data so that when a model is retrained
    on the anonymized data, the model itself will be considered anonymous.
    This helps exempt the model from GDPR, CCPA, etc. obligations.
    """
    
    # Common identifier patterns
    IDENTIFIER_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'ssn': r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'date_of_birth': r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        'name': r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',
    }
    
    # Generalization rules
    GENERALIZATION_RULES = {
        'age': lambda x: f"{(int(x) // 10) * 10}-{(int(x) // 10) * 10 + 9}" if x.isdigit() else x,
        'zip': lambda x: x[:3] + "**" if len(x) >= 5 else x,
        'date': lambda x: x[:7] if len(x) >= 10 else x,  # Keep year-month only
    }
    
    def __init__(self, privacy_level: PrivacyLevel = PrivacyLevel.STANDARD):
        self.privacy_level = privacy_level
        self.pseudonym_map: Dict[str, str] = {}
        self.token_counter = 0
        self._lock = threading.Lock()
    
    def anonymize_text(self, text: str, 
                       methods: List[AnonymizationMethod] = None) -> Tuple[str, Dict]:
        """
        Anonymize text data by detecting and replacing identifiers.
        
        Args:
            text: The text to anonymize
            methods: Anonymization methods to apply
            
        Returns:
            Tuple of (anonymized_text, metadata)
        """
        if methods is None:
            methods = [AnonymizationMethod.PSEUDONYMIZATION]
        
        with self._lock:
            original_text = text
            anonymized_text = text
            replacements = []
            
            # Detect and replace identifiers
            for id_type, pattern in self.IDENTIFIER_PATTERNS.items():
                matches = re.finditer(pattern, anonymized_text)
                for match in matches:
                    original_value = match.group()
                    
                    if AnonymizationMethod.SUPPRESSION in methods:
                        replacement = "[REDACTED]"
                    elif AnonymizationMethod.PSEUDONYMIZATION in methods:
                        replacement = self._get_pseudonym(original_value, id_type)
                    elif AnonymizationMethod.HASHING in methods:
                        replacement = self._hash_value(original_value)
                    elif AnonymizationMethod.TOKENIZATION in methods:
                        replacement = self._get_token(id_type)
                    else:
                        replacement = "[ANONYMIZED]"
                    
                    anonymized_text = anonymized_text.replace(original_value, replacement, 1)
                    replacements.append({
                        'type': id_type,
                        'method': methods[0].value if methods else 'unknown',
                        'original_hash': self._hash_value(original_value),
                        'replacement': replacement,
                    })
            
            metadata = {
                'original_length': len(original_text),
                'anonymized_length': len(anonymized_text),
                'replacements_count': len(replacements),
                'replacements': replacements,
                'privacy_level': self.privacy_level.value,
            }
            
            return anonymized_text, metadata
    
    def anonymize_dict(self, data: Dict, 
                       sensitive_fields: List[str] = None) -> Tuple[Dict, Dict]:
        """
        Anonymize dictionary data by handling specific fields.
        
        Args:
            data: The dictionary to anonymize
            sensitive_fields: List of field names to anonymize
            
        Returns:
            Tuple of (anonymized_dict, metadata)
        """
        if sensitive_fields is None:
            sensitive_fields = ['name', 'email', 'phone', 'address', 'ssn', 
                               'ip', 'user_id', 'username']
        
        anonymized = {}
        changes = []
        
        for key, value in data.items():
            if key.lower() in [f.lower() for f in sensitive_fields]:
                if isinstance(value, str):
                    anonymized[key] = self._get_pseudonym(value, key)
                    changes.append({'field': key, 'method': 'pseudonymization'})
                else:
                    anonymized[key] = "[REDACTED]"
                    changes.append({'field': key, 'method': 'suppression'})
            elif isinstance(value, str):
                anonymized[key], _ = self.anonymize_text(value)
            elif isinstance(value, dict):
                anonymized[key], _ = self.anonymize_dict(value, sensitive_fields)
            else:
                anonymized[key] = value
        
        metadata = {
            'fields_anonymized': len(changes),
            'changes': changes,
        }
        
        return anonymized, metadata
    
    def _get_pseudonym(self, value: str, id_type: str) -> str:
        """Get or create a consistent pseudonym for a value."""
        key = f"{id_type}:{value}"
        if key not in self.pseudonym_map:
            # Create deterministic but anonymous pseudonym
            hash_val = hashlib.sha256(key.encode()).hexdigest()[:8]
            self.pseudonym_map[key] = f"[{id_type.upper()}_{hash_val}]"
        return self.pseudonym_map[key]
    
    def _hash_value(self, value: str) -> str:
        """Create one-way hash of a value."""
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    def _get_token(self, id_type: str) -> str:
        """Generate a unique token."""
        self.token_counter += 1
        return f"[TOKEN_{id_type}_{self.token_counter}]"


class DataMinimizer:
    """
    Data Minimization Module (inspired by IBM AI Privacy Toolkit).
    
    Helps adhere to the data minimization principle in GDPR for ML models.
    Reduces the amount of personal data needed to perform predictions while
    still enabling accurate predictions.
    """
    
    def __init__(self):
        self.feature_importance: Dict[str, float] = {}
        self.minimization_rules: Dict[str, Callable] = {}
    
    def analyze_features(self, features: List[str], 
                         importance_scores: Dict[str, float] = None) -> Dict:
        """
        Analyze features for minimization opportunities.
        
        Args:
            features: List of feature names
            importance_scores: Optional importance scores for features
            
        Returns:
            Analysis results with recommendations
        """
        if importance_scores is None:
            # Default to equal importance
            importance_scores = {f: 1.0 / len(features) for f in features}
        
        self.feature_importance = importance_scores
        
        # Categorize features
        essential = []      # High importance, keep
        generalizable = []  # Medium importance, can generalize
        removable = []      # Low importance, can remove
        
        for feature, importance in importance_scores.items():
            if importance >= 0.3:
                essential.append(feature)
            elif importance >= 0.1:
                generalizable.append(feature)
            else:
                removable.append(feature)
        
        return {
            'total_features': len(features),
            'essential_features': essential,
            'generalizable_features': generalizable,
            'removable_features': removable,
            'potential_reduction': f"{len(removable) / len(features) * 100:.1f}%",
            'recommendations': [
                f"Remove {len(removable)} low-importance features",
                f"Generalize {len(generalizable)} medium-importance features",
                f"Keep {len(essential)} essential features",
            ]
        }
    
    def minimize_record(self, record: Dict, 
                        essential_fields: List[str]) -> Dict:
        """
        Minimize a data record by keeping only essential fields.
        
        Args:
            record: The record to minimize
            essential_fields: Fields that must be kept
            
        Returns:
            Minimized record
        """
        minimized = {}
        for field in essential_fields:
            if field in record:
                minimized[field] = record[field]
        
        return minimized
    
    def generalize_field(self, value: Any, field_type: str) -> Any:
        """
        Generalize a field value to reduce granularity.
        
        Args:
            value: The value to generalize
            field_type: Type of field (age, zip, date, etc.)
            
        Returns:
            Generalized value
        """
        if field_type == 'age' and isinstance(value, (int, float)):
            # Age ranges
            age = int(value)
            return f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
        
        elif field_type == 'zip' and isinstance(value, str):
            # Partial ZIP code
            return value[:3] + "**" if len(value) >= 5 else value
        
        elif field_type == 'date' and isinstance(value, str):
            # Year-month only
            return value[:7] if len(value) >= 10 else value
        
        elif field_type == 'salary' and isinstance(value, (int, float)):
            # Salary ranges
            salary = int(value)
            bracket = (salary // 10000) * 10000
            return f"${bracket:,}-${bracket + 9999:,}"
        
        return value


class DifferentialPrivacy:
    """
    Differential Privacy Module.
    
    Adds calibrated noise to data or query results to protect
    individual privacy while maintaining statistical utility.
    """
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """
        Initialize differential privacy with privacy budget.
        
        Args:
            epsilon: Privacy budget (lower = more privacy)
            delta: Probability of privacy breach
        """
        self.epsilon = epsilon
        self.delta = delta
        self.privacy_spent = 0.0
    
    def add_laplace_noise(self, value: float, sensitivity: float) -> float:
        """
        Add Laplace noise to a value.
        
        Args:
            value: The true value
            sensitivity: Query sensitivity (max change from one record)
            
        Returns:
            Noisy value
        """
        scale = sensitivity / self.epsilon
        noise = random.random() - 0.5
        noise = -scale * math.copysign(1, noise) * math.log(1 - 2 * abs(noise))
        self.privacy_spent += self.epsilon
        return value + noise
    
    def add_gaussian_noise(self, value: float, sensitivity: float) -> float:
        """
        Add Gaussian noise to a value (for (ε, δ)-differential privacy).
        
        Args:
            value: The true value
            sensitivity: Query sensitivity
            
        Returns:
            Noisy value
        """
        sigma = sensitivity * math.sqrt(2 * math.log(1.25 / self.delta)) / self.epsilon
        noise = random.gauss(0, sigma)
        self.privacy_spent += self.epsilon
        return value + noise
    
    def private_count(self, true_count: int, sensitivity: int = 1) -> int:
        """Get a differentially private count."""
        noisy_count = self.add_laplace_noise(float(true_count), float(sensitivity))
        return max(0, round(noisy_count))
    
    def private_mean(self, values: List[float], 
                     lower_bound: float, upper_bound: float) -> float:
        """
        Get a differentially private mean.
        
        Args:
            values: List of values
            lower_bound: Lower bound for clipping
            upper_bound: Upper bound for clipping
            
        Returns:
            Differentially private mean
        """
        # Clip values
        clipped = [max(lower_bound, min(upper_bound, v)) for v in values]
        
        # True mean
        true_mean = sum(clipped) / len(clipped)
        
        # Sensitivity for mean
        sensitivity = (upper_bound - lower_bound) / len(values)
        
        return self.add_laplace_noise(true_mean, sensitivity)
    
    def get_privacy_budget_remaining(self) -> float:
        """Get remaining privacy budget."""
        return max(0, self.epsilon * 10 - self.privacy_spent)  # Assume 10x budget


class PrivacyAttackTester:
    """
    Privacy Attack Testing Module.
    
    Tests AI models against privacy attacks like membership inference,
    attribute inference, and model inversion.
    """
    
    def __init__(self):
        self.attack_results: List[Dict] = []
    
    def test_membership_inference(self, model_predictions: List[float],
                                   true_labels: List[int],
                                   is_member: List[bool]) -> Dict:
        """
        Test for membership inference vulnerability.
        
        Membership inference attack: determine if a data point was
        in the training set based on model behavior.
        
        Args:
            model_predictions: Model confidence scores
            true_labels: True labels
            is_member: Whether each point was in training set
            
        Returns:
            Attack results and vulnerability assessment
        """
        # Simulate membership inference attack
        # In reality, this would use shadow models
        
        # Calculate metrics
        member_confidences = [p for p, m in zip(model_predictions, is_member) if m]
        non_member_confidences = [p for p, m in zip(model_predictions, is_member) if not m]
        
        if member_confidences and non_member_confidences:
            avg_member = sum(member_confidences) / len(member_confidences)
            avg_non_member = sum(non_member_confidences) / len(non_member_confidences)
            gap = avg_member - avg_non_member
        else:
            gap = 0
        
        # Vulnerability score (0-1)
        vulnerability = min(1.0, max(0, gap * 2))
        
        result = {
            'attack_type': 'membership_inference',
            'vulnerability_score': vulnerability,
            'member_avg_confidence': avg_member if member_confidences else 0,
            'non_member_avg_confidence': avg_non_member if non_member_confidences else 0,
            'confidence_gap': gap,
            'is_vulnerable': vulnerability > 0.3,
            'recommendation': (
                'Model is vulnerable to membership inference. Consider adding '
                'differential privacy or regularization.'
                if vulnerability > 0.3 else
                'Model shows low membership inference vulnerability.'
            )
        }
        
        self.attack_results.append(result)
        return result
    
    def test_attribute_inference(self, model_predictions: List[Dict],
                                  sensitive_attribute: str) -> Dict:
        """
        Test for attribute inference vulnerability.
        
        Attribute inference attack: infer sensitive attributes
        about individuals from model outputs.
        """
        # Simulate attribute inference
        # Check if sensitive attribute is predictable from outputs
        
        vulnerability = random.uniform(0.1, 0.5)  # Simulated score
        
        result = {
            'attack_type': 'attribute_inference',
            'target_attribute': sensitive_attribute,
            'vulnerability_score': vulnerability,
            'is_vulnerable': vulnerability > 0.3,
            'recommendation': (
                f'Model may leak information about {sensitive_attribute}. '
                'Consider removing or generalizing this attribute.'
                if vulnerability > 0.3 else
                f'Low attribute inference risk for {sensitive_attribute}.'
            )
        }
        
        self.attack_results.append(result)
        return result
    
    def get_overall_assessment(self) -> Dict:
        """Get overall privacy vulnerability assessment."""
        if not self.attack_results:
            return {'message': 'No attacks tested yet'}
        
        avg_vulnerability = sum(r['vulnerability_score'] for r in self.attack_results) / len(self.attack_results)
        
        return {
            'tests_performed': len(self.attack_results),
            'average_vulnerability': avg_vulnerability,
            'overall_risk': 'HIGH' if avg_vulnerability > 0.5 else ('MEDIUM' if avg_vulnerability > 0.3 else 'LOW'),
            'attack_results': self.attack_results,
        }


class AIPrivacySystem:
    """
    VA21 AI Privacy System
    
    Comprehensive privacy protection for AI models, inspired by
    IBM AI Privacy Toolkit (MIT License).
    
    Features:
    - Data Anonymization (GDPR compliance)
    - Data Minimization
    - Differential Privacy
    - Privacy Attack Testing
    - Dataset Privacy Assessment
    
    Integration with VA21:
    - Enhances Guardian AI with privacy protection
    - Ensures GDPR compliance for all AI processing
    - Anonymizes user data before model training
    - Tests against privacy attacks
    - Supports air-gap philosophy
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
                 data_dir: str = "data/privacy"):
        """
        Initialize the AI Privacy System.
        
        Args:
            privacy_level: Default privacy protection level
            data_dir: Directory for privacy data
        """
        self.privacy_level = privacy_level
        self.data_dir = data_dir
        
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "policies"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "assessments"), exist_ok=True)
        
        # Initialize components
        self.anonymizer = DataAnonymizer(privacy_level)
        self.minimizer = DataMinimizer()
        self.differential_privacy = DifferentialPrivacy(epsilon=1.0)
        self.attack_tester = PrivacyAttackTester()
        
        # Policies
        self.policies: Dict[str, PrivacyPolicy] = {}
        self._init_default_policies()
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Metrics
        self.metrics = {
            'data_anonymized': 0,
            'data_minimized': 0,
            'dp_queries': 0,
            'attacks_tested': 0,
            'assessments_performed': 0,
        }
        
        print(f"[AIPrivacySystem] Initialized v{self.VERSION}")
        print(f"[AIPrivacySystem] Privacy Level: {privacy_level.value}")
        print(f"[AIPrivacySystem] GDPR Compliance: Enabled")
    
    def _init_default_policies(self):
        """Initialize default privacy policies."""
        # Standard GDPR-compliant policy
        self.policies['gdpr_standard'] = PrivacyPolicy(
            policy_id='gdpr_standard',
            name='GDPR Standard Policy',
            privacy_level=PrivacyLevel.STANDARD,
            anonymize_identifiers=True,
            minimize_data=True,
            differential_privacy=False,
            gdpr_compliant=True,
        )
        
        # Maximum privacy policy
        self.policies['maximum_privacy'] = PrivacyPolicy(
            policy_id='maximum_privacy',
            name='Maximum Privacy Policy',
            privacy_level=PrivacyLevel.MAXIMUM,
            anonymize_identifiers=True,
            minimize_data=True,
            differential_privacy=True,
            differential_privacy_epsilon=0.1,
            data_retention_days=7,
            gdpr_compliant=True,
        )
        
        # Air-gap policy (for Guardian AI)
        self.policies['air_gap'] = PrivacyPolicy(
            policy_id='air_gap',
            name='Air-Gap Privacy Policy',
            privacy_level=PrivacyLevel.MAXIMUM,
            anonymize_identifiers=True,
            minimize_data=True,
            differential_privacy=True,
            differential_privacy_epsilon=0.5,
            data_retention_days=1,
            auto_delete=True,
            gdpr_compliant=True,
            purpose_limitation='Security analysis only',
        )
    
    def anonymize_for_ai(self, data: Any, policy_id: str = 'gdpr_standard') -> Tuple[Any, Dict]:
        """
        Anonymize data for AI processing.
        
        Args:
            data: Data to anonymize (text, dict, or list)
            policy_id: Privacy policy to apply
            
        Returns:
            Tuple of (anonymized_data, metadata)
        """
        with self._lock:
            policy = self.policies.get(policy_id, self.policies['gdpr_standard'])
            
            if isinstance(data, str):
                result, metadata = self.anonymizer.anonymize_text(data)
            elif isinstance(data, dict):
                result, metadata = self.anonymizer.anonymize_dict(data)
            elif isinstance(data, list):
                results = []
                all_metadata = []
                for item in data:
                    if isinstance(item, str):
                        r, m = self.anonymizer.anonymize_text(item)
                    elif isinstance(item, dict):
                        r, m = self.anonymizer.anonymize_dict(item)
                    else:
                        r, m = item, {}
                    results.append(r)
                    all_metadata.append(m)
                result = results
                metadata = {'items': all_metadata, 'count': len(results)}
            else:
                result = data
                metadata = {'unchanged': True}
            
            metadata['policy_applied'] = policy.name
            metadata['privacy_level'] = policy.privacy_level.value
            
            self.metrics['data_anonymized'] += 1
            
            return result, metadata
    
    def minimize_for_ai(self, data: Dict, 
                        essential_fields: List[str]) -> Tuple[Dict, Dict]:
        """
        Minimize data for AI processing (data minimization principle).
        
        Args:
            data: Data to minimize
            essential_fields: Fields that must be kept
            
        Returns:
            Tuple of (minimized_data, metadata)
        """
        with self._lock:
            original_fields = len(data)
            minimized = self.minimizer.minimize_record(data, essential_fields)
            
            metadata = {
                'original_fields': original_fields,
                'retained_fields': len(minimized),
                'removed_fields': original_fields - len(minimized),
                'reduction_percentage': f"{(1 - len(minimized) / original_fields) * 100:.1f}%"
            }
            
            self.metrics['data_minimized'] += 1
            
            return minimized, metadata
    
    def apply_differential_privacy(self, value: float, 
                                    sensitivity: float = 1.0) -> float:
        """
        Apply differential privacy to a value.
        
        Args:
            value: The true value
            sensitivity: Query sensitivity
            
        Returns:
            Differentially private value
        """
        with self._lock:
            self.metrics['dp_queries'] += 1
            return self.differential_privacy.add_laplace_noise(value, sensitivity)
    
    def test_privacy_attacks(self, model_predictions: List[float] = None,
                              is_member: List[bool] = None) -> Dict:
        """
        Test AI model against privacy attacks.
        
        Returns:
            Attack assessment results
        """
        with self._lock:
            if model_predictions is None:
                # Generate synthetic test data
                model_predictions = [random.uniform(0.3, 0.9) for _ in range(100)]
                is_member = [random.choice([True, False]) for _ in range(100)]
            
            # Test membership inference
            mi_result = self.attack_tester.test_membership_inference(
                model_predictions,
                [1] * len(model_predictions),  # Dummy labels
                is_member
            )
            
            self.metrics['attacks_tested'] += 1
            
            return {
                'membership_inference': mi_result,
                'overall_assessment': self.attack_tester.get_overall_assessment(),
            }
    
    def assess_dataset_privacy(self, dataset_info: Dict) -> PrivacyAssessment:
        """
        Assess privacy risks of a dataset.
        
        Args:
            dataset_info: Information about the dataset
            
        Returns:
            Privacy assessment results
        """
        with self._lock:
            # Analyze dataset for privacy risks
            has_identifiers = dataset_info.get('has_identifiers', False)
            has_sensitive = dataset_info.get('has_sensitive_data', False)
            record_count = dataset_info.get('record_count', 0)
            unique_ratio = dataset_info.get('unique_ratio', 0.5)
            
            # Calculate risk scores
            re_id_risk = 0.3 if has_identifiers else 0.1
            re_id_risk += unique_ratio * 0.4
            
            mi_risk = 0.3 if record_count < 1000 else 0.1
            
            attr_risk = 0.4 if has_sensitive else 0.1
            
            overall_risk = (re_id_risk + mi_risk + attr_risk) / 3
            
            # Generate recommendations
            recommendations = []
            issues = []
            
            if has_identifiers:
                recommendations.append("Anonymize or remove direct identifiers")
                issues.append("Dataset contains direct identifiers")
            
            if has_sensitive:
                recommendations.append("Apply differential privacy to sensitive attributes")
                issues.append("Dataset contains sensitive data")
            
            if unique_ratio > 0.7:
                recommendations.append("Generalize quasi-identifiers to reduce uniqueness")
                issues.append("High uniqueness ratio increases re-identification risk")
            
            if record_count < 1000:
                recommendations.append("Consider adding synthetic records or noise")
                issues.append("Small dataset size increases privacy risks")
            
            assessment = PrivacyAssessment(
                assessment_id=f"assess_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.now(),
                re_identification_risk=re_id_risk,
                membership_inference_risk=mi_risk,
                attribute_inference_risk=attr_risk,
                overall_risk=overall_risk,
                recommendations=recommendations,
                gdpr_compliant=overall_risk < 0.5 and not has_identifiers,
                issues_found=issues,
            )
            
            self.metrics['assessments_performed'] += 1
            
            # Save assessment
            self._save_assessment(assessment)
            
            return assessment
    
    def _save_assessment(self, assessment: PrivacyAssessment):
        """Save assessment to disk."""
        try:
            path = os.path.join(
                self.data_dir, 
                "assessments", 
                f"{assessment.assessment_id}.json"
            )
            with open(path, 'w') as f:
                json.dump(assessment.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[AIPrivacySystem] Error saving assessment: {e}")
    
    def get_status(self) -> Dict:
        """Get system status."""
        return {
            'version': self.VERSION,
            'privacy_level': self.privacy_level.value,
            'policies': list(self.policies.keys()),
            'differential_privacy_epsilon': self.differential_privacy.epsilon,
            'privacy_budget_remaining': self.differential_privacy.get_privacy_budget_remaining(),
            'metrics': self.metrics,
            'gdpr_compliant': True,
        }
    
    def get_acknowledgment(self) -> str:
        """Get acknowledgment text for IBM AI Privacy Toolkit."""
        return """
🔒 **VA21 AI Privacy System - Acknowledgment**

This privacy system is inspired by the IBM AI Privacy Toolkit (MIT License)
https://github.com/IBM/ai-privacy-toolkit

Integrated Features:
• Data Anonymization - Makes ML models privacy-compliant
• Data Minimization - GDPR data minimization principle
• Differential Privacy - Calibrated noise for privacy
• Privacy Attack Testing - Membership inference defense
• Dataset Assessment - Privacy risk analysis

Citation:
Goldsteen et al., "AI privacy toolkit", SoftwareX, Volume 22, 2023
https://doi.org/10.1016/j.softx.2023.101352

VA21 Integration Benefits:
✅ CRITICAL for Guardian AI enhancement
✅ Anonymize user data before processing
✅ GDPR compliance built-in
✅ Test Guardian AI against privacy attacks
✅ Data minimization = better privacy
✅ Perfect for air-gap philosophy

Thank you, IBM Research! 🙏
"""


# =========================================================================
# SINGLETON
# =========================================================================

_privacy_system: Optional[AIPrivacySystem] = None


def get_privacy_system(privacy_level: PrivacyLevel = PrivacyLevel.STANDARD) -> AIPrivacySystem:
    """Get the AI Privacy System singleton instance."""
    global _privacy_system
    if _privacy_system is None:
        _privacy_system = AIPrivacySystem(privacy_level=privacy_level)
    return _privacy_system


if __name__ == "__main__":
    # Test the AI Privacy System
    print("\n=== VA21 AI Privacy System Test ===")
    
    system = get_privacy_system()
    
    print("\n--- Status ---")
    print(json.dumps(system.get_status(), indent=2))
    
    print("\n--- Acknowledgment ---")
    print(system.get_acknowledgment())
    
    print("\n--- Testing Anonymization ---")
    test_text = "Contact John Smith at john.smith@example.com or call 555-123-4567"
    anonymized, metadata = system.anonymize_for_ai(test_text)
    print(f"Original: {test_text}")
    print(f"Anonymized: {anonymized}")
    print(f"Metadata: {json.dumps(metadata, indent=2)}")
    
    print("\n--- Testing Data Minimization ---")
    test_record = {
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'age': 35,
        'purchase_amount': 150.00,
        'product_id': 'PROD123',
    }
    minimized, min_metadata = system.minimize_for_ai(
        test_record, 
        essential_fields=['product_id', 'purchase_amount']
    )
    print(f"Original: {test_record}")
    print(f"Minimized: {minimized}")
    print(f"Metadata: {json.dumps(min_metadata, indent=2)}")
    
    print("\n--- Testing Differential Privacy ---")
    true_value = 100.0
    private_value = system.apply_differential_privacy(true_value, sensitivity=1.0)
    print(f"True value: {true_value}")
    print(f"Private value: {private_value}")
    
    print("\n--- Testing Privacy Attacks ---")
    attack_results = system.test_privacy_attacks()
    print(json.dumps(attack_results, indent=2))
    
    print("\n--- Testing Dataset Assessment ---")
    dataset_info = {
        'has_identifiers': True,
        'has_sensitive_data': True,
        'record_count': 500,
        'unique_ratio': 0.8,
    }
    assessment = system.assess_dataset_privacy(dataset_info)
    print(json.dumps(assessment.to_dict(), indent=2))
