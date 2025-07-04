from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, sessionmaker
from config.db import Base, engine
from pydantic import BaseModel
from typing import Optional

class UserCarrera(Base):
    __tablename__ = "user_carrera"
    __table_args__ = (UniqueConstraint('user_id', 'carrera_id', name='uq_user_carrera'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    carrera_id = Column(Integer, ForeignKey("carreras.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="carreras")
    carrera = relationship("Carrera", back_populates="users")


# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

#region Schemas PYDANTIC
class UserCarreraOut(BaseModel):
    id: int
    user_id: int
    carrera_id: int

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy

class NuevaUserCarrera(BaseModel):
    user_id: int
    carrera_id: int

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy


class EditarUserCarrera(BaseModel):
    user_id: Optional[int] = None
    carrera_id: Optional[int] = None

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy

#endregion Schemas PYDANTIC

Session = sessionmaker(bind=engine)

session = Session()