import telebot
from telebot import types
import os

# --- 🟢 YANGI BOT SOZLAMALARI ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822
CHANNEL_ID = "@efotball_1v1" # Kanal linkidan yuzerneym olindi

bot = telebot.TeleBot(TOKEN)

# SIZ YAGONA ADMINSIZ
MY_ADMIN_TEXT = "    ◾️ @kattabekov"

# Olish eloni uchun rasm
OLISH_IMAGE = "https://i.ibb.co/3ykC6W2/olaman-efuz.jpg"

user_temp = {}

# --- ⌨️ KLAVIATURA ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🔍 Akkaunt qidirish"))
    markup.add(types.KeyboardButton("➕ Elon berish"), types.KeyboardButton("📂 Elonlarim"))
    markup.add(types.KeyboardButton("👨‍💻 Adminlar"), types.KeyboardButton("📚 Qoidalar"))
    markup.add(types.KeyboardButton("💰 Elon narxlari"))
    return markup

# --- 👤 ADMINLAR BO'LIMI ---
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def show_admins(message):
    text = (
        "♻️ <b>OLDI SOTDI ADMINI</b>\n\n"
        f"{MY_ADMIN_TEXT}\n\n"
        "✨ Barcha savollar va xaridlar bo'yicha faqatgina adminga murojaat qiling. 😊"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💂‍♂️ Asosiy Admin", url="https://t.me/kattabekov"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

# --- 📢 E'LON CHIQARISH (INTERFEYS) ---
def s_final(message):
    uid = message.chat.id
    d = user_temp[uid]
    contact = f"@{message.from_user.username}" if message.from_user.username else f"ID: {uid}"
    
    caption = (
        f"🔥 <b>#SOTILADI</b>\n\n"
        f"💰 <b>Narxi:</b> {d['price']} so'm\n"
        f"♻️ <b>Obmen ko'rish:</b> {d['obmen']}\n"
        f"⚠️ <b>Google & Game Center:</b> {d['info']}\n"
        f"👤 <b>Murojaat:</b> {contact}\n\n"
        f"📋 <b>Qo'shimcha ma'lumot:</b>\n<i>{message.text}</i>\n\n"
        f"♻️ <b>OLDI SOTDI ADMINI</b>\n"
        f"{MY_ADMIN_TEXT}\n\n"
        f"🔻 <b>ELON BERISH UCHUN BOTIMIZ:</b>\n"
        f"@{bot.get_me().username}"
    )
    bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    bot.send_message(uid, "🎉 <b>Tabriklaymiz!</b> E'loningiz kanalga muvaffaqiyatli joylandi.", reply_markup=main_menu(), parse_mode="HTML")

def o_final(message):
    uid = message.chat.id
    contact = f"@{message.from_user.username}" if message.from_user.username else f"ID: {uid}"
    
    caption = (
        f"⚡️ <b>#OLINADI #FAQAT_TOZA</b>\n\n"
        f"💵 <b>BUDJET:</b> {user_temp[uid]['budget']} so'm\n"
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
    bot.send_message(uid, "✅ <b>Tayyor!</b> Olish e'loningiz kanalga yuborildi.", reply_markup=main_menu(), parse_mode="HTML")

# --- 🔄 SAVOL-JAVOB TIZIMI ---
@bot.message_handler(func=lambda m: m.text == "➕ Elon berish")
def start_ad(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔺 Sotish eloni", callback_data="type_sotish"),
        types.InlineKeyboardButton("🔻 Olish eloni", callback_data="type_olish")
    )
    bot.send_message(message.chat.id, "❓ <b>Qanday e'lon bermoqchisiz?</b>", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("type_"))
def handle_ad_type(call):
    user_temp[call.message.chat.id] = {"type": call.data.split("_")[1]}
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if user_temp[call.message.chat.id]["type"] == "sotish":
        msg = bot.send_message(call.message.chat.id, "📸 <b>Akkaunt rasmini yuboring:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, s_photo)
    else:
        msg = bot.send_message(call.message.chat.id, "💵 <b>Budjetingizni kiriting:</b>\n(Masalan: 300.000)", parse_mode="HTML")
        bot.register_next_step_handler(msg, o_budget)

def s_photo(message):
    if not message.photo:
        msg = bot.send_message(message.chat.id, "⚠️ Iltimos, rasm yuboring:"); bot.register_next_step_handler(msg, s_photo); return
    user_temp[message.chat.id]['photo'] = message.photo[-1].file_id
    msg = bot.send_message(message.chat.id, "💰 <b>Narxini kiriting:</b>", parse_mode="HTML"); bot.register_next_step_handler(msg, s_price)

def s_price(message):
    user_temp[message.chat.id]['price'] = message.text
    msg = bot.send_message(message.chat.id, "🔄 <b>Obmen bormi? (Bor/Yo'q):</b>", parse_mode="HTML"); bot.register_next_step_handler(msg, s_obmen)

def s_obmen(message):
    user_temp[message.chat.id]['obmen'] = message.text
    msg = bot.send_message(message.chat.id, "⚠️ <b>Holati qanday?</b>", parse_mode="HTML"); bot.register_next_step_handler(msg, s_info)

def s_info(message):
    user_temp[message.chat.id]['info'] = message.text
    msg = bot.send_message(message.chat.id, "📋 <b>Akkaunt haqida batafsil yozing:</b>", parse_mode="HTML"); bot.register_next_step_handler(msg, s_final)

def o_budget(message):
    user_temp[message.chat.id]['budget'] = message.text
    msg = bot.send_message(message.chat.id, "📋 <b>Qanday akkaunt qidiryapsiz?</b>", parse_mode="HTML"); bot.register_next_step_handler(msg, o_final)

# --- 🚀 START VA BOSHQALAR ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\neFootball 1v1 botiga xush kelibsiz. E'lon berish hozirda <b>mutlaqo BEPUL</b>. 😊", reply_markup=main_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 Elon narxlari")
def prices(message):
    bot.send_message(message.chat.id, "🎁 <b>E'lon berish hozirda MUTLAQO BEPUL!</b>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules(message):
    bot.send_message(message.chat.id, "🛑 <b>Asosiy qoida:</b> Aldovsiz savdo qiling. Faqat eFootball akkauntlari uchun!", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔍 Akkaunt qidirish")
def search_off(message):
    bot.send_message(message.chat.id, "❌ Qidiruv tizimi vaqtincha faol emas.", parse_mode="HTML")

bot.polling(none_stop=True)
                     
