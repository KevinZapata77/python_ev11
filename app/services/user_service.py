from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from fastapi import HTTPException
from app.models.user_model import User
from app.schemas.user_schema import UserUpdate, UserPatch


def get_all_users(db, role=None, is_active=None, order_by="id", order_dir="asc"):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    col = getattr(User, order_by, User.id)
    query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    return query.all()


def get_user_by_id(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email).first()


def update_user(db, user_id, data: UserUpdate):
    user = get_user_by_id(db, user_id)
    existing = get_user_by_email(db, data.email)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=400, detail="El email ya está en uso")
    for field, value in data.model_dump().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def patch_user(db, user_id, data: UserPatch):
    user = get_user_by_id(db, user_id)
    changes = data.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    if "email" in changes:
        existing = get_user_by_email(db, changes["email"])
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="El email ya está en uso")
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db, user_id):
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()