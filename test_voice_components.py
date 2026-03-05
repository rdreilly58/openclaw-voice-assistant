#!/usr/bin/env python3
"""
Test script for Voice Assistant components
Tests each part of the pipeline individually
"""

import subprocess
import requests
import tempfile
import wave
import json
from pathlib import Path

def test_microphone():
    """Test microphone input"""
    print("🎙️ Testing microphone...")
    try:
        import pyaudio
        
        audio = pyaudio.PyAudio()
        
        # List input devices
        print("\n📱 Available audio input devices:")
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  {i}: {info['name']} ({info['maxInputChannels']} channels)")
        
        # Test recording
        print("\n🔴 Testing 3-second recording...")
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        frames = []
        for _ in range(int(16000 / 1024 * 3)):  # 3 seconds
            data = stream.read(1024)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        print("✅ Microphone test successful")
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_whisper():
    """Test Whisper transcription"""
    print("\n🎧 Testing Whisper...")
    try:
        # Check if whisper command exists
        result = subprocess.run(['whisper', '--help'], capture_output=True)
        if result.returncode != 0:
            print("❌ Whisper command not found")
            return False
            
        print("✅ Whisper is available")
        
        # Test with a sample (you'd need to create a test audio file)
        # For now, just verify the command works
        return True
        
    except FileNotFoundError:
        print("❌ Whisper not installed")
        print("   Install with: brew install openai-whisper")
        return False
    except Exception as e:
        print(f"❌ Whisper test error: {e}")
        return False

def test_openclaw_connection():
    """Test OpenClaw gateway connection"""
    print("\n🤖 Testing OpenClaw connection...")
    try:
        response = requests.get('http://localhost:18789/api/status', timeout=5)
        if response.status_code == 200:
            print("✅ OpenClaw gateway is responding")
            return True
        else:
            print(f"❌ OpenClaw returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to OpenClaw")
        print("   Make sure it's running: openclaw gateway start")
        return False
    except Exception as e:
        print(f"❌ OpenClaw test error: {e}")
        return False

def test_openclaw_query():
    """Test sending a query to OpenClaw"""
    print("\n🗣️ Testing OpenClaw query...")
    
    # Get token from config
    try:
        config_path = Path.home() / '.openclaw' / 'openclaw.json'
        with open(config_path) as f:
            config_text = f.read()
            import re
            token_match = re.search(r'token:\s*[\'"]([^\'"]+)[\'"]', config_text)
            if not token_match:
                print("❌ Could not find OpenClaw token in config")
                return False
            token = token_match.group(1)
    except Exception as e:
        print(f"❌ Could not read OpenClaw config: {e}")
        return False
    
    try:
        url = "http://localhost:18789/api/sessions/send"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {
            'message': 'Test query from voice assistant',
            'sessionKey': 'voice-test'
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ OpenClaw query successful")
            result = response.json()
            print(f"   Response preview: {str(result)[:100]}...")
            return True
        else:
            print(f"❌ Query failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Query test error: {e}")
        return False

def test_tts():
    """Test text-to-speech"""
    print("\n🔊 Testing text-to-speech...")
    try:
        # Test OpenClaw TTS command
        result = subprocess.run([
            'openclaw', 'tts', '--text', 'Voice assistant test'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ TTS test successful")
            return True
        else:
            print(f"❌ TTS failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TTS timed out")
        return False
    except Exception as e:
        print(f"❌ TTS test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 OpenClaw Voice Assistant Component Tests")
    print("=" * 50)
    
    tests = [
        ("Microphone", test_microphone),
        ("Whisper", test_whisper),
        ("OpenClaw Connection", test_openclaw_connection),
        ("OpenClaw Query", test_openclaw_query),
        ("Text-to-Speech", test_tts),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! Voice assistant should work.")
        print("Run: python3 voice_assistant.py")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        print("\nCommon fixes:")
        print("  • Install dependencies: ./setup_voice_assistant.sh")
        print("  • Start OpenClaw: openclaw gateway start")
        print("  • Check microphone permissions in System Preferences")

if __name__ == "__main__":
    main()