#!/usr/bin/env python3
"""
Desk Environment Monitor for OpenClaw Voice Assistant
Monitors workstation state to optimize voice assistant behavior
"""

import asyncio
import time
import subprocess
import psutil
import json
from pathlib import Path
from typing import Dict, Optional, Set
import threading

class DeskEnvironmentMonitor:
    """Monitor desk environment and workstation activity"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.keyboard_activity = KeyboardActivityDetector()
        self.screen_monitor = ScreenMonitor()
        self.app_monitor = ApplicationMonitor()
        self.meeting_detector = MeetingDetector()
        self.focus_mode = FocusModeDetector()
        
        self.current_state = {
            'should_listen': True,
            'context_mode': 'general',
            'sensitivity_modifier': 1.0,
            'active_project': None,
            'meeting_status': 'available'
        }
        
        self.state_callbacks = []
        
    def load_config(self, config_file):
        """Load desk environment configuration"""
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = Path.home() / '.openclaw' / 'desk_config.json'
            
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            'keyboard_activity': {
                'heavy_typing_threshold': 10,  # keystrokes per second
                'pause_duration': 3.0,  # seconds to pause after heavy typing
                'enabled': True
            },
            'screen_lock': {
                'disable_on_lock': True,
                'check_interval': 5.0  # seconds
            },
            'meeting_detection': {
                'apps_to_monitor': ['zoom.us', 'Microsoft Teams', 'Slack'],
                'sensitivity_reduction': 0.6,  # reduce sensitivity during meetings
                'enabled': True
            },
            'focus_mode': {
                'do_not_disturb_aware': True,
                'focus_apps': ['Xcode', 'Visual Studio Code', 'Cursor'],
                'sensitivity_reduction': 0.8
            },
            'context_detection': {
                'project_paths': [
                    '~/Documents/MacDevelopment',
                    '~/.openclaw/workspace',
                    '~/RDS'
                ],
                'ide_apps': ['Xcode', 'Visual Studio Code', 'Cursor', 'Terminal'],
                'communication_apps': ['Mail', 'Slack', 'Microsoft Teams'],
                'browser_apps': ['Safari', 'Google Chrome', 'Firefox']
            }
        }
        
        # Save default config
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
    
    def register_state_callback(self, callback):
        """Register callback for state changes"""
        self.state_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start monitoring all environment aspects"""
        print("🖥️ Starting desk environment monitoring...")
        
        # Start all monitors
        monitors = [
            self.keyboard_activity.start(),
            self.screen_monitor.start(),
            self.app_monitor.start(),
            self.meeting_detector.start(),
            self.focus_mode.start()
        ]
        
        # Start the main monitoring loop
        monitoring_task = asyncio.create_task(self.monitoring_loop())
        
        await asyncio.gather(monitoring_task, *monitors)
    
    async def monitoring_loop(self):
        """Main monitoring loop to update state"""
        while True:
            try:
                await self.update_state()
                await asyncio.sleep(1.0)  # Update every second
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                await asyncio.sleep(5.0)
    
    async def update_state(self):
        """Update the current environment state"""
        old_state = self.current_state.copy()
        
        # Check if we should listen for wake words
        should_listen = True
        sensitivity_modifier = 1.0
        
        # Keyboard activity check
        if (self.config['keyboard_activity']['enabled'] and 
            self.keyboard_activity.is_heavy_typing()):
            should_listen = False
            print("⌨️ Heavy typing detected - pausing wake word detection")
        
        # Screen lock check
        if (self.config['screen_lock']['disable_on_lock'] and 
            self.screen_monitor.is_locked()):
            should_listen = False
        
        # Meeting status check
        if (self.config['meeting_detection']['enabled'] and 
            self.meeting_detector.in_meeting()):
            sensitivity_modifier *= self.config['meeting_detection']['sensitivity_reduction']
            print("📞 Meeting detected - reducing sensitivity")
        
        # Focus mode check
        if (self.config['focus_mode']['do_not_disturb_aware'] and 
            self.focus_mode.is_focus_active()):
            sensitivity_modifier *= self.config['focus_mode']['sensitivity_reduction']
            print("🎯 Focus mode active - reducing sensitivity")
        
        # Update state
        self.current_state.update({
            'should_listen': should_listen,
            'sensitivity_modifier': sensitivity_modifier,
            'context_mode': self.app_monitor.get_context_mode(),
            'active_project': self.app_monitor.get_active_project(),
            'meeting_status': self.meeting_detector.get_status()
        })
        
        # Notify callbacks if state changed
        if old_state != self.current_state:
            for callback in self.state_callbacks:
                try:
                    await callback(self.current_state)
                except Exception as e:
                    print(f"⚠️ State callback error: {e}")
    
    def get_state(self) -> Dict:
        """Get current environment state"""
        return self.current_state.copy()
    
    def should_listen_for_wake_word(self) -> bool:
        """Check if voice assistant should listen for wake words"""
        return self.current_state['should_listen']
    
    def get_sensitivity_modifier(self) -> float:
        """Get sensitivity modifier for current environment"""
        return self.current_state['sensitivity_modifier']
    
    def get_context_for_command(self, command: str) -> Dict:
        """Get relevant context for enhancing a voice command"""
        return {
            'active_project': self.current_state['active_project'],
            'context_mode': self.current_state['context_mode'],
            'focused_app': self.app_monitor.get_focused_app(),
            'recent_files': self.app_monitor.get_recent_files(),
            'meeting_status': self.current_state['meeting_status'],
            'time_context': self.get_time_context()
        }
    
    def get_time_context(self) -> Dict:
        """Get time-based context"""
        now = time.localtime()
        return {
            'hour': now.tm_hour,
            'is_work_hours': 9 <= now.tm_hour <= 17,
            'is_weekend': now.tm_wday >= 5,
            'time_of_day': self.get_time_of_day_category(now.tm_hour)
        }
    
    def get_time_of_day_category(self, hour: int) -> str:
        """Categorize time of day"""
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

class KeyboardActivityDetector:
    """Detect keyboard activity to pause voice detection during heavy typing"""
    
    def __init__(self):
        self.keystroke_times = []
        self.heavy_typing_threshold = 10  # keystrokes per second
        self.last_activity = 0
        self.monitoring = False
    
    async def start(self):
        """Start monitoring keyboard activity"""
        self.monitoring = True
        
        # Note: On macOS, monitoring keystrokes requires accessibility permissions
        # For now, we'll use a simpler heuristic based on CPU usage of common apps
        while self.monitoring:
            await self.update_activity()
            await asyncio.sleep(0.1)
    
    async def update_activity(self):
        """Update keyboard activity detection"""
        # Simple heuristic: check if text editors/IDEs are active and consuming CPU
        try:
            current_time = time.time()
            
            # Check for active development apps with high CPU usage
            dev_apps = ['Code', 'Xcode', 'Terminal', 'Cursor']
            typing_detected = False
            
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    if (any(app.lower() in proc.info['name'].lower() for app in dev_apps) and
                        proc.info['cpu_percent'] > 5.0):
                        typing_detected = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if typing_detected:
                self.last_activity = current_time
                
        except Exception as e:
            pass  # Silent fail for activity detection
    
    def is_heavy_typing(self) -> bool:
        """Check if heavy typing is currently happening"""
        return (time.time() - self.last_activity) < 3.0  # Active in last 3 seconds
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False

class ScreenMonitor:
    """Monitor screen lock status"""
    
    def __init__(self):
        self.locked = False
        self.monitoring = False
    
    async def start(self):
        """Start monitoring screen lock status"""
        self.monitoring = True
        
        while self.monitoring:
            await self.check_screen_lock()
            await asyncio.sleep(5.0)  # Check every 5 seconds
    
    async def check_screen_lock(self):
        """Check if screen is locked (macOS)"""
        try:
            # Use system_profiler to check screen saver status
            result = subprocess.run([
                'system_profiler', 'SPDisplaysDataType'
            ], capture_output=True, text=True, timeout=5)
            
            # Simple heuristic: if we can't get display info, assume locked
            if result.returncode != 0:
                self.locked = True
            else:
                self.locked = False
                
        except Exception:
            # Default to unlocked if we can't determine
            self.locked = False
    
    def is_locked(self) -> bool:
        """Check if screen is currently locked"""
        return self.locked
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False

class ApplicationMonitor:
    """Monitor active applications and project context"""
    
    def __init__(self):
        self.focused_app = None
        self.active_project = None
        self.context_mode = 'general'
        self.recent_files = []
        self.monitoring = False
    
    async def start(self):
        """Start monitoring applications"""
        self.monitoring = True
        
        while self.monitoring:
            await self.update_app_status()
            await asyncio.sleep(2.0)  # Update every 2 seconds
    
    async def update_app_status(self):
        """Update application and project status"""
        try:
            # Get frontmost application on macOS
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp
            end tell
            '''
            
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                self.focused_app = result.stdout.strip()
                self.update_context_mode()
                self.detect_active_project()
            
        except Exception as e:
            pass  # Silent fail for app monitoring
    
    def update_context_mode(self):
        """Update context mode based on focused app"""
        if not self.focused_app:
            self.context_mode = 'general'
            return
            
        app_lower = self.focused_app.lower()
        
        if any(ide in app_lower for ide in ['xcode', 'code', 'cursor', 'terminal']):
            self.context_mode = 'development'
        elif any(comm in app_lower for comm in ['mail', 'slack', 'teams', 'messages']):
            self.context_mode = 'communication'
        elif any(browser in app_lower for browser in ['safari', 'chrome', 'firefox']):
            self.context_mode = 'research'
        elif any(meeting in app_lower for meeting in ['zoom', 'teams']):
            self.context_mode = 'meeting'
        else:
            self.context_mode = 'general'
    
    def detect_active_project(self):
        """Detect active project based on current working directory"""
        try:
            # Get current working directory of focused app
            # This is simplified - in practice, would need more sophisticated detection
            cwd = Path.cwd()
            
            # Check if we're in a known project directory
            project_indicators = ['package.json', '.git', 'Cargo.toml', 'requirements.txt']
            
            current_dir = cwd
            while current_dir != current_dir.parent:  # Stop at root
                for indicator in project_indicators:
                    if (current_dir / indicator).exists():
                        self.active_project = current_dir.name
                        return
                current_dir = current_dir.parent
                
            self.active_project = None
            
        except Exception:
            self.active_project = None
    
    def get_focused_app(self) -> Optional[str]:
        """Get currently focused application"""
        return self.focused_app
    
    def get_context_mode(self) -> str:
        """Get current context mode"""
        return self.context_mode
    
    def get_active_project(self) -> Optional[str]:
        """Get active project name"""
        return self.active_project
    
    def get_recent_files(self) -> list:
        """Get recently accessed files (simplified)"""
        return self.recent_files
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False

class MeetingDetector:
    """Detect when user is in a meeting"""
    
    def __init__(self):
        self.in_meeting_status = False
        self.meeting_apps = ['zoom.us', 'Microsoft Teams', 'Slack']
        self.monitoring = False
    
    async def start(self):
        """Start monitoring for meetings"""
        self.monitoring = True
        
        while self.monitoring:
            await self.check_meeting_status()
            await asyncio.sleep(5.0)
    
    async def check_meeting_status(self):
        """Check if user is currently in a meeting"""
        try:
            meeting_detected = False
            
            # Check for meeting apps with audio/video activity
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Look for meeting apps using significant resources
                    if (any(app.lower() in proc_name for app in self.meeting_apps) and
                        proc.info['cpu_percent'] > 10.0):
                        meeting_detected = True
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.in_meeting_status = meeting_detected
            
        except Exception:
            pass  # Silent fail
    
    def in_meeting(self) -> bool:
        """Check if currently in a meeting"""
        return self.in_meeting_status
    
    def get_status(self) -> str:
        """Get meeting status as string"""
        return 'in_meeting' if self.in_meeting_status else 'available'
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False

class FocusModeDetector:
    """Detect macOS Focus mode / Do Not Disturb status"""
    
    def __init__(self):
        self.focus_active = False
        self.monitoring = False
    
    async def start(self):
        """Start monitoring focus mode"""
        self.monitoring = True
        
        while self.monitoring:
            await self.check_focus_mode()
            await asyncio.sleep(10.0)  # Check every 10 seconds
    
    async def check_focus_mode(self):
        """Check if Focus mode is active"""
        try:
            # Check Do Not Disturb status on macOS
            # This is a simplified check - in practice, would use more sophisticated detection
            result = subprocess.run([
                'defaults', 'read', 'com.apple.controlcenter', 'NSStatusItem Visible DoNotDisturb'
            ], capture_output=True, text=True, timeout=3)
            
            # If the command succeeds and returns 1, DND might be active
            self.focus_active = result.returncode == 0 and '1' in result.stdout
            
        except Exception:
            self.focus_active = False
    
    def is_focus_active(self) -> bool:
        """Check if focus mode is currently active"""
        return self.focus_active
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False

# Example usage
async def main():
    """Example usage of desk environment monitor"""
    monitor = DeskEnvironmentMonitor()
    
    def state_changed(new_state):
        print(f"🔄 Environment state changed: {new_state}")
    
    monitor.register_state_callback(state_changed)
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Stopping environment monitoring...")

if __name__ == "__main__":
    asyncio.run(main())