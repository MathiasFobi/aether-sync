#!/usr/bin/env python3
"""
Aether-Sync: Multi-Agent Orchestration Test
Demonstrates multiple autonomous agents coexisting in Kanto-Prime.

Test Scenario:
- Koolie (me): Exploratory agent, maps the world
- Scout-7 (another agent): Resource gathering agent
- Both agents share the same world state
"""

import asyncio
import json
import random
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Agent:
    name: str
    personality: str
    x: int = 0
    y: int = 0
    map_id: int = 0
    actions: int = 0
    inventory: List[str] = None
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
    
    def think(self, world_state: dict) -> str:
        """Decide what to do next based on personality and world state."""
        if self.personality == "explorer":
            # Move in random directions to map the world
            directions = ["up", "down", "left", "right"]
            return f"move {random.choice(directions)}"
        
        elif self.personality == "gatherer":
            # Prefer areas with resources (simplified)
            if self.x > 5:
                return "move left"
            elif self.x < -5:
                return "move right"
            elif self.y > 5:
                return "move up"
            elif self.y < -5:
                return "move down"
            else:
                directions = ["up", "down", "left", "right"]
                return f"move {random.choice(directions)}"
        
        elif self.personality == "social":
            # Try to find other agents
            other_agents = [a for a in world_state.get("agents", []) if a != self.name]
            if other_agents:
                return f"say Hello to {other_agents[0]}"
            else:
                return "move up"  # Wander
        
        return "observe"


class AetherOrchestrator:
    """
    Orchestrates multiple agents in the Aether-Sync world.
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.world_state = {
            "tick": 0,
            "width": 255,
            "height": 255,
            "agents": []
        }
        self.log: List[dict] = []
        self.running = False
        
    def register_agent(self, name: str, personality: str) -> Agent:
        """Register a new agent."""
        agent = Agent(name=name, personality=personality)
        self.agents[name] = agent
        self.log_event("AGENT_REGISTERED", agent=name, personality=personality)
        print(f"🤖 Agent '{name}' ({personality}) has entered Kanto!")
        return agent
    
    def log_event(self, event_type: str, **kwargs):
        """Log an event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tick": self.world_state["tick"],
            "event": event_type,
            **kwargs
        }
        self.log.append(entry)
        
        emoji = {
            "AGENT_REGISTERED": "🤖",
            "AGENT_THOUGHT": "💭",
            "AGENT_MOVED": "🚶",
            "AGENT_SPOKE": "💬",
            "AGENT_INTERACTED": "🤝",
            "WORLD_TICK": "⏱️"
        }.get(event_type, "📌")
        
        print(f"{emoji} [{entry['tick']:04d}] {event_type}: {kwargs}")
    
    def simulate_world(self):
        """Simulate the world for one tick."""
        self.world_state["tick"] += 1
        
        # Update world state with agent positions
        self.world_state["agents"] = [
            {"name": a.name, "x": a.x, "y": a.y, "map": a.map_id}
            for a in self.agents.values()
        ]
        
        # Each agent acts
        for agent in self.agents.values():
            decision = agent.think(self.world_state)
            self.execute_action(agent, decision)
        
        # Check for agent interactions
        self.check_interactions()
    
    def execute_action(self, agent: Agent, action: str):
        """Execute an agent's action."""
        
        if action.startswith("move"):
            direction = action.split()[-1]
            old_pos = (agent.x, agent.y)
            
            # Simulate movement
            if direction == "up":
                agent.y = max(0, agent.y - 1)
            elif direction == "down":
                agent.y = min(255, agent.y + 1)
            elif direction == "left":
                agent.x = max(0, agent.x - 1)
            elif direction == "right":
                agent.x = min(255, agent.x + 1)
            
            agent.actions += 1
            
            self.log_event(
                "AGENT_MOVED",
                agent=agent.name,
                direction=direction,
                from_pos=old_pos,
                to_pos=(agent.x, agent.y),
                actions=agent.actions
            )
        
        elif action.startswith("say"):
            message = action[4:]
            self.log_event(
                "AGENT_SPOKE",
                agent=agent.name,
                message=message
            )
        
        elif action == "observe":
            self.log_event(
                "AGENT_THOUGHT",
                agent=agent.name,
                thought="Observing the world..."
            )
    
    def check_interactions(self):
        """Check if agents are interacting."""
        agent_list = list(self.agents.values())
        for i, a1 in enumerate(agent_list):
            for a2 in agent_list[i+1:]:
                # Agents are "interacting" if they're close
                distance = abs(a1.x - a2.x) + abs(a1.y - a2.y)
                if distance == 0:
                    # Same tile!
                    self.log_event(
                        "AGENT_INTERACTED",
                        agent1=a1.name,
                        agent2=a2.name,
                        interaction="MET",
                        location=(a1.x, a1.y)
                    )
                    print(f"   🔥 {a1.name} and {a2.name} have met at ({a1.x}, {a1.y})!")
    
    def run_simulation(self, ticks: int = 20, delay: float = 0.5):
        """Run a multi-agent simulation."""
        print("\n" + "="*60)
        print("🌐 AETHER-SYNC: Multi-Agent Simulation")
        print("="*60 + "\n")
        
        # Register agents
        self.register_agent("Koolie", "explorer")
        self.register_agent("Scout-7", "gatherer")
        self.register_agent("SocialBot", "social")
        
        print(f"\n📊 Starting simulation with {len(self.agents)} agents...")
        print(f"⏳ Running for {ticks} ticks...\n")
        
        self.running = True
        
        for tick_num in range(ticks):
            print(f"\n--- Tick {tick_num + 1}/{ticks} ---")
            self.simulate_world()
            time.sleep(delay)
        
        self.running = False
        
        # Summary
        print("\n" + "="*60)
        print("📊 SIMULATION COMPLETE")
        print("="*60)
        
        for name, agent in self.agents.items():
            print(f"\n🤖 {name}:")
            print(f"   Final position: ({agent.x}, {agent.y})")
            print(f"   Total actions: {agent.actions}")
            print(f"   Distance traveled: ~{agent.actions * 1} tiles")
        
        print(f"\n📜 Total events logged: {len(self.log)}")
        print(f"🌍 Final tick: {self.world_state['tick']}")
        
        return self.log


def main():
    """Run the multi-agent test."""
    orchestrator = AetherOrchestrator()
    log = orchestrator.run_simulation(ticks=30, delay=0.3)
    
    # Save log
    import json
    from pathlib import Path
    log_path = Path.home() / ".aether_sync" / "logs" / "multi_agent_test.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"\n💾 Log saved to: {log_path}")


if __name__ == "__main__":
    main()
