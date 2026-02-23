import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVER QISMI (Render o'chirmasligi uchun) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is live!"
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
    markup.add("➕ Elon berish", "📂 Elonlarim", "👨‍💻 Adminlar", "📚 Qoidalar", "💰 Elon narxlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ <b>Bot serverda 24/7 rejimida ishga tushdi!</b>\n\nQuyidagi menyudan foydalaning:", 
                     reply_markup=main_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 Elon narxlari")
def price_info(message):
    bot.send_message(message.chat.id, "💳 <b>Elon berish narxi: 2 000 so'm.</b>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admin_info(message):
    bot.send_message(message.chat.id, "👨‍💻 <b>Asosiy admin:</b> @kattabekov", parse_mode="HTML")

# --- ELON BERISH JARAYONI ---
@bot.message_handler(func=lambda m: m.text == "➕ Elon berish")
def start_ad(message):
    bot.send_message(message.chat.id, "📸 <b>Akkauntingiz rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Iltimos, rasm yuboring!")
        bot.register_next_step_handler(message, get_photo)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Akkaunt narxini kiriting:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Akkaunt haqida qisqacha izoh yozing:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_desc)

def get_desc(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    uid = message.chat.id
    bot.send_message(uid, "✅ <b>Ma'lumotlar qabul qilindi.</b> Tez orada kanalga joylanadi.", parse_mode="HTML")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"p_{uid}"))
    bot.send_photo(ADMIN_ID, user_temp[uid]['photo'], 
                   caption=f"🔔 <b>Yangi e'lon!</b>\n\nNarxi: {user_temp[uid]['price']}\nIzoh: {user_temp[uid]['desc']}", 
                   parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("p_"))
def final_publish(call):
    uid = int(call.data.split("_")[1])
    d = user_temp.get(uid)
    if not d: return
    user = bot.get_chat(uid)
    contact = f"@{user.username}" if user.username else f"ID: {uid}"
    caption = (f"🔥 <b>#SOTILADI</b>\n\n💰 <b>Narxi:</b> {d['price']}\n☎️ <b>Murojaat:</b> {contact}\n📋 <b>Izoh:</b> {d['desc']}\n\n♻️ <b>GARANT:</b> @kattabekov")
    bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    bot.send_message(uid, "🎉 <b>E'loningiz kanalga joylandi!</b>", parse_mode="HTML")
    bot.edit_message_caption("✅ Kanalga chiqdi!", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
  
