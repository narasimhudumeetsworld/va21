#!/usr/bin/env python3
"""
VA21 Research OS - Security Expert Toolkit
============================================

Advanced security tools for security researchers, penetration testers,
and cybersecurity professionals.

Features:
- Vulnerability Scanner Integration
- Network Analysis Tools
- Forensic Analysis
- Malware Analysis Sandbox
- Password Security Tools
- Encryption/Decryption Utilities
- Hash Calculator
- Log Analyzer
- Threat Intelligence
- Security Audit Checklist
- Incident Response Toolkit
- CTF Helper Tools

Om Vinayaka - Shield of wisdom, sword of knowledge.
"""

import os
import sys
import json
import hashlib
import secrets
import base64
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class SeverityLevel(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "informational"


class ThreatCategory(Enum):
    """Threat categories."""
    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    APT = "apt"
    ZERO_DAY = "zero_day"
    INSIDER = "insider"
    DDOS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    RCE = "rce"
    LFI = "lfi"
    PRIVILEGE_ESCALATION = "privilege_escalation"


@dataclass
class Vulnerability:
    """A security vulnerability."""
    id: str
    title: str
    description: str
    severity: SeverityLevel
    category: ThreatCategory
    
    # Technical details
    affected_component: str = ""
    affected_versions: List[str] = field(default_factory=list)
    attack_vector: str = ""
    
    # References
    cve: str = ""
    cvss_score: float = 0.0
    references: List[str] = field(default_factory=list)
    
    # Status
    discovered: datetime = field(default_factory=datetime.now)
    patched: bool = False
    patch_available: bool = False
    
    # Exploitation
    exploit_available: bool = False
    exploit_notes: str = ""


@dataclass
class SecurityAudit:
    """A security audit record."""
    id: str
    name: str
    target: str
    audit_type: str  # network, web, mobile, system
    
    started: datetime = field(default_factory=datetime.now)
    completed: Optional[datetime] = None
    
    findings: List[str] = field(default_factory=list)  # Vulnerability IDs
    notes: str = ""
    report_path: str = ""


@dataclass
class Incident:
    """A security incident."""
    id: str
    title: str
    description: str
    severity: SeverityLevel
    
    detected: datetime = field(default_factory=datetime.now)
    contained: bool = False
    eradicated: bool = False
    recovered: bool = False
    
    ioc: List[str] = field(default_factory=list)  # Indicators of Compromise
    affected_systems: List[str] = field(default_factory=list)
    response_actions: List[str] = field(default_factory=list)
    lessons_learned: str = ""


class SecurityToolkit:
    """
    VA21 Security Expert Toolkit
    
    Comprehensive security tools for professionals.
    
    Categories:
    - Reconnaissance
    - Vulnerability Analysis
    - Cryptography
    - Forensics
    - Incident Response
    - CTF Tools
    - Secure Development
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, data_path: str = "/va21/security"):
        self.data_path = data_path
        
        # Create directories
        for subdir in ["audits", "incidents", "evidence", "tools", "reports"]:
            os.makedirs(os.path.join(data_path, subdir), exist_ok=True)
        
        # Data stores
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.audits: Dict[str, SecurityAudit] = {}
        self.incidents: Dict[str, Incident] = {}
        
        # Tool paths
        self.tool_paths = self._detect_tools()
        
        print(f"[SecurityToolkit] Initialized. Detected {len(self.tool_paths)} security tools.")
    
    def _detect_tools(self) -> Dict[str, str]:
        """Detect available security tools."""
        tools = {}
        
        common_tools = [
            "nmap", "nikto", "sqlmap", "gobuster", "dirb", "hydra",
            "john", "hashcat", "aircrack-ng", "wireshark", "tcpdump",
            "metasploit", "burpsuite", "zaproxy", "nuclei", "subfinder",
            "amass", "ffuf", "wfuzz", "masscan", "netcat", "socat",
            "curl", "wget", "openssl", "gpg", "steghide", "binwalk",
            "volatility", "autopsy", "foremost", "strings", "file",
            "radare2", "ghidra", "gdb", "ltrace", "strace",
        ]
        
        for tool in common_tools:
            try:
                result = subprocess.run(
                    ["which", tool],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    tools[tool] = result.stdout.strip()
            except:
                pass
        
        return tools
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CRYPTOGRAPHY TOOLS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def hash_text(self, text: str, algorithm: str = "sha256") -> str:
        """
        Hash text with various algorithms.
        
        Args:
            text: Text to hash
            algorithm: Hash algorithm (md5, sha1, sha256, sha512, blake2b)
            
        Returns:
            Hash string
        """
        algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
            "blake2b": hashlib.blake2b,
            "blake2s": hashlib.blake2s,
        }
        
        if algorithm not in algorithms:
            return f"Unknown algorithm: {algorithm}"
        
        return algorithms[algorithm](text.encode()).hexdigest()
    
    def hash_file(self, filepath: str, algorithm: str = "sha256") -> Optional[str]:
        """Hash a file."""
        if not os.path.exists(filepath):
            return None
        
        algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }
        
        if algorithm not in algorithms:
            return None
        
        hasher = algorithms[algorithm]()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def generate_password(self, length: int = 16, 
                          include_special: bool = True) -> str:
        """Generate a secure random password."""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        if include_special:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    def encode_base64(self, text: str) -> str:
        """Encode text to base64."""
        return base64.b64encode(text.encode()).decode()
    
    def decode_base64(self, encoded: str) -> str:
        """Decode base64 text."""
        try:
            return base64.b64decode(encoded).decode()
        except:
            return "Decoding failed"
    
    def encode_hex(self, text: str) -> str:
        """Encode text to hex."""
        return text.encode().hex()
    
    def decode_hex(self, hex_string: str) -> str:
        """Decode hex to text."""
        try:
            return bytes.fromhex(hex_string).decode()
        except:
            return "Decoding failed"
    
    def rot13(self, text: str) -> str:
        """Apply ROT13 cipher."""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    def caesar_cipher(self, text: str, shift: int) -> str:
        """Apply Caesar cipher with custom shift."""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    def xor_cipher(self, text: str, key: str) -> str:
        """XOR cipher."""
        result = []
        for i, char in enumerate(text):
            result.append(chr(ord(char) ^ ord(key[i % len(key)])))
        return ''.join(result)
    
    def analyze_hash(self, hash_string: str) -> Dict:
        """Identify hash type."""
        length = len(hash_string)
        
        possible_types = []
        
        if length == 32:
            possible_types.extend(["MD5", "MD4", "LM"])
        elif length == 40:
            possible_types.extend(["SHA-1", "MySQL5"])
        elif length == 56:
            possible_types.append("SHA-224")
        elif length == 64:
            possible_types.extend(["SHA-256", "SHA3-256", "RIPEMD-256"])
        elif length == 96:
            possible_types.append("SHA-384")
        elif length == 128:
            possible_types.extend(["SHA-512", "SHA3-512", "Whirlpool"])
        
        # Check for common patterns
        if hash_string.startswith("$2a$") or hash_string.startswith("$2b$"):
            possible_types.append("bcrypt")
        elif hash_string.startswith("$6$"):
            possible_types.append("SHA-512 crypt")
        elif hash_string.startswith("$5$"):
            possible_types.append("SHA-256 crypt")
        elif hash_string.startswith("$1$"):
            possible_types.append("MD5 crypt")
        
        return {
            "hash": hash_string,
            "length": length,
            "possible_types": possible_types,
            "is_hex": all(c in "0123456789abcdefABCDEF" for c in hash_string)
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NETWORK ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def analyze_url(self, url: str) -> Dict:
        """Analyze a URL for security indicators."""
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        
        # Check for suspicious patterns
        suspicious = []
        
        # IP address in URL
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parsed.netloc):
            suspicious.append("IP address in URL (possible phishing)")
        
        # Suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work']
        if any(parsed.netloc.endswith(tld) for tld in suspicious_tlds):
            suspicious.append("Suspicious TLD")
        
        # URL shorteners
        shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'is.gd']
        if any(s in parsed.netloc for s in shorteners):
            suspicious.append("URL shortener (destination unknown)")
        
        # Excessive subdomains
        if parsed.netloc.count('.') > 3:
            suspicious.append("Many subdomains (possible impersonation)")
        
        # HTTP instead of HTTPS
        if parsed.scheme == 'http':
            suspicious.append("Not using HTTPS")
        
        # Suspicious keywords in path
        sus_keywords = ['login', 'verify', 'secure', 'account', 'update', 'confirm']
        if any(kw in parsed.path.lower() for kw in sus_keywords):
            suspicious.append("Suspicious keywords in path")
        
        return {
            "url": url,
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path,
            "query": parse_qs(parsed.query),
            "fragment": parsed.fragment,
            "suspicious_indicators": suspicious,
            "risk_level": "high" if len(suspicious) >= 3 else "medium" if suspicious else "low"
        }
    
    def analyze_ip(self, ip: str) -> Dict:
        """Analyze an IP address."""
        result = {
            "ip": ip,
            "is_private": False,
            "is_loopback": False,
            "is_reserved": False,
            "type": "unknown"
        }
        
        # Parse octets
        try:
            octets = [int(o) for o in ip.split('.')]
            if len(octets) != 4:
                return {"error": "Invalid IP format"}
            
            # Check ranges
            if octets[0] == 10:
                result["is_private"] = True
                result["type"] = "Private (Class A)"
            elif octets[0] == 172 and 16 <= octets[1] <= 31:
                result["is_private"] = True
                result["type"] = "Private (Class B)"
            elif octets[0] == 192 and octets[1] == 168:
                result["is_private"] = True
                result["type"] = "Private (Class C)"
            elif octets[0] == 127:
                result["is_loopback"] = True
                result["type"] = "Loopback"
            elif octets[0] == 0:
                result["is_reserved"] = True
                result["type"] = "Reserved"
            elif octets[0] >= 224:
                result["type"] = "Multicast/Reserved"
            else:
                result["type"] = "Public"
            
        except:
            return {"error": "Failed to parse IP"}
        
        return result
    
    def check_port(self, host: str, port: int, timeout: int = 3) -> Dict:
        """Check if a port is open."""
        import socket
        
        result = {
            "host": host,
            "port": port,
            "open": False,
            "service": self._get_common_service(port)
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            connection = sock.connect_ex((host, port))
            
            if connection == 0:
                result["open"] = True
            
            sock.close()
            
        except socket.error as e:
            result["error"] = str(e)
        
        return result
    
    def _get_common_service(self, port: int) -> str:
        """Get common service for a port."""
        services = {
            20: "FTP-data", 21: "FTP", 22: "SSH", 23: "Telnet",
            25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
            119: "NNTP", 123: "NTP", 143: "IMAP", 161: "SNMP",
            194: "IRC", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
            587: "SMTP", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL",
            1521: "Oracle", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
            5900: "VNC", 6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
            27017: "MongoDB"
        }
        return services.get(port, "Unknown")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FORENSICS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def extract_strings(self, filepath: str, min_length: int = 4) -> List[str]:
        """Extract readable strings from a file."""
        if not os.path.exists(filepath):
            return []
        
        strings = []
        
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # ASCII strings
            pattern = re.compile(b'[\x20-\x7e]{' + str(min_length).encode() + b',}')
            strings = [s.decode('ascii', errors='ignore') for s in pattern.findall(data)]
            
        except Exception as e:
            print(f"Error: {e}")
        
        return strings
    
    def get_file_info(self, filepath: str) -> Dict:
        """Get detailed file information."""
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        stat = os.stat(filepath)
        
        info = {
            "path": os.path.abspath(filepath),
            "size": stat.st_size,
            "size_human": self._human_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "mode": oct(stat.st_mode),
            "uid": stat.st_uid,
            "gid": stat.st_gid,
        }
        
        # File hashes
        info["hashes"] = {
            "md5": self.hash_file(filepath, "md5"),
            "sha1": self.hash_file(filepath, "sha1"),
            "sha256": self.hash_file(filepath, "sha256"),
        }
        
        # Try to get file type
        try:
            result = subprocess.run(
                ["file", "-b", filepath],
                capture_output=True, text=True, timeout=5
            )
            info["type"] = result.stdout.strip()
        except:
            pass
        
        return info
    
    def _human_size(self, size: int) -> str:
        """Convert size to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    def analyze_log_file(self, filepath: str, patterns: List[str] = None) -> Dict:
        """Analyze a log file for security events."""
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        # Default patterns to look for
        if patterns is None:
            patterns = [
                r'failed\s+password',
                r'authentication\s+failure',
                r'invalid\s+user',
                r'refused\s+connect',
                r'connection\s+refused',
                r'permission\s+denied',
                r'access\s+denied',
                r'error',
                r'warning',
                r'critical',
                r'SQL\s+injection',
                r'XSS',
                r'command\s+injection',
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
            ]
        
        results = {
            "file": filepath,
            "total_lines": 0,
            "pattern_matches": {p: [] for p in patterns},
            "ip_addresses": set(),
            "timestamps": [],
        }
        
        try:
            with open(filepath, 'r', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    results["total_lines"] += 1
                    
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            results["pattern_matches"][pattern].append({
                                "line": line_num,
                                "content": line.strip()[:200]
                            })
                    
                    # Extract IPs
                    ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
                    results["ip_addresses"].update(ips)
            
            results["ip_addresses"] = list(results["ip_addresses"])
            
            # Count matches
            results["summary"] = {
                p: len(m) for p, m in results["pattern_matches"].items() if m
            }
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VULNERABILITY MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_vulnerability(self, title: str, description: str,
                             severity: SeverityLevel, category: ThreatCategory,
                             **kwargs) -> Vulnerability:
        """Create a vulnerability record."""
        vuln_id = f"vuln_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        vuln = Vulnerability(
            id=vuln_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            affected_component=kwargs.get("affected_component", ""),
            cve=kwargs.get("cve", ""),
            cvss_score=kwargs.get("cvss_score", 0.0),
            attack_vector=kwargs.get("attack_vector", ""),
        )
        
        self.vulnerabilities[vuln_id] = vuln
        return vuln
    
    def get_severity_stats(self) -> Dict:
        """Get vulnerability statistics by severity."""
        return {
            severity.value: len([
                v for v in self.vulnerabilities.values()
                if v.severity == severity
            ])
            for severity in SeverityLevel
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INCIDENT RESPONSE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_incident(self, title: str, description: str,
                        severity: SeverityLevel) -> Incident:
        """Create an incident record."""
        incident_id = f"inc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity
        )
        
        self.incidents[incident_id] = incident
        return incident
    
    def add_ioc(self, incident_id: str, ioc: str, ioc_type: str = "") -> bool:
        """Add an Indicator of Compromise to an incident."""
        if incident_id not in self.incidents:
            return False
        
        self.incidents[incident_id].ioc.append(f"[{ioc_type}] {ioc}" if ioc_type else ioc)
        return True
    
    def get_incident_response_checklist(self) -> List[Dict]:
        """Get incident response checklist."""
        return [
            {"phase": "Preparation", "items": [
                "Incident response team contacts updated",
                "Response tools and software ready",
                "Documentation templates available",
                "Communication channels established",
            ]},
            {"phase": "Identification", "items": [
                "Confirm incident is genuine",
                "Determine scope and impact",
                "Identify affected systems",
                "Document timeline of events",
                "Collect initial evidence",
            ]},
            {"phase": "Containment", "items": [
                "Isolate affected systems",
                "Block malicious IPs/domains",
                "Disable compromised accounts",
                "Preserve evidence for forensics",
                "Implement temporary fixes",
            ]},
            {"phase": "Eradication", "items": [
                "Remove malware/threats",
                "Patch vulnerabilities",
                "Reset compromised credentials",
                "Review and clean logs",
                "Verify removal of threats",
            ]},
            {"phase": "Recovery", "items": [
                "Restore systems from clean backups",
                "Verify system integrity",
                "Monitor for reinfection",
                "Return to normal operations",
                "Update security controls",
            ]},
            {"phase": "Lessons Learned", "items": [
                "Conduct post-incident review",
                "Document lessons learned",
                "Update incident response plan",
                "Implement preventive measures",
                "Share findings (as appropriate)",
            ]},
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CTF TOOLS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def ctf_hints(self, category: str) -> List[str]:
        """Get CTF hints for a category."""
        hints = {
            "crypto": [
                "Check for common ciphers: Caesar, Vigenère, XOR",
                "Try base64, base32, base16, base58 decoding",
                "Look for RSA with weak parameters",
                "Check for hash collisions or weak hashing",
                "Try frequency analysis for substitution ciphers",
            ],
            "web": [
                "Check robots.txt and .git directories",
                "Look for SQL injection in all input fields",
                "Check for IDOR (Insecure Direct Object Reference)",
                "Try XSS payloads in input fields",
                "Check cookies for session manipulation",
                "Look at page source for hidden comments",
            ],
            "forensics": [
                "Use binwalk to extract embedded files",
                "Check file headers with file and xxd",
                "Use strings to find readable text",
                "Check EXIF data in images",
                "Use Wireshark for pcap analysis",
                "Check for steganography in images",
            ],
            "reverse": [
                "Use strings on binaries first",
                "Check with file command for binary type",
                "Use Ghidra or radare2 for decompilation",
                "Look for common functions: strcmp, strlen",
                "Check for hardcoded strings and keys",
                "Use dynamic analysis with gdb",
            ],
            "pwn": [
                "Check for buffer overflow opportunities",
                "Look for format string vulnerabilities",
                "Check security protections with checksec",
                "Look for use-after-free bugs",
                "Check for integer overflows",
                "Try ROP chains for bypassing NX",
            ],
            "misc": [
                "Check all file types with file command",
                "Look for QR codes in images",
                "Check for Morse code or binary encoding",
                "Try common passwords on archives",
                "Look for metadata in files",
            ],
        }
        
        return hints.get(category.lower(), [
            "Category not found. Try: crypto, web, forensics, reverse, pwn, misc"
        ])
    
    def common_wordlists(self) -> Dict[str, str]:
        """Get paths to common wordlists."""
        wordlists = {
            "rockyou": "/usr/share/wordlists/rockyou.txt",
            "dirb_common": "/usr/share/dirb/wordlists/common.txt",
            "dirbuster_medium": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
            "seclists_passwords": "/usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt",
            "seclists_dirs": "/usr/share/seclists/Discovery/Web-Content/common.txt",
        }
        
        # Check which exist
        available = {}
        for name, path in wordlists.items():
            available[name] = path if os.path.exists(path) else "Not found"
        
        return available
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECURITY AUDIT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_security_checklist(self, audit_type: str = "general") -> List[Dict]:
        """Get security audit checklist."""
        checklists = {
            "general": [
                {"id": "1", "category": "Authentication",
                 "items": ["Strong password policy", "MFA enabled", "Session timeout configured"]},
                {"id": "2", "category": "Authorization",
                 "items": ["Principle of least privilege", "Role-based access control", "Regular access reviews"]},
                {"id": "3", "category": "Encryption",
                 "items": ["Data encrypted at rest", "Data encrypted in transit", "Strong encryption algorithms"]},
                {"id": "4", "category": "Logging",
                 "items": ["Security events logged", "Log integrity protected", "Log retention policy"]},
                {"id": "5", "category": "Updates",
                 "items": ["Patches applied promptly", "EOL software replaced", "Vulnerability scanning"]},
            ],
            "web": [
                {"id": "1", "category": "Input Validation",
                 "items": ["SQL injection prevention", "XSS prevention", "CSRF tokens", "Input sanitization"]},
                {"id": "2", "category": "Authentication",
                 "items": ["Secure session management", "Password hashing (bcrypt/argon2)", "Brute force protection"]},
                {"id": "3", "category": "Headers",
                 "items": ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "HSTS"]},
            ],
        }
        
        return checklists.get(audit_type, checklists["general"])
    
    def get_statistics(self) -> Dict:
        """Get security toolkit statistics."""
        return {
            "total_vulnerabilities": len(self.vulnerabilities),
            "total_incidents": len(self.incidents),
            "total_audits": len(self.audits),
            "available_tools": len(self.tool_paths),
            "vulnerabilities_by_severity": self.get_severity_stats(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_security_toolkit_instance = None

def get_security_toolkit() -> SecurityToolkit:
    """Get the SecurityToolkit singleton."""
    global _security_toolkit_instance
    if _security_toolkit_instance is None:
        _security_toolkit_instance = SecurityToolkit()
    return _security_toolkit_instance


if __name__ == "__main__":
    toolkit = get_security_toolkit()
    
    # Test hash
    print("Hash test:", toolkit.hash_text("test", "sha256"))
    
    # Test password generation
    print("Password:", toolkit.generate_password(20))
    
    # Analyze hash
    print("Hash analysis:", json.dumps(
        toolkit.analyze_hash("5d41402abc4b2a76b9719d911017c592"),
        indent=2
    ))
    
    # CTF hints
    print("CTF Web hints:", toolkit.ctf_hints("web"))
