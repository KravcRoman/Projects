# Vacation Management Service

API сервис для управления информацией об отпусках сотрудников, разработанный на Python 3.12, FastAPI, SQLAlchemy и PostgreSQL.

## Технологии

* Python 3.12
* FastAPI
* SQLAlchemy 2.0 (Async)
* PostgreSQL (16+)
* Alembic (Миграции БД)
* Pydantic V2 (Валидация)
* AsyncPG (Асинхронный драйвер PostgreSQL)
* Poetry (Управление зависимостями)
* Docker & Docker Compose
* Pytest (Тестирование)
* Black / Flake8 / MyPy (Качество кода)

## Запуск с Docker (Рекомендуемый способ)

1.  **Клонировать репозиторий:**
    ```bash
    git clone <your-repo-url>
    cd vacation-manager
    ```
2.  **Создать файл `.env`:**
    Скопируйте `.env.example` в `.env` и при необходимости измените данные для подключения к PostgreSQL (по умолчанию `user:password@db:5432/vacations_db`).
    ```bash
    cp .env.example .env
    # nano .env # (Optional: Edit if needed)
    ```
3.  **Запустить сервисы:**
    Эта команда соберет образ приложения и запустит контейнеры приложения (`app`) и базы данных (`db`).
    ```bash
    docker-compose up -d --build
    ```
    При первом запуске или после изменений в `Dockerfile` / зависимостях используйте `--build`.
    Приложение автоматически применит миграции Alembic перед запуском FastAPI сервера (согласно `CMD` в `Dockerfile`).

4.  **Сервис будет доступен:**
    * API: `http://localhost:8000`
    * Интерактивная документация (Swagger UI): `http://localhost:8000/docs`
    * Альтернативная документация (ReDoc): `http://localhost:8000/redoc`

5.  **Остановка сервисов:**
    ```bash
    docker-compose down
    ```
    Чтобы удалить volume с данными БД (если нужно начать с чистого листа):
    ```bash
    docker-compose down -v
    ```

## Запуск миграций вручную (если требуется)

Хотя миграции применяются автоматически при старте контейнера `app`, вы можете запустить их вручную:

# Создать новую автогенерируемую миграцию (после изменения моделей SQLAlchemy)
```bash
docker-compose exec app poetry run alembic revision --autogenerate -m "Your migration message"
```

# Применить все ожидающие миграции
```bash
docker-compose exec app poetry run alembic upgrade head
```

# Откатить последнюю миграцию
```bash
docker-compose exec app poetry run alembic downgrade -1
```

## Запуск тестов
1. Убедитесь, что сервисы запущены (docker-compose up -d).
2. Настройте тестовую БД (если она отличается). Фикстура conftest.py попытается использовать TEST_DATABASE_URL из окружения или создаст имя вида <основная_БД>_test. Убедитесь, что эта БД доступна или измените логику в conftest.py.
3. Запустите тесты внутри контейнера app:

# Можно передать переменные окружения для тестов так:
# docker-compose exec -e TEST_DATABASE_URL="<your_test_db_url>" app poetry run pytest tests/
# Или настроить их в docker-compose.yml / .env для тестов
```bash
docker-compose exec app poetry run pytest tests/
```

## Документация API

# Базовый URL: http://localhost:8000/api/v1/vacations

# См. интерактивную документацию: http://localhost:8000/docs

# Основные эндпоинты:

1. Добавить отпуск

    * POST /
    * Тело запроса (JSON):
    {
      "employee_id": 101,
      "start_date": "2025-08-01",
      "end_date": "2025-08-10"
    }
   
    * Успешный ответ: 201 Created с данными созданного отпуска.
    * Ошибка: 409 Conflict (пересечение), 422 Unprocessable Entity (невалидные данные).

2. Получить отпуска за период

    * GET /?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    * Параметры запроса: start_date, end_date (обязательные).
    * Пример: GET /?start_date=2025-07-01&end_date=2025-09-30
    * Успешный ответ: 200 OK со списком отпусков.

3. Получить последние отпуска сотрудника

    * GET /employees/{employee_id}?limit=N
    * Параметры пути: employee_id (обязательный).
    * Параметр запроса: limit (опциональный, по умолчанию 3).
    * Пример: GET /employees/101?limit=2
    * Успешный ответ: 200 OK со списком N последних отпусков сотрудника.

4. Удалить отпуск

    * DELETE /{vacation_id}
    * Параметр пути: vacation_id (ID удаляемого отпуска).
    * Пример: DELETE /5
    * Успешный ответ: 204 No Content.
    * Ошибка: 404 Not Found (отпуск не найден).
