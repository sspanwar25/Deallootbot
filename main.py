import logging
import os
import re
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
MAIN_CHANNEL = os.getenv("MAIN_CHANNEL", "@DealLoot_India")

# -------- Platform Templates --------
def get_template(text: str, links: list) -> str:
    text = text or ""
    text_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    preview = text_lines[0] if text_lines else "Product"

    text_lower = text.lower()

    # Remove other @usernames (but keep whitespace)
    sanitized = re.sub(r"@\w+", "", text).strip()

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

    # Format links (collect lines that look like links)
    formatted_links = []
    for ln in text_lines:
        if "http" in ln:
            formatted_links.append(ln)

    # Build final message
    msg = [header]
    msg.append(f"🛒 Product: {preview}")
    msg.append(price_line)
    if tagline:
        msg.append(tagline)
    msg.append("")
    msg.append("👉 Grab Here:")
    if formatted_links:
        msg.extend(formatted_links)
    else:
        # If no link lines detected, try the links param
        msg.extend(links or [])

    msg.append("")
    msg.append(f"👉 Follow {MAIN_CHANNEL} for 🔥 daily loot deals!")
    msg.append("")
    msg.append(hashtags)

    return "\n".join(msg)


# -------- Error handler --------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and do not crash the bot."""
    logger.error("Exception while handling an update:", exc_info=True)
    # Optionally notify the developer (commented out for privacy)
    try:
        if isinstance(context.error, TelegramError):
            logger.error(f"Telegram error: {context.error}")
    except Exception:
        # context may be None in some error cases
        pass


# -------- Handlers --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running ✅")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    try:
        text = message.caption if message.caption else message.text
        if not text or not text.strip():
            await message.reply_text("⚠️ Please send text or photo with caption.")
            return

        links = re.findall(r"(https?://\S+|www\.\S+)", text)
        response = get_template(text, links)

        if message.photo:
            # reply with same photo and formatted caption
            await message.reply_photo(photo=message.photo[-1].file_id, caption=response)
        else:
            await message.reply_text(response)

    except TelegramError as e:
        logger.error(f"Telegram error while processing message: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in handle_message: {e}")


# -------- Main --------

def main():
    if not BOT_TOKEN:
        raise ValueError("⚠️ BOT_TOKEN environment variable is required")

    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.PHOTO, handle_message))

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("Bot started in polling mode ✅")

    # run polling (suitable when deploying as a background worker)
    app.run_polling()


if __name__ == "__main__":
    main()
