from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from config.db import Base, engine
from models.userCarrera import UserCarrera, UserCarreraOut, NuevaUserCarrera, EditarUserCarrera, session
from models.user import User
from sqlalchemy.exc import IntegrityError
from security.auth import obtener_usuario_actual
from sqlalchemy.orm import (
   joinedload,
)

user_carrera_router = APIRouter()

@user_carrera_router.get("/")
def welcome():
    return "Bienvenido a la ruta de usuario-carrera!"

@user_carrera_router.get("/user_carreras/all")
def obtener_user_carreras(payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede ver todos los usuarios y carreras")

    user_carreras = session.query(UserCarrera).options(joinedload(UserCarrera.user), joinedload(UserCarrera.carrera)).all()
    resultado = []
    for uc in user_carreras:
        resultado.append({
            "id": uc.id,
            "user_id": uc.user_id,
            "carrera_id": uc.carrera_id,
            "user": {"id": uc.user.id, "username": uc.user.username},
            "carrera": {"id": uc.carrera.id, "nombre": uc.carrera.nombre}
        })
    return resultado
    
@user_carrera_router.get("/user_carreras/my")
def obtener_mis_carreras(payload=Depends(obtener_usuario_actual)):
    user_carreras = session.query(UserCarrera).options(joinedload(UserCarrera.carrera)).filter(UserCarrera.user_id == payload["sub"]).all()
    resultado = []
    for uc in user_carreras:
        resultado.append({
            "id": uc.carrera.id,
            "nombre": uc.carrera.nombre
        })
    return resultado
    
@user_carrera_router.post("/user_carreras/assign")
def asignar_carrera_a_alumno(user_carrera: NuevaUserCarrera, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede asignar carreras a alumnos")
    
    # Opcional: Verificar que user_id corresponde a un alumno
    usuario = session.query(User).filter(User.id == user_carrera.user_id).first()
    if not usuario or usuario.user_detail.type != "alumno":
        raise HTTPException(status_code=400, detail="El usuario no es un alumno válido")

    nueva_relacion = UserCarrera(user_id=user_carrera.user_id, carrera_id=user_carrera.carrera_id)
    try:
        session.add(nueva_relacion)
        session.commit()
        return {"detail": "Carrera asignada al alumno exitosamente"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al asignar carrera")
    
@user_carrera_router.put("/user_carreras/edit/{id}")
def editar_user_carrera(id: int, user_carrera: EditarUserCarrera, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede editar inscripciones")
    
    relacion = session.query(UserCarrera).filter(UserCarrera.id == id).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    
    if user_carrera.carrera_id:
        relacion.carrera_id = user_carrera.carrera_id

    try:
        session.commit()
        return {"detail": "Inscripción actualizada exitosamente"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar inscripción")
    
@user_carrera_router.delete("/user_carreras/delete/{id}")
def eliminar_user_carrera(id: int, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede eliminar inscripciones")

    relacion = session.query(UserCarrera).filter(UserCarrera.id == id).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Usuario-Carrera no encontrada")

    try:
        session.delete(relacion)
        session.commit()
        return {"detail": "Inscripción eliminada exitosamente"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar inscripción")