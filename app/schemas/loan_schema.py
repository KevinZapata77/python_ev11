from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime


class LoanCreate(BaseModel):
    user_id: int = Field(..., examples=[1])
    device_id: int = Field(..., examples=[1])


class LoanUpdate(BaseModel):
    status: Literal["active", "returned", "overdue"]


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    status: str


# ── Respuesta detallada con datos relacionados ─────────────────────────────────
class UserBasic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class DeviceBasic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    serial_number: str
    device_type: str


class LoanDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    loan_date: datetime
    return_date: Optional[datetime]
    user: UserBasic
    device: DeviceBasic
