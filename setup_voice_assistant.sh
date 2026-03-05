#!/bin/bash

# OpenClaw Voice Assistant Setup Script

echo "🎙️ Setting up OpenClaw Voice Assistant"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "voice_assistant.py" ]; then
    echo "❌ voice_assistant.py not found"
    echo "Run this script from the workspace directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install Python 3"
    exit 1
fi

# Install pyaudio (can be tricky on macOS)
echo "🔧 Installing pyaudio..."
if command -v brew &> /dev/null; then
    # Use homebrew for easier pyaudio installation
    brew install portaudio
    pip3 install pyaudio
else
    # Try direct pip install
    pip3 install pyaudio
fi

# Install other dependencies
pip3 install requests pathlib

# Check if Whisper is installed
echo "🎧 Checking Whisper installation..."
if ! command -v whisper &> /dev/null; then
    echo "📥 Installing OpenAI Whisper..."
    if command -v brew &> /dev/null; then
        brew install openai-whisper
    else
        pip3 install openai-whisper
    fi
else
    echo "✅ Whisper already installed"
fi

# Check if OpenClaw is running
echo "🤖 Checking OpenClaw status..."
if curl -s http://localhost:18789/api/status > /dev/null 2>&1; then
    echo "✅ OpenClaw is running"
else
    echo "⚠️ OpenClaw not responding on localhost:18789"
    echo "   Make sure OpenClaw is running: openclaw gateway start"
fi

# Make the script executable
chmod +x voice_assistant.py

# Test audio devices
echo "🎙️ Testing audio devices..."
python3 -c "
import pyaudio
p = pyaudio.PyAudio()
print(f'Audio devices found: {p.get_device_count()}')
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'  Input device {i}: {info[\"name\"]}')
p.terminate()
" 2>/dev/null || echo "⚠️ Could not test audio devices"

echo ""
echo "🎯 Setup complete!"
echo ""
echo "To test the voice assistant:"
echo "  python3 voice_assistant.py"
echo ""
echo "If you encounter issues:"
echo "  1. Check that your microphone is working"
echo "  2. Make sure OpenClaw is running"
echo "  3. Verify ElevenLabs TTS is configured in OpenClaw"
echo ""
echo "Configuration file will be created at:"
echo "  ~/.openclaw/voice_config.json"