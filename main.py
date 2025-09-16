from keep_alive import keep_alive   # 
import logging
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------- Platform Templates --------
def get_template(text: str, links: list) -> str:
    text_lower = text.lower()

    # Remove unwanted usernames and keep only @DealLoot_India
    text = re.sub(r"@\w+", "", text).strip()

    # Detect platform
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

    # Format links (category wise if available)
    formatted_links = []
    for line in text.splitlines():
        if "http" in line:
            formatted_links.append(line.strip())

    # Final response
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

    if message.photo:
        await message.reply_photo(photo=message.photo[-1].file_id, caption=response)
    else:
        await message.reply_text(response)


# -------- Main --------
def main():
    if not BOT_TOKEN:
        raise ValueError("⚠️ BOT_TOKEN not set in Replit Secrets!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    logger.info("Bot started in polling mode ✅")
    app.run_polling()


if __name__ == "__main__":
    keep_alive()   # 🔹 NEW LINE
    main()