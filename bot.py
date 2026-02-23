import telebot
from telebot import types
from flask import Flask
import threading
import os
import html

# --- SERVER UCHUN (Render uyg'oq turishi uchun) ---
app = Flask('')
@app.route('/')
def home(): return "Bot 24/7 rejimida!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- ASOSIY SOZLAMALAR ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822  # Sizning ID
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)

user_temp = {}
published_ads = {} # Foydalanuvchi e'lonlari va FAST imkoniyatlari

# --- TUGMALAR ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ E'lon berish", "📂 E'lonlarim", "👨‍💻 Adminlar", "📚 Qoidalar", "💰 E'lon narxlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        "E'lon berish botimizga xush kelibsiz! 😊\n"
        "Bu yerda hamma narsa avvalgidek — qulay va tezkor.\n\n"
        "👇 Kerakli bo'limni tanlang:", 
        reply_markup=main_menu(), 
        parse_mode="HTML"
    )

# --- QOIDALAR ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules(message):
    bot.send_message(message.chat.id, 
        "📚 <b>Botdan foydalanish qoidalari:</b>\n\n"
        "1️⃣ Faqat real akkauntlar e'lon qilinishi shart.\n"
        "2️⃣ Yolg'on ma'lumot berish qat'iyan taqiqlanadi.\n"
        "3️⃣ To'lov qilingandan so'ng e'lon adminga boradi.\n"
        "4️⃣ Savdolarni faqat @kattabekov (Garant) orqali qiling.",
        parse_mode="HTML")

# --- E'LON NARXLARI ---
@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def price_info(message):
    bot.send_message(message.chat.id, 
        "💳 <b>E'lon berish narxi:</b>\n\n"
        "Bir martalik e'lon — <b>2 000 so'm</b>.\n\n"
        "To'lovni amalga oshirgach, e'loningiz tekshirilib kanalga chiqariladi. ✅", 
        parse_mode="HTML")

# --- ADMINLAR ---
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admin_info(message):
    bot.send_message(message.chat.id, "👨‍💻 <b>Asosiy admin:</b> @kattabekov\n\nHar qanday muammo bo'yicha murojaat qilishingiz mumkin! 😊", parse_mode="HTML")

# --- E'LONLARIM VA FAST TIZIMI ---
@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads and published_ads[uid]:
        for idx, ad in enumerate(published_ads[uid]):
            markup = types.InlineKeyboardMarkup()
            # Har bir e'lon uchun 2 marta FAST imkoniyati
            btn_text = f"⚡️ FAST (Qolgan imkoniyat: {ad['fast_count']})"
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
        # Kanalga "FAST" belgisi bilan qayta chiqarish yoki xabar berish
        bot.send_message(CHANNEL_ID, f"⚡️ <b>TEZKOR SOTUV!</b>\n\n{ad['caption']}", parse_mode="HTML")
        bot.answer_callback_query(call.id, f"🚀 E'lon kanalga TEZKOR qilib qayta yuborildi! (Qoldi: {ad['fast_count']})", show_alert=True)
        # Tugmani yangilash uchun "E'lonlarim"ni qayta ko'rsatishni tavsiya qilamiz
    else:
        bot.answer_callback_query(call.id, "❌ Bu e'lon uchun FAST imkoniyatlari tugagan!", show_alert=True)

# --- E'LON BERISH JARAYONI ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def step1(message):
    bot.send_message(message.chat.id, "📸 <b>Ajoyib! Avvalo akkauntingiz rasmini yuboring:</b>", parse_mode="HTML")
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
    bot.send_message(message.chat.id, "📝 <b>Akkaunt haqida batafsil ma'lumot bering:</b>\n(Level, o'yinchilar va h.k.)", parse_mode="HTML")
    bot.register_next_step_handler(message, step4)

def step4(message):
    user_temp[message.chat.id]['desc'] = html.escape(message.text)
    # KARTA MA'LUMOTI (TO'G'RI KARTA)
    payment_msg = (
        "💳 <b>To'lov ma'lumotlari:</b>\n\n"
        "E'lonni chiqarish uchun to'lov qiling:\n"
        "💰 <b>Narxi:</b> 2 000 so'm\n"
        "💳 <b>Karta:</b> <code>5440810304875684</code>\n"
        "👤 <b>Ega:</b> G A\n\n"
        "✅ To'lovni qilgach, <b>to'lov chekini (rasmini)</b> shu yerga yuboring. Adminga tasdiqlash uchun yuboraman! 😊"
    )
    bot.send_message(message.chat.id, payment_msg, parse_mode="HTML")
    bot.register_next_step_handler(message, step5_check)

def step5_check(message):
    uid = message.chat.id
    if not message.photo:
        bot.send_message(uid, "⚠️ Iltimos, chekni rasm sifatida yuboring!")
        bot.register_next_step_handler(message, step5_check)
        return
    
    bot.send_message(uid, "⏳ <b>Rahmat!</b> Chek va ma'lumotlar adminga yuborildi. Tasdiqlanishini kuting... ✅", parse_mode="HTML")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"accept_{uid}"),
               types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{uid}"))
    
    # Adminga chek va e'lonni yuborish
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"💰 <b>Yangi to'lov cheki!</b>\nKimdan: @{message.from_user.username}", parse_mode="HTML")
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
            user = bot.get_chat(uid)
            contact = f"@{user.username}" if user.username else f"ID: {uid}"
            
            chan_caption = (
                f"🔥 <b>#SOTILADI #EFOOTBALL</b>\n\n"
                f"💰 <b>Narxi:</b> {d['price']}\n"
                f"📋 <b>Ma'lumot:</b> {d['desc']}\n"
                f"👤 <b>Murojaat:</b> {contact}\n\n"
                f"🤝 <b>Garant:</b> @kattabekov\n"
                f"📢 <b>Kanal:</b> {CHANNEL_ID}"
            )
            
            bot.send_photo(CHANNEL_ID, d['photo'], caption=chan_caption, parse_mode="HTML")
            
            # E'lonlarimga saqlash va 2 ta FAST imkoniyati berish
            if uid not in published_ads: published_ads[uid] = []
            published_ads[uid].append({
                'photo': d['photo'], 
                'caption': chan_caption,
                'fast_count': 2
            })
            
            bot.send_message(uid, "🎉 <b>Xushxabar!</b> E'loningiz kanalga joylandi! 'E'lonlarim' bo'limidan FAST xizmatini ishlatishingiz mumkin.")
            bot.edit_message_caption("✅ Tasdiqlandi", call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(uid, "❌ <b>Afsuski, e'loningiz tasdiqlanmadi.</b>")
        bot.edit_message_caption("❌ Rad etildi", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
                                  
