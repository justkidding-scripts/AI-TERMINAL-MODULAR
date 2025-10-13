#!/usr/bin/env python3
"""
Real Terminal GUI with AI Integration
Uses VTE (Virtual Terminal Emulator) for full shell functionality
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk, Vte, GLib, Pango
import os
import sys
import threading
import time
import subprocess
import json
from pathlib import Path

# Add ollama enhancements path
OLLAMA_PATH = "/home/nike/ollama-enhancements"
sys.path.insert(0, OLLAMA_PATH)

try:
    from code_assistant.code_assistant import CodeAssistant
    OLLAMA_AVAILABLE = True
except ImportError:
    try:
        # Try with hyphen
        import sys
        sys.path.append('/home/nike/ollama-enhancements/code-assistant')
        from code_assistant import CodeAssistant
        OLLAMA_AVAILABLE = True
    except ImportError:
        OLLAMA_AVAILABLE = False

class RealTerminalWindow(Gtk.Window):
    """Real terminal window with AI integration"""
    
    def __init__(self):
        super().__init__(title="🤖 AI Enhanced Terminal")
        
        # Window setup
        self.set_default_size(1200, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # AI setup
        self.ai = None
        if OLLAMA_AVAILABLE:
            try:
                self.ai = CodeAssistant()
                print("✅ AI assistant loaded")
            except Exception as e:
                print(f"⚠️ AI assistant error: {e}")
        
        # Create layout
        self.setup_ui()
        
        # Connect signals
        self.connect('destroy', Gtk.main_quit)
        self.show_all()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_box = Gtk.VBox()
        self.add(main_box)
        
        # Menu bar
        menubar = self.create_menubar()
        main_box.pack_start(menubar, False, False, 0)
        
        # Terminal container
        terminal_box = Gtk.HBox()
        main_box.pack_start(terminal_box, True, True, 0)
        
        # Create terminal
        self.terminal = Vte.Terminal()
        
        # Terminal settings
        self.terminal.set_font(Pango.FontDescription("JetBrains Mono 12"))
        self.terminal.set_scrollback_lines(10000)
        self.terminal.set_mouse_autohide(True)
        
        # Colors
        palette = [
            '#2E3440', '#BF616A', '#A3BE8C', '#EBCB8B',
            '#81A1C1', '#B48EAD', '#88C0D0', '#E5E9F0',
            '#4C566A', '#BF616A', '#A3BE8C', '#EBCB8B',
            '#81A1C1', '#B48EAD', '#8FBCBB', '#ECEFF4'
        ]
        
        from gi.repository import Gdk
        colors = [Gdk.RGBA(*[int(c[i:i+2], 16)/255.0 for i in (1, 3, 5)] + [1.0]) for c in palette]
        self.terminal.set_colors(
            Gdk.RGBA(0.9, 0.9, 0.9, 1.0),  # Foreground
            Gdk.RGBA(0.1, 0.1, 0.1, 1.0),  # Background
            colors  # Palette
        )
        
        # Spawn shell
        self.spawn_shell()
        
        # Terminal in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.terminal)
        
        terminal_box.pack_start(scrolled, True, True, 0)
        
        # AI panel (optional, can be toggled)
        self.ai_panel = self.create_ai_panel()
        terminal_box.pack_start(self.ai_panel, False, False, 5)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        self.status_context = self.status_bar.get_context_id("status")
        self.status_bar.push(self.status_context, f"Ready | AI: {'✅' if OLLAMA_AVAILABLE else '❌'}")
        main_box.pack_start(self.status_bar, False, False, 0)
        
        # Connect terminal signals
        self.terminal.connect('child-exited', self.on_terminal_exit)
        self.terminal.connect('key-press-event', self.on_key_press)
    
    def create_menubar(self):
        """Create menu bar"""
        menubar = Gtk.MenuBar()
        
        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        menubar.append(file_item)
        
        # New tab
        new_tab = Gtk.MenuItem(label="New Tab")
        new_tab.connect('activate', self.on_new_tab)
        file_menu.append(new_tab)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        # Exit
        exit_item = Gtk.MenuItem(label="Exit")
        exit_item.connect('activate', lambda x: Gtk.main_quit())
        file_menu.append(exit_item)
        
        # View menu
        view_menu = Gtk.Menu()
        view_item = Gtk.MenuItem(label="View")
        view_item.set_submenu(view_menu)
        menubar.append(view_item)
        
        # Toggle AI panel
        toggle_ai = Gtk.CheckMenuItem(label="Show AI Panel")
        toggle_ai.set_active(True)
        toggle_ai.connect('toggled', self.on_toggle_ai_panel)
        view_menu.append(toggle_ai)
        
        # AI menu
        ai_menu = Gtk.Menu()
        ai_item = Gtk.MenuItem(label="AI")
        ai_item.set_submenu(ai_menu)
        menubar.append(ai_item)
        
        # Ask AI
        ask_ai = Gtk.MenuItem(label="Ask AI about current command")
        ask_ai.connect('activate', self.on_ask_ai)
        ai_menu.append(ask_ai)
        
        # Explain last error
        explain_error = Gtk.MenuItem(label="Explain last error")
        explain_error.connect('activate', self.on_explain_error)
        ai_menu.append(explain_error)
        
        return menubar
    
    def create_ai_panel(self):
        """Create AI assistance panel"""
        ai_frame = Gtk.Frame(label="🤖 AI Assistant")
        ai_frame.set_size_request(300, -1)
        
        ai_box = Gtk.VBox(spacing=5)
        ai_frame.add(ai_box)
        
        # AI output
        self.ai_textview = Gtk.TextView()
        self.ai_textview.set_editable(False)
        self.ai_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.ai_textview.set_margin_left(5)
        self.ai_textview.set_margin_right(5)
        
        # AI text buffer
        self.ai_buffer = self.ai_textview.get_buffer()
        
        # Scrolled window for AI output
        ai_scrolled = Gtk.ScrolledWindow()
        ai_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        ai_scrolled.add(self.ai_textview)
        ai_scrolled.set_size_request(-1, 400)
        
        ai_box.pack_start(ai_scrolled, True, True, 0)
        
        # AI input
        ai_input_box = Gtk.HBox(spacing=5)
        ai_box.pack_start(ai_input_box, False, False, 5)
        
        self.ai_entry = Gtk.Entry()
        self.ai_entry.set_placeholder_text("Ask AI anything...")
        self.ai_entry.connect('activate', self.on_ai_entry_activate)
        ai_input_box.pack_start(self.ai_entry, True, True, 0)
        
        ai_send_button = Gtk.Button(label="Send")
        ai_send_button.connect('clicked', self.on_ai_entry_activate)
        ai_input_box.pack_start(ai_send_button, False, False, 0)
        
        # Welcome message
        self.add_ai_message("🤖 AI Assistant Ready!\nAsk me anything about commands, coding, or general questions.", "assistant")
        
        return ai_frame
    
    def spawn_shell(self):
        """Spawn the shell in terminal"""
        try:
            # Use zsh if available, otherwise bash
            shell = "/bin/zsh" if os.path.exists("/bin/zsh") else "/bin/bash"
            
            self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                os.environ['HOME'],
                [shell],
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None,
            )
            
            # Send welcome message to terminal
            welcome = f"\n🤖 AI Enhanced Terminal Ready! Shell: {shell}\n"
            welcome += "💡 Try: 'ai help' for AI commands\n\n"
            
            # Wait a moment then send welcome
            GLib.timeout_add(500, lambda: self.terminal.feed_child(welcome.encode(), len(welcome.encode())))
            
        except Exception as e:
            print(f"Error spawning shell: {e}")
    
    def add_ai_message(self, message, sender="user"):
        """Add message to AI panel"""
        end_iter = self.ai_buffer.get_end_iter()
        
        if sender == "user":
            prefix = "👤 You: "
        else:
            prefix = "🤖 AI: "
        
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {prefix}{message}\n\n"
        
        self.ai_buffer.insert(end_iter, full_message)
        
        # Scroll to bottom
        mark = self.ai_buffer.get_insert()
        self.ai_textview.scroll_mark_onscreen(mark)
    
    def get_ai_response(self, message):
        """Get AI response in background thread"""
        def ai_worker():
            try:
                if self.ai:
                    if message.startswith("explain"):
                        # Error explanation
                        response = self.ai.debug_code(
                            code="command",
                            error_message=message[7:].strip(),
                            language='bash'
                        )
                    else:
                        # General response
                        response = self.ai.code_completion(
                            partial_code=f"# User asks: {message}\n# Helpful response:",
                            language='bash',
                            context="Terminal assistance"
                        )
                else:
                    response = f"I'd love to help with '{message}', but AI features aren't fully available. Try running commands directly in the terminal!"
                
                # Update UI in main thread
                GLib.idle_add(lambda: self.add_ai_message(response or "Sorry, I couldn't generate a response.", "assistant"))
                
            except Exception as e:
                GLib.idle_add(lambda: self.add_ai_message(f"Error: {e}", "assistant"))
        
        # Run in background thread
        thread = threading.Thread(target=ai_worker, daemon=True)
        thread.start()
    
    def on_terminal_exit(self, terminal, status):
        """Handle terminal exit"""
        print("Terminal exited")
        # Respawn shell
        self.spawn_shell()
    
    def on_key_press(self, terminal, event):
        """Handle key press in terminal"""
        # Could add AI shortcuts here
        return False
    
    def on_new_tab(self, menuitem):
        """Create new tab (placeholder)"""
        print("New tab requested - feature coming soon")
    
    def on_toggle_ai_panel(self, checkmenuitem):
        """Toggle AI panel visibility"""
        if checkmenuitem.get_active():
            self.ai_panel.show()
        else:
            self.ai_panel.hide()
    
    def on_ask_ai(self, menuitem):
        """Ask AI about current situation"""
        current_dir = os.getcwd()
        question = f"I'm in directory {current_dir}. What are some useful commands I can run here?"
        self.add_ai_message(question, "user")
        self.get_ai_response(question)
    
    def on_explain_error(self, menuitem):
        """Explain last error (placeholder)"""
        self.add_ai_message("explain last command error", "user")
        self.get_ai_response("explain the most common terminal errors and how to fix them")
    
    def on_ai_entry_activate(self, widget=None):
        """Handle AI entry activation"""
        text = self.ai_entry.get_text().strip()
        if text:
            self.ai_entry.set_text("")
            self.add_ai_message(text, "user")
            self.get_ai_response(text)

def main():
    """Main entry point"""
    try:
        # Check if VTE is available
        gi.require_version('Vte', '2.91')
        
        app = RealTerminalWindow()
        Gtk.main()
        
    except Exception as e:
        print(f"Error: {e}")
        print("VTE not available. Install with: sudo apt install libvte-2.91-dev python3-gi-cairo")
        
        # Fallback to simple version
        print("Falling back to simple terminal...")
        os.system("python3 ai_terminal_enhanced.py")

if __name__ == "__main__":
    main()