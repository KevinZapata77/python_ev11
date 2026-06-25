"""
user_routes.py
--------------
CRUD de usuarios. Rutas protegidas por JWT.
"""
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_active_user, require_admin
from app.schemas.user_schema import UserUpdate, UserPatch, UserResponse
from app.services import user_service
from app.models.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Retorna todos los usuarios. Requiere autenticación.",
)
def list_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    order_by: str = "id",
    order_dir: str = "asc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),   # protección: usuario autenticado
):
    return user_service.get_all_users(db, role, is_active, order_by, order_dir)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Requiere autenticación.",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return user_service.get_user_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo (PUT)",
    description="Solo admin puede actualizar completamente un usuario.",
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.update_user(db, user_id, data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcial (PATCH)",
    description="Solo admin puede hacer actualizaciones parciales.",
)
def patch_user(
    user_id: int,
    data: UserPatch,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.patch_user(db, user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Solo admin puede eliminar usuarios.",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user_service.delete_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
