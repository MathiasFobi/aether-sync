#!/usr/bin/env python3
"""
Aether-Sync Enhanced v1.1
Full-featured with enhanced chat overlay, inventory GUI, and trade system
"""

import sys
import time
import json
import random
import threading
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ItemType(Enum):
    POTION = "potion"
    POKEBALL = "pokeball"
    GOLD_NUGGET = "gold_nugget"
    RARE_CANDY = "rare_candy"
    LAND_DEED = "land_deed"
    MYSTERY_BOX = "mystery_box"

@dataclass
class Item:
    type: ItemType
    quantity: int = 1
    owner: str = ""
    value: int = 10

@dataclass
class Territory:
    x: int
    y: int
    owner: str
    name: str
    value: int = 100
    tax_rate: float = 0.05

@dataclass
class Agent:
    name: str
    personality: str
    x: int = 6
    y: int = 4
    wallet: int = 100
    inventory: List[Item] = field(default_factory=list)
    actions: int = 0
    reputation: int = 50
    guild: Optional[str] = None
    level: int = 1
    xp: int = 0
    
    def think(self, world) -> str:
        """AI decision making with personality."""
        if self.personality == "explorer":
            # Explore toward unexplored areas
            if self.y > 10:
                return "move up"
            elif self.y < 2:
                return "move down"
            elif self.x > 15:
                return "move left"
            else:
                return random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "gatherer":
            # Search for items or move strategically
            if random.random() > 0.7:
                return "search"
            elif self.wallet >= 150:
                return "buy_land"
            else:
                return random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "social":
            # Find others and interact
            nearest = world.get_nearest_agent(self)
            if nearest:
                dx = nearest.x - self.x
                dy = nearest.y - self.y
                
                if abs(dx) <= 1 and abs(dy) <= 1:
                    if random.random() > 0.5:
                        return f"say Hey {nearest.name}! Want to team up?"
                    else:
                        return f"offer_trade {nearest.name}"
                
                if abs(dx) > abs(dy):
                    return "right" if dx > 0 else "left"
                else:
                    return "down" if dy > 0 else "up"
            return random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "merchant":
            # Find rich agents and sell to them
            target = world.get_richest_agent(exclude=self.name)
            if target:
                dx = target.x - self.x
                dy = target.y - self.y
                
                if abs(dx) <= 1 and abs(dy) <= 1 and self.inventory:
                    return f"offer_trade {target.name}"
                elif abs(dx) > abs(dy):
                    return "right" if dx > 0 else "left"
                else:
                    return "down" if dy > 0 else "up"
            return random.choice(["up", "down", "left", "right"])
        
        elif self.personality == "fighter":
            # Challenge other agents
            others = [a for a in world.agents.values() if a.name != self.name]
            if others:
                target = random.choice(others)
                if abs(target.x - self.x) <= 1 and abs(target.y - self.y) <= 1:
                    return f"challenge {target.name}"
                dx = target.x - self.x
                dy = target.y - self.y
                if abs(dx) > abs(dy):
                    return "right" if dx > 0 else "left"
                return "down" if dy > 0 else "up"
            return random.choice(["up", "down", "left", "right"])
        
        return "move up"

class AetherEnhanced:
    """Enhanced Aether world with full features."""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.territories: List[Territory] = []
        self.chat_history: List[Dict] = []
        self.tick = 0
        self.market_prices = {
            ItemType.POTION: 20,
            ItemType.POKEBALL: 50,
            ItemType.GOLD_NUGGET: 100,
            ItemType.RARE_CANDY: 200,
            ItemType.LAND_DEED: 150,
            ItemType.MYSTERY_BOX: 75
        }
        self.events = [
            "A wild Pidgey flies overhead",
            "Market prices shift slightly",
            "A trainer walks by",
            "Wind rustles the grass",
            "Sunlight breaks through clouds",
            "You hear a distant cry",
            "A merchant passes through",
            "The air feels electric"
        ]
    
    def register_agent(self, name: str, personality: str) -> Agent:
        """Register a new agent with flair."""
        agent = Agent(name=name, personality=personality)
        # Random spawn in Pallet Town area
        agent.x = random.randint(4, 8)
        agent.y = random.randint(3, 7)
        agent.wallet = 100 + random.randint(0, 100)
        self.agents[name] = agent
        
        self.chat("system", f"🎉 {name} the {personality.title()} enters Kanto-Prime!", "join")
        return agent
    
    def get_nearest_agent(self, agent: Agent) -> Optional[Agent]:
        """Find nearest other agent."""
        others = [a for a in self.agents.values() if a.name != agent.name]
        if not others:
            return None
        return min(others, key=lambda a: abs(a.x - agent.x) + abs(a.y - agent.y))
    
    def get_richest_agent(self, exclude: str = None) -> Optional[Agent]:
        """Find wealthiest agent."""
        candidates = [a for a in self.agents.values() if a.name != exclude] if exclude else list(self.agents.values())
        if not candidates:
            return None
        return max(candidates, key=lambda a: a.wallet)
    
    def chat(self, agent: str, message: str, msg_type: str = "chat"):
        """Add to chat with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "time": timestamp,
            "agent": agent,
            "text": message,
            "type": msg_type,
            "tick": self.tick
        }
        self.chat_history.append(entry)
        
        # Keep only last 30 messages
        if len(self.chat_history) > 30:
            self.chat_history.pop(0)
        
        # Print with styling
        emoji = {
            "join": "🎉",
            "movement": "🚶",
            "chat": "💬",
            "trade": "💰",
            "loot": "✨",
            "system": "🌍",
            "event": "🔔",
            "battle": "⚔️",
            "levelup": "⭐"
        }.get(msg_type, "📌")
        
        # Color codes for terminals
        colors = {
            "Koolie": "\033[94m",      # Blue
            "Scout-7": "\033[92m",     # Green
            "Merchant-X": "\033[93m",  # Yellow
            "HelpBot": "\033[96m",     # Cyan
            "Warrior-Z": "\033[91m",   # Red
            "system": "\033[90m"      # Gray
        }
        reset = "\033[0m"
        color = colors.get(agent, "")
        
        print(f"{emoji} [{timestamp}] {color}{agent}{reset}: {message}")
    
    def execute_action(self, agent: Agent, action: str):
        """Execute an action with full effects."""
        
        if action.startswith("move"):
            direction = action.split()[-1]
            old = (agent.x, agent.y)
            
            # Movement
            if direction == "up":
                agent.y = max(4, agent.y - 1)
            elif direction == "down":
                agent.y = min(11, agent.y + 1)
            elif direction == "left":
                agent.x = max(4, agent.x - 1)
            elif direction == "right":
                agent.x = min(11, agent.x + 1)
            
            agent.actions += 1
            agent.xp += 1
            
            # Level up check
            if agent.xp >= agent.level * 10:
                agent.level += 1
                agent.xp = 0
                agent.wallet += 50
                self.chat(agent.name, f"Leveled up to {agent.level}! Gained 50g bonus!", "levelup")
            
            # Announce movement periodically
            if agent.actions % 5 == 0:
                self.chat(agent.name, f"Moving {direction} to ({agent.x}, {agent.y})", "movement")
            
            # Check territory
            self.check_territory(agent)
        
        elif action.startswith("say"):
            msg = action[4:]
            self.chat(agent.name, msg, "chat")
        
        elif action == "search":
            # Find items
            found_type = random.choice(list(ItemType))
            item = Item(found_type, 1, agent.name, self.market_prices[found_type])
            agent.inventory.append(item)
            agent.xp += 5
            self.chat(agent.name, f"Found {found_type.value}!", "loot")
        
        elif action == "buy_land":
            if agent.wallet >= 150:
                agent.wallet -= 150
                territory = Territory(agent.x, agent.y, agent.name, f"{agent.name}'s Land")
                self.territories.append(territory)
                agent.inventory.append(Item(ItemType.LAND_DEED, 1, agent.name, 150))
                self.chat(agent.name, f"Bought land at ({agent.x}, {agent.y})!", "system")
        
        elif action.startswith("offer_trade"):
            target_name = action.split()[1] if len(action.split()) > 1 else None
            if target_name and target_name in self.agents:
                target = self.agents[target_name]
                if agent.inventory and target.wallet >= 30:
                    item = agent.inventory[0]
                    price = self.market_prices[item.type] + random.randint(-5, 5)
                    
                    if target.wallet >= price:
                        target.wallet -= price
                        agent.wallet += price
                        item.owner = target.name
                        target.inventory.append(agent.inventory.pop(0))
                        self.chat(agent.name, f"Sold {item.type.value} to {target.name} for {price}g!", "trade")
        
        elif action.startswith("challenge"):
            target_name = action.split()[1] if len(action.split()) > 1 else None
            if target_name and target_name in self.agents:
                target = self.agents[target_name]
                # Simple battle simulation
                power = random.randint(1, 10) + agent.level
                target_power = random.randint(1, 10) + target.level
                
                if power > target_power:
                    winnings = min(target.wallet // 10, 50)
                    target.wallet -= winnings
                    agent.wallet += winnings
                    self.chat(agent.name, f"Defeated {target.name} in battle! Won {winnings}g!", "battle")
                else:
                    loss = min(agent.wallet // 10, 30)
                    agent.wallet -= loss
                    target.wallet += loss
                    self.chat(agent.name, f"Lost to {target.name}! Lost {loss}g!", "battle")
    
    def check_territory(self, agent: Agent):
        """Check territory interactions."""
        for terr in self.territories:
            if terr.x == agent.x and terr.y == agent.y:
                if terr.owner != agent.name:
                    tax = int(agent.wallet * terr.tax_rate)
                    agent.wallet -= tax
                    owner_agent = self.agents.get(terr.owner)
                    if owner_agent:
                        owner_agent.wallet += tax
                    self.chat(agent.name, f"Paid {tax}g tax to {terr.owner}'s territory", "system")
    
    def tick_world(self):
        """One world tick."""
        self.tick += 1
        
        # Each agent acts
        for agent in self.agents.values():
            action = agent.think(self)
            self.execute_action(agent, action)
        
        # Random events
        if random.random() < 0.12:
            self.chat("World", random.choice(self.events), "event")
        
        # Market fluctuation
        if self.tick % 10 == 0:
            for item_type in self.market_prices:
                change = random.randint(-2, 5)
                self.market_prices[item_type] = max(10, self.market_prices[item_type] + change)
    
    def print_status(self):
        """Print fancy status panel."""
        print("\n" + "─" * 65)
        print("👥 AGENT STATUS | 🌍 Tick: " + str(self.tick))
        print("─" * 65)
        
        for name, agent in self.agents.items():
            inv_summary = f"{len(agent.inventory)} items" if agent.inventory else "Empty"
            bar = "█" * agent.level + "░" * (10 - agent.level)
            print(f"🤖 {name:12} | ({agent.x:2}, {agent.y:2}) | 💰 {agent.wallet:4}g | 🎒 {inv_summary:10} | LVL {agent.level} {bar}")
        
        print("─" * 65)
        if self.territories:
            print(f"🏰 Territories: {len(self.territories)} | Tax revenue: {sum(t.tax_rate * 100 for t in self.territories):.1f}%")
        print("─" * 65)
    
    def print_chat_history(self, n: int = 8):
        """Print recent chat."""
        print("\n💬 RECENT MESSAGES:")
        for msg in self.chat_history[-n:]:
            emoji = {"chat": "💬", "movement": "🚶", "trade": "💰", "loot": "✨", 
                    "system": "🌍", "event": "🔔", "battle": "⚔️", "levelup": "⭐", "join": "🎉"}.get(msg["type"], "📌")
            print(f"  {emoji} [{msg['time']}] {msg['agent']}: {msg['text']}")
    
    def run(self, ticks: int = 50):
        """Run the simulation."""
        print("\n" + "=" * 65)
        print("⚡ AETHER-SYNC ENHANCED v1.1")
        print("Multi-Agent Economy with Chat Overlay")
        print("=" * 65 + "\n")
        
        # Register agents
        self.register_agent("Koolie", "explorer")
        self.register_agent("Scout-7", "gatherer")
        self.register_agent("Merchant-X", "merchant")
        self.register_agent("HelpBot", "social")
        self.register_agent("Warrior-Z", "fighter")
        
        print(f"\n🌍 World initialized with {len(self.agents)} agents")
        print(f"💰 Total starting wealth: {sum(a.wallet for a in self.agents.values())}g")
        print(f"🏁 Running for {ticks} ticks...\n")
        
        for i in range(ticks):
            print(f"\n{'═' * 65}")
            print(f"TICK {i+1:2d}/{ticks} | {datetime.now().strftime('%H:%M:%S')}")
            print("═" * 65)
            
            self.tick_world()
            
            # Show status every 5 ticks
            if (i + 1) % 5 == 0:
                self.print_status()
            
            time.sleep(1.0)
        
        # Final report
        print("\n" + "=" * 65)
        print("📊 FINAL REPORT")
        print("=" * 65)
        
        # Sort by wealth
        sorted_agents = sorted(self.agents.items(), key=lambda x: x[1].wallet, reverse=True)
        
        print(f"\n🏆 RANKINGS:")
        for rank, (name, agent) in enumerate(sorted_agents, 1):
            print(f"\n  #{rank} {name} ({agent.personality})")
            print(f"     💰 {agent.wallet}g | LVL {agent.level} | XP {agent.xp}")
            print(f"     📦 {len(agent.inventory)} items | {agent.actions} actions")
            if agent.inventory:
                items = ", ".join(f"{i.type.value} x{i.quantity}" for i in agent.inventory[:3])
                print(f"     🎒 {items}")
        
        print(f"\n🏰 Territories claimed: {len(self.territories)}")
        for t in self.territories:
            print(f"   • {t.owner}'s territory at ({t.x}, {t.y})")
        
        print(f"\n📜 Total events: {len(self.chat_history)}")
        print(f"💬 Chat messages: {len([m for m in self.chat_history if m['type'] == 'chat'])}")
        print(f"💰 Trades completed: {len([m for m in self.chat_history if m['type'] == 'trade'])}")
        print(f"⚔️ Battles fought: {len([m for m in self.chat_history if m['type'] == 'battle'])}")
        
        # Show final chat
        self.print_chat_history(10)

def main():
    world = AetherEnhanced()
    world.run(ticks=30)

if __name__ == "__main__":
    main()
