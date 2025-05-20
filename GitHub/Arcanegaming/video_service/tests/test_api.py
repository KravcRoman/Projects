import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from ..app import schemas
from ..app.core.config import settings  # Для API_V1_STR, если используется

# pytest.mark.asyncio нужен для всех тестовых функций, использующих async/await
pytestmark = pytest.mark.asyncio

# Базовый URL для API эндпоинтов
API_BASE_URL = "/api/videos"  # Учитывая, что base_url клиента "http://testserver"


async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


async def test_create_video_success(client: AsyncClient, db: AsyncSession):
    video_data = {
        "title": "Тестовое видео 1",
        "url": "http://example.com/testvideo1.mp4"  # Используем url вместо original_url для запроса
    }
    response = await client.post(API_BASE_URL, json=video_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == video_data["title"]
    assert "id" in data
    assert "playlist_url" in data
    # Проверка, что playlist_url соответствует ожидаемому формату
    expected_playlist_url_part = f"{settings.BASE_URL}/hls/{data['id']}.m3u8"
    assert data["playlist_url"] == expected_playlist_url_part


async def test_create_video_duplicate_url(client: AsyncClient):
    video_data_1 = {"title": "Уникальное видео 1", "url": "http://example.com/unique.mp4"}
    response1 = await client.post(API_BASE_URL, json=video_data_1)
    assert response1.status_code == status.HTTP_201_CREATED

    video_data_2 = {"title": "Дубликат видео", "url": "http://example.com/unique.mp4"}
    response2 = await client.post(API_BASE_URL, json=video_data_2)
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert "уже существует" in response2.json()["detail"]


async def test_create_video_invalid_url(client: AsyncClient):
    video_data = {"title": "Невалидный URL", "url": "этонеurl"}
    response = await client.post(API_BASE_URL, json=video_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_get_video_success(client: AsyncClient):
    # Сначала создаем видео
    video_create_data = {"title": "Видео для GET", "url": "http://example.com/get_video.mp4"}
    create_response = await client.post(API_BASE_URL, json=video_create_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_video_id = create_response.json()["id"]
    expected_playlist_url = create_response.json()["playlist_url"]

    # Тестируем GET эндпоинт
    get_response = await client.get(f"{API_BASE_URL}/{created_video_id}")
    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert data["id"] == created_video_id
    assert data["title"] == video_create_data["title"]
    assert data["original_url"] == video_create_data["url"]  # original_url должен быть равен url из запроса
    assert data["playlist_url"] == expected_playlist_url
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_video_not_found(client: AsyncClient):
    non_existent_id = 99999
    response = await client.get(f"{API_BASE_URL}/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Видео не найдено"


async def test_get_video_uses_cache(client: AsyncClient, db: AsyncSession):
    # 1. Создаем видео
    video_create_data = {"title": "Кешируемое видео", "url": "http://example.com/cache_video.mp4"}
    create_response = await client.post(API_BASE_URL, json=video_create_data)
    video_id = create_response.json()["id"]

    # 2. Первый запрос (данные из БД, должны кешироваться)
    response1 = await client.get(f"{API_BASE_URL}/{video_id}")
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()

    # 3. "Удаляем" видео из БД (или изменяем так, чтобы было видно, что данные из кеша)
    #    Это сложнее сделать чисто, не влияя на другие тесты, если БД общая.
    #    Проще проверить, что Redis содержит ключ.
    from ..app.cache import get_redis_client
    redis_client = await get_redis_client()
    cached_data_raw = await redis_client.get(f"video:{video_id}")
    await redis_client.close()

    assert cached_data_raw is not None
    cached_video = schemas.VideoResponse.model_validate_json(cached_data_raw)
    assert cached_video.id == video_id
    assert cached_video.title == video_create_data["title"]

    # 4. Второй запрос (данные должны быть из кеша)
    #    Чтобы это доказать, можно было бы попробовать "испортить" данные в БД,
    #    но это рискованно для параллельных тестов.
    #    Достаточно того, что мы проверили наличие в Redis.
    response2 = await client.get(f"{API_BASE_URL}/{video_id}")
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    assert data1 == data2  # Ответы должны быть идентичны
