import httpx
from email.message import EmailMessage
import aiosmtplib
from src.config import settings

async def send_vk_notification(name: str, phone: str, message: str):
    """Асинхронная отправка сообщения в ВКонтакте"""
    if not settings.VK_BOT_TOKEN or not settings.VK_USER_IDS:
        print("⚠️ VK Token или User IDs не настроены!")
        return

    text = (
        f"🚨 Новая заявка с сайта ГлавКрепеж!\n\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"💬 Сообщение: {message}"
    )

    url = "https://api.vk.com/method/messages.send"
    user_ids =[uid.strip() for uid in settings.VK_USER_IDS.split(",") if uid.strip()]

    async with httpx.AsyncClient() as client:
        for uid in user_ids:
            payload = {
                "user_id": uid,
                "message": text,
                "random_id": 0, # Обязательный параметр для VK
                "access_token": settings.VK_BOT_TOKEN,
                "v": "5.131"    # Версия API VK
            }
            try:
                # В отличие от ТГ, ВК любит данные в виде формы (data), а не JSON
                response = await client.post(url, data=payload)
                resp_json = response.json()
                
                if "error" in resp_json:
                    print(f"❌ Ошибка VK для {uid}: {resp_json['error']['error_msg']}")
                else:
                    print(f"✅ Сообщение ВК успешно отправлено пользователю {uid}")
            except Exception as e:
                print(f"❌ Критическая ошибка VK для {uid}: {e}")

async def send_email_notification(name: str, phone: str, message: str):
    """Асинхронная отправка сообщения на Email нескольким получателям"""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD or not settings.EMAIL_RECIPIENTS:
        print("⚠️ Настройки SMTP не заданы!")
        return

    text = (
        f"🚨 Новая заявка с сайта ГлавКрепеж!\n\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n\n"
        f"💬 Сообщение:\n{message}"
    )

    raw_emails = settings.EMAIL_RECIPIENTS.split(",")
    recipients =[email.strip() for email in raw_emails if email.strip()]

    if not recipients:
        print("⚠️ Список получателей Email пуст!")
        return

    msg = EmailMessage()
    msg.set_content(text)
    msg["Subject"] = "🚨 Новая заявка с сайта ГлавКрепеж!"
    msg["From"] = settings.SMTP_USER
    
    msg["To"] = ", ".join(recipients)

    try:
        use_start_tls = (settings.SMTP_PORT == 587)
        use_ssl = (settings.SMTP_PORT == 465)

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            use_tls=use_ssl,           # True если 465
            start_tls=use_start_tls,   # True если 587
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            timeout=10
        )
        print(f"✅ Email успешно отправлен!")
    except Exception as e:
        print(f"❌ Ошибка отправки Email: {e}")