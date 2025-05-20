# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем переменные окружения
# предотвращает запись .pyc файлов Python в контейнер
ENV PYTHONDONTWRITEBYTECODE 1
# обеспечивает немедленный вывод логов Python в консоль
ENV PYTHONUNBUFFERED 1


# Копируем файлы зависимостей и устанавливаем их
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini
COPY .env /app/.env_example

# 7. Открываем порт, на котором будет работать приложение
EXPOSE 8000

# 8. Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]