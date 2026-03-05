#!/usr/bin/env python3
"""
Simple launcher for the desk-optimized voice assistant with error handling
"""

import sys
import asyncio
import subprocess
from pathlib import Path

def check_dependencies():
    """Quick dependency check"""
    missing = []
    
    try:
        import pyaudio
    except ImportError:
        missing.append("pyaudio")
    
    try:
        import pvporcupine
    except ImportError:
        missing.append("pvporcupine")
    
    try:
        import psutil
    except ImportError:
        missing.append("psutil")
    
    # Check Whisper CLI
    try:
        subprocess.run(['whisper', '--help'], capture_output=True, timeout=5)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing.append("whisper (CLI)")
    
    return missing

def test_openclaw_connection():
    """Test OpenClaw gateway connectivity"""
    try:
        import requests
        response = requests.get("http://localhost:18789/api/prompt", 
                              json={"prompt": "test"}, 
                              timeout=3)
        return response.status_code in [200, 400, 401]  # Any response means it's running
    except:
        return False

async def main():
    """Launch the desk-optimized assistant with checks"""
    print("🖥️ Starting Desk-Optimized OpenClaw Voice Assistant...")
    print("=" * 55)
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("🔧 Run: ./setup_desk_assistant.sh")
        return
    
    print("✅ Dependencies checked")
    
    # Check OpenClaw
    if not test_openclaw_connection():
        print("⚠️ OpenClaw gateway not responding")
        print("   Make sure OpenClaw is running: openclaw gateway start")
        print("   Continuing anyway...")
    else:
        print("✅ OpenClaw gateway ready")
    
    # Import and run the assistant
    try:
        from desk_optimized_assistant import DeskOptimizedVoiceAssistant
        
        print("\n🚀 Initializing desk-optimized assistant...")
        assistant = DeskOptimizedVoiceAssistant()
        
        print("\n" + "="*55)
        print("🎙️ DESK VOICE ASSISTANT READY")
        print("="*55)
        print(f"Wake word: Say '{getattr(assistant, 'wake_word_phrase', 'computer')}'")
        print("Features: Environment awareness, work commands, performance optimized")
        print("Press Ctrl+C to stop")
        print("="*55)
        
        await assistant.run_desk_optimized()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Try running setup again: ./setup_desk_assistant.sh")
    except Exception as e:
        print(f"❌ Assistant error: {e}")
        print("🔧 Check configuration and dependencies")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Assistant stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Launcher error: {e}")