#!/usr/bin/env python3
"""
Warp-Style Terminal with AI Integration
Unified interface where you can chat with AI and run commands in the same terminal
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk, Vte, GLib, Pango, Gdk
import os
import sys
import threading
import time
import subprocess
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

# Enhanced Ollama integration
OLLAMA_AVAILABLE = False
OLLAMA_CLIENT = None

try:
    import ollama
    OLLAMA_CLIENT = ollama.Client()
    OLLAMA_AVAILABLE = True
    print("✅ Ollama Python client available")
except ImportError:
    # Fallback: check if local Ollama HTTP API is reachable or CLI exists
    def _ollama_http_available():
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=0.5) as resp:
                return resp.status == 200
        except Exception:
            return False
    OLLAMA_AVAILABLE = _ollama_http_available() or (shutil.which("ollama") is not None if 'shutil' in globals() else __import__('shutil').which("ollama") is not None)
    print("⚠️ Ollama Python client not installed; HTTP/CLI fallback {}".format("enabled" if OLLAMA_AVAILABLE else "unavailable"))

class WarpTerminalWindow(Gtk.Window):
    """Warp-style terminal with unified AI chat and command interface"""
    
    def __init__(self):
        super().__init__(title="🤖 Warp-Style AI Terminal")
        
        # Window setup
        self.set_default_size(1400, 900)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # AI state
        self.ai_mode = False
        self.command_history = []
        self.current_command = ""
        
        # Create layout
        self.setup_ui()
        
        # Connect signals
        self.connect('destroy', Gtk.main_quit)
        self.show_all()
        
        # Start with welcome message
        self.add_ai_message("🤖 Warp-Style AI Terminal Ready!\n\n" +
                           "💡 How to use:\n" +
                           "• Type commands normally (e.g., ls, git status, python script.py)\n" +
                           "• Start messages with 'ai:' to chat with AI (e.g., ai: what is docker?)\n" +
                           "• Use natural language questions (e.g., how do I use git?)\n" +
                           "• All in one unified terminal - just like Warp!\n")
    
    def setup_ui(self):
        """Setup the unified Warp-style interface"""
        # Main container
        main_box = Gtk.VBox()
        self.add(main_box)
        
        # Menu bar (minimal)
        menubar = self.create_menubar()
        main_box.pack_start(menubar, False, False, 0)
        
        # Main terminal area (like Warp)
        self.terminal = Vte.Terminal()
        
        # Terminal settings optimized for Warp-like experience
        self.terminal.set_font(Pango.FontDescription("JetBrains Mono 12"))
        self.terminal.set_scrollback_lines(10000)
        self.terminal.set_mouse_autohide(False)  # Keep mouse visible for editing
        
        # Enable mouse support for better text editing
        self.terminal.set_enable_bidi(True)  # Better text rendering
        self.terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        self.terminal.set_cursor_shape(Vte.CursorShape.IBEAM)  # I-beam cursor
        
        # Enable text selection and copy/paste
        self.terminal.set_word_char_exceptions("-#:._")
        
        # Note: set_allow_bold is deprecated in newer VTE; remove to avoid warnings
        
        # Lighter, more modern colors (inspired by VS Code Light)
        colors = [
            Gdk.RGBA(0.25, 0.25, 0.25, 1.0),  # Black
            Gdk.RGBA(0.80, 0.25, 0.33, 1.0),  # Red
            Gdk.RGBA(0.13, 0.55, 0.13, 1.0),  # Green  
            Gdk.RGBA(0.80, 0.60, 0.00, 1.0),  # Yellow
            Gdk.RGBA(0.00, 0.40, 0.80, 1.0),  # Blue
            Gdk.RGBA(0.67, 0.13, 0.67, 1.0),  # Magenta
            Gdk.RGBA(0.00, 0.60, 0.60, 1.0),  # Cyan
            Gdk.RGBA(0.75, 0.75, 0.75, 1.0),  # White
            # Bright colors
            Gdk.RGBA(0.50, 0.50, 0.50, 1.0),  # Bright black
            Gdk.RGBA(0.90, 0.30, 0.40, 1.0),  # Bright red
            Gdk.RGBA(0.20, 0.70, 0.20, 1.0),  # Bright green
            Gdk.RGBA(0.90, 0.70, 0.10, 1.0),  # Bright yellow
            Gdk.RGBA(0.30, 0.60, 0.90, 1.0),  # Bright blue
            Gdk.RGBA(0.80, 0.30, 0.80, 1.0),  # Bright magenta
            Gdk.RGBA(0.20, 0.80, 0.80, 1.0),  # Bright cyan
            Gdk.RGBA(0.95, 0.95, 0.95, 1.0),  # Bright white
        ]
        
        # Lighter background and darker text for better readability
        self.terminal.set_colors(
            Gdk.RGBA(0.20, 0.20, 0.20, 1.0),  # Foreground - dark text
            Gdk.RGBA(0.98, 0.98, 0.98, 1.0),  # Background - very light
            colors
        )
        
        # Terminal in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.terminal)
        
        main_box.pack_start(scrolled, True, True, 0)
        
        # Status bar with AI indicator
        self.status_bar = Gtk.Statusbar()
        self.status_context = self.status_bar.get_context_id("status")
        ai_status = "✅ AI Ready" if OLLAMA_AVAILABLE else "❌ AI Unavailable"
        self.status_bar.push(self.status_context, f"Warp Terminal | {ai_status} | Type 'ai:' for AI chat")
        main_box.pack_start(self.status_bar, False, False, 0)
        
        # Connect terminal signals for AI integration
        self.terminal.connect('child-exited', self.on_terminal_exit)
        self.terminal.connect('commit', self.on_terminal_commit)
        self.terminal.connect('key-press-event', self.on_key_press)
        self.terminal.connect('button-press-event', self.on_button_press)
        
        # Track input for AI detection
        self.current_input = ""
        
        # Spawn enhanced shell with AI integration
        self.spawn_enhanced_shell()
    
    def create_menubar(self):
        """Create minimal menu bar"""
        menubar = Gtk.MenuBar()
        
        # AI menu
        ai_menu = Gtk.Menu()
        ai_item = Gtk.MenuItem(label="AI")
        ai_item.set_submenu(ai_menu)
        menubar.append(ai_item)
        
        # AI shortcuts
        ai_help = Gtk.MenuItem(label="AI Help")
        ai_help.connect('activate', lambda x: self.send_ai_message("How can I use this AI terminal?"))
        ai_menu.append(ai_help)
        
        ai_status = Gtk.MenuItem(label="Check AI Status")
        ai_status.connect('activate', self.on_check_ai_status)
        ai_menu.append(ai_status)
        
        # View menu
        view_menu = Gtk.Menu()
        view_item = Gtk.MenuItem(label="View")
        view_item.set_submenu(view_menu)
        menubar.append(view_item)
        
        # Clear terminal
        clear_term = Gtk.MenuItem(label="Clear Terminal")
        clear_term.connect('activate', lambda x: self.terminal.reset(True, True))
        view_menu.append(clear_term)
        
        return menubar
    
    def spawn_enhanced_shell(self):
        """Spawn shell directly with better compatibility"""
        try:
            # Simple direct shell spawn
            shell = os.environ.get('SHELL', '/bin/bash')
            if not os.path.exists(shell):
                shell = '/bin/bash' if os.path.exists('/bin/bash') else '/bin/sh'
            
            # Prepare environment as list of KEY=VALUE strings
            env_list = [f"{k}={v}" for k, v in os.environ.items()]

            # Use the simpler spawn method
            try:
                self.terminal.spawn_sync(
                    Vte.PtyFlags.DEFAULT,
                    os.environ.get('HOME', '/'),
                    [shell],
                    env_list,
                    GLib.SpawnFlags.DEFAULT,
                    None,
                    None,
                )
                
                # Send welcome message after successful spawn
                GLib.timeout_add(500, self.send_welcome_message)
                
            except Exception as e:
                print(f"spawn_sync failed: {e}, trying spawn_async...")
                if hasattr(self.terminal, 'spawn_async'):
                    self.terminal.spawn_async(
                        Vte.PtyFlags.DEFAULT,
                        os.environ.get('HOME', '/'),
                        [shell],
                        env_list,
                        GLib.SpawnFlags.DEFAULT,
                        None,
                        None,
                        -1,
                        None,
                        None
                    )
                    GLib.timeout_add(500, self.send_welcome_message)
            
        except Exception as e:
            print(f"Error spawning shell: {e}")
            
    def send_welcome_message(self):
        """Send welcome message to terminal"""
        welcome = "\n🚀 Warp-Style AI Terminal Ready!\n"
        welcome += "💡 Type 'ai: your question' to chat with AI\n"
        welcome += "💡 Natural questions are detected automatically\n"
        welcome += "💡 Use mouse to click and edit text normally\n"
        welcome += "===============================================\n\n"
        
        try:
            self.terminal.feed_child(welcome.encode())
        except Exception as e:
            print(f"Welcome message error: {e}")
        return False  # Don't repeat
    
    def on_key_press(self, widget, event):
        """Handle key press events for better input tracking"""
        key_name = Gdk.keyval_name(event.keyval)
        
        if key_name == 'Return' or key_name == 'KP_Enter':
            # Check if current input should go to AI
            if self.current_input.strip():
                self.check_ai_input(self.current_input.strip())
            self.current_input = ""
        elif key_name == 'BackSpace':
            if self.current_input:
                self.current_input = self.current_input[:-1]
        elif len(key_name) == 1:  # Regular character
            self.current_input += key_name.lower()
        elif key_name == 'space':
            self.current_input += " "
        
        return False  # Let terminal handle the key too
    
    def check_ai_input(self, text):
        """Check if input should be processed by AI"""
        text = text.strip()
        if not text:
            return
            
        # Method 1: Explicit AI prefix
        if text.startswith('ai:'):
            ai_query = text[3:].strip()
            if ai_query:
                self.process_ai_query(ai_query)
                return
        
        # Method 2: Natural language patterns
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can you', 'could you', 'explain', 'help']
        text_lower = text.lower()
        
        # Check if it starts with question words and contains question mark
        if any(text_lower.startswith(word) for word in question_words) and '?' in text:
            self.process_ai_query(text)
            return
            
        # Method 3: Help-related keywords
        help_keywords = ['help me', 'how do i', 'what is', 'explain', 'show me']
        if any(keyword in text_lower for keyword in help_keywords):
            self.process_ai_query(text)
            return
    
    def on_button_press(self, widget, event):
        """Handle mouse button press for context menu"""
        if event.button == 3:  # Right click
            self.show_context_menu(event)
            return True
        return False
    
    def show_context_menu(self, event):
        """Show context menu with copy/paste options"""
        menu = Gtk.Menu()
        
        # Copy
        copy_item = Gtk.MenuItem(label="Copy")
        copy_item.connect('activate', lambda x: self.terminal.copy_clipboard_format(Vte.Format.TEXT))
        menu.append(copy_item)
        
        # Paste
        paste_item = Gtk.MenuItem(label="Paste")
        paste_item.connect('activate', lambda x: self.terminal.paste_clipboard())
        menu.append(paste_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # AI Help
        ai_help = Gtk.MenuItem(label="Ask AI for Help")
        ai_help.connect('activate', lambda x: self.process_ai_query("Can you help me with terminal commands?"))
        menu.append(ai_help)
        
        # Select All
        select_all = Gtk.MenuItem(label="Select All")
        select_all.connect('activate', lambda x: self.terminal.select_all())
        menu.append(select_all)
        
        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)
    
    def on_terminal_commit(self, terminal, text, length):
        """Handle terminal commit (legacy fallback)"""
        # This is a fallback - main detection happens in key_press
        return False
    
    def process_ai_query(self, query):
        """Process AI query in background"""
        def ai_worker():
            try:
                response = self.get_ai_response(query)
                GLib.idle_add(self.display_ai_response, query, response)
            except Exception as e:
                GLib.idle_add(self.display_ai_response, query, f"AI Error: {e}")
        
        thread = threading.Thread(target=ai_worker, daemon=True)
        thread.start()
    
    def _ollama_http_chat(self, model, messages):
        """Send chat request to Ollama HTTP API"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            req = urllib.request.Request(
                url="http://127.0.0.1:11434/api/chat",
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            
            with urllib.request.urlopen(req, timeout=10) as resp:  # Reduced timeout
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    # Ollama HTTP API returns { "message": { "role": "assistant", "content": "..." } }
                    if data and isinstance(data, dict) and "message" in data:
                        message = data["message"]
                        if isinstance(message, dict) and "content" in message:
                            return message["content"].strip()
                            
        except urllib.error.URLError as e:
            print(f"HTTP URL Error: {e}")
            return None
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected HTTP error: {e}")
            return None

    def get_ai_response(self, query):
        """Get response from Ollama AI with multiple fallbacks"""
        messages = [{
            'role': 'user',
            'content': f"You are a helpful terminal assistant. Answer this question concisely: {query}"
        }]

        preferred_models = ['llama3.2:1b', 'llama3.2', 'llama3.2:3b', 'codellama:7b']  # Fastest first

        # 1) Try Python client if available
        if OLLAMA_CLIENT is not None:
            for model in preferred_models:
                try:
                    response = OLLAMA_CLIENT.chat(model=model, messages=messages)
                    if response and 'message' in response and 'content' in response['message']:
                        return response['message']['content']
                except Exception:
                    continue

        # 2) Try HTTP API (primary method since CLI hangs)
        print("Trying HTTP API...")
        for model in preferred_models:
            print(f"Trying model: {model}")
            content = self._ollama_http_chat(model, messages)
            if content:
                print(f"Success with model: {model}")
                return content
            print(f"Failed with model: {model}")

        # 3) Fast check if Ollama is even running
        try:
            test_req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
            with urllib.request.urlopen(test_req, timeout=2) as resp:
                if resp.status != 200:
                    return "🤖 Ollama server not responding properly."
        except Exception:
            return "🤖 Ollama server is not running. Start with: ollama serve"

        return "🤖 AI models are busy or unavailable. The server is running but not responding to chat requests."
    
    def display_ai_response(self, query, response):
        """Display AI response in terminal with better formatting"""
        # Clear any partial input and create a clean AI response section
        ai_output = "\r\n"  # New line and carriage return
        ai_output += "\033[1;36m"  # Bright cyan color
        ai_output += "🤖 AI Response to: "
        ai_output += "\033[1;33m"  # Bright yellow for query
        ai_output += f"'{query}'"
        ai_output += "\033[0m\n"  # Reset color
        ai_output += "\033[1;34m" + "═" * 60 + "\033[0m\n"  # Blue separator
        
        # Format response with proper line breaks
        ai_output += "\033[0;32m"  # Green for AI response
        formatted_response = response.replace('\n', '\n\033[0;32m')  # Keep green on new lines
        ai_output += formatted_response
        ai_output += "\033[0m\n"  # Reset color
        
        ai_output += "\033[1;34m" + "═" * 60 + "\033[0m\n\n"  # Blue separator
        
        # Use GLib.idle_add to ensure proper display
        GLib.idle_add(self._feed_ai_output, ai_output)
    
    def _feed_ai_output(self, output):
        """Feed AI output to terminal safely"""
        try:
            self.terminal.feed_child(output.encode())
        except Exception as e:
            print(f"Error feeding AI output: {e}")
        return False
    
    def add_ai_message(self, message):
        """Add AI message to terminal"""
        output = f"\n{message}\n\n"
        self.terminal.feed_child(output.encode())
    
    def send_ai_message(self, message):
        """Send message to AI"""
        self.process_ai_query(message)
    
    def on_terminal_exit(self, terminal, status):
        """Handle terminal exit"""
        print("Terminal exited, respawning...")
        self.spawn_enhanced_shell()
    
    def on_check_ai_status(self, menuitem):
        """Check and display AI status"""
        if OLLAMA_CLIENT is not None:
            try:
                models = OLLAMA_CLIENT.list()
                model_names = [m['name'] for m in models.get('models', [])]
                status_msg = f"✅ Ollama AI is running\nAvailable models: {', '.join(model_names) if model_names else 'No models found'}"
            except Exception as e:
                status_msg = f"❌ Ollama connection error: {e}"
        else:
            # Try HTTP/CLI
            try:
                with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1) as resp:
                    tags = json.loads(resp.read().decode())
                    model_names = [m.get('name') for m in tags.get('models', [])]
                    status_msg = f"✅ Ollama (HTTP) is running\nAvailable models: {', '.join([m for m in model_names if m]) or 'No models'}"
            except Exception:
                # CLI fallback
                try:
                    proc = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=3)
                    if proc.returncode == 0:
                        lines = [l.strip() for l in proc.stdout.splitlines()[1:] if l.strip()]
                        names = [l.split()[0] for l in lines if l]
                        status_msg = f"✅ Ollama (CLI) is available\nAvailable models: {', '.join(names) or 'No models'}"
                    else:
                        status_msg = "❌ Ollama not installed or not running"
                except Exception:
                    status_msg = "❌ Ollama not installed or not running"
        
        self.add_ai_message(f"🔍 AI Status Check:\n{status_msg}")

def main():
    """Main entry point"""
    try:
        # Check if VTE is available
        app = WarpTerminalWindow()
        Gtk.main()
        
    except Exception as e:
        print(f"Error: {e}")
        print("VTE not available. Install with: sudo apt install libvte-2.91-dev python3-gi-cairo")
        
        # Fallback to CLI
        print("Falling back to CLI terminal...")
        os.system("python3 core/ai_terminal_enhanced.py")

if __name__ == "__main__":
    main()