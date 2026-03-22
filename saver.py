import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events

# --- إعدادات الحساب (تأكد من بياناتك) ---
API_ID = 1234567  # رقم الـ ID
API_HASH = 'your_api_hash'  # الـ Hash
BOT_TOKEN = 'your_bot_token'  # توكن البوت

# --- إعداد تطبيق ويب (لإبقاء السيرفر صاحي) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت شغال ومستقر بنسبة 100%!"

# --- إعداد عملاء التيليجرام ---
bot = TelegramClient('bot_session', API_ID, API_HASH)
user = TelegramClient('user_session', API_ID, API_HASH)

# دالة لحساب النسبة المئوية للتحميل والرفع
async def progress_callback(current, total, event, action_verb):
    percentage = (current / total) * 100
    if int(percentage) % 10 == 0:  # يحدث الرسالة كل 10% عشان ميعملش سبام
        try:
            await event.edit(f'⏳ جاري {action_verb}: {percentage:.1f}%...')
        except:
            pass

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('🚀 يا هلا! ابعت لي رابط فيديو من قناة مقيدة وهسحبهولك بالثانية.')

@bot.on(events.NewMessage)
async def handler(event):
    if 't.me/' in event.text:
        link = event.text
        status_msg = await event.respond('⏳ جاري فحص الرابط...')
        
        try:
            parts = link.split('/')
            channel_username = parts[-2]
            msg_id = int(parts[-1])
            
            msg = await user.get_messages(channel_username, ids=msg_id)
            
            if msg and msg.media:
                await status_msg.edit('📂 تم العثور على الميديا.. بجهز المحرك!')
                
                # التحميل مع إظهار النسبة المئوية
                path = await user.download_media(
                    msg.media, 
                    progress_callback=lambda c, t: progress_callback(c, t, status_msg, "التحميل من المصدر")
                )
                
                await status_msg.edit('📤 جاري الرفع إليك الآن (ثواني معدودة)...')
                
                # الرفع مع إظهار النسبة المئوية
                await bot.send_file(
                    event.chat_id, 
                    path, 
                    caption="✅ تم السحب بنجاح!",
                    progress_callback=lambda c, t: progress_callback(c, t, status_msg, "الرفع لتيليجرام")
                )
                
                if os.path.exists(path):
                    os.remove(path)
                
                await status_msg.delete()
            else:
                await status_msg.edit('❌ الرابط ده مفيش فيه فيديو أو صورة.')
                
        except Exception as e:
            await status_msg.edit(f'❌ حصلت مشكلة: {str(e)}')

async def main():
    print("🔗 جاري تشغيل المحركات...")
    await bot.start(bot_token=BOT_TOKEN)
    await user.start()
    print("✅ البوت الآن في وضع الطيران المستقر!")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, use_reloader=False)).start()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
