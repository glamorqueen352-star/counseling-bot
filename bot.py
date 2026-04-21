from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = "8676060897:AAFiFJM5EPhh2f2900tGhNlPf0YLJyJqpVo"
OWNER_ID = 6366800569  # your Telegram ID

users = {}


# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
       "Hi 👋 We're here to help.\n\n"
        "Please write your questions here, and our counseling team will contact you"
    )


# HANDLE USER MESSAGES
async def handle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    user_id = user.id
    name = user.first_name
    username = user.username

    username_text = f"@{username}" if username else "No username"

    # store user
    users[user_id] = {
        "name": name,
        "username": username
    }

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            f"📩 New message\n\n"
            f"👤 Name: {name}\n"
            f"🔗 Username: {username_text}\n"
            f"🆔 ID: {user_id}\n\n"
            f"💬 Message:\n{text}\n\n"
            f"Reply: /reply {user_id} <message>"
        )
    )

    await update.message.reply_text(
        "✅ We received your message.\n\n"
        "A member of our team will contact you within 24 hours."
    )


# ADMIN REPLY COMMAND
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    try:
        user_id = int(context.args[0])
        msg = " ".join(context.args[1:])

        if user_id not in users:
            await update.message.reply_text("❌ User not found.")
            return

        await context.bot.send_message(
            chat_id=user_id,
            text=f"💬 Helper:\n\n{msg}"
        )

        await update.message.reply_text("✅ Sent.")

    except:
        await update.message.reply_text("Usage: /reply <user_id> <message>")


# OPTIONAL: LIST USERS
async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    if not users:
        await update.message.reply_text("No active users.")
        return

    text = "👥 Active users:\n\n"
    for uid, data in users.items():
        name = data["name"]
        username = data["username"]
        username_text = f"@{username}" if username else "No username"

        text += f"{name} ({username_text}) → {uid}\n"

    await update.message.reply_text(text)


# APP SETUP
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reply", reply))
app.add_handler(CommandHandler("users", users_list))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.User(OWNER_ID),
        handle_user
    )
)

