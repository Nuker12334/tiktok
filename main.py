import asyncio
import aiohttp
import random
import string
import sys

# ---------- CONFIG ----------
WEBHOOK_URL = "https://discord.com/api/webhooks/1521761282091384883/1K9VG1irCWgQDPzZJ8qhkM0EjV6pH5uPqNkzEnfYWI7M_brxgcy3VJo0lfz4iLVtPRND"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# ---------- Specific Pattern Username Generator ----------
def generate_usernames(count=15):
    usernames = set()
    chars = string.ascii_letters + string.digits
    while len(usernames) < count:
        length = random.choice([4, 5])
        combo = ''.join(random.choices(chars, k=length))
        usernames.add(combo.lower())
    return list(usernames)

# ---------- API Checker ----------
async def check_username(session, username):
    results = {'discord': None, 'tiktok': None}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Discord Lookup
    discord_url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
    try:
        async with session.post(discord_url, json={"username": username}, headers=headers, timeout=5) as resp:
            if resp.status == 200:
                data = await resp.json()
                results['discord'] = not data.get('taken', True)
            else:
                results['discord'] = f"HTTP {resp.status}"
    except Exception:
        results['discord'] = "Error"

    # TikTok Lookup
    tiktok_url = f"https://www.tiktok.com/@{username}"
    try:
        async with session.head(tiktok_url, headers=headers, allow_redirects=False, timeout=5) as resp:
            if resp.status == 404:
                results['tiktok'] = True
            elif resp.status == 200:
                results['tiktok'] = False
            else:
                results['tiktok'] = f"HTTP {resp.status}"
    except Exception:
        results['tiktok'] = "Error"

    return results

# ---------- Webhook Sender ----------
async def send_webhook(session, username, platforms):
    if not platforms:
        return
    msg = f"🎯 **{username}** is verified available on: **{', '.join(platforms)}**!"
    payload = {
        "content": msg,
        "username": "Username Sniper",
    }
    try:
        async with session.post(WEBHOOK_URL, json=payload, timeout=5):
            pass
    except Exception:
        pass

# ---------- Main Loop ----------
async def main():
    print("🚀 High-Speed Sniper Active on Render.\n")
    
    connector = aiohttp.TCPConnector()
    cycle = 0
    
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            cycle += 1
            print(f"\n--- Cycle #{cycle} ---")
            
            usernames = generate_usernames(count=10)
            
            for username in usernames:
                results = await check_username(session, username)
                
                print(f"👤 {username} ->", end=" ")
                
                d = results.get('discord')
                if d is True:
                    print(f"Discord: {GREEN}[AVAILABLE]{RESET}", end=" | ")
                elif d is False:
                    print(f"Discord: {RED}[TAKEN]{RESET}", end=" | ")
                else:
                    print(f"Discord: {YELLOW}[{d}]{RESET}", end=" | ")
                
                t = results.get('tiktok')
                if t is True:
                    print(f"TikTok: {GREEN}[AVAILABLE]{RESET}")
                elif t is False:
                    print(f"TikTok: {RED}[TAKEN]{RESET}")
                else:
                    print(f"TikTok: {YELLOW}[{t}]{RESET}")
                
                # Check for hits
                available = []
                if d is True: available.append("Discord")
                if t is True: available.append("TikTok")
                
                if available:
                    await send_webhook(session, username, available)
                
                await asyncio.sleep(2) # Safe delay to avoid quick cloud bans
        
            print(f"\n✅ Cycle #{cycle} complete. Cooling down...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
