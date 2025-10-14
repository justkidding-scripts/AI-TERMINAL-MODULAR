#!/usr/bin/env python3
"""
Warp-Style AI Terminal Launcher 
Unified AI+Terminal Interface Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_gui_requirements():
    """Check if GUI libraries are available"""
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('Vte', '2.91')
        from gi.repository import Gtk, Vte
        return True
    except (ImportError, ValueError):
        return False

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def check_ollama():
    """Check if Ollama is available and running"""
    # Method 1: Try Python package
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        return True, len(models.get('models', []))
    except ImportError:
        pass
    except Exception:
        pass
        
    # Method 2: Try HTTP API
    try:
        import urllib.request
        import json
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                return True, len(data.get('models', []))
    except Exception:
        pass
        
    # Method 3: Try CLI
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            model_count = len([l for l in lines if l.strip()])
            return True, model_count
    except Exception:
        pass
        
    return False, 0

def print_banner():
    """Print launch banner"""
    print("🚀" + "=" * 50)
    print("   WARP-STYLE AI TERMINAL - UNIFIED INTERFACE")
    print("   Chat with AI and run commands in one place")
    print("=" * 52)

def print_status():
    """Print system status"""
    has_vte = check_gui_requirements()
    has_tkinter = check_tkinter()
    ollama_running, model_count = check_ollama()
    
    print(f"🖥️  VTE/GTK3 support: {'✅' if has_vte else '❌'}")
    print(f"🐍  Tkinter support: {'✅' if has_tkinter else '❌'}")
    print(f"🤖  Ollama AI: {'✅' if ollama_running else '❌'} ({model_count} models)")
    print()

def launch_warp_terminal():
    """Launch the new Warp-style terminal"""
    warp_path = project_root / "core" / "warp_terminal_gui.py"
    
    if not warp_path.exists():
        print("❌ Warp terminal not found!")
        return False
        
    try:
        print("🚀 Launching Warp-Style AI Terminal...")
        subprocess.run([sys.executable, str(warp_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Warp terminal failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Terminal closed by user")
        return True

def launch_fallback():
    """Launch fallback terminals"""
    has_vte = check_gui_requirements()
    has_tkinter = check_tkinter()
    
    print("🔄 Trying fallback options...")
    
    # Try standard VTE terminal
    if has_vte:
        real_terminal_path = project_root / "core" / "real_terminal_gui.py"
        if real_terminal_path.exists():
            print("📟 Launching standard VTE terminal...")
            try:
                subprocess.run([sys.executable, str(real_terminal_path)], check=True)
                return True
            except subprocess.CalledProcessError:
                pass
    
    # Try tkinter GUI
    if has_tkinter:
        gui_path = project_root / "core" / "ai_terminal_gui.py"
        if gui_path.exists():
            print("🖼️ Launching tkinter GUI...")
            try:
                subprocess.run([sys.executable, str(gui_path)], check=True)
                return True
            except subprocess.CalledProcessError:
                pass
    
    # Try enhanced CLI
    cli_path = project_root / "core" / "ai_terminal_enhanced.py"
    if cli_path.exists():
        print("💻 Launching enhanced CLI...")
        try:
            subprocess.run([sys.executable, str(cli_path)], check=True)
            return True
        except subprocess.CalledProcessError:
            pass
    
    print("❌ No working terminal found!")
    return False

def show_help():
    """Show help message"""
    print("🤖 Warp-Style AI Terminal Launcher")
    print()
    print("Usage:")
    print("  python3 launch_warp.py [options]")
    print()
    print("Options:")
    print("  --help, -h     Show this help")
    print("  --status, -s   Show system status")
    print("  --force, -f    Force launch even with warnings")
    print()
    print("Features:")
    print("  • Unified AI chat and terminal in one interface")
    print("  • Type commands normally (ls, git, python, etc.)")
    print("  • Chat with AI using 'ai: your question'")
    print("  • Natural language questions detected automatically")
    print("  • Warp-like modern terminal experience")

def main():
    """Main launcher"""
    # Parse arguments
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        show_help()
        return
    
    if '--status' in args or '-s' in args:
        print_banner()
        print_status()
        return
    
    force = '--force' in args or '-f' in args
    
    print_banner()
    print_status()
    
    # Check if we can run GUI
    has_vte = check_gui_requirements()
    
    if not has_vte and not force:
        print("⚠️  Warning: VTE/GTK3 not available!")
        print("   Install with: sudo apt install libvte-2.91-dev python3-gi-cairo")
        print("   Or run with --force to try fallbacks")
        return
    
    # Try to launch Warp terminal
    if has_vte:
        if launch_warp_terminal():
            return
    
    # Fallback to other options
    if not launch_fallback():
        print()
        print("💡 Troubleshooting:")
        print("   1. Install VTE: sudo apt install libvte-2.91-dev python3-gi-cairo")
        print("   2. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("   3. Run Ollama: ollama serve")
        print("   4. Pull a model: ollama pull llama3.2")

if __name__ == "__main__":
    main()