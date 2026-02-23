import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVER QISMI ---
app = Flask('')
@app.route('/')
def home(): return "Bot is live!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- BOT SOZLAMALARI ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822  # Sizning ID
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)
user_temp = {}
published_ads = {} # E'lonlarim bo'limi uchun

# --- ASOSIY MENYU ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ E'lon berish", "📂 E'lonlarim", "👨‍💻 Adminlar", "📚 Qoidalar", "💰 E'lon narxlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌟 <b>Assalomu alaykum!</b>\nAkkaunt sotish uchun barcha ma'lumotlarni kiriting.", reply_markup=main_menu(), parse_mode="HTML")

# --- QOIDALAR ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules(message):
    bot.send_message(message.chat.id, "1. Yolg'on ma'lumot taqiqlanadi.\n2. To'lovdan so'ng e'lon chiqadi.")

# --- E'LONLARIM BO'LIMI ---
@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads:
        for ad in published_ads[uid]:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⚡️ FAST (TEZKOR)", callback_data="fast_info"))
            bot.send_photo(uid, ad['photo'], caption=ad['caption'], reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(uid, "🗂 Sizda hali tasdiqlangan e'lonlar yo'q.")

@bot.callback_query_handler(func=lambda call: call.data == "fast_info")
def fast_info(call):
    bot.answer_callback_query(call.id, "Bu e'lon tezkor sotuvda!", show_alert=True)

# --- E'LON BERISH VA TO'LOV ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def start_ad(message):
    bot.send_message(message.chat.id, "📸 Akkaunt rasmini yuboring:")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Rasm yuboring!")
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 Akkaunt narxi:")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 Akkaunt haqida batafsil ma'lumot (Level, o'yinchilar):")
    bot.register_next_step_handler(message, get_desc)

def get_desc(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    # TO'LOV BOSQICHI
    payment_text = (
        "💳 <b>To'lov qilish vaqti keldi!</b>\n\n"
        "E'lon narxi: 2 000 so'm\n"
        "Karta raqami: <code>8600123456789012</code> (Namuna)\n"
        "Ega: SARDORBEK K.\n\n"
        "✅ To'lovni amalga oshirib, <b>chekni (skrinshot)</b> shu yerga yuboring!"
    )
    bot.send_message(message.chat.id, payment_text, parse_mode="HTML")
    bot.register_next_step_handler(message, get_check)

def get_check(message):
    uid = message.chat.id
    if not message.photo:
        bot.send_message(uid, "⚠️ Iltimos, to'lov chekini rasm ko'rinishida yuboring!")
        bot.register_next_step_handler(message, get_check)
        return
    
    bot.send_message(uid, "⏳ <b>Rahmat! To'lovingiz adminga yuborildi.</b> Tasdiqlangach e'lon kanalga chiqadi.")
    
    # ADMINGA TASDIQLASH UCHUN
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{uid}"),
               types.InlineKeyboardButton("❌ Rad etish", callback_data=f"no_{uid}"))
    
    # Adminga chekni yuborish
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"💰 <b>Yangi to'lov cheki!</b>\nFoydalanuvchi: @{message.from_user.username}", parse_mode="HTML")
    # Adminga e'lonni yuborish
    bot.send_photo(ADMIN_ID, user_temp[uid]['photo'], 
                   caption=f"📋 <b>E'lon ma'lumotlari:</b>\n\nNarxi: {user_temp[uid]['price']}\nMa'lumot: {user_temp[uid]['desc']}", 
                   parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(("ok_", "no_")))
def admin_verify(call):
    action, uid = call.data.split("_")
    uid = int(uid)
    
    if action == "ok":
        d = user_temp.get(uid)
        if d:
            contact = f"@{call.from_user.username}" if call.from_user.username else f"ID: {uid}"
            caption = f"🔥 <b>#SOTILADI</b>\n\n💰 Narxi: {d['price']}\n📝 Ma'lumot: {d['desc']}\n👤 Murojaat: {contact}\n\n♻️ Garant: @kattabekov"
            
            # Kanalga chiqarish
            bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
            
            # E'lonlarim bo'limiga saqlash
            if uid not in published_ads: published_ads[uid] = []
            published_ads[uid].append({'photo': d['photo'], 'caption': caption})
            
            bot.send_message(uid, "🎉 <b>Xushxabar! To'lovingiz tasdiqlandi va e'lon kanalga chiqdi.</b>")
            bot.edit_message_caption("✅ Tasdiqlandi", call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(uid, "❌ Afsuski, to'lovingiz tasdiqlanmadi. Qayta urinib ko'ring yoki adminga yozing.")
        bot.edit_message_caption("❌ Rad etildi", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
