import asyncio
import logging
from schemas import VideoResponse
from cache import set_video_cache
from core.config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_fake_hls_playlist(video_id: int, original_url: str) -> str:
    """
    Генерирует фейковый HLS плейлист (.m3u8).
    В реальном приложении здесь будет логика с использованием ffmpeg или подобного.
    """
    logger.info(f"Начало генерации HLS для видео ID: {video_id}")

    playlist_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
{settings.BASE_URL}/media/video_{video_id}_segment_0.ts
#EXTINF:10.0,
{settings.BASE_URL}/media/video_{video_id}_segment_1.ts
#EXTINF:10.0,
{settings.BASE_URL}/media/video_{video_id}_segment_2.ts
#EXT-X-ENDLIST"""

    # URL будет сформирован на основе этого пути.
    playlist_url = f"{settings.BASE_URL}/hls/{video_id}.m3u8"

    logger.info(f"HLS плейлист для видео ID: {video_id} сгенерирован: {playlist_url}")
    return playlist_url # Возвращаем URL к "сгенерированному" плейлисту


async def process_new_video_tasks(video_db_id: int, video_title: str, video_original_url: str, video_created_at: str, video_updated_at: str):
    """
    Асинхронная обертка для выполнения всех фоновых задач после создания видео.
    """
    logger.info(f"Запуск фоновых задач для видео ID: {video_db_id}, Title: {video_title}")

    playlist_url_generated = generate_fake_hls_playlist(video_db_id, video_original_url)
    logger.info(f"Сгенерирован HLS плейлист: {playlist_url_generated} для видео ID: {video_db_id}")

    video_data_for_cache = VideoResponse(
        id=video_db_id,
        title=video_title,
        original_url=video_original_url,
        playlist_url=playlist_url_generated,
        created_at=video_created_at,
        updated_at=video_updated_at
    )
    await set_video_cache(video_db_id, video_data_for_cache)
    logger.info(f"Видео ID: {video_db_id} записано в кеш Redis.")

    # Дополнительное логирование
    logger.info(f"Фоновая обработка для видео ID: {video_db_id} завершена.")
