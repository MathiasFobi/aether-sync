#!/usr/bin/env python3
"""
Aether-Sync: Overnight Learning Run
Continuous operation with data logging for marketplace development.
"""

from pyboy import PyBoy
from datetime import datetime
import time
import random
import json
from pathlib import Path

class LearningAgent:
    """Agent that learns from exploration."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.actions = 0
        self.discoveries = []
        self.position_log = []
        self.start_time = datetime.now()
        
    def decide_move(self, tick):
        """Smart movement with variety."""
        directions = ['up', 'down', 'left', 'right']
        
        # Add randomness
        if random.random() < 0.7:
            return random.choice(directions)
        else:
            # Prefer changing direction
            return random.choice(directions)
    
    def log_action(self, action, position=None):
        """Log what the agent did."""
        self.actions += 1
        self.position_log.append({
            'time': datetime.now().isoformat(),
            'action': action,
            'tick': len(self.position_log)
        })

def main():
    print("=" * 70)
    print("   🌙 AETHER-SYNC: OVERNIGHT LEARNING RUN")
    print("   Running through the night - checking in periodically")
    print("=" * 70)
    print()
    
    # Initialize PyBoy
    gb = PyBoy(
        "/Users/myassistant/Documents/Pokemon/Pokemon - Red Version (UE) [S][!].gb",
        window="SDL2",
        scale=2,  # Smaller scale for overnight
        sound=False
    )
    
    # Boot
    print("⏳ Booting...")
    for i in range(300):
        gb.tick()
        if i % 50 == 0:
            print(f"  Boot progress: {i}/300")
    
    print("✅ Game ready!")
    print()
    
    # Create agents
    agents = [
        LearningAgent("Koolie", "Explorer"),
        LearningAgent("Scout-7", "Scout"),
        LearningAgent("Merchant-X", "Merchant"),
        LearningAgent("HelpBot", "Social"),
    ]
    
    for agent in agents:
        print(f"🎮 {agent.name} ({agent.role}) ready")
    
    print()
    print("🔥 Starting continuous exploration...")
    print("📝 Logging actions every 100 ticks")
    print("💾 Auto-saving stats hourly")
    print()
    print("To view from phone tomorrow:")
    print("  http://192.168.64.6:8080/controller.html")
    print()
    
    tick = 0
    start_time = datetime.now()
    stats = {
        'start_time': start_time.isoformat(),
        'total_ticks': 0,
        'moves': {'up': 0, 'down': 0, 'left': 0, 'right': 0},
        'agent_actions': {a.name: 0 for a in agents}
    }
    
    # Run overnight (8 hours = ~28,800 ticks at 1 tick/sec)
    # But speed it up: 60 ticks/sec
    while True:
        # Each agent acts
        for agent in agents:
            action = agent.decide_move(tick)
            
            # Execute
            gb.button_press(action)
            for _ in range(10):
                gb.tick()
            gb.button_release(action)
            
            for _ in range(5):
                gb.tick()
            
            agent.log_action(action)
            stats['moves'][action] += 1
            stats['agent_actions'][agent.name] += 1
        
        tick += 1
        stats['total_ticks'] = tick
        
        # Log every 100 ticks
        if tick % 100 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            total_moves = sum(stats['moves'].values())
            print(f"[{datetime.now().strftime('%H:%M')}] Tick {tick}: {total_moves} moves | "
                  f"Runtime: {elapsed/60:.1f} min")
        
        # Save stats every hour (3600 ticks at 1/sec, adjusted for speed)
        if tick % 3600 == 0:
            stats_file = Path.home() / ".openclaw/workspace/aether-sync/overnight_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            print(f"💾 Stats saved at tick {tick}")
        
        # Speed: ~60 ticks per second
        time.sleep(0.016)

if __name__ == "__main__":
    main()
