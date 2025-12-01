# AiNux: Natural Language to System Command Executor (Gemini Enhanced)

AiNux is an advanced Python prototype that converts natural language input into system commands and executes them safely. **Version 2.0** now includes **Google Gemini API integration** for superior natural language understanding, with intelligent fallback to regex patterns.

## 🆕 What's New in Version 2.0

- **🤖 Google Gemini Integration**: Uses Google's powerful Gemini API for sophisticated natural language processing
- **🧠 Intelligent Parsing**: Better understanding of complex and varied language inputs
- **🔄 Smart Fallback**: Automatically falls back to regex patterns if Gemini API is unavailable
- **⚡ Enhanced Performance**: Cloud-based AI for faster, more accurate command generation
- **🛡️ Advanced Security**: Enhanced safety checks for AI-generated commands

## Features

### Core Features
- **Natural Language Processing**: Converts human-readable input into system commands
- **Cross-Platform Support**: Works on Windows, Linux, and macOS
- **Dual Parsing Modes**: LLM-enhanced + Regex fallback
- **Security Features**: Blocks dangerous commands to prevent system damage
- **Error Handling**: Comprehensive error handling with informative messages
- **Interactive Mode**: Continuous command execution until user exits
- **Timeout Protection**: Commands timeout after 30 seconds to prevent hanging

### LLM Features (New!)
- **Google Gemini Support**: Integration with Google's advanced Gemini API
- **Intelligent Prompting**: Context-aware prompts with examples for better results
- **Cloud-based AI**: No local installation required, always up-to-date
- **Automatic Fallback**: Seamlessly switches to regex patterns if API unavailable

## Requirements

- Python 3.6 or higher
- `google-generativeai` library (for Gemini API)
- `python-dotenv` library (for environment variables)
- **Optional**: Google Gemini API key for enhanced parsing

## Installation

### Basic Installation
```bash
# Clone the repository
git clone <repository-url>
cd ainux-proto

# Install Python dependencies
pip install -r requirements.txt
```

### Enhanced Installation (with Gemini AI)
```bash
# 1. Install basic requirements
pip install -r requirements.txt

# 2. Get Gemini API key
# Visit: https://aistudio.google.com/app/apikey
# Sign in and create a new API key

# 3. Create .env file in project directory
echo "GEMINI_API_KEY=your_api_key_here" > .env
# Replace "your_api_key_here" with your actual API key

# 4. Verify installation
python test_ainux_llm.py
```

## Usage

### Quick Start
```bash
# Basic version (regex patterns)
python ainux.py

# LLM Enhanced version
python ainux_llm.py

# Run tests
python test_ainux_llm.py

# Show setup guide
python test_ainux_llm.py --setup
```

### Example Commands

#### Enhanced Commands (LLM Mode Works Better)
- **"Show me all Python files in this directory"**
- **"What is my current location in the file system?"**
- **"Create a backup folder called project_backup"**
- **"Find all running processes containing chrome"**
- **"Display detailed network configuration"**
- **"List all files modified in the last hour"**

#### Classic Commands (Both Modes)
- **"List all files in the current directory"** → `dir` (Windows) or `ls -la` (Linux/Mac)
- **"Show current working directory"** → `cd` (Windows) or `pwd` (Linux/Mac)
- **"Create directory myproject"** → `mkdir myproject`
- **"Show running processes"** → `tasklist` (Windows) or `ps aux` (Linux/Mac)

### Interactive Commands
- **help**, **h**, **?** - Show help with examples
- **mode**, **info**, **status** - Show current parsing mode and configuration
- **exit**, **quit**, **q**, **bye** - Exit the program

## Architecture

### Core Components

1. **AiNux Class**: Main application logic
2. **OllamaLLM Class**: Handles local LLM communication
3. **Natural Language Parser**: Dual-mode parsing (LLM + Regex)
4. **Command Executor**: Safe subprocess-based execution
5. **Security Module**: Multi-layered command validation
6. **Interactive Interface**: User-friendly command loop

### LLM Integration Flow

```
User Input → LLM Processing → Safety Check → Command Execution
     ↓              ↓               ↓            ↓
   "Create a     mkdir folder   ✅ Safe      Execute & Show
    folder"         command     Command        Results
     ↓
  Fallback to Regex (if LLM fails)
```

## Configuration

### LLM Configuration
```python
from ainux_llm import AiNuxLLM, OllamaConfig

# Custom configuration
config = OllamaConfig(
    host="http://localhost:11434",  # Ollama server
    model="llama3.2:3b",           # Model to use
    temperature=0.1,                # Response determinism
    timeout=30,                    # Request timeout
    max_retries=3                  # Retry attempts
)

# Initialize with custom config
ainux = AiNuxLLM(use_llm=True, ollama_config=config)
```

### Security Configuration
Modify dangerous command patterns in `_load_dangerous_commands()`:
```python
dangerous_commands = [
    'rm -rf /',
    'format',
    'shutdown',
    # Add more patterns...
]
```

## File Structure

```
ainux-proto/
├── ainux.py              # Original regex-based version
├── ainux_llm.py          # LLM enhanced version
├── test_ainux.py         # Tests for original version  
├── test_ainux_llm.py     # Tests for LLM version
├── demo.py               # Basic demo script
├── demo_llm.py           # LLM demo script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Model Recommendations

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|-----------|
| `llama3.2:1b` | 1GB | Fast | Good | Quick responses |
| `llama3.2:3b` | 2GB | Medium | Better | **Recommended** |
| `qwen3:4b` | 4GB | Medium | Better | Alternative |
| `llama3.1:8b` | 4.7GB | Slower | Best | High accuracy |

## Performance Comparison

| Feature | Regex Mode | LLM Mode |
|---------|------------|-----------|
| Speed | ⚡ Very Fast | 🐢 2-5 seconds |
| Accuracy | 📊 Limited patterns | 🎯 High understanding |
| Flexibility | 🔧 Fixed patterns | 🤖 Natural language |
| Offline | ✅ Yes | ✅ Yes (with Ollama) |
| Resource Usage | 💾 Minimal | 🧠 Medium (RAM) |

## Security Features

### Multi-Layer Protection
1. **Pre-execution Validation**: Dangerous command blacklist
2. **Pattern Recognition**: Regex-based dangerous pattern detection
3. **LLM Safety**: Model trained to avoid harmful outputs
4. **Timeout Protection**: 30-second execution limits
5. **Sandboxed Execution**: Controlled subprocess environment

### Blocked Commands
- System destruction: `rm -rf /`, `format`, `fdisk`
- System control: `shutdown`, `reboot`, `halt`
- Network attacks: `wget | sh`, `curl | bash`
- Permission changes: `chmod 777`, `chown -R`

## Troubleshooting

### Common Issues

**"Ollama not available" Warning**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Install a model if none available
ollama run llama3.2:3b
```

**"Model not found" Error**
```bash
# List available models
ollama list

# Pull a specific model
ollama pull llama3.2:3b
```

**LLM Timeouts**
- Reduce `timeout` in `OllamaConfig`
- Use smaller model (`llama3.2:1b`)
- Check system resources (RAM/CPU)

## Future Enhancements

- **Voice Commands**: Speech-to-text integration
- **Context Memory**: Remember previous commands and context
- **Command Chaining**: Support for complex piped commands
- **GUI Interface**: Desktop application with visual interface
- **Cloud LLM Support**: Integration with cloud-based language models
- **Custom Training**: Fine-tuning models for specific command patterns

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Test thoroughly across platforms
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Changelog

### Version 2.0.0 (September 15, 2025)
- ➕ Added Ollama LLM integration
- ➕ Dual-mode parsing (LLM + Regex fallback)
- ➕ Enhanced security validation
- ➕ Improved interactive interface
- ➕ Comprehensive test suite

### Version 1.0.0 (September 15, 2025)
- 🎉 Initial release with regex-based parsing
- ✅ Cross-platform support
- ✅ Basic security measures
- ✅ Interactive command interface

## License

This project is provided as-is for educational purposes. Feel free to use, modify, and distribute.

## Disclaimer

**Important**: While AiNux includes multiple security layers, always be cautious when running system commands. Test in a safe environment first. The authors are not responsible for any system damage.

---

**Author**: AI Assistant  
**Date**: September 15, 2025  
**Version**: 2.0.0 (LLM Enhanced)  
**Repository**: [AiNux Proto](https://github.com/your-repo/ainux-proto)