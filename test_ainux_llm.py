#!/usr/bin/env python3
"""
Test script for AiNux LLM Enhanced functionality
Tests both LLM mode and regex fallback mode
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ainux_llm import AiNuxLLM, GeminiConfig

def test_ainux_llm():
    """Test AiNux LLM Enhanced functionality"""
    
    print("🧪 Testing AiNux LLM Enhanced...")
    print("=" * 60)
    
    # Initialize AiNux with LLM support
    print("🤖 Testing with LLM enabled...")
    ainux_llm = AiNuxLLM(use_llm=True)
    
    # Initialize AiNux without LLM for comparison
    print("🔧 Testing with regex fallback...")
    ainux_regex = AiNuxLLM(use_llm=False)
    
    print("\n" + "=" * 60)
    
    # Test cases - mix of simple and complex
    test_cases = [
        # Simple cases (should work in both modes)
        "List all files in the current directory",
        "Show current working directory",
        "Show running processes",
        
        # Complex cases (should work better with LLM)
        "Show me all Python files in this directory",
        "Create a folder called test_project",
        "What is my current location in the file system?",
        "Display all active processes on this computer",
        "Show me network configuration details",
        
        # Edge cases
        "This is not a valid command",
        "rm -rf /",  # Should be blocked
        "shutdown now",  # Should be blocked
    ]
    
    print("🔍 Testing Natural Language Parsing:")
    print("-" * 40)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_input}'")
        print("   " + "─" * 50)
        
        # Test with LLM
        llm_command = ainux_llm.parse_natural_language(test_input)
        llm_safe = "SAFE" if llm_command and ainux_llm.is_command_safe(llm_command) else "BLOCKED/UNKNOWN"
        
        # Test with regex
        regex_command = ainux_regex.parse_natural_language(test_input)
        regex_safe = "SAFE" if regex_command and ainux_regex.is_command_safe(regex_command) else "BLOCKED/UNKNOWN"
        
        print(f"   🤖 LLM Mode:   {llm_command if llm_command else 'Not recognized'} ({llm_safe})")
        print(f"   🔧 Regex Mode: {regex_command if regex_command else 'Not recognized'} ({regex_safe})")
        
        # Show which mode performed better
        if llm_command and not regex_command:
            print("   ✨ LLM shows superior understanding!")
        elif regex_command and not llm_command:
            print("   🔧 Regex worked, LLM didn't recognize")
        elif llm_command == regex_command:
            print("   ⚖️  Both modes produced same result")
    
    print("\n" + "=" * 60)
    print("🔒 Testing Security Features:")
    print("-" * 30)
    
    dangerous_commands = [
        "rm -rf /",
        "format c:",
        "shutdown /s /t 0",
        "del /q /s *.*",
        "dd if=/dev/zero of=/dev/sda"
    ]
    
    for dangerous_cmd in dangerous_commands:
        is_safe_llm = ainux_llm.is_command_safe(dangerous_cmd)
        is_safe_regex = ainux_regex.is_command_safe(dangerous_cmd)
        
        status = "✅ BLOCKED" if not is_safe_llm and not is_safe_regex else "❌ NOT BLOCKED"
        print(f"   {dangerous_cmd:<25} → {status}")
    
    print("\n" + "=" * 60)
    print("🚀 Testing Safe Command Execution:")
    print("-" * 35)
    
    # Test a few safe commands
    safe_test_cases = [
        "Show current working directory",
        "List all files in the current directory"
    ]
    
    for test_input in safe_test_cases:
        print(f"\n🧪 Testing execution: '{test_input}'")
        
        # Try LLM first
        command = ainux_llm.parse_natural_language(test_input)
        if command and ainux_llm.is_command_safe(command):
            result = ainux_llm.execute_command(command)
            print(f"   🔧 Command: {result['command']}")
            print(f"   ✅ Success: {result['success']}")
            if result['success'] and result['output']:
                # Show only first 3 lines to avoid clutter
                output_lines = result['output'].split('\n')[:3]
                print(f"   📄 Output (first 3 lines): {' | '.join(output_lines)}")
            elif not result['success']:
                print(f"   🚨 Error: {result['error']}")
        else:
            print("   ⚠️  Command was blocked or not recognized")

def show_gemini_setup_guide():
    """Display setup instructions for Gemini API"""
    print("\n" + "🤖 Google Gemini Setup Guide for AiNux LLM Enhanced")
    print("=" * 55)
    print("\n📥 API Key Setup:")
    print("   1. Visit: https://aistudio.google.com/app/apikey")
    print("   2. Sign in with your Google account")
    print("   3. Create a new API key")
    print("   4. Copy the API key")
    print("\n📄 Environment Setup:")
    print("   1. Create a .env file in the project directory")
    print("   2. Add: GEMINI_API_KEY=your_api_key_here")
    print("   3. Replace 'your_api_key_here' with your actual key")
    print("\n🚀 Usage:")
    print("   • Gemini runs as a cloud-based API service")
    print("   • AiNux automatically detects the API key")
    print("   • If unavailable, AiNux falls back to regex parsing")
    print("\n🧠 Model Options:")
    print("   • gemini-pro        (default, balanced)")
    print("   • gemini-pro-vision (supports images)")
    print("   • gemini-1.5-pro    (advanced reasoning)")
    print("\n💡 Benefits:")
    print("   • No local installation required")
    print("   • Powerful language understanding")
    print("   • Always up-to-date model")
    print("   • Fast response times")
    print("\n� Pricing:")
    print("   • Free tier available with rate limits")
    print("   • Pay-per-use for higher usage")
    print("   • Very cost-effective for personal use")

if __name__ == "__main__":
    print("🎯 AiNux LLM Enhanced Test Suite")
    print("=" * 40)
    
    # Check if user wants setup guide
    if len(sys.argv) > 1 and sys.argv[1] in ['--setup', '-s', 'setup']:
        show_gemini_setup_guide()
    else:
        test_ainux_llm()
        print("\n💡 For Gemini setup guide, run: python test_ainux_llm.py --setup")