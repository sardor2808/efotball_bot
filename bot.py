import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVER UCHUN (24/7) ---
app = Flask('')
@app.route('/')
def home(): return "Bot uyg'oq!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- ASOSIY SOZLAMALAR ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822 
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)

# Namunaviy rasm (Internetdan neytral rasm)
SHABLON_RASM = "https://img.freepik.com/free-vector/gaming-controller-concept-illustration_114360-3162.jpg"

user_temp = {}
published_ads = {} # E'lonlar va FAST imkoniyatlari

# --- ASOSIY MENYU ---
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
        "Botimizga xush kelibsiz. Bu yerda akkauntingizni tezkor sota olasiz. 😊\n"
        "Marhamat, kerakli bo'limni tanlang:", 
        reply_markup=main_menu(), 
        parse_mode="HTML"
    )

# --- BARCHA BO'LIMLAR ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules_info(message):
    bot.send_message(message.chat.id, 
        "📚 <b>Bot qoidalari:</b>\n\n"
        "1. Faqat real ma'lumotlar berilsin.\n"
        "2. To'lov cheki yuborilishi shart.\n"
        "3. Savdolar @kattabekov orqali amalga oshirilsin.", 
        parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admin_info(message):
    bot.send_message(message.chat.id, "👨‍💻 <b>Asosiy admin:</b> @kattabekov\nSavollar bo'lsa, bemalol yozing! 😊", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def price_info(message):
    bot.send_message(message.chat.id, 
        "💰 <b>Xizmat narxlari:</b>\n\n"
        "✨ Oddiy e'lon: 2 000 so'm\n"
        "⚡️ FAST imkoniyati: 2 marta (Bepul)\n\n"
        "To'lovni tasdiqlash uchun chek yuborish kerak.", 
        parse_mode="HTML")

# --- E'LONLARIM VA FAST (REPLY QILISH) ---
@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads and published_ads[uid]:
        bot.send_message(uid, "🗂 <b>Sizning faol e'lonlaringiz:</b>", parse_mode="HTML")
        for idx, ad in enumerate(published_ads[uid]):
            markup = types.InlineKeyboardMarkup()
            btn_text = f"⚡️ FAST (Imkoniyat: {ad['fast_count']})"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"fast_{uid}_{idx}"))
            bot.send_photo(uid, ad['photo'], caption=ad['caption'], reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(uid, "😕 <b>Sizda hali tasdiqlangan e'lonlar yo'q.</b>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fast_"))
def handle_fast_step1(call):
    _, uid, idx = call.data.split("_")
    uid, idx = int(uid), int(idx)
    ad = published_ads[uid][idx]
    
    if ad['fast_count'] > 0:
        msg = bot.send_message(call.message.chat.id, "🚀 <b>Yangi (Tezkor) narxni kiriting:</b>\n(Masalan: 50 000 so'm)", parse_mode="HTML")
        bot.register_next_step_handler(msg, handle_fast_final, uid, idx)
    else:
        bot.answer_callback_query(call.id, "❌ Imkoniyatlar tugagan!", show_alert=True)

def handle_fast_final(message, uid, idx):
    yangi_narx = message.text
    ad = published_ads[uid][idx]
    ad['fast_count'] -= 1
    
    # Kanaldagi e'longa REPLY qilish
    try:
        fast_text = f"⚡️ <b>#TEZKOR_SOTUV</b>\n\n💰 <b>Yangi narx:</b> {yangi_narx}\n🤝 Shoshiling, e'lon yangilandi!"
        bot.send_message(CHANNEL_ID, fast_text, reply_to_message_id=ad['message_id'], parse_mode="HTML")
        bot.send_message(uid, f"✅ E'loningiz kanalga REPLY qilindi! Qolgan FAST imkoniyati: {ad['fast_count']}")
    except Exception as e:
        bot.send_message(uid, "❌ Xatolik: Kanaldagi e'lon topilmadi yoki botda muammo.")

# --- E'LON BERISH ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def step1(message):
    bot.send_photo(message.chat.id, SHABLON_RASM, caption="📸 <b>Iltimos, akkaunt rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step2)

def step2(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Iltimos, rasm yuboring!")
        bot.register_next_step_handler(message, step2)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Akkaunt narxi:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step3)

def step3(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Batafsil ma'lumot (Level va h.k.):</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step4)

def step4(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    payment_msg = (
        "💳 <b>To'lov ma'lumotlari:</b>\n\n"
        "Narxi: 2 000 so'm\n"
        "Karta: <code>5440810304875684</code>\n"
        "Ega: <b>G A</b>\n\n"
        "✅ To'lov chekini (rasm) shu yerga yuboring!"
    )
    bot.send_message(message.chat.id, payment_msg, parse_mode="HTML")
    bot.register_next_step_handler(message, step5_check)

def step5_check(message):
    uid = message.chat.id
    if not message.photo:
        bot.send_message(uid, "⚠️ Iltimos, chekni rasm ko'rinishida yuboring!")
        bot.register_next_step_handler(message, step5_check)
        return
    
    bot.send_message(uid, "⏳ <b>Adminga yuborildi...</b> ✅", parse_mode="HTML")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"accept_{uid}"),
               types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{uid}"))
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption="💰 To'lov cheki")
    bot.send_photo(ADMIN_ID, user_temp[uid]['photo'], 
                   caption=f"📋 <b>E'lon:</b>\nNarxi: {user_temp[uid]['price']}\nMa'lumot: {user_temp[uid]['desc']}", 
                   parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(("accept_", "reject_")))
def admin_control(call):
    action, uid = call.data.split("_")
    uid = int(uid)
    
    if action == "accept":
        d = user_temp.get(uid)
        if d:
            user = bot.get_chat(uid)
            contact = f"@{user.username}" if user.username else f"<a href='tg://user?id={uid}'>Bog'lanish</a>"
            
            caption = (
                f"🔥 <b>#SOTILADI #EFOOTBALL</b>\n\n"
                f"💰 <b>Narxi:</b> {d['price']}\n"
                f"📝 <b>Ma'lumot:</b> {d['desc']}\n"
                f"👤 <b>Murojaat:</b> {contact}\n\n"
                f"🤝 <b>Garant:</b> @kattabekov"
            )
            
            # Kanalga chiqarish va ID sini saqlash
            sent_msg = bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
            
            if uid not in published_ads: published_ads[uid] = []
            published_ads[uid].append({
                'photo': d['photo'], 
                'caption': caption, 
                'fast_count': 2,
                'message_id': sent_msg.message_id # FAST uchun reply ID si
            })
            
            bot.send_message(uid, "🎉 E'loningiz kanalga chiqdi!")
            bot.edit_message_caption("✅ Tasdiqlandi", call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(uid, "❌ E'lon rad etildi.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
