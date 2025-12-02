#!/bin/bash
# VA21 Research OS - ISO Build Script
# =====================================
# Builds bootable ISO images for VA21 OS
# Supports both Debian and Alpine editions
#
# Usage:
#   ./build_iso.sh debian    # Build Debian edition ISO
#   ./build_iso.sh alpine    # Build Alpine edition ISO
#   ./build_iso.sh all       # Build both editions
#
# Output:
#   output/va21-debian-x86_64.iso
#   output/va21-alpine-x86_64.iso
#
# Om Vinayaka - Bootable freedom.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."
OUTPUT_DIR="${ROOT_DIR}/output"
BUILD_DIR="${OUTPUT_DIR}/iso-build"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Version
VERSION="1.0.0"
DATE=$(date +%Y%m%d)

echo -e "${BLUE}"
cat << 'EOF'
 ██╗   ██╗ █████╗ ██████╗  ██╗    ██╗███████╗ ██████╗ 
 ██║   ██║██╔══██╗╚════██╗███║    ██║██╔════╝██╔═══██╗
 ██║   ██║███████║ █████╔╝╚██║    ██║███████╗██║   ██║
 ╚██╗ ██╔╝██╔══██║██╔═══╝  ██║    ██║╚════██║██║   ██║
  ╚████╔╝ ██║  ██║███████╗ ██║    ██║███████║╚██████╔╝
   ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═╝    ╚═╝╚══════╝ ╚═════╝ 
              ISO Builder v1.0.0
EOF
echo -e "${NC}"

# Check dependencies
check_dependencies() {
    echo -e "${YELLOW}[CHECK]${NC} Checking dependencies..."
    
    local deps=("xorriso" "mksquashfs" "grub-mkrescue" "docker")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}[ERROR]${NC} Missing dependencies: ${missing[*]}"
        echo "Install them with:"
        echo "  Debian/Ubuntu: sudo apt install xorriso squashfs-tools grub-pc-bin grub-efi-amd64-bin docker.io"
        echo "  Alpine: sudo apk add xorriso squashfs-tools grub grub-efi docker"
        exit 1
    fi
    
    echo -e "${GREEN}[CHECK]${NC} All dependencies found"
}

# Build Debian ISO
build_debian_iso() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}[BUILD]${NC} Building VA21 Debian Edition ISO..."
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    local ISO_NAME="va21-debian-${VERSION}-x86_64.iso"
    local WORK_DIR="${BUILD_DIR}/debian"
    
    # Clean and create work directory
    rm -rf "${WORK_DIR}"
    mkdir -p "${WORK_DIR}"/{staging,rootfs,boot/grub}
    
    # Build Docker image first
    echo -e "${YELLOW}[BUILD]${NC} Building Docker image..."
    docker build -f "${ROOT_DIR}/Dockerfile.debian" -t va21-debian:build "${ROOT_DIR}"
    
    # Export rootfs from Docker
    echo -e "${YELLOW}[BUILD]${NC} Exporting rootfs..."
    local container_id=$(docker create va21-debian:build)
    docker export "$container_id" | tar -C "${WORK_DIR}/rootfs" -xf -
    docker rm "$container_id"
    
    # Create squashfs
    echo -e "${YELLOW}[BUILD]${NC} Creating squashfs..."
    mksquashfs "${WORK_DIR}/rootfs" "${WORK_DIR}/staging/live/filesystem.squashfs" \
        -comp xz -Xbcj x86 -b 1M -no-duplicates
    
    # Copy kernel and initramfs
    echo -e "${YELLOW}[BUILD]${NC} Copying boot files..."
    mkdir -p "${WORK_DIR}/staging/live"
    cp "${WORK_DIR}/rootfs/boot/vmlinuz-"* "${WORK_DIR}/staging/live/vmlinuz" 2>/dev/null || \
        echo "Note: Using default kernel"
    cp "${WORK_DIR}/rootfs/boot/initrd.img-"* "${WORK_DIR}/staging/live/initrd" 2>/dev/null || \
        echo "Note: Using default initrd"
    
    # Create GRUB config
    cat > "${WORK_DIR}/staging/boot/grub/grub.cfg" << 'GRUB_EOF'
set timeout=10
set default=0

menuentry "VA21 Research OS (Debian Edition)" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}

menuentry "VA21 Research OS (Safe Mode)" {
    linux /live/vmlinuz boot=live single
    initrd /live/initrd
}

menuentry "Memory Test" {
    linux16 /boot/memtest86+.bin
}
GRUB_EOF

    # Create ISO
    echo -e "${YELLOW}[BUILD]${NC} Creating ISO..."
    grub-mkrescue -o "${OUTPUT_DIR}/${ISO_NAME}" "${WORK_DIR}/staging" 2>/dev/null || \
        xorriso -as mkisofs \
            -iso-level 3 \
            -full-iso9660-filenames \
            -volid "VA21_DEBIAN" \
            -eltorito-boot boot/grub/i386-pc/eltorito.img \
            -no-emul-boot \
            -boot-load-size 4 \
            -boot-info-table \
            -isohybrid-mbr /usr/lib/grub/i386-pc/boot_hybrid.img \
            -output "${OUTPUT_DIR}/${ISO_NAME}" \
            "${WORK_DIR}/staging"
    
    # Create checksum
    cd "${OUTPUT_DIR}"
    sha256sum "${ISO_NAME}" > "${ISO_NAME}.sha256"
    
    echo -e "${GREEN}[BUILD]${NC} Debian ISO created: ${OUTPUT_DIR}/${ISO_NAME}"
    echo -e "${GREEN}[BUILD]${NC} Size: $(du -h "${OUTPUT_DIR}/${ISO_NAME}" | cut -f1)"
}

# Build Alpine ISO
build_alpine_iso() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}[BUILD]${NC} Building VA21 Alpine Edition ISO..."
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    local ISO_NAME="va21-alpine-${VERSION}-x86_64.iso"
    local WORK_DIR="${BUILD_DIR}/alpine"
    
    # Clean and create work directory
    rm -rf "${WORK_DIR}"
    mkdir -p "${WORK_DIR}"/{staging,rootfs,boot/grub}
    
    # Build Docker image first
    echo -e "${YELLOW}[BUILD]${NC} Building Docker image..."
    docker build -f "${ROOT_DIR}/Dockerfile.alpine-desktop" -t va21-alpine:build "${ROOT_DIR}"
    
    # Export rootfs from Docker
    echo -e "${YELLOW}[BUILD]${NC} Exporting rootfs..."
    local container_id=$(docker create va21-alpine:build)
    docker export "$container_id" | tar -C "${WORK_DIR}/rootfs" -xf -
    docker rm "$container_id"
    
    # Create squashfs
    echo -e "${YELLOW}[BUILD]${NC} Creating squashfs..."
    mksquashfs "${WORK_DIR}/rootfs" "${WORK_DIR}/staging/live/filesystem.squashfs" \
        -comp xz -Xbcj x86 -b 1M -no-duplicates
    
    # Copy kernel and initramfs
    echo -e "${YELLOW}[BUILD]${NC} Copying boot files..."
    mkdir -p "${WORK_DIR}/staging/live"
    cp "${WORK_DIR}/rootfs/boot/vmlinuz-"* "${WORK_DIR}/staging/live/vmlinuz" 2>/dev/null || \
        echo "Note: Using default kernel"
    cp "${WORK_DIR}/rootfs/boot/initramfs-"* "${WORK_DIR}/staging/live/initrd" 2>/dev/null || \
        echo "Note: Using default initrd"
    
    # Create GRUB config
    cat > "${WORK_DIR}/staging/boot/grub/grub.cfg" << 'GRUB_EOF'
set timeout=10
set default=0

menuentry "VA21 Research OS (Alpine Edition)" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}

menuentry "VA21 Research OS (Safe Mode)" {
    linux /live/vmlinuz boot=live single
    initrd /live/initrd
}

menuentry "Memory Test" {
    linux16 /boot/memtest86+.bin
}
GRUB_EOF

    # Create ISO
    echo -e "${YELLOW}[BUILD]${NC} Creating ISO..."
    grub-mkrescue -o "${OUTPUT_DIR}/${ISO_NAME}" "${WORK_DIR}/staging" 2>/dev/null || \
        xorriso -as mkisofs \
            -iso-level 3 \
            -full-iso9660-filenames \
            -volid "VA21_ALPINE" \
            -eltorito-boot boot/grub/i386-pc/eltorito.img \
            -no-emul-boot \
            -boot-load-size 4 \
            -boot-info-table \
            -isohybrid-mbr /usr/lib/grub/i386-pc/boot_hybrid.img \
            -output "${OUTPUT_DIR}/${ISO_NAME}" \
            "${WORK_DIR}/staging"
    
    # Create checksum
    cd "${OUTPUT_DIR}"
    sha256sum "${ISO_NAME}" > "${ISO_NAME}.sha256"
    
    echo -e "${GREEN}[BUILD]${NC} Alpine ISO created: ${OUTPUT_DIR}/${ISO_NAME}"
    echo -e "${GREEN}[BUILD]${NC} Size: $(du -h "${OUTPUT_DIR}/${ISO_NAME}" | cut -f1)"
}

# Clean build artifacts
clean() {
    echo -e "${YELLOW}[CLEAN]${NC} Cleaning build artifacts..."
    rm -rf "${BUILD_DIR}"
    echo -e "${GREEN}[CLEAN]${NC} Done"
}

# Show usage
usage() {
    echo "Usage: $0 [debian|alpine|all|clean]"
    echo ""
    echo "Commands:"
    echo "  debian  - Build Debian edition ISO"
    echo "  alpine  - Build Alpine edition ISO"
    echo "  all     - Build both editions"
    echo "  clean   - Remove build artifacts"
    echo ""
    echo "Output:"
    echo "  output/va21-debian-${VERSION}-x86_64.iso"
    echo "  output/va21-alpine-${VERSION}-x86_64.iso"
}

# Main
main() {
    mkdir -p "${OUTPUT_DIR}"
    
    case "${1:-all}" in
        debian)
            check_dependencies
            build_debian_iso
            ;;
        alpine)
            check_dependencies
            build_alpine_iso
            ;;
        all)
            check_dependencies
            build_debian_iso
            build_alpine_iso
            ;;
        clean)
            clean
            ;;
        *)
            usage
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[DONE]${NC} Build complete!"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "ISO files are in: ${OUTPUT_DIR}/"
    ls -lh "${OUTPUT_DIR}"/*.iso 2>/dev/null || echo "No ISO files found yet"
}

main "$@"
