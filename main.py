import asyncio
import random
import re
import json
import os
import requests
from playwright.async_api import async_playwright

# ─── Load token from environment ──────────────────────────────
BROWSERLESS_TOKEN = os.getenv("BROWSERLESS_TOKEN")
if not BROWSERLESS_TOKEN:
    raise ValueError("BROWSERLESS_TOKEN environment variable not set.")

BROWSERLESS_URL = f"wss://chrome.browserless.io?token={BROWSERLESS_TOKEN}"

ACCOUNT_COUNT = 3           # How many accounts to create
PREFIX = "user_"
PASSWORD_LENGTH = 10

# ─── Temp email helpers ────────────────────────────────────────
def get_temp_email():
    try:
        resp = requests.get('https://api.guerrillamail.com/ajax.php?f=get_email_address&ip=127.0.0.1&agent=Mozilla')
        data = resp.json()
        if data.get('email_addr'):
            return data['email_addr']
    except:
        pass
    return f"test{random.randint(1000,9999)}@guerrillamail.com"

def fetch_inbox(email):
    try:
        resp = requests.get('https://api.guerrillamail.com/ajax.php?f=get_email_list&sid_token=')
        data = resp.json()
        return data.get('list', [])
    except:
        return []

def read_message(email, mail_id):
    try:
        resp = requests.get(f'https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}')
        data = resp.json()
        return data.get('mail_body', '')
    except:
        return ''

def extract_code(text):
    match = re.search(r'\b(\d{6})\b', text)
    return match.group(1) if match else None

# ─── Main account creation ──────────────────────────────────────
async def create_tiktok_account():
    async with async_playwright() as p:
        # Connect to Browserless
        browser = await p.chromium.connect_over_cdp(BROWSERLESS_URL)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        email = get_temp_email()
        password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*', k=PASSWORD_LENGTH))
        username = f"{PREFIX}{random.randint(10000,99999)}"

        print(f"→ Email: {email}")
        print(f"→ Password: {password}")
        print(f"→ Username: {username}")

        await page.goto('https://www.tiktok.com/signup', wait_until='networkidle')
        await page.wait_for_selector('input[type="email"]', timeout=15000)

        await page.fill('input[type="email"]', email)
        await page.fill('input[type="password"]', password)
        await page.click('button[type="submit"]')
        print("→ Form submitted, waiting for verification email...")

        code = None
        for _ in range(20):
            await asyncio.sleep(3)
            messages = fetch_inbox(email)
            if messages:
                latest = messages[0]
                body = read_message(email, latest['mail_id'])
                extracted = extract_code(body)
                if extracted:
                    code = extracted
                    print(f"→ Received code: {code}")
                    break

        if not code:
            print("❌ No verification code received.")
            await browser.close()
            return None

        try:
            await page.fill('input[placeholder*="code" i]', code)
            await page.click('button[type="submit"]')
        except:
            await page.fill('input[type="text"]', code)
            await page.click('button[type="submit"]')

        await page.wait_for_url('https://www.tiktok.com/*', timeout=30000)
        print("✅ Account created successfully!")

        account = {'email': email, 'username': username, 'password': password}
        # Save to a file (Railway persists the filesystem)
        with open('accounts.json', 'a') as f:
            json.dump(account, f)
            f.write('\n')

        await browser.close()
        return account

async def main():
    for i in range(ACCOUNT_COUNT):
        print(f"\n─── Creating account #{i+1} ───")
        result = await create_tiktok_account()
        if result:
            print(f"✔ Saved: {result['email']}")
        else:
            print("✖ Failed, moving on...")
        await asyncio.sleep(random.randint(10, 20))

if __name__ == '__main__':
    asyncio.run(main())
