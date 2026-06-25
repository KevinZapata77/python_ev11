from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import datetime, timezone
from app.models.loan_model import Loan
from app.models.device_model import Device
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate


def get_all_loans(
    db: Session,
    status: str | None = None,
    user_email: str | None = None,
    device_type: str | None = None,
) -> list[Loan]:
    query = db.query(Loan).options(joinedload(Loan.user), joinedload(Loan.device))
    if status:
        query = query.filter(Loan.status == status)
    if user_email:
        query = query.join(User).filter(User.email.ilike(f"%{user_email}%"))
    if device_type:
        query = query.join(Device).filter(Device.device_type == device_type)
    return query.all()


def get_loan_by_id(db: Session, loan_id: int) -> Loan:
    loan = (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.id == loan_id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan


def create_loan(db: Session, data: LoanCreate) -> Loan:
    # Validar usuario
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar dispositivo y disponibilidad
    device = db.query(Device).filter(Device.id == data.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if not device.is_available:
        raise HTTPException(status_code=409, detail="El dispositivo no está disponible")

    # Crear préstamo y marcar dispositivo como no disponible
    loan = Loan(user_id=data.user_id, device_id=data.device_id, status="active")
    device.is_available = False
    db.add(loan)
    db.commit()
    db.refresh(loan)
    # Cargar relaciones para la respuesta
    return get_loan_by_id(db, loan.id)


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = get_loan_by_id(db, loan_id)
    if loan.status == "returned":
        raise HTTPException(status_code=409, detail="El préstamo ya fue devuelto")

    loan.status = "returned"
    loan.return_date = datetime.now(timezone.utc)
    loan.device.is_available = True
    db.commit()
    db.refresh(loan)
    return get_loan_by_id(db, loan_id)


def get_loans_by_user(db: Session, user_id: int) -> list[Loan]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.user_id == user_id)
        .all()
    )


def get_loans_by_device(db: Session, device_id: int) -> list[Loan]:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.device_id == device_id)
        .all()
    )
