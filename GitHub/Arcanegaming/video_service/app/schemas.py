from pydantic import BaseModel, HttpUrl
from datetime import datetime

# Базовая схема для видео, общие поля
class VideoBase(BaseModel):
    title: str
    original_url: HttpUrl # Используем HttpUrl для валидации URL

# Схема для создания нового видео (то, что приходит в POST запросе)
class VideoCreate(VideoBase):
    pass

# Схема для ответа при создании видео
class VideoCreateResponse(BaseModel):
    id: int
    title: str
    playlist_url: HttpUrl | None = None # Может быть None, если еще не сгенерирован

    model_config = {
        "from_attributes": True # Ранее orm_mode = True
    }

# Схема для отображения информации о видео (то, что отдается в GET запросе)
class VideoResponse(BaseModel):
    id: int
    title: str
    original_url: HttpUrl
    playlist_url: HttpUrl | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True # Позволяет Pydantic работать с объектами SQLAlchemy
    }
