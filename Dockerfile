# Используем легкий официальный образ Python
FROM python:3.11-slim-bookworm

# Устанавливаем системные зависимости (если нужны для psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Копируем uv из официального образа (это самый быстрый и надежный способ)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Настройки Python и uv
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1

# Рабочая директория
WORKDIR /app

# Сначала копируем только файлы зависимостей (для кэширования слоев Docker)
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости с помощью uv (создаст .venv внутри /app)
RUN uv sync --frozen --no-dev

# Копируем весь остальной код
COPY . .

# Даем права на запуск скрипта
RUN chmod +x start.sh

# Открываем порт
EXPOSE 8000

# Запускаем скрипт (Миграции -> FastAPI)
CMD ["./start.sh"]