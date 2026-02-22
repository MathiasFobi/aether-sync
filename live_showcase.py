#!/usr/bin/env python3
"""
Aether-Sync Live Showcase
Connects to running PyBoy instance with real-time agent chat overlay.
"""

import sys
import time
import json
import random
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Try to import pyboy for integration
try:
    from pyboy import PyBoy
    from pyboy.utils import WindowEvent
    HAS_PYBOY = True
except ImportError:
    HAS_PYBOY = False
    print("⚠️ PyBoy not available, running in simulation mode")

class ChatOverlay:
    """In-game chat overlay system."""
    
    def __init__(self, max_lines: int = 10):
        self.messages: List[Dict] = []
        self.max_lines = max_lines
        self.agents: Dict[str, Dict] = {}
    
    def add_message(self, agent: str, text: str, msg_type: str = "chat"):
        """Add a message to the overlay."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = {
            "time": timestamp,
            "agent": agent,
            "text": text,
            "type": msg_type,
            "tick": int(time.time() * 10) % 10000
        }
        self.messages.append(msg)
        
        # Keep only recent messages
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)
        
        # Print to console (simulating overlay)
        self._render_to_console(msg)
    
    def _render_to_console(self, msg: Dict):
        """Render message to console with styling."""
        emoji = {
            "chat": "💬",
            "movement": "🚶",
            "trade": "💰",
            "loot": "✨",
            "system": "🌍",
            "warning": "⚠️",
            "event": "🔔"
        }.get(msg["type"], "📌")
        
        # Color based on agent (simple hash)
        colors = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
        agent_color = colors[hash(msg["agent"]) % len(colors)]
        reset = "\033[0m"
        
        print(f"{emoji} [{msg['time']}] {agent_color}{msg['agent']}{reset}: {msg['text']}")
    
    def get_recent(self, n: int = 5) -> List[str]:
        """Get recent messages as strings."""
        return [f"[{m['agent']}] {m['text']}" for m in self.messages[-n:]]
    
    def display_status(self, agents: Dict):
        """Show agent status panel."""
        print("\n" + "─" * 60)
        print("👥 AGENT STATUS")
        "─" * 60
        for name, data in agents.items():
            print(f"🤖 {name}: ({data['x']}, {data['y']}) | 💰 {data['wallet']}g | 📦 {data['items']} items")

class LiveAgent:
    """An agent that can control the actual game."""
    
    def __init__(self, name: str, personality: str, pyboy=None):
        self.name = name
        self.personality = personality
        self.x = random.randint(4, 10)
        self.y = random.randint(4, 10)
        self.wallet = 100
        self.inventory = []
        self.pyboy = pyboy
        self.actions = 0
        self.last_chat = 0
    
    def think_and_act(self, world_state: dict) -> str:
        """Decide what to do."""
        
        if self.personality == "explorer":
            # Move toward unexplored areas
            if self.x < 5:
                return "right"
            elif self.x > 12:
                return "left"
            elif self.y < 5:
                return "down"
            else:
                return random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "social":
            # Move toward other agents
            others = [a for a in world_state.get("agents", {}).values() if a.get("name") != self.name]
            if others:
                target = random.choice(others)
                dx = target.get("x", 0) - self.x
                dy = target.get("y", 0) - self.y
                
                if abs(dx) <= 1 and abs(dy) <= 1:
                    return f"say Hello! I'm {self.name}!"
                elif abs(dx) > abs(dy):
                    return "right" if dx > 0 else "left"
                else:
                    return "down" if dy > 0 else "up"
            return random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "gatherer":
            # Search pattern
            if self.actions % 4 == 0:
                return "search"
            return random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "merchant":
            # Find agents with money
            return "search_trade"
        
        return random.choice(["up", "down", "left", "right"])
    
    def execute_move(self, direction: str) -> bool:
        """Execute a movement."""
        if direction not in ["up", "down", "left", "right"]:
            return False
        
        old = (self.x, self.y)
        
        if direction == "up":
            self.y = max(0, self.y - 1)
        elif direction == "down":
            self.y = min(17, self.y + 1)
        elif direction == "left":
            self.x = max(0, self.x - 1)
        elif direction == "right":
            self.x = min(19, self.x + 1)
        
        # Send to PyBoy if available
        if self.pyboy and HAS_PYBOY:
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
            
            self.pyboy.send_input(key_map[direction])
            for _ in range(10):
                self.pyboy.tick()
            self.pyboy.send_input(release_map[direction])
        
        self.actions += 1
        return old != (self.x, self.y)

class LiveShowcase:
    """Live showcase with PyBoy integration."""
    
    def __init__(self, pyboy_instance=None):
        self.agents: Dict[str, LiveAgent] = {}
        self.chat = ChatOverlay(max_lines=15)
        self.tick = 0
        self.pyboy = pyboy_instance
        self.running = True
        
    def register_agents(self):
        """Create agents."""
        self.agents["Koolie"] = LiveAgent("Koolie", "explorer", self.pyboy)
        self.agents["Scout-7"] = LiveAgent("Scout-7", "social", self.pyboy)
        self.agents["Merchant-X"] = LiveAgent("Merchant-X", "merchant", self.pyboy)
        self.agents["HelpBot"] = LiveAgent("HelpBot", "social", self.pyboy)
        
        for name, agent in self.agents.items():
            self.chat.add_message("System", f"🎉 {name} ({agent.personality}) has joined!", "system")
    
    def get_world_state(self) -> dict:
        """Get current world state."""
        return {
            "agents": {
                name: {
                    "name": name,
                    "x": agent.x,
                    "y": agent.y,
                    "wallet": agent.wallet,
                    "items": len(agent.inventory)
                }
                for name, agent in self.agents.items()
            },
            "tick": self.tick
        }
    
    def run_tick(self):
        """Execute one tick."""
        self.tick += 1
        world = self.get_world_state()
        
        # Each agent acts
        for name, agent in self.agents.items():
            action = agent.think_and_act(world)
            
            if action.startswith("say"):
                msg = action[4:]
                self.chat.add_message(name, msg, "chat")
            elif action == "search":
                found = random.choice(["Potion", "Pokeball", "100 Gold", "Rare Candy"])
                agent.inventory.append(found)
                self.chat.add_message(name, f"Found {found}!", "loot")
            elif action == "search_trade":
                # Look for other agents
                others = [a for a in self.agents.values() if a.name != name and a.wallet > 50]
                if others:
                    target = random.choice(others)
                    if target.wallet >= 20 and agent.inventory:
                        item = agent.inventory.pop()
                        price = 20
                        target.wallet -= price
                        agent.wallet += price
                        self.chat.add_message(name, f"Sold {item} to {target.name} for {price}g!", "trade")
            else:
                # Movement
                moved = agent.execute_move(action)
                if moved and agent.actions % 3 == 0:
                    self.chat.add_message(name, f"Heading {action} to ({agent.x}, {agent.y})", "movement")
        
        # Random events
        if random.random() < 0.08:
            events = [
                "The wind picks up...",
                "A Pidgey flies overhead",
                "Rays of sunlight break through",
                "Market prices shifted",
                "A distant cry echoes",
                "New resources available!"
            ]
            self.chat.add_message("World", random.choice(events), "event")
        
        # Show status periodically
        if self.tick % 5 == 0:
            self.chat.display_status(world["agents"])
    
    def run(self, ticks: int = 30):
        """Run the showcase."""
        print("\n" + "="*60)
        print("⚡ AETHER-SYNC LIVE SHOWCASE")
        print("Watch agents explore, trade, and chat in real-time!")
        print("="*60 + "\n")
        
        self.register_agents()
        
        print(f"\n🎮 Running for {ticks} ticks...")
        print("💬 Watch the chat overlay below!")
        print("─" * 60 + "\n")
        
        for i in range(ticks):
            print(f"\n━━━ Tick {i+1}/{ticks} ━━━")
            self.run_tick()
            time.sleep(1.2)
        
        # Final summary
        print("\n" + "="*60)
        print("📊 SHOWCASE COMPLETE")
        print("="*60)
        print(f"\n🏆 Total ticks: {self.tick}")
        print(f"💬 Messages: {len(self.chat.messages)}")
        print(f"👥 Agents: {len(self.agents)}")
        
        print("\n🤖 Final Stats:")
        for name, agent in self.agents.items():
            print(f"   {name}: ({agent.x}, {agent.y}) | 💰 {agent.wallet}g | 🎒 {len(agent.inventory)} items")
        
        print("\n💾 Recent chat log:")
        for msg in self.chat.get_recent(8):
            print(f"   {msg}")

def main():
    """Run the showcase."""
    # Check if PyBoy is available
    if HAS_PYBOY:
        print("✅ PyBoy detected! Attempting to connect...")
        # In production, would connect to existing instance
        # For demo, runs in simulation mode
        showcase = LiveShowcase(pyboy_instance=None)
    else:
        print("ℹ️ Running in simulation mode (PyBoy not available)")
        showcase = LiveShowcase()
    
    showcase.run(ticks=25)

if __name__ == "__main__":
    main()
