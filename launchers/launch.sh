#!/bin/bash

# AI-Enhanced Terminal Launcher
# Simple launcher that works with existing Ollama setup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_TERMINAL="$SCRIPT_DIR/ai_terminal.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 AI-Enhanced Terminal${NC}"
echo "========================="

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check if Ollama is running
if command -v ollama >/dev/null 2>&1; then
    if pgrep -x "ollama" > /dev/null; then
        echo -e "${GREEN}✅ Ollama is running${NC}"
    else
        echo -e "${YELLOW}⚠️ Ollama not running, starting...${NC}"
        ollama serve > /dev/null 2>&1 &
        sleep 2
    fi
else
    echo -e "${YELLOW}⚠️ Ollama not installed, AI features will be limited${NC}"
fi

# Check if existing Ollama enhancements are available
if [ -d "/home/nike/ollama-enhancements" ]; then
    echo -e "${GREEN}✅ Found Ollama enhancements${NC}"
else
    echo -e "${YELLOW}⚠️ Ollama enhancements not found${NC}"
fi

echo ""

# Make the script executable
chmod +x "$AI_TERMINAL"

# Launch the terminal
python3 "$AI_TERMINAL" "$@"