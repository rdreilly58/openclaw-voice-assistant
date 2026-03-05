#!/bin/bash
# Setup Desk-Optimized OpenClaw Voice Assistant

set -e

echo "🖥️ Setting up Desk-Optimized OpenClaw Voice Assistant..."
echo "=================================================="

# Change to the script directory
cd "$(dirname "$0")"

# Check if we're in the right place
if [ ! -f "desk_optimized_assistant.py" ]; then
    echo "❌ desk_optimized_assistant.py not found. Run from the correct directory."
    exit 1
fi

echo ""
echo "📦 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi
echo "✅ Python3 found"

# Check pip packages (with proper macOS handling)
echo "🔄 Installing/checking Python dependencies..."

# Function to check and install Python package
install_python_package() {
    local package=$1
    local import_name=${2:-$1}
    
    python3 -c "import $import_name" 2>/dev/null && {
        echo "✅ $package already available"
        return 0
    }
    
    echo "⚠️ $package not found - installing..."
    
    # Try user install first
    if pip3 install --user --break-system-packages "$package" 2>/dev/null; then
        echo "✅ $package installed via pip (user)"
        return 0
    fi
    
    # Try without break-system-packages for older systems
    if pip3 install --user "$package" 2>/dev/null; then
        echo "✅ $package installed via pip (user)"
        return 0
    fi
    
    echo "❌ Failed to install $package"
    echo "Try: pip3 install --user --break-system-packages $package"
    return 1
}

# Install required packages
install_python_package "pyaudio" || echo "⚠️ PyAudio may need manual installation"
install_python_package "webrtcvad" || echo "⚠️ WebRTC VAD may need manual installation"
install_python_package "psutil" || echo "⚠️ psutil may need manual installation"
install_python_package "requests" || echo "⚠️ requests may need manual installation"

# Check Porcupine
install_python_package "pvporcupine" || {
    echo "ℹ️ Porcupine not available - wake word will use fallback mode"
}

# Check Whisper
if ! command -v whisper &> /dev/null; then
    echo "⚠️ Whisper not found - trying to install..."
    install_python_package "openai-whisper" "whisper" || {
        echo "❌ Whisper installation failed"
        echo "Try: pip3 install --user --break-system-packages openai-whisper"
        exit 1
    }
else
    echo "✅ Whisper found"
fi

echo ""
echo "⚙️ Setting up configuration..."

# Create config directory if needed
mkdir -p ~/.openclaw

# Create basic desk configuration
cat > ~/.openclaw/desk_config.json << 'EOF'
{
  "keyboard_activity": {
    "heavy_typing_threshold": 10,
    "pause_duration": 3.0,
    "enabled": true
  },
  "screen_lock": {
    "disable_on_lock": true,
    "check_interval": 5.0
  },
  "meeting_detection": {
    "apps_to_monitor": ["zoom.us", "Microsoft Teams", "Slack", "Google Meet"],
    "sensitivity_reduction": 0.6,
    "enabled": true
  },
  "focus_mode": {
    "do_not_disturb_aware": true,
    "focus_apps": ["Xcode", "Visual Studio Code", "Cursor", "Terminal"],
    "sensitivity_reduction": 0.8
  },
  "context_detection": {
    "project_paths": [
      "~/Documents/MacDevelopment",
      "~/.openclaw/workspace",
      "~/RDS"
    ],
    "ide_apps": ["Xcode", "Visual Studio Code", "Cursor", "Terminal"],
    "communication_apps": ["Mail", "Slack", "Microsoft Teams"],
    "browser_apps": ["Safari", "Google Chrome", "Firefox"]
  }
}
EOF

# Update voice config for desk optimization
if [ ! -f ~/.openclaw/voice_config.json ]; then
    echo "📝 Creating voice configuration..."
    cat > ~/.openclaw/voice_config.json << 'EOF'
{
  "porcupine_access_key": "ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE",
  "porcupine_sensitivity": 0.7,
  "porcupine_model_path": "hey-openclaw.ppn",
  "openclaw_port": 18789,
  "openclaw_token": "",
  "command_timeout": 10.0,
  "vad_aggressiveness": 2,
  "desk_optimization": {
    "context_aware_commands": true,
    "smart_sensitivity": true,
    "conversation_memory": true,
    "performance_mode": true,
    "work_commands_enabled": true
  },
  "performance": {
    "model_preloading": true,
    "response_caching": true,
    "streaming_transcription": false,
    "parallel_processing": false
  },
  "work_integration": {
    "git_commands": true,
    "project_detection": true,
    "meeting_awareness": true,
    "communication_integration": true
  }
}
EOF
    echo "✅ Voice configuration created"
else
    echo "✅ Voice configuration exists"
fi

echo ""
echo "🧪 Testing basic functionality..."

# Test audio system (simplified check)
echo "🔊 Testing audio system..."
python3 -c "
try:
    import pyaudio
    audio = pyaudio.PyAudio()
    device_count = audio.get_device_count()
    print(f'✅ Audio system working ({device_count} devices)')
    audio.terminate()
except Exception as e:
    print(f'⚠️ Audio system test: {e}')
    print('Audio may still work - test with the main script')
"

# Test environment monitoring (basic check)
echo "🖥️ Testing environment monitoring..."
python3 -c "
try:
    import psutil
    procs = len(list(psutil.process_iter()))
    print(f'✅ Environment monitoring ready ({procs} processes)')
except Exception as e:
    print(f'⚠️ Environment monitoring: {e}')
"

# Test porcupine availability
echo "🎙️ Testing wake word detection..."
python3 -c "
try:
    import pvporcupine
    print('✅ Porcupine available - wake word detection ready')
except ImportError:
    print('⚠️ Porcupine not available - will run in testing mode')
except Exception as e:
    print(f'⚠️ Porcupine test: {e}')
"

echo ""
echo "🚀 Setup complete!"
echo ""
echo "📋 Quick Start:"
echo "  python3 desk_optimized_assistant.py"
echo ""
echo "🎯 Desk Features Ready:"
echo "  ✅ Environment awareness (keyboard, meetings, focus mode)"
echo "  ✅ Context-aware commands (project detection, app focus)"
echo "  ✅ Performance optimizations (caching, preloading)"
echo "  ✅ Work-specific command enhancement"
echo ""
echo "🎙️ Wake Word Status:"
if python3 -c "import pvporcupine" 2>/dev/null; then
    echo "  ✅ Wake word: 'computer' (built-in, ready to test)"
    echo "  🔄 For 'Hey OpenClaw': Get key from https://console.picovoice.ai/"
else
    echo "  ⚠️ Wake word detection needs Porcupine installation"
    echo "  Try: pip3 install --user --break-system-packages pvporcupine"
fi
echo ""
echo "▶️ Test now: python3 desk_optimized_assistant.py"
echo "   Say 'computer' + your command when prompted"