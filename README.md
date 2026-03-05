# OpenClaw Voice Assistant

A custom voice assistant that provides natural speech interaction with OpenClaw. Say your commands, get AI responses through high-quality speech synthesis.

![Voice Assistant Demo](https://img.shields.io/badge/Status-Ready%20to%20Test-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey)

## 🎯 What This Does

Transform your OpenClaw experience with voice commands:

```
You speak → Whisper (local) → OpenClaw AI → ElevenLabs → Speakers
```

- **Voice Input**: Record questions naturally
- **AI Processing**: Full OpenClaw integration with all your tools and skills  
- **Speech Output**: High-quality ElevenLabs text-to-speech
- **Privacy First**: Speech recognition happens locally (no cloud)
- **Zero Latency**: Direct integration with your OpenClaw gateway

## ✅ Quick Start

### Manual Mode (Ready Now)
```bash
# 1. Install dependencies
chmod +x setup_voice_assistant.sh
./setup_voice_assistant.sh

# 2. Test components
python3 test_voice_components.py

# 3. Start voice assistant
python3 voice_assistant.py
```

### Wake Word Mode ("Hey OpenClaw")
```bash
# 1. Install wake word dependencies
chmod +x setup_wake_word.sh
./setup_wake_word.sh

# 2. Set up Porcupine (see WAKE_WORD_SETUP.md)
# 3. Test wake word detection
python3 test_wake_word.py

# 4. Start continuous assistant
python3 porcupine_voice_assistant.py
```

### 4. Use It
1. Press Enter to start recording
2. Speak your question: *"What's my schedule today?"*
3. Press Enter to stop recording
4. Listen to AI response through speakers
5. Type 'quit' to exit

## 🎙️ Demo Interaction

```
🎙️ OpenClaw Voice Assistant (Interactive Mode)
Press Enter to record (or 'quit' to exit): [Enter]

🔴 Recording... Press Enter to stop: [speak] "Check my email for anything urgent" [Enter]

🔄 Transcribing speech...
📝 You said: 'Check my email for anything urgent'
🤖 Asking OpenClaw: Check my email for anything urgent
🤖 Response: I found 2 urgent emails: one from your client about...
🔊 Generating speech...
✅ Speech generated successfully

Press Enter to record (or 'quit' to exit):
```

## 🏗️ System Architecture

### Current Implementation (Phase 1)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Microphone  │ -> │ Manual      │ -> │ Audio       │
│ Input       │    │ Recording   │    │ Buffer      │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Speaker     │ <- │ ElevenLabs  │ <- │ OpenClaw    │
│ Output      │    │ TTS         │    │ Gateway     │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
                   ┌─────────────┐    ┌─────────────┐
                   │ Whisper STT │ <- │ Speech      │
                   │ (Local)     │    │ Audio File  │
                   └─────────────┘    └─────────────┘
```

### Future Implementation (Phase 2)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Always-On   │ -> │ "Hey        │ -> │ Voice       │
│ Microphone  │    │ OpenClaw"   │    │ Command     │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🔧 Components

### Core Technologies
- **Speech Recognition**: OpenAI Whisper (local processing)
- **Wake Word Detection**: Porcupine by Picovoice (custom "Hey OpenClaw" model)
- **Voice Activity Detection**: WebRTC VAD (smart speech capture)
- **AI Processing**: OpenClaw Gateway API
- **Text-to-Speech**: ElevenLabs (high-quality synthesis)
- **Audio I/O**: PyAudio for microphone and speaker control

### Key Features
- ✅ **Local Speech Processing** - No cloud dependencies for transcription
- ✅ **Wake Word Detection** - "Hey OpenClaw" continuous listening (Porcupine)
- ✅ **OpenClaw Integration** - Full access to all your AI tools and skills
- ✅ **Voice Activity Detection** - Smart speech capture with automatic timeout
- ✅ **Conversation Context** - Maintains session state across interactions
- ✅ **High-Quality Voice** - ElevenLabs professional speech synthesis
- ✅ **Privacy Focused** - Audio processing stays on your machine
- ✅ **Dual Modes** - Manual recording or continuous "always listening"
- ✅ **Configurable** - Adjust sensitivity, timeouts, and audio settings

## 📋 Requirements

### System Requirements
- **Operating System**: macOS (Linux support coming)
- **Python**: 3.8 or later
- **RAM**: 4GB+ (for Whisper model)
- **Audio**: Microphone and speakers
- **OpenClaw**: Running gateway instance

### Dependencies
- `pyaudio` - Audio input/output
- `requests` - HTTP communication
- `openai-whisper` - Speech recognition
- OpenClaw gateway (running locally)
- ElevenLabs API key (configured in OpenClaw)

### Hardware Recommendations

| Setup | Cost | Description | Use Case |
|-------|------|-------------|----------|
| **Basic** | $0 | Built-in mic + speakers | Testing, casual use |
| **Good** | $50-100 | USB microphone + decent speakers | Daily use |
| **Better** | $150-250 | Raspberry Pi + microphone array | Always-on assistant |
| **Professional** | $300-500 | Seeed reTerminal + studio mic | Production deployment |

## ⚙️ Configuration

Configuration is stored in `~/.openclaw/voice_config.json`:

```json
{
  "openclaw_port": 18789,
  "openclaw_token": "auto-detected-from-config",
  "elevenlabs_key": "auto-detected-from-config", 
  "whisper_model": "medium",
  "speech_timeout": 10,
  "sample_rate": 16000,
  "chunk_size": 1024
}
```

### Whisper Model Options
- `tiny` - Fastest (39 MB), English-only, lower accuracy
- `base` - Fast (74 MB), multilingual, good for testing
- `small` - Balanced (244 MB), multilingual, good accuracy
- `medium` - **Recommended** (769 MB), multilingual, best balance
- `large` - Best accuracy (1550 MB), multilingual, slower

## 🔄 Development Roadmap

### ✅ Phase 1: Manual Mode (Complete)
- Manual recording trigger (press Enter)
- Whisper speech recognition
- OpenClaw API integration
- ElevenLabs text-to-speech
- Configuration management
- Error handling and recovery

### 🔄 Phase 2: Wake Word Detection (Next)
- "Hey OpenClaw" activation phrase
- Continuous background listening
- Voice activity detection
- Porcupine integration ($10/month)
- Always-on operation mode

### 🔮 Phase 3: Advanced Features (Future)
- Multi-room support (multiple microphones)
- Context awareness (location, time, activity)
- Home automation integration
- Custom voice training
- Interruption handling
- Conversation memory

### 🔒 Phase 4: Privacy & Security (Future)
- Local-only processing options
- Encrypted communications
- Physical disconnect switch
- Audio isolation modes
- Security audit capabilities

## 🚀 Usage Examples

### Basic Commands
```bash
# Start the assistant
python3 voice_assistant.py

# Test individual components  
python3 test_voice_components.py

# Run setup script
./setup_voice_assistant.sh
```

### Voice Commands (Examples)
- *"What's my schedule today?"*
- *"Check for urgent emails"*
- *"What's the weather like?"*
- *"Create a reminder for 3 PM"*
- *"Search for AI consulting projects"*
- *"Generate a project summary"*

### OpenClaw Integration
The voice assistant has full access to your OpenClaw ecosystem:
- All configured AI models
- Installed skills and tools
- Memory and context
- File system access
- Browser automation
- Message sending capabilities

## 🧪 Testing & Troubleshooting

### Component Testing
```bash
python3 test_voice_components.py
```

This tests:
- ✅ Microphone input
- ✅ Whisper transcription
- ✅ OpenClaw connectivity  
- ✅ OpenClaw API queries
- ✅ Text-to-speech output

### Common Issues

**Microphone Permission (macOS)**
```bash
# System Preferences → Security & Privacy → Microphone
# Enable access for Terminal/iTerm
```

**OpenClaw Connection Issues**
```bash
# Check if OpenClaw is running
curl http://localhost:18789/api/status

# Start OpenClaw
openclaw gateway start
```

**Audio Device Problems**
```bash
# List available audio devices
python3 -c "
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'{i}: {info[\"name\"]}')
p.terminate()
"
```

**Whisper Issues**
```bash
# Test Whisper directly
whisper test_audio.wav --model medium

# Reinstall if needed
brew reinstall openai-whisper
```

## 💰 Cost Analysis

### Development Costs
| Component | Setup Cost | Monthly Cost |
|-----------|------------|--------------|
| Software Development | Free | $0 |
| Manual Mode | Free | $0 |
| Whisper (Local) | Free | $0 |
| ElevenLabs TTS | Free | $5-15 |
| Porcupine Wake Word | Free trial | $10 |
| **Manual Mode Total** | **$0** | **$5-15** |
| **Wake Word Mode Total** | **$0** | **$15-25** |

### Hardware Costs
| Option | Initial Cost | Description |
|--------|--------------|-------------|
| Desktop Setup | $0 | Use existing Mac + USB mic |
| Pi Setup | $150-250 | Raspberry Pi + accessories |
| Professional | $300-500 | Dedicated hardware + studio gear |

### Comparison to Alternatives
| Solution | Cost | Privacy | Customization | OpenClaw Integration |
|----------|------|---------|---------------|---------------------|
| **Custom Assistant** | $15-25/mo | ✅ High | ✅ Full | ✅ Native |
| Amazon Echo | $50 + privacy | ❌ Low | ❌ Limited | ❌ None |
| Google Home | $30 + privacy | ❌ Low | ❌ Limited | ❌ None |
| Apple HomePod | $99 + privacy | ⚠️ Medium | ❌ Limited | ❌ None |

## 🔒 Privacy & Security

### Local Processing
- **Speech Recognition**: Whisper runs locally (no cloud)
- **Audio Storage**: Temporary files only, automatically deleted
- **Network Traffic**: Only OpenClaw API calls (local)
- **Data Retention**: No conversation logging by default

### Security Features
- Audio input only when manually triggered
- Encrypted communication with OpenClaw gateway
- No persistent audio recording
- Configurable data retention policies
- Local-only speech processing

### Privacy Controls
- Disable wake word for manual-only mode
- Configure audio file cleanup policies
- Monitor network traffic and API calls
- Physical microphone disconnect option

## 🤝 Contributing

### Development Setup
```bash
git clone https://github.com/rdreilly58/openclaw-voice-assistant.git
cd openclaw-voice-assistant
./setup_voice_assistant.sh
```

### Adding Features
1. Fork the repository
2. Create a feature branch
3. Test thoroughly with `test_voice_components.py`
4. Submit a pull request

### Wake Word Implementation
See `wake_word_implementation.py` for:
- Porcupine integration template
- Voice activity detection examples
- Continuous listening architecture
- Alternative wake word solutions

## 📚 Advanced Topics

### Custom Wake Words
```python
# Porcupine custom wake word training
# 1. Sign up at https://console.picovoice.ai/
# 2. Train "Hey OpenClaw" model
# 3. Download .ppn file
# 4. Configure in wake_word_implementation.py
```

### Voice Activity Detection
```python
import webrtcvad

def setup_vad():
    vad = webrtcvad.Vad(2)  # Aggressiveness 0-3
    return vad

def detect_speech(audio_frame):
    return vad.is_speech(audio_frame, sample_rate=16000)
```

### Multi-Room Architecture
```python
# Distributed microphones concept
class MultiRoomVoiceAssistant:
    def __init__(self):
        self.zones = {
            'kitchen': MicrophoneArray(location='kitchen'),
            'office': MicrophoneArray(location='office'),
            'bedroom': MicrophoneArray(location='bedroom')
        }
```

## 📖 Documentation

### API Reference
- `voice_assistant.py` - Manual recording mode assistant
- `porcupine_voice_assistant.py` - Wake word continuous mode assistant  
- `test_voice_components.py` - Basic component testing suite
- `test_wake_word.py` - Wake word detection testing
- `setup_voice_assistant.sh` - Basic dependency installer
- `setup_wake_word.sh` - Wake word detection setup
- `WAKE_WORD_SETUP.md` - Complete Porcupine setup guide

### Configuration Files
- `~/.openclaw/voice_config.json` - Voice assistant settings
- `~/.openclaw/openclaw.json` - OpenClaw gateway configuration

### Log Files
- Console output for real-time debugging
- OpenClaw gateway logs for API interactions
- Component test results for troubleshooting

## 🆘 Support

### Getting Help
1. Run component tests: `python3 test_voice_components.py`
2. Check OpenClaw status: `openclaw status`
3. Verify audio permissions in System Preferences
4. Review configuration in `~/.openclaw/voice_config.json`

### Common Solutions
- **No audio input**: Check microphone permissions
- **OpenClaw errors**: Restart gateway with `openclaw gateway restart`
- **Speech recognition fails**: Try different Whisper model
- **TTS not working**: Verify ElevenLabs API key in OpenClaw config

### Reporting Issues
Include in bug reports:
- Output from `test_voice_components.py`
- Your `voice_config.json` (redact keys)
- OpenClaw version: `openclaw version`
- System information: macOS version, Python version

## 🏆 Credits

**Author**: Robert D. Reilly  
**Email**: rdreilly2010@gmail.com  
**GitHub**: [@rdreilly58](https://github.com/rdreilly58)  

**Technologies**:
- [OpenAI Whisper](https://openai.com/research/whisper) - Speech recognition
- [ElevenLabs](https://elevenlabs.io) - Text-to-speech synthesis  
- [OpenClaw](https://openclaw.ai) - AI assistant platform
- [Porcupine](https://picovoice.ai/porcupine/) - Wake word detection
- [PyAudio](https://pypi.org/project/PyAudio/) - Audio I/O

**License**: MIT License

---

**Ready to give your OpenClaw assistant a voice?** 🎙️

Start with: `./setup_voice_assistant.sh`