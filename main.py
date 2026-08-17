# ============================================================
# ULTIMATE OWO GRINDER - RAILWAY OPTIMIZED
# ============================================================

import discord
import asyncio
import random
import logging
import os
import sys
from datetime import datetime, timedelta

# ============================================================
# READ DISCORD_TOKEN FROM ENV WITH CLEANUP
# ============================================================

TOKEN_RAW = os.getenv("DISCORD_TOKEN", "")
logger.info(f"RAW TOKEN: {repr(TOKEN_RAW)}")  # This shows hidden characters
logger.info(f"TOKEN LENGTH: {len(TOKEN_RAW)}")

CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
GAMBLING_ENABLED = os.getenv("GAMBLING_ENABLED", "true").lower() == "true"
STRATEGY = os.getenv("STRATEGY", "martingale")
BASE_BET = int(os.getenv("BASE_BET", 1000))
MAX_BET = int(os.getenv("MAX_BET", 1000000))
FARMING_ENABLED = os.getenv("FARMING_ENABLED", "true").lower() == "true"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OwO-Grinder")

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
        elif self.strategy == "d_alembert":
            net = self.losses - self.wins
            bet = self.base_bet + net * 1000
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
# MAIN BOT CLIENT
# ============================================================

class OwOClient:
    def __init__(self):
        self.DISCORD_TOKEN = DISCORD_TOKEN
        self.channel_id = CHANNEL_ID
        self.clients = {}
        self.gambling = GamblingEngine()
        self.stats = {}
        self.running = True
        self.last_actions = {k: datetime.now() - timedelta(days=1) for k in 
                             ["daily","vote","quest","pray","boss","zoo","lootbox","dismantle","battle"]}
        self.break_until = datetime.now()
    
    async def start(self):
        logger.info(f"🚀 Starting with {len(self.DISCORD_TOKEN)} token(s)")
        if not self.DISCORD_TOKEN:
            logger.error("❌ No DISCORD_TOKEN found!")
            return
            
        for token in self.DISCORD_TOKEN:
            client = discord.Client()
            
            @client.event
            async def on_ready():
                logger.info(f"✅ Logged in as {client.user.name}")
                self.stats[client.user.id] = {"hunts":0,"battles":0,"gambles":0,"wins":0,"losses":0}
                asyncio.create_task(self.farming_loop(client))
            
            try:
                await client.start(token)
                self.clients[token] = client
            except Exception as e:
                logger.error(f"Failed to start token: {e}")
        
        await asyncio.Event().wait()
    
    async def send(self, client, cmd: str):
        channel = client.get_channel(self.channel_id)
        if not channel:
            logger.warning(f"Channel {self.channel_id} not found")
            return
        await client.send_message(channel, cmd)
        await asyncio.sleep(random.uniform(0.2, 0.6))
    
    async def farming_loop(self, client):
        while self.running:
            try:
                if datetime.now() < self.break_until:
                    await asyncio.sleep(60)
                    continue
                    
                now = datetime.now()
                
                # Daily tasks
                if (now - self.last_actions["daily"]).total_seconds() > 86400:
                    await self.send(client, "owo daily")
                    self.last_actions["daily"] = now
                    await asyncio.sleep(2)
                    
                if (now - self.last_actions["vote"]).total_seconds() > 86400:
                    await self.send(client, "owo vote")
                    self.last_actions["vote"] = now
                    await asyncio.sleep(2)
                    
                if (now - self.last_actions["quest"]).total_seconds() > 86400:
                    await self.send(client, "owo quest")
                    self.last_actions["quest"] = now
                    await asyncio.sleep(2)
                    
                if (now - self.last_actions["pray"]).total_seconds() > 300:
                    await self.send(client, "owo pray")
                    self.last_actions["pray"] = now
                    await asyncio.sleep(1)
                    
                if (now - self.last_actions["boss"]).total_seconds() > 3600:
                    await self.send(client, "owo boss")
                    self.last_actions["boss"] = now
                    await asyncio.sleep(3)
                
                # Farming
                if FARMING_ENABLED:
                    await self.send(client, "owo hunt")
                    self.stats[client.user.id]["hunts"] += 1
                    
                    if random.random() < 0.2:
                        await self.send(client, "owo battle")
                        self.stats[client.user.id]["battles"] += 1
                        await asyncio.sleep(2)
                    
                    if random.random() < 0.01:
                        await self.send(client, "owo sell common")
                        await asyncio.sleep(1)
                        await self.send(client, "owo sacrifice")
                        await asyncio.sleep(1)
                        await self.send(client, "owo equip best")
                        await asyncio.sleep(1)
                
                # Gambling
                if GAMBLING_ENABLED and random.random() < 0.1:
                    bet = self.gambling.next_bet()
                    if 0 < bet <= MAX_BET:
                        game = random.choice(["cf","slots"])
                        await self.send(client, f"owo {game} {bet}")
                        self.stats[client.user.id]["gambles"] += 1
                        
                        if random.random() < 0.5:
                            self.gambling.record(True)
                            self.stats[client.user.id]["wins"] += 1
                        else:
                            self.gambling.record(False)
                            self.stats[client.user.id]["losses"] += 1
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
    
    if not DISCORD_TOKEN:
        logger.error("❌ No DISCORD_TOKEN found. Set DISCORD_TOKEN env var.")
        sys.exit(1)
        
    if not CHANNEL_ID:
        logger.error("❌ CHANNEL_ID not set.")
        sys.exit(1)
    
    client = OwOClient()
    asyncio.run(client.start())
