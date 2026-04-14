from fastapi import APIRouter, Form, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from pathlib import Path

from src.depends import SessionDep
from src.feedback.models import Customer, FeedbackMessage
from src.feedback.schemas import FeedbackCreate
from src.feedback.telegram import send_telegram_notification
from src.feedback.notifications import send_vk_notification, send_email_notification

router = APIRouter(tags=["Feedback"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.post("/api/feedback")
async def submit_feedback(
    request: Request,
    background_tasks: BackgroundTasks,
    db: SessionDep,
    # Принимаем данные как Form (так как отправлять будем через HTMX)
    name: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...)
):
    # 1. Валидация через Pydantic
    form_data = FeedbackCreate(name=name, phone=phone, message=message)

    # 2. Ищем клиента в базе по номеру телефона
    query = select(Customer).where(Customer.phone == form_data.phone)
    result = await db.execute(query)
    customer = result.scalars().first()

    # Если новый клиент — создаем
    if not customer:
        customer = Customer(name=form_data.name, phone=form_data.phone)
        db.add(customer)
        await db.flush() # Получаем ID
    elif customer.name != form_data.name:
        # Если клиент с таким телефоном есть, но имя другое — обновляем имя
        customer.name = form_data.name

    # 3. Сохраняем сообщение
    feedback = FeedbackMessage(customer_id=customer.id, message=form_data.message)
    db.add(feedback)
    await db.commit()

    # 4. Отправляем в Telegram ФОНОМ (чтобы не тормозить сайт)
    # background_tasks.add_task(
    #     send_telegram_notification, 
    #     name=form_data.name, 
    #     phone=form_data.phone, 
    #     message=form_data.message
    # )
    background_tasks.add_task(send_vk_notification, name=form_data.name, phone=form_data.phone, message=form_data.message)
    background_tasks.add_task(send_email_notification, name=form_data.name, phone=form_data.phone, message=form_data.message)

    # 5. Возвращаем кусочек HTML (Успех) для HTMX
    return templates.TemplateResponse("components/success_message.html", {"request": request})


@router.get("/api/feedback/form")
async def get_feedback_form(request: Request):
    return templates.TemplateResponse("components/feedback_form.html", {"request": request})