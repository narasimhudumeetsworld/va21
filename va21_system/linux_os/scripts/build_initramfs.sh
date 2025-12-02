#!/bin/bash
# VA21 Research OS - Initramfs Build Script
# ==========================================
# Creates the initial RAM filesystem with Guardian AI
#
# Om Vinayaka - The first breath of the system.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/../output"
INITRAMFS_DIR="${OUTPUT_DIR}/initramfs"
ROOTFS_DIR="${OUTPUT_DIR}/rootfs"

echo "Building VA21 Initramfs..."

# Create directory structure
mkdir -p "${INITRAMFS_DIR}"/{bin,sbin,etc,proc,sys,dev,tmp,run,var,usr/{bin,sbin,lib},lib,lib64,home/researcher,va21/{guardian,vault,logs,config}}

# Create init script
cat > "${INITRAMFS_DIR}/init" << 'INIT_EOF'
#!/bin/busybox sh
# VA21 Research OS - Init Script
# Real Linux init with Guardian AI

# Mount essential filesystems
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
mount -t tmpfs none /tmp
mount -t tmpfs none /run

# Set hostname
hostname va21

# Setup console
exec 0</dev/console
exec 1>/dev/console
exec 2>/dev/console

# Display boot message
clear
cat << 'BANNER'

  ██╗   ██╗ █████╗ ██████╗  ██╗     ██████╗ ███████╗
  ██║   ██║██╔══██╗╚════██╗███║    ██╔═══██╗██╔════╝
  ██║   ██║███████║ █████╔╝╚██║    ██║   ██║███████╗
  ╚██╗ ██╔╝██╔══██║██╔═══╝  ██║    ██║   ██║╚════██║
   ╚████╔╝ ██║  ██║███████╗ ██║    ╚██████╔╝███████║
    ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═╝     ╚═════╝ ╚══════╝
           Research OS - Real Linux Kernel

                   Om Vinayaka

BANNER

echo "[INIT] VA21 Research OS starting..."
echo "[INIT] Kernel: $(uname -r)"
echo "[INIT] Architecture: $(uname -m)"

# Load essential kernel modules
echo "[INIT] Loading kernel modules..."
modprobe virtio_blk 2>/dev/null || true
modprobe virtio_net 2>/dev/null || true
modprobe e1000 2>/dev/null || true

# Start udev or mdev
if [ -x /sbin/udevd ]; then
    echo "[INIT] Starting udev..."
    /sbin/udevd --daemon
    udevadm trigger
    udevadm settle
else
    echo "[INIT] Starting mdev..."
    echo /sbin/mdev > /proc/sys/kernel/hotplug
    mdev -s
fi

# Setup networking
echo "[INIT] Configuring network..."
ip link set lo up
ip link set eth0 up 2>/dev/null || true
udhcpc -i eth0 -q 2>/dev/null || true

# Mount root filesystem if available
if [ -b /dev/vda ]; then
    echo "[INIT] Mounting root filesystem..."
    mkdir -p /mnt/root
    mount /dev/vda /mnt/root
    if [ -x /mnt/root/sbin/init ]; then
        echo "[INIT] Switching to root filesystem..."
        exec switch_root /mnt/root /sbin/init
    fi
fi

# Initialize Guardian AI
echo "[INIT] Initializing Guardian AI..."
if [ -f /va21/guardian/guardian_core.py ]; then
    python3 /va21/guardian/guardian_core.py --daemon &
    echo "[INIT] Guardian AI started (PID: $!)"
fi

# Start VA21 Zork Interface
echo ""
echo "[INIT] Starting VA21 Research OS Interface..."
echo ""

if [ -f /va21/zork_shell/zork_interface.py ]; then
    exec python3 /va21/zork_shell/zork_interface.py
else
    # Fallback to shell
    echo "Welcome to VA21 Research OS"
    echo "Type 'help' for commands"
    exec /bin/sh
fi
INIT_EOF

chmod +x "${INITRAMFS_DIR}/init"

# Download and install BusyBox (static)
echo "Installing BusyBox..."
BUSYBOX_URL="https://busybox.net/downloads/binaries/1.35.0-x86_64-linux-musl/busybox"
if command -v wget &> /dev/null; then
    wget -q -O "${INITRAMFS_DIR}/bin/busybox" "$BUSYBOX_URL" || echo "Using system busybox"
elif command -v curl &> /dev/null; then
    curl -sL -o "${INITRAMFS_DIR}/bin/busybox" "$BUSYBOX_URL" || echo "Using system busybox"
fi

# If download failed, try to copy system busybox
if [ ! -f "${INITRAMFS_DIR}/bin/busybox" ] || [ ! -s "${INITRAMFS_DIR}/bin/busybox" ]; then
    if command -v busybox &> /dev/null; then
        cp "$(which busybox)" "${INITRAMFS_DIR}/bin/busybox"
    fi
fi

chmod +x "${INITRAMFS_DIR}/bin/busybox"

# Create busybox symlinks
cd "${INITRAMFS_DIR}/bin"
for cmd in sh ash cat cp dd df echo grep kill ln ls mkdir mknod mount mv ps rm sed sh sleep tar touch umount uname; do
    ln -sf busybox $cmd 2>/dev/null || true
done

cd "${INITRAMFS_DIR}/sbin"
for cmd in init halt reboot poweroff ifconfig ip route mdev switch_root modprobe; do
    ln -sf ../bin/busybox $cmd 2>/dev/null || true
done

# Copy VA21 components
echo "Copying VA21 components..."
cp -r "${SCRIPT_DIR}/../guardian" "${INITRAMFS_DIR}/va21/" 2>/dev/null || true
cp -r "${SCRIPT_DIR}/../zork_shell" "${INITRAMFS_DIR}/va21/" 2>/dev/null || true
cp -r "${SCRIPT_DIR}/../searxng" "${INITRAMFS_DIR}/va21/" 2>/dev/null || true
cp -r "${SCRIPT_DIR}/../obsidian" "${INITRAMFS_DIR}/va21/" 2>/dev/null || true

# Create etc files
cat > "${INITRAMFS_DIR}/etc/passwd" << 'EOF'
root:x:0:0:root:/root:/bin/sh
researcher:x:1000:1000:VA21 Researcher:/home/researcher:/bin/sh
EOF

cat > "${INITRAMFS_DIR}/etc/group" << 'EOF'
root:x:0:
researcher:x:1000:
EOF

cat > "${INITRAMFS_DIR}/etc/hostname" << 'EOF'
va21
EOF

# Create initramfs cpio archive
echo "Creating initramfs archive..."
cd "${INITRAMFS_DIR}"
find . | cpio -H newc -o | gzip > "${OUTPUT_DIR}/initramfs-va21.img"

echo ""
echo "Initramfs created: ${OUTPUT_DIR}/initramfs-va21.img"
echo "Size: $(du -h "${OUTPUT_DIR}/initramfs-va21.img" | cut -f1)"
