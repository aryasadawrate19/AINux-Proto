#!/usr/bin/env python3
"""
Quick smoke test for voice_input module.
Does not record audio; only imports and reports availability.
"""

if __name__ == "__main__":
    try:
        import voice_input
        has_api = hasattr(voice_input, "listen_for_command")
        print("voice_input import: OK", "API found" if has_api else "API missing")
    except Exception as e:
        print("voice_input import failed:", e)
