import time
import asyncio
from collections import OrderedDict
from typing import Any, Optional, Tuple, List

class LRUCache:
    """
    Реализация LRU Cache с поддержкой TTL и asyncio safe.
    """
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self._capacity = capacity
        # OrderedDict хранит пары ключ -> (значение, время_истечения)
        # Время истечения None означает отсутствие TTL.
        self._cache: OrderedDict[Any, Tuple[Any, Optional[float]]] = OrderedDict()
        self._lock = asyncio.Lock() # Блокировка для безопасности в asyncio

    async def get(self, key: Any) -> Optional[Any]:
        """
        Получает значение по ключу. Обновляет порядок использования.
        Удаляет элемент, если TTL истек.
        """
        async with self._lock:
            if key not in self._cache:
                return None

            value, expiration_time = self._cache[key]

            # Проверка TTL
            if expiration_time is not None and time.time() > expiration_time:
                # TTL истек, удаляем элемент
                del self._cache[key]
                return None

            # Ключ использован, перемещаем в конец (самый свежий)
            self._cache.move_to_end(key)
            return value

    async def put(self, key: Any, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Добавляет или обновляет значение по ключу.
        Управляет TTL и размером кэша (вытеснение LRU).
        Возвращает True, если ключ был создан, False - если обновлен.
        """
        if ttl is not None and ttl <= 0:
             raise ValueError("TTL must be a positive integer if provided")

        async with self._lock:
            expiration_time = (time.time() + ttl) if ttl else None
            created = key not in self._cache # Проверяем, новый ли это ключ

            self._cache[key] = (value, expiration_time)
            self._cache.move_to_end(key) # Обновляем порядок использования

            # Проверка на превышение емкости и вытеснение LRU
            if len(self._cache) > self._capacity:
                # popitem(last=False) удаляет самый старый элемент (LRU)
                self._cache.popitem(last=False)

            return created

    async def delete(self, key: Any) -> bool:
        """
        Удаляет значение по ключу.
        Возвращает True, если ключ был найден и удален, иначе False.
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def stats(self) -> dict:
        """
        Возвращает статистику кэша.
        """
        async with self._lock:
            # Важно: статистика показывает текущее состояние, включая элементы,
            # чей TTL мог истечь, но они еще не были запрошены (get) или удалены.
            # Можно добавить опциональную очистку перед показом статистики,
            # но это может быть затратно. Оставим текущее состояние.
            current_items = list(self._cache.keys()) # Ключи уже упорядочены по LRU
            return {
                "size": len(self._cache),
                "capacity": self._capacity,
                "items": current_items,
                 # Дополнительно можно вернуть элементы с их TTL (для отладки)
                # "details": {k: (v[0], v[1] - time.time() if v[1] else None) for k, v in self._cache.items()}
            }

    async def clear(self):
        """Очищает весь кэш (полезно для тестов)."""
        async with self._lock:
            self._cache.clear()

# Создаем единственный экземпляр кэша для всего приложения
# Используем емкость из конфигурации
cache_instance = LRUCache(capacity=settings.cache_capacity)