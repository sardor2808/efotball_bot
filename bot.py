import telebot
from telebot import types
from flask import Flask
import threading
import os
import html
import re  # Linklarni tozalash uchun
from PIL import Image, ImageDraw
import requests
from io import BytesIO

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot uyg'oq!"
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

user_temp = {}
published_ads = {}
news_temp = {}

# --- MATNNI TOZALASH FUNKSIYASI ---
def clean_text(text):
    if not text: return ""
    # @username larni o'chirish
    text = re.sub(r'@\S+', '', text)
    # t.me linklarini o'chirish
    text = re.sub(r'https?://t\.me/\S+', '', text)
    # Ortiqcha bo'shliqlarni tozalash
    text = re.sub(r'\n\s*\n', '\n\n', text).strip()
    return text

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ E'lon berish", "📂 E'lonlarim", "👨‍💻 Adminlar", "📚 Qoidalar", "💰 E'lon narxlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌟 Bot faol!", reply_markup=main_menu(), parse_mode="HTML")

# --- ADMIN UCHUN YANGILIK TAHRIRLASH ---
@bot.message_handler(content_types=['photo'], func=lambda m: m.chat.id == ADMIN_ID)
def handle_news_photo(message):
    if message.chat.id not in user_temp:
        processing_msg = bot.send_message(message.chat.id, "🖌 <b>Begona linklar tozalanmoqda va rasm tayyorlanmoqda...</b>", parse_mode="HTML")
        
        # Rasmni yuklab olish va watermark
        file_info = bot.get_file(message.photo[-1].file_id)
        response = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        img = Image.open(BytesIO(response.content)).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        draw.text((width - 160, height - 40), "@efotball_1v1", fill=(255, 255, 255))
        
        bio = BytesIO()
        bio.name = 'news.jpg'
        img.save(bio, 'JPEG')
        bio.seek(0)
        
        # MATNNI TOZALASH QISMI
        original_caption = message.caption if message.caption else ""
        cleaned_caption = clean_text(original_caption)
        
        full_caption = (
            f"{cleaned_caption}\n\n"
            f"Rasmiy sahifamiz: @efotball_1v1✔️\n\n"
            f"♻️ OLDI SOTDI GARANT\n"
            f"ADMINLAR\n"
            f"▪️ @kattabekov\n\n"
            f"🔻 ELON BERISH UCHUN BOTIMIZ\n"
            f"@efotball1v1_bot"
        )
        
        news_temp[message.chat.id] = {'photo': bio.getvalue(), 'caption': full_caption}
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚀 Kanalga yuborish", callback_data="send_news"),
                   types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_news"))
        
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.send_photo(message.chat.id, bio.getvalue(), caption=f"<b>Tayyor variant (Linklar tozalandi):</b>\n\n{full_caption}", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["send_news", "cancel_news"])
def callback_news(call):
    if call.data == "send_news":
        data = news_temp.get(call.message.chat.id)
        if data:
            bot.send_photo(CHANNEL_ID, data['photo'], caption=data['caption'], parse_mode="HTML")
            bot.answer_callback_query(call.id, "✅ Kanalga chiqdi!", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)

# --- E'LON BERISH VA BOSHQA FUNKSIYALAR ---
@bot.message_handler(func=lambda m: m.text == "➕ E'lon berish")
def step1(message):
    bot.send_photo(message.chat.id, SHABLON_RASM, caption="📸 <b>Rasm yuboring:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step2)

def step2(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⚠️ Rasm yuboring!")
        bot.register_next_step_handler(message, step2)
        return
    user_temp[message.chat.id] = {'photo': message.photo[-1].file_id}
    bot.send_message(message.chat.id, "💰 <b>Narxi:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step3)

def step3(message):
    user_temp[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📝 <b>Ma'lumot:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, step4)

def step4(message):
    uid = message.chat.id
    user_temp[uid]['desc'] = html.escape(message.text)
    user = bot.get_chat(uid)
    contact = f"@{user.username}" if user.username else f"<a href='tg://user?id={uid}'>Bog'lanish</a>"
    d = user_temp[uid]
    caption = f"🔥 <b>#SOTILADI</b>\n\n💰 <b>Narxi:</b> {d['price']}\n📝 <b>Ma'lumot:</b> {d['desc']}\n👤 <b>Murojaat:</b> {contact}\n\n🤝 <b>Garant:</b> @kattabekov"
    sent_msg = bot.send_photo(CHANNEL_ID, d['photo'], caption=caption, parse_mode="HTML")
    if uid not in published_ads: published_ads[uid] = []
    published_ads[uid].append({'photo': d['photo'], 'caption': caption, 'fast_count': 2, 'message_id': sent_msg.message_id})
    bot.send_message(uid, "✅ E'lon joylandi!", reply_markup=main_menu())
    del user_temp[uid]

@bot.message_handler(func=lambda m: m.text == "📂 E'lonlarim")
def my_ads(message):
    uid = message.chat.id
    if uid in published_ads and published_ads[uid]:
        for idx, ad in enumerate(published_ads[uid]):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"⚡️ FAST ({ad['fast_count']})", callback_data=f"fast_{uid}_{idx}"))
            bot.send_photo(uid, ad['photo'], caption=ad['caption'], reply_markup=markup, parse_mode="HTML")
    else: bot.send_message(uid, "😕 E'lonlar yo'q.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fast_"))
def handle_fast_start(call):
    _, uid, idx = call.data.split("_")
    uid, idx = int(uid), int(idx)
    if published_ads[uid][idx]['fast_count'] > 0:
        msg = bot.send_message(call.message.chat.id, "🚀 <b>Yangi narx:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, handle_fast_finish, uid, idx)
    else: bot.answer_callback_query(call.id, "❌ Tugadi!", show_alert=True)

def handle_fast_finish(message, uid, idx):
    yangi_narx = message.text
    ad = published_ads[uid][idx]
    ad['fast_count'] -= 1
    bot.send_message(CHANNEL_ID, f"⚡️ <b>#TEZKOR_SOTUV</b>\n\n💰 <b>Yangi narx:</b> {yangi_narx}", reply_to_message_id=ad['message_id'], parse_mode="HTML")
    bot.send_message(uid, "✅ FAST bajarildi!")

@bot.message_handler(func=lambda m: m.text == "📚 Qoidalar")
def rules(message): bot.send_message(message.chat.id, "📚 Garant: @kattabekov")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Adminlar")
def admins(message): bot.send_message(message.chat.id, "👨‍💻 @kattabekov")

@bot.message_handler(func=lambda m: m.text == "💰 E'lon narxlari")
def prices(message): bot.send_message(message.chat.id, "💰 Hozircha BEPUL!")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
