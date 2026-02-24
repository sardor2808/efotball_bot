import telebot
from telebot import types
from flask import Flask
import threading
import os
import html
import re
import json
from PIL import Image, ImageDraw
import requests
from io import BytesIO

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot uyg'oq va o'ta hushmuomala! 😊"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- SOZLAMALAR ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
ADMIN_ID = 6286567822 
CHANNEL_ID = "@efotball_1v1"
bot = telebot.TeleBot(TOKEN)

SHABLON_RASM = "https://img.freepik.com/free-vector/gaming-controller-concept-illustration_114360-3162.jpg"
USER_DB = "users.json"

# --- BAZA FUNKSIYALARI ---
def save_user(user_id):
    users = get_users()
    if str(user_id) not in users:
        users.append(str(user_id))
        with open(USER_DB, "w") as f:
            json.dump(users, f)

def get_users():
    if not os.path.exists(USER_DB): return []
    with open(USER_DB, "r") as f: return json.load(f)

# --- YORDAMCHI FUNKSIYALAR ---
user_temp = {}
published_ads = {}
news_temp = {}

def clean_text(text):
    if not text: return ""
    text = re.sub(r'@\S+', '', text)
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text).strip()
    return text

def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ E'lon berish", "📂 E'lonlarim")
    markup.add("👨‍💻 Adminlar", "📚 Qoidalar")
    markup.add("💰 E'lon narxlari")
    if user_id == ADMIN_ID:
        markup.add("📊 Statistika", "📢 Reklama yuborish")
    return markup

# --- ASOSIY BUYRUQLAR ---
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)
    ism = message.from_user.first_name
    bot.send_message(
        message.chat.id, 
        f"🌟 <b>Assalomu alaykum, {ism} 🤍!</b>\n\n"
        f"Botimizga xush kelibsiz. Hozirda e'lon berish <b>vaqtinchalik BEPUL!</b> 😊\n"
        f"Marhamat, e'lon joylashtirishingiz yoki kerakli bo'limni tanlashingiz mumkin:", 
        reply_markup=main_menu(message.chat.id), 
        parse_mode="HTML"
    )

# --- ADMIN STATISTIKA VA REKLAMA ---
@bot.message_handler(func=lambda m: m.text == "📊 Statistika" and m.chat.id == ADMIN_ID)
def show_stats(message):
    users = get_users()
    bot.send_message(message.chat.id, f"📊 <b>Botimiz statistikasi:</b>\n\n👤 Foydalanuvchilar soni: <b>{len(users)} ta</b>\n🌟 Bot stabil holatda ishlamoqda!", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📢 Reklama yuborish" and m.chat.id == ADMIN_ID)
def start_broadcast(message):
    msg = bot.send_message(message.chat.id, "📢 <b>Barcha foydalanuvchilarga yuboriladigan xabar matnini kiriting:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    users = get_users()
    count = 0
    for user in users:
        try:
            bot.send_message(user, message.text, parse_mode="HTML")
            count += 1
        except: continue
    bot.send_message(ADMIN_ID, f"✅ Reklama <b>{count}</b> ta odamga muvaffaqiyatli yetib bordi!", parse_mode="HTML")

# --- ADMIN UCHUN YANGILIKLARNI TAHRIRLASH ---
@bot.message_handler(content_types=['photo'], func=lambda m: m.chat.id == ADMIN_ID)
def handle_news_photo(message):
    if message.chat.id not in user_temp:
        processing_msg = bot.send_message(message.chat.id, "🖌 <b>Begona reklamalar tozalanmoqda va rasm tayyorlanmoqda...</b>", parse_mode="HTML")
        file_info = bot.get_file(message.photo[-1].file_id)
        response = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        img = Image.open(BytesIO(response.content)).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        draw.text((width - 160, height - 40), "@efotball_1v1", fill=(255, 255, 255))
        bio = BytesIO(); bio.name = 'news.jpg'; img.save(bio, 'JPEG'); bio.seek(0)
        
        cleaned_caption = clean_text(message.caption if message.caption else "")
        full_caption = (
            f"{cleaned_caption}\n\n"
            f"📍 <b>Sahifamiz:</b> @efotball_1v1 ✔️\n"
            f"🤝 <b>Garant:</b> @kattabekov\n"
            f"🚀 <b>Bot:</b> @efotball1v1_bot"
        )
        news_temp[message.chat.id] = {'photo': bio.getvalue(), 'caption': full_caption}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚀 Kanalga yuborish", callback_data="send_news"),
                   types.InlineKeyboardButton("📝 Matnni tahrirlash", callback_data="edit_news_text"),
                   types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_news"))
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.send_photo(message.chat.id, bio.getvalue(), caption=f"✨ <b>Tayyor ko'rinish (Tasdiqlaysizmi?):</b>\n\n{full_caption}", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["send_news", "cancel_news", "edit_news_text"])
def callback_news(call):
    if call.data == "send_news":
        data = news_temp.get(call.message.chat.id)
        if data:
            bot.send_photo(CHANNEL_ID, data['photo'], caption=data['caption'], parse_mode="HTML")
            bot.answer_callback_query(call.id, "✅ Kanalga yuborildi!", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "edit_news_text":
        msg = bot.send_message(call.message.chat.id, "📝 <b>Yangi matnni yuboring (Eski matn butunlay o'chadi):</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_new_news_text)
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "❌ Amalyot bekor qilindi.")

def process_new_news_text(message):
    uid = message.chat.id
    if uid in news_temp:
        news_temp[uid]['caption'] = message.text
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚀 Kanalga yuborish", callback_data="send_news"),
                   types.InlineKeyboardButton("📝 Qayta tahrirlash", callback_data="edit_news_text"),
                   types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_news"))
        bot.send_photo(uid, news_temp[uid]['photo'], caption=f"✅ <b>Matn yangilandi:</b>\n\n{message.text}", parse_mode="HTML", reply_markup=markup)

# --- BO'LIMLAR MATNLARI ---
@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules(message):
    text = "📚 <b>Garant: @kattabekov</b>\n\nBotdan foydalanish orqali siz barcha xavfsizlik qoidalariga rozilik bildirasiz. Akkauntlarni faqat ishonchli adminlar orqali soting! 🛡"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admins(message):
    bot.send_message(message.chat.id, "👨‍💻 <b>Adminimiz:</b> @kattabekov\nSavollar yoki takliflar bo'lsa, bemalol murojaat qiling! 😊", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def prices(message):
    bot.send_message(message.chat.id, "💰 <b>Hozircha BEPUL!</b>\n\nFursatdan foydalanib, o'z akkauntingizni tezroq sotib oling! ✨", parse_mode="HTML")

# --- E'LON BERISH JARAYONI ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def step1(message):
    bot.send_photo(message.chat.id, SHABLON_RASM, caption="📸 <b>Iltimos, akkaunt rasmini yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step2)

def step2(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Rasm yuborishingiz shart!"); bot.register_next_step_handler(message, step2); return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Akkaunt narxini kiriting:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step3)

def step3(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Akkaunt haqida batafsil ma'lumot bering:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step4)

def step4(message):
    uid = message.chat.id
    user_temp[uid]['desc'] = html.escape(message.text)
    user = bot.get_chat(uid); contact = f"@{user.username}" if user.username else f"ID: {uid}"
    d = user_temp[uid]
    caption = f"🔥 <b>#SOTILADI #EFOOTBALL</b>\n\n💰 <b>Narxi:</b> {d['price']}\n📝 <b>Ma'lumot:</b> {d['desc']}\n👤 <b>Murojaat:</b> {contact}\n🤝 <b>Garant:</b> @kattabekov"
    sent_msg = bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    if uid not in published_ads: published_ads[uid] = []
    published_ads[uid].append({'photo': d['photo'], 'caption': caption, 'fast_count': 2, 'message_id': sent_msg.message_id})
    bot.send_message(uid, "🎉 <b>Tabriklaymiz!</b> E'loningiz kanalga muvaffaqiyatli joylandi. ✅", reply_markup=main_menu(uid), parse_mode="HTML")
    del user_temp[uid]

@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads and published_ads[uid]:
        bot.send_message(uid, "📂 <b>Sizning e'lonlaringiz:</b>", parse_mode="HTML")
        for idx, ad in enumerate(published_ads[uid]):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"⚡️ FAST ({ad['fast_count']})", callback_data=f"fast_{uid}_{idx}"))
            bot.send_photo(uid, ad['photo'], caption=ad['caption'], reply_markup=markup, parse_mode="HTML")
    else: bot.send_message(uid, "😕 <b>E'lonlaringiz mavjud emas.</b>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fast_"))
def handle_fast_start(call):
    _, uid, idx = call.data.split("_")
    uid, idx = int(uid), int(idx)
    if published_ads[uid][idx]['fast_count'] > 0:
        msg = bot.send_message(call.message.chat.id, "🚀 <b>Yangi narxni yuboring:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, handle_fast_finish, uid, idx)
    else: bot.answer_callback_query(call.id, "❌ FAST imkoniyati tugagan!", show_alert=True)

def handle_fast_finish(message, uid, idx):
    yangi_narx = message.text; ad = published_ads[uid][idx]; ad['fast_count'] -= 1
    bot.send_message(CHANNEL_ID, f"⚡️ <b>#TEZKOR_SOTUV</b>\n\n💰 <b>Yangi narx:</b> {yangi_narx}", reply_to_message_id=ad['message_id'], parse_mode="HTML")
    bot.send_message(uid, f"✅ FAST bajarildi! Qolgan imkoniyat: {ad['fast_count']}", parse_mode="HTML")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
                   
