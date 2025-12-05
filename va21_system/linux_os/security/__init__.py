#!/usr/bin/env python3
"""
VA21 OS - Security Module
==========================

🙏 OM VINAYAKA - SECURE AGENTIC COMPUTING 🙏

This module implements comprehensive security features for VA21 OS:

1. SENSITIVE DATA PROTECTION
   - Ephemeral memory (25-second auto-delete)
   - Pre-authentication encryption
   - Air-gap between AI and encrypted data

2. WEBSITE AUTHENTICITY VERIFICATION
   - WHOIS lookup
   - Homoglyph detection
   - New registration warnings

3. MULTI-FACTOR AUTHENTICATION
   - Password, fingerprint, voice, webcam
   - Platform-specific biometric integration

Author: Prayaga Vaibhav
License: Om Vinayaka Prayaga Vaibhav Inventions License
Copyright (c) 2024-2025 Prayaga Vaibhav
"""

from .sensitive_data_protection import (
    SensitiveDataProtectionFramework,
    SensitiveDataDetector,
    EphemeralMemoryManager,
    WebsiteAuthenticityVerifier,
    AuthenticationManager,
    SensitiveDataType,
    AuthenticationMethod,
    WebsiteRiskLevel,
    get_security_framework,
    SECURITY_VERSION,
)

__all__ = [
    'SensitiveDataProtectionFramework',
    'SensitiveDataDetector',
    'EphemeralMemoryManager',
    'WebsiteAuthenticityVerifier',
    'AuthenticationManager',
    'SensitiveDataType',
    'AuthenticationMethod',
    'WebsiteRiskLevel',
    'get_security_framework',
    'SECURITY_VERSION',
]
