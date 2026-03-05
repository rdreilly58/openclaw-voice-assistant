#!/bin/bash

# OpenClaw Voice Assistant - Wake Word Setup Script

echo "🎙️ Setting up Wake Word Detection for OpenClaw Voice Assistant"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "porcupine_voice_assistant.py" ]; then
    echo "❌ porcupine_voice_assistant.py not found"
    echo "Run this script from the openclaw-voice-assistant directory"
    exit 1
fi

# Install basic dependencies first
echo "📦 Installing basic dependencies..."
if [ ! -f "setup_voice_assistant.sh" ]; then
    echo "❌ setup_voice_assistant.sh not found"
    exit 1
fi

./setup_voice_assistant.sh

# Install wake word specific dependencies
echo ""
echo "🎯 Installing wake word detection dependencies..."

# Install Porcupine
echo "📥 Installing Porcupine (Picovoice)..."
pip3 install pvporcupine

# Install WebRTC VAD for better speech detection
echo "📥 Installing WebRTC Voice Activity Detection..."
pip3 install webrtcvad

# Check installations
echo ""
echo "✅ Checking installations..."
python3 -c "
try:
    import pvporcupine
    print('✅ Porcupine installed successfully')
except ImportError:
    print('❌ Porcupine installation failed')

try:
    import webrtcvad
    print('✅ WebRTC VAD installed successfully')
except ImportError:
    print('❌ WebRTC VAD installation failed')
"

echo ""
echo "🔧 Porcupine Setup Instructions:"
echo "================================"
echo ""
echo "1. Sign up for Picovoice (free tier available):"
echo "   https://console.picovoice.ai/"
echo ""
echo "2. Get your Access Key from the console"
echo ""
echo "3. Train your custom wake word:"
echo "   - Go to 'Wake Word' section"
echo "   - Create new wake word: 'Hey OpenClaw'"
echo "   - Language: English"
echo "   - Follow the training process"
echo "   - Download the .ppn model file"
echo ""
echo "4. Configure the assistant:"
echo "   - Place the .ppn file in this directory"
echo "   - Update ~/.openclaw/voice_config.json with:"
echo "     {"
echo "       \"porcupine_access_key\": \"your-access-key-here\","
echo "       \"porcupine_model_path\": \"hey-openclaw.ppn\","
echo "       \"porcupine_sensitivity\": 0.7"
echo "     }"
echo ""
echo "5. Test with built-in keyword (before custom training):"
echo "   python3 porcupine_voice_assistant.py"
echo "   (Will use 'computer' as temporary wake word)"
echo ""

# Create a sample config file
config_file="$HOME/.openclaw/voice_config.json"
if [ ! -f "$config_file" ]; then
    echo "📝 Creating sample configuration..."
    mkdir -p "$(dirname "$config_file")"
    cat > "$config_file" << 'EOF'
{
  "openclaw_port": 18789,
  "openclaw_token": "auto-detected",
  "elevenlabs_key": "auto-detected",
  "whisper_model": "medium",
  "speech_timeout": 10,
  "sample_rate": 16000,
  "chunk_size": 1024,
  "porcupine_access_key": "ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE",
  "porcupine_model_path": "hey-openclaw.ppn",
  "porcupine_sensitivity": 0.7,
  "wake_word_timeout": 5.0,
  "command_timeout": 10.0,
  "activation_sound": true,
  "vad_aggressiveness": 2
}
EOF
    echo "✅ Sample config created: $config_file"
fi

echo ""
echo "🧪 Testing wake word detection..."
echo "================================"

# Test Porcupine with built-in keyword
python3 -c "
import sys
try:
    import pvporcupine
    
    # Test with built-in keyword
    try:
        porcupine = pvporcupine.create(keywords=['computer'])
        porcupine.delete()
        print('✅ Porcupine wake word detection ready')
        print('   You can test with the built-in \"computer\" keyword')
    except Exception as e:
        print(f'⚠️ Porcupine test with built-in keyword failed: {e}')
        print('   You will need a valid access key from Picovoice')
        
except ImportError:
    print('❌ Porcupine not properly installed')
    sys.exit(1)
"

echo ""
echo "🎯 Next Steps:"
echo "============="
echo ""
echo "For immediate testing (built-in keyword):"
echo "  python3 porcupine_voice_assistant.py"
echo "  Say 'computer' instead of 'Hey OpenClaw'"
echo ""
echo "For custom 'Hey OpenClaw' wake word:"
echo "  1. Get Picovoice access key"
echo "  2. Train custom wake word model"
echo "  3. Update ~/.openclaw/voice_config.json"
echo "  4. Run: python3 porcupine_voice_assistant.py"
echo ""
echo "Cost: $10/month for commercial use (free tier available)"
echo "Accuracy: 95%+ with proper training"
echo ""

# Make the wake word assistant executable
chmod +x porcupine_voice_assistant.py

echo "✅ Wake word setup complete!"