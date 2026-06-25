"""
auth_schema.py
--------------
Schemas Pydantic v2 para registro, login y respuesta de tokens.
"""
import re
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

ROLES = Literal["admin", "support", "user"]


class UserRegister(BaseModel):
    """Schema para registrar un nuevo usuario."""

    name: str = Field(..., min_length=3, max_length=100, examples=["Ana Pérez"])
    email: EmailStr = Field(..., examples=["ana@sena.edu.co"])
    password: str = Field(..., min_length=8, examples=["MiClave123"])
    role: ROLES = Field(default="user", examples=["user"])

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Valida que la contraseña cumpla los requisitos mínimos de seguridad:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Sin espacios en blanco
        """
        if " " in v:
            raise ValueError("La contraseña no puede contener espacios.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe tener al menos una mayúscula.")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe tener al menos una minúscula.")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe tener al menos un número.")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return v.strip()


class UserLogin(BaseModel):
    """Schema para iniciar sesión."""

    email: EmailStr = Field(..., examples=["ana@sena.edu.co"])
    password: str = Field(..., examples=["MiClave123"])


class Token(BaseModel):
    """Schema de respuesta al hacer login."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos extraídos del token JWT."""

    email: str | None = None
    role: str | None = None


class UserPublicResponse(BaseModel):
    """Respuesta pública del usuario (SIN hashed_password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    is_active: bool
