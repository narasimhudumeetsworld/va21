#!/bin/bash
# VA21 Research OS - Entrypoint Script
# Handles initialization and mode selection

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# VA21 Banner
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

# Initialize Guardian AI
init_guardian() {
    echo -e "${YELLOW}[INIT]${NC} Awakening Guardian AI..."
    
    # Start Guardian monitoring in background
    if [ -f "/va21/guardian/guardian_core.py" ]; then
        python3 /va21/guardian/guardian_core.py --daemon &
        echo -e "${GREEN}[INIT]${NC} Guardian AI: ONLINE"
    else
        echo -e "${YELLOW}[INIT]${NC} Guardian AI: SIMULATION MODE"
    fi
}

# Initialize directories
init_directories() {
    echo -e "${YELLOW}[INIT]${NC} Preparing research environment..."
    
    # Ensure directories exist
    mkdir -p /home/researcher/{research,notes,tools,sandbox}
    mkdir -p /va21/{logs,vault}
    
    echo -e "${GREEN}[INIT]${NC} Research environment ready"
}

# Main entrypoint logic
main() {
    show_banner
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}[BOOT]${NC} Starting VA21 Research OS..."
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    init_directories
    init_guardian
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[BOOT]${NC} System initialization complete"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Handle different run modes
    case "${1:-zork}" in
        zork)
            # Start the Zork-style text adventure interface
            echo -e "${CYAN}Entering the VA21 realm...${NC}"
            echo ""
            exec python3 /va21/zork_shell/zork_interface.py
            ;;
        shell|bash)
            # Drop to bash shell
            echo -e "${YELLOW}Entering direct shell mode...${NC}"
            exec /bin/bash
            ;;
        guardian)
            # Run Guardian AI in foreground
            echo -e "${YELLOW}Starting Guardian AI in foreground...${NC}"
            exec python3 /va21/guardian/guardian_core.py
            ;;
        daemon)
            # Run as daemon (for services)
            echo -e "${YELLOW}Running in daemon mode...${NC}"
            python3 /va21/guardian/guardian_core.py --daemon &
            tail -f /dev/null
            ;;
        *)
            # Run custom command
            exec "$@"
            ;;
    esac
}

main "$@"
