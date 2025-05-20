from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Video
from schemas import VideoCreate

async def get_video(db: AsyncSession, video_id: int) -> Video | None:
    """
    Получает видео по его ID.
    """
    result = await db.execute(select(Video).filter(Video.id == video_id))
    return result.scalars().first()

async def get_video_by_original_url(db: AsyncSession, original_url: str) -> Video | None:
    """
    Получает видео по его оригинальному URL.
    """
    result = await db.execute(select(Video).filter(Video.original_url == original_url))
    return result.scalars().first()

async def create_video(db: AsyncSession, video: VideoCreate) -> Video:
    """
    Создает новую запись о видео в базе данных.
    Начальное значение playlist_url будет None или пустым.
    """
    db_video = Video(
        title=video.title,
        original_url=str(video.original_url) # Преобразуем HttpUrl в строку для БД
    )
    db.add(db_video)
    await db.flush() # Чтобы получить ID до коммита
    await db.refresh(db_video) # Обновить объект db_video данными из БД (включая ID, created_at)
    return db_video

async def update_video_playlist_url(db: AsyncSession, video_id: int, playlist_url: str) -> Video | None:
    """
    Обновляет URL плейлиста для существующего видео.
    """
    video = await get_video(db, video_id)
    if video:
        video.playlist_url = playlist_url
        db.add(video) # SQLAlchemy отслеживает изменения, но add() не повредит
        await db.flush()
        await db.refresh(video)
    return video
