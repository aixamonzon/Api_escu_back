from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from psycopg2 import IntegrityError
from models.user import UserDetail, session, InputUser, User, InputLogin, InputUserDetail, InputAlumnoRegistro, UserUpdateAdmin, AlumnoCompletarRegistro, PasswordChange, AlumnoOut
from security.auth import crear_token, obtener_usuario_actual
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import (
   joinedload,
)
from security.security import verificar_password, hash_password
from security.dependencies import solo_admin, solo_alumno

user = APIRouter()


@user.get("/")
def welcome():
   return "Bienvenido!!"


@user.get("/users/all", dependencies=[Depends(solo_admin)]) # Solo accesible para administradores
def obtener_usuario_detalle():
  try:
      # Carga los detalles del usuario con unión
      usuarios = session.query(User).options(joinedload(User.user_detail)).all()
      # Convierte los usuarios en una lista de diccionarios
      usuarios_con_detalles = []
      for usuario in usuarios:
          usuario_con_detalle = {
              "id": usuario.id,
              "username": usuario.username,
              "email": usuario.user_detail.email,
              "dni": usuario.user_detail.dni,
              "first_name": usuario.user_detail.first_name,
              "last_name": usuario.user_detail.last_name,
              "type": usuario.user_detail.type,
          }
          usuarios_con_detalles.append(usuario_con_detalle)

      return JSONResponse(status_code=200, content=usuarios_con_detalles)
  except Exception as e:
      print("Error al obtener usuarios:", e)
      return JSONResponse(
          status_code=500, content={"detail": "Error al obtener usuarios"}
      )

@user.get("/users/alumnos", response_model=list[AlumnoOut])
def obtener_usuarios_alumnos(
    payload=Depends(obtener_usuario_actual),
):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden ver esta información")

    alumnos = session.query(User).options(joinedload(User.user_detail)) \
        .join(UserDetail) \
        .filter(UserDetail.type == "alumno").all()

    # Pydantic se encarga de convertir desde el modelo con orm_mode=True
    return [
        AlumnoOut(
            id=alumno.id,
            username=alumno.username,
            dni=alumno.user_detail.dni,
            firstname=alumno.user_detail.first_name,
            lastname=alumno.user_detail.last_name,
            email=alumno.user_detail.email,
            type=alumno.user_detail.type,
        )
        for alumno in alumnos
    ]

@user.post("/users/login")
def login_post(userIn: InputLogin):
   try:
        user = session.query(User).filter(User.username == userIn.username).first()
        if not user or not verificar_password(userIn.password, user.password):
           # Si el usuario no existe o la contraseña es incorrecta
           raise HTTPException(
               status_code=401,
               detail="Credenciales inválidas",
           )
         # Si las credenciales son correctas, crea el token
        token = crear_token(user)
        return {"success": True, "token": token}

   except Exception as e:
       print("Error en login:", e)
       return JSONResponse(
           status_code=500,
           content={
               "success": False,
               "message": "Error interno del servidor",
           },
       )

@user.post("/users/register/admin")
def crear_usuario_admin(user: InputUser, payload=Depends(obtener_usuario_actual)):
    # Solo admin puede crear usuarios con todos los datos
    if payload.get("type") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    if not validate_username(user.username):
        raise HTTPException(status_code=400, detail="El username ya existe")
    if not validate_email(user.email):
        raise HTTPException(status_code=400, detail="El email ya existe")

    try:
        hashed_pw = hash_password(user.password)
        newUser = User(username=user.username, password=hashed_pw)
        newUserDetail = UserDetail(
            dni=user.dni,
            first_name=user.first_name,
            last_name=user.last_name,
            type=user.type,
            email=user.email,
        )
        newUser.user_detail = newUserDetail
        session.add(newUser)
        session.commit()
        return {"success": True, "message": "Usuario creado"}
    except Exception as e:
        print("Error al crear usuario:", e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al crear usuario")
    finally:
        session.close()

@user.put("/users/{user_id}/update")
def actualizar_usuario_admin(
    user_id: int,
    datos: UserUpdateAdmin,
    payload=Depends(obtener_usuario_actual),
):
    # Sólo admin
    if payload.get("type") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar username y email si vienen para evitar duplicados
    if datos.username and datos.username != user.username:
        if not validate_username(datos.username):
            raise HTTPException(status_code=400, detail="El username ya existe")
        user.username = datos.username

    if datos.email and datos.email != user.user_detail.email:
        if not validate_email(datos.email):
            raise HTTPException(status_code=400, detail="El email ya existe")
        user.user_detail.email = datos.email

    # Actualizar otros campos si vienen
    if datos.dni:
        user.user_detail.dni = datos.dni
    if datos.first_name:
        user.user_detail.first_name = datos.first_name
    if datos.last_name:
        user.user_detail.last_name = datos.last_name
    if datos.type:
        user.user_detail.type = datos.type

    session.commit()
    session.close()
    return {"success": True, "message": "Usuario actualizado"}

@user.post("/users/register/alumno")
def crear_usuario_alumno(user: InputAlumnoRegistro):
    if not validate_username(user.username):
        raise HTTPException(status_code=400, detail="El username ya existe")
    if not validate_email(user.email):
        raise HTTPException(status_code=400, detail="El email ya existe")

    try:
        hashed_pw = hash_password(user.password)
        newUser = User(username=user.username, password=hashed_pw)
        newUserDetail = UserDetail(
            dni="",  # Vacío hasta completar registro
            first_name="",
            last_name="",
            type="alumno",
            email=user.email,
        )
        newUser.user_detail = newUserDetail
        session.add(newUser)
        session.commit()
        return {"success": True, "message": "Usuario alumno creado"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al crear usuario alumno")
    finally:
        session.close()

@user.put("/users/alumno/completar")
def completar_registro_alumno(
    datos: AlumnoCompletarRegistro,
    payload=Depends(obtener_usuario_actual),
):
    try:
        user = session.query(User).filter(User.id == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Actualizar datos en user_detail
        detail = user.user_detail
        detail.dni = datos.dni
        detail.first_name = datos.first_name
        detail.last_name = datos.last_name
        detail.type = datos.type

        session.commit()
        return {"success": True, "message": "Registro completado"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al completar registro")
    finally:
        session.close()

@user.get("/users/me")
def ver_perfil(payload=Depends(obtener_usuario_actual)):
    user = session.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.user_detail.email,
        "dni": user.user_detail.dni,
        "first_name": user.user_detail.first_name,
        "last_name": user.user_detail.last_name,
        "type": user.user_detail.type,
    }

@user.put("/users/change-password")
def cambiar_contraseña(
    data: PasswordChange,
    payload=Depends(obtener_usuario_actual),
):
    user = session.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    user.password = hash_password(data.new_password)
    session.commit()
    session.close()
    return {"success": True, "message": "Contraseña actualizada correctamente"}

@user.get("/userdetail/all")
def get_userDetails():
   try:
       return session.query(UserDetail).all()
   except Exception as e:
       print(e)

@user.post("/userdetail/add")
def add_usuarDetail(userDet: InputUserDetail):
   usuNuevo = UserDetail(
   userDet.dni, userDet.first_name, userDet.last_name, userDet.type, userDet.email
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
