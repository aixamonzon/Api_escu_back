from fastapi import APIRouter
from fastapi.responses import JSONResponse
from psycopg2 import session, IntegrityError
from models.userCarrera import UserCarrera, UserCarreraOut, NuevaUserCarrera, EditarUserCarrera
from sqlalchemy.orm import (
   joinedload,
)

user_carrera_router = APIRouter()

@user_carrera_router.get("/")
def welcome():
    return "Bienvenido a la ruta de usuario-carrera!"

@user_carrera_router.get("/user_carreras/all")
def obtener_user_carreras():
    try:
        # Carga las relaciones usuario-carrera con unión a usuarios y carreras
        user_carreras = session.query(UserCarrera).options(joinedload(UserCarrera.user), joinedload(UserCarrera.carrera)).all()
        # Convierte las relaciones en una lista de diccionarios
        user_carreras_con_detalles = []
        for user_carrera in user_carreras:
            user_carrera_con_detalle = {
                "id": user_carrera.id,
                "user_id": user_carrera.user_id,
                "carrera_id": user_carrera.carrera_id,
                "user": {
                    "id": user_carrera.user.id,
                    "username": user_carrera.user.username
                },
                "carrera": {
                    "id": user_carrera.carrera.id,
                    "nombre": user_carrera.carrera.nombre
                }
            }
            user_carreras_con_detalles.append(user_carrera_con_detalle)

        return JSONResponse(status_code=200, content=user_carreras_con_detalles)
    except Exception as e:
        print("Error al obtener usuario-carreras:", e)
        return JSONResponse(
            status_code=500, content={"detail": "Error al obtener usuario-carreras"}
        )
    
@user_carrera_router.get("/user_carreras/{id}")
def obtener_user_carrera_por_id(id: int):
    try:
        # Buscar la relación usuario-carrera por ID
        user_carrera = session.query(UserCarrera).options(joinedload(UserCarrera.user), joinedload(UserCarrera.carrera)).filter(UserCarrera.id == id).first()
        
        if not user_carrera:
            return JSONResponse(status_code=404, content={"detail": "Usuario-Carrera no encontrado"})
        
        # Convertir la relación en un diccionario
        user_carrera_con_detalle = {
            "id": user_carrera.id,
            "user_id": user_carrera.user_id,
            "carrera_id": user_carrera.carrera_id,
            "user": {
                "id": user_carrera.user.id,
                "username": user_carrera.user.username
            },
            "carrera": {
                "id": user_carrera.carrera.id,
                "nombre": user_carrera.carrera.nombre
            }
        }
        
        return JSONResponse(status_code=200, content=user_carrera_con_detalle)
    except Exception as e:
        print("Error al obtener usuario-carrera:", e)
        return JSONResponse(
            status_code=500, content={"detail": "Error al obtener usuario-carrera"}
        )
    
@user_carrera_router.post("/user_carreras/create")
def crear_user_carrera(user_carrera: NuevaUserCarrera):
    try:
        nueva_user_carrera = UserCarrera(user_id=user_carrera.user_id, carrera_id=user_carrera.carrera_id)
        session.add(nueva_user_carrera)
        session.commit()
        return JSONResponse(status_code=201, content={"detail": "Usuario-Carrera creada exitosamente"})
    except IntegrityError as e:
        session.rollback()
        print("Error de integridad al crear usuario-carrera:", e)
        return JSONResponse(status_code=400, content={"detail": "Error de integridad al crear usuario-carrera"})
    except Exception as e:
        print("Error al crear usuario-carrera:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al crear usuario-carrera"})
    
@user_carrera_router.put("/user_carreras/edit/{id}")
def editar_user_carrera(id: int, user_carrera: EditarUserCarrera):
    try:
        # Buscar la relación usuario-carrera por ID
        user_carrera_existente = session.query(UserCarrera).filter(UserCarrera.id == id).first()
        
        if not user_carrera_existente:
            return JSONResponse(status_code=404, content={"detail": "Usuario-Carrera no encontrado"})
        
        # Actualizar los campos si se proporcionan
        if user_carrera.user_id is not None:
            user_carrera_existente.user_id = user_carrera.user_id
        if user_carrera.carrera_id is not None:
            user_carrera_existente.carrera_id = user_carrera.carrera_id
        
        session.commit()
        return JSONResponse(status_code=200, content={"detail": "Usuario-Carrera actualizada exitosamente"})
    except IntegrityError as e:
        session.rollback()
        print("Error de integridad al editar usuario-carrera:", e)
        return JSONResponse(status_code=400, content={"detail": "Error de integridad al editar usuario-carrera"})
    except Exception as e:
        print("Error al editar usuario-carrera:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al editar usuario-carrera"})
    
@user_carrera_router.delete("/user_carreras/delete/{id}")
def eliminar_user_carrera(id: int):
    try:
        # Buscar la relación usuario-carrera por ID
        user_carrera = session.query(UserCarrera).filter(UserCarrera.id == id).first()
        
        if not user_carrera:
            return JSONResponse(status_code=404, content={"detail": "Usuario-Carrera no encontrado"})
        
        session.delete(user_carrera)
        session.commit()
        return JSONResponse(status_code=200, content={"detail": "Usuario-Carrera eliminada exitosamente"})
    except Exception as e:
        print("Error al eliminar usuario-carrera:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al eliminar usuario-carrera"})