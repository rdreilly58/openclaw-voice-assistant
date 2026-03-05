#!/usr/bin/env python3
"""
Test script for Wake Word Detection components
Tests Porcupine integration, VAD, and wake word pipeline
"""

import sys
import subprocess
import tempfile
import wave
import struct
import time
import json
from pathlib import Path

def test_porcupine_installation():
    """Test if Porcupine is properly installed"""
    print("🎯 Testing Porcupine installation...")
    try:
        import pvporcupine
        
        print(f"✅ Porcupine version: {pvporcupine.LIBRARY_VERSION}")
        return True
        
    except ImportError:
        print("❌ Porcupine not installed")
        print("   Install with: pip install pvporcupine")
        return False
    except Exception as e:
        print(f"❌ Porcupine import error: {e}")
        return False

def test_webrtc_vad():
    """Test WebRTC Voice Activity Detection"""
    print("\n🗣️ Testing WebRTC VAD...")
    try:
        import webrtcvad
        
        # Create VAD instance
        vad = webrtcvad.Vad(2)
        
        # Test with silence (should return False)
        silence = b'\x00' * 320  # 10ms of silence at 16kHz
        is_speech = vad.is_speech(silence, 16000)
        
        if not is_speech:
            print("✅ WebRTC VAD working (silence detection)")
        else:
            print("⚠️ WebRTC VAD may be too sensitive")
            
        return True
        
    except ImportError:
        print("❌ WebRTC VAD not installed")
        print("   Install with: pip install webrtcvad")
        return False
    except Exception as e:
        print(f"❌ WebRTC VAD error: {e}")
        return False

def test_porcupine_access_key():
    """Test Porcupine with access key"""
    print("\n🔑 Testing Porcupine access key...")
    
    # Load config
    config_file = Path.home() / '.openclaw' / 'voice_config.json'
    if not config_file.exists():
        print("❌ No voice config found")
        print("   Run setup_wake_word.sh first")
        return False
    
    with open(config_file) as f:
        config = json.load(f)
    
    access_key = config.get('porcupine_access_key')
    
    if not access_key or access_key == "ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE":
        print("⚠️ Access key not configured")
        print("   Get your key from https://console.picovoice.ai/")
        print("   Test will use built-in keyword...")
        
        # Try with built-in keyword
        try:
            import pvporcupine
            porcupine = pvporcupine.create(keywords=['computer'])
            porcupine.delete()
            print("✅ Built-in keyword test successful")
            print("   Say 'computer' to test wake word detection")
            return True
        except Exception as e:
            print(f"❌ Built-in keyword test failed: {e}")
            return False
    else:
        # Test with user's access key
        try:
            import pvporcupine
            porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=['computer']  # Test with built-in first
            )
            porcupine.delete()
            print("✅ Access key valid")
            return True
        except Exception as e:
            print(f"❌ Access key test failed: {e}")
            print("   Check your access key in ~/.openclaw/voice_config.json")
            return False

def test_custom_wake_word_model():
    """Test custom wake word model if available"""
    print("\n🎙️ Testing custom wake word model...")
    
    # Load config
    config_file = Path.home() / '.openclaw' / 'voice_config.json'
    with open(config_file) as f:
        config = json.load(f)
    
    model_path = Path(config.get('porcupine_model_path', 'hey-openclaw.ppn'))
    access_key = config.get('porcupine_access_key')
    
    if not model_path.exists():
        # Try relative to script directory
        script_dir = Path(__file__).parent
        model_path = script_dir / model_path.name
    
    if not model_path.exists():
        print("⚠️ Custom wake word model not found")
        print(f"   Expected: {model_path}")
        print("   Train your model at https://console.picovoice.ai/")
        return False
    
    if access_key == "ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE":
        print("❌ Valid access key required for custom model")
        return False
    
    try:
        import pvporcupine
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[str(model_path)]
        )
        porcupine.delete()
        print(f"✅ Custom wake word model loaded: {model_path}")
        return True
    except Exception as e:
        print(f"❌ Custom model test failed: {e}")
        return False

def test_audio_pipeline():
    """Test the complete audio pipeline for wake word detection"""
    print("\n🎧 Testing audio pipeline...")
    
    try:
        import pyaudio
        import pvporcupine
        
        # Get sample rate and frame length from Porcupine
        porcupine = pvporcupine.create(keywords=['computer'])
        sample_rate = porcupine.sample_rate
        frame_length = porcupine.frame_length
        porcupine.delete()
        
        # Test audio input
        audio = pyaudio.PyAudio()
        
        try:
            stream = audio.open(
                rate=sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=frame_length
            )
            
            # Read a few frames to test
            for i in range(5):
                pcm = stream.read(frame_length, exception_on_overflow=False)
                pcm_data = struct.unpack_from("h" * frame_length, pcm)
                
                # Check if we got valid audio data
                if max(abs(x) for x in pcm_data) > 0:
                    print(f"✅ Audio frame {i+1}: Valid data")
                else:
                    print(f"⚠️ Audio frame {i+1}: Silence (check microphone)")
            
            stream.close()
            print("✅ Audio pipeline test successful")
            return True
            
        except Exception as e:
            print(f"❌ Audio pipeline error: {e}")
            return False
        finally:
            audio.terminate()
            
    except Exception as e:
        print(f"❌ Audio pipeline setup failed: {e}")
        return False

def test_wake_word_detection_live():
    """Interactive test of wake word detection"""
    print("\n🎯 Live wake word detection test...")
    print("This will listen for 10 seconds. Say the wake word to test.")
    
    try:
        import pvporcupine
        import pyaudio
        import struct
        
        # Load config for sensitivity
        config_file = Path.home() / '.openclaw' / 'voice_config.json'
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
            sensitivity = config.get('porcupine_sensitivity', 0.7)
        else:
            sensitivity = 0.7
        
        # Create Porcupine instance (use computer keyword for testing)
        porcupine = pvporcupine.create(
            keywords=['computer'],
            sensitivities=[sensitivity]
        )
        
        audio = pyaudio.PyAudio()
        stream = audio.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        print(f"👂 Listening for 'computer' (sensitivity: {sensitivity})...")
        print("Speak now or press Ctrl+C to skip...")
        
        detections = 0
        frames_processed = 0
        max_frames = int(10 * porcupine.sample_rate / porcupine.frame_length)  # 10 seconds
        
        try:
            while frames_processed < max_frames:
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
                
                keyword_index = porcupine.process(pcm)
                
                if keyword_index >= 0:
                    detections += 1
                    print(f"🎉 Wake word detected! (Detection #{detections})")
                
                frames_processed += 1
                
                # Progress indicator
                if frames_processed % (max_frames // 10) == 0:
                    print(".", end="", flush=True)
        
        except KeyboardInterrupt:
            print("\n⏹️ Test stopped by user")
        
        stream.close()
        audio.terminate()
        porcupine.delete()
        
        if detections > 0:
            print(f"✅ Wake word detection successful ({detections} detections)")
            return True
        else:
            print("⚠️ No wake word detected")
            print("   Try speaking more clearly or adjusting sensitivity")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ Test skipped")
        return True
    except Exception as e:
        print(f"❌ Live test failed: {e}")
        return False

def test_configuration():
    """Test configuration file and settings"""
    print("\n⚙️ Testing configuration...")
    
    config_file = Path.home() / '.openclaw' / 'voice_config.json'
    
    if not config_file.exists():
        print("❌ Configuration file not found")
        print("   Run setup_wake_word.sh to create default config")
        return False
    
    try:
        with open(config_file) as f:
            config = json.load(f)
        
        required_keys = [
            'porcupine_access_key',
            'porcupine_model_path', 
            'porcupine_sensitivity',
            'command_timeout',
            'vad_aggressiveness'
        ]
        
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"⚠️ Missing config keys: {missing_keys}")
            print("   Run setup_wake_word.sh to update config")
        else:
            print("✅ Configuration file complete")
        
        # Validate sensitivity
        sensitivity = config.get('porcupine_sensitivity', 0.7)
        if 0.0 <= sensitivity <= 1.0:
            print(f"✅ Sensitivity setting valid: {sensitivity}")
        else:
            print(f"⚠️ Sensitivity out of range: {sensitivity} (should be 0.0-1.0)")
        
        return len(missing_keys) == 0
        
    except json.JSONDecodeError as e:
        print(f"❌ Configuration file invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all wake word tests"""
    print("🧪 OpenClaw Voice Assistant - Wake Word Detection Tests")
    print("=" * 60)
    
    tests = [
        ("Porcupine Installation", test_porcupine_installation),
        ("WebRTC VAD", test_webrtc_vad),
        ("Configuration", test_configuration),
        ("Porcupine Access Key", test_porcupine_access_key),
        ("Custom Wake Word Model", test_custom_wake_word_model),
        ("Audio Pipeline", test_audio_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Optional live test
    print("\n" + "=" * 60)
    try:
        user_input = input("Run live wake word test? [y/N]: ").strip().lower()
        if user_input in ['y', 'yes']:
            results["Live Wake Word Test"] = test_wake_word_detection_live()
    except KeyboardInterrupt:
        print("\n⏹️ Live test skipped")
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    all_passed = True
    critical_passed = True
    
    critical_tests = ["Porcupine Installation", "Configuration", "Audio Pipeline"]
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        critical = " (CRITICAL)" if test_name in critical_tests else ""
        print(f"  {test_name}: {status}{critical}")
        
        if not passed:
            all_passed = False
            if test_name in critical_tests:
                critical_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! Wake word detection ready.")
        print("Run: python3 porcupine_voice_assistant.py")
    elif critical_passed:
        print("⚠️ Basic functionality working, but some features need setup.")
        print("Run: python3 porcupine_voice_assistant.py")
        print("Check the failed tests above for improvements.")
    else:
        print("❌ Critical issues found. Setup required.")
        print("\nNext steps:")
        print("  1. Run: ./setup_wake_word.sh")
        print("  2. Get Picovoice access key from https://console.picovoice.ai/")
        print("  3. Configure access key in ~/.openclaw/voice_config.json")

if __name__ == "__main__":
    main()