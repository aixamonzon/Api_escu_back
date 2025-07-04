from fastapi import APIRouter
from fastapi.responses import JSONResponse
from psycopg2 import IntegrityError
from models.user import UserDetail, session, InputUser, User, InputLogin, InputUserDetail
from security.auth import create_access_token, get_current_user
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import (
   joinedload,
)

user = APIRouter()


@user.get("/")
def welcome():
   return "Bienvenido!!"


@user.get("/users/all")
def obtener_usuario_detalle():
  try:
      # Carga los detalles del usuario con unión
      usuarios = session.query(User).options(joinedload(User.userdetail)).all()
      # Convierte los usuarios en una lista de diccionarios
      usuarios_con_detalles = []
      for usuario in usuarios:
          usuario_con_detalle = {
              "id": usuario.id,
              "username": usuario.username,
              "email": usuario.userdetail.email,
              "dni": usuario.userdetail.dni,
              "first_name": usuario.userdetail.first_name,
              "last_name": usuario.userdetail.last_name,
              "type": usuario.userdetail.type,
          }
          usuarios_con_detalles.append(usuario_con_detalle)

      return JSONResponse(status_code=200, content=usuarios_con_detalles)
  except Exception as e:
      print("Error al obtener usuarios:", e)
      return JSONResponse(
          status_code=500, content={"detail": "Error al obtener usuarios"}
      )


@user.post("/users/login")
def login_post(userIn: InputLogin):
   try:
       user = session.query(User).filter(User.username == userIn.username).first()
       if not user.password == userIn.password:
           return JSONResponse(
               status_code=401,
               content={
                   "success": False,
                   "message": "Usuario y/o password incorrectos!",
               },
           )
       else:
           authDat = create_access_token(user)
           if not authDat:
               return JSONResponse(
                   status_code=401,
                   content={
                       "success": False,
                       "message": "Error de generación de token!",
                   },
               )
           else:
               return JSONResponse(
                   status_code=200, content={"success": True, "token": authDat}
               )


   except Exception as e:
       print(e)
       return JSONResponse(
           status_code=500,
           content={
               "success": False,
               "message": "Error interno del servidor",
           },
       )



@user.post("/users/add")
def crear_usuario(user: InputUser):
    try:
       if validate_username(user.username):
           if validate_email(user.email):
               newUser = User(
                   user.username,
                   user.password,
               )
               newUserDetail = UserDetail(
                   user.dni, user.firstname, user.lastname, user.type, user.email
               )
               newUser.userdetail = newUserDetail
               session.add(newUser)
               session.commit()
               return "usuario agregado"
           else:
               return "el email ya existe"
       else:
           return "el usuario ya existe"
    except IntegrityError as e:
       # Suponiendo que el msj de error contiene "username" para el campo duplicado
       if "username" in str(e):
           return JSONResponse(
               status_code=400, content={"detail": "Username ya existe"}
           )
       else:
           # Maneja otros errores de integridad
           print("Error de integridad inesperado:", e)
           return JSONResponse(
               status_code=500, content={"detail": "Error al agregar usuario"}
           )
    except Exception as e:
       session.rollback()
       print("Error inesperado:", e)
       return JSONResponse(
           status_code=500, content={"detail": "Error al agregar usuario"}
       )
    finally:
       session.close()

@user.get("/userdetail/all")
def get_userDetails():
   try:
       return session.query(UserDetail).all()
   except Exception as e:
       print(e)

@user.post("/userdetail/add")
def add_usuarDetail(userDet: InputUserDetail):
   usuNuevo = UserDetail(
   userDet.dni, userDet.firstName, userDet.lastName, userDet.type,           userDet.email
   )
   session.add(usuNuevo)
   session.commit()
   return "usuario detail agregado"

def validate_username(value):
   existing_user = session.query(User).filter(User.username == value).first()
   session.close()
   if existing_user:
       ##raise ValueError("Username already exists")
       return None
   else:
       return value

def validate_email(value):
   existing_email = session.query(UserDetail).filter(UserDetail.email == value).first()
   session.close()
   if existing_email:
       ##raise ValueError("Username already exists")
       return None
   else:
       return value
