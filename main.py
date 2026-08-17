# ============================================================
# ULTIMATE OWO GRINDER - PURE REST API (NO DISCORD.PY)
# ============================================================

import aiohttp
import asyncio
import random
import logging
import os
import sys
from datetime import datetime, timedelta

# ============================================================
# YOUR TOKEN - SPLIT INTO 3 PARTS
# ============================================================
token_parts = [
    "MTUzODc4MDgwNzg4NjI3ODY5Mg",
    "GCHUwf",
    "3Dw0vCREowDFnmx2tSS_7r31plyJ4ZAUv3doRc"
]
TOKEN = ".".join(token_parts)

# ============================================================
# CHANNEL ID - ENV VAR
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
# DISCORD REST API CLIENT
# ============================================================
class DiscordREST:
    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.base_url = "https://discord.com/api/v9"
        self.headers = {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def send_message(self, content: str) -> bool:
        """Send a message to the channel via REST API."""
        url = f"{self.base_url}/channels/{self.channel_id}/messages"
        payload = {"content": content}
        try:
            async with self.session.post(url, headers=self.headers, json=payload) as resp:
                if resp.status == 200 or resp.status == 201:
                    return True
                else:
                    text = await resp.text()
                    logger.error(f"Send failed: {resp.status} - {text}")
                    return False
        except Exception as e:
            logger.error(f"Request error: {e}")
            return False

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
# MAIN BOT
# ============================================================
class OwOClient:
    def __init__(self):
        self.token = TOKEN
        self.channel_id = CHANNEL_ID
        self.gambling = GamblingEngine()
        self.stats = {"hunts":0, "battles":0, "gambles":0}
        self.running = True
        self.last_actions = {k: datetime.now() - timedelta(days=1) for k in 
                             ["daily","vote","quest","pray","boss","battle"]}
        self.break_until = datetime.now()
        self.rest = None
    
    async def start(self):
        logger.info("🚀 Starting OwO Grinder (REST mode)")
        async with DiscordREST(self.token, self.channel_id) as rest:
            self.rest = rest
            # Test the token by sending a test message (or just send a harmless command)
            logger.info("🔍 Testing token...")
            test_result = await rest.send_message("owo ping")
            if test_result:
                logger.info("✅ Token works! Sending 'owo ping' successful.")
            else:
                logger.error("❌ Token test failed. Check token or channel ID.")
                return
            
            # Start farming loop
            await self.farming_loop()
    
    async def send(self, cmd: str):
        """Send a command using REST."""
        if not self.rest:
            return False
        success = await self.rest.send_message(cmd)
        if success:
            await asyncio.sleep(random.uniform(0.3, 0.7))
        return success
    
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
                
                # Hunt
                await self.send("owo hunt")
                self.stats["hunts"] += 1
                
                # Battle
                if random.random() < 0.2:
                    await self.send("owo battle")
                    self.stats["battles"] += 1
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
                    self.stats["gambles"] += 1
                    # Simulate result (we can't know real result without parsing)
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
    print("🔥 ULTIMATE OWO GRINDER (REST) 🔥")
    print("="*60)
    client = OwOClient()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
