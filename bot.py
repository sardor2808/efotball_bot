import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVER QISMI ---
app = Flask('')
@app.route('/')
def home(): return "Bot is fully functional!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- BOT SOZLAMALARI ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)
user_temp = {}

# --- ASOSIY MENYU ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ E'lon berish", "📂 E'lonlarim", "👨‍💻 Adminlar", "📚 Qoidalar", "💰 E'lon narxlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    welcome = "🌟 <b>Assalomu alaykum!</b>\n\nE'lon berish botiga xush kelibsiz. Marhamat, quyidagi menyudan foydalaning:"
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu(), parse_mode="HTML")

# --- QOIDALAR BO'LIMI ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules_info(message):
    rules = (
        "⚠️ <b>Botdan foydalanish qoidalari:</b>\n\n"
        "1. Faqat real akkauntlar e'lon qilinishi shart.\n"
        "2. Yolg'on ma'lumot berish taqiqlanadi.\n"
        "3. To'lov qilingandan so'ng e'lon kanalda chiqariladi.\n"
        "4. Barcha savdolar @kattabekov orqali (Garant) amalga oshirilishi tavsiya etiladi."
    )
    bot.send_message(message.chat.id, rules, parse_mode="HTML")

# --- E'LONLARIM BO'LIMI ---
@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    bot.send_message(message.chat.id, "🗂 <b>Sizning e'lonlaringiz:</b>\n\nHali sizda faol e'lonlar mavjud emas.", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def price_info(message):
    bot.send_message(message.chat.id, "💳 <b>E'lon berish narxi: 2 000 so'm.</b>\nTo'lov uchun: @kattabekov", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admin_info(message):
    bot.send_message(message.chat.id, "👤 <b>Asosiy admin:</b> @kattabekov", parse_mode="HTML")

# --- E'LON BERISH JARAYONI ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def start_ad(message):
    bot.send_message(message.chat.id, "📸 <b>Akkaunt rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Rasm yuboring!")
        bot.register_next_step_handler(message, get_photo)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Narxi (Masalan: 50 000 so'm):</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Batafsil ma'lumot (Level, Oyinchilar va h.k.):</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_desc)

def get_desc(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    uid = message.chat.id
    bot.send_message(uid, "✅ <b>Rahmat! Ma'lumotlar adminga yuborildi.</b>", parse_mode="HTML")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"p_{uid}"))
    bot.send_photo(ADMIN_ID, user_temp[uid]['photo'], 
                   caption=f"🔔 <b>Yangi e'lon!</b>\n\nNarxi: {user_temp[uid]['price']}\nMa'lumot: {user_temp[uid]['desc']}", 
                   parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("p_"))
def final_publish(call):
    uid = int(call.data.split("_")[1])
    d = user_temp.get(uid)
    if not d: return

    user = bot.get_chat(uid)
    contact = f"@{user.username}" if user.username else f"ID: {uid}"
    
    # KANALGA CHIQADIGAN E'LON (FAST TUGMASI BILAN)
    caption = (
        f"🔥 <b>#SOTILADI #FAST</b>\n\n"
        f"💰 <b>Narxi:</b> {d['price']}\n"
        f"📝 <b>Ma'lumot:</b> {d['desc']}\n"
        f"👤 <b>Murojaat:</b> {contact}\n\n"
        f"♻️ <b>Garant:</b> @kattabekov\n"
        f"📢 <b>Kanal:</b> {CHANNEL_ID}"
    )

    # FAST TUGMASI (Inline)
    fast_markup = types.InlineKeyboardMarkup()
    fast_markup.add(types.InlineKeyboardButton("⚡️ TEZKOR SOTIB OLISH", url=f"https://t.me/kattabekov"))

    bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML", reply_markup=fast_markup)
    bot.send_message(uid, "🎉 <b>E'loningiz kanalga 'FAST' tugmasi bilan joylandi!</b>", parse_mode="HTML")
    bot.edit_message_caption("✅ Kanalga chiqdi!", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
