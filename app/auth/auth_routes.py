"""
auth_routes.py
--------------
Endpoints de autenticación: /auth/register, /auth/login, /auth/me
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import auth_service
from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_active_user
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister, Token, UserPublicResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserPublicResponse,
    status_code=201,
    summary="Registrar nuevo usuario",
    description="Crea un usuario con contraseña segura (hasheada con bcrypt). "
                "La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula y un número.",
)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return auth_service.register_user(db, data)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autentica con email y contraseña. Retorna un JWT Bearer token para usar en rutas protegidas.",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Usa OAuth2PasswordRequestForm para compatibilidad con Swagger UI
    (el formulario pide 'username' y 'password', donde username = email).
    """
    from app.schemas.auth_schema import UserLogin
    data = UserLogin(email=form_data.username, password=form_data.password)
    return auth_service.login_user(db, data)


@router.get(
    "/me",
    response_model=UserPublicResponse,
    summary="Obtener usuario autenticado",
    description="Retorna los datos del usuario que envía el token JWT. No expone la contraseña.",
)
def me(current_user: User = Depends(get_current_active_user)):
    return current_user
