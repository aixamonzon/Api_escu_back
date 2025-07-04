from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey
from config.db import Base, engine
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import sessionmaker, relationship

class User(Base):
   __tablename__ = "usuarios"


   id = Column("id", Integer, primary_key=True)
   username = Column(String(50), nullable=False, unique=True)
   password = Column("password", String)
   id_userdetail = Column(Integer, ForeignKey("userdetails.id"))
   userdetail = relationship("UserDetail", backref="user", uselist=False)
   pagos = relationship("Pago", back_populates="user")
   carreras = relationship("UserCarrera", back_populates="user")

   def __init__(
       self,
       id,
       username,
       password,
   ):
       self.id = id
       self.username = username
       self.password = password

class UserDetail(Base):

   __tablename__ = "userdetails"

   id = Column("id", Integer, primary_key=True)
   dni = Column("dni", Integer)
   firstName = Column("firstName", String)
   lastName = Column("lastName", String)
   type = Column("type", String)
   email = Column("email", String(80), nullable=False, unique=True)

   def __init__(self, dni, firstName, lastName, type, email):
       self.dni = dni
       self.firstName = firstName
       self.lastName = lastName
       self.type = type
       self.email = email

# Borra las tablas en la base de datos
Base.metadata.drop_all(bind=engine)
# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

#region Schemas PYDANTIC
class InputUser(BaseModel):
   username: str
   password: str
   email: str
   dni: int
   firstName: str
   lastName: str
   type: str
   
class InputLogin(BaseModel):
    username: str
    password: str

class InputUserDetail(BaseModel):
   dni: int
   firstName: str
   lastName: str
   type: str
   email: str

class UserDetailUpdate(BaseModel):
    dni: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    type: Optional[str] = None
    email: Optional[str]  = None

class InputRegister(BaseModel):
   username: str
   password: str
   email: str
       
class UserDetailOut(BaseModel):
    email: str
    dni: int
    firstName: str
    lastName: str
    type: str

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    username: str
    userdetail: UserDetailOut  # 👈 Anidado

    class Config:
        orm_mode = True

#endregion

Session = sessionmaker(bind=engine)

session = Session()