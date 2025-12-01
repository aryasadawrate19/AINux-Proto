#!/usr/bin/env python3
"""
Test script for AiNux functionality
"""

from ainux import AiNux

def test_ainux():
    """Test AiNux functionality with various inputs"""
    
    print("Testing AiNux Natural Language Parser...")
    print("=" * 50)
    
    # Initialize AiNux
    ainux = AiNux()
    
    # Test cases
    test_cases = [
        "List all files in the current directory",
        "Show current working directory", 
        "Where am I?",
        "Show running processes",
        "Create directory testfolder",
        "Show network info",
        "Show system info",
        "This is not a valid command",
        "rm -rf /",  # This should be blocked
    ]
    
    print("Testing natural language parsing:")
    print("-" * 30)
    
    for test_input in test_cases:
        command = ainux.parse_natural_language(test_input)
        safety_check = "SAFE" if command and ainux.is_command_safe(command) else "BLOCKED/UNKNOWN"
        
        print(f"Input: '{test_input}'")
        print(f"Parsed Command: {command if command else 'Not recognized'}")
        print(f"Safety: {safety_check}")
        print("-" * 30)
    
    print("\nTesting command execution (safe commands only):")
    print("-" * 40)
    
    # Test safe commands
    safe_tests = [
        "Show current working directory",
        "List all files in the current directory",
    ]
    
    for test_input in safe_tests:
        print(f"\nTesting: '{test_input}'")
        command = ainux.parse_natural_language(test_input)
        if command and ainux.is_command_safe(command):
            result = ainux.execute_command(command)
            print(f"Command: {result['command']}")
            print(f"Success: {result['success']}")
            if result['success'] and result['output']:
                # Show only first few lines to avoid clutter
                output_lines = result['output'].split('\n')[:5]
                print(f"Output (first 5 lines): {chr(10).join(output_lines)}")
            elif not result['success']:
                print(f"Error: {result['error']}")
        else:
            print("Command was blocked or not recognized")

if __name__ == "__main__":
    test_ainux()