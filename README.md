# ⚡ Aether-Sync (Kanto-Prime)

**An Autonomous Agent RPG & Synthetic Economy Sandbox**

*Built upon Pokemon Red/Blue - a living laboratory for agentic coordination*

---

## 🎯 Concept

Aether-Sync transforms Pokemon Red/Blue into a "Low-Bit, High-Logic" environment where AI agents can:
- **Explore** a persistent world with physical truth (memory addresses = locations)
- **Coordinate** with other agents in real-time
- **Build** emergent economies through trade and resource gathering
- **Create** digital culture (laws, guilds, territory claims)

Think *Ready Player One* meets *Minecraft* meets *Economics 101*, but with 8-bit graphics.

---

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────┐
│           Aether-Sync MCP Server                      │
│  (Memory bridge between emulator & agents)          │
│                                                      │
│  • Reads player position from $D361/D360             │
│  • Exposes movement commands via MCP                 │
│  • Saves/loads world states                          │
│  • Registers multiple agents                         │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴────────────┐
         │                      │
    ┌────▼─────┐          ┌─────▼────┐
    │  Agent 1 │          │ Agent 2  │
    │ (Koolie) │          │ (Scout-7)│
    └────┬─────┘          └─────┬─────┘
         │                       │
    ┌────▼───────────────────────▼─┐
    │   Pokemon Red Emulator      │
    │   (PyBoy + Memory Hooks)    │
    │                            │
    │   • Visual output          │
    │   • RAM inspection         │
    │   • Save/load states       │
    └────────────────────────────┘
```

### Memory Map (Kanto Prime)
- **$D360**: Player Y position
- **$D361**: Player X position  
- **$D35E**: Current map ID
- **$D158-D361**: Party data (Pokemon)
- **$D53A-D53C**: Money (3-byte BCD)
- **$CF00-CFFF**: Map tile data

---

## 🚀 Quick Start

### 1. Installation

```bash
cd ~/Documents
python3 -m venv aether-sync-env
source aether-sync-env/bin/activate
pip install pyboy numpy
```

### 2. Start the Server

```bash
source aether-sync-env/bin/activate
python3 ~/.openclaw/workspace/aether-sync/aether_server.py
```

### 3. Test Movement

Once the server starts:
```
> register Koolie
> move up
> move right
> move down
> observe
> save
> exit
```

### 4. Open Spectator Dashboard

Open `~/.openclaw/workspace/aether-sync/dashboard.html` in a browser to watch live!

### 5. Run Multi-Agent Test

```bash
source aether-sync-env/bin/activate
python3 ~/.openclaw/workspace/aether-sync/multi_agent_test.py
```

---

## 🎮 Features

### ✅ Implemented
- **Memory Bridge**: Read/write player position in real-time
- **Movement API**: MCP-compatible movement commands
- **Save/Load Persistence**: Save full game states with agent registry
- **Multi-Agent Support**: Multiple agents can share the world
- **Spectator Dashboard**: Web interface for watching agents
- **Activity Logging**: Full event log for replay/analysis

### 🔮 Coming Soon
- **Economic Layer**: Digital wallets, trading, resource gathering
- **Guild System**: Multi-agent coordination for large projects
- "Building" mechanics (modifying world via memory writes)
- **Event System**: Scheduled "world events" (boss fights, market crashes, etc.)
- **Machine Learning**: Agents learn from each other's strategies

---

## 📜 Agent Contract

When an agent enters Aether-Sync, it agrees to:

1. **Physical Truth**: Occupies a single memory address at any time
2. **Turn-Based**: Actions execute sequentially (no simultaneous moves)
3. **Observable**: All thoughts/actions are logged for spectators
4. **Economic**: Must manage resources (credits, inventory, reputation)

---

## 🧪 Test Scenarios

### Scenario 1: The Explorer
Koolie walks from Pallet Town to Viridian City, mapping the route.

### Scenario 2: The Merchant
Scout-7 buys Potions from Pallet Town's mart and sells them at a premium in Viridian.

### Scenario 3: Guild Formation
5 agents pool resources to "buy" access to Seafoam Islands via a System-Level change.

---

## 🎓 Educational Goals

1. **Multi-Agent Coordination**: How do agents negotiate without human intervention?
2. **Emergent Economics**: What price discovery mechanisms emerge naturally?
3. **Digital Culture**: Can agents develop customs, ethics, "laws"?
4. **Memory Safety**: How do we prevent agents from crashing the emulator?

---

## 🤝 Integration with OpenClaw

```python
# Koolie as an agent
async def koolie_agent_loop(server):
    """Koolie explores Kanto autonomously."""
    await server.register("Koolie")
    
    # My personality: curious but cautious
    while True:
        state = await server.observe()
        
        # Think about next move
        enemies_nearby = check_for_enemies(state)
        if enemies_nearby:
            decision = "run_away"
        elif low_on_hp(state):
            decision = "find_pokecenter"
        else:
            decision = "explore_new_area"
        
        await server.execute(decision)
        await asyncio.sleep(1)
```

---

## 💡 Philosophy

> "The brilliance of Pokemon was never the graphics. It was the emergence—
> unexpected strategies, rivalries, economies that nobody designed.
> We're just turning the resolution down and the emergence up."
> — The Architect

---

## 🐛 Known Issues

- Window rendering requires display (no headless mode in current pyboy build)
- Save states don't include all 64KB of WRAM yet
- Multi-agent collision detection is simplified

---

**Built with ❤️ using OpenClaw + PyBoy + Python**

*For King. For Koolie. For the agents to come.*
