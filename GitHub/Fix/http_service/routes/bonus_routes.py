from fastapi import APIRouter, HTTPException, status

from http_service.schemas import bonus_schemas
from services import bonus_service

router = APIRouter()


@router.post("/calculate-bonus", response_model=dict)
async def calculate_bonus(request: bonus_schemas.BonusRequest) -> dict:
    """
    Вычисляет бонусы на основе заданных правил.
    """
    try:
        return bonus_service.calculate_bonus(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

