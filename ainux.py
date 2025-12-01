#!/usr/bin/env python3
"""
AiNux: Natural Language to System Command Executor
A prototype system that converts natural language input into system commands.

Author: AI Assistant
Date: September 15, 2025
"""

import subprocess
import sys
import os
import re
import platform
import argparse
from typing import Optional, Dict, List


class AiNux:
    """
    AiNux - Natural Language to System Command Executor
    
    This class handles the conversion of natural language input into system commands
    and executes them safely with proper error handling.
    """
    
    def __init__(self):
        """Initialize AiNux with platform-specific settings and command mappings."""
        self.platform = platform.system().lower()
        self.dangerous_commands = self._load_dangerous_commands()
        self.command_mappings = self._load_command_mappings()
    
    def _load_dangerous_commands(self) -> List[str]:
        """
        Load a list of dangerous commands that should not be executed.
        
        Returns:
            List[str]: List of dangerous command patterns
        """
        return [
            'rm -rf /',
            'del /q /s',
            'format',
            'fdisk',
            'mkfs',
            'dd',
            'shutdown',
            'reboot',
            'halt',
            'poweroff',
            'init 0',
            'init 6',
        ]
    
    def _load_command_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Load command mappings for different platforms.
        
        Returns:
            Dict: Command mappings organized by platform
        """
        return {
            'windows': {
                'list_files': 'dir',
                'current_directory': 'cd',
                'change_directory': 'cd',
                'create_directory': 'mkdir',
                'remove_file': 'del',
                'copy_file': 'copy',
                'move_file': 'move',
                'show_processes': 'tasklist',
                'network_info': 'ipconfig',
                'system_info': 'systeminfo',
                'disk_usage': 'dir /-c',
            },
            'linux': {
                'list_files': 'ls -la',
                'current_directory': 'pwd',
                'change_directory': 'cd',
                'create_directory': 'mkdir',
                'remove_file': 'rm',
                'copy_file': 'cp',
                'move_file': 'mv',
                'show_processes': 'ps aux',
                'network_info': 'ifconfig',
                'system_info': 'uname -a',
                'disk_usage': 'df -h',
            },
            'darwin': {  # macOS
                'list_files': 'ls -la',
                'current_directory': 'pwd',
                'change_directory': 'cd',
                'create_directory': 'mkdir',
                'remove_file': 'rm',
                'copy_file': 'cp',
                'move_file': 'mv',
                'show_processes': 'ps aux',
                'network_info': 'ifconfig',
                'system_info': 'uname -a',
                'disk_usage': 'df -h',
            }
        }
    
    def parse_natural_language(self, user_input: str) -> Optional[str]:
        """
        Convert natural language input into a system command.
        
        Args:
            user_input (str): Natural language input from user
            
        Returns:
            Optional[str]: System command or None if not recognized
        """
        # Convert input to lowercase for easier matching
        input_lower = user_input.lower().strip()
        
        # Define natural language patterns and their corresponding command types
        patterns = {
            'list_files': [
                r'list.*files?.*current.*director',
                r'show.*files?.*current.*director',
                r'list.*files?.*here',
                r'show.*files?.*here',
                r'list.*director.*content',
                r'what.*files?.*here',
                r'dir',
                r'ls'
            ],
            'current_directory': [
                r'show.*current.*director',
                r'what.*current.*director',
                r'where.*am.*i',
                r'current.*path',
                r'working.*director',
                r'pwd'
            ],
            'change_directory': [
                r'change.*director.*to\s+(\S+)',
                r'go.*to.*director.*(\S+)',
                r'cd\s+(\S+)',
                r'navigate.*to\s+(\S+)'
            ],
            'create_directory': [
                r'create.*director.*(\S+)',
                r'make.*director.*(\S+)',
                r'mkdir\s+(\S+)',
                r'new.*folder.*(\S+)'
            ],
            'show_processes': [
                r'show.*process',
                r'list.*process',
                r'running.*process',
                r'task.*list',
                r'ps'
            ],
            'network_info': [
                r'show.*network.*info',
                r'network.*config',
                r'ip.*config',
                r'network.*settings'
            ],
            'system_info': [
                r'system.*info',
                r'show.*system.*info',
                r'computer.*info',
                r'machine.*info'
            ],
            'disk_usage': [
                r'disk.*usage',
                r'disk.*space',
                r'storage.*info',
                r'free.*space'
            ]
        }
        
        # Try to match input against patterns
        for command_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, input_lower)
                if match:
                    # Get the appropriate command for the current platform
                    platform_commands = self.command_mappings.get(self.platform, {})
                    base_command = platform_commands.get(command_type)
                    
                    if base_command:
                        # Handle commands that need arguments
                        if command_type in ['change_directory', 'create_directory'] and match.groups():
                            return f"{base_command} {match.group(1)}"
                        else:
                            return base_command
        
        # If no pattern matches, return None
        return None
    
    def is_command_safe(self, command: str) -> bool:
        """
        Check if a command is safe to execute by comparing against dangerous commands.
        
        Args:
            command (str): Command to check
            
        Returns:
            bool: True if command is safe, False otherwise
        """
        command_lower = command.lower().strip()
        
        # Check against dangerous command patterns
        for dangerous_cmd in self.dangerous_commands:
            if dangerous_cmd.lower() in command_lower:
                return False
        
        # Additional safety checks
        dangerous_keywords = [
            'format', 'fdisk', 'mkfs', 'dd if=', 'rm -rf /',
            'del /q /s', '>nul', '/dev/null', 'shutdown', 'reboot'
        ]
        
        for keyword in dangerous_keywords:
            if keyword.lower() in command_lower:
                return False
        
        return True
    
    def execute_command(self, command: str) -> Dict[str, any]:
        """
        Execute a system command safely using subprocess.
        
        Args:
            command (str): Command to execute
            
        Returns:
            Dict: Dictionary containing success status, output, and error information
        """
        try:
            # Check if command is safe before execution
            if not self.is_command_safe(command):
                return {
                    'success': False,
                    'output': '',
                    'error': f'Command blocked for security reasons: {command}',
                    'command': command
                }
            
            # Use shell=True for Windows compatibility with built-in commands
            # Set timeout to prevent hanging processes
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=os.getcwd()
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip() if result.stdout else '',
                'error': result.stderr.strip() if result.stderr else '',
                'command': command,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Command timed out after 30 seconds: {command}',
                'command': command
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'output': e.stdout.strip() if e.stdout else '',
                'error': f'Command failed with return code {e.returncode}: {e.stderr.strip() if e.stderr else ""}',
                'command': command
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'Unexpected error executing command: {str(e)}',
                'command': command
            }
    
    def display_result(self, result: Dict[str, any]) -> None:
        """
        Display the result of a command execution in a user-friendly format.
        
        Args:
            result (Dict): Result dictionary from execute_command
        """
        print(f"\n{'='*50}")
        print(f"🔧 EXECUTED COMMAND: {result['command']}")
        print(f"{'='*50}")
        
        if result['success']:
            print("Status: SUCCESS")
            if result['output']:
                print(f"Output:")
                print(f"{result['output']}")
            else:
                print("Output: (no output)")
        else:
            print("Status: FAILED")
            if result['error']:
                print(f"Error: {result['error']}")
        
        print("=" * 50)
    
    def run_interactive_mode(self, voice: bool = False) -> None:
        """
        Run AiNux in interactive mode, continuously accepting user input
        until the user chooses to exit.
        """
        print("\nAiNux is ready! Enter natural language commands.")
        print("Examples:")
        print("  - 'List all files in the current directory'")
        print("  - 'Show current working directory'")
        print("  - 'Show running processes'")
        print("  - 'Create directory myproject'")
        print("\n")
        
        while True:
            try:
                # Get user input (voice or text)
                if voice:
                    try:
                        from voice_input import listen_for_command, VoiceInputError
                        print("🎤 Listening... (say a command, or say 'exit' to quit)")
                        heard = listen_for_command(timeout=6, phrase_time_limit=8, language="en-US")
                        user_input = (heard or "").strip()
                        if user_input:
                            print(f"You said: {user_input}")
                    except ImportError:
                        print("Voice mode requires SpeechRecognition. Falling back to text input.")
                        voice = False
                        user_input = input("AiNux> ").strip()
                    except VoiceInputError as e:
                        print(f"Voice error: {e}")
                        user_input = input("AiNux> ").strip()
                    except Exception as e:
                        print(f"Voice capture failed: {e}")
                        user_input = input("AiNux> ").strip()
                else:
                    user_input = input("AiNux> ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                    print("Goodbye! Thanks for using AiNux.")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Show help if requested
                if user_input.lower() in ['help', 'h', '?']:
                    self.show_help()
                    continue
                
                # Parse natural language input to command
                command = self.parse_natural_language(user_input)
                
                if command is None:
                    print(f"Sorry, I don't understand: '{user_input}'")
                    print("Type 'help' for examples of supported commands.")
                    continue
                
                # Show the generated command to the user
                print(f"💡 Generated command: {command}")
                
                # Execute the command
                result = self.execute_command(command)
                
                # Display the result
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\nUnexpected error: {str(e)}")
                print("Please try again or type 'exit' to quit.")
    
    def show_help(self) -> None:
        """Display help information with example commands."""
        print("\n" + "=" * 60)
        print("AiNux Help - Natural Language Command Examples")
        print("=" * 60)
        print("File Operations:")
        print("  • 'List files here' or 'Show files in current directory'")
        print("  • 'Show current directory' or 'Where am I?'")
        print("  • 'Create directory myproject'")
        print("")
        print("System Information:")
        print("  • 'Show running processes'")
        print("  • 'Show network info'")
        print("  • 'Show system info'")
        print("  • 'Show disk usage'")
        print("")
        print("Navigation:")
        print("  • 'Change directory to Documents'")
        print("  • 'Go to directory myproject'")
        print("")
        print("Other Commands:")
        print("  • 'help' or 'h' or '?' - Show this help")
        print("  • 'exit' or 'quit' or 'q' - Exit AiNux")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        # CLI args
        parser = argparse.ArgumentParser(description="AiNux - Natural Language to System Command Executor")
        parser.add_argument("--voice", action="store_true", help="Enable microphone voice input")
        args = parser.parse_args()

        # Initialize AiNux
        ainux = AiNux()
        print("AiNux Natural Language Command Executor initialized!")
        print(f"Running on: {platform.system()}")
        print("Type 'exit' or 'quit' to stop the program.")
        print("-" * 50)

        # Start interactive mode
        ainux.run_interactive_mode(voice=args.voice)
        
    except Exception as e:
        print(f"Fatal error initializing AiNux: {str(e)}")
        sys.exit(1)