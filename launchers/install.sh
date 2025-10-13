#!/bin/bash
set -e

# AI-Enhanced Terminal Installer and Manager
# Comprehensive setup for your enhanced AI terminal

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/ai-terminal"
DESKTOP_DIR="$HOME/.local/share/applications"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m' 
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python 3
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    log_success "Python 3: $(python3 --version)"
    
    # Check zsh
    if ! command -v zsh >/dev/null 2>&1; then
        log_warning "zsh not found - some features will be limited"
    else
        log_success "zsh: $(zsh --version | head -1)"
    fi
    
    # Check if Ollama is available
    if command -v ollama >/dev/null 2>&1; then
        if pgrep -x "ollama" > /dev/null; then
            log_success "Ollama is running"
        else
            log_warning "Ollama installed but not running"
        fi
    else
        log_warning "Ollama not found - AI features will be limited"
    fi
    
    # Check for existing enhancements
    if [ -d "/home/nike/ollama-enhancements" ]; then
        log_success "Found existing Ollama enhancements"
    else
        log_warning "Ollama enhancements not found at /home/nike/ollama-enhancements"
    fi
}

install_terminal() {
    log_info "Installing AI Terminal..."
    
    # Create directories
    mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$DESKTOP_DIR"
    
    # Copy files
    cp "$SCRIPT_DIR/ai_terminal_enhanced.py" "$INSTALL_DIR/ai-terminal"
    cp "$SCRIPT_DIR/ai_terminal.py" "$INSTALL_DIR/ai-terminal-simple"
    cp "$SCRIPT_DIR/terminal_proxy.py" "$INSTALL_DIR/ai-terminal-proxy"
    
    # Make executable
    chmod +x "$INSTALL_DIR/ai-terminal"
    chmod +x "$INSTALL_DIR/ai-terminal-simple" 
    chmod +x "$INSTALL_DIR/ai-terminal-proxy"
    
    log_success "Terminal binaries installed to $INSTALL_DIR"
}

setup_desktop_integration() {
    log_info "Setting up desktop integration..."
    
    # Create desktop entry
    cat > "$DESKTOP_DIR/ai-terminal.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Enhanced Terminal
Comment=Terminal with AI assistance and Ollama integration
Exec=$INSTALL_DIR/ai-terminal
Icon=utilities-terminal
Terminal=true
Categories=System;TerminalEmulator;Development;
StartupNotify=true
EOF
    
    log_success "Desktop entry created"
}

setup_shell_integration() {
    log_info "Setting up shell integration..."
    
    # Create shell alias function
    cat > "$CONFIG_DIR/shell_integration.sh" << 'EOF'
# AI Terminal Shell Integration
# Add to your .bashrc or .zshrc

# Alias for quick access
alias ait='ai-terminal'
alias ait-simple='ai-terminal-simple'
alias ait-proxy='ai-terminal-proxy'

# Function to quickly get AI suggestions
ai_suggest() {
    if [ -z "$1" ]; then
        echo "Usage: ai_suggest <command>"
        return 1
    fi
    python3 -c "
import sys
sys.path.insert(0, '/home/nike/ai-enhanced-terminal')
from ai_terminal_enhanced import OllamaIntegration
ollama = OllamaIntegration()
suggestion = ollama.get_code_suggestion('$*')
if suggestion:
    print('💡 AI Suggestion:', suggestion)
else:
    print('No suggestion available')
"
}

# Function to explain errors
ai_explain() {
    if [ -z "$1" ]; then
        echo "Usage: ai_explain <error_message>"
        return 1
    fi
    python3 -c "
import sys
sys.path.insert(0, '/home/nike/ai-enhanced-terminal')
from ai_terminal_enhanced import OllamaIntegration
ollama = OllamaIntegration()
explanation = ollama.debug_command('', '$*')
if explanation:
    print('🔍 AI Explanation:', explanation)
else:
    print('No explanation available')
"
}
EOF
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$CONFIG_DIR/path_setup.sh"
        log_info "Added $INSTALL_DIR to PATH setup"
    fi
    
    log_success "Shell integration files created in $CONFIG_DIR"
}

create_launch_scripts() {
    log_info "Creating launch scripts..."
    
    # Main launcher
    cat > "$INSTALL_DIR/ait" << EOF
#!/bin/bash
# AI Terminal Launcher

# Ensure Ollama is running
if command -v ollama >/dev/null 2>&1; then
    if ! pgrep -x "ollama" > /dev/null; then
        echo "Starting Ollama..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
    fi
fi

# Launch enhanced terminal
exec "$INSTALL_DIR/ai-terminal" "\$@"
EOF
    chmod +x "$INSTALL_DIR/ait"
    
    # Quick suggestion script
    cat > "$INSTALL_DIR/ai" << 'EOF'
#!/bin/bash
# Quick AI command suggestion

if [ $# -eq 0 ]; then
    echo "Usage: ai <command>"
    echo "Example: ai git push"
    exit 1
fi

python3 -c "
import sys
import os
sys.path.insert(0, os.path.expanduser('~/ai-enhanced-terminal'))
try:
    from ai_terminal_enhanced import OllamaIntegration
    ollama = OllamaIntegration()
    suggestion = ollama.get_code_suggestion(' '.join(sys.argv[1:]))
    if suggestion:
        print('💡', suggestion)
    else:
        print('No suggestion available')
except Exception as e:
    print('Error:', e)
" "$@"
EOF
    chmod +x "$INSTALL_DIR/ai"
    
    log_success "Launch scripts created"
}

setup_zsh_completions() {
    log_info "Setting up zsh completions..."
    
    ZSH_COMP_DIR="$HOME/.zfunc"
    mkdir -p "$ZSH_COMP_DIR"
    
    cat > "$ZSH_COMP_DIR/_ai-terminal" << 'EOF'
#compdef ai-terminal

_ai_terminal() {
    local context state line
    
    _arguments -C \
        '--help[Show help message]' \
        '--no-ai[Disable AI features]' \
        '--debug[Enable debug mode]' \
        '*::command:_command_names'
}

_ai_terminal
EOF
    
    # Add to fpath if zsh is available
    if command -v zsh >/dev/null 2>&1; then
        if [ -f "$HOME/.zshrc" ]; then
            if ! grep -q "fpath=(.*$ZSH_COMP_DIR" "$HOME/.zshrc"; then
                echo "# AI Terminal completions" >> "$HOME/.zshrc"
                echo "fpath=($ZSH_COMP_DIR \$fpath)" >> "$HOME/.zshrc"
                echo "autoload -U compinit && compinit" >> "$HOME/.zshrc"
                log_info "Added completions to .zshrc"
            fi
        fi
    fi
    
    log_success "Zsh completions set up"
}

setup_systemd_user_service() {
    log_info "Setting up systemd user service for Ollama auto-start..."
    
    SYSTEMD_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SYSTEMD_DIR"
    
    if command -v ollama >/dev/null 2>&1; then
        cat > "$SYSTEMD_DIR/ollama.service" << EOF
[Unit]
Description=Ollama AI Service
After=network.target

[Service]
Type=exec
ExecStart=$(which ollama) serve
Restart=always
RestartSec=3
Environment=HOME=$HOME

[Install]
WantedBy=default.target
EOF
        
        # Enable service
        systemctl --user daemon-reload
        systemctl --user enable ollama.service
        
        log_success "Ollama systemd service created and enabled"
    else
        log_warning "Ollama not found, skipping systemd service"
    fi
}

show_usage_instructions() {
    log_success "AI Terminal Installation Complete! 🎉"
    echo
    echo "Usage Options:"
    echo "=============="
    echo
    echo "🚀 Enhanced Terminal (Recommended):"
    echo "   ai-terminal              # Full featured AI terminal"
    echo "   ait                      # Quick launcher with Ollama auto-start"
    echo
    echo "⚡ Quick Commands:"
    echo "   ai git push              # Get AI suggestion for git commands"
    echo "   ai_suggest 'python -m'   # Get completion suggestions"
    echo "   ai_explain 'command not found' # Explain errors"
    echo
    echo "🔧 Other Versions:"
    echo "   ai-terminal-simple       # Simple interactive terminal"
    echo "   ai-terminal-proxy        # Real terminal with AI integration"
    echo
    echo "⚙️ Configuration:"
    echo "   ai-terminal config       # Edit configuration"
    echo "   ai-terminal stats        # Show session stats"
    echo "   ai-terminal aliases      # Show zsh aliases"
    echo
    echo "📁 Files:"
    echo "   Config: ~/.config/ai-terminal/config.json"
    echo "   Shell:  ~/.config/ai-terminal/shell_integration.sh"
    echo
    echo "🔧 Shell Integration:"
    echo "   Add to your ~/.zshrc or ~/.bashrc:"
    echo "   source ~/.config/ai-terminal/shell_integration.sh"
    echo "   export PATH=\"$INSTALL_DIR:\$PATH\""
    echo
    if command -v ollama >/dev/null 2>&1; then
        echo "✅ Ollama detected - AI features will be fully functional"
    else
        echo "⚠️  Install Ollama for full AI functionality: curl -fsSL https://ollama.com/install.sh | sh"
    fi
    echo
    echo "Test the installation:"
    echo "   ait                      # Launch AI terminal"
    echo "   ai git status            # Test AI suggestions"
}

uninstall() {
    log_info "Uninstalling AI Terminal..."
    
    # Remove binaries
    rm -f "$INSTALL_DIR/ai-terminal"
    rm -f "$INSTALL_DIR/ai-terminal-simple"
    rm -f "$INSTALL_DIR/ai-terminal-proxy" 
    rm -f "$INSTALL_DIR/ait"
    rm -f "$INSTALL_DIR/ai"
    
    # Remove desktop entry
    rm -f "$DESKTOP_DIR/ai-terminal.desktop"
    
    # Remove systemd service
    if [ -f "$HOME/.config/systemd/user/ollama.service" ]; then
        systemctl --user stop ollama.service 2>/dev/null || true
        systemctl --user disable ollama.service 2>/dev/null || true
        rm -f "$HOME/.config/systemd/user/ollama.service"
        systemctl --user daemon-reload
    fi
    
    # Keep config directory but notify user
    log_warning "Configuration directory kept at: $CONFIG_DIR"
    log_warning "Remove manually if desired: rm -rf $CONFIG_DIR"
    
    log_success "AI Terminal uninstalled"
}

main() {
    case "${1:-install}" in
        "install"|"")
            check_prerequisites
            install_terminal
            setup_desktop_integration
            setup_shell_integration
            create_launch_scripts
            setup_zsh_completions
            setup_systemd_user_service
            show_usage_instructions
            ;;
        "uninstall")
            uninstall
            ;;
        "update")
            log_info "Updating AI Terminal..."
            install_terminal
            log_success "AI Terminal updated"
            ;;
        "status")
            log_info "AI Terminal Status:"
            echo "Install dir: $INSTALL_DIR"
            echo "Config dir: $CONFIG_DIR"
            echo "Installed files:"
            ls -la "$INSTALL_DIR"/ai* 2>/dev/null || echo "  None found"
            ;;
        *)
            echo "Usage: $0 [install|uninstall|update|status]"
            echo "  install   - Install AI Terminal (default)"
            echo "  uninstall - Remove AI Terminal"
            echo "  update    - Update existing installation"
            echo "  status    - Show installation status"
            exit 1
            ;;
    esac
}

main "$@"