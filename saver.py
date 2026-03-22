from telethon import TelegramClient, events
import os
import asyncio

# --- البيانات الخاصة بك (جاهزة للعمل) ---
API_ID = 35688859
API_HASH = 'f5d5a60d655bce7925675c711731ca1b'
BOT_TOKEN = '8697118092:AAEHucNVoixdd3FK-vF7qCYxHzJkpz5zYh8'
OWNER_ID = 5344366814
# ---------------------------------------

async def main():
    # إنشاء جلسة البوت وجلسة الحساب الشخصي
    bot = TelegramClient('bot_session', API_ID, API_HASH)
    user = TelegramClient('user_session', API_ID, API_HASH)

    print("🔗 جاري الاتصال بخوادم تيليجرام...")
    
    # تشغيل البوت
    await bot.start(bot_token=BOT_TOKEN)
    
    # تشغيل الحساب الشخصي (هنا سيطلب منك الرقم والكود في أول مرة فقط)
    await user.start()
    
    print("✅ البوت شغال الآن ومستعد لسحب المحتوى!")
    print("👋 مرحباً بك يا ريس (Owner ID: 5344366814)")

    @bot.on(events.NewMessage(pattern='/start'))
    async def start(event):
        if event.sender_id == OWNER_ID:
            await event.reply("أهلاً بك! أنا جاهز لسحب أي ميديا مقيدة. ابعت لي رابط المنشور (Post Link) وسأقوم بإعادة إرساله لك.")

    @bot.on(events.NewMessage(pattern=r'https?://t\.me/'))
    async def downloader(event):
        # التأكد أن صاحب البوت فقط هو من يستخدمه
        if event.sender_id != OWNER_ID:
            return
        
        url = event.text.strip()
        status = await event.reply("⏳ جاري فحص الرابط ومحاولة الوصول للمحتوى...")
        
        try:
            # تحليل الرابط لاستخراج ID الرسالة والدردشة
            parts = url.split('/')
            msg_id = int(parts[-1])
            
            # التعامل مع الروابط الخاصة (التي تحتوي على /c/) والروابط العامة
            if '/c/' in url:
                peer = int('-100' + parts[-2])
            else:
                peer = parts[-2]

            # سحب الرسالة باستخدام حسابك الشخصي (Userbot)
            msg = await user.get_messages(peer, ids=msg_id)
            
            if msg and msg.media:
                await status.edit("⬇️ جاري تحميل الميديا من القناة المقيدة...")
                # تحميل الملف مؤقتاً
                path = await user.download_media(msg)
                
                await status.edit("⬆️ جاري إعادة الرفع إليك...")
                # إرسال الملف عن طريق البوت
                await bot.send_file(event.chat_id, path, caption=msg.text)
                
                # حذف الملف المؤقت للحفاظ على مساحة جهازك
                if os.path.exists(path):
                    os.remove(path)
                await status.delete()
            else:
                await status.edit("❌ عذراً، هذا المنشور لا يحتوي على ميديا (صورة أو فيديو).")
        
        except Exception as e:
            error_text = str(e)
            if "Cannot find any entity" in error_text:
                await status.edit("⚠️ خطأ: يجب أن يكون حسابك الشخصي مشتركاً في القناة أولاً.")
            else:
                await status.edit(f"⚠️ حدث خطأ فني: {error_text}")

    # إبقاء البرنامج يعمل
    await bot.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم إغلاق البوت.")