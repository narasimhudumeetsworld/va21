#!/bin/bash
# VA21 Research OS - Quick Start Script
# Works with Docker, Podman, or VirtualBox
#
# Usage:
#   ./run.sh              # Auto-detect and run
#   ./run.sh docker       # Force Docker
#   ./run.sh podman       # Force Podman
#   ./run.sh vbox         # Create VirtualBox image

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Banner
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
 ██╗   ██╗ █████╗ ██████╗  ██╗
 ██║   ██║██╔══██╗╚════██╗███║
 ██║   ██║███████║ █████╔╝╚██║
 ╚██╗ ██╔╝██╔══██║██╔═══╝  ██║
  ╚████╔╝ ██║  ██║███████╗ ██║
   ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═╝
    Research OS v1.0 (Vinayaka)
EOF
    echo -e "${NC}"
    echo -e "${GREEN}Om Vinayaka - Secure Research Environment${NC}"
    echo ""
}

# Check for container runtime
detect_runtime() {
    if command -v docker &> /dev/null; then
        echo "docker"
    elif command -v podman &> /dev/null; then
        echo "podman"
    else
        echo "none"
    fi
}

# Build the image
build_image() {
    local runtime=$1
    echo -e "${YELLOW}Building VA21 Research OS image...${NC}"
    
    if [ "$runtime" == "docker" ]; then
        docker build -t va21-research-os:latest .
    else
        podman build -t va21-research-os:latest .
    fi
    
    echo -e "${GREEN}Build complete!${NC}"
}

# Run with Docker
run_docker() {
    echo -e "${BLUE}Starting VA21 Research OS with Docker...${NC}"
    
    # Check if image exists, build if not
    if ! docker image inspect va21-research-os:latest &> /dev/null; then
        build_image "docker"
    fi
    
    # Run the container interactively
    docker run -it --rm \
        --name va21-os \
        --hostname va21 \
        -v va21_research:/home/researcher/research \
        -v va21_notes:/home/researcher/notes \
        -v va21_vault:/va21/vault \
        -e TERM=xterm-256color \
        va21-research-os:latest zork
}

# Run with Podman
run_podman() {
    echo -e "${BLUE}Starting VA21 Research OS with Podman...${NC}"
    
    # Check if image exists, build if not
    if ! podman image inspect va21-research-os:latest &> /dev/null; then
        build_image "podman"
    fi
    
    # Run the container interactively
    podman run -it --rm \
        --name va21-os \
        --hostname va21 \
        -v va21_research:/home/researcher/research \
        -v va21_notes:/home/researcher/notes \
        -v va21_vault:/va21/vault \
        -e TERM=xterm-256color \
        va21-research-os:latest zork
}

# Run with Docker Compose
run_compose() {
    local runtime=$1
    echo -e "${BLUE}Starting VA21 Research OS with ${runtime}-compose...${NC}"
    
    if [ "$runtime" == "docker" ]; then
        docker-compose up -d
        echo -e "${GREEN}VA21 OS started in background.${NC}"
        echo -e "To enter the Zork interface: ${YELLOW}docker-compose exec va21 va21${NC}"
        echo -e "To view logs: ${YELLOW}docker-compose logs -f${NC}"
        echo -e "To stop: ${YELLOW}docker-compose down${NC}"
    else
        podman-compose up -d
        echo -e "${GREEN}VA21 OS started in background.${NC}"
        echo -e "To enter the Zork interface: ${YELLOW}podman-compose exec va21 va21${NC}"
    fi
}

# Create VirtualBox image
create_vbox() {
    echo -e "${BLUE}Creating VirtualBox image...${NC}"
    echo -e "${YELLOW}Note: This requires docker/buildx and additional tools.${NC}"
    
    # Check for required tools
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is required to build VirtualBox image.${NC}"
        exit 1
    fi
    
    # Build the image first
    build_image "docker"
    
    # Export to tar
    echo "Exporting container filesystem..."
    docker create --name va21-export va21-research-os:latest
    docker export va21-export > va21-rootfs.tar
    docker rm va21-export
    
    echo -e "${GREEN}Filesystem exported to va21-rootfs.tar${NC}"
    echo -e "${YELLOW}To create a VirtualBox VM:${NC}"
    echo "1. Create a new VM in VirtualBox (Linux/Other Linux 64-bit)"
    echo "2. Use the Alpine Linux ISO to boot"
    echo "3. Extract va21-rootfs.tar to the VM's filesystem"
    echo "4. Configure boot loader"
    echo ""
    echo "For a pre-built VM, check the releases page."
}

# Show help
show_help() {
    echo "VA21 Research OS - Run Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  (none)     Auto-detect runtime and start interactively"
    echo "  docker     Force Docker runtime"
    echo "  podman     Force Podman runtime"
    echo "  compose    Start with docker-compose (background)"
    echo "  build      Build the image only"
    echo "  vbox       Create VirtualBox-compatible image"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Auto-detect and run"
    echo "  $0 docker       # Run with Docker"
    echo "  $0 compose      # Start in background with compose"
}

# Main
main() {
    show_banner
    
    local command=${1:-auto}
    
    case "$command" in
        auto)
            runtime=$(detect_runtime)
            if [ "$runtime" == "none" ]; then
                echo -e "${RED}No container runtime found!${NC}"
                echo "Please install Docker or Podman."
                echo ""
                echo "Docker: https://docs.docker.com/get-docker/"
                echo "Podman: https://podman.io/getting-started/installation"
                exit 1
            fi
            echo -e "${GREEN}Detected: $runtime${NC}"
            if [ "$runtime" == "docker" ]; then
                run_docker
            else
                run_podman
            fi
            ;;
        docker)
            run_docker
            ;;
        podman)
            run_podman
            ;;
        compose)
            runtime=$(detect_runtime)
            run_compose "$runtime"
            ;;
        build)
            runtime=$(detect_runtime)
            build_image "$runtime"
            ;;
        vbox|virtualbox)
            create_vbox
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
