# bot.py

import telebot
from telebot import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("8501918863:AAE6YCS4j3z0JM9RcpmNXVtk2Kh1qUfABRQ")
CHANNEL = os.getenv("CHANNEL")
ADMIN_ID = int(os.getenv("5775388579"))

bot = telebot.TeleBot(8501918863:AAE6YCS4j3z0JM9RcpmNXVtk2Kh1qUfABRQ)

# Kino ma'lumotlarini JSON fayldan yuklash
if os.path.exists("kinolar.json"):
    with open("kinolar.json", "r", encoding="utf-8") as f:
        kinolar = json.load(f)
else:
    kinolar = {}

# Majburiy kanal tekshiruvi
def check_subscription(5775388579):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, f"Obuna bo'ling: {CHANNEL}")
        return
    bot.send_message(message.chat.id, "Kino kodini kiriting:")

# Kino kodi yozilganda
@bot.message_handler(func=lambda m: True)
def send_movie(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, f"Obuna bo'ling: {CHANNEL}")
        return

    code = message.text.strip()
    if code in kinolar:
        bot.send_message(message.chat.id, f"Kino: {kinolar[code]}")
    else:
        bot.send_message(message.chat.id, "Kod topilmadi!")

# Admin panel
@bot.message_handler(commands=['5775388579'])
def admin_panel(message):
    if message.from_user.id != 5775388579:
        bot.send_message(message.chat.id, "Siz admin emassiz!")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎬 Kino yuklash", "📊 Kino ro‘yxati")
    markup.row("❌ Kino o‘chirish")
    bot.send_message(message.chat.id, "Admin panel:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_actions(message):
    global kinolar
    text = message.text.strip()
    if text == "🎬 Kino yuklash":
        msg = bot.send_message(message.chat.id, "Kino kodini kiriting:")
        bot.register_next_step_handler(msg, add_movie)
    elif text == "📊 Kino ro‘yxati":
        if kinolar:
            movie_list = "\n".join([f"{k}: {v}" for k, v in kinolar.items()])
            bot.send_message(message.chat.id, movie_list)
        else:
            bot.send_message(message.chat.id, "Hali kino yo‘q")
    elif text == "❌ Kino o‘chirish":
        msg = bot.send_message(message.chat.id, "O‘chiriladigan kodni kiriting:")
        bot.register_next_step_handler(msg, remove_movie)

def add_movie(message):
    global kinolar
    code = message.text.strip()
    msg = bot.send_message(message.chat.id, "Kino linkini kiriting:")
    bot.register_next_step_handler(msg, lambda m: save_movie(code, m))

def save_movie(code, message):
    global kinolar
    link = message.text.strip()
    kinolar[code] = link
    with open("kinolar.json", "w", encoding="utf-8") as f:
        json.dump(kinolar, f, ensure_ascii=False, indent=4)
    bot.send_message(message.chat.id, f"Kino {code} qo‘shildi!")

def remove_movie(message):
    global kinolar
    code = message.text.strip()
    if code in kinolar:
        kinolar.pop(code)
        with open("kinolar.json", "w", encoding="utf-8") as f:
            json.dump(kinolar, f, ensure_ascii=False, indent=4)
        bot.send_message(message.chat.id, f"Kino {code} o‘chirildi!")
    else:
        bot.send_message(message.chat.id, "Kod topilmadi!")

bot.infinity_polling()
