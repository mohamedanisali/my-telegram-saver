import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events

# --- إعدادات الحساب (تأكد من وضع بياناتك الصحيحة هنا) ---
API_ID = 1234567  # استبدله بـ ID حسابك
API_HASH = 'your_api_hash'  # استبدله بـ Hash حسابك
BOT_TOKEN = 'your_bot_token'  # استبدله بتوكن البوت

# --- إعداد تطبيق ويب بسيط (لإبقاء السيرفر "Healthy") ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت شغال ومستقر بنسبة 100%!"

# --- إعداد عملاء التيليجرام (البوت والحساب الشخصي) ---
bot = TelegramClient('bot_session', API_ID, API_HASH)
user = TelegramClient('user_session', API_ID, API_HASH)

# دالة ذكية لتحديث النسبة المئوية للتحميل والرفع
async def progress_callback(current, total, event, action_verb):
    percentage = (current / total) * 100
    # تحديث الرسالة كل 10% لتجنب حظر التيليجرام (Flood)
    if int(percentage) % 10 == 0:
        try:
            await event.edit(f'⏳ جاري {action_verb}: {percentage:.1f}%...')
        except:
            pass

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('🚀 أهلاً بك! أرسل لي رابط الفيديو من القناة المقيدة (التي تشترك بها) وسأقوم بسحبه فوراً.')

@bot.on(events.NewMessage)
async def handler(event):
    if 't.me/' in event.text:
        link = event.text.strip()
        status_msg = await event.respond('⏳ جاري محاولة الوصول للمحتوى وفحصه...')
        
        try:
            # السحر هنا: استخدام الرابط مباشرة لجلب الرسالة وحل مشكلة الـ Entity
            msg = await user.get_messages(link)
            
            if msg and msg.media:
                await status_msg.edit('📂 تم العثور على الميديا.. جاري البدء!')
                
                # 1. التحميل من القناة المصدر إلى السيرفر
                path = await user.download_media(
                    msg.media, 
                    progress_callback=lambda c, t: progress_callback(c, t, status_msg, "التحميل من المصدر")
                )
                
                await status_msg.edit('📤 جاري الرفع إليك الآن (ثواني معدودة)...')
                
                # 2. الرفع من السيرفر إليك عبر البوت
                await bot.send_file(
                    event.chat_id, 
                    path, 
                    caption="✅ تم السحب بنجاح بواسطة بوتك الخاص!",
                    progress_callback=lambda c, t: progress_callback(c, t, status_msg, "الرفع لتيليجرام")
                )
                
                # مسح الملف من السيرفر فوراً لتوفير المساحة
                if os.path.exists(path):
                    os.remove(path)
                
                await status_msg.delete()
            else:
                await status_msg.edit('❌ الرابط لا يحتوي على ميديا أو الحساب ليس عضواً في القناة.')
                
        except Exception as e:
            # عرض الخطأ لو حدث (مثل الحظر أو عدم الوصول)
            await status_msg.edit(f'❌ حصلت مشكلة: {str(e)}')

async def main():
    print("🔗 جاري تشغيل المحركات والاتصال بتيليجرام...")
    await bot.start(bot_token=BOT_TOKEN)
    await user.start()
    print("✅ البوت الآن في وضع الطيران المستقر!")
    await bot.run_until_disconnected()

# --- تشغيل السيرفر (Flask) والبوت معاً بطريقة متوازية ---
if __name__ == "__main__":
    # تشغيل Flask على البورت المتاح (لحل مشكلة Health Check)
    port = int(os.environ.get("PORT", 8080))
    
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, use_reloader=False)).start()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
