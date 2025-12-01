#!/usr/bin/env python3
"""
Quick demo showing the enhanced command display feature
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ainux_llm import AiNuxLLM

def show_command_display_demo():
    """Demonstrate the enhanced command display feature"""
    
    print("🎯 AiNux Enhanced Command Display Demo")
    print("=" * 45)
    print("This demo shows how AiNux now displays the generated commands clearly!")
    print()
    
    # Initialize AiNux (will use regex fallback if Ollama not available)
    ainux = AiNuxLLM(use_llm=True)
    
    # Test cases to demonstrate command generation
    demo_inputs = [
        "List all files in the current directory",
        "Show current working directory",
        "Show running processes",
        "Show network information",
        "Create directory test_demo"
    ]
    
    print("🔍 Command Generation Examples:")
    print("-" * 35)
    
    for i, user_input in enumerate(demo_inputs, 1):
        print(f"\n{i}. Natural Language Input:")
        print(f"   '{user_input}'")
        
        # Parse the command
        command = ainux.parse_natural_language(user_input)
        
        if command:
            parsing_mode = "🤖 LLM" if (ainux.use_llm and ainux.llm and ainux.llm.available) else "🔧 Regex"
            is_safe = ainux.is_command_safe(command)
            status = "✅ SAFE" if is_safe else "🚫 BLOCKED"
            
            print(f"   💡 Generated Command ({parsing_mode}): {command}")
            print(f"   🛡️  Security Status: {status}")
            
            # Show what would happen in interactive mode
            if is_safe:
                print(f"   ▶️  Would execute: {command}")
            else:
                print(f"   🚫 Would be blocked for safety")
        else:
            print("   ❌ Not recognized by current parsing mode")
    
    print(f"\n{'='*45}")
    print("🌟 New Features:")
    print("  • Clear command generation display")
    print("  • Shows parsing mode (LLM vs Regex)")
    print("  • Enhanced visual feedback")
    print("  • Security status indication")
    print(f"{'='*45}")
    
    print(f"\n🚀 Try the full interactive experience:")
    print(f"   python ainux_llm.py")

if __name__ == "__main__":
    show_command_display_demo()