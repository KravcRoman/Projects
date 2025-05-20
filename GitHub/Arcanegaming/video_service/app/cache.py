import redis.asyncio as redis
from core.config import settings
from schemas import VideoResponse # Для сериализации/десериализации

# Глобальный пул соединений Redis
redis_pool = None

async def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            decode_responses=True # Автоматически декодировать ответы из байтов в строки
        )
    return redis_pool

async def get_redis_client() -> redis.Redis:
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)


async def set_video_cache(video_id: int, video_data: VideoResponse):
    """
    Сохраняет данные видео в кеш Redis.
    Данные сериализуются в JSON.
    """
    try:
        r = await get_redis_client()
        cache_key = f"video:{video_id}"
        await r.set(cache_key, video_data.model_dump_json(), ex=settings.CACHE_EXPIRATION_SECONDS)
        await r.close() # Закрываем соединение (возвращаем в пул)
    except Exception as e:
        # Здесь можно добавить логирование ошибки кеширования
        print(f"Ошибка записи в Redis: {e}")


async def get_video_cache(video_id: int) -> VideoResponse | None:
    """
    Получает данные видео из кеша Redis.
    Если данные найдены, они десериализуются из JSON.
    """
    try:
        r = await get_redis_client()
        cache_key = f"video:{video_id}"
        cached_video = await r.get(cache_key)
        await r.close() # Закрываем соединение (возвращаем в пул)

        if cached_video:
            return VideoResponse.model_validate_json(cached_video)
        return None
    except Exception as e:
        # Логирование ошибки
        print(f"Ошибка чтения из Redis: {e}")
        return None

async def clear_video_cache(video_id: int):
    """
    Удаляет данные видео из кеша Redis.
    (Может понадобиться при обновлении/удалении видео)
    """
    try:
        r = await get_redis_client()
        cache_key = f"video:{video_id}"
        await r.delete(cache_key)
        await r.close()
    except Exception as e:
        print(f"Ошибка удаления из Redis: {e}")

# Функция для закрытия пула соединений при остановке приложения
async def close_redis_pool():
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()
        print("Redis connection pool closed.")
