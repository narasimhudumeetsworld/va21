#!/bin/bash
# VA21 Research OS - Real Linux Kernel Build Script
# ==================================================
# Builds a minimal Linux kernel with Guardian AI security hooks
#
# Requirements:
#   - build-essential, libncurses-dev, flex, bison, libssl-dev, libelf-dev
#   - bc, cpio, xz-utils
#
# Usage: ./build_kernel.sh [version]
#
# Om Vinayaka - Real kernel, real security.

set -e

KERNEL_VERSION="${1:-6.6.10}"  # LTS kernel
KERNEL_URL="https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KERNEL_VERSION}.tar.xz"
BUILD_DIR="/tmp/va21-kernel-build"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../kernel/va21_kernel.config"
OUTPUT_DIR="${SCRIPT_DIR}/../output"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << 'EOF'
 ██╗   ██╗ █████╗ ██████╗  ██╗    ██╗  ██╗███████╗██████╗ ███╗   ██╗███████╗██╗     
 ██║   ██║██╔══██╗╚════██╗███║    ██║ ██╔╝██╔════╝██╔══██╗████╗  ██║██╔════╝██║     
 ██║   ██║███████║ █████╔╝╚██║    █████╔╝ █████╗  ██████╔╝██╔██╗ ██║█████╗  ██║     
 ╚██╗ ██╔╝██╔══██║██╔═══╝  ██║    ██╔═██╗ ██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝  ██║     
  ╚████╔╝ ██║  ██║███████╗ ██║    ██║  ██╗███████╗██║  ██║██║ ╚████║███████╗███████╗
   ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
                        Real Linux Kernel Build System
EOF
echo -e "${NC}"

echo -e "${GREEN}Building VA21 Linux Kernel v${KERNEL_VERSION}${NC}"
echo "=============================================="

# Check dependencies
check_deps() {
    echo -e "${YELLOW}Checking build dependencies...${NC}"
    local deps=("gcc" "make" "flex" "bison" "bc" "cpio" "xz")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Missing dependencies: ${missing[*]}${NC}"
        echo "Install with: sudo apt-get install build-essential libncurses-dev flex bison libssl-dev libelf-dev bc cpio"
        exit 1
    fi
    
    echo -e "${GREEN}All dependencies satisfied.${NC}"
}

# Download kernel
download_kernel() {
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    
    if [ ! -f "linux-${KERNEL_VERSION}.tar.xz" ]; then
        echo -e "${YELLOW}Downloading Linux kernel ${KERNEL_VERSION}...${NC}"
        wget -q --show-progress "$KERNEL_URL" || curl -L -O "$KERNEL_URL"
    else
        echo -e "${GREEN}Kernel archive already downloaded.${NC}"
    fi
    
    if [ ! -d "linux-${KERNEL_VERSION}" ]; then
        echo -e "${YELLOW}Extracting kernel source...${NC}"
        tar xf "linux-${KERNEL_VERSION}.tar.xz"
    fi
}

# Configure kernel
configure_kernel() {
    cd "${BUILD_DIR}/linux-${KERNEL_VERSION}"
    
    echo -e "${YELLOW}Applying VA21 kernel configuration...${NC}"
    
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" .config
        make olddefconfig
    else
        echo -e "${YELLOW}No custom config found, using minimal defconfig...${NC}"
        make defconfig
        
        # Enable critical security features
        ./scripts/config --enable CONFIG_BPF
        ./scripts/config --enable CONFIG_BPF_SYSCALL
        ./scripts/config --enable CONFIG_BPF_LSM
        ./scripts/config --enable CONFIG_SECCOMP
        ./scripts/config --enable CONFIG_SECCOMP_FILTER
        ./scripts/config --enable CONFIG_SECURITY
        ./scripts/config --enable CONFIG_SECURITY_SELINUX
        ./scripts/config --enable CONFIG_SECURITY_APPARMOR
        ./scripts/config --enable CONFIG_SECURITY_LANDLOCK
        ./scripts/config --enable CONFIG_SECURITY_YAMA
        ./scripts/config --enable CONFIG_AUDIT
        ./scripts/config --enable CONFIG_AUDITSYSCALL
        ./scripts/config --set-str CONFIG_LOCALVERSION "-va21"
        ./scripts/config --set-str CONFIG_DEFAULT_HOSTNAME "va21"
        
        make olddefconfig
    fi
}

# Build kernel
build_kernel() {
    cd "${BUILD_DIR}/linux-${KERNEL_VERSION}"
    
    local cpus=$(nproc)
    echo -e "${YELLOW}Building kernel with ${cpus} CPUs...${NC}"
    
    make -j${cpus} bzImage
    make -j${cpus} modules
    
    echo -e "${GREEN}Kernel build complete!${NC}"
}

# Package output
package_output() {
    mkdir -p "$OUTPUT_DIR"
    
    echo -e "${YELLOW}Packaging kernel...${NC}"
    
    cp "${BUILD_DIR}/linux-${KERNEL_VERSION}/arch/x86/boot/bzImage" "${OUTPUT_DIR}/vmlinuz-va21"
    cp "${BUILD_DIR}/linux-${KERNEL_VERSION}/.config" "${OUTPUT_DIR}/config-va21"
    cp "${BUILD_DIR}/linux-${KERNEL_VERSION}/System.map" "${OUTPUT_DIR}/System.map-va21"
    
    # Install modules to temp location
    make -C "${BUILD_DIR}/linux-${KERNEL_VERSION}" INSTALL_MOD_PATH="${OUTPUT_DIR}/modules" modules_install
    
    echo -e "${GREEN}Kernel packaged to: ${OUTPUT_DIR}${NC}"
    echo ""
    echo "Files created:"
    ls -la "$OUTPUT_DIR"
}

# Main
main() {
    check_deps
    download_kernel
    configure_kernel
    build_kernel
    package_output
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  VA21 Kernel Build Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Kernel: ${OUTPUT_DIR}/vmlinuz-va21"
    echo ""
    echo "Next steps:"
    echo "  1. Build initramfs: ./build_initramfs.sh"
    echo "  2. Create bootable image: ./create_image.sh"
    echo "  3. Run in QEMU: ./run_qemu.sh"
}

main "$@"
