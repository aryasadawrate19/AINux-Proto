#!/usr/bin/env python3

import subprocess
import sys
import os
import re
import platform
import json
import time
from typing import Optional, Dict, List, Union
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class GeminiConfig:
    """Configuration for Gemini LLM integration"""
    api_key: str = os.getenv('GEMINI_API_KEY', '')
    model: str = "gemini-2.5-flash"  # Updated to current available model
    timeout: int = 30
    temperature: float = 0.2
    max_retries: int = 2
    max_output_tokens: int = 100  


class GeminiLLM:
    """
    Handles communication with Google Gemini API for intelligent natural language processing
    """
    
    def __init__(self, config: GeminiConfig):
        """Initialize Gemini LLM client with configuration"""
        self.config = config
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """
        Check if Gemini API key is available and valid
        
        Returns:
            bool: True if Gemini API is available
        """
        try:
            if not self.config.api_key:
                print("ERROR: No GEMINI_API_KEY found in .env file")
                return False
            
            # Configure Gemini
            genai.configure(api_key=self.config.api_key)
            
            # Test the connection by listing models
            models = genai.list_models()
            available_models = [model.name for model in models]
            
            # Check if our target model is available
            target_model = f"models/{self.config.model}"
            if target_model in available_models:
                print(f"SUCCESS: Gemini API connected successfully with model: {self.config.model}")
                return True
            else:
                print(f"WARNING: Model '{self.config.model}' not found. Using default.")
                return True
                
        except Exception as e:
            print(f"ERROR: Gemini API not available: {str(e)}")
            return False
    
    def generate_command(self, user_input: str, platform: str) -> Optional[str]:
        """
        Use Gemini LLM to convert natural language to system command
        
        Args:
            user_input (str): Natural language input from user
            platform (str): Current operating system platform
            
        Returns:
            Optional[str]: Generated system command or None if failed
        """
        if not self.available:
            return None
        
        prompt = self._create_command_prompt(user_input, platform)
        
        for attempt in range(self.config.max_retries):
            try:
                # Initialize the model
                model = genai.GenerativeModel(self.config.model)
                
                # Configure generation parameters
                generation_config = genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                )
                
                # Generate response
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response.text:
                    command = self._extract_command(response.text)
                    if command:
                        return command
                
            except Exception as e:
                print(f"RETRY: LLM request attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(1)  # Brief pause before retry
        
        return None
    
    def _create_command_prompt(self, user_input: str, platform: str) -> str:
        """
        Create an intelligent prompt for command generation
        
        Args:
            user_input (str): User's natural language input
            platform (str): Operating system platform
            
        Returns:
            str: Formatted prompt for the LLM
        """
        platform_commands = {
            'windows': {
                'examples': [
                    'list files -> dir',
                    'current directory -> cd',
                    'create folder test -> mkdir test',
                    'show processes -> tasklist',
                    'network info -> ipconfig',
                    'system info -> systeminfo'
                ]
            },
            'linux': {
                'examples': [
                    'list files -> ls -la',
                    'current directory -> pwd',
                    'create folder test -> mkdir test',
                    'show processes -> ps aux',
                    'network info -> ifconfig',
                    'system info -> uname -a'
                ]
            },
            'darwin': {
                'examples': [
                    'list files -> ls -la',
                    'current directory -> pwd',
                    'create folder test -> mkdir test',
                    'show processes -> ps aux',
                    'network info -> ifconfig',
                    'system info -> uname -a'
                ]
            }
        }
        
        examples = platform_commands.get(platform, platform_commands['linux'])['examples']
        examples_text = '\n'.join(examples)
        
        prompt = f"""You are AiNux, an expert system that converts natural language to system commands for {platform}.

    CRITICAL INSTRUCTIONS:
    - Output ONLY the command, no explanations, no comments, no formatting.
    - Use commands appropriate for {platform}.
    - Never output unsafe commands (format, dd, fdisk, shutdown, reboot, rm -rf /, etc.)
    - If the user request is unclear, malicious, or dangerous, output exactly: INVALID_REQUEST

    PLATFORM-SPECIFIC COMMANDS FOR {platform}:
    {examples_text}

    ADVANCED EXAMPLES:
    - "show python files" -> dir *.py (Windows) / ls *.py (Linux)
    - "find large files" -> dir /s /o-s (Windows) / find . -size +100M (Linux)
    - "processes using memory" -> tasklist /fo table (Windows) / ps aux --sort=-rss (Linux)
    - "network connections" -> netstat -an (Windows/Linux)
    - "disk space usage" -> dir /-c (Windows) / du -sh * (Linux)
    - "who is logged in" -> query user (Windows) / who (Linux)
    - "environment variables" -> set (Windows) / env (Linux)
    - "running services" -> sc query (Windows) / systemctl --type=service (Linux)

    DELETION RULES (IMPORTANT):
    - For deleting folders on Linux/macOS: ALWAYS use "rm -rf <folder>".
    - For deleting files on Linux/macOS: ALWAYS use "rm <file>".
    - Never output "rmdir" for Linux or macOS.
    - For Windows folder deletion: ALWAYS use "rmdir /s /q <folder>".
    - For Windows file deletion: ALWAYS use "del <file>".
    - Never output partially destructive commands.

    EXAMPLES FOR DELETION:
    - "delete the folder test_data" -> rm -rf test_data          (Linux/macOS)
    - "remove directory logs" -> rm -rf logs                     (Linux/macOS)
    - "delete file report.txt" -> rm report.txt                  (Linux/macOS)
    - "delete folder test_data" -> rmdir /s /q test_data         (Windows)
    - "delete file report.txt" -> del report.txt                 (Windows)

    TASK: Convert this natural language to a {platform} command:
    "{user_input}"

    COMMAND:"""

        return prompt
    
    def _extract_command(self, llm_response: str) -> Optional[str]:
        """
        Extract and validate command from LLM response
        
        Args:
            llm_response (str): Raw response from LLM
            
        Returns:
            Optional[str]: Cleaned command or None if invalid
        """
        if not llm_response:
            return None
        
        # Clean the response
        command = llm_response.strip()
        
        # Remove common prefixes and suffixes
        prefixes_to_remove = ['command:', 'output:', '>', '$', '#']
        for prefix in prefixes_to_remove:
            if command.lower().startswith(prefix):
                command = command[len(prefix):].strip()
        
        # Check for invalid responses
        invalid_responses = ['invalid_request', 'invalid request', 'error', 'unknown']
        if command.lower() in invalid_responses:
            return None
        
        # Basic validation - command should not be empty or too long
        if not command or len(command) > 200:
            return None
        
        # Remove quotes if present
        if command.startswith('"') and command.endswith('"'):
            command = command[1:-1]
        if command.startswith("'") and command.endswith("'"):
            command = command[1:-1]
        
        return command


class AiNuxLLM:
    """
    AiNux LLM Enhanced - Natural Language to System Command Executor with Gemini Integration
    
    This class combines traditional regex-based parsing with intelligent LLM processing
    for superior natural language understanding and command generation.
    """
    
    def __init__(self, use_llm: bool = True, gemini_config: Optional[GeminiConfig] = None):
        """Initialize AiNux with LLM capabilities"""
        self.platform = platform.system().lower()
        self.dangerous_commands = self._load_dangerous_commands()
        self.command_mappings = self._load_command_mappings()
        
        # LLM Configuration
        self.use_llm = use_llm
        self.gemini_config = gemini_config or GeminiConfig()
        self.llm = GeminiLLM(self.gemini_config) if use_llm else None
        
        # Display initialization info
        if self.use_llm:
            if self.llm and self.llm.available:
                print(f"LLM Mode: Enabled (Model: {self.gemini_config.model})")
            else:
                print("WARNING: LLM Mode: Requested but Gemini unavailable, using regex fallback")
                self.use_llm = False
        else:
            print("LLM Mode: Disabled, using regex patterns")
    
    def _load_dangerous_commands(self) -> List[str]:
        """
        Load a comprehensive list of dangerous commands that should not be executed.
        
        Returns:
            List[str]: List of dangerous command patterns
        """
        return [
            'rm -rf /',
            'rm -rf *',
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
            ':(){:|:&};:',  # Fork bomb
            'wget',  # Can be used maliciously
            'curl',  # Can be used maliciously
            'chmod 777',
            'chown -R',
            'rm -f /boot',
            'mv /home',
        ]
    
    def _load_command_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Load command mappings for different platforms.
        This serves as fallback when LLM is not available.
        
        Returns:
            Dict: Command mappings organized by platform
        """
        return {
            'windows': {
                'list_files': 'dir',
                'list_python_files': 'dir *.py',
                'list_specific_files': 'dir *.',
                'current_directory': 'cd',
                'change_directory': 'cd',
                'create_directory': 'mkdir',
                'remove_file': 'del',
                'copy_file': 'copy',
                'move_file': 'move',
                'show_processes': 'tasklist',
                'show_specific_processes': 'tasklist /fi "imagename eq',
                'network_info': 'ipconfig',
                'network_connections': 'netstat -an',
                'system_info': 'systeminfo',
                'disk_usage': 'dir /-c',
                'environment_vars': 'set',
                'logged_users': 'query user',
                'large_files': 'dir /s /o-s',
                'recent_files': 'forfiles /m *.* /c "cmd /c echo @path @fdate"',
                'file_count': 'dir /b | find /c /v ""',
                'memory_usage': 'systeminfo | findstr "Available Physical Memory"'
            },
            'linux': {
                'list_files': 'ls -la',
                'list_python_files': 'ls -la *.py',
                'list_specific_files': 'ls -la *.',
                'current_directory': 'pwd',
                'change_directory': 'cd',
                'create_directory': 'mkdir',
                'remove_file': 'rm',
                'copy_file': 'cp',
                'move_file': 'mv',
                'show_processes': 'ps aux',
                'show_specific_processes': 'ps aux | grep',
                'network_info': 'ifconfig',
                'network_connections': 'netstat -tuln',
                'system_info': 'uname -a',
                'disk_usage': 'df -h',
                'environment_vars': 'env',
                'logged_users': 'who',
                'large_files': 'find . -size +100M -ls',
                'recent_files': 'find . -mtime -1 -ls',
                'file_count': 'ls -1 | wc -l',
                'memory_usage': 'free -h'
            },
            'darwin': {  # macOS
                'list_files': 'ls -la',
                'list_python_files': 'ls -la *.py',
                'list_specific_files': 'ls -la *.',
                'current_directory': 'pwd',
                'change_directory': 'cd',
                'create_directory': 'mkdir',
                'remove_file': 'rm',
                'copy_file': 'cp',
                'move_file': 'mv',
                'show_processes': 'ps aux',
                'show_specific_processes': 'ps aux | grep',
                'network_info': 'ifconfig',
                'network_connections': 'netstat -tuln',
                'system_info': 'uname -a',
                'disk_usage': 'df -h',
                'environment_vars': 'env',
                'logged_users': 'who',
                'large_files': 'find . -size +100M -ls',
                'recent_files': 'find . -mtime -1 -ls',
                'file_count': 'ls -1 | wc -l',
                'memory_usage': 'vm_stat'
            }
        }
    
    def parse_natural_language(self, user_input: str) -> Optional[str]:
        """
        Convert natural language input into a system command using LLM or regex fallback.
        
        Args:
            user_input (str): Natural language input from user
            
        Returns:
            Optional[str]: System command or None if not recognized
        """
        # First try LLM if available
        if self.use_llm and self.llm and self.llm.available:
            print(f"Trying LLM processing...")
            command = self.llm.generate_command(user_input, self.platform)
            if command and self.is_command_safe(command):
                print(f"SUCCESS: LLM generated safe command: {command}")
                return command
            elif command:
                print(f"BLOCKED: LLM generated unsafe command: {command}")
            else:
                print(f"FAILED: LLM could not process: '{user_input}'")
        
        # Fallback to regex-based parsing
        print(f"Falling back to enhanced regex parsing...")
        result = self._parse_with_regex(user_input)
        if result:
            print(f"SUCCESS: Regex found match: {result}")
        else:
            print(f"FAILED: No regex pattern matched")
        return result
    
    def _parse_with_regex(self, user_input: str) -> Optional[str]:
        """
        Fallback regex-based parsing (original AiNux functionality)
        
        Args:
            user_input (str): Natural language input from user
            
        Returns:
            Optional[str]: System command or None if not recognized
        """
        # Convert input to lowercase for easier matching
        input_lower = user_input.lower().strip()
        
        # Define comprehensive natural language patterns and their corresponding command types
        patterns = {
            'list_files': [
                r'list.*files?.*current.*director',
                r'show.*files?.*current.*director',
                r'list.*files?.*here',
                r'show.*files?.*here',
                r'list.*director.*content',
                r'what.*files?.*here',
                r'dir',
                r'ls',
                r'show.*all.*files?',
                r'display.*files?',
                r'files?.*in.*this',
                r'contents?.*of.*this',
                r'what.*is.*in.*this'
            ],
            'list_python_files': [
                r'python.*files?',
                r'\.py.*files?',
                r'show.*python',
                r'list.*python',
                r'find.*python.*files?',
                r'all.*\.py'
            ],
            'list_specific_files': [
                r'show.*(\w+).*files?',
                r'list.*(\w+).*files?',
                r'find.*(\w+).*files?',
                r'all.*\.(\w+).*files?'
            ],
            'current_directory': [
                r'show.*current.*director',
                r'what.*current.*director',
                r'where.*am.*i',
                r'current.*path',
                r'working.*director',
                r'pwd',
                r'current.*location',
                r'what.*director.*am.*i',
                r'my.*location',
                r'present.*working'
            ],
            'change_directory': [
                r'change.*director.*to\s+(\S+)',
                r'go.*to.*director.*(\S+)',
                r'cd\s+(\S+)',
                r'navigate.*to\s+(\S+)',
                r'move.*to.*director.*(\S+)',
                r'switch.*to.*(\S+)'
            ],
            'create_directory': [
                r'create.*director.*(\S+)',
                r'make.*director.*(\S+)',
                r'mkdir\s+(\S+)',
                r'new.*folder.*(\S+)',
                r'create.*folder.*(\S+)',
                r'make.*folder.*(\S+)',
                r'add.*director.*(\S+)'
            ],
            'show_processes': [
                r'show.*process',
                r'list.*process',
                r'running.*process',
                r'task.*list',
                r'ps',
                r'what.*process.*running',
                r'active.*process',
                r'current.*process',
                r'process.*list',
                r'tasks?.*running'
            ],
            'show_specific_processes': [
                r'process.*contain.*(\w+)',
                r'find.*process.*(\w+)',
                r'(\w+).*process',
                r'running.*(\w+)',
                r'tasks?.*with.*(\w+)'
            ],
            'network_info': [
                r'show.*network.*info',
                r'network.*config',
                r'ip.*config',
                r'network.*settings',
                r'network.*details',
                r'my.*ip',
                r'network.*address',
                r'connection.*info'
            ],
            'network_connections': [
                r'network.*connection',
                r'active.*connection',
                r'open.*connection',
                r'established.*connection',
                r'netstat',
                r'who.*connected'
            ],
            'system_info': [
                r'system.*info',
                r'show.*system.*info',
                r'computer.*info',
                r'machine.*info',
                r'system.*details',
                r'hardware.*info',
                r'system.*specification'
            ],
            'disk_usage': [
                r'disk.*usage',
                r'disk.*space',
                r'storage.*info',
                r'free.*space',
                r'available.*space',
                r'how.*much.*space',
                r'disk.*size',
                r'storage.*usage'
            ],
            'environment_vars': [
                r'environment.*variable',
                r'env.*var',
                r'system.*variable',
                r'path.*variable',
                r'show.*env'
            ],
            'logged_users': [
                r'who.*logged.*in',
                r'current.*user',
                r'logged.*user',
                r'active.*user',
                r'who.*online'
            ],
            'large_files': [
                r'large.*files?',
                r'big.*files?',
                r'huge.*files?',
                r'files?.*large',
                r'biggest.*files?'
            ],
            'recent_files': [
                r'recent.*files?',
                r'modified.*files?',
                r'new.*files?',
                r'latest.*files?',
                r'files?.*modified',
                r'changed.*files?'
            ],
            'file_count': [
                r'how.*many.*files?',
                r'count.*files?',
                r'number.*of.*files?',
                r'files?.*count'
            ],
            'memory_usage': [
                r'memory.*usage',
                r'ram.*usage',
                r'memory.*info',
                r'free.*memory',
                r'available.*memory'
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
                        elif command_type == 'list_specific_files' and match.groups():
                            extension = match.group(1)
                            if self.platform == 'windows':
                                return f"dir *.{extension}"
                            else:
                                return f"ls -la *.{extension}"
                        elif command_type == 'show_specific_processes' and match.groups():
                            process_name = match.group(1)
                            if self.platform == 'windows':
                                return f'tasklist /fi "imagename eq {process_name}*"'
                            else:
                                return f"ps aux | grep {process_name}"
                        else:
                            return base_command
        
        # Advanced pattern matching for more complex queries
        advanced_patterns = {
            # File-related patterns
            r'find.*files?.*larger.*than.*(\d+)': lambda m: self._get_large_files_command(m.group(1)),
            r'show.*files?.*modified.*today': lambda m: self._get_recent_files_command('today'),
            r'files?.*modified.*last.*(\d+).*days?': lambda m: self._get_recent_files_command(m.group(1)),
            r'count.*files?.*in.*current': lambda m: self._get_file_count_command(),
            r'size.*of.*all.*files?': lambda m: self._get_total_size_command(),
            
            # Process-related patterns
            r'kill.*process.*(\w+)': lambda m: self._get_kill_process_command(m.group(1)),
            r'memory.*used.*by.*(\w+)': lambda m: self._get_process_memory_command(m.group(1)),
            
            # System patterns
            r'free.*space.*on.*(\w+)': lambda m: self._get_disk_space_command(m.group(1)),
            r'temperature|thermal': lambda m: self._get_temperature_command(),
            r'uptime|how.*long.*running': lambda m: self._get_uptime_command(),
        }
        
        for pattern, command_func in advanced_patterns.items():
            match = re.search(pattern, input_lower)
            if match:
                try:
                    return command_func(match)
                except:
                    continue
        
        # If no pattern matches, return None
        return None
    
    def _get_large_files_command(self, size_mb: str) -> str:
        """Generate command to find large files"""
        if self.platform == 'windows':
            return f'forfiles /s /c "cmd /c if @fsize geq {int(size_mb)*1024*1024} echo @path @fsize"'
        else:
            return f'find . -size +{size_mb}M -ls'
    
    def _get_recent_files_command(self, timeframe: str) -> str:
        """Generate command to find recently modified files"""
        if self.platform == 'windows':
            if timeframe == 'today':
                return 'forfiles /m *.* /c "cmd /c echo @path @fdate @ftime"'
            else:
                return f'forfiles /m *.* /d -{timeframe} /c "cmd /c echo @path @fdate"'
        else:
            if timeframe == 'today':
                return 'find . -newermt "$(date +%Y-%m-%d)" -ls'
            else:
                return f'find . -mtime -{timeframe} -ls'
    
    def _get_file_count_command(self) -> str:
        """Generate command to count files"""
        if self.platform == 'windows':
            return 'dir /b | find /c /v ""'
        else:
            return 'ls -1 | wc -l'
    
    def _get_total_size_command(self) -> str:
        """Generate command to get total size of files"""
        if self.platform == 'windows':
            return 'dir /s'
        else:
            return 'du -sh .'
    
    def _get_kill_process_command(self, process_name: str) -> str:
        """Generate command to kill a process (but return safe alternative)"""
        # Instead of actually killing, just show the process
        if self.platform == 'windows':
            return f'tasklist /fi "imagename eq {process_name}*"'
        else:
            return f'ps aux | grep {process_name}'
    
    def _get_process_memory_command(self, process_name: str) -> str:
        """Generate command to show process memory usage"""
        if self.platform == 'windows':
            return f'tasklist /fi "imagename eq {process_name}*" /fo table'
        else:
            return f'ps aux | grep {process_name} | awk \'{{print $4" "$11}}\''
    
    def _get_disk_space_command(self, drive: str) -> str:
        """Generate command to show disk space for specific drive"""
        if self.platform == 'windows':
            return f'dir {drive}:\\ /-c'
        else:
            return f'df -h /{drive} 2>/dev/null || df -h'
    
    def _get_temperature_command(self) -> str:
        """Generate command to show system temperature"""
        if self.platform == 'windows':
            return 'wmic /namespace:\\\\root\\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature'
        else:
            return 'sensors 2>/dev/null || cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null || echo "Temperature sensors not available"'
    
    def _get_uptime_command(self) -> str:
        """Generate command to show system uptime"""
        if self.platform == 'windows':
            return 'systeminfo | findstr "System Boot Time"'
        else:
            return 'uptime'
    
    def is_command_safe(self, command: str) -> Union[bool, str]:
        """
        Check if a command is safe, confirmable, or forbidden.

        Returns:
            True  -> fully safe
            "confirm" -> dangerous but allowed with confirmation
            False -> absolutely forbidden
        """

        command_lower = command.lower().strip()

        # Absolutely forbidden commands (no confirmation allowed)
        forbidden_patterns = [
            r'rm\s+-rf\s+/',                     # rm -rf /
            r'format(\s|$)',                     # format disk
            r'fdisk',                            # partitioning
            r'dd\s+if=',                         # raw disk writes
            r':\(\)\s*\{\s*:|:&\}\s*;\s*:',    # fork bomb
            r'shutdown(\s|$)',
            r'reboot(\s|$)',
            r'poweroff(\s|$)',
            r'init\s+[06]',
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, command_lower):
                return False

        # Dangerous but confirmable commands (Linux + Windows)
        confirmable_patterns = [
            r'rm\s+-rf\s+.+',            # rm -rf <folder>
            r'rm\s+.+',                  # rm <file>
            r'del\s+.+',                 # del file.ext
            r'rmdir\s+/s\s+/q\s+.+',   # WINDOWS delete folder
            r'rmdir\s+.+',               # any rmdir is dangerous
            r'mv\s+.+',                  # move operations
            r'chmod\s+7[0-7][0-7]',      # chmod 7xx
            r'chown\s+-r\s+.+',
        ]

        for pattern in confirmable_patterns:
            if re.search(pattern, command_lower):
                return "confirm"

        # Everything else is safe
        return True
    
    def execute_command(self, command: str) -> Dict[str, any]:
        """
        Execute a system command safely, with confirmation for dangerous commands.
        """

        safety = self.is_command_safe(command)

        # Fully forbidden
        if safety is False:
            return {
                'success': False,
                'output': '',
                'error': f'Command blocked for security reasons: {command}',
                'command': command
            }

        # Dangerous but confirmable
        if safety == "confirm":
            print(f"\nWARNING: This command may delete or modify important files:\n  {command}")
            print("If you're absolutely certain, type YES.")
            confirm = input("Confirm (YES to run): ").strip()

            if confirm.upper() != "YES":
                return {
                    'success': False,
                    'output': '',
                    'error': f'Execution cancelled by user: {command}',
                    'command': command
                }

        # Safe or confirmed — run it
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
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
        print(f"EXECUTED COMMAND: {result['command']}")
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
        Run AiNux in interactive mode with optional voice input.
        """

        mode_str = "LLM Enhanced" if (self.use_llm and self.llm and self.llm.available) else "Regex Fallback"
        print(f"\n{mode_str} AiNux is ready! Enter natural language commands.")
        print("(Say 'exit' or 'quit' to stop if in voice mode.)\n")

        # Try importing voice system early
        voice_available = False
        if voice:
            try:
                from voice_input import listen_for_command, VoiceInputError
                voice_available = True
                print("Voice mode enabled. Listening for commands...")
            except Exception as e:
                print(f"Voice mode failed to initialize: {e}")
                voice = False

        while True:
            try:
                # Voice input mode
                if voice and voice_available:
                    from voice_input import listen_for_command
                    print("🎤 Listening...")
                    heard = listen_for_command(timeout=6, phrase_time_limit=8, language="en-US")
                    user_input = (heard or "").strip()

                    if not user_input:
                        continue

                    print(f"You said: {user_input}")

                # Text input mode
                else:
                    user_input = input("AiNux> ").strip()

                # Exit commands
                if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                    print("Goodbye! Thanks for using AiNux.")
                    break

                if not user_input:
                    continue

                # Help commands
                if user_input.lower() in ['help', 'h', '?']:
                    self.show_help()
                    continue

                if user_input.lower() in ['mode', 'info', 'status']:
                    self.show_mode_info()
                    continue

                # Process natural language
                print("Processing natural language input...")
                command = self.parse_natural_language(user_input)

                if command is None:
                    print(f"Sorry, I don't understand: '{user_input}'")
                    print("Type 'help' for supported commands.")
                    continue

                parsing_mode = "LLM" if (self.use_llm and self.llm and self.llm.available) else "Regex"
                print(f"Generated command ({parsing_mode}): {command}")

                # Execute it
                result = self.execute_command(command)

                # Display result
                self.display_result(result)

            except KeyboardInterrupt:
                print("\nInterrupted by user. Exiting.")
                break

            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
    
    def show_help(self) -> None:
        """Display comprehensive help information."""
        print("\n" + "=" * 70)
        print("AiNux LLM Enhanced Help - Natural Language Command Examples")
        print("=" * 70)
        
        mode_str = "LLM Enhanced" if (self.use_llm and self.llm and self.llm.available) else "Regex Fallback"
        print(f"Current Mode: {mode_str}")
        
        print("\nEnhanced Commands (LLM Mode):")
        print("  • 'Show me all Python files in this directory'")
        print("  • 'Find running processes containing chrome or firefox'")
        print("  • 'Create a backup folder called backup_2025'")
        print("  • 'What files were modified in the last hour?'")
        print("  • 'Display detailed network configuration'")
        print("  • 'Show me the size of all directories here'")
        
        print("\nFile Operations:")
        print("  • 'List files here' or 'Show files in current directory'")
        print("  • 'Show current directory' or 'Where am I?'")
        print("  • 'Create directory myproject'")
        
        print("\nSystem Information:")
        print("  • 'Show running processes'")
        print("  • 'Show network info'")
        print("  • 'Show system info'")
        print("  • 'Show disk usage'")
        
        print("\nNavigation:")
        print("  • 'Change directory to Documents'")
        print("  • 'Go to directory myproject'")
        
        print("\nOther Commands:")
        print("  • 'help' or 'h' or '?' - Show this help")
        print("  • 'mode' or 'info' - Show current parsing mode")
        print("  • 'exit' or 'quit' or 'q' - Exit AiNux")
        
        print("\nSecurity:")
        print("  • All commands are checked for safety before execution")
        print("  • Dangerous commands are automatically blocked")
        print("  • Commands timeout after 30 seconds")
        
        print("=" * 70 + "\n")
    
    def show_mode_info(self) -> None:
        """Display current mode and configuration information."""
        print("\n" + "📊 AiNux Mode Information")
        print("-" * 30)
        
        if self.use_llm and self.llm and self.llm.available:
            print("Mode: LLM Enhanced")
            print(f"Model: {self.gemini_config.model}")
            print(f"API: Google Gemini")
            print(f" Temperature: {self.gemini_config.temperature}")
            print("Capabilities: Advanced natural language understanding")
        else:
            print("Mode: Regex Fallback")
            print("Parser: Pattern matching")
            print("Note: Add GEMINI_API_KEY to .env file for enhanced LLM mode")
        
        print(f"Platform: {platform.system()}")
        print(f"Security: Active (dangerous commands blocked)")
        print("-" * 30 + "\n")


if __name__ == "__main__":
    try:
        import argparse
        
        parser = argparse.ArgumentParser(description="AiNux LLM Enhanced Shell")
        parser.add_argument("--voice", action="store_true", help="Enable microphone voice input")
        args = parser.parse_args()

        ainux = AiNuxLLM(use_llm=True)
        print("AiNux LLM Enhanced Natural Language Command Executor initialized!")
        print(f"Running on: {platform.system()}")
        print("Type 'exit' or 'quit' to stop the program.")
        print("-" * 60)

        # Start interactive mode (voice-enabled)
        ainux.run_interactive_mode(voice=args.voice)

    except Exception as e:
        print(f"Fatal error initializing AiNux: {str(e)}")
        sys.exit(1)
