from sqlalchemy  import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    original_url = Column(String, nullable=False, unique=True) # URL исходного видео файла
    playlist_url = Column(String, nullable=True) # URL сгенерированного HLS плейлиста
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}')>"
