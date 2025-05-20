import pytest
import asyncio
import time
from httpx import AsyncClient
from fastapi import status

# Импортируем основной app и cache_instance для управления состоянием в тестах
# Важно: тесты будут работать с тем же экземпляром кэша, что и приложение
from app.main import app
from app.cache import cache_instance, LRUCache # Импорт LRUCache нужен для проверки capacity
from app.config import settings # Импортируем настройки для проверки capacity

# Фикстура для создания асинхронного клиента для каждого теста
# scope="function" гарантирует, что клиент создается заново для каждого теста
@pytest.fixture(scope="function")
async def client():
    # Перед каждым тестом очищаем кэш, чтобы тесты были независимыми
    await cache_instance.clear()
    # Сбрасываем capacity на случай, если оно менялось (хотя в коде нет такой логики)
    # Это важно, если бы capacity можно было менять динамически
    # cache_instance._capacity = settings.cache_capacity

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    # Можно добавить очистку после теста, но очистка перед важнее
    # await cache_instance.clear()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Тест корневого эндпоинта."""
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"LRU Cache API is running. Capacity: {settings.cache_capacity}"}

@pytest.mark.asyncio
async def test_put_get_item_no_ttl(client: AsyncClient):
    """Тест добавления и получения элемента без TTL."""
    key = "test_key_1"
    value = {"data": "some_value", "number": 123}
    # PUT
    response_put = await client.put(f"/v1/cache/{key}", json={"value": value})
    assert response_put.status_code == status.HTTP_201_CREATED
    assert response_put.json() == {"message": "Key created successfully"}

    # GET
    response_get = await client.get(f"/v1/cache/{key}")
    assert response_get.status_code == status.HTTP_200_OK
    assert response_get.json() == value # Проверяем, что вернулось то же значение

@pytest.mark.asyncio
async def test_put_update_item(client: AsyncClient):
    """Тест обновления существующего элемента."""
    key = "test_key_update"
    value1 = "initial_value"
    value2 = "updated_value"

    # PUT (Create)
    response_put1 = await client.put(f"/v1/cache/{key}", json={"value": value1})
    assert response_put1.status_code == status.HTTP_201_CREATED

    # PUT (Update)
    response_put2 = await client.put(f"/v1/cache/{key}", json={"value": value2})
    assert response_put2.status_code == status.HTTP_200_OK
    assert response_put2.json() == {"message": "Key updated successfully"}


    # GET (Verify update)
    response_get = await client.get(f"/v1/cache/{key}")
    assert response_get.status_code == status.HTTP_200_OK
    assert response_get.json() == value2

@pytest.mark.asyncio
async def test_get_non_existent_key(client: AsyncClient):
    """Тест получения несуществующего ключа."""
    response = await client.get("/v1/cache/non_existent_key")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Key not found or expired"}

@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient):
    """Тест удаления существующего элемента."""
    key = "test_key_delete"
    value = "to_be_deleted"
    await client.put(f"/v1/cache/{key}", json={"value": value}) # Добавляем

    # DELETE
    response_delete = await client.delete(f"/v1/cache/{key}")
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT
    # Тело ответа должно быть пустым для 204

    # GET (Verify deletion)
    response_get = await client.get(f"/v1/cache/{key}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_non_existent_key(client: AsyncClient):
    """Тест удаления несуществующего ключа."""
    response = await client.delete("/v1/cache/non_existent_key_delete")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Key not found"}

@pytest.mark.asyncio
async def test_cache_capacity_and_lru_eviction(client: AsyncClient):
    """Тест достижения лимита емкости и вытеснения LRU."""
    capacity = settings.cache_capacity # Получаем емкость из настроек
    assert capacity > 0, "Capacity must be positive for this test"

    keys = [f"key_{i}" for i in range(capacity + 1)] # Создаем ключи на 1 больше емкости
    values = [f"value_{i}" for i in range(capacity + 1)]

    # Заполняем кэш до предела
    for i in range(capacity):
        response = await client.put(f"/v1/cache/{keys[i]}", json={"value": values[i]})
        assert response.status_code == status.HTTP_201_CREATED

    # Проверяем размер
    stats_before = await client.get("/v1/cache/stats")
    assert stats_before.status_code == status.HTTP_200_OK
    assert stats_before.json()["size"] == capacity
    assert stats_before.json()["items"] == keys[:capacity] # Порядок добавления

    # Добавляем еще один элемент, который должен вытеснить первый (keys[0])
    response_put_over = await client.put(f"/v1/cache/{keys[capacity]}", json={"value": values[capacity]})
    assert response_put_over.status_code == status.HTTP_201_CREATED

    # Проверяем, что первый элемент (LRU) был вытеснен
    response_get_evicted = await client.get(f"/v1/cache/{keys[0]}")
    assert response_get_evicted.status_code == status.HTTP_404_NOT_FOUND

    # Проверяем, что последний добавленный элемент существует
    response_get_new = await client.get(f"/v1/cache/{keys[capacity]}")
    assert response_get_new.status_code == status.HTTP_200_OK
    assert response_get_new.json() == values[capacity]

    # Проверяем статистику после вытеснения
    stats_after = await client.get("/v1/cache/stats")
    assert stats_after.status_code == status.HTTP_200_OK
    assert stats_after.json()["size"] == capacity
    # Ожидаемый порядок: [key_1, key_2, ..., key_{capacity-1}, key_{capacity}]
    expected_keys_after = keys[1:] # Все ключи, кроме первого
    assert stats_after.json()["items"] == expected_keys_after

@pytest.mark.asyncio
async def test_lru_update_on_get(client: AsyncClient):
    """Тест обновления порядка LRU при GET запросе."""
    capacity = settings.cache_capacity
    if capacity < 2: pytest.skip("Test requires capacity >= 2") # Пропускаем тест, если емкость мала

    key1, value1 = "lru_key1", "lru_val1"
    key2, value2 = "lru_key2", "lru_val2"

    # Добавляем два элемента
    await client.put(f"/v1/cache/{key1}", json={"value": value1}) # key1 - LRU
    await client.put(f"/v1/cache/{key2}", json={"value": value2}) # key2 - MRU

    # Статистика до GET
    stats_before = await client.get("/v1/cache/stats")
    assert stats_before.json()["items"] == [key1, key2]

    # Делаем GET для key1, он должен стать MRU
    await client.get(f"/v1/cache/{key1}")

    # Статистика после GET
    stats_after = await client.get("/v1/cache/stats")
    assert stats_after.json()["items"] == [key2, key1] # Порядок изменился

@pytest.mark.asyncio
async def test_lru_update_on_put_update(client: AsyncClient):
    """Тест обновления порядка LRU при обновлении (PUT) элемента."""
    capacity = settings.cache_capacity
    if capacity < 2: pytest.skip("Test requires capacity >= 2")

    key1, value1 = "lru_upd_key1", "lru_upd_val1"
    key2, value2 = "lru_upd_key2", "lru_upd_val2"

    await client.put(f"/v1/cache/{key1}", json={"value": value1}) # key1 - LRU
    await client.put(f"/v1/cache/{key2}", json={"value": value2}) # key2 - MRU

    stats_before = await client.get("/v1/cache/stats")
    assert stats_before.json()["items"] == [key1, key2]

    # Обновляем key1, он должен стать MRU
    await client.put(f"/v1/cache/{key1}", json={"value": "new_value"})

    stats_after = await client.get("/v1/cache/stats")
    assert stats_after.json()["items"] == [key2, key1] # Порядок изменился

@pytest.mark.asyncio
async def test_put_get_with_ttl(client: AsyncClient):
    """Тест добавления элемента с TTL и получения его до истечения срока."""
    key = "ttl_key_1"
    value = "ttl_value_1"
    ttl_seconds = 2 # Короткий TTL для теста

    # PUT с TTL
    response_put = await client.put(f"/v1/cache/{key}", json={"value": value, "ttl": ttl_seconds})
    assert response_put.status_code == status.HTTP_201_CREATED

    # GET сразу после добавления
    response_get_1 = await client.get(f"/v1/cache/{key}")
    assert response_get_1.status_code == status.HTTP_200_OK
    assert response_get_1.json() == value

    # Ждем половину времени TTL
    await asyncio.sleep(ttl_seconds / 2)

    # GET снова (все еще должно работать)
    response_get_2 = await client.get(f"/v1/cache/{key}")
    assert response_get_2.status_code == status.HTTP_200_OK
    assert response_get_2.json() == value

@pytest.mark.asyncio
async def test_get_expired_ttl(client: AsyncClient):
    """Тест получения элемента после истечения TTL."""
    key = "ttl_key_expired"
    value = "ttl_value_expired"
    ttl_seconds = 1 # Очень короткий TTL

    # PUT с TTL
    await client.put(f"/v1/cache/{key}", json={"value": value, "ttl": ttl_seconds})

    # Ждем больше времени, чем TTL
    await asyncio.sleep(ttl_seconds + 0.5)

    # GET (ожидаем 404, так как TTL истек и элемент удаляется при GET)
    response_get = await client.get(f"/v1/cache/{key}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND
    assert response_get.json() == {"detail": "Key not found or expired"}

    # Проверяем статистику, элемента не должно быть
    stats = await client.get("/v1/cache/stats")
    assert key not in stats.json()["items"]


@pytest.mark.asyncio
async def test_put_invalid_ttl(client: AsyncClient):
    """Тест добавления элемента с невалидным TTL (отрицательным)."""
    key = "invalid_ttl_key"
    value = "invalid_ttl_value"

    # PUT с отрицательным TTL
    response_put = await client.put(f"/v1/cache/{key}", json={"value": value, "ttl": -60})
    # Pydantic модель CachePutRequest должна вернуть 422
    assert response_put.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # Проверяем структуру ошибки валидации
    assert "detail" in response_put.json()
    assert isinstance(response_put.json()["detail"], list)
    assert len(response_put.json()["detail"]) > 0
    assert response_put.json()["detail"][0]["loc"] == ["body", "ttl"] # Указывает на поле ttl в теле запроса
    assert "should be a positive integer" in response_put.json()["detail"][0]["msg"] # Сообщение об ошибке

    # PUT с нулевым TTL
    response_put_zero = await client.put(f"/v1/cache/{key}", json={"value": value, "ttl": 0})
    assert response_put_zero.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_cache_stats(client: AsyncClient):
    """Тест эндпоинта статистики."""
    capacity = settings.cache_capacity

    # 1. Пустой кэш
    response_empty = await client.get("/v1/cache/stats")
    assert response_empty.status_code == status.HTTP_200_OK
    assert response_empty.json() == {"size": 0, "capacity": capacity, "items": []}

    # 2. Частично заполненный кэш
    key1, value1 = "stat_key1", "stat_val1"
    key2, value2 = "stat_key2", "stat_val2"
    await client.put(f"/v1/cache/{key1}", json={"value": value1})
    await client.put(f"/v1/cache/{key2}", json={"value": value2})

    response_partial = await client.get("/v1/cache/stats")
    assert response_partial.status_code == status.HTTP_200_OK
    stats_partial = response_partial.json()
    assert stats_partial["size"] == 2
    assert stats_partial["capacity"] == capacity
    assert stats_partial["items"] == [key1, key2] # Порядок добавления/использования

    # 3. Полный кэш (если capacity > 2)
    if capacity >= 2:
        # Заполняем до конца, если нужно
        for i in range(2, capacity):
            await client.put(f"/v1/cache/stat_key_{i}", json={"value": f"stat_val_{i}"})

        response_full = await client.get("/v1/cache/stats")
        assert response_full.status_code == status.HTTP_200_OK
        stats_full = response_full.json()
        assert stats_full["size"] == capacity
        assert stats_full["capacity"] == capacity
        # Проверяем, что все ключи на месте и в правильном порядке (самый старый - первый)
        expected_keys = [key1, key2] + [f"stat_key_{i}" for i in range(2, capacity)]
        assert stats_full["items"] == expected_keys

# Можно добавить тест на очистку кэша, если эндпоинт /cache/clear реализован
@pytest.mark.asyncio
async def test_clear_cache(client: AsyncClient):
    """Тест эндпоинта очистки кэша."""
    key = "clear_key"
    value = "clear_value"
    await client.put(f"/v1/cache/{key}", json={"value": value})

    # Проверяем, что ключ есть
    stats_before = await client.get("/v1/cache/stats")
    assert stats_before.json()["size"] == 1

    # Очищаем кэш
    response_clear = await client.post("/v1/cache/clear")
    assert response_clear.status_code == status.HTTP_204_NO_CONTENT

    # Проверяем, что кэш пуст
    stats_after = await client.get("/v1/cache/stats")
    assert stats_after.json()["size"] == 0
    assert stats_after.json()["items"] == []

    # Проверяем, что ключа больше нет
    response_get = await client.get(f"/v1/cache/{key}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND