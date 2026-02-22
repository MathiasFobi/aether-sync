#!/usr/bin/env python3
"""
Aether-Sync: Boot Helper
Automatically advances past PyBoy's logo screen and gets to gameplay.
"""

import sys
import time
from pathlib import Path
from pyboy import PyBoy
from pyboy.utils import WindowEvent

def boot_game(rom_path: str, skip_intro: bool = True):
    """
    Boot a Pokemon game and optionally skip the intro.
    
    Args:
        rom_path: Path to the ROM file
        skip_intro: Whether to auto-press buttons to get past logos
    """
    print(f"🎮 Booting: {rom_path}")
    
    # Initialize PyBoy with larger window
    pyboy = PyBoy(rom_path, scale=3)
    
    print("⏳ Waiting for boot sequence...")
    
    # Run through the Nintendo logo (needs ~180 frames)
    for i in range(200):
        pyboy.tick()
        if i % 50 == 0:
            print(f"   Booting... {i}/200")
    
    print("✅ Past Nintendo logo!")
    
    if skip_intro:
        print("⏭️  Skipping intro sequence...")
        
        # Press START to skip intro
        time.sleep(0.5)
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        for _ in range(30):
            pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        # Wait for title screen
        time.sleep(0.5)
        for _ in range(100):
            pyboy.tick()
        
        # Press START on title screen
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        for _ in range(30):
            pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        print("✅ At main menu!")
        
        # Press A to continue (if save exists) or new game
        time.sleep(0.5)
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
        for _ in range(30):
            pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        
        print("⏳ Loading world...")
        # Wait for world to load
        for _ in range(200):
            pyboy.tick()
        
        print("✅ World loaded!")
    
    # Get position
    PLAYER_X = 0xD361
    PLAYER_Y = 0xD360
    
    x = pyboy.memory[PLAYER_X]
    y = pyboy.memory[PLAYER_Y]
    
    print(f"\n📍 Player position: X={x}, Y={y}")
    print("\n🎮 Game is ready!")
    print("   Controls:")
    print("   - Arrow keys: Move")
    print("   - Z/A: Open menu / Select")
    print("   - X/B: Back / Cancel")
    print("   - ENTER: Start button")
    print("\n   Keep this window open to play!")
    print("   Press Ctrl+C to exit.\n")
    
    # Keep running
    try:
        while pyboy.tick():
            pass
    except KeyboardInterrupt:
        print("\n👋 Saving and exiting...")
        pyboy.stop()
    
    return pyboy

def main():
    # Find ROM
    rom_path = Path.home() / "Documents" / "Pokemon" / "Pokemon - Red Version (UE) [S][!].gb"
    
    if not rom_path.exists():
        print(f"❌ ROM not found: {rom_path}")
        print("   Expected: ~/Documents/Pokemon/Pokemon - Red Version (UE) [S][!].gb")
        sys.exit(1)
    
    boot_game(str(rom_path), skip_intro=True)

if __name__ == "__main__":
    main()
