from pydantic import BaseModel, Field

class FeedbackCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Имя клиента")
    phone: str = Field(..., min_length=10, max_length=20, description="Телефон")
    message: str = Field(..., min_length=1, max_length=2000, description="Текст сообщения")