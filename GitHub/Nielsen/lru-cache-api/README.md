# REST API для LRU Cache с TTL

Это реализация простого REST API для управления LRU (Least Recently Used) кэшем с поддержкой TTL (Time-To-Live) с использованием FastAPI, Pydantic и asyncio.

## Особенности

* **LRU Логика**: Автоматическое вытеснение наименее используемых элементов при достижении лимита емкости.
* **TTL**: Поддержка времени жизни для каждого элемента кэша. Элементы с истекшим TTL удаляются при доступе.
* **Асинхронность**: API и логика кэша используют `asyncio` для неблокирующей обработки запросов.
* **Потокобезопасность**: Доступ к кэшу защищен с помощью `asyncio.Lock`.
* **Конфигурируемая емкость**: Максимальный размер кэша задается через переменную окружения `CACHE_CAPACITY`.
* **Валидация**: Входящие данные валидируются с помощью Pydantic.
* **Логирование**: Middleware для логирования запросов и времени их выполнения.
* **Тесты**: Unit-тесты с использованием `pytest` и `httpx`.
* **Docker**: Готовые `Dockerfile` и `docker-compose.yml` для легкого запуска в контейнере.
* **Документация API**: Автоматически генерируемая документация Swagger UI (`/docs`) и ReDoc (`/redoc`).

## Технологии

* Python 3.11+
* FastAPI
* Pydantic (v2) / Pydantic-Settings
* Uvicorn
* Pytest
* HTTPX
* Poetry
* Docker
* Docker Compose

## Структура проекта
lru-cache-api/
├── api/v1/endpoints.py  # Маршруты API v1
├── app/                 # Основной код
│   ├── cache.py         # Логика LRU Cache
│   ├── config.py        # Конфигурация
│   ├── main.py          # Точка входа FastAPI
│   ├── middleware.py    # Middleware логирования
│   └── models.py        # Pydantic модели
├── tests/               # Unit тесты
│   └── test_api.py
├── .env.example         # Пример файла переменных окружения
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml       # Зависимости и настройки Poetry
├── README.md
└── poetry.lock

## Предварительные требования

* Docker
* Docker Compose (обычно идет вместе с Docker Desktop)
* Опционально: Python 3.11+ и Poetry (для локальной разработки/тестирования без Docker)

## Запуск с Docker (Рекомендуемый способ)

1.  **Склонируйте репозиторий:**
    ```bash
    git clone <url-репозитория>
    cd lru-cache-api
    ```

2.  **Создайте файл `.env`** (опционально):
    Скопируйте `.env.example` в `.env` и установите желаемое значение `CACHE_CAPACITY`. Если файл `.env` отсутствует или переменная не задана, будет использовано значение по умолчанию (10) или значение из `docker-compose.yml`.
    ```bash
    cp .env.example .env
    # Отредактируйте .env, например:
    # CACHE_CAPACITY=50
    ```

3.  **Запустите с помощью Docker Compose:**
    Эта команда соберет Docker-образ (если он еще не собран) и запустит контейнер с API.
    ```bash
    docker-compose up -d
    ```
    * `-d` запускает контейнер в фоновом режиме. Уберите `-d`, чтобы видеть логи в терминале.

4.  **API будет доступен по адресу:** `http://localhost:8000`
    * Документация Swagger UI: `http://localhost:8000/docs`
    * Документация ReDoc: `http://localhost:8000/redoc`

5.  **Остановка:**
    ```bash
    docker-compose down
    ```

## Локальный запуск (Без Docker)

1.  **Установите Poetry:** [Инструкции по установке Poetry](https://python-poetry.org/docs/#installation)

2.  **Склонируйте репозиторий и перейдите в директорию:**
    ```bash
    git clone <url-репозитория>
    cd lru-cache-api
    ```

3.  **Создайте файл `.env`** (как описано выше), чтобы установить `CACHE_CAPACITY`.

4.  **Установите зависимости:**
    ```bash
    poetry install
    ```

5.  **Активируйте виртуальное окружение:**
    ```bash
    poetry shell
    ```

6.  **Запустите FastAPI приложение с Uvicorn:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    * `--reload` включает автоматическую перезагрузку при изменении кода (удобно для разработки).

7.  API будет доступен по адресу `http://localhost:8000`.

## Запуск тестов

Тесты используют `pytest` и `httpx` для взаимодействия с API.

**С помощью Docker Compose:**

1.  Убедитесь, что контейнеры остановлены (`docker-compose down`).
2.  Вы можете запустить тесты в отдельном контейнере или изменить `docker-compose.yml` для запуска тестов. Простой способ - запустить команду внутри запущенного контейнера или использовать отдельный сервис в compose.

   *Пример команды для запуска тестов внутри работающего контейнера:*
    ```bash
    docker-compose exec lru-cache-api poetry run pytest tests/
    ```
   *(где `lru-cache-api` - имя сервиса в `docker-compose.yml`)*

**Локально (без Docker):**

1.  Убедитесь, что вы находитесь в активированном виртуальном окружении (`poetry shell`).
2.  Запустите `pytest`:
    ```bash
    pytest tests/
    ```

## API Эндпоинты (Префикс: /v1)

* `GET /cache/{key}`: Получить значение по ключу.
* `PUT /cache/{key}`: Добавить или обновить значение. Тело запроса: `{"value": <any>, "ttl": <int | null>}`.
* `DELETE /cache/{key}`: Удалить значение по ключу.
* `GET /cache/stats`: Получить статистику кэша (`size`, `capacity`, `items`).
* `POST /cache/clear`: Очистить весь кэш.
* `GET /`: Health check.

См. `http://localhost:8000/docs` для детальной интерактивной документации.

## Конфигурация

* `CACHE_CAPACITY` (переменная окружения): Устанавливает максимальное количество элементов в кэше. По умолчанию: `10`. Должно быть положительным целым числом.