#!/usr/bin/env python3
"""
Test script for desk-optimized assistant components
"""

import asyncio
import time
import sys
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        import pyaudio
        print("✅ PyAudio")
    except ImportError as e:
        print(f"❌ PyAudio: {e}")
        return False
    
    try:
        import pvporcupine
        print("✅ Porcupine")
    except ImportError as e:
        print(f"❌ Porcupine: {e}")
        return False
        
    try:
        import webrtcvad
        print("✅ WebRTC VAD")
    except ImportError as e:
        print(f"⚠️ WebRTC VAD: {e}")
    
    try:
        import psutil
        print("✅ psutil")
    except ImportError as e:
        print(f"❌ psutil: {e}")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    return True

def test_audio_devices():
    """Test audio device enumeration"""
    print("\n🔊 Testing audio devices...")
    
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        
        device_count = audio.get_device_count()
        print(f"Found {device_count} audio devices")
        
        input_devices = []
        for i in range(device_count):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info['name']))
        
        print(f"Available input devices ({len(input_devices)}):")
        for idx, name in input_devices:
            print(f"  [{idx}] {name}")
        
        audio.terminate()
        return len(input_devices) > 0
        
    except Exception as e:
        print(f"❌ Audio device test failed: {e}")
        return False

def test_porcupine():
    """Test Porcupine wake word detection setup"""
    print("\n🎙️ Testing Porcupine setup...")
    
    try:
        import pvporcupine
        
        # Test with built-in keyword
        porcupine = pvporcupine.create(
            keywords=['computer'],
            sensitivities=[0.7]
        )
        
        print(f"✅ Porcupine initialized")
        print(f"   Frame length: {porcupine.frame_length}")
        print(f"   Sample rate: {porcupine.sample_rate}")
        print(f"   Wake word: 'computer'")
        
        porcupine.delete()
        return True
        
    except Exception as e:
        print(f"❌ Porcupine test failed: {e}")
        return False

async def test_environment_monitor():
    """Test environment monitoring"""
    print("\n🖥️ Testing environment monitor...")
    
    try:
        from desk_environment_monitor import DeskEnvironmentMonitor
        
        monitor = DeskEnvironmentMonitor()
        state = monitor.get_state()
        
        print("✅ Environment monitor initialized")
        print(f"   Should listen: {state['should_listen']}")
        print(f"   Context mode: {state['context_mode']}")
        print(f"   Sensitivity modifier: {state['sensitivity_modifier']}")
        
        # Test context generation
        context = monitor.get_context_for_command("test command")
        print(f"   Context keys: {list(context.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment monitor test failed: {e}")
        return False

def test_whisper():
    """Test Whisper availability"""
    print("\n🗣️ Testing Whisper...")
    
    try:
        import subprocess
        result = subprocess.run(['whisper', '--help'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Whisper CLI available")
            return True
        else:
            print("❌ Whisper CLI not working")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Whisper test timed out")
        return False
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

def test_openclaw_connection():
    """Test OpenClaw gateway connection"""
    print("\n🌐 Testing OpenClaw connection...")
    
    try:
        import requests
        
        # Test basic connection
        url = "http://localhost:18789/api/status"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ OpenClaw gateway reachable")
            return True
        else:
            print(f"⚠️ OpenClaw responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ OpenClaw gateway not reachable (is it running?)")
        return False
    except Exception as e:
        print(f"❌ OpenClaw connection test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🖥️ Desk-Optimized Voice Assistant - System Test")
    print("=" * 50)
    
    tests = [
        ("Import test", test_imports),
        ("Audio devices", test_audio_devices),
        ("Porcupine setup", test_porcupine),
        ("Environment monitor", test_environment_monitor),
        ("Whisper availability", test_whisper),
        ("OpenClaw connection", test_openclaw_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'─' * 20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print(f"\n{'=' * 50}")
    print("📊 Test Results Summary:")
    print(f"{'=' * 50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🚀 All tests passed! Desk-optimized assistant is ready.")
        print("\n▶️  Run: python3 desk_optimized_assistant.py")
        print("    Say 'computer' + your command")
    elif passed >= total - 2:
        print("\n⚠️  Most tests passed. Assistant should work with minor issues.")
        print("    Run with caution: python3 desk_optimized_assistant.py")
    else:
        print("\n❌ Too many test failures. Check dependencies and setup.")
        print("    Try running: ./setup_desk_assistant.sh")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())