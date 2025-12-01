#!/usr/bin/env python3
"""
AiNux LLM Demo with Available Model
Demonstrates AiNux with the locally available Ollama model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ainux_llm import AiNuxLLM, GeminiConfig

def demo_with_available_model():
    """Demo AiNux using the available model"""
    
    print("🎯 AiNux LLM Demo with Gemini")
    print("=" * 35)
    
    # Try to use Gemini
    config = GeminiConfig()
    
    print(f"🤖 Attempting to use model: {config.model}")
    ainux = AiNuxLLM(use_llm=True, gemini_config=config)
    
    print("\n🧪 Testing Enhanced Natural Language Processing:")
    print("-" * 50)
    
    # Test cases that show LLM advantages
    enhanced_test_cases = [
        "Show me all the files in this folder",
        "What directory am I currently in?",
        "List running processes on the system",
        "Create a new directory called test_folder",
        "Display the network configuration",
        "Show system information",
        "Find all Python files here",
        "What processes are currently running?",
    ]
    
    for i, test_input in enumerate(enhanced_test_cases, 1):
        print(f"\n{i}. Input: '{test_input}'")
        
        # Parse with potential LLM enhancement
        command = ainux.parse_natural_language(test_input)
        
        if command:
            is_safe = ainux.is_command_safe(command)
            status = "✅ SAFE" if is_safe else "🚫 BLOCKED"
            parsing_mode = "🤖 LLM" if (ainux.use_llm and ainux.llm and ainux.llm.available) else "🔧 Regex"
            print(f"   💡 Generated Command ({parsing_mode}): {command}")
            print(f"   🛡️  Security Status: {status}")
        else:
            print("   ❌ Generated: Not recognized")
    
    print(f"\n{'='*50}")
    print("🎮 Interactive Mode Available!")
    print("Run: python ainux_llm.py")
    print(f"{'='*50}")

def run_quick_interactive():
    """Run a quick interactive session for demo"""
    
    print("\n🚀 Quick Interactive Demo")
    print("(Type 'demo exit' to return)")
    print("-" * 30)
    
    config = GeminiConfig()  # Use Gemini
    ainux = AiNuxLLM(use_llm=True, gemini_config=config)
    
    demo_commands = [
        "list files in current directory",
        "show current directory", 
        "demo exit"
    ]
    
    for command in demo_commands:
        print(f"\nAiNux🤖> {command}")
        
        if "demo exit" in command:
            print("👋 Demo completed!")
            break
            
        result_command = ainux.parse_natural_language(command)
        if result_command and ainux.is_command_safe(result_command):
            result = ainux.execute_command(result_command)
            ainux.display_result(result)
        else:
            print(f"❓ Could not process: {command}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        run_quick_interactive()
    else:
        demo_with_available_model()
        
        print(f"\n💡 To try quick interactive demo:")
        print(f"   python demo_llm.py interactive")