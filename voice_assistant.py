#!/usr/bin/env python3
"""
OpenClaw Voice Assistant - Basic Implementation
Usage: python voice_assistant.py
Press Enter to start recording, speak, press Enter again when done.
"""

import asyncio
import json
import requests
import pyaudio
import wave
import tempfile
import subprocess
from pathlib import Path
import threading
import sys
import os

class OpenClawVoiceAssistant:
    def __init__(self):
        self.config = self.load_config()
        self.setup_audio()
        self.recording = False
        
    def load_config(self):
        """Load configuration with sensible defaults"""
        config_file = Path.home() / '.openclaw' / 'voice_config.json'
        
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "openclaw_port": 18789,
                "openclaw_token": self.get_openclaw_token(),
                "elevenlabs_key": self.get_elevenlabs_key(),
                "whisper_model": "medium",
                "speech_timeout": 10,
                "sample_rate": 16000,
                "chunk_size": 1024
            }
            
            # Save default config
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"📝 Created config file: {config_file}")
            print("Edit it to customize settings")
            return default_config
    
    def get_openclaw_token(self):
        """Extract OpenClaw token from config"""
        try:
            with open(Path.home() / '.openclaw' / 'openclaw.json') as f:
                config_text = f.read()
                # Look for token in the config (it's in the auth section)
                import re
                token_match = re.search(r'token:\s*[\'"]([^\'"]+)[\'"]', config_text)
                if token_match:
                    return token_match.group(1)
        except:
            pass
        return "your-openclaw-token-here"
    
    def get_elevenlabs_key(self):
        """Extract ElevenLabs key from OpenClaw config"""
        try:
            with open(Path.home() / '.openclaw' / 'openclaw.json') as f:
                config_text = f.read()
                # Look for ElevenLabs key
                import re
                key_match = re.search(r'apiKey:\s*[\'"]([^\'"]+)[\'"]', config_text)
                if key_match:
                    return key_match.group(1)
        except:
            pass
        return "your-elevenlabs-key-here"
        
    def setup_audio(self):
        """Initialize audio system"""
        try:
            import pyaudio
            self.audio = pyaudio.PyAudio()
            self.format = pyaudio.paInt16
            self.channels = 1
            self.rate = self.config['sample_rate']
            self.chunk = self.config['chunk_size']
            
            # Test audio input
            try:
                stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk
                )
                stream.close()
                print("🎙️ Audio input initialized successfully")
            except Exception as e:
                print(f"⚠️ Audio input issue: {e}")
                print("Make sure you have a microphone connected")
                
        except ImportError:
            print("❌ pyaudio not installed. Run: pip install pyaudio")
            sys.exit(1)
    
    def record_audio(self, duration=None):
        """Record audio from microphone"""
        print("🔴 Recording... Press Enter when finished speaking")
        
        frames = []
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        # Start recording in background
        self.recording = True
        start_time = asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0
        
        while self.recording:
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                # Auto-stop after timeout
                if duration and len(frames) > (self.rate / self.chunk * duration):
                    break
                    
            except Exception as e:
                print(f"Recording error: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            return f.name
    
    def stop_recording(self):
        """Stop current recording"""
        self.recording = False
    
    def transcribe_audio(self, audio_file):
        """Convert speech to text using Whisper"""
        try:
            print("🔄 Transcribing speech...")
            
            # Run Whisper
            result = subprocess.run([
                'whisper', audio_file,
                '--model', self.config['whisper_model'],
                '--output_format', 'txt',
                '--output_dir', '/tmp',
                '--language', 'en'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"Whisper error: {result.stderr}")
                return None
            
            # Find the output file
            base_name = Path(audio_file).stem
            txt_file = Path('/tmp') / f"{base_name}.txt"
            
            if txt_file.exists():
                text = txt_file.read_text().strip()
                txt_file.unlink()  # Clean up
                return text
            else:
                print("❌ Whisper output file not found")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Whisper transcription timed out")
            return None
        except FileNotFoundError:
            print("❌ Whisper not found. Install with: brew install openai-whisper")
            return None
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def query_openclaw(self, text):
        """Send query to OpenClaw gateway"""
        try:
            print(f"🤖 Asking OpenClaw: {text}")
            
            url = f"http://localhost:{self.config['openclaw_port']}/api/sessions/send"
            headers = {
                'Authorization': f"Bearer {self.config['openclaw_token']}",
                'Content-Type': 'application/json'
            }
            data = {
                'message': text,
                'sessionKey': 'voice-assistant-test'
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'response' in result:
                    return result['response']
                elif 'message' in result:
                    return result['message']
                else:
                    return str(result)
            else:
                print(f"❌ OpenClaw API error: {response.status_code}")
                return f"Sorry, I couldn't process that request. (Error {response.status_code})"
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to OpenClaw. Is it running?")
            return "OpenClaw is not responding. Please make sure it's running."
        except Exception as e:
            print(f"❌ Query error: {e}")
            return "Sorry, something went wrong while processing your request."
    
    def synthesize_speech(self, text):
        """Convert text to speech using ElevenLabs"""
        try:
            print("🔊 Generating speech...")
            
            # Use the TTS tool that's already configured
            import subprocess
            
            # Try using OpenClaw's built-in TTS
            result = subprocess.run([
                'openclaw', 'tts', '--text', text
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Speech generated successfully")
                return True
            else:
                print(f"TTS error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Speech synthesis error: {e}")
            return False
    
    def run_interactive(self):
        """Interactive mode - press Enter to record"""
        print("🎙️ OpenClaw Voice Assistant (Interactive Mode)")
        print("=" * 50)
        print("Press Enter to start recording")
        print("Speak your question")
        print("Press Enter again to stop recording")
        print("Type 'quit' to exit")
        print()
        
        while True:
            try:
                # Wait for user to press Enter
                user_input = input("Press Enter to record (or 'quit' to exit): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                # Start recording in a thread
                audio_file = None
                
                def record_thread():
                    nonlocal audio_file
                    audio_file = self.record_audio()
                
                recording_thread = threading.Thread(target=record_thread)
                recording_thread.start()
                
                # Wait for user to press Enter to stop
                input("🔴 Recording... Press Enter to stop: ")
                self.stop_recording()
                recording_thread.join()
                
                if audio_file:
                    # Process the recording
                    text = self.transcribe_audio(audio_file)
                    
                    if text:
                        print(f"📝 You said: '{text}'")
                        
                        # Query OpenClaw
                        response = self.query_openclaw(text)
                        print(f"🤖 Response: {response}")
                        
                        # Convert to speech
                        self.synthesize_speech(response)
                    else:
                        print("❌ Could not understand the audio")
                    
                    # Clean up
                    Path(audio_file).unlink()
                
                print()  # Add spacing
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    print("🚀 Initializing OpenClaw Voice Assistant...")
    
    # Check dependencies
    missing_deps = []
    
    try:
        import pyaudio
    except ImportError:
        missing_deps.append("pyaudio")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   pip install {dep}")
        return
    
    # Check if Whisper is available
    try:
        subprocess.run(['whisper', '--help'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Whisper not found. Install with: brew install openai-whisper")
        return
    
    # Check if OpenClaw is running
    try:
        response = requests.get('http://localhost:18789/api/status', timeout=5)
        if response.status_code != 200:
            print("⚠️ OpenClaw may not be running properly")
    except:
        print("⚠️ Could not connect to OpenClaw on localhost:18789")
        print("   Make sure OpenClaw gateway is running")
    
    # Start the assistant
    assistant = OpenClawVoiceAssistant()
    assistant.run_interactive()

if __name__ == "__main__":
    main()