from datetime import date, datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from config.db import Base, engine
from pydantic import BaseModel

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    carrera_id = Column(Integer, ForeignKey("carreras.id", ondelete="CASCADE"), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    mes = Column(String(20), nullable=False)
    fecha_pago = Column(Date, nullable=False)

    user = relationship("User", back_populates="pagos")
    carrera = relationship("Carrera", back_populates="pagos")

    def __init__(self, user_id, carrera_id, monto, mes, fecha_pago=None):
        self.user_id = user_id
        self.carrera_id = carrera_id
        self.monto = monto
        self.mes = mes
        if fecha_pago is None:
            fecha_pago = datetime.now().date()
        self.fecha_pago = fecha_pago

#region Schemas PYDANTIC
class NuevoPago(BaseModel):
   carrera_id: int
   user_id: int
   monto: int
   mes: datetime.datetime
   fecha_pago: datetime.datetime = datetime.datetime.now()

class VerPagos(BaseModel):
    id: int
    carrera_id: int
    user_id: int
    monto: int
    mes: datetime.datetime
    fecha_pago: datetime.datetime

class EditarPago(BaseModel):
    user_id: Optional[int] = None
    carrera_id: Optional[int] = None
    monto: Optional[float] = None
    mes: Optional[str] = None

class PagoOut(BaseModel): # Modelo de salida para Pago
    id: int
    user_id: int
    carrera_id: int
    monto: int
    mes: datetime.datetime

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy
#endregion Schemas PYDANTIC
Session = sessionmaker(bind=engine)

session = Session()