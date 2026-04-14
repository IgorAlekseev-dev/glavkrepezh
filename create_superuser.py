import asyncio
import getpass
from sqlalchemy import select

from src.database import async_session_maker
from src.auth.models import AdminUser
from src.auth.security import get_password_hash

async def create_admin():
    print("\n=== Создание нового администратора ===")
    
    # 1. Ввод логина
    username = input("Введите логин: ").strip()
    if not username:
        print("❌ Ошибка: Логин не может быть пустым.")
        return

    # 2. Ввод пароля (скрыто)
    password = getpass.getpass(f"Введите пароль для '{username}': ")
    if not password:
        print("❌ Ошибка: Пароль не может быть пустым.")
        return
        
    # 3. Подтверждение пароля
    password_confirm = getpass.getpass("Повторите пароль: ")
    if password != password_confirm:
        print("❌ Ошибка: Пароли не совпадают!")
        return

    # 4. Работа с базой данных
    async with async_session_maker() as session:
        # Проверяем, не занят ли логин
        result = await session.execute(select(AdminUser).where(AdminUser.username == username))
        if result.scalars().first():
            print(f"❌ Ошибка: Пользователь с логином '{username}' уже существует.")
            return

        # Хэшируем и сохраняем
        new_admin = AdminUser(
            username=username,
            password_hash=get_password_hash(password)
        )
        session.add(new_admin)
        await session.commit()
        
        print(f"\n✅ Успех! Суперпользователь '{username}' создан и добавлен в базу.")
        print("Теперь вы можете использовать эти данные для входа в панель управления.\n")

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(create_admin())