import datetime
from typing import List, Optional, Sequence
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vacation import Vacation
from app.schemas.vacation import VacationCreate

class CRUDVacation:
    async def check_overlap(
        self, db: AsyncSession, *, employee_id: int, start_date: datetime.date, end_date: datetime.date, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Checks if a given period overlaps with existing vacations for the employee,
        optionally excluding a specific vacation ID (useful for updates if implemented).
        """
        query = select(Vacation.id).where(
            Vacation.employee_id == employee_id,
            Vacation.start_date <= end_date, # Existing ends on or after new one starts
            Vacation.end_date >= start_date  # Existing starts on or before new one ends
        )
        if exclude_id is not None:
            query = query.where(Vacation.id != exclude_id)

        query = query.limit(1) # We only need existence check
        result = await db.execute(query)
        return result.scalars().first() is not None

    async def create(self, db: AsyncSession, *, obj_in: VacationCreate) -> Vacation:
        """Creates a new vacation record."""
        # Note: Overlap check should ideally happen in the API layer before calling create
        # or be part of a more complex service layer logic.
        # Adding it here for simplicity, but it mixes concerns slightly.

        # Overlap Check (moved to API layer is better practice)
        # has_overlap = await self.check_overlap(...)
        # if has_overlap:
        #    raise ValueError("Overlapping vacation period") # Or custom exception

        db_obj = Vacation(
            employee_id=obj_in.employee_id,
            start_date=obj_in.start_date,
            end_date=obj_in.end_date,
            # created_at is handled by the database default
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_employee(
        self, db: AsyncSession, *, employee_id: int, limit: int = 3
    ) -> Sequence[Vacation]:
        """Gets the latest vacations for a specific employee."""
        stmt = select(Vacation).where(
            Vacation.employee_id == employee_id
        ).order_by(Vacation.start_date.desc(), Vacation.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_period(
        self, db: AsyncSession, *, start_date_filter: datetime.date, end_date_filter: datetime.date
    ) -> Sequence[Vacation]:
        """Gets all vacations overlapping with the specified period."""
        stmt = select(Vacation).where(
            # Overlap condition: vacation starts before filter ends AND vacation ends after filter starts
            Vacation.start_date <= end_date_filter,
            Vacation.end_date >= start_date_filter
        ).order_by(Vacation.employee_id, Vacation.start_date)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get(self, db: AsyncSession, *, id: int) -> Optional[Vacation]:
        """Gets a single vacation by its ID using await db.get()."""
        # db.get is efficient for PK lookups
        return await db.get(Vacation, id)

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Vacation]:
        """Deletes a vacation by its ID."""
        db_obj = await db.get(Vacation, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return db_obj # Return the deleted object
        return None # Return None if not found

# Create a single instance of the CRUD class for convenient import
vacation = CRUDVacation()