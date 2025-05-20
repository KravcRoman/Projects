import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas import Vacation, VacationCreate # Import schemas
from app.crud import vacation as crud_vacation # Import CRUD operations instance

# Create router instance
router = APIRouter()

@router.post(
    "/", # Endpoint relative to router prefix (e.g., /api/v1/vacations/)
    response_model=Vacation,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить новый отпуск",
    description="Добавляет информацию об отпуске сотрудника. Проверяет пересечения."
)
async def add_vacation(
    vacation_in: VacationCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check for overlaps before creating
    has_overlap = await crud_vacation.check_overlap(
        db,
        employee_id=vacation_in.employee_id,
        start_date=vacation_in.start_date,
        end_date=vacation_in.end_date
    )
    if has_overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vacation period overlaps with an existing vacation for this employee."
        )

    # If no overlap, proceed to create
    created_vacation = await crud_vacation.create(db=db, obj_in=vacation_in)
    return created_vacation

@router.get(
    "/",
    response_model=List[Vacation],
    summary="Получить отпуска за период",
    description="Получает список всех отпусков, которые пересекаются с указанным периодом."
)
async def read_vacations_by_period(
    start_date: datetime.date = Query(..., description="Начало периода фильтрации (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="Конец периода фильтрации (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Start date for filtering cannot be after end date."
        )
    vacations_list = await crud_vacation.get_by_period(
        db=db, start_date_filter=start_date, end_date_filter=end_date
    )
    return vacations_list

@router.get(
    "/employees/{employee_id}",
    response_model=List[Vacation],
    summary="Получить последние отпуска сотрудника",
    description="Получает список N последних (по дате начала) отпусков для указанного сотрудника."
)
async def read_employee_vacations(
    employee_id: int = Path(..., gt=0, description="ID сотрудника"),
    limit: int = Query(3, gt=0, le=100, description="Количество последних отпусков (по умолч. 3)"),
    db: AsyncSession = Depends(get_db)
):
    vacations_list = await crud_vacation.get_by_employee(
        db=db, employee_id=employee_id, limit=limit
    )
    # Returning an empty list if employee has no vacations is appropriate
    return vacations_list

@router.delete(
    "/{vacation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить отпуск",
    description="Удаляет информацию об отпуске по его уникальному ID."
)
async def delete_vacation(
    vacation_id: int = Path(..., gt=0, description="ID удаляемого отпуска"),
    db: AsyncSession = Depends(get_db)
):
    deleted_vacation = await crud_vacation.remove(db=db, id=vacation_id)
    if deleted_vacation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacation with id {vacation_id} not found."
        )
    # No response body needed for 204
    return None