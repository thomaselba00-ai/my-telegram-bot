import logging
import urllib.request
import urllib.parse
import json
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
TELEGRAM_TOKEN = "8896570204:AAEsrNG02fWDutel-EBariwCmKKu80WIa4Y"   # ← replace this
GEMINI_API_BASE = "https://api-rebix.vercel.app/api/gemini"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Helper: call the Gemini API
# ─────────────────────────────────────────────
def ask_gemini(question: str) -> str:
    """Send a question to the Rebix Gemini API and return the reply."""
    encoded_q = urllib.parse.quote(question)
    url = f"{GEMINI_API_BASE}?q={encoded_q}"

    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data.get("message", "⚠️ No message in response.")
    except urllib.error.URLError as e:
        logger.error("Network error: %s", e)
        return "⚠️ Could not reach the AI service. Please try again later."
    except json.JSONDecodeError:
        return "⚠️ Received an unexpected response from the AI service."


# ─────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message."""
    await update.message.reply_text(
        "👋 Hello! I'm an AI-powered bot.\n"
        "Just send me any message and I'll reply using Gemini AI.\n\n"
        "Commands:\n"
        "  /start  – Show this message\n"
        "  /help   – How to use the bot"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help message."""
    await update.message.reply_text(
        "💡 *How to use:*\n"
        "Simply type any question or message and I'll answer it using Gemini AI.\n\n"
        "Example:\n"
        "  _What is the capital of France?_\n"
        "  _Write a poem about rain._",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to every text message using the Gemini API."""
    user_text = update.message.text
    user_name = update.effective_user.first_name
    logger.info("Message from %s: %s", user_name, user_text)

    # Show typing indicator while we wait
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    reply = ask_gemini(user_text)
    await update.message.reply_text(reply)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Update %s caused error: %s", update, context.error)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN", TELEGRAM_TOKEN)
    if token == "YOUR_TELEGRAM_BOT_TOKEN":
        raise ValueError(
            "Please set your Telegram bot token!\n"
            "Either edit TELEGRAM_TOKEN in this file or set the "
            "TELEGRAM_TOKEN environment variable."
        )

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
