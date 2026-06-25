"""
loan_routes.py
--------------
Gestión de préstamos con protección:
- GET: admin o support
- POST: usuario autenticado
- PATCH /return: admin o support
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_active_user, require_admin_or_support
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse
from app.services import loan_service
from app.models.user_model import User

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get(
    "/",
    response_model=list[LoanDetailResponse],
    summary="Listar préstamos",
    description="Requiere rol admin o support.",
)
def list_loans(
    status: Optional[str] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_support),
):
    return loan_service.get_all_loans(db, status, user_email, device_type)


@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Préstamos con detalle completo",
    description="Requiere rol admin o support.",
)
def loan_details(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_support),
):
    return loan_service.get_all_loans(db)


@router.get(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    summary="Obtener préstamo por ID",
    description="Requiere rol admin o support.",
)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_support),
):
    return loan_service.get_loan_by_id(db, loan_id)


@router.post(
    "/",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear préstamo",
    description="Cualquier usuario autenticado puede crear un préstamo.",
)
def create_loan(
    data: LoanCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return loan_service.create_loan(db, data)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanDetailResponse,
    summary="Devolver dispositivo",
    description="Requiere rol admin o support.",
)
def return_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_support),
):
    return loan_service.return_loan(db, loan_id)
