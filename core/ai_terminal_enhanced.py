#!/usr/bin/env python3
"""
Enhanced AI Terminal with better Ollama integration
Optimized for zsh and your existing setup
"""

import subprocess
import sys
import os
import json
import time
import threading
import signal
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, List

class OllamaIntegration:
    """Better integration with existing Ollama enhancements"""
    
    def __init__(self):
        self.ollama_path = Path("/home/nike/ollama-enhancements")
        self.code_assistant = None
        self.quality_scorer = None
        self.conversation_memory = None
        self.performance_monitor = None
        
        self.load_ollama_components()
    
    def load_component(self, component_name: str, module_path: str):
        """Dynamically load an Ollama component"""
        try:
            spec = importlib.util.spec_from_file_location(component_name, module_path)
            if spec is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Failed to load {component_name}: {e}")
            return None
    
    def load_ollama_components(self):
        """Load all available Ollama components"""
        components = {
            'code_assistant': self.ollama_path / "code-assistant/code_assistant.py",
            'quality_scorer': self.ollama_path / "quality-scorer/quality_scorer.py", 
            'conversation_memory': self.ollama_path / "memory-system/conversation_memory.py",
            'performance_monitor': self.ollama_path / "performance-monitor/performance_monitor.py"
        }
        
        loaded_components = []
        
        for name, path in components.items():
            if path.exists():
                module = self.load_component(name, str(path))
                if module:
                    try:
                        if name == 'code_assistant' and hasattr(module, 'CodeAssistant'):
                            self.code_assistant = module.CodeAssistant()
                            loaded_components.append('CodeAssistant')
                        elif name == 'quality_scorer' and hasattr(module, 'QualityScorer'):
                            self.quality_scorer = module.QualityScorer()
                            loaded_components.append('QualityScorer')
                        elif name == 'conversation_memory' and hasattr(module, 'ConversationMemory'):
                            self.conversation_memory = module.ConversationMemory()
                            loaded_components.append('ConversationMemory')
                        elif name == 'performance_monitor' and hasattr(module, 'PerformanceMonitor'):
                            self.performance_monitor = module.PerformanceMonitor()
                            loaded_components.append('PerformanceMonitor')
                    except Exception as e:
                        print(f"Failed to initialize {name}: {e}")
        
        if loaded_components:
            print(f"✅ Loaded Ollama components: {', '.join(loaded_components)}")
        else:
            print("⚠️ No Ollama components loaded, running in basic mode")
    
    def get_code_suggestion(self, partial_command: str, context: str = "") -> Optional[str]:
        """Get code suggestion using CodeAssistant"""
        if not self.code_assistant:
            return None
        
        try:
            # Detect language/context
            if any(word in partial_command for word in ['git', 'gh', 'glab']):
                language = 'bash'
            elif any(word in partial_command for word in ['python', 'python3', 'pip']):
                language = 'python'
            elif any(word in partial_command for word in ['node', 'npm', 'yarn']):
                language = 'javascript'
            elif any(word in partial_command for word in ['docker', 'kubectl']):
                language = 'bash'
            else:
                language = 'bash'
            
            # Get completion
            completion = self.code_assistant.code_completion(
                partial_code=partial_command,
                language=language,
                context=context
            )
            
            return completion.strip() if completion else None
            
        except Exception as e:
            print(f"AI suggestion error: {e}")
            return None
    
    def debug_command(self, command: str, error_output: str) -> Optional[str]:
        """Debug failed command using CodeAssistant"""
        if not self.code_assistant:
            return None
        
        try:
            debug_result = self.code_assistant.debug_code(
                code=command,
                error_message=error_output,
                language='bash'
            )
            return debug_result if debug_result else None
        except Exception as e:
            print(f"Debug error: {e}")
            return None

class EnhancedAITerminal:
    """Enhanced AI terminal with better zsh support"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "ai-terminal"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        self.config = self.load_config()
        self.ollama = OllamaIntegration()
        self.running = True
        self.command_history = []
        self.session_start = time.time()
        
        # Zsh-specific features
        self.zsh_aliases = self.load_zsh_aliases()
        self.zsh_functions = self.load_zsh_functions()
    
    def load_config(self) -> Dict[str, Any]:
        """Load enhanced configuration"""
        default_config = {
            "ai_enabled": True,
            "model": "codellama:7b",
            "suggest_on_tab": True,
            "explain_errors": True,
            "auto_suggestions": True,
            "context_aware": True,
            "shell": "zsh",
            "theme": {
                "prompt": "🤖",
                "prompt_color": "\033[1;32m",
                "ai_color": "\033[1;34m",
                "error_color": "\033[1;31m",
                "success_color": "\033[1;32m",
                "warning_color": "\033[1;33m",
                "reset": "\033[0m"
            },
            "features": {
                "smart_completion": True,
                "error_analysis": True,
                "command_suggestions": True,
                "performance_hints": True,
                "security_warnings": True
            },
            "zsh": {
                "load_aliases": True,
                "load_functions": True,
                "oh_my_zsh": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self.deep_update(default_config, user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            self.save_config(default_config)
        
        return default_config
    
    def deep_update(self, base_dict: dict, update_dict: dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self.deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_zsh_aliases(self) -> Dict[str, str]:
        """Load zsh aliases"""
        aliases = {}
        try:
            # Get aliases from zsh
            result = subprocess.run(['zsh', '-c', 'alias'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '=' in line and line.strip():
                        try:
                            alias_name, alias_value = line.split('=', 1)
                            aliases[alias_name.strip()] = alias_value.strip('\'"')
                        except:
                            continue
        except Exception:
            pass
        
        return aliases
    
    def load_zsh_functions(self) -> List[str]:
        """Load zsh function names"""
        functions = []
        try:
            # Get function names from zsh
            result = subprocess.run(['zsh', '-c', 'print -l ${(k)functions}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                functions = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except Exception:
            pass
        
        return functions
    
    def get_smart_suggestions(self, partial_command: str) -> List[str]:
        """Get smart command suggestions"""
        suggestions = []
        
        # AI-powered suggestions
        ai_suggestion = self.ollama.get_code_suggestion(partial_command)
        if ai_suggestion:
            suggestions.append(f"🤖 AI: {ai_suggestion}")
        
        # Zsh alias suggestions
        if partial_command in self.zsh_aliases:
            suggestions.append(f"📎 Alias: {self.zsh_aliases[partial_command]}")
        
        # Common command suggestions
        common_patterns = {
            'git': ['status', 'add .', 'commit -m ""', 'push', 'pull', 'log --oneline'],
            'python': ['-m pip install', '-c', '-m venv venv', '-m http.server'],
            'docker': ['ps', 'images', 'run -it', 'build .', 'compose up'],
            'kubectl': ['get pods', 'get services', 'describe', 'logs'],
            'npm': ['install', 'start', 'run build', 'test'],
        }
        
        for cmd, patterns in common_patterns.items():
            if partial_command.startswith(cmd):
                remaining = partial_command[len(cmd):].strip()
                if not remaining:
                    suggestions.extend([f"💡 {cmd} {pattern}" for pattern in patterns[:3]])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def print_colored(self, text: str, color_key: str = "reset"):
        """Print colored text"""
        color = self.config["theme"].get(color_key, "")
        reset = self.config["theme"]["reset"]
        print(f"{color}{text}{reset}")
    
    def show_suggestions(self, partial_command: str):
        """Show smart suggestions"""
        if not partial_command.strip():
            return
        
        suggestions = self.get_smart_suggestions(partial_command)
        if suggestions:
            self.print_colored("\n💡 Suggestions:", "ai_color")
            for suggestion in suggestions:
                print(f"   {suggestion}")
            print()
    
    def analyze_error(self, command: str, error_output: str):
        """Analyze and explain command errors"""
        if not self.config["features"]["error_analysis"]:
            return
        
        explanation = self.ollama.debug_command(command, error_output)
        if explanation:
            print()
            self.print_colored("🔍 Error Analysis:", "warning_color")
            self.print_colored(f"   {explanation}", "ai_color")
            print()
    
    def show_performance_hint(self, command: str, execution_time: float):
        """Show performance hints for slow commands"""
        if execution_time > 2.0:  # Commands taking more than 2 seconds
            hints = {
                'find': 'Try using `fd` for faster file searching',
                'grep': 'Consider using `rg` (ripgrep) for faster text search',
                'ls': 'Use `exa` or `lsd` for faster directory listing with colors',
                'cat': 'Try `bat` for syntax-highlighted file viewing',
                'ps': 'Use `htop` or `btop` for better process monitoring'
            }
            
            for cmd, hint in hints.items():
                if command.startswith(cmd):
                    self.print_colored(f"⚡ Performance hint: {hint}", "warning_color")
                    break
    
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
            self.show_suggestions(cmd[3:])
            return True
        elif cmd.startswith('explain '):
            error_text = cmd[8:]
            explanation = self.ollama.debug_command("", error_text)
            if explanation:
                self.print_colored(f"🔍 Explanation: {explanation}", "ai_color")
            else:
                self.print_colored("No explanation available", "error_color")
            return True
        elif cmd == 'stats':
            self.show_session_stats()
            return True
        elif cmd == 'aliases':
            self.show_zsh_aliases()
            return True
        elif cmd in ['exit', 'quit']:
            self.running = False
            return True
        
        return False
    
    def show_help(self):
        """Show enhanced help"""
        self.print_colored("🤖 Enhanced AI Terminal", "ai_color")
        print("Commands:")
        print("  help, ?           - Show this help")
        print("  config            - Edit configuration")
        print("  ai <command>      - Get AI suggestions")
        print("  explain <error>   - Explain error message")
        print("  stats             - Show session statistics")
        print("  aliases           - Show zsh aliases")
        print("  exit, quit        - Exit terminal")
        print()
        print("Features:")
        print("  • Press Tab for AI suggestions")
        print("  • Automatic error analysis")
        print("  • Performance hints for slow commands")
        print("  • Zsh alias integration")
        print("  • Smart context awareness")
        print()
        
        # Show loaded components
        components = []
        if self.ollama.code_assistant:
            components.append("CodeAssistant")
        if self.ollama.quality_scorer:
            components.append("QualityScorer")
        if self.ollama.conversation_memory:
            components.append("ConversationMemory")
        
        if components:
            self.print_colored(f"🔧 Loaded: {', '.join(components)}", "success_color")
        else:
            self.print_colored("⚠️ AI components not loaded", "warning_color")
        print()
    
    def show_session_stats(self):
        """Show session statistics"""
        uptime = time.time() - self.session_start
        self.print_colored("📊 Session Statistics:", "ai_color")
        print(f"   Uptime: {uptime:.1f} seconds")
        print(f"   Commands executed: {len(self.command_history)}")
        if self.command_history:
            print(f"   Last command: {self.command_history[-1][:50]}...")
        print(f"   Zsh aliases loaded: {len(self.zsh_aliases)}")
        print(f"   Zsh functions loaded: {len(self.zsh_functions)}")
        print()
    
    def show_zsh_aliases(self):
        """Show zsh aliases"""
        if not self.zsh_aliases:
            self.print_colored("No zsh aliases loaded", "warning_color")
            return
        
        self.print_colored("📎 Zsh Aliases:", "ai_color")
        for alias, value in list(self.zsh_aliases.items())[:10]:  # Show first 10
            print(f"   {alias} -> {value}")
        
        if len(self.zsh_aliases) > 10:
            print(f"   ... and {len(self.zsh_aliases) - 10} more")
        print()
    
    def edit_config(self):
        """Open configuration for editing"""
        editor = os.environ.get('EDITOR', 'nano')
        try:
            subprocess.run([editor, str(self.config_file)])
            self.config = self.load_config()
            self.print_colored("Configuration updated! 🎉", "success_color")
        except Exception as e:
            self.print_colored(f"Error editing config: {e}", "error_color")
    
    def run_command(self, command: str) -> tuple[bool, str, float]:
        """Run shell command and return success, output, execution time"""
        start_time = time.time()
        try:
            # Use zsh as the shell
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
            output = result.stdout
            if result.stderr:
                output += result.stderr
            
            return result.returncode == 0, output, execution_time
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return False, "Command timed out (30s limit)", execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            return False, str(e), execution_time
    
    def run_interactive_shell(self):
        """Run enhanced interactive shell"""
        self.print_colored("🚀 Enhanced AI Terminal Started", "success_color")
        print("Optimized for zsh with AI assistance")
        print("Type 'help' for commands, Tab for suggestions")
        print("=" * 50)
        
        while self.running:
            try:
                # Enhanced prompt
                prompt_symbol = self.config["theme"]["prompt"]
                prompt_color = self.config["theme"]["prompt_color"]
                reset_color = self.config["theme"]["reset"]
                
                prompt = f"{prompt_color}{prompt_symbol} ai-terminal{reset_color} "
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                # Add to history
                self.command_history.append(command)
                
                # Handle special commands
                if self.handle_special_commands(command):
                    continue
                
                # Show suggestions on Tab-like behavior (when command ends with space and user wants help)
                if command.endswith(' ?'):
                    self.show_suggestions(command[:-2])
                    continue
                
                # Execute command
                success, output, exec_time = self.run_command(command)
                
                # Show output
                if output.strip():
                    if success:
                        print(output)
                    else:
                        print(output)
                        # Analyze error if enabled
                        if self.config["features"]["error_analysis"]:
                            self.analyze_error(command, output)
                
                # Show performance hints
                if self.config["features"]["performance_hints"]:
                    self.show_performance_hint(command, exec_time)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit (Ctrl+C to interrupt commands)")
                continue
            except EOFError:
                break
        
        self.print_colored("Thanks for using AI Terminal! 👋", "success_color")

def main():
    """Main entry point"""
    try:
        import argparse
        parser = argparse.ArgumentParser(description="Enhanced AI Terminal")
        parser.add_argument("--no-ai", action="store_true", help="Disable AI features")
        parser.add_argument("--config", help="Configuration file path")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        args = parser.parse_args()
        
        if args.debug:
            print("Debug mode enabled")
    except ImportError:
        args = None
    
    # Handle signals
    def signal_handler(signum, frame):
        print("\nExiting gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run enhanced terminal
    terminal = EnhancedAITerminal()
    terminal.run_interactive_shell()

if __name__ == "__main__":
    main()