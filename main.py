import asyncio
import aiohttp
import random
import string
import sys

WEBHOOK_URL = "https://discord.com/api/webhooks/1521761282091384883/1K9VG1irCWgQDPzZJ8qhkM0EjV6pH5uPqNkzEnfYWI7M_brxgcy3VJo0lfz4iLVtPRND"

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def generate_usernames(count=15):
    usernames = set()
    chars = string.ascii_letters + string.digits
    while len(usernames) < count:
        length = random.choice([3, 4, 5])
        combo = ''.join(random.choices(chars, k=length))
        usernames.add(combo.lower())
    return list(usernames)

async def check_username(session, username):
    results = {'discord': None, 'tiktok': None}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Discord
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

    # TikTok
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

async def send_webhook(session, username, platforms):
    msg = f"🎯 **{username}** is verified available on: **{', '.join(platforms)}**!"
    payload = {"content": msg, "username": "Username Sniper"}
    try:
        async with session.post(WEBHOOK_URL, json=payload, timeout=5):
            pass
    except Exception:
        pass

async def main():
    print("🚀 High-Speed Sniper Active on Railway.\n")
    async with aiohttp.ClientSession() as session:
        while True:
            usernames = generate_usernames(count=10)
            for username in usernames:
                results = await check_username(session, username)
                print(f"👤 {username} -> Discord: {results['discord']} | TikTok: {results['tiktok']}")
                
                available = []
                if results['discord'] is True: available.append("Discord")
                if results['tiktok'] is True: available.append("TikTok")
                
                if available:
                    await send_webhook(session, username, available)
                await asyncio.sleep(2)
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
