# OpenClaw Voice Assistant Implementation Plan

## System Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   Microphone    │ -> │ Wake Word    │ -> │ Audio       │
│                 │    │ Detection    │    │ Capture     │
└─────────────────┘    └──────────────┘    └─────────────┘
                                                   │
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   Speaker       │ <- │ ElevenLabs   │ <- │ OpenClaw    │
│                 │    │ TTS          │    │ Gateway     │
└─────────────────┘    └──────────────┘    └─────────────┘
                                                   │
                              ┌──────────────┐    │
                              │ Whisper STT  │ <- │
                              └──────────────┘    │
                                                  │
                              ┌──────────────┐    │
                              │ Audio Buffer │ <- │
                              └──────────────┘
```

## Components

### 1. Wake Word Detection
**Options:**
- **Porcupine** (Picovoice) - Most reliable, $10/mo for commercial use
- **Snowboy** - Open source but deprecated
- **Custom TensorFlow** - Build your own "Hey OpenClaw" model

**Recommendation:** Porcupine for reliability

### 2. Audio Processing
- **pyaudio** - Audio I/O
- **webrtcvad** - Voice activity detection
- **pydub** - Audio manipulation

### 3. Speech Recognition
- **OpenAI Whisper** (local) - Already available
- **Faster-Whisper** - Optimized version, 4x faster

### 4. Text-to-Speech
- **ElevenLabs API** - Already configured
- **Local alternatives:** piper, espeak (lower quality)

### 5. OpenClaw Integration
- **Gateway API** - HTTP requests to localhost:18789
- **Session management** - Maintain conversation context

## Hardware Requirements

### Minimum (Desktop)
- **USB microphone** - Blue Yeti, Audio-Technica ATR2100x-USB
- **Speakers** - Any decent desktop speakers
- **Processing** - M4 Mac Mini (sufficient)

### Optimal (Always-On)
- **Raspberry Pi 5** - $75 + accessories
- **ReSpeaker HAT** - $25, 4-mic array with noise cancellation
- **Good speaker** - $50-100
- **SD card** - 64GB+

### Professional (Best Experience)
- **Seeed reTerminal** - $195, built-in display + good audio
- **USB microphone array** - $100-200
- **Dedicated speakers** - $100-300

## Software Implementation

### Core Voice Assistant (Python)
```python
#!/usr/bin/env python3
"""
OpenClaw Voice Assistant
Handles wake word detection, speech recognition, and TTS
"""

import asyncio
import json
import requests
import pyaudio
import wave
import io
import tempfile
from pathlib import Path

class OpenClawVoice:
    def __init__(self, config_file="voice_config.json"):
        self.config = self.load_config(config_file)
        self.setup_audio()
        self.setup_apis()
        
    def setup_audio(self):
        self.audio = pyaudio.PyAudio()
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        
    async def listen_for_wake_word(self):
        """Continuous listening for 'Hey OpenClaw'"""
        # Porcupine integration here
        pass
        
    async def capture_speech(self, duration=5):
        """Capture audio after wake word detection"""
        frames = []
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        # Voice activity detection loop
        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)
            
        stream.stop_stream()
        stream.close()
        
        # Save to temp file for Whisper
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            return f.name
            
    async def transcribe_audio(self, audio_file):
        """Use Whisper to convert speech to text"""
        import subprocess
        result = subprocess.run([
            'whisper', audio_file, 
            '--model', 'medium',
            '--output_format', 'txt',
            '--output_dir', '/tmp'
        ], capture_output=True, text=True)
        
        # Parse Whisper output
        txt_file = Path(audio_file).with_suffix('.txt')
        if txt_file.exists():
            return txt_file.read_text().strip()
        return None
        
    async def query_openclaw(self, text):
        """Send query to OpenClaw gateway"""
        url = f"http://localhost:{self.config['openclaw_port']}/api/chat"
        headers = {
            'Authorization': f"Bearer {self.config['openclaw_token']}",
            'Content-Type': 'application/json'
        }
        data = {
            'message': text,
            'sessionKey': 'voice-assistant'
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['response']
        return "Sorry, I couldn't process that request."
        
    async def synthesize_speech(self, text):
        """Convert text to speech using ElevenLabs"""
        url = "https://api.elevenlabs.io/v1/text-to-speech/your-voice-id"
        headers = {
            'xi-api-key': self.config['elevenlabs_key'],
            'Content-Type': 'application/json'
        }
        data = {
            'text': text,
            'model_id': 'eleven_monolingual_v1',
            'voice_settings': {
                'stability': 0.7,
                'similarity_boost': 0.8
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.content
        return None
        
    async def play_audio(self, audio_data):
        """Play audio through speakers"""
        # Implementation depends on your audio setup
        pass
        
    async def main_loop(self):
        """Main conversation loop"""
        print("🎙️ OpenClaw Voice Assistant started")
        print("Say 'Hey OpenClaw' to begin...")
        
        while True:
            # Wait for wake word
            await self.listen_for_wake_word()
            print("👂 Listening...")
            
            # Capture speech
            audio_file = await self.capture_speech()
            
            # Transcribe
            text = await self.transcribe_audio(audio_file)
            if text:
                print(f"🗣️ You said: {text}")
                
                # Query OpenClaw
                response = await self.query_openclaw(text)
                print(f"🤖 OpenClaw: {response}")
                
                # Convert to speech and play
                audio = await self.synthesize_speech(response)
                if audio:
                    await self.play_audio(audio)
            
            # Cleanup
            Path(audio_file).unlink()

if __name__ == "__main__":
    assistant = OpenClawVoice()
    asyncio.run(assistant.main_loop())
```

### Configuration File
```json
{
  "openclaw_port": 18789,
  "openclaw_token": "your-gateway-token",
  "elevenlabs_key": "your-elevenlabs-key",
  "wake_word_sensitivity": 0.7,
  "speech_timeout": 5,
  "voice_id": "your-preferred-voice"
}
```

## Development Phases

### Phase 1: Basic Pipeline (Week 1)
- ✅ Audio capture working
- ✅ Whisper transcription
- ✅ OpenClaw API integration
- ✅ ElevenLabs synthesis
- ✅ Audio playback

### Phase 2: Wake Word (Week 2)
- ✅ Porcupine integration
- ✅ Continuous listening
- ✅ Voice activity detection
- ✅ Background operation

### Phase 3: Enhancement (Week 3)
- ✅ Conversation context
- ✅ Interruption handling
- ✅ Audio quality optimization
- ✅ Error handling

### Phase 4: Polish (Week 4)
- ✅ Hardware optimization
- ✅ Performance tuning
- ✅ Installation scripts
- ✅ Documentation

## Cost Breakdown

### Development
- **Porcupine license:** $10/month
- **Hardware (Pi setup):** $150-250 one-time
- **Development time:** ~20-30 hours

### Operating Costs
- **ElevenLabs:** ~$5-15/month (based on usage)
- **Porcupine:** $10/month
- **Total:** ~$15-25/month

### Comparison to Alternatives
- **Amazon Echo:** $50 + privacy concerns + limited customization
- **Google Home:** $30 + privacy concerns + no OpenClaw integration
- **Custom solution:** $200 initial + $20/month + full control

## Advanced Features (Future)

### Multi-Room Support
- **Multiple microphones** throughout house
- **Distributed processing** via multiple Pi devices
- **Zone-based responses** (kitchen vs office commands)

### Context Awareness
- **Location detection** - different responses based on room
- **Time awareness** - different behavior during work hours
- **Activity detection** - respond differently during meetings

### Integration Extensions
- **Home automation** - "Hey OpenClaw, dim the lights"
- **Calendar integration** - "What's my next meeting?"
- **Email management** - "Read my urgent emails"
- **System control** - "Start my development environment"

### Security & Privacy
- **Local processing** - All speech stays on your network
- **Encrypted communications** - TLS to OpenClaw gateway
- **Wake word only** - No cloud processing until activated
- **Audio isolation** - Physical disconnect capability

## Next Steps

1. **Choose hardware platform** (Mac desktop vs Pi vs dedicated device)
2. **Set up development environment** (Python, dependencies)
3. **Build basic pipeline** (no wake word, manual trigger)
4. **Add wake word detection** (Porcupine trial)
5. **Optimize and deploy** (continuous operation)

Would you like me to start with Phase 1 and build the basic pipeline?