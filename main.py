# ============================================================
# 200 IQ OWO FARMER – FAST + UNDETECTABLE
# ============================================================

import aiohttp
import asyncio
import random
import logging
import os
import sys
import time
from datetime import datetime, timedelta

# ============================================================
# TOKEN – SPLIT INTO 3 PARTS
# ============================================================
token_parts = [
    "MTUzODgwNTgwNzMzMDYyNzYzNQ",  # Part 1
    "G045yU",                       # Part 2
    "C-k2W1X_XFRo_NQX6OWmS7An0EPq6gdTGE5Vk0"  # Part 3
]
TOKEN = ".".join(token_parts)

# ============================================================
# CHANNEL ID – FROM ENV
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
logger = logging.getLogger("OwO-Stealth")
logger.info(f"Token length: {len(TOKEN)}")
logger.info(f"Channel ID: {CHANNEL_ID}")

# ============================================================
# DISCORD REST API
# ============================================================
class DiscordREST:
    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.base_url = "https://discord.com/api/v9"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
        ]
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        self.session = None
        self.last_request_time = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def send_message(self, content: str) -> bool:
        """Send a message via REST API."""
        self.headers["User-Agent"] = random.choice(self.user_agents)
        
        # Prevent rate limiting (0.5-2s between requests)
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < 0.5:
            await asyncio.sleep(0.5 - elapsed + random.uniform(0, 0.3))
        
        url = f"{self.base_url}/channels/{self.channel_id}/messages"
        payload = {"content": content}
        try:
            async with self.session.post(url, headers=self.headers, json=payload) as resp:
                self.last_request_time = time.time()
                if resp.status in (200, 201):
                    return True
                elif resp.status == 429:  # Rate limit
                    data = await resp.json()
                    retry_after = data.get('retry_after', 5)
                    logger.warning(f"⏳ Rate limited! Waiting {retry_after}s...")
                    await asyncio.sleep(retry_after + 1)
                    return False
                else:
                    logger.error(f"Send failed: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"Request error: {e}")
            await asyncio.sleep(2)
            return False

# ============================================================
# 200 IQ STEALTH ENGINE
# ============================================================
class StealthEngine:
    @staticmethod
    def random_delay(min_sec=1.0, max_sec=8.0):
        """Human-like delay with jitter."""
        base = random.uniform(min_sec, max_sec)
        jitter = base * random.uniform(-0.3, 0.3)
        return max(0.5, base + jitter)
    
    @staticmethod
    def random_variation(cmd: str) -> str:
        """Generate random command variations."""
        variations = [
            cmd,
            cmd.lower(),
            cmd.capitalize(),
            f"{cmd} pls",
            f"{cmd} please",
            f"pls {cmd}",
        ]
        return random.choice(variations)
    
    @staticmethod
    def random_typo(cmd: str) -> str:
        """Occasional typo (5% chance)."""
        if len(cmd) < 4 or random.random() > 0.05:
            return cmd
        pos = random.randint(1, len(cmd)-2)
        chars = list(cmd)
        chars[pos], chars[pos+1] = chars[pos+1], chars[pos]
        return ''.join(chars)

# ============================================================
# MAIN CLIENT
# ============================================================
class OwoFarmer:
    def __init__(self):
        self.token = TOKEN
        self.channel_id = CHANNEL_ID
        self.rest = None
        self.running = True
        self.command_count = 0
        self.stealth = StealthEngine()
        self.last_actions = {k: datetime.now() - timedelta(days=1) for k in 
                             ["daily","vote","quest","pray","boss"]}
        self.break_until = datetime.now()
    
    async def start(self):
        logger.info("🧠 Starting 200 IQ OWO Farmer")
        async with DiscordREST(self.token, self.channel_id) as rest:
            self.rest = rest
            # Test token
            logger.info("🔍 Testing token...")
            if await rest.send_message("owo ping"):
                logger.info("✅ Token works! Starting smart farm.")
            else:
                logger.error("❌ Token failed.")
                return
            await self.farming_loop()
    
    async def send(self, cmd: str) -> bool:
        """Send with human-like preprocessing."""
        cmd = self.stealth.random_variation(cmd)
        cmd = self.stealth.random_typo(cmd)
        success = await self.rest.send_message(cmd)
        if success:
            self.command_count += 1
        return success
    
    async def farming_loop(self):
        while self.running:
            try:
                # Check if on break
                if datetime.now() < self.break_until:
                    await asyncio.sleep(60)
                    continue
                
                now = datetime.now()
                
                # === Daily tasks (once per day) ===
                if (now - self.last_actions["daily"]).total_seconds() > 86400:
                    await self.send("owo daily")
                    self.last_actions["daily"] = now
                    await asyncio.sleep(self.stealth.random_delay(3, 8))
                
                if (now - self.last_actions["vote"]).total_seconds() > 86400:
                    await self.send("owo vote")
                    self.last_actions["vote"] = now
                    await asyncio.sleep(self.stealth.random_delay(3, 8))
                
                if (now - self.last_actions["quest"]).total_seconds() > 86400:
                    await self.send("owo quest")
                    self.last_actions["quest"] = now
                    await asyncio.sleep(self.stealth.random_delay(3, 8))
                
                # === Hourly tasks ===
                if (now - self.last_actions["pray"]).total_seconds() > 3600:
                    await self.send("owo pray")
                    self.last_actions["pray"] = now
                    await asyncio.sleep(self.stealth.random_delay(2, 5))
                
                if (now - self.last_actions["boss"]).total_seconds() > 7200:
                    await self.send("owo boss")
                    self.last_actions["boss"] = now
                    await asyncio.sleep(self.stealth.random_delay(3, 8))
                
                # === MAIN FARMING ===
                await self.send("owo hunt")
                
                # Battle occasionally (10% chance)
                if random.random() < 0.1:
                    await self.send("owo battle")
                    await asyncio.sleep(self.stealth.random_delay(2, 5))
                
                # Inventory cleanup (rare)
                if random.random() < 0.005:
                    await self.send("owo sell common")
                    await asyncio.sleep(self.stealth.random_delay(1, 3))
                    await self.send("owo sacrifice")
                    await asyncio.sleep(self.stealth.random_delay(1, 3))
                    await self.send("owo equip best")
                    await asyncio.sleep(self.stealth.random_delay(1, 3))
                
                # === Smart break logic ===
                # After 20-50 commands, take a 15-45 min break
                if self.command_count % random.randint(20, 50) == 0 and self.command_count > 0:
                    break_minutes = random.randint(15, 45)
                    self.break_until = datetime.now() + timedelta(minutes=break_minutes)
                    logger.info(f"☕ Taking a {break_minutes}-minute break (looks human).")
                    await asyncio.sleep(2)
                
                # === Wait between commands (1-8 seconds) ===
                delay = self.stealth.random_delay(1.0, 8.0)
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Loop error: {e}")
                await asyncio.sleep(10)

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("🧠 200 IQ OWO FARMER")
    print("="*60)
    client = OwoFarmer()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
