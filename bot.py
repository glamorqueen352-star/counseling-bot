from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

print("🚀 BOT STARTING...")

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ✅ ADMINS
ADMIN_IDS = [5688638871, 931448330]

# ✅ TEMP STORAGE
users_by_id = {}
users_by_username = {}

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing from environment variables")

print("✅ TOKEN LOADED")


# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 /start triggered")
    await update.message.reply_text(
        "Hi 👋 We're here to help.\n\n"
        "Please write your questions here, and our counseling team will contact you"
    )


# HANDLE USER MESSAGES
async def handle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # 🚫 Ignore admins
    if user.id in ADMIN_IDS:
        return

    text = update.message.text
    user_id = user.id
    name = user.first_name
    username = user.username

    # store user
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

    print(f"📨 Message received from {user_id}")

    # send to admins
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message)
        except Exception as e:
            print(f"❌ Failed to send to admin {admin_id}: {e}")

    await update.message.reply_text(
        "✅ We've received your message.\n\n"
        "A member of our team will contact you within 24 hours."
    )


# REPLY COMMAND
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_IDS:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply <user_id|@username> <message>")
        return

    target = context.args[0]
    msg = " ".join(context.args[1:])

    try:
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
        print(f"✅ Reply sent to {user_id}")

    except Exception as e:
        print(f"❌ Reply error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


# USERS LIST
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
    try:
        print("⚙️ Building bot...")

        app = ApplicationBuilder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("reply", reply))
        app.add_handler(CommandHandler("users", users_list))

        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_user
            )
        )

        print("✅ Bot is running...")
        app.run_polling()

    except Exception as e:
        print("🔥 CRASH ERROR:", e)


if __name__ == "__main__":
    main()
