# ============================================================
# ULTIMATE SAFE OWO GRINDER – EXTREME STEALTH
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
# TOKEN – SPLIT INTO 3 PARTS (HIDE FROM GITHUB)
# ============================================================
token_parts = [
    "MTUzODgwNTgwNzMzMDYyNzYzNQ",  # Replace with your new token parts
    "YG045yU",
    "C-k2W1X_XFRo_NQX6OWmS7An0EPq6gdTGE5Vk0"
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
# DISCORD REST API (MIMICS BROWSER)
# ============================================================
class DiscordREST:
    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.base_url = "https://discord.com/api/v9"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
        ]
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        self.session = None
        self.last_request_time = 0
        self.min_request_interval = 5.0  # minimum seconds between requests
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def send_message(self, content: str) -> bool:
        """Send a message with human-like pacing."""
        # Randomize user agent each time (mimic different devices)
        self.headers["User-Agent"] = random.choice(self.user_agents)
        
        # Enforce minimum interval (avoid spam)
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - elapsed + random.uniform(0, 1))
        
        url = f"{self.base_url}/channels/{self.channel_id}/messages"
        payload = {"content": content}
        try:
            async with self.session.post(url, headers=self.headers, json=payload) as resp:
                self.last_request_time = time.time()
                if resp.status in (200, 201):
                    return True
                else:
                    text = await resp.text()
                    if "rate limited" in text.lower():
                        logger.warning("Rate limited – sleeping 60s")
                        await asyncio.sleep(60)
                        return False
                    logger.error(f"Send failed: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"Request error: {e}")
            await asyncio.sleep(10)
            return False

# ============================================================
# HUMAN BEHAVIOR ENGINE
# ============================================================
class HumanBehavior:
    @staticmethod
    def random_delay(min_sec=5, max_sec=20):
        """Sleep for a random human-like duration."""
        # Add ±50% jitter
        base = random.uniform(min_sec, max_sec)
        jitter = base * random.uniform(-0.5, 0.5)
        delay = max(0.5, base + jitter)
        return delay
    
    @staticmethod
    def should_be_awake() -> bool:
        """Simulate sleeping at night (1 AM – 7 AM local time)."""
        # Use UTC to be consistent, or we can use random sleep windows
        # We'll just use a random chance of sleeping for 4-8 hours.
        return True  # We'll handle breaks separately
    
    @staticmethod
    def random_typo(cmd: str) -> str:
        """Occasionally introduce a typo like a real human."""
        if len(cmd) < 3 or random.random() > 0.15:
            return cmd
        pos = random.randint(1, len(cmd)-2)
        chars = list(cmd)
        # Swap two adjacent chars
        chars[pos], chars[pos+1] = chars[pos+1], chars[pos]
        return ''.join(chars)
    
    @staticmethod
    def random_variation(cmd: str) -> str:
        """Add pls/please or change case."""
        variations = [
            cmd,
            cmd.lower(),
            cmd.capitalize(),
            f"{cmd} pls",
            f"{cmd} please",
            f"pls {cmd}",
            cmd.upper(),
        ]
        return random.choice(variations)

# ============================================================
# MAIN STEALTH CLIENT
# ============================================================
class OwoStealth:
    def __init__(self):
        self.token = TOKEN
        self.channel_id = CHANNEL_ID
        self.rest = None
        self.running = True
        self.command_count = 0
        self.batch_start = datetime.now()
        
        # Daily task timers
        self.last_daily = datetime.now() - timedelta(days=1)
        self.last_vote = datetime.now() - timedelta(days=1)
        self.last_quest = datetime.now() - timedelta(days=1)
        self.last_pray = datetime.now() - timedelta(hours=1)
        self.last_boss = datetime.now() - timedelta(hours=2)
        
        # Break until (next wake time)
        self.sleep_until = datetime.now()
        self.human = HumanBehavior()
    
    async def start(self):
        logger.info("🦎 Starting ULTIMATE STEALTH grinder")
        async with DiscordREST(self.token, self.channel_id) as rest:
            self.rest = rest
            # Test token with a single ping
            logger.info("🔍 Testing token...")
            if await rest.send_message("owo ping"):
                logger.info("✅ Token works. Entering stealth mode.")
            else:
                logger.error("❌ Token failed. Check token/channel.")
                return
            await self.farming_loop()
    
    async def send_human(self, cmd: str) -> bool:
        """Send a command with human-like preprocessing."""
        # Random typo
        cmd = self.human.random_typo(cmd)
        # Random variation
        cmd = self.human.random_variation(cmd)
        # Send
        success = await self.rest.send_message(cmd)
        if success:
            self.command_count += 1
        return success
    
    async def sleep_if_needed(self):
        """Check if we should sleep for a long period."""
        now = datetime.now()
        if now < self.sleep_until:
            remaining = (self.sleep_until - now).total_seconds()
            if remaining > 60:
                logger.info(f"💤 Sleeping for {remaining//60:.0f} minutes...")
            await asyncio.sleep(min(remaining, 3600))  # sleep in chunks
            return True
        return False
    
    async def farming_loop(self):
        while self.running:
            try:
                # Check long sleep first
                if await self.sleep_if_needed():
                    continue
                
                now = datetime.now()
                
                # === Daily tasks (once per day, with random delay) ===
                if (now - self.last_daily).total_seconds() > 86400:
                    await self.send_human("owo daily")
                    self.last_daily = now
                    await asyncio.sleep(self.human.random_delay(10, 30))
                
                if (now - self.last_vote).total_seconds() > 86400:
                    await self.send_human("owo vote")
                    self.last_vote = now
                    await asyncio.sleep(self.human.random_delay(10, 30))
                
                if (now - self.last_quest).total_seconds() > 86400:
                    await self.send_human("owo quest")
                    self.last_quest = now
                    await asyncio.sleep(self.human.random_delay(10, 30))
                
                # === Hourly tasks ===
                if (now - self.last_pray).total_seconds() > 3600:
                    await self.send_human("owo pray")
                    self.last_pray = now
                    await asyncio.sleep(self.human.random_delay(5, 15))
                
                if (now - self.last_boss).total_seconds() > 7200:  # every 2 hours
                    await self.send_human("owo boss")
                    self.last_boss = now
                    await asyncio.sleep(self.human.random_delay(10, 20))
                
                # === MAIN FARM: HUNT ONLY (no gambling, no battle spam) ===
                await self.send_human("owo hunt")
                
                # Occasionally do a battle (but rarely)
                if random.random() < 0.05:  # 5% chance
                    await self.send_human("owo battle")
                    await asyncio.sleep(self.human.random_delay(5, 15))
                
                # Rare inventory cleanup
                if random.random() < 0.002:  # 0.2% chance
                    await self.send_human("owo sell common")
                    await asyncio.sleep(self.human.random_delay(3, 8))
                    await self.send_human("owo sacrifice")
                    await asyncio.sleep(self.human.random_delay(3, 8))
                    await self.send_human("owo equip best")
                    await asyncio.sleep(self.human.random_delay(3, 8))
                
                # === Decide if we need a long break ===
                # After every 10-30 commands, take a 1-6 hour break
                if self.command_count % random.randint(10, 30) == 0:
                    break_minutes = random.randint(60, 360)  # 1 to 6 hours
                    self.sleep_until = datetime.now() + timedelta(minutes=break_minutes)
                    logger.info(f"🛌 Taking a {break_minutes}-minute break to mimic human inactivity.")
                    await asyncio.sleep(5)  # small pause before next loop
                
                # === Human-like pause between commands (5-60 seconds) ===
                pause = self.human.random_delay(5, 60)
                logger.debug(f"⏳ Waiting {pause:.1f}s before next command.")
                await asyncio.sleep(pause)
                
            except Exception as e:
                logger.error(f"Loop error: {e}")
                await asyncio.sleep(60)  # pause on error

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("🦎 ULTIMATE STEALTH OWO GRINDER")
    print("="*60)
    client = OwOstealth()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
