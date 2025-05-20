import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationInfo

# Base schema with common fields and validation logic
class VacationBase(BaseModel):
    employee_id: int = Field(..., gt=0, description="Employee ID (must be positive)")
    start_date: datetime.date = Field(..., description="Vacation start date (YYYY-MM-DD)")
    end_date: datetime.date = Field(..., description="Vacation end date (YYYY-MM-DD)")

    # Pydantic V2 validator using field_validator
    @field_validator('end_date')
    @classmethod
    def end_date_must_be_after_start_date(cls, v: datetime.date, info: ValidationInfo):
        # info.data contains the partially validated model data
        if info.data and 'start_date' in info.data and isinstance(info.data['start_date'], datetime.date):
            if v < info.data['start_date']:
                raise ValueError('End date must be on or after start date')
        elif not (info.data and 'start_date' in info.data):
             # Should not happen if start_date is mandatory, but good practice
             pass # Or raise if start_date could be missing validation yet
        return v

# Schema for creating a new vacation (input)
class VacationCreate(VacationBase):
    # No additional fields needed for creation beyond the base
    pass

# Schema for reading/returning vacation data (output)
class Vacation(VacationBase):
    id: int = Field(..., description="Unique Vacation ID")
    created_at: datetime.datetime = Field(..., description="Timestamp when the record was created")

    # Pydantic V2 configuration to work with ORM models
    model_config = ConfigDict(
        from_attributes=True, # Enable ORM mode (reads attributes from model instances)
    )