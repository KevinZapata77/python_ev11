"""
user_schema.py
--------------
Schemas Pydantic v2 para el recurso /users.
Nota: UserCreate ya no incluye password (el registro va por /auth/register).
"""
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

ROLES = Literal["admin", "support", "user"]


class UserUpdate(BaseModel):
    """Actualización completa de un usuario (PUT)."""
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    role: ROLES
    is_active: bool


class UserPatch(BaseModel):
    """Actualización parcial de un usuario (PATCH)."""
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[ROLES] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Respuesta completa de un usuario (nunca expone hashed_password)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
