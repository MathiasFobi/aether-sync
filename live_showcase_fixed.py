#!/usr/bin/env python3
"""
Aether-Sync Live Showcase v2.0
PyBoy integration with real-time game control + screen capture
"""

import sys
import time
import random
import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

# Try to import PIL for screenshots
try:
    from PIL import Image
    HAS_PIL = True
except:
    HAS_PIL = False

# Try to import PyBoy
try:
    from pyboy import PyBoy
    HAS_PYBOY = True
except:
    HAS_PYBOY = False
    print("⚠️  PyBoy not available, running in simulation mode")

@dataclass
class LiveAgent:
    name: str
    personality: str
    x: int = 6
    y: int = 4
    gb: Optional[PyBoy] = None
    actions: int = 0
    
    def execute_action(self, action: str):
        """Execute action via PyBoy button presses."""
        if not HAS_PYBOY or not self.gb:
            # Simulation mode
            if action == "move_up":
                self.y = max(4, self.y - 1)
            elif action == "move_down":
                self.y = min(11, self.y + 1)
            elif action == "move_left":
                self.x = max(4, self.x - 1)
            elif action == "move_right":
                self.x = min(11, self.x + 1)
            self.actions += 1
            return True
        
        # Real PyBoy mode
        moved = False
        if action == "move_up":
            self.gb.button_press("up")
            self.gb.tick()
            self.gb.button_release("up")
            moved = True
        elif action == "move_down":
            self.gb.button_press("down")
            self.gb.tick()
            self.gb.button_release("down")
            moved = True
        elif action == "move_left":
            self.gb.button_press("left")
            self.gb.tick()
            self.gb.button_release("left")
            moved = True
        elif action == "move_right":
            self.gb.button_press("right")
            self.gb.tick()
            self.gb.button_release("right")
            moved = True
        elif action == "a":
            self.gb.button_press("a")
            self.gb.tick()
            self.gb.button_release("a")
        elif action == "b":
            self.gb.button_press("b")
            self.gb.tick()
            self.gb.button_release("b")
        elif action == "start":
            self.gb.button_press("start")
            self.gb.tick()
            self.gb.button_release("start")
        
        if moved:
            self.actions += 1
        return moved

class LiveShowcase:
    def __init__(self, rom_path: Optional[str] = None):
        self.agents: Dict[str, LiveAgent] = {}
        self.tick_count = 0
        self.gb: Optional[PyBoy] = None
        self.rom_path = rom_path
        
        if HAS_PYBOY and rom_path and Path(rom_path).exists():
            self._init_pyboy(rom_path)
    
    def _init_pyboy(self, rom_path: str):
        """Initialize PyBoy and boot past logo."""
        print("🎮 Initializing PyBoy...")
        
        # Enable sound, window scaling
        self.gb = PyBoy(
            rom_path,
            window="SDL2",
            scale=3,
            sound=False  # Disable sound for speed
        )
        
        # Boot past Nintendo logo
        print("⏳ Booting past Nintendo logo...")
        for _ in range(250):
            self.gb.tick()
        
        # Skip intro
        print("⏭️  Auto-skipping intro...")
        for _ in range(200):
            self.gb.tick()
        
        print("✅ PyBoy ready!")
    
    def register_agent(self, name: str, personality: str):
        """Register a live agent."""
        agent = LiveAgent(name=name, personality=personality, gb=self.gb)
        
        # Random spawn in Pallet Town area
        agent.x = random.randint(4, 8)
        agent.y = random.randint(3, 7)
        
        self.agents[name] = agent
        print(f"🎉 {name} ({personality}) ready!")
    
    def think(self, agent: LiveAgent) -> str:
        """Simple AI for movement."""
        if agent.personality == "explorer":
            return random.choice(["move_up", "move_down", "move_left", "move_right"])
        elif agent.personality == "social":
            return random.choice(["move_up", "move_down", "move_left", "move_right", "a"])
        return "move_up"
    
    def capture_screen(self):
        """Capture current screen screenshot."""
        if HAS_PIL and self.gb:
            try:
                # Get screen buffer from PyBoy
                screen = self.gb.botsupport_manager().screen()
                pixels = screen.screen_ndarray()
                
                # Convert to PIL Image
                img = Image.fromarray(pixels)
                
                # Save
                screenshot_path = Path("/Users/myassistant/.openclaw/workspace/aether-sync/screen_live.png")
                img.save(screenshot_path)
                
                # Also save ASCII preview
                self._ascii_preview(img)
                
                print(f"📸 Screenshot saved: {screenshot_path}")
                return True
            except Exception as e:
                print(f"⚠️  Screenshot failed: {e}")
                return False
        return False
    
    def _ascii_preview(self, img: Image.Image, width: int = 40):
        """Generate ASCII art preview."""
        img = img.convert('L').resize((width, width))
        chars = " ░▒▓█"
        
        lines = []
        for y in range(0, img.height, 2):
            line = ""
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                char_idx = int(pixel / 255 * (len(chars) - 1))
                line += chars[char_idx]
            lines.append(line)
        
        return "\n".join(lines)
    
    def tick(self):
        """One tick of the showcase."""
        self.tick_count += 1
        
        print(f"\n{'━' * 50}")
        print(f"TICK {self.tick_count}")
        print('━' * 50)
        
        # Each agent acts
        for name, agent in self.agents.items():
            action = self.think(agent)
            agent.execute_action(action)
            print(f"🚶 {name}: {action.replace('_', ' ')}")
        
        # Capture screenshot
        self.capture_screen()
        
        # Show status
        print("\n👥 AGENT STATUS:")
        for name, agent in self.agents.items():
            print(f"  {name}: ({agent.x}, {agent.y}) | {agent.actions} actions")
        
        # Run PyBoy for a few frames
        if self.gb:
            for _ in range(10):
                self.gb.tick()
    
    def run(self, ticks: int = 25):
        """Run the showcase."""
        print("\n" + "=" * 50)
        print("⚡ AETHER-SYNC LIVE SHOWCASE v2.0")
        if HAS_PYBOY and self.gb:
            print("🎮 Real PyBoy mode - agents control actual game!")
        else:
            print("🧪 Simulation mode - no PyBoy window")
        print("=" * 50 + "\n")
        
        # Register agents
        self.register_agent("Koolie", "explorer")
        self.register_agent("Scout-7", "social")
        self.register_agent("Merchant-X", "merchant")
        self.register_agent("HelpBot", "social")
        
        print(f"\n🏁 Running for {ticks} ticks...")
        print(f"📸 Screenshots saved to: ./screen_live.png\n")
        
        for _ in range(ticks):
            self.tick()
            time.sleep(1)
        
        print("\n✅ Showcase complete!")
        
        if self.gb:
            # Keep window open
            print("Press Ctrl+C to close PyBoy window...")
            try:
                while True:
                    self.gb.tick()
            except KeyboardInterrupt:
                pass
            self.gb.stop()

def main():
    rom_path = None
    
    # Look for ROM
    if len(sys.argv) > 1:
        rom_path = sys.argv[1]
    else:
        # Default location
        default = "/Users/myassistant/Documents/Pokemon/Pokemon - Red Version (UE) [S][!].gb"
        if Path(default).exists():
            rom_path = default
    
    showcase = LiveShowcase(rom_path)
    showcase.run(ticks=10)

if __name__ == "__main__":
    main()
