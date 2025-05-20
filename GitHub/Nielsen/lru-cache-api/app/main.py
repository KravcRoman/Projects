from fastapi import FastAPI
from app.middleware import LoggingMiddleware
from api.v1 import endpoints as api_v1 # Импортируем роутер v1
from app.config import settings # Импортируем настройки для информации

# Создаем экземпляр FastAPI
app = FastAPI(
    title="LRU Cache API with TTL",
    description="REST API для управления LRU-кэшем с поддержкой Time-To-Live.",
    version="1.0.0",
    # Можно добавить docs_url и redoc_url, если нужно изменить пути к документации
    # docs_url="/documentation",
    # redoc_url=None, # Отключить ReDoc
)

# Добавляем Middleware для логирования
app.add_middleware(LoggingMiddleware)

# Подключаем роутер API версии 1
app.include_router(api_v1.router)

# Добавляем корневой эндпоинт для проверки работоспособности
@app.get("/", tags=["Health Check"])
async def read_root():
    """Простой эндпоинт для проверки, что API работает."""
    return {"message": f"LRU Cache API is running. Capacity: {settings.cache_capacity}"}

# Запуск приложения (обычно выполняется через uvicorn в командной строке или Docker CMD)
# Если нужно запустить напрямую из Python (например, для отладки):
if __name__ == "__main__":
    import uvicorn
    # Загружаем настройки uvicorn из командной строки или переменных окружения,
    # но можно задать и здесь для простоты локального запуска.
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")