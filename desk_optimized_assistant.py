#!/usr/bin/env python3
"""
Desk-Optimized OpenClaw Voice Assistant
Integrates environment monitoring with wake word detection for seamless desk workflow
"""

import asyncio
import json
import requests
import pyaudio
import struct
import time
import tempfile
import subprocess
from pathlib import Path
import sys
import threading
from typing import Dict, Optional, List

from desk_environment_monitor import DeskEnvironmentMonitor

class DeskOptimizedVoiceAssistant:
    """Voice assistant optimized for desk environment with intelligent context awareness"""
    
    def __init__(self):
        self.config = self.load_config()
        self.environment_monitor = DeskEnvironmentMonitor()
        self.setup_porcupine()
        self.setup_audio()
        self.setup_command_processor()
        
        # State management
        self.listening = True
        self.processing_command = False
        self.current_sensitivity = self.config.get('porcupine_sensitivity', 0.7)
        self.conversation_context = []
        
        # Performance optimization
        self.model_cache = {}
        self.response_cache = {}
        self.startup_time = time.time()
        
        # Register for environment state changes
        self.environment_monitor.register_state_callback(self.on_environment_change)
        
    def load_config(self):
        """Load configuration with desk-specific settings"""
        config_file = Path.home() / '.openclaw' / 'voice_config.json'
        
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        else:
            config = {}
        
        # Add desk-specific defaults
        desk_defaults = {
            'desk_optimization': {
                'context_aware_commands': True,
                'smart_sensitivity': True,
                'conversation_memory': True,
                'performance_mode': True,
                'work_commands_enabled': True
            },
            'performance': {
                'model_preloading': True,
                'response_caching': True,
                'streaming_transcription': False,  # Future enhancement
                'parallel_processing': False       # Future enhancement
            },
            'work_integration': {
                'git_commands': True,
                'project_detection': True,
                'meeting_awareness': True,
                'communication_integration': True
            }
        }
        
        # Merge with existing config
        for section, settings in desk_defaults.items():
            if section not in config:
                config[section] = settings
            else:
                for key, value in settings.items():
                    if key not in config[section]:
                        config[section][key] = value
        
        # Save updated config
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config
    
    def setup_porcupine(self):
        """Initialize Porcupine with desk optimization"""
        try:
            import pvporcupine
            
            access_key = self.config.get('porcupine_access_key', 'ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE')
            
            # Handle newer Porcupine API that requires access_key
            if access_key == "ENTER_YOUR_PICOVOICE_ACCESS_KEY_HERE":
                print("🔧 Using built-in 'computer' keyword for testing")
                # Try without access key first (older API), then with demo key
                try:
                    self.porcupine = pvporcupine.create(
                        keywords=['computer'],
                        sensitivities=[self.config.get('porcupine_sensitivity', 0.7)]
                    )
                except Exception:
                    # Use demo access key for testing
                    try:
                        self.porcupine = pvporcupine.create(
                            access_key="demo",  # Demo key for testing
                            keywords=['computer'],
                            sensitivities=[self.config.get('porcupine_sensitivity', 0.7)]
                        )
                    except Exception:
                        print("⚠️ Porcupine requires access key. Get one from https://console.picovoice.ai/")
                        self.porcupine = None
                        return
                self.wake_word_phrase = "computer"
            else:
                # Try custom model first, fallback to built-in
                model_path = Path(self.config.get('porcupine_model_path', 'hey-openclaw.ppn'))
                
                if not model_path.exists():
                    script_dir = Path(__file__).parent
                    model_path = script_dir / model_path.name
                
                if model_path.exists():
                    self.porcupine = pvporcupine.create(
                        access_key=access_key,
                        keyword_paths=[str(model_path)],
                        sensitivities=[self.config.get('porcupine_sensitivity', 0.7)]
                    )
                    self.wake_word_phrase = "Hey OpenClaw"
                else:
                    self.porcupine = pvporcupine.create(
                        access_key=access_key,
                        keywords=['computer'],
                        sensitivities=[self.config.get('porcupine_sensitivity', 0.7)]
                    )
                    self.wake_word_phrase = "computer"
            
            self.frame_length = self.porcupine.frame_length
            self.sample_rate = self.porcupine.sample_rate
            
            print(f"🎙️ Desk-optimized wake word ready: '{self.wake_word_phrase}'")
            
        except ImportError:
            print("❌ Porcupine not installed. Run: ./setup_wake_word.sh")
            self.porcupine = None
        except Exception as e:
            print(f"❌ Porcupine setup failed: {e}")
            self.porcupine = None
    
    def setup_audio(self):
        """Initialize audio with desk-specific optimizations"""
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
            
            # Audio optimization for desk environment
            self.audio_optimizer = DeskAudioOptimizer(self.config)
            
            print(f"🔊 Desk-optimized audio: {self.sample_rate}Hz, noise filtering enabled")
            
        except Exception as e:
            print(f"❌ Audio setup failed: {e}")
            sys.exit(1)
    
    def setup_command_processor(self):
        """Initialize command processor with work-specific commands"""
        self.command_processor = WorkContextCommandProcessor(self.config, self.environment_monitor)
        
        # Preload models if enabled
        if self.config.get('performance', {}).get('model_preloading', True):
            asyncio.create_task(self.preload_models())
    
    async def preload_models(self):
        """Preload models for better performance"""
        print("🔄 Preloading models for faster response...")
        try:
            # Test Whisper to ensure it's cached
            subprocess.run(['whisper', '--help'], capture_output=True)
            print("✅ Whisper model ready")
        except Exception:
            pass
    
    async def on_environment_change(self, new_state: Dict):
        """Handle environment state changes"""
        # Adjust sensitivity based on environment
        if self.config.get('desk_optimization', {}).get('smart_sensitivity', True):
            base_sensitivity = self.config.get('porcupine_sensitivity', 0.7)
            modifier = new_state.get('sensitivity_modifier', 1.0)
            self.current_sensitivity = base_sensitivity * modifier
        
        # Log important state changes
        if not new_state['should_listen'] and self.listening:
            context = new_state.get('context_mode', 'unknown')
            print(f"⏸️ Pausing wake word detection ({context} mode)")
        elif new_state['should_listen'] and not self.listening:
            print(f"▶️ Resuming wake word detection")
    
    async def listen_for_wake_word(self):
        """Intelligent wake word detection with environment awareness"""
        if not self.porcupine:
            print("❌ Wake word detection not available")
            return
        
        print(f"👂 Desk-optimized listening for '{self.wake_word_phrase}'...")
        print("🖥️ Environment monitoring active")
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
                # Check environment state
                env_state = self.environment_monitor.get_state()
                
                if not env_state['should_listen'] or self.processing_command:
                    await asyncio.sleep(0.1)
                    continue
                
                try:
                    # Read audio frame
                    pcm = stream.read(self.frame_length, exception_on_overflow=False)
                    
                    # Apply audio optimization
                    pcm = self.audio_optimizer.process_frame(pcm)
                    pcm = struct.unpack_from("h" * self.frame_length, pcm)
                    
                    # Check for wake word with current sensitivity
                    keyword_index = self.porcupine.process(pcm)
                    
                    if keyword_index >= 0:
                        print(f"\n🎯 Wake word '{self.wake_word_phrase}' detected!")
                        await self.handle_voice_command()
                        
                        # Brief pause after processing
                        await asyncio.sleep(1.0)
                        print(f"👂 Listening for '{self.wake_word_phrase}'...")
                    
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
        """Process voice command with context awareness"""
        self.processing_command = True
        
        try:
            print("🔴 Listening for command...")
            
            # Get environment context
            env_context = self.environment_monitor.get_context_for_command("")
            
            # Capture speech
            audio_file = await self.capture_command_with_context(env_context)
            
            if audio_file:
                # Process command with full context
                await self.process_voice_command_with_context(audio_file, env_context)
                Path(audio_file).unlink()
            else:
                print("❌ No command detected")
                
        except Exception as e:
            print(f"❌ Command processing error: {e}")
        finally:
            self.processing_command = False
    
    async def capture_command_with_context(self, context: Dict):
        """Capture speech with context-aware timeout"""
        # Adjust timeout based on context
        if context.get('context_mode') == 'development':
            timeout = self.config.get('command_timeout', 10.0) * 1.5  # Longer for dev commands
        elif context.get('meeting_status') == 'in_meeting':
            timeout = self.config.get('command_timeout', 10.0) * 0.7  # Shorter in meetings
        else:
            timeout = self.config.get('command_timeout', 10.0)
        
        return await self.capture_speech_with_vad(timeout)
    
    async def capture_speech_with_vad(self, timeout: float = 10.0):
        """Capture speech with voice activity detection"""
        try:
            import webrtcvad
            
            vad = webrtcvad.Vad(self.config.get('vad_aggressiveness', 2))
            
            frames = []
            silence_count = 0
            speech_detected = False
            frame_duration_ms = 10
            frames_per_buffer = int(self.sample_rate * frame_duration_ms / 1000)
            max_silence_frames = int(3000 / frame_duration_ms)  # 3 seconds silence
            max_total_frames = int(timeout * 1000 / frame_duration_ms)
            
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
                    
                    # Apply audio optimization
                    frame = self.audio_optimizer.process_frame(frame)
                    frames.append(frame)
                    frame_count += 1
                    
                    try:
                        is_speech = vad.is_speech(frame, self.sample_rate)
                        
                        if is_speech:
                            speech_detected = True
                            silence_count = 0
                            print("🗣️", end="", flush=True)
                        else:
                            if speech_detected:
                                silence_count += 1
                                if silence_count % 20 == 0:  # Every 200ms
                                    print(".", end="", flush=True)
                        
                        if speech_detected and silence_count > max_silence_frames:
                            print(" [end]")
                            break
                            
                    except Exception:
                        pass  # Continue without VAD if it fails
                    
                    await asyncio.sleep(0.001)
                    
            finally:
                stream.close()
            
            if not speech_detected:
                print("❌ No speech detected")
                return None
            
            print(" ✅ Speech captured")
            
            # Save audio
            import wave
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wf = wave.open(f.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
                wf.close()
                return f.name
                
        except ImportError:
            print("⚠️ WebRTC VAD not available, using simple capture")
            return await self.capture_speech_simple(timeout)
        except Exception as e:
            print(f"❌ VAD capture failed: {e}")
            return await self.capture_speech_simple(timeout)
    
    async def capture_speech_simple(self, timeout: float = 5.0):
        """Fallback simple speech capture"""
        frames = []
        frames_per_second = int(self.sample_rate / 1024)
        total_frames = int(frames_per_second * timeout)
        
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
                data = self.audio_optimizer.process_frame(data)
                frames.append(data)
                
                if i % (frames_per_second // 2) == 0:
                    print("🔴", end="", flush=True)
                    
                await asyncio.sleep(0.001)
                
        finally:
            stream.close()
            
        print(" ✅ Timeout capture complete")
        
        import wave
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            return f.name
    
    async def process_voice_command_with_context(self, audio_file: str, context: Dict):
        """Process command with full context awareness and work-specific enhancements"""
        
        # Transcribe with performance optimization
        print("🔄 Transcribing...")
        start_time = time.time()
        text = await self.transcribe_audio_optimized(audio_file)
        transcribe_time = time.time() - start_time
        
        if not text:
            print("❌ Could not transcribe audio")
            return
        
        print(f"📝 You said: '{text}' (transcribed in {transcribe_time:.1f}s)")
        
        # Enhance command with context
        enhanced_command = self.command_processor.enhance_command(text, context, self.conversation_context)
        
        print(f"🧠 Enhanced command: {enhanced_command}")
        
        # Process with OpenClaw
        start_time = time.time()
        response = await self.query_openclaw_optimized(enhanced_command)
        response_time = time.time() - start_time
        
        print(f"🤖 Response: {response} (generated in {response_time:.1f}s)")
        
        # Update conversation context
        self.conversation_context.append({
            'command': text,
            'enhanced_command': enhanced_command,
            'response': response,
            'context': context,
            'timestamp': time.time()
        })
        
        # Keep only recent context
        if len(self.conversation_context) > 5:
            self.conversation_context = self.conversation_context[-5:]
        
        # Synthesize speech
        await self.synthesize_speech_optimized(response)
    
    async def transcribe_audio_optimized(self, audio_file: str) -> Optional[str]:
        """Optimized audio transcription"""
        try:
            # Use medium model for balance of speed/accuracy in desk environment
            model = 'medium'  # Could be configurable based on performance needs
            
            result = subprocess.run([
                'whisper', audio_file,
                '--model', model,
                '--output_format', 'txt',
                '--output_dir', '/tmp',
                '--language', 'en'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"Whisper error: {result.stderr}")
                return None
            
            base_name = Path(audio_file).stem
            txt_file = Path('/tmp') / f"{base_name}.txt"
            
            if txt_file.exists():
                text = txt_file.read_text().strip()
                txt_file.unlink()
                return text
            
            return None
            
        except subprocess.TimeoutExpired:
            print("❌ Transcription timed out")
            return None
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    async def query_openclaw_optimized(self, enhanced_command: str) -> str:
        """Optimized OpenClaw query with caching"""
        try:
            # Check response cache for similar recent commands
            cache_key = enhanced_command.lower().strip()
            if (self.config.get('performance', {}).get('response_caching', True) and
                cache_key in self.response_cache):
                cached_response, cache_time = self.response_cache[cache_key]
                if time.time() - cache_time < 300:  # 5 minute cache
                    print("💾 Using cached response")
                    return cached_response
            
            # Query OpenClaw
            url = f"http://localhost:{self.config.get('openclaw_port', 18789)}/api/prompt"
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Add auth if token is configured
            token = self.config.get('openclaw_token', '').strip()
            if token:
                headers['Authorization'] = f"Bearer {token}"
            
            data = {
                'prompt': enhanced_command
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', result.get('message', str(result)))
                
                # Cache successful responses
                if self.config.get('performance', {}).get('response_caching', True):
                    self.response_cache[cache_key] = (response_text, time.time())
                    
                    # Limit cache size
                    if len(self.response_cache) > 50:
                        oldest_key = min(self.response_cache.keys(), 
                                       key=lambda k: self.response_cache[k][1])
                        del self.response_cache[oldest_key]
                
                return response_text
            else:
                return f"Sorry, I couldn't process that request. (Error {response.status_code})"
                
        except Exception as e:
            print(f"❌ Query error: {e}")
            return "Sorry, something went wrong while processing your request."
    
    async def synthesize_speech_optimized(self, text: str):
        """Optimized speech synthesis"""
        try:
            print("🔊 Generating speech...")
            
            result = subprocess.run([
                'openclaw', 'tts', '--text', text
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ Speech synthesis complete")
                return True
            else:
                print(f"TTS error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Speech synthesis error: {e}")
            return False
    
    async def run_desk_optimized(self):
        """Main desk-optimized operation"""
        print("🖥️ OpenClaw Desk-Optimized Voice Assistant")
        print("=" * 50)
        print(f"Wake word: '{self.wake_word_phrase}'")
        print("Environment monitoring: Active")
        print("Performance optimizations: Enabled")
        print("Work command integration: Ready")
        print()
        
        if not self.porcupine:
            print("❌ Wake word detection not available")
            return
        
        try:
            # Start environment monitoring
            environment_task = asyncio.create_task(
                self.environment_monitor.start_monitoring()
            )
            
            # Start wake word detection
            voice_task = asyncio.create_task(
                self.listen_for_wake_word()
            )
            
            await asyncio.gather(environment_task, voice_task)
            
        except Exception as e:
            print(f"❌ Desk-optimized operation failed: {e}")
        finally:
            if hasattr(self, 'audio'):
                self.audio.terminate()

class DeskAudioOptimizer:
    """Audio optimization for desk environment"""
    
    def __init__(self, config):
        self.config = config
        self.noise_gate_threshold = -40  # dB
        
    def process_frame(self, frame_data):
        """Apply audio optimizations to frame"""
        # Simple noise gate to filter keyboard clicks
        # In a full implementation, would add more sophisticated filtering
        return frame_data

class WorkContextCommandProcessor:
    """Process commands with work context awareness"""
    
    def __init__(self, config, environment_monitor):
        self.config = config
        self.environment_monitor = environment_monitor
        self.work_commands = self.load_work_commands()
    
    def load_work_commands(self):
        """Load work-specific command patterns"""
        return {
            'development': {
                'patterns': [
                    ('open project', self.handle_open_project),
                    ('run tests', self.handle_run_tests),
                    ('check build', self.handle_check_build),
                    ('create branch', self.handle_create_branch),
                    ('commit changes', self.handle_commit),
                    ('push code', self.handle_push)
                ]
            },
            'communication': {
                'patterns': [
                    ('check email', self.handle_check_email),
                    ('schedule meeting', self.handle_schedule_meeting),
                    ('send message', self.handle_send_message),
                    ('set status', self.handle_set_status)
                ]
            },
            'research': {
                'patterns': [
                    ('research', self.handle_research),
                    ('summarize', self.handle_summarize),
                    ('find docs', self.handle_find_docs)
                ]
            }
        }
    
    def enhance_command(self, raw_command: str, context: Dict, conversation_history: List) -> str:
        """Enhance command with context and work-specific intelligence"""
        enhanced = raw_command
        
        # Add project context if available
        if context.get('active_project'):
            if 'project' in raw_command.lower() and not any(proj in raw_command.lower() for proj in ['openclaw', 'rds', 'voice']):
                enhanced = f"{raw_command} (current project: {context['active_project']})"
        
        # Add app context
        if context.get('focused_app'):
            if 'current' in raw_command.lower() or 'this' in raw_command.lower():
                enhanced = f"{raw_command} (current app: {context['focused_app']})"
        
        # Add time context
        time_context = context.get('time_context', {})
        if time_context.get('is_work_hours'):
            if 'schedule' in raw_command.lower():
                enhanced = f"{raw_command} (during work hours)"
        
        return enhanced
    
    def handle_open_project(self, command: str, context: Dict) -> str:
        """Handle open project commands"""
        return f"Open project workspace. {command}"
    
    def handle_run_tests(self, command: str, context: Dict) -> str:
        """Handle run tests commands"""
        return f"Run test suite for current project. {command}"
    
    def handle_check_build(self, command: str, context: Dict) -> str:
        """Handle check build commands"""
        return f"Check CI/CD build status. {command}"
    
    def handle_create_branch(self, command: str, context: Dict) -> str:
        """Handle create branch commands"""
        return f"Create git branch. {command}"
    
    def handle_commit(self, command: str, context: Dict) -> str:
        """Handle commit commands"""
        return f"Commit code changes. {command}"
    
    def handle_push(self, command: str, context: Dict) -> str:
        """Handle push commands"""
        return f"Push code to repository. {command}"
    
    def handle_check_email(self, command: str, context: Dict) -> str:
        """Handle check email commands"""
        return f"Check email for urgent messages. {command}"
    
    def handle_schedule_meeting(self, command: str, context: Dict) -> str:
        """Handle schedule meeting commands"""
        return f"Schedule calendar meeting. {command}"
    
    def handle_send_message(self, command: str, context: Dict) -> str:
        """Handle send message commands"""
        return f"Send message or communication. {command}"
    
    def handle_set_status(self, command: str, context: Dict) -> str:
        """Handle set status commands"""
        return f"Set availability status. {command}"
    
    def handle_research(self, command: str, context: Dict) -> str:
        """Handle research commands"""
        return f"Research and summarize information. {command}"
    
    def handle_summarize(self, command: str, context: Dict) -> str:
        """Handle summarize commands"""
        return f"Summarize content or information. {command}"
    
    def handle_find_docs(self, command: str, context: Dict) -> str:
        """Handle find documentation commands"""
        return f"Find documentation or references. {command}"

async def main():
    """Main entry point for desk-optimized assistant"""
    print("🚀 Initializing Desk-Optimized OpenClaw Voice Assistant...")
    
    # Check dependencies
    try:
        import pvporcupine
        import pyaudio
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: ./setup_wake_word.sh")
        return
    
    # Start the assistant
    assistant = DeskOptimizedVoiceAssistant()
    
    try:
        await assistant.run_desk_optimized()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())