"""
auth_service.py
---------------
Lógica de negocio para autenticación: registro y login.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash, verify_password, create_access_token
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister, UserLogin, Token


def register_user(db: Session, data: UserRegister) -> User:
    """
    Registra un nuevo usuario:
    1. Verifica que el email no exista.
    2. Hashea la contraseña.
    3. Guarda en la base de datos.
    """
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado.",
        )

    hashed_pwd = get_password_hash(data.password)

    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hashed_pwd,
        role=data.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, data: UserLogin) -> Token:
    """
    Autentica al usuario:
    1. Busca por email.
    2. Verifica la contraseña con bcrypt.
    3. Retorna un JWT.
    """
    user = db.query(User).filter(User.email == data.email).first()

    # Mensaje genérico para no revelar si el email existe
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de usuario inactiva.",
        )

    token = create_access_token(data={"sub": user.email, "role": user.role})
    return Token(access_token=token, token_type="bearer")
