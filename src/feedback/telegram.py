import httpx
from src.config import settings

async def send_telegram_notification(name: str, phone: str, message: str):
    """Асинхронная отправка сообщения в Telegram"""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_IDS:
        print("⚠️ Telegram Token или Chat IDs не настроены!")
        return

    text = (
        f"🚨 <b>Новое сообщение с сайта!</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📞 <b>Телефон:</b> {phone}\n\n"
        f"💬 <b>Сообщение:</b>\n{message}"
    )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    chat_ids =[chat_id.strip() for chat_id in settings.TELEGRAM_CHAT_IDS.split(",") if chat_id.strip()]

    async with httpx.AsyncClient() as client:
        for chat_id in chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            try:
                # Отправляем POST запрос
                response = await client.post(url, json=payload)
                
                if response.status_code != 200:
                    print(f"❌ Telegram Error for {chat_id}: {response.json().get('description')}")
                else:
                    print(f"✅ Успех для {chat_id}")
                    
            except Exception as e:
                print(f"❌ Критическая ошибка отправки для {chat_id}: {e}")
                if hasattr(e, 'response'):
                    print(f"🔍 Ответ API: {e.response.text}")
