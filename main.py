import asyncio
import aiohttp
from aiohttp import web
import random
import string
import os

# ---------- CONFIG ----------
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://discord.com/api/webhooks/1521761282091384883/1K9VG1irCWgQDPzZJ8qhkM0EjV6pH5uPqNkzEnfYWI7M_brxgcy3VJo0lfz4iLVtPRND")

# Terminal Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Global list to store recent checks for the website display
recent_checks = []

# ---------- Web Server Configuration ----------
async def handle_ping(request):
    # Generates a basic HTML view of the live tracking data
    html_content = """
    <html>
    <head>
        <title>Username Sniper Dashboard</title>
        <meta http-equiv="refresh" content="5"> <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #e0e0e0; padding: 20px; }
            h1 { color: #ffffff; border-bottom: 2px solid #333; padding-bottom: 10px; }
            .check-entry { background: #1e1e1e; padding: 10px; margin-bottom: 8px; border-radius: 5px; font-family: monospace; font-size: 14px; }
            .available { color: #4caf50; font-weight: bold; }
            .taken { color: #f44336; font-weight: bold; }
            .error { color: #ffeb3b; }
        </style>
    </head>
    <body>
        <h1>🎯 Live Username Sniper Logs</h1>
        <p><i>Page auto-refreshes every 5 seconds. Storing last 20 checks.</i></p>
        <div>
    """
    
    if not recent_checks:
        html_content += "<p>Starting cycles... No usernames checked yet.</p>"
    else:
        for entry in reversed(recent_checks): # Show newest on top
            html_content += f"<div class='check-entry'>{entry}</div>"
            
    html_content += """
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Dashboard available on port {port}")

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
    await start_web_server()
    
    connector = aiohttp.TCPConnector()
    cycle = 0
    
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            cycle += 1
            print(f"\n--- Cycle #{cycle} ---")
            
            usernames = generate_usernames(count=10)
            
            for username in usernames:
                results = await check_username(session, username)
                
                # Format text strings for the live web dashboard UI
                d_val = results.get('discord')
                if d_val is True:
                    d_web = "<span class='available'>[AVAILABLE]</span>"
                    print(f"👤 {username} -> Discord: {GREEN}[AVAILABLE]{RESET}", end=" | ")
                elif d_val is False:
                    d_web = "<span class='taken'>[TAKEN]</span>"
                    print(f"👤 {username} -> Discord: {RED}[TAKEN]{RESET}", end=" | ")
                else:
                    d_web = f"<span class='error'>[{d_val}]</span>"
                    print(f"👤 {username} -> Discord: {YELLOW}[{d_val}]{RESET}", end=" | ")
                
                t_val = results.get('tiktok')
                if t_val is True:
                    t_web = "<span class='available'>[AVAILABLE]</span>"
                    print(f"TikTok: {GREEN}[AVAILABLE]{RESET}")
                elif t_val is False:
                    t_web = "<span class='taken'>[TAKEN]</span>"
                    print(f"TikTok: {RED}[TAKEN]{RESET}")
                else:
                    t_web = f"<span class='error'>[{t_val}]</span>"
                    print(f"TikTok: {YELLOW}[{t_val}]{RESET}")
                
                # Save data log structure to the web view list
                web_log = f"👤 <b>{username}</b> &nbsp;|&nbsp; Discord: {d_web} &nbsp;|&nbsp; TikTok: {t_web}"
                recent_checks.append(web_log)
                
                # Keep list limited to last 20 entries so it stays clean
                if len(recent_checks) > 20:
                    recent_checks.pop(0)
                
                # Hit checking
                available = []
                if d_val is True: available.append("Discord")
                if t_val is True: available.append("TikTok")
                
                if available:
                    await send_webhook(session, username, available)
                
                await asyncio.sleep(2)
        
            print(f"\n✅ Cycle #{cycle} complete. Cooling down...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
