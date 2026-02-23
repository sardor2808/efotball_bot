import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVER UCHUN (24/7) ---
app = Flask('')
@app.route('/')
def home(): return "Bot uyg'oq va bepul rejimda!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- ASOSIY SOZLAMALAR ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822 
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)

# Namunaviy rasm
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
    bot.send_message(
        message.chat.id, 
        f"🌟 <b>Assalomu alaykum, {ism}!</b>\n\n"
        "Botimizga xush kelibsiz. Hozirda e'lon berish <b>vaqtinchalik BEPUL!</b> 😊\n"
        "Marhamat, e'lon joylashtirishingiz mumkin:", 
        reply_markup=main_menu(), 
        parse_mode="HTML"
    )

# --- BARCHA BO'LIMLAR ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules_info(message):
    bot.send_message(message.chat.id, "📚 <b>Qoidalar:</b>\n\n1. Faqat real e'lonlar.\n2. Savdolar @kattabekov orqali.", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admin_info(message):
    bot.send_message(message.chat.id, "👨‍💻 Admin: @kattabekov", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def price_info(message):
    bot.send_message(message.chat.id, "💰 <b>Aksiya!</b>\n\nHozirda e'lon berish mutlaqo <b>BEPUL!</b> ✨", parse_mode="HTML")

# --- E'LONLARIM VA FAST (REPLY) ---
@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads and published_ads[uid]:
        for idx, ad in enumerate(published_ads[uid]):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"⚡️ FAST ({ad['fast_count']})", callback_data=f"fast_{uid}_{idx}"))
            bot.send_photo(uid, ad['photo'], caption=ad['caption'], reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(uid, "😕 Sizda faol e'lonlar yo'q.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fast_"))
def handle_fast_step1(call):
    _, uid, idx = call.data.split("_")
    uid, idx = int(uid), int(idx)
    if published_ads[uid][idx]['fast_count'] > 0:
        msg = bot.send_message(call.message.chat.id, "🚀 <b>Yangi narxni yozing:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, handle_fast_final, uid, idx)
    else:
        bot.answer_callback_query(call.id, "❌ Imkoniyat tugadi!", show_alert=True)

def handle_fast_final(message, uid, idx):
    yangi_narx = message.text
    ad = published_ads[uid][idx]
    ad['fast_count'] -= 1
    try:
        fast_text = f"⚡️ <b>#TEZKOR_SOTUV</b>\n\n💰 <b>Yangi narx:</b> {yangi_narx}"
        bot.send_message(CHANNEL_ID, fast_text, reply_to_message_id=ad['message_id'], parse_mode="HTML")
        bot.send_message(uid, "✅ FAST bajarildi!")
    except:
        bot.send_message(uid, "❌ Xatolik yuz berdi.")

# --- BEPUL E'LON BERISH JARAYONI ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def step1(message):
    bot.send_photo(message.chat.id, SHABLON_RASM, caption="📸 <b>Akkaunt rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step2)

def step2(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Rasm yuboring!")
        bot.register_next_step_handler(message, step2)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Narxini yozing:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step3)

def step3(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Batafsil ma'lumot:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step4)

def step4(message):
    uid = message.chat.id
    user_temp[uid]['desc'] = html.escape(message.text)
    
    # Kanalga to'g'ridan-to'g'ri chiqarish
    user = bot.get_chat(uid)
    contact = f"@{user.username}" if user.username else f"<a href='tg://user?id={uid}'>Bog'lanish</a>"
    d = user_temp[uid]
    
    caption = (
        f"🔥 <b>#SOTILADI #EFOOTBALL</b>\n\n"
        f"💰 <b>Narxi:</b> {d['price']}\n"
        f"📝 <b>Ma'lumot:</b> {d['desc']}\n"
        f"👤 <b>Murojaat:</b> {contact}\n\n"
        f"🤝 <b>Garant:</b> @kattabekov"
    )
    
    sent_msg = bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    
    # E'lonlarimga saqlash
    if uid not in published_ads: published_ads[uid] = []
    published_ads[uid].append({
        'photo': d['photo'], 
        'caption': caption, 
        'fast_count': 2,
        'message_id': sent_msg.message_id
    })
    
    bot.send_message(uid, "🎉 <b>Tabriklaymiz!</b>\nE'loningiz <b>bepul aksiya</b> doirasida kanalga joylandi! ✅", parse_mode="HTML")
    
    # Adminga shunchaki xabar berish (nazorat uchun)
    bot.send_message(ADMIN_ID, f"📢 Yangi bepul e'lon joylandi!\nKimdan: {contact}")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
