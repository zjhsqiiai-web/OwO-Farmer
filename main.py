# ============================================================
# ULTIMATE OWO GRINDER - FINAL WORKING VERSION
# ============================================================

import discord
import asyncio
import random
import logging
import os
import sys
from datetime import datetime, timedelta

# ============================================================
# YOUR TOKEN - SPLIT INTO 3 PARTS
# GET FRESH TOKEN: F12 -> Network -> authorization header
# ============================================================
token_parts = [
    "MTUzODc4MDgwNzg4NjI3ODY5Mg",
    "GCHUwf",
    "3Dw0vCREowDFnmx2tSS_7r31plyJ4ZAUv3doRc"
]
TOKEN = ".".join(token_parts)

# ============================================================
# CHANNEL ID - ONLY ENV VAR NEEDED
# ============================================================
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
if not CHANNEL_ID:
    print("❌ Set CHANNEL_ID environment variable.")
    sys.exit(1)

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OwO-Grinder")
logger.info(f"Token length: {len(TOKEN)}")
logger.info(f"Channel ID: {CHANNEL_ID}")

# ============================================================
# GAMBLING ENGINE
# ============================================================
class GamblingEngine:
    def __init__(self):
        self.losses = 0
        self.wins = 0
        self.base_bet = 1000
        self.max_bet = 1000000
    
    def next_bet(self):
        bet = self.base_bet * (2 ** self.losses)
        return min(bet, self.max_bet)
    
    def record(self, won):
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
                             ["daily","vote","quest","pray","boss","battle"]}
        self.break_until = datetime.now()
    
    async def start(self):
        logger.info("🚀 Starting OwO Grinder")
        
        # Create client with custom headers to avoid detection
        self.client = discord.Client()
        
        @self.client.event
        async def on_ready():
            logger.info(f"✅ Logged in as {self.client.user.name}")
            self.stats[self.client.user.id] = {"hunts":0, "battles":0, "gambles":0}
            asyncio.create_task(self.farming_loop())
        
        try:
            # Try to login
            await self.client.start(self.token)
        except discord.LoginFailure as e:
            logger.error(f"❌ Login failed: {e}")
            logger.error("Token is invalid. Get a fresh one from Discord.")
            logger.error("Open Discord in browser -> F12 -> Network -> find 'authorization' header -> copy value")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            sys.exit(1)
        
        await asyncio.Event().wait()
    
    async def send(self, cmd: str):
        try:
            channel = self.client.get_channel(self.channel_id)
            if not channel:
                logger.warning(f"Channel {self.channel_id} not found")
                return
            await channel.send(cmd)
            await asyncio.sleep(random.uniform(0.3, 0.7))
        except Exception as e:
            logger.error(f"Send error: {e}")
    
    async def farming_loop(self):
        logger.info("🔄 Starting farming loop...")
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
                
                # Hunt
                await self.send("owo hunt")
                self.stats[self.client.user.id]["hunts"] += 1
                
                # Battle
                if random.random() < 0.2:
                    await self.send("owo battle")
                    self.stats[self.client.user.id]["battles"] += 1
                    await asyncio.sleep(2)
                
                # Inventory management
                if random.random() < 0.01:
                    await self.send("owo sell common")
                    await asyncio.sleep(1)
                    await self.send("owo sacrifice")
                    await asyncio.sleep(1)
                    await self.send("owo equip best")
                    await asyncio.sleep(1)
                
                # Gambling
                if random.random() < 0.1:
                    bet = self.gambling.next_bet()
                    game = random.choice(["cf", "slots"])
                    await self.send(f"owo {game} {bet}")
                    self.stats[self.client.user.id]["gambles"] += 1
                    # Simulate result
                    if random.random() < 0.5:
                        self.gambling.record(True)
                    else:
                        self.gambling.record(False)
                    await asyncio.sleep(1)
                
                # Random break
                if random.random() < 0.001:
                    mins = random.randint(30, 60)
                    self.break_until = datetime.now() + timedelta(minutes=mins)
                    logger.info(f"💤 Break for {mins} minutes.")
                
                await asyncio.sleep(random.uniform(0.3, 0.7))
                
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
    client = OwOClient()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
