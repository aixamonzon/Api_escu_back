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
