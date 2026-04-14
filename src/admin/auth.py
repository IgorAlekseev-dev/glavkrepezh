import asyncio
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AuthProvider
from starlette_admin.exceptions import LoginFailed
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AdminUser
from src.auth.security import verify_password
from src.database import engine

class MyAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        # 1. Защита от брутфорса (задержка)
        await asyncio.sleep(2)

        # 2. Проверка пользователя в БД
        async with AsyncSession(engine) as session:
            stmt = select(AdminUser).where(AdminUser.username == username)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user and verify_password(password, user.password_hash):
                # 3. Успех: сохраняем ID в сессию
                request.session.update({"user_id": user.id, "username": user.username})
                # Возвращаем response (он уже содержит редирект, подготовленный Starlette Admin)
                return response
        
        # 4. Неудача: Выбрасываем специальное исключение
        raise LoginFailed("Неверный логин или пароль")

    async def is_authenticated(self, request: Request) -> bool:
        # Проверяем, есть ли пользователь в сессии
        return request.session.get("user_id") is not None

    async def logout(self, request: Request, response: Response) -> Response:
        # Очищаем сессию при выходе
        request.session.clear()
        return response