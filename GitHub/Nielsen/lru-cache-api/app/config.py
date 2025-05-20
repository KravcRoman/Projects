import os
from pydantic import Field, PositiveInt # Используем старый Field для совместимости с settings
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения."""
    # Используем переменную окружения CACHE_CAPACITY
    # Значение по умолчанию - 10, если переменная не установлена
    cache_capacity: PositiveInt = Field(default=10, validation_alias='CACHE_CAPACITY')

    # Pydantic V2 style model_config
    model_config = SettingsConfigDict(
        env_file='.env',          # Загружать переменные из .env файла
        env_file_encoding='utf-8',
        extra='ignore'            # Игнорировать лишние переменные окружения
    )

# Создаем экземпляр настроек, который будет использоваться в приложении
settings = Settings()

# Проверка при импорте, что capacity > 0 (хотя PositiveInt уже это делает)
if settings.cache_capacity <= 0:
     raise ValueError("CACHE_CAPACITY must be a positive integer")

print(f"Cache capacity loaded: {settings.cache_capacity}")
