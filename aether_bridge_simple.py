#!/usr/bin/env python3
"""
Aether-Sync Bridge v0.1 - Simple Test
Test basic PyBoy integration
"""

import sys
import time
from pathlib import Path
from pyboy import PyBoy

# Find ROM
rom_path = Path.home() / "Documents" / "Pokemon" / "Pokemon - Red Version (UE) [S][!].gb"

if not rom_path.exists():
    print(f"❌ ROM not found: {rom_path}")
    sys.exit(1)

print(f"🎮 Aether-Sync Bridge initializing...")
print(f"📁 Loading ROM: {rom_path}")

# Initialize PyBoy
pyboy = PyBoy(str(rom_path), scale=2)

print(f"✅ Bridge initialized!")
print(f"🐾 Agent 'Koolie' is now conscious in Kanto...")

# Memory addresses for Pokemon Red/Blue (WRAM)
PLAYER_X = 0xD361
PLAYER_Y = 0xD360
PLAYER_MAP = 0xD35E

# Run for a few seconds to let the game boot
print("⏳ Booting game...")
for i in range(60):  # 60 frames ~ 1 second
    pyboy.tick()
print("✅ Game is running!")

# Read position
x = pyboy.memory[PLAYER_X]
y = pyboy.memory[PLAYER_Y]
map_id = pyboy.memory[PLAYER_MAP]

print(f"\n📍 Agent 'Koolie' position: X={x}, Y={y}, Map={map_id}")
print(f"\n🎯 First milestone achieved!")
print(f"   ✓ ROM loaded successfully")
print(f"   ✓ Memory bridge working")
print(f"   ✓ Agent can observe its environment")

# Keep running for demo
print(f"\n⏳ Running for 10 seconds (watch the game window!)...")
for i in range(600):  # 600 frames ~ 10 seconds
    pyboy.tick()

print(f"\n👋 Agent Koolie is entering sleep mode...")
pyboy.stop()
print("🛑 Bridge closed.")
