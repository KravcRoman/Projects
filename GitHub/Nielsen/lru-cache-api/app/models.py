from pydantic import BaseModel, Field, PositiveInt, Json # Json нужен для Any
from typing import Any, Optional, List

class CachePutRequest(BaseModel):
    """Модель для запроса PUT /cache/{key}."""
    value: Any # Позволяем хранить любые JSON-совместимые значения
    ttl: Optional[PositiveInt] = Field(default=None, description="Time-To-Live в секундах")

class CacheStatsResponse(BaseModel):
    """Модель для ответа GET /cache/stats."""
    size: int = Field(..., description="Текущее количество элементов в кэше")
    capacity: int = Field(..., description="Максимальная емкость кэша")
    items: List[str] = Field(..., description="Список ключей в порядке LRU (от новых к старым)")

class ErrorDetail(BaseModel):
    """Стандартная модель ошибки FastAPI при валидации."""
    loc: List[str | int]
    msg: str
    type: str

class ValidationErrorResponse(BaseModel):
    """Модель для ответа с ошибкой валидации (422)."""
    detail: List[ErrorDetail]

class NotFoundErrorResponse(BaseModel):
    """Модель для ответа 404."""
    message: str = "Key not found or expired"