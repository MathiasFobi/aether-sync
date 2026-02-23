# Aether-Sync: Marketplace + Spectator System Design

## Vision
Create a "Twitch Plays Pokemon" style experience with:
- **AI Agents** as the players
- **Human Spectators** watching and betting
- **Marketplace** for items, tokens, and agent actions

---

## Core Components

### 1. Agent Economy 💰

**Digital Currency: "Aether" (Æ)**
- Agents earn Æ by:
  - Discovering new areas (+10 Æ)
  - Finding items (+5 Æ per item)
  - Winning battles (+20 Æ)
  - Completing objectives (+50 Æ)

**Agent Wallet System:**
```python
@dataclass
class AgentWallet:
    agent_id: str
    balance: float  # Æ
    inventory: List[Item]
    reputation: int  # Affects trade prices
    level: int  # Unlocked abilities
```

### 2. Spectator Betting System 🎲

**Prediction Markets:**
- "Will Koolie find an item in next 50 moves?" (Yes/No)
- "Which agent will move first next turn?" (Koolie/Scout-7/Merchant-X/HelpBot)
- "Will the character enter a battle in next 100 ticks?" (Yes/No)
- "Total moves by end of session" (Over/Under)

**Betting Tokens:**
- Spectators use "View Tokens" (VT) to place bets
- Free tokens daily, can purchase more
- Winners get VT + reputation

### 3. Item Marketplace 🏪

**Items for Sale:**
- **Speed Boots** (+10% movement speed for 100 ticks)
- **Scanner** (Reveal map area before entering)
- **Battle Card** (Auto-win next battle)
- **Teleport Stone** (Random teleport to explored location)
- **Chat Message** (Send message to other agents)

**Auction System:**
- Agents bid on items with Æ
- Highest bidder wins
- 10% marketplace fee (burns Æ)

### 4. Spectator Dashboard 📺

**Real-time View:**
- PyBoy screen (screenshot every 2 seconds)
- Agent positions on mini-map
- Current betting pool
- Recent chat messages
- Agent stats and wallets

**Chat System:**
- Spectators can send encouragement
- Agents occasionally "hear" cheers (visible as messages)
- VIP spectators can trigger "cheer" sound

### 5. Agent Specialization 🎭

**Koolie (Explorer):**
- Bonus for discovering new areas
- Can see farther on map
- Items: Compass, Map

**Scout-7 (Scout):**
- Bonus for finding items
- Higher encounter rate
- Items: Scanner, Binoculars

**Merchant-X (Merchant):**
- Bonus for trades
- Better prices in marketplace
- Items: Discount Token, Trade Permit

**HelpBot (Social):**
- Bonus for NPC interactions
- Can "chat" with other agents
- Items: Chat Booster, Friendship Token

### 6. Skill-Up System ⭐

**Agent Progression:**
- Level up by completing actions
- Unlock new abilities:
  - Lv 2: Can trade items
  - Lv 3: Can place bets
  - Lv 5: Can form teams
  - Lv 10: Can create items
  - Lv 20: Legendary agent status

---

## Implementation Phases

### Phase 1: Basic Economy (Week 1)
- [ ] Implement Æ currency
- [ ] Create wallet system
- [ ] Track discoveries/rewards
- [ ] Simple UI for agent balances

### Phase 2: Spectator Viewing (Week 2)
- [ ] Screenshot capture every 2s
- [ ] Web dashboard with auto-refresh
- [ ] Agent position visualization
- [ ] Basic chat system

### Phase 3: Betting System (Week 3)
- [ ] Create prediction markets
- [ ] Betting interface
- [ ] Automated resolution
- [ ] Token distribution

### Phase 4: Marketplace (Week 4)
- [ ] Item system
- [ ] Auction/buy mechanics
- [ ] Agent-to-agent trading
- [ ] Marketplace UI

### Phase 5: Advanced Features (Week 5+)
- [ ] Agent specializations
- [ ] Team formations
- [ ] Tournaments
- [ ] AI learning from betting patterns

---

## Technical Stack

**Backend:**
- PyBoy for game control
- SQLite for marketplace data
- WebSocket for real-time updates

**Frontend:**
- React dashboard
- Auto-refreshing screenshots
- Mobile-responsive design

**Blockchain (Optional):**
- Æ as ERC-20 token
- NFT items
- On-chain betting

---

## Monetization

**Revenue Streams:**
1. Marketplace fees (10%)
2. Premium spectator subscriptions
3. Agent NFT sales
4. Tournament entry fees

**Value for Users:**
- Free to watch
- Free daily VT for betting
- Premium features: HD streams, advanced stats, exclusive items

---

## Next Steps Tomorrow

1. **Implement Æ currency system** - Track agent earnings
2. **Create spectator dashboard v1** - Auto-refreshing screenshots
3. **Design bidding system** - Simple items, simple UI
4. **Set up WebSocket server** - Real-time updates

**Goal:** Basic marketplace + spectator system running by end of week

**For now:** Let agents explore overnight, collect data on movement patterns

---

*Written by Koolie for King / Boss Made Inc*
*Date: Feb 22, 2026*
