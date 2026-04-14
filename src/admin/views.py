import asyncio
from typing import Any, Dict
from fastapi import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import FileField, IntegerField
from fastapi.concurrency import run_in_threadpool

from src.admin.models import PriceDoc
from src.admin.service import handle_price_upload 

class PriceDocView(ModelView):
    icon = "fa fa-file-excel"
    label = "Загрузка прайса"

    fields = [
        IntegerField("id", read_only=True),
        FileField("filename", label="Файл Excel (.xlsx)"),
    ]

    sort = [("created_at", True)]

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        value = data.get("filename")

        if isinstance(value, tuple):
            uploaded_file = value[0]
        else:
            uploaded_file = value

        if uploaded_file and hasattr(uploaded_file, "filename") and hasattr(uploaded_file, "read"):
            
            print(f"✅ Файл найден: {uploaded_file.filename}")

            content = await uploaded_file.read()
            
            async def wrapper():
                await run_in_threadpool(handle_price_upload, content)
            
            asyncio.create_task(wrapper())
            
            data["filename"] = "price.xlsx"
        
        else:
            print(f"❌ Файл не найден или неверный формат. Получено: {type(value)}")

        session = request.state.session
        obj = PriceDoc()
        session.add(obj)
        await session.commit()
        return obj