#!/usr/bin/env python3
"""
AI Terminal Proxy
Real terminal integration with AI assistance
"""

import os
import sys
import pty
import select
import termios
import tty
import signal
import json
import threading
import time
from pathlib import Path

# Ollama integration
OLLAMA_PATH = "/home/nike/ollama-enhancements"
sys.path.insert(0, OLLAMA_PATH)

try:
    from code_assistant.code_assistant import CodeAssistant
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class TerminalProxy:
    def __init__(self):
        self.master_fd = None
        self.slave_fd = None
        self.original_settings = None
        self.running = True
        self.current_input = ""
        self.ai_assistant = None
        
        # Initialize AI if available
        if AI_AVAILABLE:
            try:
                self.ai_assistant = CodeAssistant()
                print("\033[32m🤖 AI assistant ready\033[0m")
            except Exception as e:
                print(f"\033[33m⚠️ AI init failed: {e}\033[0m")
        
        # Setup signal handlers
        signal.signal(signal.SIGWINCH, self.handle_resize)
    
    def handle_resize(self, signum, frame):
        """Handle terminal resize"""
        if self.master_fd:
            # Get current terminal size
            rows, cols = os.popen('stty size', 'r').read().split()
            # Resize the pty
            os.system(f'stty -F /dev/pts/{self.master_fd} rows {rows} cols {cols} 2>/dev/null')
    
    def setup_terminal(self):
        """Setup pseudo-terminal"""
        # Save original terminal settings
        self.original_settings = termios.tcgetattr(sys.stdin.fileno())
        
        # Create pty
        self.master_fd, self.slave_fd = pty.openpty()
        
        # Set terminal to raw mode
        tty.setraw(sys.stdin.fileno())
        
        return True
    
    def restore_terminal(self):
        """Restore original terminal settings"""
        if self.original_settings:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.original_settings)
        if self.master_fd:
            os.close(self.master_fd)
        if self.slave_fd:
            os.close(self.slave_fd)
    
    def get_ai_suggestion(self, partial_command: str) -> str:
        """Get AI suggestion for partial command"""
        if not self.ai_assistant or not partial_command.strip():
            return ""
        
        try:
            # Get completion from AI
            completion = self.ai_assistant.code_completion(
                partial_command, 
                'bash', 
                ""
            )
            return completion if completion else ""
        except Exception:
            return ""
    
    def show_ai_suggestion(self, suggestion: str):
        """Display AI suggestion"""
        if suggestion:
            # Save cursor position
            sys.stdout.write('\033[s')
            # Move to next line
            sys.stdout.write('\n')
            # Show suggestion in dim gray
            sys.stdout.write(f'\033[2m💡 {suggestion}\033[0m')
            # Restore cursor position
            sys.stdout.write('\033[u')
            sys.stdout.flush()
    
    def handle_tab_completion(self):
        """Handle tab key for AI completion"""
        if not self.current_input.strip():
            return False
        
        suggestion = self.get_ai_suggestion(self.current_input)
        if suggestion:
            # Clear current suggestion line
            sys.stdout.write('\033[K')
            # Show suggestion
            self.show_ai_suggestion(suggestion)
            return True
        return False
    
    def process_input(self, data: bytes) -> bytes:
        """Process input data"""
        try:
            char = data.decode('utf-8')
        except:
            return data
        
        if char == '\t':  # Tab key
            if self.handle_tab_completion():
                return b''  # Don't pass tab to shell
        elif char == '\r' or char == '\n':  # Enter key
            self.current_input = ""
        elif char == '\x7f':  # Backspace
            if self.current_input:
                self.current_input = self.current_input[:-1]
        elif char.isprintable():
            self.current_input += char
        
        return data
    
    def run_shell(self):
        """Run the shell process"""
        shell = os.environ.get('SHELL', '/bin/bash')
        
        try:
            pid = os.fork()
            if pid == 0:  # Child process
                # Set up the slave terminal
                os.setsid()
                os.dup2(self.slave_fd, 0)
                os.dup2(self.slave_fd, 1)
                os.dup2(self.slave_fd, 2)
                
                # Close the master fd in child
                os.close(self.master_fd)
                
                # Execute the shell
                os.execv(shell, [shell])
            else:  # Parent process
                # Close slave fd in parent
                os.close(self.slave_fd)
                self.slave_fd = None
                
                return pid
        except OSError as e:
            print(f"Error starting shell: {e}")
            return None
    
    def main_loop(self, shell_pid):
        """Main terminal loop"""
        try:
            while self.running:
                # Use select to check for input from stdin or shell
                ready, _, _ = select.select([sys.stdin, self.master_fd], [], [], 0.1)
                
                for fd in ready:
                    if fd == sys.stdin:
                        # User input
                        try:
                            data = os.read(sys.stdin.fileno(), 1024)
                            if data:
                                # Process input for AI features
                                processed_data = self.process_input(data)
                                if processed_data:
                                    os.write(self.master_fd, processed_data)
                        except OSError:
                            self.running = False
                            break
                    
                    elif fd == self.master_fd:
                        # Shell output
                        try:
                            data = os.read(self.master_fd, 1024)
                            if data:
                                sys.stdout.buffer.write(data)
                                sys.stdout.flush()
                            else:
                                self.running = False
                                break
                        except OSError:
                            self.running = False
                            break
                
                # Check if shell process is still alive
                try:
                    pid, status = os.waitpid(shell_pid, os.WNOHANG)
                    if pid:
                        self.running = False
                        break
                except OSError:
                    pass
        
        except KeyboardInterrupt:
            # Let the shell handle Ctrl+C
            os.write(self.master_fd, b'\x03')
        except Exception as e:
            print(f"\nTerminal error: {e}")
            self.running = False
    
    def run(self):
        """Main run method"""
        try:
            if not self.setup_terminal():
                print("Failed to setup terminal")
                return 1
            
            # Start shell
            shell_pid = self.run_shell()
            if not shell_pid:
                print("Failed to start shell")
                return 1
            
            # Run main loop
            self.main_loop(shell_pid)
            
        except Exception as e:
            print(f"Terminal proxy error: {e}")
            return 1
        
        finally:
            self.restore_terminal()
        
        return 0

def main():
    """Main entry point"""
    print("🚀 AI-Enhanced Terminal Proxy")
    print("Press Tab for AI suggestions, Ctrl+C to interrupt commands")
    print("=" * 50)
    
    proxy = TerminalProxy()
    return proxy.run()

if __name__ == "__main__":
    sys.exit(main())