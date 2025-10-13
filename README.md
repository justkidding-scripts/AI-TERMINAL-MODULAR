# AI Enhanced Terminal - MODULAR

A complete modular AI-enhanced terminal system with multiple interface options and full Ollama integration.

## Features

### ️ Multiple Interface Options
- **Real Terminal GUI** - Full VTE-based terminal emulator with AI sidebar
- **Basic GUI** - tkinter-based interface with unified chat/command experience
- **Enhanced CLI** - Feature-rich command-line version with AI assistance
- **Lightweight CLI** - Basic AI terminal for minimal setups

### AI Integration
- **Ollama Integration** - Full support for local AI models
- **RAG System** - Enhanced document indexing and retrieval
- **Code Assistant** - Real-time code suggestions and debugging
- **Error Analysis** - Automatic error explanation and solutions
- **Smart Detection** - Distinguishes between commands and AI chat

### Advanced Features
- **Multi-shell Support** - Works with zsh, bash, fish
- **Performance Monitoring** - Command execution tracking
- **Session Management** - Save/load terminal sessions
- **Theme Customization** - Configurable colors and fonts
- **Desktop Integration** - System menu entries
- **Fallback Modes** - Graceful degradation when services unavailable

## Quick Start

### Installation
```bash
# Clone repository
git clone https/github.com/your-username/AI-TERMINAL-MODULAR.git
cd AI-TERMINAL-MODULAR

# Run setup
./setup.sh

# Launch (GUI version with fallbacks)
./launch.sh
```

### Launch Options
```bash
# Real terminal with VTE (recommended)
./launch.sh --real

# Basic GUI version
./launch.sh --gui

# Enhanced CLI version
./launch.sh --cli

# Test connectivity
./launch.sh --test
```

## Project Structure

```
AI-TERMINAL-MODULAR/
├── core/ # Core terminal implementations
│ ├── real_terminal_gui.py # VTE-based real terminal
│ ├── ai_terminal_gui.py # Basic GUI terminal
│ ├── ai_terminal_enhanced.py # Enhanced CLI terminal
│ └── ai_terminal_basic.py # Basic CLI terminal
├── modules/ # Modular components
│ ├── rag_integration/ # RAG system integration
│ ├── ai_assistant/ # AI assistance modules
│ └── performance/ # Performance monitoring
├── launchers/ # Launch scripts and utilities
│ ├── launch.sh # Universal launcher
│ ├── setup.sh # Setup script
│ └── install_deps.sh # Dependency installer
├── config/ # Configuration templates
│ ├── terminal_config.json # Terminal settings
│ └── ai_config.json # AI settings
├── desktop/ # Desktop integration
│ ├── ai-terminal.desktop # Desktop entry
│ └── icons/ # Application icons
└── docs/ # Documentation
 ├── INSTALL.md # Installation guide
 ├── USAGE.md # Usage instructions
 └── API.md # API documentation
```

## Requirements

### System Requirements
- **OS**: Linux (Debian/Ubuntu recommended)
- **Python**: 3.8+
- **Display**: X11 or Wayland for GUI versions

### Dependencies
- **Required**: `python3`, `python3-tk`, `python3-gi`
- **Optional**: `ollama`, `git`, VTE libraries
- **Auto-installed**: See `requirements.txt`

### AI Requirements
- **Ollama**: For AI functionality
- **Models**: codellama:7b, llama3.2 (auto-downloaded)

## Usage

### Basic Commands
```bash
# Terminal commands work normally
ls -la
git status
python script.py

# AI chat (automatically detected)
what is docker?
how do I use git?
explain this error
```

### RAG System
```bash
# Index documents
rag add ~/Documents
rag add /path/to/project

# Query knowledge base
rag ask "What is machine learning?"
rag search "python functions"

# Manage documents
rag list
rag status
rag clear
```

### Special Commands
```bash
help # Show help
config # Edit configuration
stats # Performance statistics
ai <command> # Get AI suggestion
explain <error> # Explain error message
```

## ️ Configuration

### Terminal Configuration (`~/.config/ai-terminal/config.json`)
```json
{
 "ai_enabled": true,
 "model": "codellama:7b",
 "theme": {
 "prompt_color": "#00ff00",
 "ai_color": "#4da6ff",
 "error_color": "#ff4444"
 },
 "performance": {
 "monitor_commands": true,
 "show_execution_time": true
 }
}
```

### GUI Configuration (`~/.config/ai-terminal/gui_config.json`)
```json
{
 "theme": {
 "bg_color": "#1e1e1e",
 "fg_color": "#ffffff",
 "font_family": "JetBrains Mono",
 "font_size": 12
 },
 "layout": {
 "show_ai_panel": true,
 "terminal_width": 70,
 "ai_width": 30
 }
}
```

## API Integration

### Ollama Integration
```python
from modules.ai_assistant import OllamaAI

ai = OllamaAI()
response = ai.get_suggestion("git commit")
explanation = ai.explain_error("command not found")
```

### RAG Integration
```python
from modules.rag_integration import RAGSkill

rag = RAGSkill()
rag.handle("rag add ~/documents")
results = rag.handle("rag ask What is Python?")
```

## Troubleshooting

### Common Issues

**GUI won't start**
```bash
# Install dependencies
sudo apt install python3-tk libvte-2.91-dev
./setup.sh
```

**AI not responding**
```bash
# Check Ollama
ollama serve
ollama list
./launch.sh --test
```

**VTE errors**
```bash
# Install VTE libraries
sudo apt install gir1.2-vte-2.91 python3-gi-cairo
```

### Debug Mode
```bash
# Enable debug output
export AI_TERMINAL_DEBUG=1
./launch.sh --cli --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Ollama** - Local AI model runtime
- **VTE** - Terminal emulator library
- **ChromaDB** - Vector database for RAG
- **tkinter** - GUI framework

## Support

- **Issues**: [GitHub Issues](https/github.com/your-username/AI-TERMINAL-MODULAR/issues)
- **Documentation**: [Wiki](https/github.com/your-username/AI-TERMINAL-MODULAR/wiki)
- **Discussions**: [GitHub Discussions](https/github.com/your-username/AI-TERMINAL-MODULAR/discussions)

---

**Built with ️ for developers who love AI-enhanced workflows**