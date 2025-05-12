import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent

# --- CONFIGURATION ---
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Y0U PUT YOUR OWN FROM @BotFather
AUTHORIZED_USER_ID = 123456789      # Y0UR USER ID ONLY
ua = UserAgent()

HEADERS = {
    "User-Agent": ua.random,
    "Accept-Language": "en-US,en;q=0.5"
}

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- MAIN HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != AUTHORIZED_USER_ID:
        await update.message.reply_text("❌ Unauth0rized. Y0u ar3n't VIP.")
        return

    url = update.message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❗️Inv4lid URL. Pl3as3 s3nd a v4lid w3bsit3 link.")
        return

    try:
        await update.message.reply_text("🔍 Scanning t3rrain...")

        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            await update.message.reply_text(f"🌐 Sit3 r3fus3d acc3ss. HTTP {res.status_code}")
            return

        soup = BeautifulSoup(res.text, 'html.parser')

        # Basic scraping
        title = soup.title.string if soup.title else "No Title Found"
        meta_tags = soup.find_all('meta')
        links = list(set([a.get('href') for a in soup.find_all('a', href=True)]))
        
        response = f"""
🎯 Target: {url}
📄 Title: {title}
🔢 Status Code: {res.status_code}
🔗 Links Found: {len(links)}

META TAGS:
{chr(10).join([str(tag) for tag in meta_tags[:10]])}

PREVIEW OF CONTENT:
{res.text[:500]}...
"""

        if len(response) > 4096:
            # Split into chunks
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i:i+4096])
        else:
            await update.message.reply_text(response)

        # Optional: Send raw HTML as file if too big
        with open("scraped_output.html", "w", encoding="utf-8") as f:
            f.write(str(soup.prettify()))

        await update.message.reply_document(document=open("scraped_output.html", "rb"))

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

# --- STARTUP ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == AUTHORIZED_USER_ID:
        await update.message.reply_text("🔓 VIP s3ssion act1v3. S3nd a URL.")
    else:
        await update.message.reply_text("🚫 Acc3ss d3n13d.")

# --- MAIN FUNCTION ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(None, handle_message))  # Handles all text messages
    
    print("[+] Bot is now running...")
    app.run_polling()