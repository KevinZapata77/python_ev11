from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.connection import Base


class Device(Base):
    """Tabla de dispositivos disponibles para préstamo."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False, index=True)
    device_type = Column(String(50), nullable=False)   # laptop, tablet, proyector, cámara, router, monitor
    brand = Column(String(100), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relación: un dispositivo puede aparecer en muchos préstamos históricos
    loans = relationship("Loan", back_populates="device")

    def __repr__(self) -> str:
        return f"<Device id={self.id} serial={self.serial_number!r}>"
