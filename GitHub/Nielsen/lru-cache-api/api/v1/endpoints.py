from fastapi import APIRouter, Body, HTTPException, status, Response, Path
from typing import Any
from app.cache import cache_instance
from app.models import (
    CachePutRequest,
    CacheStatsResponse,
    NotFoundErrorResponse,
    ValidationErrorResponse
)

# Создаем роутер для версии v1 API
router = APIRouter(prefix="/v1", tags=["Cache API v1"])

# --- Эндпоинты ---

@router.get(
    "/cache/{key}",
    response_model=Any, # Возвращаем значение как есть
    summary="Получить значение по ключу",
    responses={
        status.HTTP_200_OK: {"description": "Значение найдено"},
        status.HTTP_404_NOT_FOUND: {"model": NotFoundErrorResponse, "description": "Ключ не найден или TTL истек"},
    }
)
async def get_cache_value(key: str = Path(..., description="Ключ для поиска в кэше")):
    """
    Возвращает значение, связанное с ключом `key`.

    - Обновляет позицию ключа в LRU.
    - Если ключ не найден или его TTL истек, возвращает 404.
    """
    value = await cache_instance.get(key)
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found or expired"
        )
    return value

@router.put(
    "/cache/{key}",
    status_code=status.HTTP_200_OK, # По умолчанию 200, но можем изменить
    summary="Добавить или обновить значение по ключу",
    responses={
        status.HTTP_200_OK: {"description": "Значение успешно обновлено"},
        status.HTTP_201_CREATED: {"description": "Значение успешно добавлено"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorResponse, "description": "Ошибка валидации данных (например, отрицательный TTL)"}
    }
)
async def put_cache_value(
    response: Response, # Для установки status_code
    key: str = Path(..., description="Ключ для добавления/обновления"),
    payload: CachePutRequest = Body(...) # Используем модель для валидации тела запроса
):
    """
    Добавляет или обновляет значение для ключа `key`.

    - Принимает JSON с `value` и опциональным `ttl` (в секундах).
    - Если `ttl` не указан, значение кэшируется "навсегда" (до вытеснения).
    - Возвращает 201 Created, если ключ был добавлен, или 200 OK, если обновлен.
    - Обновляет позицию ключа в LRU.
    """
    try:
        created = await cache_instance.put(key, payload.value, payload.ttl)
        if created:
            response.status_code = status.HTTP_201_CREATED
            # Можно вернуть пустое тело или {"message": "Created"}
            return {"message": "Key created successfully"}
        else:
            response.status_code = status.HTTP_200_OK
            # Можно вернуть пустое тело или {"message": "Updated"}
            return {"message": "Key updated successfully"}
    except ValueError as e: # Ловим ошибку валидации TTL из cache.py
         raise HTTPException(
              status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
              detail=str(e) # Или более структурированный формат ошибки
         )


@router.delete(
    "/cache/{key}",
    status_code=status.HTTP_204_NO_CONTENT, # Стандарт для успешного DELETE без тела ответа
    summary="Удалить значение по ключу",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Значение успешно удалено"},
        status.HTTP_404_NOT_FOUND: {"model": NotFoundErrorResponse, "description": "Ключ не найден"},
    }
)
async def delete_cache_value(key: str = Path(..., description="Ключ для удаления")):
    """
    Удаляет значение, связанное с ключом `key`.

    - Возвращает 204 No Content при успехе.
    - Возвращает 404 Not Found, если ключ не найден.
    """
    deleted = await cache_instance.delete(key)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found"
        )
    # При статусе 204 тело ответа должно быть пустым
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/cache/stats",
    response_model=CacheStatsResponse,
    summary="Получить статистику кэша",
    tags=["Cache Stats"] # Отдельный тег для статистики в документации Swagger
)
async def get_cache_stats():
    """
    Возвращает текущую статистику LRU-кэша:
    - `size`: Количество элементов.
    - `capacity`: Максимальная емкость.
    - `items`: Список ключей в порядке LRU (от наиболее к наименее используемым).
    """
    stats = await cache_instance.stats()
    return stats

# Можно добавить эндпоинт для очистки кэша (удобно для тестов/отладки)
@router.post(
    "/cache/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить весь кэш",
    tags=["Cache Management"]
)
async def clear_cache():
    """Полностью очищает содержимое кэша."""
    await cache_instance.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)