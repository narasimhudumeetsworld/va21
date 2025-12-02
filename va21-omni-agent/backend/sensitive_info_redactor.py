"""
Sensitive Information Redaction Manager

This module provides functionality for detecting and redacting sensitive
information from research outputs to protect confidential data.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Set, Pattern, Tuple
from datetime import datetime
import hashlib
import json
import os


@dataclass
class RedactionRule:
    """Represents a redaction rule."""
    name: str
    pattern: Pattern
    replacement: str
    category: str
    severity: str  # low, medium, high, critical


class RedactionResult:
    """Result of a redaction operation."""
    
    def __init__(self, original: str, redacted: str, 
                 redactions: List[Dict], metadata: Dict = None):
        self.original = original
        self.redacted = redacted
        self.redactions = redactions
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()


class SensitiveInfoRedactor:
    """
    Manages detection and redaction of sensitive information.
    
    Features:
    - Pattern-based sensitive data detection
    - Configurable redaction rules
    - Audit logging of redactions
    - Category-based filtering
    - Hash-based consistent replacement
    """
    
    def __init__(self, config_path: str = None, log_dir: str = "data/redaction_logs"):
        self.log_dir = log_dir
        self.rules: List[RedactionRule] = []
        self.custom_patterns: Dict[str, str] = {}
        self.redaction_log: List[Dict] = []
        
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize default rules
        self._initialize_default_rules()
        
        # Load custom rules if config exists
        if config_path and os.path.exists(config_path):
            self._load_custom_rules(config_path)
    
    def _initialize_default_rules(self):
        """Initialize default redaction rules."""
        default_rules = [
            # API Keys and Tokens
            RedactionRule(
                name="api_key_generic",
                pattern=re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?'),
                replacement="[REDACTED_API_KEY]",
                category="credentials",
                severity="critical"
            ),
            RedactionRule(
                name="bearer_token",
                pattern=re.compile(r'Bearer\s+[a-zA-Z0-9_.-]+'),
                replacement="Bearer [REDACTED_TOKEN]",
                category="credentials",
                severity="critical"
            ),
            RedactionRule(
                name="jwt_token",
                pattern=re.compile(r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'),
                replacement="[REDACTED_JWT]",
                category="credentials",
                severity="critical"
            ),
            
            # AWS
            RedactionRule(
                name="aws_access_key",
                pattern=re.compile(r'(?i)(aws[_-]?access[_-]?key[_-]?id|AKIA)[a-zA-Z0-9]{16,}'),
                replacement="[REDACTED_AWS_KEY]",
                category="cloud_credentials",
                severity="critical"
            ),
            RedactionRule(
                name="aws_secret_key",
                pattern=re.compile(r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?'),
                replacement="[REDACTED_AWS_SECRET]",
                category="cloud_credentials",
                severity="critical"
            ),
            
            # Google
            RedactionRule(
                name="gcp_api_key",
                pattern=re.compile(r'AIza[a-zA-Z0-9_-]{35}'),
                replacement="[REDACTED_GCP_KEY]",
                category="cloud_credentials",
                severity="critical"
            ),
            
            # GitHub
            RedactionRule(
                name="github_token",
                pattern=re.compile(r'gh[pousr]_[a-zA-Z0-9]{36,}'),
                replacement="[REDACTED_GITHUB_TOKEN]",
                category="credentials",
                severity="critical"
            ),
            RedactionRule(
                name="github_pat",
                pattern=re.compile(r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}'),
                replacement="[REDACTED_GITHUB_PAT]",
                category="credentials",
                severity="critical"
            ),
            
            # Passwords
            RedactionRule(
                name="password_field",
                pattern=re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\',]{6,})["\']?'),
                replacement=r"\1: [REDACTED_PASSWORD]",
                category="credentials",
                severity="critical"
            ),
            
            # Private Keys
            RedactionRule(
                name="private_key",
                pattern=re.compile(r'-----BEGIN [A-Z]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z]+ PRIVATE KEY-----'),
                replacement="[REDACTED_PRIVATE_KEY]",
                category="credentials",
                severity="critical"
            ),
            RedactionRule(
                name="ssh_private_key",
                pattern=re.compile(r'-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]*?-----END OPENSSH PRIVATE KEY-----'),
                replacement="[REDACTED_SSH_KEY]",
                category="credentials",
                severity="critical"
            ),
            
            # Email Addresses
            RedactionRule(
                name="email",
                pattern=re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),
                replacement="[REDACTED_EMAIL]",
                category="pii",
                severity="medium"
            ),
            
            # IP Addresses
            RedactionRule(
                name="ip_address",
                pattern=re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'),
                replacement="[REDACTED_IP]",
                category="network",
                severity="low"
            ),
            
            # Phone Numbers
            RedactionRule(
                name="phone_number",
                pattern=re.compile(r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'),
                replacement="[REDACTED_PHONE]",
                category="pii",
                severity="medium"
            ),
            
            # Credit Card Numbers
            RedactionRule(
                name="credit_card",
                pattern=re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'),
                replacement="[REDACTED_CC]",
                category="financial",
                severity="critical"
            ),
            
            # Social Security Numbers
            RedactionRule(
                name="ssn",
                pattern=re.compile(r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b'),
                replacement="[REDACTED_SSN]",
                category="pii",
                severity="critical"
            ),
            
            # Database Connection Strings
            RedactionRule(
                name="db_connection_string",
                pattern=re.compile(r'(?i)(mongodb|mysql|postgresql|postgres|redis)://[^\s<>"\']+'),
                replacement="[REDACTED_DB_CONNECTION]",
                category="credentials",
                severity="critical"
            ),
            
            # Slack Tokens
            RedactionRule(
                name="slack_token",
                pattern=re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,48}'),
                replacement="[REDACTED_SLACK_TOKEN]",
                category="credentials",
                severity="high"
            ),
            
            # Stripe Keys
            RedactionRule(
                name="stripe_key",
                pattern=re.compile(r'(?:sk|pk)_(?:test|live)_[a-zA-Z0-9]{24,}'),
                replacement="[REDACTED_STRIPE_KEY]",
                category="credentials",
                severity="critical"
            ),
        ]
        
        self.rules.extend(default_rules)
    
    def _load_custom_rules(self, config_path: str):
        """Load custom redaction rules from config file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            for rule_data in config.get('rules', []):
                rule = RedactionRule(
                    name=rule_data['name'],
                    pattern=re.compile(rule_data['pattern']),
                    replacement=rule_data['replacement'],
                    category=rule_data.get('category', 'custom'),
                    severity=rule_data.get('severity', 'medium')
                )
                self.rules.append(rule)
        except Exception as e:
            print(f"[Redactor] Error loading custom rules: {e}")
    
    def add_rule(self, name: str, pattern: str, replacement: str,
                 category: str = "custom", severity: str = "medium"):
        """Add a custom redaction rule."""
        rule = RedactionRule(
            name=name,
            pattern=re.compile(pattern),
            replacement=replacement,
            category=category,
            severity=severity
        )
        self.rules.append(rule)
    
    def remove_rule(self, name: str):
        """Remove a redaction rule by name."""
        self.rules = [r for r in self.rules if r.name != name]
    
    def redact(self, text: str, categories: List[str] = None,
               min_severity: str = None, 
               use_consistent_replacement: bool = False) -> RedactionResult:
        """
        Redact sensitive information from text.
        
        Args:
            text: Text to redact
            categories: Only apply rules from these categories
            min_severity: Minimum severity level (low, medium, high, critical)
            use_consistent_replacement: Use hash-based consistent replacement
            
        Returns:
            RedactionResult with redacted text and metadata
        """
        severity_levels = ['low', 'medium', 'high', 'critical']
        min_level_idx = severity_levels.index(min_severity) if min_severity else 0
        
        redacted_text = text
        all_redactions = []
        
        for rule in self.rules:
            # Filter by category
            if categories and rule.category not in categories:
                continue
            
            # Filter by severity
            rule_level_idx = severity_levels.index(rule.severity)
            if rule_level_idx < min_level_idx:
                continue
            
            # Find all matches
            for match in rule.pattern.finditer(redacted_text):
                original_value = match.group(0)
                
                if use_consistent_replacement:
                    # Use hash for consistent replacement
                    hash_suffix = hashlib.sha256(original_value.encode()).hexdigest()[:8]
                    replacement = f"{rule.replacement}_{hash_suffix}"
                else:
                    replacement = rule.replacement
                
                all_redactions.append({
                    'rule': rule.name,
                    'category': rule.category,
                    'severity': rule.severity,
                    'original_length': len(original_value),
                    'start': match.start(),
                    'end': match.end()
                })
            
            # Apply redaction
            if use_consistent_replacement:
                def replace_func(m):
                    h = hashlib.sha256(m.group(0).encode()).hexdigest()[:8]
                    return f"{rule.replacement}_{h}"
                redacted_text = rule.pattern.sub(replace_func, redacted_text)
            else:
                redacted_text = rule.pattern.sub(rule.replacement, redacted_text)
        
        result = RedactionResult(
            original=text,
            redacted=redacted_text,
            redactions=all_redactions,
            metadata={
                'categories_applied': categories,
                'min_severity': min_severity,
                'total_redactions': len(all_redactions)
            }
        )
        
        # Log redaction
        self._log_redaction(result)
        
        return result
    
    def scan(self, text: str, categories: List[str] = None) -> List[Dict]:
        """
        Scan text for sensitive information without redacting.
        
        Args:
            text: Text to scan
            categories: Only scan for these categories
            
        Returns:
            List of detected sensitive items
        """
        detections = []
        
        for rule in self.rules:
            if categories and rule.category not in categories:
                continue
            
            for match in rule.pattern.finditer(text):
                detections.append({
                    'rule': rule.name,
                    'category': rule.category,
                    'severity': rule.severity,
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        
        return detections
    
    def redact_file(self, input_path: str, output_path: str = None,
                    **kwargs) -> RedactionResult:
        """
        Redact sensitive information from a file.
        
        Args:
            input_path: Path to input file
            output_path: Path for output (defaults to input_path.redacted)
            **kwargs: Additional arguments for redact()
            
        Returns:
            RedactionResult
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = self.redact(content, **kwargs)
        
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}.redacted{ext}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.redacted)
        
        result.metadata['input_path'] = input_path
        result.metadata['output_path'] = output_path
        
        return result
    
    def _log_redaction(self, result: RedactionResult):
        """Log a redaction operation."""
        log_entry = {
            'timestamp': result.timestamp,
            'redaction_count': len(result.redactions),
            'categories': list(set(r['category'] for r in result.redactions)),
            'severities': list(set(r['severity'] for r in result.redactions)),
            'metadata': result.metadata
        }
        
        self.redaction_log.append(log_entry)
        
        # Write to log file
        log_file = os.path.join(self.log_dir, 
                                f"redaction_{datetime.now().strftime('%Y%m%d')}.json")
        try:
            existing_logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    existing_logs = json.load(f)
            
            existing_logs.append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(existing_logs, f, indent=2)
        except Exception as e:
            print(f"[Redactor] Error writing log: {e}")
    
    def get_statistics(self) -> Dict:
        """Get redaction statistics."""
        if not self.redaction_log:
            return {'total_operations': 0}
        
        total_redactions = sum(entry['redaction_count'] for entry in self.redaction_log)
        all_categories = []
        all_severities = []
        
        for entry in self.redaction_log:
            all_categories.extend(entry['categories'])
            all_severities.extend(entry['severities'])
        
        category_counts = {}
        for cat in all_categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        severity_counts = {}
        for sev in all_severities:
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        return {
            'total_operations': len(self.redaction_log),
            'total_redactions': total_redactions,
            'category_distribution': category_counts,
            'severity_distribution': severity_counts
        }
    
    def export_rules(self, output_path: str):
        """Export current rules to a JSON file."""
        rules_data = []
        for rule in self.rules:
            rules_data.append({
                'name': rule.name,
                'pattern': rule.pattern.pattern,
                'replacement': rule.replacement,
                'category': rule.category,
                'severity': rule.severity
            })
        
        with open(output_path, 'w') as f:
            json.dump({'rules': rules_data}, f, indent=2)


# Example usage
if __name__ == '__main__':
    redactor = SensitiveInfoRedactor()
    
    # Test text with various sensitive information patterns
    # NOTE: These are intentionally fake/example values for testing
    test_text = """
    Here's my API configuration:
    api_key: EXAMPLE_KEY_PLACEHOLDER_12345678901234567890
    password: testpassword123
    email: user@example.com
    
    Connect to database: mongodb://user:pass@localhost:27017/testdb
    
    My AWS credentials:
    aws_access_key_id: AKIAEXAMPLEKEYID1234
    aws_secret_access_key: EXAMPLESECRETKEYEXAMPLESECRETKEY12345678
    
    GitHub token: ghp_ExampleTokenForTestingPurposesOnly1234
    """
    
    print("Original text:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    result = redactor.redact(test_text)
    
    print("Redacted text:")
    print(result.redacted)
    print("\n" + "="*50 + "\n")
    
    print("Redactions made:")
    for r in result.redactions:
        print(f"  - {r['rule']} ({r['category']}, {r['severity']})")
    
    print("\nStatistics:")
    print(redactor.get_statistics())
