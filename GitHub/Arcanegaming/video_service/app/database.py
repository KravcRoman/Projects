from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Асинхронный движок для SQLAlchemy
# URL для подключения берется из настроек
# echo=True для логирования SQL-запросов
engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)

# Фабрика асинхронных сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Важно для асинхронных задач FastAPI
    autocommit=False,
    autoflush=False,
)

# Базовый класс для декларативных моделей SQLAlchemy
Base = declarative_base()

# Зависимость для получения сессии БД в эндпоинтах
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Коммит в конце, если все успешно
        except Exception:
            await session.rollback() # Откат при ошибке
            raise
        finally:
            await session.close()
