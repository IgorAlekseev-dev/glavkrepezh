#!/bin/bash
# Завершаем скрипт при любой ошибке
set -e

echo "🚀 Запуск миграций БД (Alembic)..."
uv run alembic upgrade head

echo "🚀 Запуск FastAPI (Uvicorn)..."
# Используем флаг --proxy-headers, так как мы за Nginx
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'