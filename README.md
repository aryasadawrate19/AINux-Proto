# AiNux: Natural Language to System Command Executor

AiNux is a Python prototype that converts natural language input into system commands and executes them safely. It provides an intuitive interface for users to interact with their operating system using plain English instead of remembering complex command syntax.

## Features

- **Natural Language Processing**: Converts human-readable input into system commands
- **Cross-Platform Support**: Works on Windows, Linux, and macOS
- **Security Features**: Blocks dangerous commands to prevent system damage
- **Error Handling**: Comprehensive error handling with informative messages
- **Interactive Mode**: Continuous command execution until user exits
- **Timeout Protection**: Commands timeout after 30 seconds to prevent hanging

## Requirements

- Python 3.6 or higher
- Core CLI uses only standard library
- Optional voice input requires: SpeechRecognition and PyAudio (Windows tips below)

## Installation

1. Clone or download the `ainux.py` file
2. Ensure you have Python 3.6+ installed
3. No additional installation required - uses only standard library

## Usage

### Running AiNux

```bash
python ainux.py
```
To enable voice input (microphone):

```bash
python ainux.py --voice
```

### Voice Input (Optional)

You can speak commands using your microphone:

```bash
python ainux.py --voice
```

Dependencies for voice input:

- SpeechRecognition
- PyAudio (for microphone access)

Windows installation tips:

```bash
pip install SpeechRecognition
pip install pyaudio
# If PyAudio fails to build:
pip install pipwin
pipwin install pyaudio
```

Speak examples like: "List all files here", "Show current directory", or "Create directory test".


### Example Commands

Once running, you can enter natural language commands such as:

- **"List all files in the current directory"** → `dir` (Windows) or `ls -la` (Linux/Mac)
- **"Show current working directory"** → `cd` (Windows) or `pwd` (Linux/Mac)
- **"Create directory myproject"** → `mkdir myproject`
- **"Show running processes"** → `tasklist` (Windows) or `ps aux` (Linux/Mac)
- **"Show network info"** → `ipconfig` (Windows) or `ifconfig` (Linux/Mac)

### Commands

- **help**, **h**, **?** - Show help with examples
- **exit**, **quit**, **q**, **bye** - Exit the program
- **Ctrl+C** - Force quit

## Architecture

### Main Components

1. **AiNux Class**: Main class that handles all functionality
2. **Natural Language Parser**: Converts user input using regex patterns
3. **Command Executor**: Safely executes commands using subprocess
4. **Security Module**: Blocks dangerous commands
5. **Interactive Loop**: Handles user interaction

### Security Features

AiNux includes several security measures:

- **Dangerous Command Blacklist**: Prevents execution of harmful commands like `rm -rf /`, `format`, etc.
- **Command Validation**: Additional checks for dangerous keywords
- **Timeout Protection**: Commands automatically timeout after 30 seconds
- **Sandboxed Execution**: Uses subprocess with controlled environment

### Supported Command Categories

- **File Operations**: List, create, navigate directories
- **System Information**: Processes, network, disk usage
- **Navigation**: Change directories
- **Platform-Specific**: Automatically uses correct commands for your OS

## Customization

### Adding New Commands

To add new natural language patterns, modify the `patterns` dictionary in the `parse_natural_language()` method:

```python
patterns = {
    'your_command_type': [
        r'pattern1',
        r'pattern2',
    ]
}
```

Then add the corresponding system command in `_load_command_mappings()`:

```python
'windows': {
    'your_command_type': 'windows_command',
},
'linux': {
    'your_command_type': 'linux_command',
}
```

### Adding Security Rules

Modify the `_load_dangerous_commands()` method to add more dangerous command patterns.

## Limitations

- **Limited NLP**: Uses regex pattern matching, not advanced NLP
- **Command Coverage**: Limited set of supported commands
- **Context Awareness**: No memory of previous commands
- **Complex Commands**: Cannot handle complex piped or chained commands

## Future Improvements

- Integration with advanced NLP libraries (spaCy, NLTK)
- Machine learning for better command recognition
- Command history and context awareness
- Support for complex command chaining
- GUI interface
- Voice command support

## Error Handling

AiNux handles various error conditions:

- **Unrecognized Commands**: Provides helpful suggestions
- **Command Failures**: Shows detailed error messages
- **Timeouts**: Prevents hanging processes
- **Security Violations**: Blocks dangerous commands with explanations
- **System Errors**: Graceful error recovery

## Contributing

This is a prototype designed for educational purposes. To contribute:

1. Fork the repository
2. Add new features or improvements
3. Test thoroughly across different platforms
4. Submit pull requests with clear descriptions

## License

This project is provided as-is for educational purposes. Feel free to use, modify, and distribute.

## Disclaimer

**Important**: While AiNux includes security measures, always be cautious when running system commands. Test in a safe environment first, and never run commands you don't understand. The authors are not responsible for any system damage.

---

**Author**: AI Assistant  
**Date**: September 15, 2025  
**Version**: 1.0.0 (Prototype)