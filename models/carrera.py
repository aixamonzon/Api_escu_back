from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from config.db import Base, engine
from pydantic import BaseModel

class Carrera(Base):
    __tablename__ = "carreras"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)

    users = relationship("UserCarrera", back_populates="carrera")
    pagos = relationship("Pago", back_populates="carrera")

    def __init__(self, nombre):
        self.nombre = nombre

#region Schemas PYDANTIC
class CarreraOut(BaseModel):
    id: int
    nombre: str

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy
        arbitrary_types_allowed = True  # Permite usar tipos arbitrarios como SQLAlchemy models

class NuevaCarrera(BaseModel):
    nombre: str

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy
        arbitrary_types_allowed = True  # Permite usar tipos arbitrarios como SQLAlchemy models

class EditarCarrera(BaseModel):
    nombre: str

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy
        arbitrary_types_allowed = True  # Permite usar tipos arbitrarios como SQLAlchemy models
#endregion Schemas PYDANTIC

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)