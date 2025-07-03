from sqlalchemy import Column, Integer, String, ForeignKey
from config.db import Base, engine
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, relationship




class User(Base):
   __tablename__ = "usuarios"


   id = Column("id", Integer, primary_key=True)
   username = Column(String(50), nullable=False, unique=True)
   password = Column("password", String)
   id_userdetail = Column(Integer, ForeignKey("userdetails.id"))
   userdetail = relationship("UserDetail", backref="user", uselist=False)

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




Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)





Session = sessionmaker(bind=engine)


session = Session()




class InputUser(BaseModel):
   id: int
   username: str
   password: str
   
class InputLogin(BaseModel):
   username: str
   password: str

class InputUser(BaseModel):
   username: str
   password: str
   email: EmailStr
   dni: int
   firstname: str
   lastname: str
   type: str