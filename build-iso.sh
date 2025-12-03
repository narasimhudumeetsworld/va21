#!/bin/bash
# VA21 OS - ISO Builder
# Om Vinayaka 🙏
#
# This script builds a bootable VA21 OS ISO image.

set -e

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                    🔒 VA21 OS ISO Builder"
echo "                  Secure AI-Powered Operating System"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Om Vinayaka 🙏"
echo ""

# Check requirements
check_requirements() {
    local missing=()
    
    for cmd in debootstrap xorriso squashfs-tools grub-pc-bin grub-efi-amd64-bin; do
        if ! command -v "$cmd" &> /dev/null && ! dpkg -l | grep -q "$cmd"; then
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo "❌ Missing required packages: ${missing[*]}"
        echo ""
        echo "Install with:"
        echo "  sudo apt install debootstrap xorriso squashfs-tools grub-pc-bin grub-efi-amd64-bin mtools"
        exit 1
    fi
    
    echo "✅ All requirements met"
}

# Parse arguments
EDITION="${1:-debian}"
OUTPUT_DIR="${2:-./output}"

echo "Edition: $EDITION"
echo "Output: $OUTPUT_DIR"
echo ""

# Check requirements
check_requirements

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build the ISO
echo ""
echo "🏗️ Building VA21 OS $EDITION ISO..."
echo "   This will take several minutes..."
echo ""

cd va21_system/linux_os

if [ -f "scripts/build_iso.sh" ]; then
    ./scripts/build_iso.sh "$EDITION"
else
    echo "❌ Build script not found. Creating basic ISO structure..."
    
    # Create basic ISO structure
    WORK_DIR="/tmp/va21-iso-$$"
    mkdir -p "$WORK_DIR"/{live,boot/grub,EFI/BOOT}
    
    # Create minimal rootfs
    echo "Creating root filesystem..."
    sudo debootstrap --variant=minbase bookworm "$WORK_DIR/chroot" http://deb.debian.org/debian
    
    # Copy VA21 OS files
    echo "Installing VA21 OS components..."
    sudo cp -r zork_shell "$WORK_DIR/chroot/opt/"
    sudo cp -r guardian "$WORK_DIR/chroot/opt/"
    sudo cp -r window_manager "$WORK_DIR/chroot/opt/"
    sudo cp -r research_suite "$WORK_DIR/chroot/opt/"
    
    # Create squashfs
    echo "Creating squashfs..."
    sudo mksquashfs "$WORK_DIR/chroot" "$WORK_DIR/live/filesystem.squashfs" -comp xz
    
    # Create GRUB config
    cat > "$WORK_DIR/boot/grub/grub.cfg" << 'GRUB'
set timeout=5
set default=0

menuentry "VA21 OS (Vinayaka)" {
    linux /boot/vmlinuz boot=live
    initrd /boot/initrd.img
}

menuentry "VA21 OS (Safe Mode)" {
    linux /boot/vmlinuz boot=live single
    initrd /boot/initrd.img
}
GRUB

    # Create ISO
    echo "Creating ISO image..."
    xorriso -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "VA21_OS" \
        -eltorito-boot boot/grub/bios.img \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        --eltorito-catalog boot/grub/boot.cat \
        -output "$OUTPUT_DIR/va21-os-$EDITION.iso" \
        "$WORK_DIR"
    
    # Cleanup
    sudo rm -rf "$WORK_DIR"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "              ✅ VA21 OS ISO BUILD COMPLETE!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "ISO Location: $OUTPUT_DIR/va21-os-$EDITION.iso"
echo ""
echo "To install:"
echo "  1. Write to USB: sudo dd if=$OUTPUT_DIR/va21-os-$EDITION.iso of=/dev/sdX bs=4M"
echo "  2. Boot from USB and follow installation"
echo ""
echo "Or use in VirtualBox/VMware:"
echo "  1. Create new VM"
echo "  2. Use ISO as boot disk"
echo "  3. Install to virtual disk"
echo ""
echo "Om Vinayaka 🙏"
