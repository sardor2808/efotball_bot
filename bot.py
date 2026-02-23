import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVERNI "UYG'OQ" TUTISH ---
app = Flask('')
@app.route('/')
def home(): return "Bot is live and polite!"
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
    welcome_text = (
        "🌟 <b>Assalomu alaykum!</b>\n\n"
        "E'lon berish botimizga xush kelibsiz. Biz orqali akkauntingizni tez va ishonchli sotishingiz mumkin. "
        "Marhamat, quyidagi tugmalardan birini tanlang:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def price_info(message):
    price_text = (
        "💎 <b>E'lon berish xizmati:</b>\n\n"
        "Sizning e'loningiz kanalda 24 soat davomida turadi.\n"
        "💵 <b>Narxi:</b> 2 000 so'm\n\n"
        "To'lov uchun adminga murojaat qiling."
    )
    bot.send_message(message.chat.id, price_text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admin_info(message):
    bot.send_message(message.chat.id, "👤 <b>Asosiy admin:</b> @kattabekov\n\nSavollaringiz bo'lsa, bemalol murojaat qiling!", parse_mode="HTML")

# --- E'LON BERISH (BATAFSIL VARIANT) ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def start_ad(message):
    bot.send_message(message.chat.id, "📸 <b>Ajoyib! Avvalo akkauntingizning asosiy rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Iltimos, rasm formatida yuboring.")
        bot.register_next_step_handler(message, get_photo)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Akkaunt narxini qancha belgilaymiz?</b> (Masalan: 50.000 so'm):", parse_mode="HTML")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    user_temp[message.chat.id]['price'] = message.text
    desc_msg = (
        "📝 <b>Endi akkaunt haqida batafsil ma'lumot bering:</b>\n\n"
        "Masalan: <i>Darajasi, ichidagi o'yinchilar, qaysi ligalarda qatnashgan va h.k.</i>"
    )
    bot.send_message(message.chat.id, desc_msg, parse_mode="HTML")
    bot.register_next_step_handler(message, get_desc)

def get_desc(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    uid = message.chat.id
    bot.send_message(uid, "✅ <b>Rahmat! Ma'lumotlar adminga yuborildi.</b>\nTez orada ko'rib chiqiladi va kanalga joylanadi.", parse_mode="HTML")
    
    # ADMINGA CHIROYLI E'LON
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash va Kanalga chiqarish", callback_data=f"p_{uid}"))
    bot.send_photo(ADMIN_ID, user_temp[uid]['photo'], 
                   caption=f"🆕 <b>Yangi e'lon kutmoqda!</b>\n\n💰 <b>Narxi:</b> {user_temp[uid]['price']}\n📋 <b>Ma'lumot:</b> {user_temp[uid]['desc']}", 
                   parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("p_"))
def final_publish(call):
    uid = int(call.data.split("_")[1])
    d = user_temp.get(uid)
    if not d: return

    user = bot.get_chat(uid)
    contact = f"@{user.username}" if user.username else f"ID: {uid}"
    
    # KANALGA CHIQADIGAN BATAZSIL E'LON SHABLONI
    caption = (
        f"🔥 <b>#SOTILADI #EFOOTBALL</b>\n\n"
        f"💳 <b>Narxi:</b> {d['price']}\n"
        f"📝 <b>Ma'lumot:</b> {d['desc']}\n"
        f"👤 <b>Murojaat:</b> {contact}\n\n"
        f"🤝 <b>Garant:</b> @kattabekov\n"
        f"📢 <b>Kanal:</b> {CHANNEL_ID}"
    )

    bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    bot.send_message(uid, "🎉 <b>Tabriklaymiz! E'loningiz kanalga joylandi.</b>", parse_mode="HTML")
    bot.edit_message_caption("✅ Kanalga muvaffaqiyatli chiqdi!", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
