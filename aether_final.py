#!/usr/bin/env python3
"""
Aether-Sync v2.0 FINAL - Smart Multi-Agent Exploration
Properly random exploration with memory and coordination.
"""

from pyboy import PyBoy
import time
import random
import json
from datetime import datetime
from pathlib import Path

class SmartAgent:
    """Agent with memory and smart movement."""
    
    def __init__(self, name, role, gb):
        self.name = name
        self.role = role
        self.gb = gb
        self.actions = 0
        self.position_history = []
        self.last_direction = None
        self.stuck_count = 0
        
    def smart_move(self):
        """Choose direction with intelligence."""
        directions = ['up', 'down', 'left', 'right']
        
        # Avoid going same direction too many times
        if self.last_direction and self.stuck_count > 3:
            # Try perpendicular directions
            perpendicular = {
                'up': ['left', 'right'],
                'down': ['left', 'right'],
                'left': ['up', 'down'],
                'right': ['up', 'down']
            }
            choices = perpendicular.get(self.last_direction, directions)
            direction = random.choice(choices)
            self.stuck_count = 0
        else:
            # Weighted random: prefer changing direction
            weights = [25, 25, 25, 25]
            if self.last_direction:
                idx = directions.index(self.last_direction)
                weights[idx] = 5  # Reduce chance of same direction
            
            direction = random.choices(directions, weights=weights)[0]
        
        self.last_direction = direction
        return direction
    
    def execute(self):
        """Execute one move."""
        action = self.smart_move()
        
        # Press and hold
        self.gb.button_press(action)
        for _ in range(12):  # Hold longer for movement
            self.gb.tick()
        self.gb.button_release(action)
        
        # Let game settle
        for _ in range(8):
            self.gb.tick()
        
        self.actions += 1
        return action

class AetherSync:
    """Main coordination system."""
    
    def __init__(self, rom_path):
        print("=" * 70)
        print("   ⚡ AETHER-SYNC v2.0 - SMART MULTI-AGENT SYSTEM")
        print("=" * 70)
        print()
        
        self.gb = PyBoy(rom_path, window="SDL2", scale=3, sound=False)
        self.agents = []
        self.tick = 0
        self.session_start = datetime.now()
        
        # Stats
        self.stats = {
            'total_turns': 0,
            'moves': {'up': 0, 'down': 0, 'left': 0, 'right': 0},
            'start_time': self.session_start.isoformat()
        }
    
    def spawn_agents(self):
        """Create agent team."""
        print("🎮 Initializing PyBoy...")
        
        # Boot
        for i in range(300):
            self.gb.tick()
            if i == 250:
                print("✅ Past Nintendo logo!")
        
        self.agents = [
            SmartAgent("Koolie", "Explorer", self.gb),
            SmartAgent("Scout-7", "Scout", self.gb),
            SmartAgent("Merchant-X", "Merchant", self.gb),
            SmartAgent("HelpBot", "Social", self.gb),
        ]
        
        print(f"\n👥 AGENT TEAM DEPLOYED:")
        for agent in self.agents:
            print(f"   🎮 {agent.name} ({agent.role})")
        print()
    
    def run_turn(self):
        """One turn of coordination."""
        self.tick += 1
        
        # Each agent acts
        for agent in self.agents:
            action = agent.execute()
            self.stats['moves'][action] += 1
            
            # Log every 10th turn
            if self.tick % 10 == 0 and agent == self.agents[0]:
                total = sum(self.stats['moves'].values())
                print(f"🔄 Turn {self.tick}: {total} total moves | " 
                      f"↑{self.stats['moves']['up']} "
                      f"↓{self.stats['moves']['down']} "
                      f"←{self.stats['moves']['left']} "
                      f"→{self.stats['moves']['right']}")
        
        self.stats['total_turns'] = self.tick
    
    def check_input(self):
        """Check for user commands."""
        try:
            import sys
            import select
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline().strip().lower()
                if line == 'q':
                    return 'quit'
                elif line == 's':
                    return 'save'
                elif line == 'stats':
                    return 'stats'
        except:
            pass
        return None
    
    def print_stats(self):
        """Display current stats."""
        elapsed = (datetime.now() - self.session_start).total_seconds()
        total_moves = sum(self.stats['moves'].values())
        
        print(f"\n{'='*70}")
        print("📊 SESSION STATISTICS")
        print(f"{'='*70}")
        print(f"⏱️  Runtime: {elapsed:.1f} seconds")
        print(f"🔄 Turns: {self.tick}")
        print(f"🚶 Total moves: {total_moves}")
        print(f"\n📍 Movement distribution:")
        for direction, count in self.stats['moves'].items():
            pct = (count / total_moves * 100) if total_moves > 0 else 0
            print(f"   {direction:>5}: {count:>4} ({pct:>5.1f}%)")
        print(f"\n👥 Per-agent actions:")
        for agent in self.agents:
            print(f"   {agent.name:>12}: {agent.actions:>4} actions")
        print(f"{'='*70}\n")
    
    def save_game(self):
        """Attempt to save."""
        print("\n💾 SAVING...")
        
        # Open menu
        self.gb.button_press('start')
        for _ in range(15):
            self.gb.tick()
        self.gb.button_release('start')
        
        for _ in range(30):
            self.gb.tick()
        
        # Navigate to save (usually 2 down)
        for _ in range(2):
            self.gb.button_press('down')
            for _ in range(10):
                self.gb.tick()
            self.gb.button_release('down')
            for _ in range(10):
                self.gb.tick()
        
        # Select save
        self.gb.button_press('a')
        for _ in range(15):
            self.gb.tick()
        self.gb.button_release('a')
        
        for _ in range(60):
            self.gb.tick()
        
        # Confirm
        self.gb.button_press('a')
        for _ in range(15):
            self.gb.tick()
        self.gb.button_release('a')
        
        print("✅ Save attempted! (check if it worked)")
    
    def save_stats(self):
        """Save stats to file."""
        stats_file = Path.home() / ".openclaw/workspace/aether-sync/agent_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        print(f"💾 Stats saved to {stats_file}")
    
    def run(self, max_turns=None):
        """Main loop."""
        self.spawn_agents()
        
        print(f"{'='*70}")
        print("🔥 SMART EXPLORATION STARTED!")
        print("   Commands: 's' = save, 'stats' = stats, 'q' = quit")
        print(f"{'='*70}\n")
        
        running = True
        
        while running:
            self.run_turn()
            
            # Check for input
            cmd = self.check_input()
            if cmd == 'quit':
                running = False
            elif cmd == 'save':
                self.save_game()
            elif cmd == 'stats':
                self.print_stats()
            
            # Stop if max turns reached
            if max_turns and self.tick >= max_turns:
                running = False
            
            # Brief pause
            time.sleep(0.02)
        
        # Final stats
        self.print_stats()
        self.save_stats()
        
        print("\n✅ SESSION COMPLETE")
        print(f"{'='*70}\n")
        
        # Keep window open
        print("🖥️  Window staying open. Press Ctrl+C to close.")
        while True:
            self.gb.tick()
            time.sleep(0.016)

def main():
    rom = "/Users/myassistant/Documents/Pokemon/Pokemon - Red Version (UE) [S][!].gb"
    game = AetherSync(rom)
    
    try:
        game.run(max_turns=200)  # Run 200 turns by default
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
        game.print_stats()
        game.save_stats()

if __name__ == "__main__":
    main()
