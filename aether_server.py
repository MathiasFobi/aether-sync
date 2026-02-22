#!/usr/bin/env python3
"""
Aether-Sync MCP Server v0.2
Exposes Pokemon Red/Blue as an MCP-compatible world for autonomous agents.

Features:
- Movement commands (up/down/left/right)
- Memory persistence (save/load states)
- Position/memory observation
- Multi-agent support
"""

import sys
import json
import time
import signal
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from pyboy import PyBoy
from pyboy.utils import WindowEvent

@dataclass
class Agent:
    name: str
    x: int = 0
    y: int = 0
    map_id: int = 0
    last_seen: str = ""
    action_count: int = 0

class AetherMCPServer:
    def __init__(self, rom_path: str, save_dir: str = None):
        self.rom_path = rom_path
        self.save_dir = Path(save_dir) if save_dir else Path.home() / ".aether_sync" / "saves"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize PyBoy
        print(f"🎮 Aether-Sync MCP Server initializing...")
        print(f"📁 ROM: {rom_path}")
        self.pyboy = PyBoy(rom_path, scale=2)
        
        # Memory addresses
        self.PLAYER_X = 0xD361
        self.PLAYER_Y = 0xD360
        self.PLAYER_MAP = 0xD35E
        
        # Agent registry
        self.agents: Dict[str, Agent] = {}
        self.current_agent: Optional[str] = None
        
        # Game state
        self.tick_count = 0
        self.last_save = None
        
        # Boot the game - wait for Nintendo logo
        print("⏳ Booting Pokemon Red...")
        print("   Waiting for Nintendo logo (this takes ~10 seconds)...")
        for i in range(250):
            self.pyboy.tick()
            if i % 50 == 0:
                print(f"   Boot progress: {i}/250")
        
        print("✅ Past Nintendo logo!")
        print("⏭️  Auto-skipping intro...")
        
        # Press START to skip intro
        time.sleep(0.5)
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        for _ in range(30):
            self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        # Wait for title screen and menu
        time.sleep(0.5)
        for _ in range(150):
            self.pyboy.tick()
        
        # Press START at title screen
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        for _ in range(30):
            self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        # Wait for world to load
        print("⏳ Loading save/world...")
        for _ in range(100):
            self.pyboy.tick()
        
        print("✅ Game loaded!")
        self._print_status()
    
    def _get_position(self) -> Dict[str, int]:
        """Read current position from memory."""
        return {
            "x": self.pyboy.memory[self.PLAYER_X],
            "y": self.pyboy.memory[self.PLAYER_Y],
            "map": self.pyboy.memory[self.PLAYER_MAP]
        }
    
    def _print_status(self):
        """Print current game state."""
        pos = self._get_position()
        print(f"📍 Position: X={pos['x']}, Y={pos['y']}, Map={pos['map']}")
    
    def register_agent(self, name: str) -> Dict[str, Any]:
        """Register a new agent in the world."""
        if name not in self.agents:
            self.agents[name] = Agent(name=name)
            print(f"🤖 Agent '{name}' registered")
        
        # Update the agent's current position
        pos = self._get_position()
        agent = self.agents[name]
        agent.x = pos['x']
        agent.y = pos['y']
        agent.map_id = pos['map']
        agent.last_seen = datetime.now().isoformat()
        
        self.current_agent = name
        
        return {
            "success": True,
            "agent": name,
            "position": asdict(agent)
        }
    
    def move(self, direction: str, agent_name: str = None) -> Dict[str, Any]:
        """Move in a direction."""
        if agent_name:
            self.register_agent(agent_name)
        elif not self.current_agent:
            return {"error": "No agent registered. Use register_agent first."}
        
        agent = self.agents.get(agent_name or self.current_agent)
        
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
        
        # Execute movement
        old_pos = self._get_position()
        self.pyboy.send_input(key_map[direction])
        
        # Hold for movement
        for _ in range(15):
            self.pyboy.tick()
        
        self.pyboy.send_input(release_map[direction])
        
        # Update agent
        new_pos = self._get_position()
        agent.x = new_pos['x']
        agent.y = new_pos['y']
        agent.map_id = new_pos['map']
        agent.action_count += 1
        agent.last_seen = datetime.now().isoformat()
        
        self.tick_count += 15
        
        return {
            "success": True,
            "agent": agent.name,
            "direction": direction,
            "old_position": old_pos,
            "new_position": new_pos,
            "moved": (old_pos != new_pos),
            "action_count": agent.action_count
        }
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get complete world state."""
        pos = self._get_position()
        
        # Read some nearby memory for "world data"
        nearby_tiles = []
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                # This is simplified - real tile reading would use VRAM
                nearby_tiles.append({"x": pos['x'] + dx, "y": pos['y'] + dy, "solid": False})
        
        return {
            "tick": self.tick_count,
            "player": pos,
            "agents": {name: asdict(agent) for name, agent in self.agents.items()},
            "current_agent": self.current_agent,
            "nearby": nearby_tiles,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_state(self, name: str = "quicksave") -> Dict[str, Any]:
        """Save current game state."""
        save_path = self.save_dir / f"{name}.state"
        self.pyboy.save_state(str(save_path))
        
        # Also save agent registry
        agent_path = self.save_dir / f"{name}.agents.json"
        agent_data = {name: asdict(agent) for name, agent in self.agents.items()}
        with open(agent_path, 'w') as f:
            json.dump(agent_data, f, indent=2)
        
        self.last_save = {
            "name": name,
            "path": str(save_path),
            "agents": agent_path,
            "time": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "save": self.last_save
        }
    
    def load_state(self, name: str = "quicksave") -> Dict[str, Any]:
        """Load a saved game state."""
        save_path = self.save_dir / f"{name}.state"
        agent_path = self.save_dir / f"{name}.agents.json"
        
        if not save_path.exists():
            return {"error": f"Save '{name}' not found"}
        
        self.pyboy.load_state(str(save_path))
        
        # Load agent registry
        if agent_path.exists():
            with open(agent_path, 'r') as f:
                agent_data = json.load(f)
                self.agents = {name: Agent(**data) for name, data in agent_data.items()}
        
        pos = self._get_position()
        
        return {
            "success": True,
            "loaded": name,
            "position": pos,
            "agents_loaded": len(self.agents)
        }
    
    def list_saves(self) -> List[str]:
        """List available saves."""
        saves = []
        for f in self.save_dir.glob("*.state"):
            saves.append(f.stem)
        return saves
    
    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP protocol request."""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return {
                "server": "aether-sync",
                "version": "0.2",
                "world": "kanto-prime",
                "game": "Pokemon Red/Blue",
                "capabilities": ["move", "observe", "save", "load", "register"]
            }
        
        elif method == "register_agent":
            return self.register_agent(params.get("name", "unknown"))
        
        elif method == "move":
            return self.move(
                params.get("direction", "up"),
                params.get("agent")
            )
        
        elif method == "observe":
            return {"success": True, "state": self.get_world_state()}
        
        elif method == "save":
            return self.save_state(params.get("name", "quicksave"))
        
        elif method == "load":
            return self.load_state(params.get("name", "quicksave"))
        
        elif method == "list_saves":
            return {"success": True, "saves": self.list_saves()}
        
        else:
            return {"error": f"Unknown method: {method}"}
    
    def run_interactive(self):
        """Run in interactive MCP mode."""
        print("\n🌐 Aether-Sync MCP Server ready")
        print("   Commands: init, register <name>, move <dir>, observe, save [name], load [name], exit\n")
        
        try:
            while True:
                line = input("> ").strip()
                if not line:
                    continue
                
                parts = line.split()
                cmd = parts[0]
                
                if cmd == "exit":
                    break
                elif cmd == "init":
                    result = self.handle_mcp_request({"method": "initialize"})
                elif cmd == "register":
                    name = parts[1] if len(parts) > 1 else "agent"
                    result = self.handle_mcp_request({"method": "register_agent", "params": {"name": name}})
                elif cmd == "move":
                    direction = parts[1] if len(parts) > 1 else "up"
                    result = self.handle_mcp_request({"method": "move", "params": {"direction": direction}})
                elif cmd == "observe":
                    result = self.handle_mcp_request({"method": "observe"})
                elif cmd == "save":
                    name = parts[1] if len(parts) > 1 else "quicksave"
                    result = self.handle_mcp_request({"method": "save", "params": {"name": name}})
                elif cmd == "load":
                    name = parts[1] if len(parts) > 1 else "quicksave"
                    result = self.handle_mcp_request({"method": "load", "params": {"name": name}})
                else:
                    result = {"error": f"Unknown command: {cmd}"}
                
                print(json.dumps(result, indent=2))
        
        except KeyboardInterrupt:
            pass
        finally:
            print("\n👋 Shutting down Aether-Sync...")
            self.pyboy.stop()

def main():
    import sys
    
    # Find ROM
    rom_path = Path.home() / "Documents" / "Pokemon" / "Pokemon - Red Version (UE) [S][!].gb"
    
    if not rom_path.exists():
        print(f"❌ ROM not found: {rom_path}")
        sys.exit(1)
    
    server = AetherMCPServer(str(rom_path))
    server.run_interactive()

if __name__ == "__main__":
    main()
