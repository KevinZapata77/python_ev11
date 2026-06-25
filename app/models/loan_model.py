from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.connection import Base


class Loan(Base):
    """Tabla de préstamos: relaciona un usuario con un dispositivo."""

    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    loan_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    return_date = Column(DateTime, nullable=True)          # None = aún no devuelto
    status = Column(String(20), nullable=False, default="active")  # active | returned | overdue

    # Relaciones
    user = relationship("User", back_populates="loans")
    device = relationship("Device", back_populates="loans")

    def __repr__(self) -> str:
        return f"<Loan id={self.id} user={self.user_id} device={self.device_id} status={self.status!r}>"
