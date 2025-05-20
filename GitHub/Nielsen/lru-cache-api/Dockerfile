# Используем официальный образ Python последней стабильной версии (slim для меньшего размера)
# Замените 3.11 на актуальную версию, если необходимо
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем переменные окружения
# PYTHONUNBUFFERED: гарантирует, что вывод Python отправляется прямо в терминал (полезно для логов Docker)
# PYTHONDONTWRITEBYTECODE: предотвращает создание .pyc файлов Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Указываем Poetry использовать системный Python и не создавать свои venv внутри контейнера
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    # Путь для установки пакетов Poetry
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Устанавливаем Poetry
# RUN pip install poetry==<конкретная_версия> # Можно зафиксировать версию Poetry
RUN pip install poetry

# Копируем файлы зависимостей
# Копируем сначала их, чтобы использовать кэш слоев Docker при изменении только кода приложения
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости проекта, исключая dev-зависимости
# --no-root: не устанавливать сам проект как пакет (он будет скопирован позже)
RUN poetry install --no-dev --no-root

# Копируем все остальное из текущей директории (.) в рабочую директорию контейнера (/app)
COPY . .

# Указываем порт, который будет слушать приложение внутри контейнера
EXPOSE 8000

# Команда для запуска приложения при старте контейнера
# Запускаем uvicorn, указывая путь к FastAPI app объекту (app.main:app)
# --host 0.0.0.0: делает сервер доступным снаружи контейнера
# --port 8000: порт внутри контейнера
# --reload: опция для разработки, автоматически перезапускает сервер при изменении кода (убрать для production)
# CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# Команда для production (без --reload):
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]