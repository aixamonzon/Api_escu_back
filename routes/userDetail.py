from fastapi import APIRouter
from models.userDetail import session, UserDetail, InputUserDetail


userDetail = APIRouter()


@userDetail.get("/userdetail/all")
def get_userDetails():
   try:
       return session.query(UserDetail).all()
   except Exception as e:
       print(e)


@userDetail.post("/userdetail/add")
def add_usuarDetail(userDet: InputUserDetail):
   usuNuevo = UserDetail(
   userDet.dni, userDet.firstName, userDet.lastName, userDet.type,           userDet.email
   )
   session.add(usuNuevo)
   session.commit()
   return "usuario detail agregado"
