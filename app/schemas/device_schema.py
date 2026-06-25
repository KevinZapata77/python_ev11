from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime

DEVICE_TYPES = Literal["laptop", "tablet", "proyector", "camara", "router", "monitor"]


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., min_length=3, max_length=100, examples=["LEN-2024-001"])
    device_type: DEVICE_TYPES = Field(..., examples=["laptop"])
    brand: Optional[str] = Field(default=None, max_length=100, examples=["Lenovo"])
    is_available: bool = Field(default=True)


class DeviceUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    serial_number: str = Field(..., min_length=3, max_length=100)
    device_type: DEVICE_TYPES
    brand: Optional[str] = Field(default=None, max_length=100)
    is_available: bool


class DevicePatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    serial_number: Optional[str] = Field(default=None, min_length=3, max_length=100)
    device_type: Optional[DEVICE_TYPES] = None
    brand: Optional[str] = None
    is_available: Optional[bool] = None


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serial_number: str
    device_type: str
    brand: Optional[str]
    is_available: bool
    created_at: datetime
