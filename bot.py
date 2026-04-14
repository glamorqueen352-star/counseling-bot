from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID =    6366800569  # your Telegram ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi 👋 We're here to help.\n\n"
        "Please write your questions here, and our counseling team will contact you"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    user = update.message.from_user
    first_name = user.first_name
    username = user.username
    user_id = user.id

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            f"📩 New counseling question:\n\n{text}\n\n"
            f"👤 Name: {first_name}\n"
            f"🔗 Username: @{username if username else 'No username'}\n"
        )
    )

    await update.message.reply_text("We have received your message. A member of our team will contact you within 48 hours.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
