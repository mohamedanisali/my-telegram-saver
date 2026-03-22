import os
import asyncio
import threading
import re
from flask import Flask
from telethon import TelegramClient, events

# --- إعدادات الحساب (تأكد من وضع بياناتك الصحيحة) ---
API_ID = 1234567  # استبدله بـ ID حسابك
API_HASH = 'your_api_hash'  # استبدله بـ Hash حسابك
BOT_TOKEN = 'your_bot_token'  # استبدله بتوكن البوت

# --- إعداد تطبيق ويب (لإبقاء السيرفر Healthy) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت يعمل بنجاح ومستعد لسحب الروابط الخاصة!"

# --- إعداد عملاء التيليجرام ---
bot = TelegramClient('bot_session', API_ID, API_HASH)
user = TelegramClient('user_session', API_ID, API_HASH)

# دالة تحديث النسبة المئوية
async def progress_callback(current, total, event, action_verb):
    percentage = (current / total) * 100
    if int(percentage) % 10 == 0:
        try:
            await event.edit(f'⏳ جاري {action_verb}: {percentage:.1f}%...')
        except:
            pass

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('🚀 أهلاً بك! أرسل لي رابط الفيديو (عام أو خاص بجهازك) وسأقوم بسحبه فوراً.')

@bot.on(events.NewMessage)
async def handler(event):
    link = event.text.strip()
    if 't.me/' not in link:
        return

    status_msg = await event.respond('⏳ جاري فحص الرابط ومعالجة التشفير...')
    
    try:
        msg = None
        # حالة الروابط الخاصة (t.me/c/12345/67)
        if '/c/' in link:
            parts = link.split('/')
            # استخراج رقم القناة وإضافة بادئة -100 المشهورة في تليجرام
            raw_channel_id = parts[parts.index('c') + 1]
            channel_id = int("-100" + raw_channel_id)
            msg_id = int(parts[-1])
            
            # محاولة جلب الرسالة باستخدام المعرف الرقمي الصريح
            msg = await user.get_messages(channel_id, ids=msg_id)
        else:
            # حالة الروابط العامة (t.me/channel/123)
            msg = await user.get_messages(link)

        if msg and msg.media:
            await status_msg.edit('📂 تم العثور على الميديا.. جاري التحميل...')
            
            # التحميل من المصدر
            path = await user.download_media(
                msg.media, 
                progress_callback=lambda c, t: progress_callback(c, t, status_msg, "التحميل")
            )
            
            await status_msg.edit('📤 جاري الرفع إليك الآن...')
            
            # الرفع للمستخدم
            await bot.send_file(
                event.chat_id, 
                path, 
                caption="✅ تم السحب بنجاح!",
                progress_callback=lambda c, t: progress_callback(c, t, status_msg, "الرفع")
            )
            
            if os.path.exists(path):
                os.remove(path)
            await status_msg.delete()
        else:
            await status_msg.edit('❌ لم يتم العثور على ميديا. تأكد أن الحساب الشخصي مشترك في القناة.')

    except Exception as e:
        await status_msg.edit(f'❌ حصلت مشكلة: {str(e)}\n\n💡 نصيحة: ادخل القناة من موبايلك وشغل الفيديو ثانية واحدة ثم جرب مجدداً.')

async def main():
    print("🔗 جاري الاتصال...")
    await bot.start(bot_token=BOT_TOKEN)
    await user.start()
    print("✅ البوت جاهز تماماً!")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, use_reloader=False)).start()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
