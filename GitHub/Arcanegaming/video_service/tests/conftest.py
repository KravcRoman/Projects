import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ..app.main import app
from ..app.database import Base, get_db
from ..app.core.config import settings
from ..app.cache import get_redis_client, close_redis_pool, get_redis_pool

# Используем основную тестовую БД, но будем очищать ее
# Убедитесь, что .env настроен для тестового окружения, если это необходимо
# или что тесты не влияют на "боевые" данные разработки.
# Для этого примера мы используем ту же конфигурацию БД, что и для разработки,
# но таблицы будут создаваться и удаляться для каждого тестового сеанса.

# Создаем engine и sessionmaker для тестов, используя URL из settings
# Это важно, чтобы тесты работали с той же конфигурацией, что и приложение в Docker (если тесты запускаются на хосте)
# или с предоставленной тестовой БД.
# Если тесты запускаются ВНУТРИ Docker, то settings.ASYNC_DATABASE_URL будет указывать на db сервис.
test_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)  # Используем URL из .env
TestAsyncSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db_for_test() -> AsyncSession:
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
            # Коммит не нужен здесь, так как каждый тест может управлять транзакциями
            # или setup_test_database будет откатывать все.
            # Но для консистентности с get_db можно оставить commit/rollback.
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db_for_test


# Фикстура для очистки Redis перед/после тестов (опционально, но полезно)
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_redis():
    # Инициализация пула Redis, если еще не сделана
    await get_redis_pool()

    # Очистка тестовой БД Redis перед тестами (если используется одна и та же БД Redis)
    # Это более безопасно, если тесты могут влиять друг на друга через кеш.
    # Убедитесь, что settings.REDIS_DB используется для тестов или это специальная тестовая БД Redis.
    try:
        r = await get_redis_client()
        await r.flushdb()  # ОСТОРОЖНО: это удалит ВСЕ ключи в текущей БД Redis!
        await r.close()
        print("Test Redis DB flushed.")
    except Exception as e:
        print(f"Could not flush test Redis DB: {e}")

    yield

    # Закрытие пула Redis после всех тестов
    await close_redis_pool()
    print("Test Redis pool closed.")


@pytest_asyncio.fixture(scope="session")  # "session" чтобы event loop был один на все тесты
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)  # autouse=True для автоматического применения
async def manage_test_database_tables():
    """Создает таблицы перед тестами и удаляет после."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Сначала удаляем, если что-то осталось
        await conn.run_sync(Base.metadata.create_all)

    yield  # Тесты выполняются здесь

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()  # Важно для корректного закрытия соединений


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncSession:  # Переименовано для соответствия с Depends(get_db)
    """Предоставляет сессию БД для каждого теста."""
    async with TestAsyncSessionLocal() as session:
        # Начало транзакции (необязательно, если каждый тест атомарен или очистка глобальная)
        # await session.begin()
        yield session
        # Откат транзакции после каждого теста для изоляции (если транзакции использовались)
        # await session.rollback()
        # Для простоты, полагаемся на drop_all/create_all в manage_test_database_tables


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncClient:
    """Асинхронный HTTP клиент для тестирования API."""
    # Убедимся, что переопределение get_db установлено
    app.dependency_overrides[get_db] = override_get_db_for_test
    async with AsyncClient(app=app, base_url="http://testserver") as ac:  # testserver - стандарт для ASGI тестов
        yield ac
