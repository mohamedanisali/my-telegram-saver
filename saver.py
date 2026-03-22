from telethon import TelegramClient, events
import os
import asyncio
from flask import Flask
from threading import Thread

# --- إعدادات البوابة الوهمية لـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "البوت شغال زي الفل!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- بياناتك (محفوظة زي ما هي) ---
API_ID = 35688859
API_HASH = 'f5d5a60d655bce7925675c711731ca1b'
BOT_TOKEN = '8697118092:AAEHucNVoixdd3FK-vF7qCYxHzJkpz5zYh8'
OWNER_ID = 5344366814
# ---------------------------------------

async def main():
    bot = TelegramClient('bot_session', API_ID, API_HASH)
    user = TelegramClient('user_session', API_ID, API_HASH)

    print("🔗 جاري الاتصال بخوادم تيليجرام...")
    await bot.start(bot_token=BOT_TOKEN)
    await user.start()
    
    print("✅ البوت شغال الآن على السيرفر!")

    @bot.on(events.NewMessage(pattern='/start'))
    async def start(event):
        if event.sender_id == OWNER_ID:
            await event.reply("أهلاً بك يا ريس! ابعت الرابط وأنا هسحبهولك.")

    @bot.on(events.NewMessage(pattern=r'https?://t\.me/'))
    async def downloader(event):
        if event.sender_id != OWNER_ID: return
        url = event.text.strip()
        status = await event.reply("⏳ جاري السحب من السيرفر...")
        try:
            parts = url.split('/')
            msg_id = int(parts[-1])
            peer = int('-100' + parts[-2]) if '/c/' in url else parts[-2]
            msg = await user.get_messages(peer, ids=msg_id)
            if msg and msg.media:
                path = await user.download_media(msg)
                await bot.send_file(event.chat_id, path, caption=msg.text)
                if os.path.exists(path): os.remove(path)
                await status.delete()
            else:
                await status.edit("❌ مفيش ميديا هنا.")
        except Exception as e:
            await status.edit(f"⚠️ خطأ: {str(e)}")

    await bot.run_until_disconnected()

if __name__ == '__main__':
    keep_alive() # تشغيل البوابة الوهمية
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
