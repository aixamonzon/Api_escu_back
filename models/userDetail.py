from config.db import engine, Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel, EmailStr




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


Base.metadata.drop_all(bind=engine) # Ojo, dropeará todas las BD primero
Base.metadata.create_all(bind=engine)


Session = sessionmaker(bind=engine)  # creo una clase session
session = Session()


class InputUser(BaseModel):
   username: str
   password: str
   email: EmailStr
   dni: int
   firstname: str
   lastname: str
   type: str