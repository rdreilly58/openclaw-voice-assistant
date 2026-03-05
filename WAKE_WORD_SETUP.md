# Wake Word Setup Guide

This guide walks you through setting up "Hey OpenClaw" wake word detection using Porcupine.

## Quick Setup

```bash
# 1. Install wake word dependencies
./setup_wake_word.sh

# 2. Get Porcupine access key (see below)

# 3. Test wake word detection
python3 test_wake_word.py

# 4. Run continuous assistant
python3 porcupine_voice_assistant.py
```

## Step-by-Step Porcupine Setup

### 1. Create Picovoice Account

1. **Go to**: https://console.picovoice.ai/
2. **Sign up** for a free account
3. **Verify** your email address
4. **Login** to the Picovoice Console

### 2. Get Your Access Key

1. In the Picovoice Console, go to the **"Account"** section
2. Copy your **Access Key** (looks like: `JVYyTn3h9Qz...`)
3. Keep this secure - you'll need it for configuration

### 3. Train Custom Wake Word

#### Option A: Use Pre-trained Model (Recommended for Testing)
- The assistant can use built-in keywords like "computer" for initial testing
- Skip to step 4 to test with "computer" as your wake word

#### Option B: Train Custom "Hey OpenClaw" Model

1. **Go to**: Wake Word section in Picovoice Console
2. **Click**: "Create Wake Word"
3. **Configure**:
   - **Wake word**: `Hey OpenClaw`
   - **Language**: English
   - **Platform**: Linux (works for macOS too)

4. **Training Process**:
   - Read the phrase naturally 3-5 times
   - Speak clearly but naturally
   - Use your normal speaking voice
   - Avoid background noise during recording

5. **Download Model**:
   - Wait for training to complete (usually 2-10 minutes)
   - Download the `.ppn` model file
   - Save as `hey-openclaw.ppn` in your project directory

### 4. Configure Access Key

Edit `~/.openclaw/voice_config.json`:

```json
{
  "porcupine_access_key": "YOUR_ACCESS_KEY_HERE",
  "porcupine_model_path": "hey-openclaw.ppn",
  "porcupine_sensitivity": 0.7,
  "command_timeout": 10.0,
  "activation_sound": true,
  "vad_aggressiveness": 2
}
```

**Configuration Options:**

- **`porcupine_access_key`**: Your Picovoice access key
- **`porcupine_model_path`**: Path to your .ppn model file
- **`porcupine_sensitivity`**: 0.0-1.0 (0.7 recommended)
  - Lower = fewer false positives, might miss real wake words
  - Higher = more sensitive, might trigger accidentally
- **`command_timeout`**: How long to listen after wake word (seconds)
- **`activation_sound`**: Play beep when wake word detected
- **`vad_aggressiveness`**: Voice activity detection level (0-3)

### 5. Test Installation

```bash
# Test all components
python3 test_wake_word.py

# Test wake word detection specifically
python3 test_wake_word.py
# Follow prompts for live wake word test
```

### 6. Run Continuous Assistant

```bash
python3 porcupine_voice_assistant.py
```

**Usage:**
1. Wait for "Listening for 'Hey OpenClaw'..." message
2. Say "Hey OpenClaw" (or "computer" if using built-in)
3. Wait for activation beep
4. Speak your command naturally
5. Listen to AI response
6. Assistant returns to listening mode

## Troubleshooting

### "Invalid Access Key" Error

**Problem**: Porcupine can't validate your access key

**Solutions**:
1. Double-check access key in config file (no extra spaces/quotes)
2. Verify account is active at https://console.picovoice.ai/
3. Check internet connection
4. Try regenerating access key in console

### Wake Word Not Detected

**Problem**: Saying wake word doesn't trigger assistant

**Solutions**:
1. **Lower sensitivity**: Change `porcupine_sensitivity` to 0.5 or 0.6
2. **Speak clearly**: Enunciate "Hey OpenClaw" distinctly
3. **Check microphone**: Ensure microphone is working and not muted
4. **Reduce background noise**: Test in quiet environment
5. **Retrain model**: If using custom model, retrain with more samples

### Too Many False Triggers

**Problem**: Assistant activates without wake word

**Solutions**:
1. **Raise sensitivity**: Change `porcupine_sensitivity` to 0.8 or 0.9
2. **Retrain model**: Include negative examples (other speech)
3. **Check for audio feedback**: Ensure speakers don't feed into microphone
4. **Test environment**: Try in different room/noise conditions

### "Model Not Found" Error

**Problem**: Can't load custom wake word model

**Solutions**:
1. **Check file path**: Ensure `hey-openclaw.ppn` is in correct location
2. **Use absolute path**: Try full path like `/path/to/hey-openclaw.ppn`
3. **Verify download**: Re-download model from Picovoice Console
4. **Check permissions**: Ensure file is readable

### Audio Issues

**Problem**: No audio input or poor quality

**Solutions**:
1. **Check microphone permissions**: 
   - macOS: System Preferences → Security & Privacy → Microphone
   - Enable for Terminal/iTerm
2. **Test microphone**: Record audio in another app first
3. **Adjust input levels**: Check system audio input levels
4. **Try different microphone**: USB mic often works better than built-in

### High CPU Usage

**Problem**: Continuous listening uses too much CPU

**Solutions**:
1. **Use smaller Whisper model**: Change to "small" or "base" model
2. **Adjust frame processing**: Modify audio processing frequency
3. **Hardware upgrade**: Consider dedicated device like Raspberry Pi
4. **Pause when not needed**: Add manual disable/enable option

## Advanced Configuration

### Custom Sensitivity Per Environment

```json
{
  "sensitivity_profiles": {
    "quiet": 0.5,
    "normal": 0.7,
    "noisy": 0.9
  }
}
```

### Multiple Wake Words

```json
{
  "wake_words": [
    {
      "phrase": "Hey OpenClaw",
      "model_path": "hey-openclaw.ppn",
      "sensitivity": 0.7
    },
    {
      "phrase": "Computer",
      "built_in": true,
      "sensitivity": 0.8
    }
  ]
}
```

### Voice Activity Detection Tuning

```json
{
  "vad_config": {
    "aggressiveness": 2,
    "frame_duration_ms": 10,
    "padding_duration_ms": 300,
    "ratio_threshold": 0.75
  }
}
```

## Performance Optimization

### CPU Usage
- **Wake word detection**: ~1-2% CPU (always running)
- **Speech recognition**: ~20-50% CPU (only when triggered)
- **Response generation**: Depends on OpenClaw configuration

### Memory Usage
- **Porcupine model**: ~1-3MB
- **Whisper model**: 244MB-1.5GB (loaded on demand)
- **Audio buffers**: ~5-10MB

### Latency Breakdown
- **Wake word detection**: ~100ms
- **Command capture**: 1-10 seconds (until silence)
- **Speech transcription**: 1-5 seconds
- **AI response**: 2-10 seconds (OpenClaw processing)
- **Speech synthesis**: 1-3 seconds
- **Total**: 5-30 seconds typical

## Alternative Solutions

### Free Alternatives

**Snowboy (Deprecated)**
- No longer maintained
- Community models available
- Lower accuracy than Porcupine

**OpenWakeWord**
- Open source
- Pre-trained models
- Install: `pip install openwakeword`

**Custom TensorFlow**
- Complete control
- Requires ML expertise
- No monthly fees

### Hardware Alternatives

**Raspberry Pi Setup**
- Always-on dedicated device
- Better microphone arrays available
- Lower power consumption
- Remote processing capability

**USB Microphone Arrays**
- Better wake word detection accuracy
- Noise cancellation
- Directional audio
- Professional audio quality

## Cost Analysis

### Porcupine Pricing
- **Personal use**: Free tier (limited usage)
- **Commercial use**: $10/month per device
- **Custom models**: Included in subscription
- **High volume**: Contact sales for enterprise pricing

### Total Monthly Cost
- **Porcupine**: $10/month
- **ElevenLabs TTS**: $5-15/month
- **OpenClaw**: Free (self-hosted)
- **Total**: $15-25/month

### One-time Hardware Costs
- **Basic**: $0 (use existing computer + mic)
- **Good**: $50-100 (USB microphone)
- **Better**: $150-250 (Raspberry Pi + microphone array)
- **Professional**: $300-500 (Dedicated hardware + studio mic)

## Security Considerations

### Local Processing
- Wake word detection runs locally
- No audio sent to cloud until triggered
- Custom models stored on device
- Configurable privacy levels

### Network Security
- Only OpenClaw API calls leave device
- All speech processing stays local
- Configurable endpoint restrictions
- Optional offline-only mode

### Access Control
- Physical access to device = voice access
- No built-in authentication
- Consider physical security for sensitive environments
- Option to disable wake word when not in use

## Getting Help

### Common Issues
1. **Run diagnostics**: `python3 test_wake_word.py`
2. **Check logs**: Look for error messages in console output
3. **Test components**: Verify each part works individually
4. **Check config**: Validate JSON syntax and values

### Support Resources
- **Picovoice Documentation**: https://picovoice.ai/docs/
- **OpenClaw Community**: https://discord.com/invite/clawd
- **Project Issues**: GitHub issues on the repository

### Debug Mode
```bash
# Run with verbose output
PYTHONPATH=. python3 -u porcupine_voice_assistant.py
```

---

Ready to set up wake word detection? Start with: `./setup_wake_word.sh`