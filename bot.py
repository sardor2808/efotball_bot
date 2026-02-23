import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVERNI UYGOQ TUTISH ---
app = Flask('')
@app.route('/')
def home(): return "Bot 24/7 rejimida va xushmuomala!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- ASOSIY SOZLAMALAR ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822 
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)

# NAMUNA RASM (Sizga profilingiz rasmini qaytarmasligi uchun umumiy rasm linki)
SHABLON_RASM = "https://img.freepik.com/free-vector/gaming-controller-concept-illustration_114360-3162.jpg"

user_temp = {}
published_ads = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ E'lon berish", "📂 E'lonlarim", "👨‍💻 Adminlar", "📚 Qoidalar", "💰 E'lon narxlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    ism = message.from_user.first_name
    welcome_text = (
        f"🌟 <b>Assalomu alaykum, {ism}!</b>\n\n"
        f"E'lon berish botimizga xush kelibsiz. 😊\n"
        f"Bu yerda siz o'z akkauntingizni tez va ishonchli sota olasiz.\n\n"
        f"👇 Marhamat, quyidagi tugmalardan birini tanlang:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")

# --- BO'LIMLARNI ISHLATISH ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules_info(message):
    text = (
        "📚 <b>Botdan foydalanish qoidalari:</b>\n\n"
        "1️⃣ Akkaunt haqida faqat to'g'ri ma'lumot bering.\n"
        "2️⃣ To'lov chekini yuborgach, e'lon ko'rib chiqiladi.\n"
        "3️⃣ Barcha savdolarni @kattabekov orqali qiling.\n"
        "4️⃣ Aldovga urinish botdan bloklanishga sabab bo'ladi."
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admin_info(message):
    bot.send_message(message.chat.id, "👨‍💻 <b>Asosiy admin:</b> @kattabekov\n\nHar qanday savolingiz bo'lsa, tortinmasdan murojaat qiling! 😊", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def price_info(message):
    text = (
        "💰 <b>E'lon berish narxlari:</b>\n\n"
        "✨ Oddiy e'lon: <b>2 000 so'm</b>\n"
        "⚡️ FAST (Tezkor) xizmati: <b>2 marta BEPUL</b> (E'lonlarim bo'limida)\n\n"
        "To'lovni amalga oshirgach, e'loningiz kanalga chiqariladi."
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# --- E'LONLARIM VA FAST ---
@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads and published_ads[uid]:
        bot.send_message(uid, "🗂 <b>Sizning tasdiqlangan e'lonlaringiz:</b>", parse_mode="HTML")
        for idx, ad in enumerate(published_ads[uid]):
            markup = types.InlineKeyboardMarkup()
            btn_text = f"⚡️ FAST (Imkoniyat: {ad['fast_count']})"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"fast_{uid}_{idx}"))
            bot.send_photo(uid, ad['photo'], caption=ad['caption'], reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(uid, "😕 <b>Sizda hali tasdiqlangan e'lonlar yo'q.</b>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fast_"))
def handle_fast(call):
    _, uid, idx = call.data.split("_")
    uid, idx = int(uid), int(idx)
    ad = published_ads[uid][idx]
    if ad['fast_count'] > 0:
        ad['fast_count'] -= 1
        bot.send_photo(CHANNEL_ID, ad['photo'], caption=f"⚡️ <b>TEZKOR SOTUV!</b>\n\n{ad['caption']}", parse_mode="HTML")
        bot.answer_callback_query(call.id, f"🚀 E'lon kanalga qayta chiqdi! (Qolgan imkoniyat: {ad['fast_count']})", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ Bu e'lon uchun FAST imkoniyatlari tugagan!", show_alert=True)

# --- E'LON BERISH ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def step1(message):
    bot.send_photo(message.chat.id, SHABLON_RASM, caption="📸 <b>Iltimos, akkauntingizning asosiy rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step2)

def step2(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Iltimos, rasm yuboring!")
        bot.register_next_step_handler(message, step2)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Akkauntingiz narxini kiriting:</b>\n(Masalan: 75 000 so'm)", parse_mode="HTML")
    bot.register_next_step_handler(message, step3)

def step3(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Endi akkaunt haqida batafsil ma'lumot bering:</b>\n(Level, o'yinchilar, bog'langan loginlar)", parse_mode="HTML")
    bot.register_next_step_handler(message, step4)

def step4(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    payment_msg = (
        "💳 <b>To'lov ma'lumotlari:</b>\n\n"
        "Karta raqami: <code>5440810304875684</code>\n"
        "Ega: <b>G A</b>\n\n"
        "✅ To'lovni amalga oshirib, <b>chek rasmini</b> shu yerga yuboring. Men uni adminga yuboraman! 😊"
    )
    bot.send_message(message.chat.id, payment_msg, parse_mode="HTML")
    bot.register_next_step_handler(message, step5_check)

def step5_check(message):
    uid = message.chat.id
    if not message.photo:
        bot.send_message(uid, "⚠️ Iltimos, chekni rasm sifatida yuboring!")
        bot.register_next_step_handler(message, step5_check)
        return
    
    bot.send_message(uid, "⏳ <b>Katta rahmat!</b> Ma'lumotlar adminga yuborildi. Tez orada tasdiqlanadi. ✅", parse_mode="HTML")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"accept_{uid}"),
               types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{uid}"))
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"💰 <b>To'lov cheki!</b>\nKimdan: @{message.from_user.username}", parse_mode="HTML")
    bot.send_photo(ADMIN_ID, user_temp[uid]['photo'], 
                   caption=f"📋 <b>E'lon ma'lumotlari:</b>\n\nNarxi: {user_temp[uid]['price']}\nMa'lumot: {user_temp[uid]['desc']}", 
                   parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(("accept_", "reject_")))
def admin_control(call):
    action, uid = call.data.split("_")
    uid = int(uid)
    
    if action == "accept":
        d = user_temp.get(uid)
        if d:
            user_info = bot.get_chat(uid)
            contact = f"@{user_info.username}" if user_info.username else f"<a href='tg://user?id={uid}'>Sotuvchi bilan bog'lanish</a>"
            
            chan_caption = (
                f"🔥 <b>#SOTILADI #EFOOTBALL</b>\n\n"
                f"💰 <b>Narxi:</b> {d['price']}\n"
                f"📝 <b>Ma'lumot:</b> {d['desc']}\n"
                f"👤 <b>Murojaat:</b> {contact}\n\n"
                f"🤝 <b>Garant:</b> @kattabekov\n"
                f"📢 <b>Kanal:</b> {CHANNEL_ID}"
            )
            
            bot.send_photo(CHANNEL_ID, d['photo'], caption=chan_caption, parse_mode="HTML")
            
            if uid not in published_ads: published_ads[uid] = []
            published_ads[uid].append({'photo': d['photo'], 'caption': chan_caption, 'fast_count': 2})
            
            bot.send_message(uid, "🎉 <b>Tabriklaymiz!</b> E'loningiz kanalga joylandi!")
            bot.edit_message_caption("✅ Tasdiqlandi", call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(uid, "❌ Afsuski, e'loningiz rad etildi.")
        bot.edit_message_caption("❌ Rad etildi", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
