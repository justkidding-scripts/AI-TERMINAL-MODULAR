# 🚀 Warp-Style AI Terminal

**Unified AI Chat + Terminal Interface**

This is the new **Warp-Style AI Terminal** that provides a unified interface where you can chat with AI and run terminal commands in the same window, just like Warp Terminal!

## ✨ Features

- **🔄 Unified Interface**: Chat with AI and run shell commands in one place
- **🤖 Intelligent AI Detection**: Automatically detects when you're asking questions
- **💬 Multiple Chat Methods**: 
  - Prefix with `ai:` (e.g., `ai: what is docker?`)
  - Natural language questions (e.g., `how do I use git?`)
  - Automatic question detection
- **🖥️ Real Terminal**: Full VTE-based terminal with shell access
- **🎨 Warp-like Styling**: Modern dark theme with beautiful colors
- **⚡ Fast & Responsive**: Threaded AI responses don't block terminal

## 🚀 Quick Start

### Option 1: Python Launcher (Recommended)
```bash
# Launch directly
python3 launch_warp.py

# Check system status first
python3 launch_warp.py --status

# Force launch even with warnings
python3 launch_warp.py --force
```

### Option 2: Bash Launcher
```bash
# Launch Warp terminal specifically  
./launch.sh --warp

# Auto-detect (will choose Warp if available)
./launch.sh
```

### Option 3: Direct Launch
```bash
python3 core/warp_terminal_gui.py
```

## 💡 How to Use

### Chat with AI
```bash
# Method 1: ai: prefix
ai: how do I create a Python virtual environment?

# Method 2: Natural questions
what is the difference between git merge and git rebase?

# Method 3: Direct questions  
how do I install Docker on Ubuntu?
```

### Run Commands Normally
```bash
ls -la
git status
python3 my_script.py
cd /some/directory
```

### Mix Both!
```bash
ls -la
ai: what do these file permissions mean?
git log --oneline
how do I undo the last commit?
```

## 🔧 Requirements

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt install libvte-2.91-dev python3-gi-cairo gir1.2-vte-2.91 gir1.2-gtk-3.0

# Python packages (if using pip)
pip3 install pygobject
```

### AI Backend (Optional but Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Run Ollama server
ollama serve

# Pull a model
ollama pull llama3.2
# or
ollama pull codellama:7b
```

## 🎯 Why This Terminal?

- **📱 Modern UX**: Like Warp Terminal but with AI built-in
- **🧠 Smart**: Understands context and intent
- **⚡ Fast**: No switching between terminal and AI chat
- **🔧 Powerful**: Full shell access + AI assistance
- **🎨 Beautiful**: Modern styling and smooth experience

## 🔍 Status Check

Run this to see what's available on your system:
```bash
python3 launch_warp.py --status
```

Output example:
```
🚀==================================================
   WARP-STYLE AI TERMINAL - UNIFIED INTERFACE
   Chat with AI and run commands in one place
====================================================
🖥️  VTE/GTK3 support: ✅
🐍  Tkinter support: ✅  
🤖  Ollama AI: ✅ (3 models)
```

## 🐛 Troubleshooting

### GUI Won't Start
```bash
# Install VTE dependencies
sudo apt install libvte-2.91-dev python3-gi-cairo

# Check if display is available
echo $DISPLAY
```

### AI Not Working
```bash
# Start Ollama service
ollama serve

# Check if models are installed
ollama list

# Pull a model if none available
ollama pull llama3.2
```

### Fallback Options
The launcher automatically falls back to other terminals if the Warp-style one can't start:
1. **Warp-style terminal** ← You are here
2. Standard VTE terminal  
3. Tkinter GUI terminal
4. CLI terminal

## 🆚 Comparison

| Feature | Warp Terminal | Standard Terminal | This AI Terminal |
|---------|---------------|-------------------|------------------|
| AI Chat | ❌ | ❌ | ✅ |
| Unified Interface | ✅ | ❌ | ✅ |
| Modern UI | ✅ | ❌ | ✅ |
| Shell Access | ✅ | ✅ | ✅ |
| Context Awareness | ✅ | ❌ | ✅ |
| Free | ❌ | ✅ | ✅ |

**Best of both worlds!** 🎉