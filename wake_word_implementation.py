#!/usr/bin/env python3
"""
OpenClaw Voice Assistant - Wake Word Implementation
Future enhancement: Continuous listening with "Hey OpenClaw" detection

This is a template/example for Phase 2 implementation with Porcupine wake word detection.
NOT FUNCTIONAL YET - requires Porcupine license and configuration.
"""

import asyncio
import pyaudio
import struct
import threading
from pathlib import Path

class WakeWordVoiceAssistant:
    """Enhanced voice assistant with wake word detection"""
    
    def __init__(self):
        self.setup_wake_word()
        self.setup_audio()
        self.listening = False
        
    def setup_wake_word(self):
        """Initialize Porcupine wake word detection"""
        try:
            import pvporcupine
            
            # You'll need to:
            # 1. Sign up at https://console.picovoice.ai/
            # 2. Get access key
            # 3. Train custom "Hey OpenClaw" model or use built-in keywords
            
            self.porcupine = pvporcupine.create(
                access_key='YOUR_PICOVOICE_ACCESS_KEY',
                keyword_paths=['path/to/hey-openclaw.ppn'],  # Custom trained model
                # Or use built-in keywords:
                # keywords=['hey google', 'alexa'],  # Just for testing
                sensitivities=[0.7]  # Adjust sensitivity 0.0-1.0
            )
            
            print("✅ Wake word detection initialized")
            
        except ImportError:
            print("❌ Porcupine not installed")
            print("   Install with: pip install pvporcupine")
            self.porcupine = None
        except Exception as e:
            print(f"❌ Wake word setup failed: {e}")
            self.porcupine = None
    
    def setup_audio(self):
        """Initialize audio for continuous listening"""
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.frame_length = 512  # Porcupine frame length
        
    async def continuous_listening(self):
        """Main loop: listen for wake word, then process command"""
        print("👂 Listening for 'Hey OpenClaw'...")
        
        if not self.porcupine:
            print("❌ Wake word detection not available")
            return
        
        stream = self.audio.open(
            rate=self.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.frame_length
        )
        
        try:
            while True:
                # Read audio frame
                pcm = stream.read(self.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.frame_length, pcm)
                
                # Check for wake word
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    print("🎯 Wake word detected!")
                    await self.handle_voice_command()
                
                # Allow other coroutines to run
                await asyncio.sleep(0.001)
                
        except KeyboardInterrupt:
            print("👋 Stopping...")
        finally:
            stream.close()
            if self.porcupine:
                self.porcupine.delete()
    
    async def handle_voice_command(self):
        """Process voice command after wake word detection"""
        print("🔴 Listening for command...")
        
        # Capture speech with voice activity detection
        audio_file = await self.capture_command_audio()
        
        if audio_file:
            # Use the existing pipeline from the basic assistant
            from voice_assistant import OpenClawVoiceAssistant
            
            assistant = OpenClawVoiceAssistant()
            
            # Transcribe
            text = assistant.transcribe_audio(audio_file)
            
            if text:
                print(f"🗣️ Command: {text}")
                
                # Process with OpenClaw
                response = assistant.query_openclaw(text)
                
                # Respond with speech
                assistant.synthesize_speech(response)
            
            # Cleanup
            Path(audio_file).unlink()
        
        print("👂 Listening for 'Hey OpenClaw'...")
    
    async def capture_command_audio(self, max_silence=3):
        """Capture speech after wake word with voice activity detection"""
        import webrtcvad
        import wave
        import tempfile
        
        # Setup voice activity detection
        vad = webrtcvad.Vad(2)  # Aggressiveness 0-3
        
        frames = []
        silence_count = 0
        speech_detected = False
        
        stream = self.audio.open(
            rate=self.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=160  # 10ms frames for VAD
        )
        
        try:
            while True:
                frame = stream.read(160)
                frames.append(frame)
                
                # Check if frame contains speech
                is_speech = vad.is_speech(frame, self.sample_rate)
                
                if is_speech:
                    speech_detected = True
                    silence_count = 0
                else:
                    if speech_detected:  # Only count silence after speech starts
                        silence_count += 1
                
                # Stop after max silence (3 seconds = 300 frames of 10ms)
                if speech_detected and silence_count > max_silence * 100:
                    break
                
                # Safety timeout (10 seconds total)
                if len(frames) > 1000:
                    break
                    
        finally:
            stream.close()
        
        if not speech_detected:
            print("❌ No speech detected")
            return None
        
        # Save audio to file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            return f.name

# Alternative implementations for different wake word solutions:

class SnowboyWakeWord:
    """Snowboy wake word detection (deprecated but free)"""
    
    def __init__(self):
        # Snowboy is no longer maintained, but code would look like:
        # import snowboydecoder
        # self.detector = snowboydecoder.HotwordDetector("hey-openclaw.pmdl")
        pass
    
    def detect(self, audio_data):
        # Would return True if wake word detected
        pass

class CustomTensorFlowWakeWord:
    """Custom TensorFlow wake word model"""
    
    def __init__(self):
        # Load custom trained TensorFlow model
        # self.model = tf.keras.models.load_model('hey_openclaw_model.h5')
        pass
    
    def detect(self, audio_data):
        # Process audio through neural network
        # Return confidence score
        pass

# Example usage and setup instructions:

def setup_porcupine_wake_word():
    """
    Setup instructions for Porcupine wake word detection:
    
    1. Sign up at https://console.picovoice.ai/
    2. Get your access key
    3. Either:
       a) Use built-in keywords (hey google, alexa, etc.) for testing
       b) Train custom "Hey OpenClaw" model using Picovoice Console
    4. Download the .ppn model file
    5. Update the config with your access key and model path
    """
    print("""
    🔧 Porcupine Setup Instructions:
    
    1. Go to https://console.picovoice.ai/
    2. Sign up for account (free tier available)
    3. Get your Access Key
    4. Train custom wake word:
       - Phrase: "Hey OpenClaw"
       - Language: English
       - Download .ppn file
    5. Update configuration:
       - access_key: 'your-key-here'
       - keyword_paths: ['path/to/hey-openclaw.ppn']
    
    Cost: $10/month for commercial use
    Accuracy: Very high (95%+)
    Latency: ~100ms
    """)

def setup_alternative_solutions():
    """Alternative wake word solutions"""
    print("""
    🔄 Alternative Wake Word Solutions:
    
    1. Snowboy (Free, deprecated):
       - No longer maintained
       - Community models available
       - Lower accuracy than Porcupine
    
    2. Custom TensorFlow:
       - Train your own model
       - Requires ML expertise
       - Completely free
       - Most customizable
    
    3. OpenWakeWord (New, promising):
       - Open source
       - Pre-trained models
       - pip install openwakeword
    
    4. Precise (Mycroft):
       - Open source
       - Good accuracy
       - Requires training
    """)

if __name__ == "__main__":
    print("🎯 Wake Word Implementation Template")
    print("=" * 40)
    
    print("\nThis is a template for adding wake word detection to the OpenClaw Voice Assistant.")
    print("It's not functional yet - you need to set up Porcupine or another wake word solution.")
    
    setup_porcupine_wake_word()
    
    print("\nFor immediate testing, use the basic voice assistant:")
    print("python3 voice_assistant.py")