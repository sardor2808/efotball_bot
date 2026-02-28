import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
import re

# --- 🌐 RENDER BARQARORLIGI UCHUN ---
app = Flask('')

@app.route('/')
def home():
    return "Bot status: Aktiv va Hushmuomala 😊"

def run_web():
    # Render portni avtomatik aniqlashi uchun os.environ ishlatamiz
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- 🟢 BOT SOZLAMALARI ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)

MY_ADMIN_TEXT = "    ◾️ @kattabekov"
OLISH_IMAGE = "https://i.ibb.co/3ykC6W2/olaman-efuz.jpg"
user_temp = {}

# --- ⌨️ ASOSIY KLAVIATURA ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🔍 Akkaunt qidirish"))
    markup.add(types.KeyboardButton("➕ E'lon berish"), types.KeyboardButton("📂 E'lonlarim"))
    markup.add(types.KeyboardButton("👨‍💻 Adminlar"), types.KeyboardButton("📚 Qoidalar"))
    markup.add(types.KeyboardButton("💰 E'lon narxlari"))
    return markup

# --- 🔄 BUYRUQLAR ---
@bot.message_handler(commands=['start'])
def welcome(message):
    ism = message.from_user.first_name
    bot.send_message(
        message.chat.id, 
        f"👋 <b>Assalomu alaykum, {ism} aka/opa!</b>\n\n"
        "eFootball 1v1 bozoriga xush kelibsiz! 😊 Sizga akkauntingizni sotishda yoki "
        "yangi, toza akkaunt topishingizda yordam berishdan judayam xursandmiz. ✨", 
        reply_markup=main_menu(), 
        parse_mode="HTML"
    )

# --- 👨‍💻 ADMINLAR (IDEAL HOLATDA QOLDIRILDI) ---
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def show_admins(message):
    text = (
        "♻️ <b>OLDI SOTDI ADMINI</b>\n\n"
        f"{MY_ADMIN_TEXT}\n\n"
        "✨ Barcha savollar va xaridlar bo'yicha faqatgina adminga murojaat qiling. "
        "Xavfsizligingiz biz uchun har doim birinchi o'rinda! 😊"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💂‍♂️ Asosiy Admin bilan bog'lanish", url="https://t.me/kattabekov"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

# --- ➕ E'LON BERISH BOSQICHLARI ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def start_ad(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔺 Sotish e'loni", callback_data="type_sotish"),
        types.InlineKeyboardButton("🔻 Olish e'loni", callback_data="type_olish")
    )
    bot.send_message(
        message.chat.id, 
        "❓ <b>Xo'sh, bugun qanday e'lon beramiz?</b>\n\nMarhamat, o'zingizga kerakli bo'limni tanlang:", 
        reply_markup=markup, 
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("type_"))
def handle_ad_type(call):
    user_temp[call.message.chat.id] = {"type": call.data.split("_")[1]}
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if user_temp[call.message.chat.id]["type"] == "sotish":
        msg = bot.send_message(call.message.chat.id, "📸 <b>Baraka bersin! Birinchi bo'lib akkauntingizning eng chiroyli rasmini yuboring:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, s_photo)
    else:
        msg = bot.send_message(call.message.chat.id, "💵 <b>Akkaunt sotib olish uchun qancha budjet ajratgansiz?</b> (Masalan: 200.000)", parse_mode="HTML")
        bot.register_next_step_handler(msg, o_budget)

def s_photo(message):
    if not message.photo:
        msg = bot.send_message(message.chat.id, "⚠️ <b>Iltimos, akkauntning skrinshotini (rasmini) yuboring:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, s_photo); return
    user_temp[message.chat.id]['photo'] = message.photo[-1].file_id
    msg = bot.send_message(message.chat.id, "💰 <b>Endi akkauntingiz narxini kiriting:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_price)

def s_price(message):
    user_temp[message.chat.id]['price'] = message.text
    msg = bot.send_message(message.chat.id, "🔄 <b>Almashish (Obmen) bormi?</b> (Bor yoki Yo'q deb yozing):", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_obmen)

def s_obmen(message):
    user_temp[message.chat.id]['obmen'] = message.text
    msg = bot.send_message(message.chat.id, "⚠️ <b>Akkaunt holati (Google & Game Center) haqida qisqacha yozing:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_info)

def s_info(message):
    user_temp[message.chat.id]['info'] = message.text
    msg = bot.send_message(message.chat.id, "📋 <b>Va nihoyat! Akkauntning boshqa afzalliklari haqida batafsil ma'lumot bering:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_final)

def s_final(message):
    uid = message.chat.id
    d = user_temp[uid]
    user = bot.get_chat(uid)
    contact = f"@{user.username}" if user.username else f"ID: {uid}"
    
    caption = (
        f"🔥 <b>#SOTILADI</b>\n\n"
        f"💰 <b>Narxi:</b> {d['price']}\n"
        f"♻️ <b>Obmen ko'rish:</b> {d['obmen']}\n"
        f"⚠️ <b>Ma'lumot:</b> {d['info']}\n"
        f"👤 <b>Murojaat:</b> {contact}\n\n"
        f"📋 <b>Qo'shimcha:</b>\n<i>{message.text}</i>\n\n"
        f"♻️ <b>OLDI SOTDI ADMINI</b>\n"
        f"{MY_ADMIN_TEXT}\n\n"
        f"🔻 <b>ELON BERISH UCHUN BOTIMIZ:</b>\n"
        f"@{bot.get_me().username}"
    )
    bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    bot.send_message(uid, "🎉 <b>Ajoyib!</b> E'loningiz kanalga joylandi. Tez orada xaridor topilishiga ishonamiz! 😊", reply_markup=main_menu(), parse_mode="HTML")

def o_budget(message):
    user_temp[message.chat.id]['budget'] = message.text
    msg = bot.send_message(message.chat.id, "📋 <b>Qanday akkaunt qidiryapsiz? Batafsil yozib bering:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, o_final)

def o_final(message):
    uid = message.chat.id
    user = bot.get_chat(uid)
    contact = f"@{user.username}" if user.username else f"ID: {uid}"
    
    caption = (
        f"⚡️ <b>#OLINADI #FAQAT_TOZA</b>\n\n"
        f"💵 <b>BUDJET:</b> {user_temp[uid]['budget']}\n"
        f"📋 <b>Ma'lumot:</b>\n<i>{message.text}</i>\n"
        f"👤 <b>Murojaat:</b> {contact}\n\n"
        f"♻️ <b>OLDI SOTDI ADMINI</b>\n"
        f"{MY_ADMIN_TEXT}\n\n"
        f"🔻 <b>ELON BERISH UCHUN BOTIMIZ:</b>\n"
        f"@{bot.get_me().username}"
    )
    try:
        bot.send_photo(CHANNEL_ID, OLISH_IMAGE, caption=caption, parse_mode="HTML")
    except:
        bot.send_message(CHANNEL_ID, caption, parse_mode="HTML")
    bot.send_message(uid, "✅ <b>Tayyor!</b> Olish e'loningiz ham kanalimizdan joy oldi. ✨", reply_markup=main_menu(), parse_mode="HTML")

# --- 💰 ELON NARXLARI ---
@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def prices(message):
    bot.send_message(
        message.chat.id, 
        "🎁 <b>Siz uchun ajoyib yangilik!</b>\n\nHozirda bizning botimizda e'lon joylashtirish <b>mutlaqo BEPUL</b>! 🎁\n\n"
        "Fursatdan foydalanib, e'loningizni hoziroq joylang! 😉", 
        parse_mode="HTML"
    )

# --- 📚 QOIDALAR ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules(message):
    bot.send_message(
        message.chat.id, 
        "🛑 <b>Muhim eslatma:</b>\n\n"
        "1. Faqat <b>toza</b> akkauntlarni soting.\n"
        "2. Aldov aralashgan e'lonlar uchun egasi butunlay bloklanadi.\n"
        "3. Har doim <b>Garant</b> xizmatidan foydalaning! ✅", 
        parse_mode="HTML"
    )

# --- QOLGAN BO'LIMLAR ---
@bot.message_handler(func=lambda m: m.text == "🔍 Akkaunt qidirish")
def search_off(message):
    bot.send_message(message.chat.id, "🔍 <b>Akkaunt qidirish tizimi hozirda yangilanmoqda.</b>\nTez orada bu funksiya yana ishga tushadi! 😊", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    bot.send_message(message.chat.id, "📁 <b>Sizning e'lonlaringiz ro'yxati:</b>\n\nBu bo'lim hali ishga tushmadi, lekin tez orada tayyor bo'ladi! ⏳", parse_mode="HTML")

# --- 🏁 ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
