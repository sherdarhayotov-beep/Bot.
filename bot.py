import json
import os
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, filters
)

BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"
ADMIN_ID = 5775388579

DATA_FILE = "movies.json"

# ================= MA'LUMOTNI YUKLASH =================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        movies = json.load(f)
else:
    movies = {}

# ================= SAQLASH FUNKSIYASI =================
def save_movies():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [[KeyboardButton("🎥 Kino olish")]]

    if user.id == ADMIN_ID:
        keyboard.append([KeyboardButton("🛠 Admin panel")])

    await update.message.reply_text(
        "🎬 Kino botga xush kelibsiz!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [KeyboardButton("➕ Kino joylash")],
        [KeyboardButton("⬅️ Ortga")]
    ]

    await update.message.reply_text(
        "🛠 Admin panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "🛠 Admin panel" and user.id == ADMIN_ID:
        await admin_panel(update, context)

    elif text == "➕ Kino joylash" and user.id == ADMIN_ID:
        context.user_data["step"] = "code"
        await update.message.reply_text("🎞 Kino kodini kiriting (masalan: 5)")

    elif context.user_data.get("step") == "code" and user.id == ADMIN_ID:
        context.user_data["movie_code"] = text
        context.user_data["step"] = "video"
        await update.message.reply_text("📽 Endi kinoni VIDEO qilib yuboring")

    elif text.isdigit():
        if text in movies:
            await update.message.reply_video(movies[text])
        else:
            await update.message.reply_text("❌ Bu kodga kino yo‘q")

# ================= VIDEO HANDLER =================
async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id != ADMIN_ID:
        return

    if context.user_data.get("step") == "video":
        code = context.user_data["movie_code"]
        file_id = update.message.video.file_id

        movies[code] = file_id
        save_movies()  # 💾 SAQLASH

        context.user_data.clear()

        await update.message.reply_text(
            f"✅ Kino saqlandi!\n🎬 Kod: {code}\n💾 Doimiy saqlandi"
        )

# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, text_handler))
app.add_handler(MessageHandler(filters.VIDEO, video_handler))

print("🎬 Kino bot ishga tushdi (saqlash bilan)...")
app.run_polling()
