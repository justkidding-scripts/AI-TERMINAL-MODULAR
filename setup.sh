#!/bin/bash
# AI Terminal Modular - Setup Script
# Configures environment and installs Python dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  🛠️ AI Terminal Setup                        ║"
    echo "║              Environment Configuration                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_python() {
    echo -e "${BLUE}🐍 Checking Python...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
        return 0
    else
        echo -e "${RED}❌ Python 3 not found${NC}"
        return 1
    fi
}

create_venv() {
    echo -e "${BLUE}📦 Setting up virtual environment...${NC}"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${YELLOW}⚠️ Virtual environment exists${NC}"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
}

install_python_deps() {
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Python dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️ requirements.txt not found, installing basic deps${NC}"
        pip install numpy requests ollama chromadb
    fi
}

setup_config_dirs() {
    echo -e "${BLUE}📁 Setting up configuration directories...${NC}"
    
    CONFIG_DIR="$HOME/.config/ai-terminal"
    mkdir -p "$CONFIG_DIR"
    
    # Create default config if doesn't exist
    if [ ! -f "$CONFIG_DIR/config.json" ] && [ -f "config/terminal_config.json" ]; then
        cp config/terminal_config.json "$CONFIG_DIR/config.json"
        echo -e "${GREEN}✅ Default terminal config created${NC}"
    fi
    
    if [ ! -f "$CONFIG_DIR/gui_config.json" ] && [ -f "config/ai_config.json" ]; then
        cp config/ai_config.json "$CONFIG_DIR/gui_config.json"
        echo -e "${GREEN}✅ Default GUI config created${NC}"
    fi
    
    # Create RAG storage directory
    mkdir -p "$CONFIG_DIR/rag_storage"
    echo -e "${GREEN}✅ RAG storage directory created${NC}"
}

setup_desktop_integration() {
    echo -e "${BLUE}🖥️ Setting up desktop integration...${NC}"
    
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    
    if [ -f "desktop/ai-terminal.desktop" ]; then
        # Update paths in desktop file
        sed "s|/home/nike/ai-enhanced-terminal|$SCRIPT_DIR|g" desktop/ai-terminal.desktop > "$DESKTOP_DIR/ai-terminal-modular.desktop"
        
        # Update desktop database
        if command -v update-desktop-database &> /dev/null; then
            update-desktop-database "$DESKTOP_DIR"
        fi
        
        echo -e "${GREEN}✅ Desktop integration setup${NC}"
    else
        echo -e "${YELLOW}⚠️ Desktop file not found${NC}"
    fi
}

check_ollama() {
    echo -e "${BLUE}🤖 Checking Ollama...${NC}"
    
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✅ Ollama found${NC}"
        
        # Check if Ollama is running
        if ollama list &>/dev/null; then
            echo -e "${GREEN}✅ Ollama is running${NC}"
            
            # Check for required models
            if ollama list | grep -q "codellama:7b\|llama3.2"; then
                echo -e "${GREEN}✅ AI models available${NC}"
            else
                echo -e "${YELLOW}⚠️ Pulling recommended models...${NC}"
                ollama pull codellama:7b || echo -e "${YELLOW}⚠️ Failed to pull codellama:7b${NC}"
                ollama pull llama3.2 || echo -e "${YELLOW}⚠️ Failed to pull llama3.2${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ Ollama not running${NC}"
            echo -e "${CYAN}💡 Start with: ollama serve${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Ollama not installed${NC}"
        echo -e "${CYAN}💡 Install from: https://ollama.ai${NC}"
    fi
}

create_launcher_symlinks() {
    echo -e "${BLUE}🔗 Creating launcher symlinks...${NC}"
    
    # Create local bin directory
    mkdir -p "$HOME/.local/bin"
    
    # Create symlinks
    ln -sf "$SCRIPT_DIR/launch.sh" "$HOME/.local/bin/ai-terminal"
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}⚠️ ~/.local/bin not in PATH${NC}"
        echo -e "${CYAN}💡 Add to your shell config: export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    else
        echo -e "${GREEN}✅ Symlinks created (ai-terminal command available)${NC}"
    fi
}

test_installation() {
    echo -e "${BLUE}🧪 Testing installation...${NC}"
    
    # Test Python imports
    python3 -c "
import sys
sys.path.insert(0, 'modules/rag_integration')
try:
    import numpy
    print('✅ numpy working')
except ImportError:
    print('❌ numpy not available')

try:
    import requests
    print('✅ requests working')
except ImportError:
    print('❌ requests not available')

try:
    from rag import RAGSkill
    print('✅ RAG system working')
except ImportError as e:
    print(f'⚠️ RAG system: {e}')

try:
    import tkinter
    print('✅ tkinter working')
except ImportError:
    print('❌ tkinter not available')
" 2>/dev/null || echo -e "${YELLOW}⚠️ Some components may not be available${NC}"
    
    echo -e "${GREEN}✅ Installation test complete${NC}"
}

print_success() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   🎉 Setup Complete!                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo -e "  ./launch.sh               # Auto-detect best interface"
    echo -e "  ./launch.sh --real        # Real terminal (recommended)"
    echo -e "  ./launch.sh --test        # Test all components"
    echo
    echo -e "${CYAN}📖 Commands:${NC}"
    echo -e "  ai-terminal               # Launch from anywhere (if PATH configured)"
    echo -e "  rag add ~/Documents       # Index documents"
    echo -e "  rag ask \"What is Python?\" # Query knowledge base"
    echo
    echo -e "${CYAN}📁 Configuration:${NC}"
    echo -e "  ~/.config/ai-terminal/    # Config files"
    echo -e "  ~/.local/bin/ai-terminal  # System command"
}

# Main setup process
main() {
    print_header
    
    echo -e "${BLUE}🔍 Running setup checks...${NC}"
    
    # Core checks
    check_python || { echo -e "${RED}❌ Setup failed: Python required${NC}"; exit 1; }
    
    # Setup steps
    create_venv
    install_python_deps
    setup_config_dirs
    setup_desktop_integration
    check_ollama
    create_launcher_symlinks
    test_installation
    
    print_success
    
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo -e "  1. Run: ./launch.sh --test"
    echo -e "  2. If Ollama not running: ollama serve"
    echo -e "  3. Launch: ./launch.sh --real"
}

# Error handling
trap 'echo -e "${RED}❌ Setup interrupted${NC}"; exit 1' INT TERM

# Run setup
main "$@"