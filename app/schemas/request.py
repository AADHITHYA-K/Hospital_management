from datetime import datetime
from pydantic import BaseModel


class RequestCreate(BaseModel):
    patient_id: int
    request_type: str
    priority: str | None = "Normal"


class RequestResponse(BaseModel):
    id: int
    patient_id: int
    request_type: str
    current_department: str
    status: str
    priority: str | None = "Normal"
    created_at: datetime | None = None

    model_config = {"from_attributes": True}