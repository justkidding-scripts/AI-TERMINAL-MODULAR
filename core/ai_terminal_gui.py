#!/usr/bin/env python3
"""
AI Terminal GUI
Modern terminal interface with integrated Ollama AI responses
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import queue
import time
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

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

class OllamaAI:
    """Simplified Ollama AI integration for GUI"""
    
    def __init__(self):
        self.code_assistant = None
        self.model = "codellama:7b"
        
        if OLLAMA_AVAILABLE:
            try:
                self.code_assistant = CodeAssistant()
                print("✅ Ollama AI initialized")
            except Exception as e:
                print(f"⚠️ Ollama AI init failed: {e}")
    
    def get_suggestion(self, command: str, context: str = "") -> Optional[str]:
        """Get AI suggestion for command"""
        if not self.code_assistant:
            return f"💡 AI suggestion for: {command}\n(Ollama not available - showing fallback)"
        
        try:
            # Simple completion request
            result = self.code_assistant.code_completion(
                partial_code=command,
                language='bash',
                context=context
            )
            return result if result else "No suggestion available"
        except Exception as e:
            return f"AI Error: {str(e)[:100]}..."
    
    def explain_error(self, command: str, error: str) -> Optional[str]:
        """Explain command error"""
        if not self.code_assistant:
            return f"🔍 Error analysis for: {command}\n{error}\n(Ollama not available)"
        
        try:
            result = self.code_assistant.debug_code(
                code=command,
                error_message=error,
                language='bash'
            )
            return result if result else "No explanation available"
        except Exception as e:
            return f"Debug Error: {str(e)[:100]}..."

class TerminalGUI:
    """Modern AI Terminal GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 AI Enhanced Terminal")
        self.root.geometry("1400x900")
        
        # Configuration
        self.config_dir = Path.home() / ".config" / "ai-terminal"
        self.config_file = self.config_dir / "gui_config.json"
        self.config = self.load_config()
        
        # AI integration
        self.ai = OllamaAI()
        self.command_history = []
        self.history_index = -1
        
        # Threading
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Setup GUI
        self.setup_ui()
        self.setup_bindings()
        
        # Start background worker
        self.worker_thread = threading.Thread(target=self.command_worker, daemon=True)
        self.worker_thread.start()
        
        # Start result processor
        self.root.after(100, self.process_results)
        
        # Welcome message
        self.add_terminal_output("🤖 AI Enhanced Terminal - Chat & Command Interface\n", "ai_response")
        self.add_terminal_output("💡 You can type shell commands or chat with AI naturally!\n", "info")
        self.add_terminal_output("Examples:\n", "info")
        self.add_terminal_output("  - Commands: ls, git status, python script.py\n", "info")
        self.add_terminal_output("  - Chat: What is Docker? How do I use git?\n", "info")
        self.add_terminal_output("=" * 60 + "\n")
    
    def load_config(self) -> Dict[str, Any]:
        """Load GUI configuration"""
        default_config = {
            "theme": {
                "bg_color": "#1e1e1e",
                "fg_color": "#ffffff",
                "prompt_color": "#00ff00",
                "ai_color": "#4da6ff",
                "error_color": "#ff4444",
                "font_family": "JetBrains Mono",
                "font_size": 11
            },
            "layout": {
                "terminal_width": 70,
                "ai_width": 30,
                "show_ai_panel": True,
                "auto_suggest": True
            },
            "ai": {
                "enabled": True,
                "model": "codellama:7b",
                "auto_explain_errors": True,
                "suggestion_delay": 1.0
            }
        }
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Config load error: {e}")
        else:
            self.save_config(default_config)
        
        return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Configure colors and fonts
        bg_color = self.config["theme"]["bg_color"]
        fg_color = self.config["theme"]["fg_color"]
        font_family = self.config["theme"]["font_family"]
        font_size = self.config["theme"]["font_size"]
        
        self.root.configure(bg=bg_color)
        
        # Main frame - unified terminal like Warp
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Terminal output area - unified like Warp
        terminal_label = ttk.Label(self.main_frame, text="🤖 AI Enhanced Terminal - Chat & Commands")
        terminal_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        self.terminal_output = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            bg=bg_color,
            fg=fg_color,
            font=(font_family, font_size),
            insertbackground=fg_color,
            height=25  # Make it taller
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Make terminal interactive - no separate input area
        self.terminal_output.bind('<KeyPress>', self.on_terminal_key)
        self.terminal_output.bind('<Return>', self.on_enter_key)
        self.terminal_output.focus_set()  # Focus on terminal
        
        # Track current input
        self.current_input = ""
        self.input_start_pos = None
        
        # AI is now integrated into the main terminal - no separate panel needed
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root, 
            text="Ready | Ollama: " + ("✅ Connected" if OLLAMA_AVAILABLE else "❌ Disconnected"),
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu bar
        self.setup_menu()
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_command(label="Load Session", command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle AI Panel", command=self.toggle_ai_panel)
        view_menu.add_command(label="Clear All", command=self.clear_all)
        
        # AI menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="AI", menu=ai_menu)
        ai_menu.add_command(label="Get Suggestion", command=self.get_ai_suggestion)
        ai_menu.add_command(label="Explain Error", command=self.explain_last_error)
        ai_menu.add_separator()
        ai_menu.add_command(label="AI Settings", command=self.show_ai_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_bindings(self):
        """Setup keyboard bindings"""
        self.command_entry.bind('<Return>', lambda e: self.execute_command())
        self.command_entry.bind('<Up>', self.history_up)
        self.command_entry.bind('<Down>', self.history_down)
        self.command_entry.bind('<Tab>', self.auto_complete)
        self.command_entry.bind('<Control-l>', lambda e: self.clear_terminal())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
        
        # Auto-suggestion on typing (if enabled)
        if self.config["layout"]["auto_suggest"]:
            self.command_entry.bind('<KeyRelease>', self.on_typing)
    
    def on_typing(self, event):
        """Handle typing for auto-suggestions"""
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return', 'Tab']:
            return
        
        # Debounced AI suggestion
        if hasattr(self, 'suggest_timer'):
            self.root.after_cancel(self.suggest_timer)
        
        self.suggest_timer = self.root.after(
            int(self.config["ai"]["suggestion_delay"] * 1000),
            self.auto_suggest
        )
    
    def auto_suggest(self):
        """Auto-suggest based on current input"""
        command = self.command_entry.get().strip()
        if len(command) > 2 and self.config["layout"]["show_ai_panel"]:
            threading.Thread(
                target=self.get_ai_suggestion_async,
                args=(command,),
                daemon=True
            ).start()
    
    def execute_command(self):
        """Execute the entered command"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = -1
        
        # Determine if it's a command or AI chat
        is_command = self.is_shell_command(command)
        
        if is_command:
            self.add_terminal_output(f"\n💻 {command}\n", "prompt")
        else:
            self.add_terminal_output(f"\n💬 You: {command}\n", "user_message")
        
        # Clear input
        self.command_entry.delete(0, tk.END)
        
        # Handle based on type
        if not is_command:
            # It's an AI chat message - get AI response
            self.command_queue.put(('ai_chat', command))
            self.update_status("AI thinking...")
            return
        
        # Queue command for execution
        self.command_queue.put(('execute', command))
        
        # Update status
        self.update_status("Executing command...")
        
        # Auto-suggest if enabled
        if self.config["ai"]["enabled"] and self.config["layout"]["show_ai_panel"]:
            threading.Thread(
                target=self.get_ai_suggestion_async,
                args=(command,),
                daemon=True
            ).start()
    
    def is_shell_command(self, text: str) -> bool:
        """Determine if input is a shell command or AI chat"""
        # Common shell command patterns
        shell_indicators = [
            'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'cp', 'mv', 'rm',
            'cat', 'less', 'more', 'head', 'tail', 'grep', 'find',
            'chmod', 'chown', 'ps', 'top', 'htop', 'kill', 'killall',
            'git', 'python', 'python3', 'pip', 'npm', 'node', 'java',
            'gcc', 'make', 'cmake', 'sudo', 'apt', 'yum', 'dnf',
            'systemctl', 'service', 'docker', 'kubectl', 'ssh', 'scp',
            'curl', 'wget', 'tar', 'zip', 'unzip', 'echo', 'printf',
            './', '../', '/', '~/', 'clear', 'history', 'which', 'whereis'
        ]
        
        # Check if starts with common shell patterns
        first_word = text.split()[0] if text.split() else ""
        
        # Shell command indicators
        if first_word in shell_indicators:
            return True
        if text.startswith(('./', '../', '/', '~/', 'sudo ')):
            return True
        if '|' in text or '>' in text or '<' in text:
            return True
        if text.startswith('export ') or '=' in text.split()[0] if text.split() else False:
            return True
            
        # Questions and natural language are AI chat
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'should']
        if any(text.lower().startswith(word) for word in question_words):
            return False
            
        # Default to command if unsure
        return len(text.split()) <= 3  # Short inputs are likely commands
    
    def command_worker(self):
        """Background worker for command execution"""
        while True:
            try:
                action, data = self.command_queue.get(timeout=1)
                
                if action == 'execute':
                    self.execute_command_bg(data)
                elif action == 'ai_suggest':
                    self.ai_suggest_bg(data)
                elif action == 'ai_explain':
                    self.ai_explain_bg(data)
                elif action == 'ai_chat':
                    self.ai_chat_bg(data)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.result_queue.put(('error', f"Worker error: {e}"))
    
    def execute_command_bg(self, command: str):
        """Execute command in background"""
        try:
            # Handle special commands
            if command.lower() in ['exit', 'quit']:
                self.result_queue.put(('special', 'exit'))
                return
            elif command.lower() == 'clear':
                self.result_queue.put(('special', 'clear'))
                return
            elif command.lower() == 'help':
                self.result_queue.put(('special', 'help'))
                return
            
            # Execute shell command
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                executable='/bin/zsh',
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'SHELL': '/bin/zsh'}
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            output = result.stdout
            
            if result.stderr:
                output += f"\n{result.stderr}"
            
            self.result_queue.put(('command_result', {
                'command': command,
                'success': success,
                'output': output,
                'execution_time': execution_time
            }))
            
        except subprocess.TimeoutExpired:
            self.result_queue.put(('command_result', {
                'command': command,
                'success': False,
                'output': "Command timed out (30s limit)",
                'execution_time': 30.0
            }))
        except Exception as e:
            self.result_queue.put(('error', f"Command execution error: {e}"))
    
    def ai_suggest_bg(self, command: str):
        """Get AI suggestion in background"""
        try:
            suggestion = self.ai.get_suggestion(command)
            self.result_queue.put(('ai_suggestion', suggestion))
        except Exception as e:
            self.result_queue.put(('ai_error', f"AI suggestion error: {e}"))
    
    def ai_explain_bg(self, data: tuple):
        """Get AI explanation in background"""
        try:
            command, error = data
            explanation = self.ai.explain_error(command, error)
            self.result_queue.put(('ai_explanation', explanation))
        except Exception as e:
            self.result_queue.put(('ai_error', f"AI explanation error: {e}"))
    
    def ai_chat_bg(self, message: str):
        """Handle AI chat conversation in background"""
        try:
            # Use AI for general conversation
            if self.ai.code_assistant:
                # Try to get a conversational response
                response = self.ai.get_suggestion(f"Respond to this message conversationally: {message}")
            else:
                # Fallback response
                response = f"I understand you said: '{message}'. I'm an AI assistant integrated into this terminal. I can help with commands, coding, and general questions. However, my full AI capabilities aren't available right now (Ollama connection issue). You can still run shell commands normally!"
            
            self.result_queue.put(('ai_chat_response', response))
        except Exception as e:
            self.result_queue.put(('ai_error', f"AI chat error: {e}"))
    
    def process_results(self):
        """Process results from background workers"""
        try:
            while True:
                result_type, data = self.result_queue.get_nowait()
                
                if result_type == 'command_result':
                    self.handle_command_result(data)
                elif result_type == 'ai_suggestion':
                    self.handle_ai_suggestion(data)
                elif result_type == 'ai_explanation':
                    self.handle_ai_explanation(data)
                elif result_type == 'ai_chat_response':
                    self.handle_ai_chat_response(data)
                elif result_type == 'ai_error':
                    self.add_terminal_output(f"❌ AI Error: {data}\n", "error")
                elif result_type == 'error':
                    self.add_terminal_output(f"❌ {data}\n", "error")
                elif result_type == 'special':
                    self.handle_special_command(data)
                
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_results)
    
    def handle_command_result(self, data: Dict[str, Any]):
        """Handle command execution result"""
        command = data['command']
        success = data['success']
        output = data['output']
        exec_time = data['execution_time']
        
        # Show output
        if output.strip():
            color = "normal" if success else "error"
            self.add_terminal_output(output, color)
        
        # Show execution time for slow commands
        if exec_time > 1.0:
            self.add_terminal_output(f"\n⏱️ Execution time: {exec_time:.2f}s\n", "info")
        
        # Auto-explain errors if enabled
        if not success and self.config["ai"]["auto_explain_errors"]:
            if self.config["layout"]["show_ai_panel"]:
                self.command_queue.put(('ai_explain', (command, output)))
        
        self.update_status("Ready")
    
    def handle_ai_suggestion(self, suggestion: str):
        """Handle AI suggestion result"""
        self.add_terminal_output(f"💡 AI Suggestion: {suggestion}\n\n", "ai_response")
    
    def handle_ai_explanation(self, explanation: str):
        """Handle AI explanation result"""
        self.add_terminal_output(f"🔍 AI Analysis: {explanation}\n\n", "ai_response")
    
    def handle_ai_chat_response(self, response: str):
        """Handle AI chat response"""
        self.add_terminal_output(f"🤖 AI: {response}\n\n", "ai_response")
    
    def handle_special_command(self, command: str):
        """Handle special commands"""
        if command == 'exit':
            self.root.quit()
        elif command == 'clear':
            self.clear_terminal()
        elif command == 'help':
            self.show_help()
    
    def add_terminal_output(self, text: str, text_type: str = "normal"):
        """Add text to terminal output"""
        self.terminal_output.insert(tk.END, text)
        
        # Configure text color based on type
        if text_type == "error":
            self.terminal_output.tag_add("error", "end-{}c".format(len(text)), "end")
            self.terminal_output.tag_configure("error", foreground=self.config["theme"]["error_color"])
        elif text_type == "prompt":
            self.terminal_output.tag_add("prompt", "end-{}c".format(len(text)), "end")
            self.terminal_output.tag_configure("prompt", foreground=self.config["theme"]["prompt_color"])
        elif text_type == "info":
            self.terminal_output.tag_add("info", "end-{}c".format(len(text)), "end")
            self.terminal_output.tag_configure("info", foreground=self.config["theme"]["ai_color"])
        elif text_type == "user_message":
            self.terminal_output.tag_add("user_message", "end-{}c".format(len(text)), "end")
            self.terminal_output.tag_configure("user_message", foreground="#90EE90", font=("Arial", 11, "bold"))
        elif text_type == "ai_response":
            self.terminal_output.tag_add("ai_response", "end-{}c".format(len(text)), "end")
            self.terminal_output.tag_configure("ai_response", foreground=self.config["theme"]["ai_color"], font=("Arial", 11, "italic"))
        
        self.terminal_output.see(tk.END)
    
    # AI output is now integrated into main terminal
    
    def get_ai_suggestion(self):
        """Get AI suggestion for current command"""
        command = self.command_entry.get().strip()
        if command:
            self.command_queue.put(('ai_suggest', command))
    
    def get_ai_suggestion_async(self, command: str):
        """Get AI suggestion asynchronously"""
        self.command_queue.put(('ai_suggest', command))
    
    def explain_last_error(self):
        """Explain the last error"""
        # This would need to track the last failed command
        self.add_ai_output("🔍 Last error explanation feature coming soon...\n")
    
    def auto_complete(self, event):
        """Handle tab completion"""
        command = self.command_entry.get()
        if command:
            self.get_ai_suggestion()
        return "break"  # Prevent default tab behavior
    
    def history_up(self, event):
        """Navigate command history up"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            cmd = self.command_history[-(self.history_index + 1)]
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, cmd)
    
    def history_down(self, event):
        """Navigate command history down"""
        if self.history_index > 0:
            self.history_index -= 1
            cmd = self.command_history[-(self.history_index + 1)]
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, cmd)
        elif self.history_index == 0:
            self.history_index = -1
            self.command_entry.delete(0, tk.END)
    
    def clear_terminal(self):
        """Clear terminal output"""
        self.terminal_output.delete(1.0, tk.END)
    
    def clear_all(self):
        """Clear terminal output"""
        self.clear_terminal()
    
    def toggle_ai_panel(self):
        """Toggle AI panel visibility"""
        # This would require rebuilding the UI
        messagebox.showinfo("Info", "AI panel toggle will be implemented in next version")
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=f"{message} | Ollama: " + 
                              ("✅ Connected" if OLLAMA_AVAILABLE else "❌ Disconnected"))
    
    def show_help(self):
        """Show help information"""
        help_text = """🤖 AI Enhanced Terminal GUI

Commands:
• Type any shell command and press Enter
• Use Up/Down arrows for command history
• Press Tab for AI completion suggestions

Special Commands:
• help - Show this help
• clear - Clear terminal output
• exit/quit - Exit application

Keyboard Shortcuts:
• Ctrl+L - Clear terminal
• Ctrl+Q - Quit application
• F1 - Show shortcuts
• Tab - AI completion

Features:
• Real-time AI suggestions
• Error analysis and explanation
• Command history
• Split-pane interface
"""
        self.add_terminal_output(help_text)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        messagebox.showinfo("Keyboard Shortcuts", """
Keyboard Shortcuts:

Ctrl+L     - Clear terminal
Ctrl+Q     - Quit application
F1         - Show this help
Tab        - AI completion
Up/Down    - Command history
Enter      - Execute command

Menu Options:
File       - Save/Load sessions
View       - Toggle panels, clear all
AI         - AI suggestions and settings
Help       - Documentation and about
        """)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", f"""
🤖 AI Enhanced Terminal GUI

A modern terminal interface with integrated 
Ollama AI assistance.

Features:
• Real-time command suggestions
• Error analysis and explanations  
• Command history and completion
• Integrated AI chat interface
• Zsh shell integration

Ollama Status: {"✅ Connected" if OLLAMA_AVAILABLE else "❌ Not Available"}

Built with Python and tkinter
        """)
    
    def show_ai_settings(self):
        """Show AI settings dialog"""
        messagebox.showinfo("AI Settings", "AI settings dialog coming soon...")
    
    def save_session(self):
        """Save current session"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.terminal_output.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Session saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save session: {e}")
    
    def load_session(self):
        """Load a session file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.terminal_output.delete(1.0, tk.END)
                self.terminal_output.insert(1.0, content)
                messagebox.showinfo("Success", f"Session loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load session: {e}")
    
    def run(self):
        """Start the GUI application"""
        self.command_entry.focus_set()
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = TerminalGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == "__main__":
    main()