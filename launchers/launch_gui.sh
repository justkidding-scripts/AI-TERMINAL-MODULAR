#!/bin/bash
# AI Terminal GUI Launcher
# Enhanced launcher script for AI Terminal with GUI option

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
PYTHON_CMD="python3"
OLLAMA_PATH="/home/nike/ollama-enhancements"
VENV_PATH="$SCRIPT_DIR/venv"

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
    echo "║                    🤖 AI Enhanced Terminal                   ║"
    echo "║                 Modern Terminal with AI Support              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_usage() {
    echo -e "${YELLOW}Usage: $0 [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  -g, --gui         Launch GUI version (default)"
    echo "  -r, --real        Launch real terminal GUI (VTE-based)"
    echo "  -c, --cli         Launch CLI/terminal version"
    echo "  -s, --setup       Setup environment and dependencies"
    echo "  -t, --test        Test Ollama connectivity"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Launch GUI version"
    echo "  $0 --gui          # Launch GUI version explicitly"
    echo "  $0 --cli          # Launch CLI version"
    echo "  $0 --setup        # Setup environment"
}

check_requirements() {
    echo -e "${BLUE}🔍 Checking requirements...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"
    
    # Check tkinter for GUI
    if python3 -c "import tkinter" 2>/dev/null; then
        echo -e "${GREEN}✅ tkinter available for GUI${NC}"
    else
        echo -e "${YELLOW}⚠️ tkinter not available - GUI mode may not work${NC}"
    fi
    
    # Check Ollama path
    if [ -d "$OLLAMA_PATH" ]; then
        echo -e "${GREEN}✅ Ollama enhancements found at: $OLLAMA_PATH${NC}"
    else
        echo -e "${YELLOW}⚠️ Ollama enhancements not found at: $OLLAMA_PATH${NC}"
        echo -e "${YELLOW}   AI features may be limited${NC}"
    fi
    
    # Check if Ollama is running
    if command -v ollama &> /dev/null && ollama list &>/dev/null; then
        echo -e "${GREEN}✅ Ollama is running${NC}"
    else
        echo -e "${YELLOW}⚠️ Ollama not running or not installed${NC}"
        echo -e "${YELLOW}   AI features will use fallback mode${NC}"
    fi
}

setup_environment() {
    echo -e "${BLUE}🚀 Setting up environment...${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${CYAN}Creating virtual environment...${NC}"
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Install requirements
    echo -e "${CYAN}Installing/updating requirements...${NC}"
    
    # Basic requirements
    pip install --upgrade pip
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        echo -e "${CYAN}Creating requirements.txt...${NC}"
        cat > requirements.txt << EOF
# Core dependencies
requests>=2.25.0

# Optional GUI dependencies
tkinter-dev>=3.0.0; platform_system != "Windows"

# Optional AI dependencies
ollama>=0.1.0
transformers>=4.20.0
torch>=1.12.0

# Optional development dependencies
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
EOF
    fi
    
    # Install requirements (skip packages that fail)
    pip install -r requirements.txt || echo -e "${YELLOW}⚠️ Some packages failed to install${NC}"
    
    echo -e "${GREEN}✅ Environment setup complete${NC}"
}

test_ollama() {
    echo -e "${BLUE}🧪 Testing Ollama connectivity...${NC}"
    
    # Test basic Ollama connection
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✅ Ollama command found${NC}"
        
        if ollama list &>/dev/null; then
            echo -e "${GREEN}✅ Ollama service is running${NC}"
            echo -e "${CYAN}Available models:${NC}"
            ollama list
        else
            echo -e "${RED}❌ Ollama service not running${NC}"
            echo -e "${YELLOW}Try: ollama serve${NC}"
        fi
    else
        echo -e "${RED}❌ Ollama not installed${NC}"
        echo -e "${YELLOW}Install from: https://ollama.ai${NC}"
    fi
    
    # Test Python Ollama integration
    echo -e "${CYAN}Testing Python integration...${NC}"
    python3 << EOF
import sys
sys.path.insert(0, "$OLLAMA_PATH")

try:
    from code_assistant.code_assistant import CodeAssistant
    print("✅ Ollama Python integration working")
    
    # Test basic functionality
    assistant = CodeAssistant()
    print("✅ CodeAssistant initialized successfully")
except ImportError as e:
    print(f"⚠️ Import error: {e}")
except Exception as e:
    print(f"⚠️ Integration error: {e}")
EOF
}

launch_cli() {
    echo -e "${BLUE}🚀 Launching CLI version...${NC}"
    
    if [ -f "ai_terminal_enhanced.py" ]; then
        python3 ai_terminal_enhanced.py "$@"
    elif [ -f "ai_terminal.py" ]; then
        python3 ai_terminal.py "$@"
    else
        echo -e "${RED}❌ No CLI terminal script found${NC}"
        exit 1
    fi
}

launch_gui() {
    echo -e "${BLUE}🚀 Launching GUI version...${NC}"
    
    # Check if GUI script exists
    if [ ! -f "ai_terminal_gui.py" ]; then
        echo -e "${RED}❌ GUI script not found: ai_terminal_gui.py${NC}"
        exit 1
    fi
    
    # Check for display (X11)
    if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
        echo -e "${RED}❌ No display server found (DISPLAY or WAYLAND_DISPLAY)${NC}"
        echo -e "${YELLOW}GUI mode requires a desktop environment${NC}"
        echo -e "${CYAN}Falling back to CLI mode...${NC}"
        launch_cli "$@"
        return
    fi
    
    # Test tkinter availability
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo -e "${RED}❌ tkinter not available${NC}"
        echo -e "${YELLOW}Install with: sudo apt install python3-tk${NC}"
        echo -e "${CYAN}Falling back to CLI mode...${NC}"
        launch_cli "$@"
        return
    fi
    
    # Launch GUI
    python3 ai_terminal_gui.py "$@"
}

launch_real_terminal() {
    echo -e "${BLUE}🚀 Launching Real Terminal GUI...${NC}"
    
    # Check if real terminal script exists
    if [ ! -f "real_terminal_gui.py" ]; then
        echo -e "${RED}❌ Real terminal script not found: real_terminal_gui.py${NC}"
        exit 1
    fi
    
    # Check for display
    if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
        echo -e "${RED}❌ No display server found${NC}"
        echo -e "${CYAN}Falling back to CLI mode...${NC}"
        launch_cli "$@"
        return
    fi
    
    # Test VTE availability
    if ! python3 -c "import gi; gi.require_version('Vte', '2.91'); from gi.repository import Vte" 2>/dev/null; then
        echo -e "${YELLOW}⚠️ VTE not available - install with:${NC}"
        echo -e "${CYAN}sudo apt install libvte-2.91-dev python3-gi-cairo gir1.2-vte-2.91${NC}"
        echo -e "${CYAN}Falling back to basic GUI...${NC}"
        launch_gui "$@"
        return
    fi
    
    # Launch real terminal
    python3 real_terminal_gui.py "$@"
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
            check_requirements
            setup_environment
            exit 0
            ;;
        -t|--test)
            check_requirements
            test_ollama
            exit 0
            ;;
        -c|--cli)
            shift
            check_requirements
            launch_cli "$@"
            ;;
        -r|--real)
            shift
            check_requirements
            launch_real_terminal "$@"
            ;;
        -g|--gui|"")
            shift
            check_requirements
            launch_gui "$@"
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