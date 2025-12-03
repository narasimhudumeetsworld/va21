#!/bin/bash
# VA21 OS - Installation Script
# Om Vinayaka 🙏
#
# This script helps you build and install VA21 OS.

set -e

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                        🔒 VA21 OS"
echo "                  Secure AI-Powered Operating System"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Om Vinayaka 🙏"
echo ""

# Detect host OS
case "$(uname -s)" in
    Linux*)     MACHINE=Linux;;
    *)          
        echo "❌ VA21 OS can only be built on Linux."
        echo ""
        echo "To install VA21 OS:"
        echo "  1. Download the ISO from https://github.com/narasimhudumeetsworld/va21/releases"
        echo "  2. Write to USB: dd if=va21-os.iso of=/dev/sdX bs=4M"
        echo "  3. Boot from USB and install"
        exit 1
        ;;
esac

echo "What would you like to do?"
echo ""
echo "  1. Build VA21 OS ISO (for installation)"
echo "  2. Download pre-built ISO"
echo "  3. Install development environment"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "═══════════════════════════════════════════════════════════════════"
        echo "                    Building VA21 OS ISO"
        echo "═══════════════════════════════════════════════════════════════════"
        echo ""
        
        # Check for required packages
        echo "Checking build requirements..."
        MISSING=""
        for pkg in debootstrap xorriso squashfs-tools grub-pc-bin; do
            if ! dpkg -l | grep -q "^ii  $pkg"; then
                MISSING="$MISSING $pkg"
            fi
        done
        
        if [ -n "$MISSING" ]; then
            echo "Installing required packages:$MISSING"
            sudo apt update
            sudo apt install -y $MISSING
        fi
        
        echo ""
        echo "Select edition:"
        echo "  1. Debian (Full GNU toolkit, ~5GB)"
        echo "  2. Alpine (Lightweight, ~2GB)"
        read -p "Enter choice [1-2]: " edition
        
        case $edition in
            1) EDITION="debian" ;;
            2) EDITION="alpine" ;;
            *) EDITION="debian" ;;
        esac
        
        echo ""
        echo "Building VA21 OS $EDITION..."
        ./build-iso.sh "$EDITION"
        ;;
        
    2)
        echo ""
        echo "═══════════════════════════════════════════════════════════════════"
        echo "                    Download VA21 OS ISO"
        echo "═══════════════════════════════════════════════════════════════════"
        echo ""
        echo "Download from: https://github.com/narasimhudumeetsworld/va21/releases"
        echo ""
        echo "After downloading:"
        echo "  1. Write to USB: sudo dd if=va21-os.iso of=/dev/sdX bs=4M status=progress"
        echo "  2. Boot from USB"
        echo "  3. Follow installation wizard"
        ;;
        
    3)
        echo ""
        echo "═══════════════════════════════════════════════════════════════════"
        echo "                    Development Environment"
        echo "═══════════════════════════════════════════════════════════════════"
        echo ""
        
        # Install Python dependencies
        echo "Installing Python dependencies..."
        pip3 install --user -r va21_system/linux_os/requirements.txt
        
        # Install Ollama for Guardian AI
        if ! command -v ollama &> /dev/null; then
            echo ""
            echo "Installing Ollama for Guardian AI..."
            curl -fsSL https://ollama.com/install.sh | sh
        fi
        
        # Download Guardian AI model
        echo ""
        echo "Downloading Guardian AI model (IBM Granite 4.0)..."
        ollama pull granite4:2b
        
        echo ""
        echo "✅ Development environment ready!"
        echo ""
        echo "To run the Zork interface:"
        echo "  cd va21_system/linux_os/zork_shell"
        echo "  python3 zork_interface.py"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    VA21 OS Features"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "🎮 Zork-style text adventure interface"
echo "🔒 Guardian AI security (IBM Granite 4.0)"
echo "🎤 Voice control (1,600+ languages)"
echo "📦 Research & writing tools"
echo "🛡️ ClamAV antivirus"
echo "🔍 SearXNG private search"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    VA21 OS Base: ~5 GB"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Om Vinayaka 🙏"
echo ""
echo "For support: https://github.com/narasimhudumeetsworld/va21"