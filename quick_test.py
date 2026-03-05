#!/usr/bin/env python3
"""Quick test of launcher functionality"""

import sys
sys.path.append('.')

from start_desk_assistant import check_dependencies, test_openclaw_connection

print("🧪 Quick launcher test...")
print("")

# Test dependencies
missing = check_dependencies()
if missing:
    print(f"❌ Missing: {', '.join(missing)}")
else:
    print("✅ All dependencies available")

# Test OpenClaw
if test_openclaw_connection():
    print("✅ OpenClaw gateway responsive")
else:
    print("⚠️ OpenClaw gateway not responding")

print("")
print("🚀 Ready to launch: python3 start_desk_assistant.py")