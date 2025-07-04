from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from config.db import Base, engine
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional
import datetime

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    carrera_id = Column(Integer, ForeignKey("carreras.id", ondelete="CASCADE"), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    mes = Column(String(2), nullable=False)
    fecha_pago = Column(Date, nullable=False, default=func.current_date())  # Usa la fecha del día actual

    user = relationship("User", back_populates="pagos")
    carrera = relationship("Carrera", back_populates="pagos")

#region Schemas PYDANTIC
class NuevoPago(BaseModel):
    monto: float = Field(..., gt=0)
    mes: str = Field(..., pattern="^(0[1-9]|1[0-2])$", description="Mes entre 01 y 12")
    user_id: int
    carrera_id: int

class VerPago(BaseModel):
    id: int
    user_id: int
    carrera_id: int
    monto: float
    mes: str
    fecha_pago: datetime.date

    class Config:
        orm_mode = True

class EditarPago(BaseModel):
    monto: Optional[float] = Field(None, gt=0)
    mes: Optional[str] = Field(None, pattern="^(0[1-9]|1[0-2])$")
    carrera_id: Optional[int]
#endregion Schemas PYDANTIC

Session = sessionmaker(bind=engine)
session = Session()