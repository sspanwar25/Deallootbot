import logging
import os
import re
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# -------- Flask Keep Alive --------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running ✅"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# -------- Logging --------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")  # Private group ID for forwarding

# -------- Platform Templates --------
def get_template(text: str, links: list) -> str:
    text_lower = text.lower()
    text = re.sub(r"@\w+", "", text).strip()

    if "amazon" in text_lower:
        header = "🔥 Amazon Loot Deal! 🔥"
        price_line = "💰 Price: Just ___"
        tagline = "⚡ Hurry, Limited Time Offer!"
        hashtags = "#Amazon #LootDeal #DealLootIndia"

    elif "flipkart" in text_lower or any("fkrt" in l for l in links):
        header = "💥 Flipkart Mega Offer! 💥"
        price_line = "💰 Price Drop Alert! Hurry 🚀"
        tagline = ""
        hashtags = "#Flipkart #Discount #DealLootIndia"

    elif "meesho" in text_lower:
        header = "🌸 Meesho Special Loot 🌸"
        price_line = "💰 Lowest Price Ever!"
        tagline = ""
        hashtags = "#Meesho #FashionLoot #DealLootIndia"

    elif "ajio" in text_lower:
        header = "✨ Ajio Super Sale ✨"
        price_line = "💰 Don’t Miss The Offer!"
        tagline = "🛒 Stylish Picks for You"
        hashtags = "#Ajio #StyleDeal #DealLootIndia"

    elif "myntra" in text_lower:
        header = "👗 Myntra Fashion Loot 👗"
        price_line = "💰 Limited Time Only!"
        tagline = "🛍️ Trendy Styles at Best Price"
        hashtags = "#Myntra #FashionDeal #DealLootIndia"

    else:
        header = "🔥 Loot Deal! 🔥"
        price_line = "💰 Best Price"
        tagline = "⚡ Limited Time Offer"
        hashtags = "#DealLootIndia #LootDeal"

    formatted_links = []
    for line in text.splitlines():
        if "http" in line:
            formatted_links.append(line.strip())

    response = f"""{header}
🛒 Product: {text.splitlines()[0]}
{price_line}
{tagline}

👉 Grab Here:
""" + "\n".join(formatted_links) + f"""

👉 Follow @DealLoot_India for 🔥 daily loot deals!

{hashtags}
"""
    return response

# -------- Handlers --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running ✅")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.caption if message.caption else message.text
    if not text:
        await message.reply_text("⚠️ Please send text or photo with caption.")
        return

    links = re.findall(r"(https?://\S+)", text)
    response = get_template(text, links)

    # ---------- Original reply ----------
    if message.photo:
        await message.reply_photo(photo=message.photo[-1].file_id, caption=response)
    else:
        await message.reply_text(response)

    # ---------- Forward to Private Group ----------
    if GROUP_ID:
        try:
            if message.photo:
                await context.bot.send_photo(chat_id=int(GROUP_ID),
                                             photo=message.photo[-1].file_id,
                                             caption=response)
            else:
                await context.bot.send_message(chat_id=int(GROUP_ID), text=response)
            logger.info(f"Message forwarded to {GROUP_ID}")
        except Exception as e:
            logger.error(f"Forwarding error: {e}")

# -------- Main --------
def main():
    if not BOT_TOKEN:
        raise ValueError("⚠️ BOT_TOKEN not set in Render Environment Variables!")

    app_tg = Application.builder().token(BOT_TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    logger.info("Bot started in polling mode ✅")
    app_tg.run_polling()

if __name__ == "__main__":
    keep_alive()  # Flask server background me chalega
    main()
