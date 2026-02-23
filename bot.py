import telebot
from telebot import types
from flask import Flask
import threading
import html
import os

# --- SERVER QISMI (Render o'chirmasligi uchun) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- BOT QISMI ---
TOKEN = "7887838088:AAExTVAoTCJp0THpdug06E0sP-7TAo0n7mM"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Assalomu alaykum! Men serverda ishlayapman.")

# Botni ishga tushirish
if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
  
