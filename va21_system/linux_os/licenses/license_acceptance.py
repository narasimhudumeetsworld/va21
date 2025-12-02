#!/usr/bin/env python3
"""
VA21 Research OS - License Acceptance and Disclaimer
======================================================

Displays license information and requires acceptance before first use.

Om Vinayaka - Transparency and honor in all dealings.
"""

import os
import json
from datetime import datetime
from typing import Optional


class LicenseAcceptance:
    """
    License acceptance and disclaimer management.
    
    Handles:
    - First-run license display and acceptance
    - Third-party license acknowledgments
    - User agreement tracking
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config_path: str = "/va21/config"):
        self.config_path = config_path
        self.acceptance_file = os.path.join(config_path, ".license_accepted")
        
        os.makedirs(config_path, exist_ok=True)
    
    def is_accepted(self) -> bool:
        """Check if license has been accepted."""
        return os.path.exists(self.acceptance_file)
    
    def get_acceptance_info(self) -> Optional[dict]:
        """Get acceptance information if available."""
        if not self.is_accepted():
            return None
        
        try:
            with open(self.acceptance_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def accept(self, username: str = "researcher") -> bool:
        """
        Record license acceptance.
        
        Args:
            username: User accepting the license
            
        Returns:
            Success status
        """
        try:
            acceptance_data = {
                "accepted": True,
                "accepted_at": datetime.now().isoformat(),
                "accepted_by": username,
                "version": self.VERSION
            }
            
            with open(self.acceptance_file, 'w') as f:
                json.dump(acceptance_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error recording acceptance: {e}")
            return False
    
    def show_license_prompt(self) -> bool:
        """
        Display license and get acceptance.
        
        Returns:
            True if accepted, False otherwise
        """
        print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                    VA21 RESEARCH OS - LICENSE AGREEMENT                        ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

                              ॐ विनायकाय नमः
                              Om Vinayaka Namah

Welcome to VA21 Research OS v1.0.0 (Vinayaka)

Before you begin, please read and accept the following terms:

════════════════════════════════════════════════════════════════════════════════
                              PROPRIETARY LICENSE
════════════════════════════════════════════════════════════════════════════════

VA21 Research OS
Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, transferring,
or reproduction of this software, via any medium, is strictly prohibited.

BY USING THIS SOFTWARE, YOU AGREE TO:

1. Use the software only for lawful purposes
2. Not redistribute the software without authorization
3. Respect the privacy and security features of the system
4. Comply with all applicable laws and regulations

════════════════════════════════════════════════════════════════════════════════
                          THIRD-PARTY ACKNOWLEDGMENTS
════════════════════════════════════════════════════════════════════════════════

VA21 Research OS incorporates the following open-source software:

┌──────────────────────────────────────────────────────────────────────────────┐
│ Software          │ License        │ Purpose                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ Alpine Linux      │ Various        │ Operating system base                  │
│ ClamAV            │ GPLv2          │ Antivirus protection                   │
│ SearXNG           │ AGPL-3.0       │ Privacy-respecting search              │
│ BusyBox           │ GPLv2          │ Unix utilities                         │
│ Python/Libraries  │ Various        │ Core functionality                     │
└──────────────────────────────────────────────────────────────────────────────┘

Full license texts and acknowledgments are available in:
  /va21/licenses/ACKNOWLEDGMENTS.md

We are grateful to all the open-source communities whose work makes
VA21 Research OS possible.

════════════════════════════════════════════════════════════════════════════════
                                 DISCLAIMER
════════════════════════════════════════════════════════════════════════════════

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.

THE ANTIVIRUS (CLAMAV) AND SECURITY FEATURES ARE PROVIDED AS ADDITIONAL
PROTECTION BUT DO NOT GUARANTEE COMPLETE SECURITY. USERS ARE RESPONSIBLE
FOR THEIR OWN DATA AND SECURITY PRACTICES.

════════════════════════════════════════════════════════════════════════════════
                                  PRIVACY
════════════════════════════════════════════════════════════════════════════════

VA21 Research OS is designed with privacy in mind:

• All data is stored locally on your device
• Research and notes are never uploaded without explicit permission
• SearXNG searches do not track or profile you
• Sensitive content can be marked for additional protection
• No telemetry or analytics are collected

════════════════════════════════════════════════════════════════════════════════
""")
        
        while True:
            response = input("\nDo you accept these terms? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y', 'accept']:
                if self.accept():
                    print("""
════════════════════════════════════════════════════════════════════════════════
                            LICENSE ACCEPTED
════════════════════════════════════════════════════════════════════════════════

Thank you for accepting the license agreement.

Your acceptance has been recorded.

Welcome to VA21 Research OS!

May your research be fruitful and your knowledge grow.

                              ॐ विनायकाय नमः

════════════════════════════════════════════════════════════════════════════════
""")
                    return True
                else:
                    print("Error recording acceptance. Please try again.")
                    
            elif response in ['no', 'n', 'decline']:
                print("""
════════════════════════════════════════════════════════════════════════════════
                            LICENSE NOT ACCEPTED
════════════════════════════════════════════════════════════════════════════════

You have declined the license agreement.

VA21 Research OS cannot be used without accepting the license.

If you have questions about the license, please contact the development team.

Exiting...
════════════════════════════════════════════════════════════════════════════════
""")
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    def show_about(self):
        """Display about information."""
        print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║   ██╗   ██╗ █████╗ ██████╗  ██╗    ██████╗ ███████╗███████╗███████╗ █████╗    ║
║   ██║   ██║██╔══██╗╚════██╗███║   ██╔═══██╗██╔════╝██╔════╝██╔════╝██╔══██╗   ║
║   ██║   ██║███████║ █████╔╝╚██║   ██║   ██║███████╗█████╗  ███████╗███████║   ║
║   ╚██╗ ██╔╝██╔══██║██╔═══╝  ██║   ██║   ██║╚════██║██╔══╝  ╚════██║██╔══██║   ║
║    ╚████╔╝ ██║  ██║███████╗ ██║   ╚██████╔╝███████║███████╗███████║██║  ██║   ║
║     ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═╝    ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝   ║
║                                                                                ║
║                        RESEARCH OS v1.0.0 (Vinayaka)                           ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                    A Secure Research Operating System

VA21 Research OS is a privacy-first, AI-powered research environment designed
for researchers, writers, journalists, and knowledge workers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CORE FEATURES:
  • Zork-style text adventure interface
  • Guardian AI security protection
  • ClamAV antivirus integration
  • SearXNG privacy-respecting search
  • Obsidian-style knowledge vault
  • Writing suite for papers and articles
  • Toggleable hints for newcomers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPEN SOURCE ACKNOWLEDGMENTS:

We gratefully acknowledge the following open-source projects:

  Alpine Linux    - Lightweight Linux distribution
  ClamAV          - Open-source antivirus engine
  SearXNG         - Privacy-respecting metasearch engine
  BusyBox         - Essential Unix utilities
  Python          - Programming language and libraries

Full acknowledgments: /va21/licenses/ACKNOWLEDGMENTS.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                              ॐ विनायकाय नमः
                  "May obstacles be removed from your path"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# Singleton instance
_license_instance = None

def get_license_acceptance() -> LicenseAcceptance:
    """Get the LicenseAcceptance singleton."""
    global _license_instance
    if _license_instance is None:
        _license_instance = LicenseAcceptance()
    return _license_instance


def check_license_on_start() -> bool:
    """Check license acceptance on startup."""
    license_mgr = get_license_acceptance()
    
    if license_mgr.is_accepted():
        return True
    
    return license_mgr.show_license_prompt()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "about":
        get_license_acceptance().show_about()
    else:
        if check_license_on_start():
            print("License accepted. You may now use VA21 Research OS.")
        else:
            sys.exit(1)
