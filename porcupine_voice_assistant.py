#!/usr/bin/env python3
"""
OpenClaw Voice Assistant - Porcupine Wake Word Implementation
Continuous listening with "Hey OpenClaw" activation

Usage: python3 porcupine_voice_assistant.py
Say "Hey OpenClaw" followed by your command.
"""

import asyncio
import json
import requests
import pyaudio
import wave
import tempfile
import subprocess
import threading
import struct
import time
from pathlib import Path
import sys
import os

class PorcupineVoiceAssistant:
    def __init__(self):
        self.config = self.load_config()
        self.setup_porcupine()
        self.setup_audio()
        self.listening = True
        self.processing_command = False
        
    def load_config(self):
        """Load configuration with Porcupine settings"""
        config_file = Path.home() / '.openclaw' / 'voice_config.json'
        
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        else:
            config = {}
        
        # Add Porcupine-specific settings
        porcupine_defaults = {
            "porcupine_access_key": "ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE",
            "porcupine_model_path": "hey-openclaw.ppn",
            "porcupine_sensitivity": 0.7,
            "wake_word_timeout": 5.0,
            "command_timeout": 10.0,
            "activation_sound": True,
            "vad_aggressiveness": 2
        }
        
        # Merge with existing config
        for key, value in porcupine_defaults.items():
            if key not in config:
                config[key] = value
        
        # Save updated config
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config
    
    def setup_porcupine(self):
        """Initialize Porcupine wake word detection"""
        try:
            import pvporcupine
            
            # Check if access key is configured
            if self.config['porcupine_access_key'] == "ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE":
                print("🔧 Porcupine Setup Required!")
                print("=" * 40)
                print("1. Go to https://console.picovoice.ai/")
                print("2. Sign up for free account")
                print("3. Get your Access Key")
                print("4. Train custom wake word:")
                print("   - Phrase: 'Hey OpenClaw'")
                print("   - Language: English")
                print("   - Download .ppn file to this directory")
                print("5. Update ~/.openclaw/voice_config.json:")
                print(f'   "porcupine_access_key": "your-access-key-here"')
                print(f'   "porcupine_model_path": "path/to/hey-openclaw.ppn"')
                print("")
                print("For testing, I'll use a built-in keyword...")
                
                # Try with built-in keyword for testing
                try:
                    self.porcupine = pvporcupine.create(
                        access_key=self.config['porcupine_access_key'],
                        keywords=['computer'],  # Built-in keyword for testing
                        sensitivities=[self.config['porcupine_sensitivity']]
                    )
                    print("✅ Using 'computer' as test wake word (say 'computer' instead of 'Hey OpenClaw')")
                    self.wake_word_phrase = "computer"
                except:
                    print("❌ Invalid access key. Please set up Porcupine properly.")
                    self.porcupine = None
                    return
            else:
                # Use custom trained model
                model_path = Path(self.config['porcupine_model_path'])
                
                if not model_path.exists():
                    # Try relative to script directory
                    script_dir = Path(__file__).parent
                    model_path = script_dir / self.config['porcupine_model_path']
                
                if model_path.exists():
                    self.porcupine = pvporcupine.create(
                        access_key=self.config['porcupine_access_key'],
                        keyword_paths=[str(model_path)],
                        sensitivities=[self.config['porcupine_sensitivity']]
                    )
                    print(f"✅ Custom wake word model loaded: {model_path}")
                    self.wake_word_phrase = "Hey OpenClaw"
                else:
                    print(f"❌ Wake word model not found: {model_path}")
                    print("Using built-in 'computer' keyword for testing...")
                    self.porcupine = pvporcupine.create(
                        access_key=self.config['porcupine_access_key'],
                        keywords=['computer'],
                        sensitivities=[self.config['porcupine_sensitivity']]
                    )
                    self.wake_word_phrase = "computer"
            
            self.frame_length = self.porcupine.frame_length
            self.sample_rate = self.porcupine.sample_rate
            
            print(f"🎙️ Wake word detection ready: '{self.wake_word_phrase}'")
            
        except ImportError:
            print("❌ Porcupine not installed")
            print("Install with: pip install pvporcupine")
            self.porcupine = None
        except Exception as e:
            print(f"❌ Porcupine setup failed: {e}")
            print("Check your access key and model path in ~/.openclaw/voice_config.json")
            self.porcupine = None
    
    def setup_audio(self):
        """Initialize audio for continuous listening"""
        try:
            self.audio = pyaudio.PyAudio()
            
            if self.porcupine:
                self.sample_rate = self.porcupine.sample_rate
                self.frame_length = self.porcupine.frame_length
            else:
                self.sample_rate = 16000
                self.frame_length = 512
                
            self.format = pyaudio.paInt16
            self.channels = 1
            
            print(f"🔊 Audio configured: {self.sample_rate}Hz, {self.frame_length} frame length")
            
        except Exception as e:
            print(f"❌ Audio setup failed: {e}")
            sys.exit(1)
    
    def play_activation_sound(self):
        """Play a sound to indicate wake word detection"""
        if not self.config.get('activation_sound', True):
            return
            
        # Simple beep using system audio
        try:
            if sys.platform == 'darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Glass.aiff &')
            elif sys.platform.startswith('linux'):
                os.system('aplay /usr/share/sounds/alsa/Front_Left.wav &')
        except:
            pass  # Don't fail if sound doesn't work
    
    async def listen_for_wake_word(self):
        """Continuous listening for wake word"""
        if not self.porcupine:
            print("❌ Wake word detection not available")
            return
        
        print(f"👂 Listening for '{self.wake_word_phrase}'...")
        print("Press Ctrl+C to stop")
        
        stream = self.audio.open(
            rate=self.sample_rate,
            channels=self.channels,
            format=self.format,
            input=True,
            frames_per_buffer=self.frame_length
        )
        
        try:
            while self.listening:
                if self.processing_command:
                    await asyncio.sleep(0.1)
                    continue
                
                try:
                    # Read audio frame
                    pcm = stream.read(self.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.frame_length, pcm)
                    
                    # Check for wake word
                    keyword_index = self.porcupine.process(pcm)
                    
                    if keyword_index >= 0:
                        print(f"\n🎯 Wake word '{self.wake_word_phrase}' detected!")
                        self.play_activation_sound()
                        await self.handle_voice_command()
                        print(f"👂 Listening for '{self.wake_word_phrase}'...")
                    
                    # Yield control to allow other operations
                    await asyncio.sleep(0.001)
                    
                except Exception as e:
                    print(f"⚠️ Audio processing error: {e}")
                    await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
        finally:
            stream.close()
            if self.porcupine:
                self.porcupine.delete()
    
    async def handle_voice_command(self):
        """Process voice command after wake word detection"""
        self.processing_command = True
        
        try:
            print("🔴 Listening for command...")
            
            # Capture speech with voice activity detection
            audio_file = await self.capture_command_with_vad()
            
            if audio_file:
                # Use existing transcription and response logic
                await self.process_voice_command(audio_file)
                
                # Cleanup
                Path(audio_file).unlink()
            else:
                print("❌ No command detected")
                
        except Exception as e:
            print(f"❌ Command processing error: {e}")
        finally:
            self.processing_command = False
    
    async def capture_command_with_vad(self):
        """Capture speech after wake word using voice activity detection"""
        try:
            import webrtcvad
            
            # Setup voice activity detection
            vad = webrtcvad.Vad(self.config.get('vad_aggressiveness', 2))
            
            frames = []
            silence_count = 0
            speech_detected = False
            frame_duration_ms = 10  # 10ms frames for VAD
            frames_per_buffer = int(self.sample_rate * frame_duration_ms / 1000)
            max_silence_frames = int(3000 / frame_duration_ms)  # 3 seconds of silence
            max_total_frames = int(self.config.get('command_timeout', 10) * 1000 / frame_duration_ms)
            
            stream = self.audio.open(
                rate=self.sample_rate,
                channels=self.channels,
                format=self.format,
                input=True,
                frames_per_buffer=frames_per_buffer
            )
            
            try:
                frame_count = 0
                while frame_count < max_total_frames:
                    frame = stream.read(frames_per_buffer, exception_on_overflow=False)
                    frames.append(frame)
                    frame_count += 1
                    
                    # Check if frame contains speech
                    try:
                        is_speech = vad.is_speech(frame, self.sample_rate)
                        
                        if is_speech:
                            speech_detected = True
                            silence_count = 0
                            print("🗣️", end="", flush=True)  # Visual indicator
                        else:
                            if speech_detected:  # Only count silence after speech starts
                                silence_count += 1
                                if silence_count % 10 == 0:  # Every 100ms
                                    print(".", end="", flush=True)
                        
                        # Stop after prolonged silence
                        if speech_detected and silence_count > max_silence_frames:
                            print(" [end of speech]")
                            break
                            
                    except Exception as vad_error:
                        # VAD failed, continue without it
                        pass
                    
                    # Brief yield
                    await asyncio.sleep(0.001)
                    
            finally:
                stream.close()
            
            if not speech_detected:
                print("❌ No speech detected")
                return None
            
            print(" ✅ Speech captured")
            
            # Save audio to file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wf = wave.open(f.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
                wf.close()
                return f.name
                
        except ImportError:
            print("⚠️ webrtcvad not available, using simple timeout capture")
            return await self.capture_command_simple()
        except Exception as e:
            print(f"❌ VAD capture failed: {e}")
            return await self.capture_command_simple()
    
    async def capture_command_simple(self):
        """Fallback: simple timeout-based capture"""
        duration = self.config.get('command_timeout', 5.0)
        
        frames = []
        frames_per_second = int(self.sample_rate / 1024)
        total_frames = int(frames_per_second * duration)
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        try:
            for i in range(total_frames):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
                
                # Progress indicator
                if i % (frames_per_second // 2) == 0:  # Every 0.5 seconds
                    print("🔴", end="", flush=True)
                    
                await asyncio.sleep(0.001)
                
        finally:
            stream.close()
            
        print(" ✅ Timeout capture complete")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            return f.name
    
    async def process_voice_command(self, audio_file):
        """Process the captured voice command"""
        # Import the existing voice assistant for transcription and response
        from voice_assistant import OpenClawVoiceAssistant
        
        assistant = OpenClawVoiceAssistant()
        
        # Transcribe
        print("🔄 Transcribing...")
        text = assistant.transcribe_audio(audio_file)
        
        if text:
            print(f"📝 You said: '{text}'")
            
            # Query OpenClaw
            response = assistant.query_openclaw(text)
            print(f"🤖 Response: {response}")
            
            # Synthesize speech
            assistant.synthesize_speech(response)
        else:
            print("❌ Could not transcribe audio")
    
    async def run_continuous(self):
        """Main continuous operation loop"""
        print("🎙️ OpenClaw Voice Assistant - Continuous Mode")
        print("=" * 50)
        
        if not self.porcupine:
            print("❌ Wake word detection not available")
            print("Please configure Porcupine in ~/.openclaw/voice_config.json")
            return
        
        print(f"Wake word: '{self.wake_word_phrase}'")
        print(f"Sensitivity: {self.config['porcupine_sensitivity']}")
        print(f"Command timeout: {self.config['command_timeout']}s")
        print("")
        
        try:
            await self.listen_for_wake_word()
        except Exception as e:
            print(f"❌ Continuous operation failed: {e}")
        finally:
            if hasattr(self, 'audio'):
                self.audio.terminate()

def install_dependencies():
    """Install required dependencies for wake word detection"""
    missing_deps = []
    
    try:
        import pvporcupine
    except ImportError:
        missing_deps.append("pvporcupine")
    
    try:
        import webrtcvad
    except ImportError:
        missing_deps.append("webrtcvad")
    
    if missing_deps:
        print("📦 Installing wake word dependencies...")
        for dep in missing_deps:
            print(f"   pip install {dep}")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep])

def main():
    """Main entry point"""
    print("🚀 Initializing OpenClaw Voice Assistant with Wake Word Detection...")
    
    # Install dependencies if needed
    install_dependencies()
    
    # Check basic dependencies
    try:
        import pvporcupine
        import pyaudio
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: ./setup_voice_assistant.sh")
        return
    
    # Start the assistant
    assistant = PorcupineVoiceAssistant()
    
    try:
        asyncio.run(assistant.run_continuous())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()