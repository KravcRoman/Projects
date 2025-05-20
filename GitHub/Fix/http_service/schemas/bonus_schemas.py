from pydantic import BaseModel
from datetime import datetime


class BonusRequest(BaseModel):
    """
    Модель данных для запроса на вычисление бонусов.
    """
    transaction_amount: int  # Целое число
    timestamp: datetime      # Временная метка
    customer_status: str     # Строка