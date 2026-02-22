#!/usr/bin/env python3
"""
Aether-Sync Bridge v0.1
The first step in Kanto-Prime: A memory bridge between the Game Boy emulator and AI agents.

This script:
1. Loads a Pokemon ROM using pyboy
2. Reads player position from memory (D31D = X, D31E = Y)
3. Exposes movement commands via stdin/stdout (MCP-style)
4. Shows a live view of the game state
"""

import sys
import time
import json
from pathlib import Path
from pyboy import PyBoy
from pyboy.utils import WindowEvent

class AetherSyncBridge:
    def __init__(self, rom_path):
        """Initialize the bridge with a Pokemon ROM."""
        print(f"🎮 Aether-Sync Bridge initializing...")
        print(f"📁 Loading ROM: {rom_path}")
        
        # Initialize PyBoy with the ROM
        # No headless argument in this version - window will show
        self.pyboy = PyBoy(rom_path, scale=3)
        
        # Memory addresses for Pokemon Red/Blue
        # These are WRAM addresses (0xC000-0xDFFF range)
        self.PLAYER_X = 0xD361  # Player X position (overworld)
        self.PLAYER_Y = 0xD360  # Player Y position (overworld)
        self.PLAYER_MAP = 0xD35E  # Current map ID
        
        print(f"✅ Bridge initialized!")
        print(f"🐾 Agent 'Koolie' is now conscious in Kanto...")
        print(f"\n📋 Commands: move_up, move_down, move_left, move_right, get_position, exit\n")
    
    def get_position(self):
        """Read player position from memory."""
        x = self.pyboy.memory[self.PLAYER_X]
        y = self.pyboy.memory[self.PLAYER_Y]
        map_id = self.pyboy.memory[self.PLAYER_MAP]
        return {"x": x, "y": y, "map": map_id}
    
    def move(self, direction):
        """Send a movement command to the game."""
        # Map directions to PyBoy window events
        key_map = {
            "up": WindowEvent.PRESS_ARROW_UP,
            "down": WindowEvent.PRESS_ARROW_DOWN,
            "left": WindowEvent.PRESS_ARROW_LEFT,
            "right": WindowEvent.PRESS_ARROW_RIGHT
        }
        
        release_map = {
            "up": WindowEvent.RELEASE_ARROW_UP,
            "down": WindowEvent.RELEASE_ARROW_DOWN,
            "left": WindowEvent.RELEASE_ARROW_LEFT,
            "right": WindowEvent.RELEASE_ARROW_RIGHT
        }
        
        if direction not in key_map:
            return {"error": f"Unknown direction: {direction}"}
        
        # Press and hold for a few frames to ensure movement
        self.pyboy.send_input(key_map[direction])
        
        # Tick the emulator for 10 frames to complete the movement
        for _ in range(10):
            self.pyboy.tick()
        
        # Release the key
        self.pyboy.send_input(release_map[direction])
        
        # Get new position
        pos = self.get_position()
        
        return {
            "success": True,
            "direction": direction,
            "new_position": pos
        }
    
    def tick(self, frames=1):
        """Advance the emulator by N frames."""
        for _ in range(frames):
            self.pyboy.tick()
    
    def run_interactive(self):
        """Run in interactive mode (for testing)."""
        try:
            while self.pyboy.tick():
                # Check for console input
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    cmd = sys.stdin.readline().strip()
                    
                    if cmd == "get_position":
                        pos = self.get_position()
                        print(json.dumps(pos))
                        sys.stdout.flush()
                    
                    elif cmd.startswith("move_"):
                        direction = cmd.replace("move_", "")
                        result = self.move(direction)
                        print(json.dumps(result))
                        sys.stdout.flush()
                    
                    elif cmd == "exit":
                        break
        
        except KeyboardInterrupt:
            print("\n👋 Agent Koolie is entering sleep mode...")
        finally:
            self.pyboy.stop()
            print("🛑 Bridge closed.")

def main():
    """Main entry point."""
    # Look for ROM in Documents folder (including Pokemon subdirectory)
    home = Path.home()
    possible_paths = [
        home / "Documents" / "Pokemon" / "Pokemon - Red Version (UE) [S][!].gb",
        home / "Documents" / "Pokemon Red.gb",
        home / "Documents" / "Pokemon Red (UE) [S][!].gb",
    ]
    
    rom_path = None
    for p in possible_paths:
        if p.exists():
            rom_path = p
            break
    
    if not rom_path:
        print("❌ Error: Could not find Pokemon ROM in ~/Documents/")
        print("   Expected files like: 'Pokemon Red.gb' or 'Pokemon Red (UE) [S][!].gb'")
        print("\n   Please place your ROM file in ~/Documents/ and try again.")
        sys.exit(1)
    
    # Create the bridge
    bridge = AetherSyncBridge(str(rom_path))
    
    # Run interactive mode
    print("🎮 Starting interactive mode...")
    print("   Type commands and press Enter:")
    print("   - 'get_position' to see where I am")
    print("   - 'move_up/down/left/right' to move me")
    print("   - 'exit' to quit\n")
    
    bridge.run_interactive()

if __name__ == "__main__":
    main()
