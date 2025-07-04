from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey
from config.db import Base, engine
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import sessionmaker, relationship
from models.userCarrera import UserCarrera

class User(Base):
   __tablename__ = "users"


   id = Column("id", Integer, primary_key=True)
   username = Column(String(50), nullable=False, unique=True)
   password = Column("password", String)

   user_detail = relationship("UserDetail", back_populates="user", uselist=False, cascade="all, delete")
   carreras = relationship("UserCarrera", back_populates="user", cascade="all, delete")
   pagos = relationship("Pago", back_populates="user", cascade="all, delete")

class UserDetail(Base):

   __tablename__ = "user_detail"
   
   id = Column(Integer, primary_key=True, autoincrement=True)
   user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
   dni = Column(String(20), unique=True, nullable=False)
   first_name = Column(String(100), nullable=False)
   last_name = Column(String(100), nullable=False)
   type = Column(String(20), nullable=False) 
   email = Column(String(100), unique=True, nullable=False)

    # Relación inversa
   user = relationship("User", back_populates="user_detail")

# Borra las tablas en la base de datos
#Base.metadata.drop_all(bind=engine)
# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

#region Schemas PYDANTIC
class InputUser(BaseModel):
   username: str
   password: str
   email: str
   dni: str
   first_name: str
   last_name: str
   type: str
   
class InputLogin(BaseModel):
    username: str
    password: str

class InputUserDetail(BaseModel):
   dni: str
   first_name: str
   last_name: str
   type: str
   email: str

class UserDetailUpdate(BaseModel):
    dni: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    type: Optional[str] = None
    email: Optional[str]  = None

class InputRegister(BaseModel):
   username: str
   password: str
   email: str
       
class UserDetailOut(BaseModel):
    email: str
    dni: str
    first_name: str
    last_name: str
    type: str

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    username: str
    user_detail: UserDetailOut  # Anidado detalle de usuario

    class Config:
        orm_mode = True

#endregion

Session = sessionmaker(bind=engine)

session = Session()