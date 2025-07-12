import os
import asyncio
from flask import Flask, request
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment.")

# Create Telegram app
telegram_app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# Flask app
app = Flask(__name__)
loop = asyncio.get_event_loop()

# Ensure Telegram App is initialized only once
initialized = False

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="🚀 Open Gem Hunters",
            web_app=WebAppInfo(url="https://telegrambot2797.vercel.app")
        )]
    ])
    await update.message.reply_text("Welcome! Launch the Mini App:", reply_markup=keyboard)

telegram_app.add_handler(CommandHandler("start", start))


@app.before_first_request
def init_bot():
    global initialized
    if not initialized:
        loop.create_task(telegram_app.initialize())
        initialized = True


@app.route("/", methods=["GET"])
def root():
    return "Bot is live!", 200


@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://telegrambot-production-39fd.up.railway.app/webhook/{BOT_TOKEN}"
    loop.create_task(telegram_app.bot.set_webhook(webhook_url))
    return f"Webhook set to: {webhook_url}", 200


@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    loop.create_task(telegram_app.process_update(update))  # ✅ no asyncio.run
    return "ok", 200
