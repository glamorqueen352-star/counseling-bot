from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 👇 Add both admins here
ADMIN_IDS = [6366800569, 580443412]

# storage
users_by_id = {}
users_by_username = {}

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing from environment variables")


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

    users_by_id[user_id] = {
        "name": name,
        "username": username
    }

    if username:
        users_by_username[username.lower()] = user_id

    username_text = f"@{username}" if username else "No username"

    message = (
        f"📩 New message\n\n"
        f"👤 Name: {name}\n"
        f"🔗 Username: {username_text}\n"
        f"🆔 ID: {user_id}\n\n"
        f"💬 Message:\n{text}\n\n"
        f"Reply: /reply <user_id | @username> <message>"
    )

    # 👇 send to ALL admins
    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=message
        )

    await update.message.reply_text(
        "✅ We've received your message.\n\n"
        "A member of our team will contact you within 24 hours."
    )


# REPLY COMMAND
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_IDS:
        return

    try:
        target = context.args[0]
        msg = " ".join(context.args[1:])

        if target.isdigit():
            user_id = int(target)
        else:
            username = target.replace("@", "").lower()
            user_id = users_by_username.get(username)

            if not user_id:
                await update.message.reply_text("❌ Username not found.")
                return

        await context.bot.send_message(
            chat_id=user_id,
            text=f"💬 Counselling Bot:\n\n{msg}"
        )

        await update.message.reply_text("✅ Sent.")

    except:
        await update.message.reply_text("Usage: /reply <user_id|@username> <message>")


# LIST USERS
async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_IDS:
        return

    if not users_by_id:
        await update.message.reply_text("No active users.")
        return

    text = "👥 Active users:\n\n"
    for uid, data in users_by_id.items():
        username_text = f"@{data['username']}" if data["username"] else "No username"
        text += f"{data['name']} ({username_text}) → {uid}\n"

    await update.message.reply_text(text)


# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply))
    app.add_handler(CommandHandler("users", users_list))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~filters.User(user_id=ADMIN_IDS),
            handle_user
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
