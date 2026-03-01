import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- 🌐 SERVER SOZLAMASI ---
app = Flask('')
@app.route('/')
def home():
    return "Bot holati: Alo darajada! 😊"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- 🟢 BOT SOZLAMALARI ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822
CHANNEL_ID = "@efotball_1v1" # E'lonlar tushadigan kanal
OFFICIAL_PAGE = "@efotball_1v1" # Rasmiy sahifa linki
bot = telebot.TeleBot(TOKEN)

# DIZAYN ELEMENTLARI
MY_ADMIN_TEXT = "♻️ <b>OLDI SOTDI ADMINI</b>\n    ◾️ @kattabekov"
BOT_LINK = "@efotball1v1_bot"
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

# --- 🔄 START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def welcome(message):
    ism = message.from_user.first_name
    bot.send_message(
        message.chat.id, 
        f"👋 <b>Assalomu alaykum, {ism} aka!</b>\n\n"
        "eFootball bozorimizga xush kelibsiz! 😊 Bu yerda siz xavfsiz va tez e'lon bera olasiz. "
        "Sizga qanday yordam bera olaman?", 
        reply_markup=main_menu(), 
        parse_mode="HTML"
    )

# --- 👨‍💻 ADMINLAR BO'LIMI ---
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def show_admins(message):
    text = (
        f"{MY_ADMIN_TEXT}\n\n"
        "✨ Savollaringiz bormi? Adminimiz har doim sizga yordam berishga tayyor! "
        "Bemalol murojaat qilishingiz mumkin. 😊"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💂‍♂️ Adminga yozish", url="https://t.me/kattabekov"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

# --- ➕ E'LON BERISH BOSQICHLARI ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def start_ad(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔺 Sotish e'loni", callback_data="type_sotish"),
        types.InlineKeyboardButton("🔻 Olish e'loni", callback_data="type_olish")
    )
    bot.send_message(message.chat.id, "❓ <b>Bugun qanday e'lon joylashtiramiz?</b>", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("type_"))
def handle_ad_type(call):
    user_temp[call.message.chat.id] = {"type": call.data.split("_")[1]}
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if user_temp[call.message.chat.id]["type"] == "sotish":
        msg = bot.send_message(call.message.chat.id, "📸 <b>Baraka bersin! Akkaunt rasmini yuboring:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, s_photo)
    else:
        msg = bot.send_message(call.message.chat.id, "💵 <b>Budjetingiz qancha?</b> (Masalan: 100 ming so'm)", parse_mode="HTML")
        bot.register_next_step_handler(msg, o_budget)

# --- 📢 SOTISH YAKUNI (XATOLAR TO'G'RILANGAN) ---
def s_final(message):
    uid = message.chat.id
    d = user_temp[uid]
    # Username yo'q bo'lsa, ism yoki "Foydalanuvchi" chiqadi
    user_link = f"@{message.from_user.username}" if message.from_user.username else f"<a href='tg://user?id={uid}'>{message.from_user.first_name}</a>"
    
    caption = (
        f"🔥 <b>#SOTILADI</b>\n\n"
        f"💰 <b>Narxi:</b> {d['price']}\n"
        f"♻️ <b>Obmen ko'rish:</b> {d['obmen']}\n"
        f"⚠️ <b>Ma'lumot:</b> {d['info']}\n"
        f"👤 <b>Murojaat:</b> {user_link}\n\n"
        f"📋 <b>Qo'shimcha:</b>\n<i>{message.text}</i>\n\n"
        f"🏝 <b>Rasmiy sahifamiz:</b> {OFFICIAL_PAGE}\n\n"
        f"{MY_ADMIN_TEXT}\n"
        f"🔻 <b>ELON BERISH UCHUN BOTIMIZ:</b>\n"
        f"{BOT_LINK}"
    )
    bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    bot.send_message(uid, "🎉 <b>Tabriklaymiz!</b> E'loningiz kanalga joylandi. ✨", reply_markup=main_menu(), parse_mode="HTML")

# --- 📢 OLISH YAKUNI ---
def o_final(message):
    uid = message.chat.id
    user_link = f"@{message.from_user.username}" if message.from_user.username else f"<a href='tg://user?id={uid}'>{message.from_user.first_name}</a>"
    
    caption = (
        f"⚡️ <b>#OLINADI #FAQAT_TOZA</b>\n\n"
        f"💵 <b>BUDJET:</b> {user_temp[uid]['budget']}\n"
        f"📋 <b>Ma'lumot:</b>\n<i>{message.text}</i>\n"
        f"👤 <b>Murojaat:</b> {user_link}\n\n"
        f"🏝 <b>Rasmiy sahifamiz:</b> {OFFICIAL_PAGE}\n\n"
        f"{MY_ADMIN_TEXT}\n"
        f"🔻 <b>ELON BERISH UCHUN BOTIMIZ:</b>\n"
        f"{BOT_LINK}"
    )
    try:
        bot.send_photo(CHANNEL_ID, OLISH_IMAGE, caption=caption, parse_mode="HTML")
    except:
        bot.send_message(CHANNEL_ID, caption, parse_mode="HTML")
    bot.send_message(uid, "✅ <b>Tayyor!</b> Olish e'loningiz kanalga yuborildi. ✨", reply_markup=main_menu(), parse_mode="HTML")

# --- 🛠 BOSHQARUV FUNKSIYALARI (SOTISH) ---
def s_photo(message):
    if not message.photo:
        msg = bot.send_message(message.chat.id, "⚠️ Iltimos, rasm yuboring:"); bot.register_next_step_handler(msg, s_photo); return
    user_temp[message.chat.id]['photo'] = message.photo[-1].file_id
    msg = bot.send_message(message.chat.id, "💰 <b>Narxini yozing:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_price)

def s_price(message):
    user_temp[message.chat.id]['price'] = message.text
    msg = bot.send_message(message.chat.id, "🔄 <b>Obmen bormi?</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_obmen)

def s_obmen(message):
    user_temp[message.chat.id]['obmen'] = message.text
    msg = bot.send_message(message.chat.id, "⚠️ <b>Google & Game Center holati:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_info)

def s_info(message):
    user_temp[message.chat.id]['info'] = message.text
    msg = bot.send_message(message.chat.id, "📋 <b>Batafsil ma'lumot kiriting:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, s_final)

def o_budget(message):
    user_temp[message.chat.id]['budget'] = message.text
    msg = bot.send_message(message.chat.id, "📋 <b>Qanday akkaunt kerak?</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, o_final)

# --- 💰 QOLGAN BO'LIMLAR ---
@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def prices(message):
    bot.send_message(message.chat.id, "🎁 <b>Hozircha e'lon berish BEPUL!</b> 😊\n\nImkoniyatni boy bermang va e'loningizni joylang!", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules(message):
    bot.send_message(message.chat.id, "🛑 <b>Qoidamiz juda oddiy:</b>\n\nFaqat toza akkauntlar sotilsin. Aldovga harakat qilganlar butunlay bloklanadi! ✅", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔍 Akkaunt qidirish")
def search_off(message):
    bot.send_message(message.chat.id, "🔍 Bu bo'lim tez orada ishga tushadi. Yangiliklarni kutib qoling! 😊", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    bot.send_message(message.chat.id, "📁 Sizning e'lonlaringiz tarixi bu yerda ko'rinadi (Tez orada).", parse_mode="HTML")

# --- 🏁 ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
