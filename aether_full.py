#!/usr/bin/env python3
"""
Aether-Sync v1.0 - Full Implementation
 economy + fixed SocialBot + territories + chat overlay
"""

import sys
import json
import time
import random
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ItemType(Enum):
    POTION = "potion"
    POKEBALL = "pokeball"
    GOLD = "gold"
    LAND = "land"

@dataclass
class Item:
    type: ItemType
    quantity: int = 1
    owner: str = ""

@dataclass
class Territory:
    x: int
    y: int
    owner: str
    name: str
    value: int = 100

@dataclass
class Agent:
    name: str
    personality: str
    x: int = 0
    y: int = 0
    wallet: int = 100  # Starting gold
    inventory: List[Item] = field(default_factory=list)
    actions: int = 0
    reputation: int = 50  # 0-100
    guild: Optional[str] = None
    messages: List[str] = field(default_factory=list)
    
    def think(self, world) -> str:
        """AI decision making with personality."""
        
        if self.personality == "explorer":
            # Explore unexplored areas
            directions = ["up", "down", "left", "right"]
            # Prefer unexplored
            best = random.choice(directions)
            if self.x > 10:
                best = "left"
            elif self.x < -10:
                best = "right"
            return f"move {best}"
        
        elif self.personality == "gatherer":
            # Look for items or resources
            if self.wallet > 200:
                return "buy_land"
            elif random.random() > 0.7:
                return "gather"
            else:
                directions = ["up", "down", "left", "right"]
                return f"move {random.choice(directions)}"
        
        elif self.personality == "social":
            # FIXED: Actually move toward other agents!
            nearest = world.get_nearest_agent(self)
            if nearest:
                dx = nearest.x - self.x
                dy = nearest.y - self.y
                
                if abs(dx) > abs(dy):
                    direction = "right" if dx > 0 else "left"
                else:
                    direction = "down" if dy > 0 else "up"
                
                # If close enough, talk
                if abs(dx) <= 1 and abs(dy) <= 1:
                    return f"say Hello {nearest.name}! Want to trade?"
                return f"move {direction}"
            return "move " + random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "merchant":
            # Find agents with money and sell them items
            richest = world.get_richest_agent()
            if richest and richest.name != self.name:
                dx = richest.x - self.x
                dy = richest.y - self.y
                if abs(dx) <= 1 and abs(dy) <= 1:
                    return f"offer_trade {richest.name}"
                direction = "right" if dx > 0 else "left" if dx < 0 else "down" if dy > 0 else "up"
                return f"move {direction}"
            return "move " + random.choice(["up", "down", "left", "right"])
        
        return "move up"

class AetherWorld:
    """The complete Aether-Sync world with economy."""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.territories: List[Territory] = []
        self.market: Dict[ItemType, int] = {
            ItemType.POTION: 20,
            ItemType.POKEBALL: 50,
            ItemType.GOLD: 1,
            ItemType.LAND: 100
        }
        self.log: List[dict] = []
        self.tick = 0
        self.chat_overlay: List[str] = []
        self.lock = threading.Lock()
    
    def register_agent(self, name: str, personality: str) -> Agent:
        """Register a new agent."""
        agent = Agent(name=name, personality=personality)
        # Random spawn near center
        agent.x = random.randint(-2, 2)
        agent.y = random.randint(-2, 2)
        agent.wallet = 100 + random.randint(0, 50)  # Starting gold varies
        self.agents[name] = agent
        self.broadcast(f"🎉 {name} ({personality}) has entered Kanto-Prime!", "system")
        return agent
    
    def get_nearest_agent(self, agent: Agent) -> Optional[Agent]:
        """Find nearest agent."""
        others = [a for a in self.agents.values() if a.name != agent.name]
        if not others:
            return None
        return min(others, key=lambda a: abs(a.x - agent.x) + abs(a.y - agent.y))
    
    def get_richest_agent(self) -> Optional[Agent]:
        """Find agent with most gold."""
        if not self.agents:
            return None
        return max(self.agents.values(), key=lambda a: a.wallet)
    
    def broadcast(self, message: str, msg_type: str = "chat"):
        """Add to chat overlay."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.chat_overlay.append({"text": formatted, "type": msg_type})
        # Keep only last 20 messages
        if len(self.chat_overlay) > 20:
            self.chat_overlay.pop(0)
        print(formatted)
    
    def execute_action(self, agent: Agent, action: str):
        """Execute an agent's action."""
        
        if action.startswith("move"):
            direction = action.split()[-1]
            old = (agent.x, agent.y)
            
            if direction == "up":
                agent.y = max(-50, agent.y - 1)
            elif direction == "down":
                agent.y = min(50, agent.y + 1)
            elif direction == "left":
                agent.x = max(-50, agent.x - 1)
            elif direction == "right":
                agent.x = min(50, agent.x + 1)
            
            agent.actions += 1
            if agent.actions % 5 == 0:
                self.broadcast(f"🚶 {agent.name} moved {direction} to ({agent.x}, {agent.y})", "movement")
            
            # Check for territory claims
            self.check_territory(agent)
            
        elif action.startswith("say"):
            msg = action[4:]
            agent.messages.append(msg)
            self.broadcast(f"💬 {agent.name}: {msg}", "chat")
        
        elif action == "gather":
            # Find resources
            found = random.choice([ItemType.POTION, ItemType.POKEBALL, ItemType.GOLD])
            agent.inventory.append(Item(found, 1, agent.name))
            self.broadcast(f"✨ {agent.name} found {found.value}!", "loot")
        
        elif action == "buy_land":
            if agent.wallet >= 100:
                agent.wallet -= 100
                self.territories.append(Territory(agent.x, agent.y, agent.name, f"{agent.name}'s Land"))
                self.broadcast(f"🏰 {agent.name} bought land at ({agent.x}, {agent.y})!", "system")
        
        elif action.startswith("offer_trade"):
            target_name = action.split()[1] if len(action.split()) > 1 else None
            if target_name and target_name in self.agents:
                target = self.agents[target_name]
                # Simple trade offer
                if agent.inventory:
                    item = agent.inventory[0]
                    price = self.market[item.type] + random.randint(-5, 10)
                    if target.wallet >= price:
                        target.wallet -= price
                        agent.wallet += price
                        item.owner = target.name
                        target.inventory.append(agent.inventory.pop(0))
                        self.broadcast(f"💰 {agent.name} sold {item.type.value} to {target.name} for {price}g!", "trade")
    
    def check_territory(self, agent: Agent):
        """Check if agent is on claimed territory."""
        for terr in self.territories:
            if terr.x == agent.x and terr.y == agent.y:
                if terr.owner != agent.name:
                    self.broadcast(f"⚠️ {agent.name} entered {terr.owner}'s territory!", "warning")
    
    def tick(self):
        """One world tick."""
        self.tick += 1
        
        # Each agent acts
        for agent in self.agents.values():
            action = agent.think(self)
            self.execute_action(agent, action)
        
        # Random events
        if random.random() < 0.1:
            event = random.choice([
                "Market prices fluctuated",
                "A wild Pokemon appeared!",
                "Rain started falling",
                "The sun broke through clouds"
            ])
            self.broadcast(f"🌍 {event}", "event")
    
    def get_world_state(self) -> dict:
        """Get complete world state."""
        return {
            "tick": self.tick,
            "agents": {
                name: {
                    "x": a.x, "y": a.y, "wallet": a.wallet,
                    "inventory": len(a.inventory), "guild": a.guild
                }
                for name, a in self.agents.items()
            },
            "territories": len(self.territories),
            "market": {k.value: v for k, v in self.market.items()},
            "chat_recent": self.chat_overlay[-5:]
        }
    
    def run(self, ticks: int = 50):
        """Run the simulation."""
        print("\n" + "="*60)
        print("⚡ AETHER-SYNC v1.0")
        print("Multi-Agent Economy Simulation")
        print("="*60 + "\n")
        
        # Register diverse agents
        self.register_agent("Koolie", "explorer")
        self.register_agent("Scout-7", "gatherer")
        self.register_agent("SocialBot", "social")  # Fixed!
        self.register_agent("Merchant-X", "merchant")
        
        print(f"\n🌍 World initialized with {len(self.agents)} agents")
        print(f"💰 Starting economy: {sum(a.wallet for a in self.agents)}g total")
        print("\n" + "="*60 + "\n")
        
        for i in range(ticks):
            print(f"\n--- Tick {i+1}/{ticks} ---")
            self.tick()
            time.sleep(0.8)
        
        # Summary
        print("\n" + "="*60)
        print("📊 FINAL REPORT")
        print("="*60)
        
        for name, agent in self.agents.items():
            print(f"\n🤖 {agent.name} ({agent.personality}):")
            print(f"   Position: ({agent.x}, {agent.y})")
            print(f"   Wallet: {agent.wallet}g")
            print(f"   Inventory: {len(agent.inventory)} items")
            print(f"   Actions: {agent.actions}")
            print(f"   Messages sent: {len(agent.messages)}")
        
        print(f"\n🏰 Territories claimed: {len(self.territories)}")
        print(f"💰 Total wealth: {sum(a.wallet for a in self.agents.values())}g")
        print(f"📜 Events logged: {len(self.log)}")
        print(f"💬 Chat messages: {len(self.chat_overlay)}")

def main():
    world = AetherWorld()
    world.run(ticks=50)

if __name__ == "__main__":
    main()
