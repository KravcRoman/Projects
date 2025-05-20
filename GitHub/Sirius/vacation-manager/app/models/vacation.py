import datetime
from sqlalchemy import Column, Integer, Date, DateTime, CheckConstraint, Index, func
from app.core.db import Base # Import Base from common db setup

class Vacation(Base):
    __tablename__ = "vacations"

    id = Column(Integer, primary_key=True, index=True) # Implicitly autoincrements with most DBs
    employee_id = Column(Integer, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False) # Use timezone=False for naive datetime

    # Constraint to ensure end_date is not before start_date
    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='chk_end_date_after_start_date'),
        # Index to speed up overlap checks and period queries
        Index('ix_vacations_period', 'start_date', 'end_date'),
        # Optional: Combined index for employee lookups + sorting
        Index('ix_vacations_employee_start_date', 'employee_id', 'start_date'),
    )

    def __repr__(self):
        return f"<Vacation(id={self.id}, employee_id={self.employee_id}, start='{self.start_date}', end='{self.end_date}')>"