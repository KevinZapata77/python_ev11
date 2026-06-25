from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceUpdate, DevicePatch


def get_all_devices(
    db: Session,
    device_type: str | None = None,
    is_available: bool | None = None,
    brand: str | None = None,
    search: str | None = None,
) -> list[Device]:
    query = db.query(Device)
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if is_available is not None:
        query = query.filter(Device.is_available == is_available)
    if brand:
        query = query.filter(Device.brand.ilike(f"%{brand}%"))
    if search:
        query = query.filter(Device.name.ilike(f"%{search}%"))
    return query.all()


def get_device_by_id(db: Session, device_id: int) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device


def create_device(db: Session, data: DeviceCreate) -> Device:
    if db.query(Device).filter(Device.serial_number == data.serial_number).first():
        raise HTTPException(status_code=400, detail="El número de serie ya existe")
    device = Device(**data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device_id: int, data: DeviceUpdate) -> Device:
    device = get_device_by_id(db, device_id)
    existing = db.query(Device).filter(Device.serial_number == data.serial_number).first()
    if existing and existing.id != device_id:
        raise HTTPException(status_code=400, detail="El número de serie ya existe")
    for field, value in data.model_dump().items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def patch_device(db: Session, device_id: int, data: DevicePatch) -> Device:
    device = get_device_by_id(db, device_id)
    changes = data.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    if "serial_number" in changes:
        existing = db.query(Device).filter(Device.serial_number == changes["serial_number"]).first()
        if existing and existing.id != device_id:
            raise HTTPException(status_code=400, detail="El número de serie ya existe")
    for field, value in changes.items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> None:
    device = get_device_by_id(db, device_id)
    db.delete(device)
    db.commit()
