import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field, AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vacation Management Service"
    API_V1_STR: str = "/api/v1"

    # Database URL constructed from environment variables if not set directly
    POSTGRES_USER: str = Field(default="user", validation_alias='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(default="password", validation_alias='POSTGRES_PASSWORD')
    POSTGRES_DB: str = Field(default="vacations_db", validation_alias='POSTGRES_DB')
    POSTGRES_HOST: str = Field(default="db", validation_alias='POSTGRES_HOST')
    POSTGRES_PORT: str = Field(default="5432", validation_alias='POSTGRES_PORT')

    # Main database URL (prefer DATABASE_URL if set directly)
    DATABASE_URL: Optional[PostgresDsn] = Field(default=None, validation_alias='DATABASE_URL')

    # Test database URL (optional)
    TEST_DATABASE_URL: Optional[PostgresDsn] = Field(default=None, validation_alias='TEST_DATABASE_URL')

    # Allow configuring CORS (Cross-Origin Resource Sharing) if needed
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(default=[], validation_alias='BACKEND_CORS_ORIGINS')

    # Construct DATABASE_URL if not provided directly
    @property
    def assemble_db_connection(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=int(self.POSTGRES_PORT),
            path=f"/{self.POSTGRES_DB}",
        ))

    # Configuration loading
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True, # Match env var case exactly
        extra='ignore'
    )

settings = Settings()

# Ensure DATABASE_URL is set, either directly or assembled
if settings.DATABASE_URL is None:
    settings.DATABASE_URL = settings.assemble_db_connection # type: ignore