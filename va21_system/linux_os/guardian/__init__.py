# VA21 Guardian AI Package
"""
VA21 Guardian AI - Security protection for VA21 Research OS.

Components:
- guardian_core.py: Main Guardian AI implementation
- clamav_integration.py: ClamAV antivirus integration
"""

from .guardian_core import GuardianAI, get_guardian

try:
    from .clamav_integration import ClamAVIntegration, get_clamav
except ImportError:
    pass

__version__ = "1.0.0"
