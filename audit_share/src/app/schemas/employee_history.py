from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmployeeHistoryResponse(BaseModel):

    id: int

    employee_id: int

    action: str

    old_value: str | None = None

    new_value: str | None = None

    changed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
