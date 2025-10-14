#!/bin/bash
# AI Terminal Modular - Universal Launcher
# Automatically detects and launches the best available terminal interface

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🤖 AI Enhanced Terminal - MODULAR               ║"
    echo "║           Advanced AI Terminal with Multiple Interfaces      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_usage() {
    echo -e "${YELLOW}Usage: $0 [OPTIONS]${NC}"
    echo ""
    echo "Interface Options:"
    echo "  -w, --warp        Launch Warp-style unified AI terminal [NEW & RECOMMENDED]"
    echo "  -r, --real        Launch real terminal GUI (VTE-based)"
    echo "  -g, --gui         Launch basic GUI version (tkinter)"
    echo "  -e, --enhanced    Launch enhanced CLI version"
    echo "  -c, --cli         Launch basic CLI version"
    echo "  -a, --auto        Auto-detect best interface (default)"
    echo ""
    echo "Utility Options:"
    echo "  -s, --setup       Setup environment and dependencies"
    echo "  -t, --test        Test all components and connectivity"
    echo "  -i, --install     Install system dependencies"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Auto-detect best interface"
    echo "  $0 --warp         # Launch Warp-style terminal (BEST experience)"
    echo "  $0 --real         # Launch real terminal (good experience)"
    echo "  $0 --setup        # Setup everything"
    echo "  $0 --test         # Test all components"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Python 3: $(python3 --version)${NC}"
    return 0
}

check_display() {
    if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
        echo -e "${RED}❌ No display server (GUI unavailable)${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Display server available${NC}"
    return 0
}

check_tkinter() {
    if python3 -c "import tkinter" 2>/dev/null; then
        echo -e "${GREEN}✅ tkinter available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ tkinter not available${NC}"
        return 1
    fi
}

check_vte() {
    if python3 -c "import gi; gi.require_version('Vte', '2.91'); from gi.repository import Vte" 2>/dev/null; then
        echo -e "${GREEN}✅ VTE available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ VTE not available${NC}"
        return 1
    fi
}

check_ollama() {
    if command -v ollama &> /dev/null && ollama list &>/dev/null; then
        echo -e "${GREEN}✅ Ollama running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Ollama not running${NC}"
        return 1
    fi
}

setup_environment() {
    echo -e "${BLUE}🚀 Setting up AI Terminal environment...${NC}"
    
    # Run setup script if available
    if [ -f "launchers/setup.sh" ]; then
        chmod +x launchers/setup.sh
        ./launchers/setup.sh
    else
        echo -e "${YELLOW}⚠️ Setup script not found, manual setup required${NC}"
    fi
}

install_dependencies() {
    echo -e "${BLUE}📦 Installing system dependencies...${NC}"
    
    # Check if running as root or with sudo access
    if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
        # Install Python and basic deps
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            
            # GUI dependencies
            sudo apt install -y python3-tk python3-gi python3-gi-cairo
            
            # VTE dependencies
            sudo apt install -y libvte-2.91-dev gir1.2-vte-2.91 gir1.2-gtk-3.0
            
            echo -e "${GREEN}✅ Dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚠️ apt not available, manual installation required${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Sudo access required for dependency installation${NC}"
        echo "Run: sudo $0 --install"
    fi
}

test_components() {
    echo -e "${BLUE}🧪 Testing all components...${NC}"
    
    echo -e "${CYAN}System Checks:${NC}"
    check_python
    check_display
    check_tkinter
    check_vte
    check_ollama
    
    echo -e "\n${CYAN}Component Tests:${NC}"
    
    # Test core terminals
    for terminal in "core/ai_terminal_basic.py" "core/ai_terminal_enhanced.py"; do
        if [ -f "$terminal" ]; then
            echo -e "${GREEN}✅ Found: $(basename "$terminal")${NC}"
        else
            echo -e "${RED}❌ Missing: $(basename "$terminal")${NC}"
        fi
    done
    
    # Test GUI terminals  
    for gui in "core/warp_terminal_gui.py" "core/ai_terminal_gui.py" "core/real_terminal_gui.py"; do
        if [ -f "$gui" ]; then
            echo -e "${GREEN}✅ Found: $(basename "$gui")${NC}"
        else
            echo -e "${RED}❌ Missing: $(basename "$gui")${NC}"
        fi
    done
    
    # Test modules
    if [ -f "modules/rag_integration/rag.py" ]; then
        echo -e "${GREEN}✅ RAG system available${NC}"
    else
        echo -e "${YELLOW}⚠️ RAG system not found${NC}"
    fi
    
    echo -e "\n${CYAN}Recommendation:${NC}"
    if check_vte && check_display && [ -f "core/warp_terminal_gui.py" ]; then
        echo -e "${GREEN}🎯 Use: $0 --warp (BEST - unified AI+terminal)${NC}"
    elif check_vte && check_display; then
        echo -e "${GREEN}🎯 Use: $0 --real (good experience)${NC}"
    elif check_tkinter && check_display; then
        echo -e "${YELLOW}🎯 Use: $0 --gui (basic GUI)${NC}"
    else
        echo -e "${BLUE}🎯 Use: $0 --enhanced (CLI experience)${NC}"
    fi
}

launch_warp_terminal() {
    echo -e "${BLUE}🚀 Launching Warp-Style AI Terminal...${NC}"
    
    if [ ! -f "core/warp_terminal_gui.py" ]; then
        echo -e "${RED}❌ Warp terminal not found${NC}"
        fallback_launch
        return
    fi
    
    if ! check_display || ! check_vte; then
        echo -e "${YELLOW}⚠️ Requirements not met for Warp terminal${NC}"
        fallback_launch
        return
    fi
    
    python3 core/warp_terminal_gui.py "$@"
}

launch_real_terminal() {
    echo -e "${BLUE}🚀 Launching Real Terminal GUI...${NC}"
    
    if [ ! -f "core/real_terminal_gui.py" ]; then
        echo -e "${RED}❌ Real terminal not found${NC}"
        fallback_launch
        return
    fi
    
    if ! check_display || ! check_vte; then
        echo -e "${YELLOW}⚠️ Requirements not met for real terminal${NC}"
        fallback_launch
        return
    fi
    
    python3 core/real_terminal_gui.py "$@"
}

launch_gui_terminal() {
    echo -e "${BLUE}🚀 Launching GUI Terminal...${NC}"
    
    if [ ! -f "core/ai_terminal_gui.py" ]; then
        echo -e "${RED}❌ GUI terminal not found${NC}"
        fallback_launch
        return
    fi
    
    if ! check_display || ! check_tkinter; then
        echo -e "${YELLOW}⚠️ Requirements not met for GUI terminal${NC}"
        fallback_launch
        return
    fi
    
    python3 core/ai_terminal_gui.py "$@"
}

launch_enhanced_cli() {
    echo -e "${BLUE}🚀 Launching Enhanced CLI Terminal...${NC}"
    
    if [ -f "core/ai_terminal_enhanced.py" ]; then
        python3 core/ai_terminal_enhanced.py "$@"
    else
        echo -e "${YELLOW}⚠️ Enhanced CLI not found, using basic...${NC}"
        launch_basic_cli "$@"
    fi
}

launch_basic_cli() {
    echo -e "${BLUE}🚀 Launching Basic CLI Terminal...${NC}"
    
    if [ -f "core/ai_terminal_basic.py" ]; then
        python3 core/ai_terminal_basic.py "$@"
    else
        echo -e "${RED}❌ No terminal implementation found${NC}"
        exit 1
    fi
}

auto_detect_launch() {
    echo -e "${BLUE}🔍 Auto-detecting best interface...${NC}"
    
    if check_display && check_vte && [ -f "core/warp_terminal_gui.py" ]; then
        echo -e "${GREEN}🎯 Launching Warp Terminal (BEST - unified AI+terminal)${NC}"
        launch_warp_terminal "$@"
    elif check_display && check_vte && [ -f "core/real_terminal_gui.py" ]; then
        echo -e "${GREEN}🎯 Launching Real Terminal (good experience)${NC}"
        launch_real_terminal "$@"
    elif check_display && check_tkinter && [ -f "core/ai_terminal_gui.py" ]; then
        echo -e "${YELLOW}🎯 Launching GUI Terminal${NC}"
        launch_gui_terminal "$@"
    elif [ -f "core/ai_terminal_enhanced.py" ]; then
        echo -e "${BLUE}🎯 Launching Enhanced CLI${NC}"
        launch_enhanced_cli "$@"
    else
        echo -e "${CYAN}🎯 Launching Basic CLI${NC}"
        launch_basic_cli "$@"
    fi
}

fallback_launch() {
    echo -e "${CYAN}🔄 Trying fallback options...${NC}"
    
    if check_display && check_vte && [ -f "core/warp_terminal_gui.py" ]; then
        launch_warp_terminal "$@"
    elif check_display && check_tkinter && [ -f "core/ai_terminal_gui.py" ]; then
        launch_gui_terminal "$@"
    elif [ -f "core/ai_terminal_enhanced.py" ]; then
        launch_enhanced_cli "$@"
    else
        launch_basic_cli "$@"
    fi
}

# Main script logic
main() {
    print_banner
    
    # Parse command line arguments
    case "${1:-}" in
        -h|--help)
            print_usage
            exit 0
            ;;
        -s|--setup)
            setup_environment
            exit 0
            ;;
        -i|--install)
            install_dependencies
            exit 0
            ;;
        -t|--test)
            test_components
            exit 0
            ;;
        -w|--warp)
            shift
            launch_warp_terminal "$@"
            ;;
        -r|--real)
            shift
            launch_real_terminal "$@"
            ;;
        -g|--gui)
            shift
            launch_gui_terminal "$@"
            ;;
        -e|--enhanced)
            shift
            launch_enhanced_cli "$@"
            ;;
        -c|--cli)
            shift
            launch_basic_cli "$@"
            ;;
        -a|--auto|"")
            shift
            auto_detect_launch "$@"
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
}

# Error handling
trap 'echo -e "${RED}❌ Script interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"