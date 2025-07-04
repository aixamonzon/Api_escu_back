from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.carrera import Carrera, NuevaCarrera, EditarCarrera, session
from psycopg2 import IntegrityError
from sqlalchemy.orm import joinedload

carrera_router = APIRouter()

@carrera_router.get("/")
def welcome():
    return "Bienvenido a la ruta de carreras!"

@carrera_router.get("/carreras/all")
def obtener_carreras():
    try:
        # Carga las carreras con unión a usuarios y pagos
        carreras = session.query(Carrera).options(joinedload(Carrera.users), joinedload(Carrera.pagos)).all()
        # Convierte las carreras en una lista de diccionarios
        carreras_con_detalles = []
        for carrera in carreras:
            carrera_con_detalle = {
                "id": carrera.id,
                "nombre": carrera.nombre,
                "users": [user.user_id for user in carrera.users],
                "pagos": [{"id": pago.id, "monto": pago.monto, "mes": pago.mes} for pago in carrera.pagos]
            }
            carreras_con_detalles.append(carrera_con_detalle)

        return JSONResponse(status_code=200, content=carreras_con_detalles)
    except Exception as e:
        print("Error al obtener carreras:", e)
        return JSONResponse(
            status_code=500, content={"detail": "Error al obtener carreras"}
        )
    
@carrera_router.get("/carreras/{id}")
def obtener_carrera_por_id(id: int):
    try:
        # Buscar la carrera por ID
        carrera = session.query(Carrera).options(joinedload(Carrera.users), joinedload(Carrera.pagos)).filter(Carrera.id == id).first()
        
        if not carrera:
            return JSONResponse(status_code=404, content={"detail": "Carrera no encontrada"})
        
        # Convertir la carrera en un diccionario
        carrera_con_detalle = {
            "id": carrera.id,
            "nombre": carrera.nombre,
            "users": [user.user_id for user in carrera.users],
            "pagos": [{"id": pago.id, "monto": pago.monto, "mes": pago.mes} for pago in carrera.pagos]
        }
        
        return JSONResponse(status_code=200, content=carrera_con_detalle)
    except Exception as e:
        print("Error al obtener carrera:", e)
        return JSONResponse(
            status_code=500, content={"detail": "Error al obtener carrera"}
        )
    
@carrera_router.post("/carreras/create")
def crear_carrera(carrera: NuevaCarrera):
    try:
        nueva_carrera = Carrera(nombre=carrera.nombre)
        session.add(nueva_carrera)
        session.commit()
        return JSONResponse(status_code=201, content={"detail": "Carrera creada exitosamente"})
    except IntegrityError as e:
        session.rollback()
        print("Error al crear carrera:", e)
        return JSONResponse(status_code=400, content={"detail": "Error al crear carrera"})
    except Exception as e:
        print("Error al crear carrera:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al crear carrera"})

@carrera_router.put("/carreras/edit/{id}")
def editar_carrera(id: int, carrera: EditarCarrera):
    try:
        # Buscar la carrera por ID
        carrera_existente = session.query(Carrera).filter(Carrera.id == id).first()
        
        if not carrera_existente:
            return JSONResponse(status_code=404, content={"detail": "Carrera no encontrada"})
        
        # Actualizar los campos de la carrera
        if carrera.nombre:
            carrera_existente.nombre = carrera.nombre
        
        session.commit()
        return JSONResponse(status_code=200, content={"detail": "Carrera actualizada exitosamente"})
    except IntegrityError as e:
        session.rollback()
        print("Error al editar carrera:", e)
        return JSONResponse(status_code=400, content={"detail": "Error al editar carrera"})
    except Exception as e:
        print("Error al editar carrera:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al editar carrera"})
    
@carrera_router.delete("/carreras/delete/{id}")
def eliminar_carrera(id: int):
    try:
        # Buscar la carrera por ID
        carrera = session.query(Carrera).filter(Carrera.id == id).first()
        
        if not carrera:
            return JSONResponse(status_code=404, content={"detail": "Carrera no encontrada"})
        
        session.delete(carrera)
        session.commit()
        return JSONResponse(status_code=200, content={"detail": "Carrera eliminada exitosamente"})
    except Exception as e:
        print("Error al eliminar carrera:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al eliminar carrera"})