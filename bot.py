import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVER UCHUN ---
app = Flask('')
@app.route('/')
def home(): return "Bot uyg'oq va xatosiz!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- ASOSIY SOZLAMALAR ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822 
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)

# SHABLON RASM (Avvalgi botingizda ishlatilgan namuna rasm ID si yoki havolasi)
SHABLON_RASM = "https://t.me/kattabekov/2" # Shu yerga namunaviy rasm linkini qo'ydim

user_temp = {}
published_ads = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ E'lon berish", "📂 E'lonlarim", "👨‍💻 Adminlar", "📚 Qoidalar", "💰 E'lon narxlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        "Barcha xatoliklar tuzatildi. Endi bot yanada qulay! 😊", 
        reply_markup=main_menu(), 
        parse_mode="HTML"
    )

# --- E'LONLARIM VA FAST ---
@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads and published_ads[uid]:
        for idx, ad in enumerate(published_ads[uid]):
            markup = types.InlineKeyboardMarkup()
            btn_text = f"⚡️ FAST (Qolgan: {ad['fast_count']})"
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
        bot.answer_callback_query(call.id, f"🚀 E'lon kanalga qayta chiqdi! (Qoldi: {ad['fast_count']})", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ Imkoniyat tugagan!", show_alert=True)

# --- E'LON BERISH (NAMUNA RASM BILAN) ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def step1(message):
    try:
        # Namunaviy rasm yuborish
        bot.send_photo(
            message.chat.id, 
            SHABLON_RASM, 
            caption="📸 <b>Mana shunday namunadagi akkaunt rasmini yuboring:</b>", 
            parse_mode="HTML"
        )
    except:
        bot.send_message(message.chat.id, "📸 <b>Akkauntingiz rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step2)

def step2(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Iltimos, rasm yuboring!")
        bot.register_next_step_handler(message, step2)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Endi narxini yozing:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step3)

def step3(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Akkaunt haqida ma'lumot (Level, o'yinchilar):</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step4)

def step4(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    payment_msg = (
        "💳 <b>To'lov ma'lumotlari:</b>\n\n"
        "💳 <b>Karta:</b> <code>5440810304875684</code>\n"
        "👤 <b>Ega:</b> G A\n\n"
        "✅ To'lov chekini yuboring!"
    )
    bot.send_message(message.chat.id, payment_msg, parse_mode="HTML")
    bot.register_next_step_handler(message, step5_check)

def step5_check(message):
    uid = message.chat.id
    if not message.photo:
        bot.send_message(uid, "⚠️ Chekni rasm sifatida yuboring!")
        bot.register_next_step_handler(message, step5_check)
        return
    
    bot.send_message(uid, "⏳ <b>Adminga yuborildi...</b> ✅", parse_mode="HTML")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"accept_{uid}"),
               types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{uid}"))
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"💰 <b>To'lov cheki!</b>", parse_mode="HTML")
    bot.send_photo(ADMIN_ID, user_temp[uid]['photo'], 
                   caption=f"📋 <b>E'lon:</b>\n\nNarxi: {user_temp[uid]['price']}\nMa'lumot: {user_temp[uid]['desc']}", 
                   parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(("accept_", "reject_")))
def admin_control(call):
    action, uid = call.data.split("_")
    uid = int(uid)
    
    if action == "accept":
        d = user_temp.get(uid)
        if d:
            # USERNAME BO'LMASA, LINK YARATISH (TUZATILDI)
            user_info = bot.get_chat(uid)
            if user_info.username:
                contact = f"@{user_info.username}"
            else:
                contact = f"<a href='tg://user?id={uid}'>Sotuvchi bilan bog'lanish</a>"
            
            chan_caption = (
                f"🔥 <b>#SOTILADI #EFOOTBALL</b>\n\n"
                f"💰 <b>Narxi:</b> {d['price']}\n"
                f"📋 <b>Ma'lumot:</b> {d['desc']}\n"
                f"👤 <b>Murojaat:</b> {contact}\n\n"
                f"🤝 <b>Garant:</b> @kattabekov"
            )
            
            bot.send_photo(CHANNEL_ID, d['photo'], caption=chan_caption, parse_mode="HTML")
            
            if uid not in published_ads: published_ads[uid] = []
            published_ads[uid].append({'photo': d['photo'], 'caption': chan_caption, 'fast_count': 2})
            
            bot.send_message(uid, "🎉 E'loningiz kanalga chiqdi!")
            bot.edit_message_caption("✅ Tasdiqlandi", call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(uid, "❌ E'lon rad etildi.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
