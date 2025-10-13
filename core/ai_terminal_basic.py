#!/usr/bin/env python3
"""
AI-Enhanced Terminal
Simple terminal wrapper with Ollama integration
"""

import subprocess
import sys
import os
import json
import time
import threading
import signal
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import existing Ollama components
OLLAMA_PATH = "/home/nike/ollama-enhancements"
sys.path.insert(0, OLLAMA_PATH)

try:
    from code_assistant.code_assistant import CodeAssistant
    OLLAMA_AVAILABLE = True
    print("✅ Found existing Ollama enhancements")
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama enhancements not found, running in basic mode")

class AITerminal:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "ai-terminal"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        self.config = self.load_config()
        self.code_assistant = None
        self.running = True
        
        if OLLAMA_AVAILABLE and self.config.get("ai_enabled", True):
            try:
                self.code_assistant = CodeAssistant()
                print("🤖 AI assistant initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize AI assistant: {e}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "ai_enabled": True,
            "model": "codellama:7b",
            "suggest_on_tab": True,
            "explain_errors": True,
            "terminal_command": "bash",
            "theme": {
                "prompt_color": "\033[1;32m",  # Green
                "ai_color": "\033[1;34m",      # Blue
                "error_color": "\033[1;31m",   # Red
                "reset": "\033[0m"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            self.save_config(default_config)
        
        return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_ai_suggestion(self, command: str, context: str = "") -> Optional[str]:
        """Get AI suggestion for command"""
        if not self.code_assistant:
            return None
        
        try:
            # Use existing code assistant
            if command.strip().endswith('git'):
                return self.code_assistant.code_completion('git ', 'bash', context)
            elif 'python' in command:
                return self.code_assistant.code_completion(command, 'python', context)
            else:
                return self.code_assistant.code_completion(command, 'bash', context)
        except Exception as e:
            print(f"AI error: {e}")
            return None
    
    def explain_error(self, command: str, error_output: str) -> Optional[str]:
        """Explain command errors using AI"""
        if not self.code_assistant:
            return None
        
        try:
            return self.code_assistant.debug_code(command, error_output, 'bash')
        except Exception:
            return None
    
    def print_colored(self, text: str, color_key: str):
        """Print colored text"""
        color = self.config["theme"].get(color_key, "")
        reset = self.config["theme"]["reset"]
        print(f"{color}{text}{reset}")
    
    def show_help(self):
        """Show help message"""
        self.print_colored("AI-Enhanced Terminal", "ai_color")
        print("Commands:")
        print("  help, ?         - Show this help")
        print("  config          - Edit configuration")
        print("  ai <command>    - Get AI suggestion for command")
        print("  explain <error> - Explain error message")
        print("  exit, quit      - Exit terminal")
        print("")
        if self.code_assistant:
            print("🤖 AI Assistant: ENABLED")
        else:
            print("⚠️ AI Assistant: DISABLED")
        print("")
    
    def handle_special_commands(self, command: str) -> bool:
        """Handle special AI terminal commands"""
        cmd = command.strip().lower()
        
        if cmd in ['help', '?']:
            self.show_help()
            return True
        elif cmd == 'config':
            self.edit_config()
            return True
        elif cmd.startswith('ai '):
            suggestion = self.get_ai_suggestion(cmd[3:])
            if suggestion:
                self.print_colored(f"AI Suggestion: {suggestion}", "ai_color")
            else:
                self.print_colored("No suggestion available", "error_color")
            return True
        elif cmd.startswith('explain '):
            explanation = self.explain_error("", cmd[8:])
            if explanation:
                self.print_colored(f"AI Explanation: {explanation}", "ai_color")
            else:
                self.print_colored("No explanation available", "error_color")
            return True
        elif cmd in ['exit', 'quit']:
            self.running = False
            return True
        
        return False
    
    def edit_config(self):
        """Open configuration for editing"""
        editor = os.environ.get('EDITOR', 'nano')
        try:
            subprocess.run([editor, str(self.config_file)])
            self.config = self.load_config()
            self.print_colored("Configuration updated!", "ai_color")
        except Exception as e:
            self.print_colored(f"Error editing config: {e}", "error_color")
    
    def run_command(self, command: str) -> tuple[bool, str]:
        """Run shell command and return success, output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def run_interactive_shell(self):
        """Run interactive shell with AI enhancements"""
        self.print_colored("🚀 AI-Enhanced Terminal Started", "ai_color")
        print("Type 'help' for commands, 'exit' to quit")
        print("")
        
        while self.running:
            try:
                # Get command input
                prompt = self.config["theme"]["prompt_color"] + "ai-terminal> " + self.config["theme"]["reset"]
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                # Handle special commands
                if self.handle_special_commands(command):
                    continue
                
                # Execute command
                success, output = self.run_command(command)
                
                if output.strip():
                    print(output)
                
                # Offer AI help for failed commands
                if not success and self.code_assistant and self.config.get("explain_errors"):
                    explanation = self.explain_error(command, output)
                    if explanation:
                        print()
                        self.print_colored(f"🤖 AI: {explanation}", "ai_color")
                        print()
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
                continue
            except EOFError:
                break
        
        self.print_colored("Goodbye! 👋", "ai_color")

def main():
    """Main entry point"""
    parser = None
    try:
        import argparse
        parser = argparse.ArgumentParser(description="AI-Enhanced Terminal")
        parser.add_argument("--no-ai", action="store_true", help="Disable AI features")
        parser.add_argument("--config", help="Configuration file path")
        args = parser.parse_args()
        
        if args.no_ai:
            global OLLAMA_AVAILABLE
            OLLAMA_AVAILABLE = False
    except ImportError:
        args = None
    
    # Handle signals
    def signal_handler(signum, frame):
        print("\nExiting...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run terminal
    terminal = AITerminal()
    terminal.run_interactive_shell()

if __name__ == "__main__":
    main()