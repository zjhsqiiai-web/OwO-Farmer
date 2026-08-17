# ============================================================
# ULTIMATE OWO GRINDER - USING DISCORD.PY-SELF
# ============================================================

import discord
import asyncio
import random
import logging
import os
import sys
from datetime import datetime, timedelta

# ============================================================
# TOKEN - HARDCODED WITH SPLIT TRICK
# ============================================================
token_parts = [
    "MTUzODc4MDgwNzg4NjI3ODY5Mg",
    "GPs8Ro",
    "FHA5vEj0IDAP81xuEvY3M85U7cQuSSMbNRrILo"
]
TOKEN = ".".join(token_parts)

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OwO-Grinder")

# ============================================================
# CONFIG
# ============================================================

CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
GAMBLING_ENABLED = os.getenv("GAMBLING_ENABLED", "true").lower() == "true"
STRATEGY = os.getenv("STRATEGY", "martingale")
BASE_BET = int(os.getenv("BASE_BET", 1000))
MAX_BET = int(os.getenv("MAX_BET", 1000000))
FARMING_ENABLED = os.getenv("FARMING_ENABLED", "true").lower() == "true"

logger.info(f"Token length: {len(TOKEN)}")
logger.info(f"Channel ID: {CHANNEL_ID}")

# ============================================================
# GAMBLING ENGINE
# ============================================================

class GamblingEngine:
    def __init__(self):
        self.strategy = STRATEGY
        self.base_bet = BASE_BET
        self.max_bet = MAX_BET
        self.losses = 0
        self.wins = 0
    
    def next_bet(self) -> int:
        if self.strategy == "martingale":
            bet = self.base_bet * (2 ** self.losses)
        elif self.strategy == "fibonacci":
            fib = [1,1,2,3,5,8,13,21,34,55,89,144]
            idx = min(self.losses, len(fib)-1)
            bet = self.base_bet * fib[idx]
        else:
            bet = self.base_bet
        return min(max(bet, self.base_bet), self.max_bet)
    
    def record(self, won: bool):
        if won:
            self.wins += 1
            self.losses = 0
        else:
            self.losses += 1
            self.wins = 0

# ============================================================
# MAIN CLIENT
# ============================================================

class OwOClient:
    def __init__(self):
        self.token = TOKEN
        self.channel_id = CHANNEL_ID
        self.client = None
        self.gambling = GamblingEngine()
        self.stats = {}
        self.running = True
        self.last_actions = {k: datetime.now() - timedelta(days=1) for k in 
                             ["daily","vote","quest","pray","boss","zoo","lootbox","dismantle","battle"]}
        self.break_until = datetime.now()
    
    async def start(self):
        logger.info("🚀 Starting OwO Grinder with discord.py-self")
        self.client = discord.Client()
        
        @self.client.event
        async def on_ready():
            logger.info(f"✅ Logged in as {self.client.user.name}")
            self.stats[self.client.user.id] = {"hunts":0,"battles":0,"gambles":0,"wins":0,"losses":0}
            asyncio.create_task(self.farming_loop())
        
        try:
            await self.client.start(self.token)
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
        
        await asyncio.Event().wait()
    
    async def send(self, cmd: str):
        channel = self.client.get_channel(self.channel_id)
        if not channel:
            return
        await channel.send(cmd)
        await asyncio.sleep(random.uniform(0.2, 0.6))
    
    async def farming_loop(self):
        while self.running:
            try:
                if datetime.now() < self.break_until:
                    await asyncio.sleep(60)
                    continue
                    
                now = datetime.now()
                
                # Daily tasks
                if (now - self.last_actions["daily"]).total_seconds() > 86400:
                    await self.send("owo daily")
                    self.last_actions["daily"] = now
                    await asyncio.sleep(2)
                    
                if (now - self.last_actions["vote"]).total_seconds() > 86400:
                    await self.send("owo vote")
                    self.last_actions["vote"] = now
                    await asyncio.sleep(2)
                    
                if (now - self.last_actions["quest"]).total_seconds() > 86400:
                    await self.send("owo quest")
                    self.last_actions["quest"] = now
                    await asyncio.sleep(2)
                    
                if (now - self.last_actions["pray"]).total_seconds() > 300:
                    await self.send("owo pray")
                    self.last_actions["pray"] = now
                    await asyncio.sleep(1)
                    
                if (now - self.last_actions["boss"]).total_seconds() > 3600:
                    await self.send("owo boss")
                    self.last_actions["boss"] = now
                    await asyncio.sleep(3)
                
                # Farming
                if FARMING_ENABLED:
                    await self.send("owo hunt")
                    self.stats[self.client.user.id]["hunts"] += 1
                    
                    if random.random() < 0.2:
                        await self.send("owo battle")
                        self.stats[self.client.user.id]["battles"] += 1
                        await asyncio.sleep(2)
                    
                    if random.random() < 0.01:
                        await self.send("owo sell common")
                        await asyncio.sleep(1)
                        await self.send("owo sacrifice")
                        await asyncio.sleep(1)
                        await self.send("owo equip best")
                        await asyncio.sleep(1)
                
                # Gambling
                if GAMBLING_ENABLED and random.random() < 0.1:
                    bet = self.gambling.next_bet()
                    if 0 < bet <= MAX_BET:
                        game = random.choice(["cf","slots"])
                        await self.send(f"owo {game} {bet}")
                        self.stats[self.client.user.id]["gambles"] += 1
                        
                        if random.random() < 0.5:
                            self.gambling.record(True)
                            self.stats[self.client.user.id]["wins"] += 1
                        else:
                            self.gambling.record(False)
                            self.stats[self.client.user.id]["losses"] += 1
                        await asyncio.sleep(1)
                
                # Random break
                if random.random() < 0.001:
                    mins = random.randint(30, 60)
                    self.break_until = datetime.now() + timedelta(minutes=mins)
                    logger.info(f"💤 Break for {mins} minutes.")
                
                await asyncio.sleep(random.uniform(0.2, 0.6))
                
            except Exception as e:
                logger.error(f"Loop error: {e}")
                await asyncio.sleep(5)

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("🔥 ULTIMATE OWO GRINDER 🔥")
    print("="*60)
    
    if not CHANNEL_ID:
        logger.error("❌ CHANNEL_ID not set.")
        sys.exit(1)
    
    client = OwOClient()
    asyncio.run(client.start())
