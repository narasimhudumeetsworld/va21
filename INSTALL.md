# VA21 OS - Installation Guide

**Om Vinayaka** 🙏

## Quick Installation

### From ISO (Recommended)

Download the VA21 OS ISO from the [Releases page](../../releases) and install like any Linux distribution:

```bash
# Write ISO to USB drive
sudo dd if=va21-os.iso of=/dev/sdX bs=4M status=progress

# Or use in VirtualBox/VMware
# Create VM → Use ISO as boot disk → Install
```

### Build ISO from Source

```bash
git clone https://github.com/narasimhudumeetsworld/va21.git
cd va21/va21_system/linux_os
./scripts/build_iso.sh debian
# ISO will be in output/ directory
```

**What the installation provides:**
- ✅ Full VA21 OS with Zork-style interface
- ✅ Guardian AI security protection
- ✅ All research and writing tools
- ✅ Tiling window manager
- ✅ Privacy-respecting search (SearXNG)
- ✅ ClamAV antivirus integration

## System Requirements

### Minimum Requirements (7GB RAM)
- **Debian-based Linux** (Debian 12+, Ubuntu 22.04+, Linux Mint 21+)
- **Python 3.8+**
- **7GB RAM** minimum for standard usage
- **5GB disk space** for VA21 OS base installation

### Recommended Requirements (10GB RAM)
- **8-10GB RAM** for heavy multitasking with all AI features
- **10GB disk space** for full installation with all AI models
- **Modern CPU** (Intel Core i5/AMD Ryzen 5 or better)
- **SSD storage** for faster model loading

### Memory Usage by Scenario

| Usage Scenario | RAM Required | Description |
|---------------|--------------|-------------|
| Minimal | ~3GB | Basic browsing, text editing |
| Standard | ~5GB | Multiple apps, AI chat |
| Heavy Multitasking | ~7GB | Many apps, FARA compatibility |
| Full Development | ~9GB | All AI features, IDE |

### Memory Optimization Features
VA21 OS uses dynamic context-aware AI activation:
- 🧠 **Lazy Loading** - Models loaded only when needed
- 📦 **Dynamic Quantization** - 4-bit, 5-bit, or 8-bit based on available RAM
- 🔄 **Context-Aware Unloading** - Automatic memory management
- 💾 **Memory Mapping** - Efficient large file handling

**Security Features Included:**
- 🛡️ Guardian AI Security Core
- 🔒 Air Gap Browser Protection  
- 🕵️ Real-time Threat Intelligence
- 🔄 Self-Analysis & Healing
- ⏱️ 5-Day Quarantine Protocol
- 🌐 Localhost-only Operation
- 🔌 FARA App Compatibility Layer (Alpha)