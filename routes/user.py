from fastapi import APIRouter
from fastapi.responses import JSONResponse
from psycopg2 import IntegrityError
from models.user import session, InputUser, User, InputLogin, InputUserDetail
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




@user.get("/users/login/{n}")
def get_users_id(user: InputLogin):
    try:
        # Buscar el usuario por nombre de usuario
        res = session.query(User).filter(User.username == user.username).first()
        
        # Verificar si el usuario fue encontrado y si la contraseña coincide
        if res and res.password == user.password:
            return res
        
        # Retornar None si no coincide la contraseña o no se encontró el usuario
        return None

    except Exception as e:
        # Mostrar el error en consola para depuración
        print(f"Error al intentar iniciar sesión: {e}")


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