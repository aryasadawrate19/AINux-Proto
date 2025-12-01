#!/usr/bin/env python3
"""
Test script for enhanced AiNux LLM with complex natural language queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ainux_llm import AiNuxLLM, OllamaConfig

def test_complex_queries():
    """Test AiNux with complex and varied natural language inputs"""
    
    print("🧪 Testing Enhanced AiNux with Complex Queries")
    print("=" * 55)
    
    # Initialize with your current config
    config = OllamaConfig(host="http://localhost:20555", model="qwen3:4b")
    ainux = AiNuxLLM(use_llm=True, ollama_config=config)
    
    # Complex test cases that should work now
    complex_test_cases = [
        # File operations
        "show me all Python files in this directory",
        "find all text files here", 
        "list all .js files",
        "what Python scripts are in this folder",
        "display all markdown files",
        
        # Process queries  
        "show processes that contain chrome",
        "find running processes with firefox",
        "what processes are using the most memory",
        "show me all java processes",
        
        # System information
        "how much free disk space do I have",
        "what's the system uptime",
        "show me environment variables",
        "who is currently logged in",
        "what's the memory usage",
        "display network connections",
        
        # File analysis
        "count how many files are in this directory",
        "find large files bigger than 100MB",
        "show files modified today",
        "what files were changed recently",
        
        # Creative/conversational queries
        "I want to see what's running on my computer",
        "can you show me the files in this folder",
        "help me find python scripts",
        "what's taking up space on my disk",
        "are there any large files I should know about"
    ]
    
    print("🔍 Testing Complex Natural Language Processing:")
    print("-" * 50)
    
    successful_llm = 0
    successful_regex = 0
    total_tests = len(complex_test_cases)
    
    for i, test_input in enumerate(complex_test_cases, 1):
        print(f"\n{i:2d}. Testing: '{test_input}'")
        
        # Parse with the enhanced system
        command = ainux.parse_natural_language(test_input)
        
        if command:
            is_safe = ainux.is_command_safe(command)
            status = "✅ SAFE" if is_safe else "🚫 BLOCKED"
            
            # Determine what parsed it (this is a simplified check)
            if ainux.use_llm and ainux.llm and ainux.llm.available:
                # Check if it looks like an LLM response (more sophisticated commands)
                if len(command.split()) > 2 or any(op in command for op in ['|', '*', 'grep', 'findstr', 'find']):
                    parsing_source = "🤖 LLM"
                    successful_llm += 1
                else:
                    parsing_source = "🔧 Enhanced Regex" 
                    successful_regex += 1
            else:
                parsing_source = "🔧 Enhanced Regex"
                successful_regex += 1
                
            print(f"    ✅ Generated ({parsing_source}): {command}")
            print(f"    🛡️  Security: {status}")
            
            if is_safe and len(sys.argv) > 1 and sys.argv[1] == '--execute':
                print(f"    🚀 Executing command...")
                result = ainux.execute_command(command)
                if result['success']:
                    # Show first 3 lines of output
                    output_lines = result['output'].split('\n')[:3]
                    print(f"    📋 Sample Output: {' | '.join(output_lines)}")
                else:
                    print(f"    ❌ Execution failed: {result['error']}")
        else:
            print(f"    ❌ Could not parse this query")
    
    print(f"\n{'='*55}")
    print(f"📊 Test Results Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   🤖 LLM Successful: {successful_llm}")
    print(f"   🔧 Enhanced Regex Successful: {successful_regex}")
    print(f"   ❌ Failed: {total_tests - successful_llm - successful_regex}")
    print(f"   📈 Success Rate: {((successful_llm + successful_regex) / total_tests * 100):.1f}%")
    print(f"{'='*55}")
    
    if successful_llm + successful_regex > total_tests * 0.7:
        print("🎉 Great! The enhanced system is working well!")
    elif successful_llm + successful_regex > total_tests * 0.5:
        print("👍 Good progress! System handles most complex queries.")
    else:
        print("🔧 System needs more work for complex queries.")
        
    print(f"\n💡 Run with --execute flag to actually run safe commands")
    print(f"   python test_complex.py --execute")

if __name__ == "__main__":
    test_complex_queries()