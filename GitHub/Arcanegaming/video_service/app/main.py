from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from . import crud, models, schemas, tasks, cache
from database import engine, get_db
from core.config import settings
from cache import close_redis_pool  # Импорт функции закрытия пула Redis

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Создание таблиц в БД при запуске (если их нет).
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


# --- FastAPI App Instance ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# --- Event Handlers ---
@app.on_event("startup")
async def on_startup():
    logger.info("Приложение запускается...")
    await create_db_and_tables()  # Создаем таблицы
    # Инициализация пула Redis (необязательно здесь, т.к. он ленивый)
    await cache.get_redis_pool()
    logger.info("Пул соединений Redis инициализирован (или проверен).")
    logger.info("Приложение успешно запущено.")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Приложение останавливается...")
    await close_redis_pool()  # Закрываем пул соединений Redis
    logger.info("Приложение успешно остановлено.")


# --- API Endpoints ---
@app.post("/api/videos", response_model=schemas.VideoCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_video_info(
        video_in: schemas.VideoCreate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    """
    Загрузка информации о новом видео.
    - Сохраняет информацию в БД.
    - Запускает фоновую задачу для генерации HLS и кеширования.
    """
    logger.info(f"Получен запрос на добавление видео: {video_in.title}")

    # Проверка, не существует ли уже видео с таким URL
    existing_video = await crud.get_video_by_original_url(db, str(video_in.original_url))
    if existing_video:
        logger.warning(f"Видео с URL {video_in.original_url} уже существует (ID: {existing_video.id})")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Видео с таким original_url уже существует."
        )

    # Создание записи в БД (пока без playlist_url)
    db_video = await crud.create_video(db=db, video=video_in)
    logger.info(f"Видео '{db_video.title}' (ID: {db_video.id}) создано в БД.")

    generated_playlist_url = tasks.generate_fake_hls_playlist(
        video_id=db_video.id,
        original_url=str(db_video.original_url)
    )
    logger.info(f"Предварительно сгенерирован HLS URL: {generated_playlist_url} для видео ID: {db_video.id}")

    # Обновляем видео в БД с URL плейлиста
    updated_db_video = await crud.update_video_playlist_url(
        db=db, video_id=db_video.id, playlist_url=generated_playlist_url
    )
    if not updated_db_video:  # На всякий случай, хотя видео только что создано
        logger.error(f"Не удалось обновить playlist_url для видео ID: {db_video.id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка обновления видео")

    background_tasks.add_task(
        tasks.process_new_video_tasks,
        video_db_id=updated_db_video.id,
        video_title=updated_db_video.title,
        video_original_url=str(updated_db_video.original_url),
        # Преобразуем datetime в строку, т.к. фоновая задача может быть в другом процессе (для Celery/RQ)
        # Для BackgroundTasks это менее критично, но хорошая практика.
        video_created_at=updated_db_video.created_at.isoformat(),
        video_updated_at=updated_db_video.updated_at.isoformat()
    )
    logger.info(f"Фоновые задачи для видео ID: {updated_db_video.id} добавлены в очередь.")

    return schemas.VideoCreateResponse(
        id=updated_db_video.id,
        title=updated_db_video.title,
        playlist_url=updated_db_video.playlist_url  # Теперь здесь есть URL
    )


@app.get("/api/videos/{video_id}", response_model=schemas.VideoResponse)
async def get_video_info(
        video_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о видео по ID.
    - Сначала проверяет кеш Redis.
    - Если в кеше нет, получает из БД и кеширует.
    """
    logger.info(f"Запрос на получение информации о видео ID: {video_id}")

    # 1. Попытка получить из кеша Redis
    cached_video = await cache.get_video_cache(video_id)
    if cached_video:
        logger.info(f"Видео ID: {video_id} найдено в кеше Redis.")
        return cached_video

    logger.info(f"Видео ID: {video_id} не найдено в кеше. Запрос к БД.")
    # 2. Если в кеше нет, получаем из БД
    db_video = await crud.get_video(db=db, video_id=video_id)
    if db_video is None:
        logger.warning(f"Видео ID: {video_id} не найдено в БД.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Видео не найдено")

    # Преобразование модели SQLAlchemy в схему Pydantic для ответа и кеширования
    video_response = schemas.VideoResponse.model_validate(db_video)  # Pydantic v2

    # 3. Сохранение в кеш Redis (в фоновом режиме, чтобы не замедлять ответ)
    await cache.set_video_cache(video_id, video_response)
    logger.info(f"Видео ID: {video_id} получено из БД и сохранено в кеш.")

    return video_response


# Дополнительный эндпоинт для проверки здоровья сервиса
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}
