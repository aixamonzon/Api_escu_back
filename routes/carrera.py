from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.carrera import Carrera, NuevaCarrera, EditarCarrera, session
from security.auth import crear_token, obtener_usuario_actual
from psycopg2 import IntegrityError
from sqlalchemy.orm import joinedload

carrera_router = APIRouter()

@carrera_router.get("/")
def welcome():
    return "Bienvenido a la ruta de carreras!"

@carrera_router.get("/carreras/all")
def obtener_carreras(payload=Depends(obtener_usuario_actual)):
    """
    Admin ve todas las carreras.
    Alumno ve solo su carrera.
    """
    if payload["type"] == "admin":
        carreras = session.query(Carrera).options(joinedload(Carrera.users)).all()
        resultado = []
        for carrera in carreras:
            resultado.append({
                "id": carrera.id,
                "nombre": carrera.nombre,
                "users": [uc.user_id for uc in carrera.users]
            })
        return resultado

    elif payload["type"] == "alumno":
        # Obtener la carrera del alumno
        user_carreras = session.query(UserCarrera).filter(UserCarrera.user_id == payload["sub"]).all()
        carreras = []
        for uc in user_carreras:
            carreras.append({
                "id": uc.carrera.id,
                "nombre": uc.carrera.nombre
            })
        return carreras
    else:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    
@carrera_router.get("/carreras/{id}")
def obtener_carrera_por_id(id: int, payload=Depends(obtener_usuario_actual)):
    carrera = session.query(Carrera).filter(Carrera.id == id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    if payload["type"] == "admin":
        # Admin puede ver todo
        return {
            "id": carrera.id,
            "nombre": carrera.nombre
        }
    elif payload["type"] == "alumno":
        # Alumno puede ver solo si está inscripto
        user_carrera = session.query(UserCarrera).filter(
            UserCarrera.user_id == payload["sub"],
            UserCarrera.carrera_id == id
        ).first()
        if user_carrera:
            return {
                "id": carrera.id,
                "nombre": carrera.nombre
            }
        else:
            raise HTTPException(status_code=403, detail="No está inscripto en esta carrera")
    else:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    
@carrera_router.post("/carreras/create")
def crear_carrera(carrera: NuevaCarrera, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede crear carreras")
    nueva_carrera = Carrera(nombre=carrera.nombre)
    try:
        session.add(nueva_carrera)
        session.commit()
        return {"detail": "Carrera creada exitosamente"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al crear carrera")

@carrera_router.put("/carreras/edit/{id}")
def editar_carrera(id: int, carrera: EditarCarrera, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede editar carreras")
    carrera_existente = session.query(Carrera).filter(Carrera.id == id).first()
    if not carrera_existente:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    if carrera.nombre:
        carrera_existente.nombre = carrera.nombre
    try:
        session.commit()
        return {"detail": "Carrera actualizada exitosamente"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al editar carrera")
    
@carrera_router.delete("/carreras/delete/{id}")
def eliminar_carrera(id: int, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede eliminar carreras")
    carrera = session.query(Carrera).filter(Carrera.id == id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    try:
        session.delete(carrera)
        session.commit()
        return {"detail": "Carrera eliminada exitosamente"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar carrera")