from fastapi import APIRouter
from fastapi.responses import JSONResponse
from psycopg2 import IntegrityError
from models.user import session, InputUser, User
from models.pago import Pago, NuevoPago
from sqlalchemy.orm import (
   joinedload,
)

pago = APIRouter()

@pago.get("/")
def welcome():
    return "Bienvenido a la ruta de pagos!"

@pago.get("/pagos/all")
def obtener_pagos():
    try:
        # Carga los pagos con unión a usuario y carrera
        pagos = session.query(User).options(joinedload(User.pagos)).all()
        # Convierte los pagos en una lista de diccionarios
        pagos_con_detalles = []
        for pago in pagos:
            for p in pago.pagos:
                pago_con_detalle = {
                    "id": p.id,
                    "user_id": p.user_id,
                    "carrera_id": p.carrera_id,
                    "monto": p.monto,
                    "mes": p.mes,
                    "fecha_pago": p.fecha_pago,
                }
                pagos_con_detalles.append(pago_con_detalle)

        return JSONResponse(status_code=200, content=pagos_con_detalles)
    except Exception as e:
        print("Error al obtener pagos:", e)
        return JSONResponse(
            status_code=500, content={"detail": "Error al obtener pagos"}
        )
    
@pago.get("/pagos/{id}")
def obtener_pago_por_id(id: int):
    try:
        # Buscar el pago por ID
        pago = session.query(User).options(joinedload(User.pagos)).filter(User.id == id).first()
        
        if not pago:
            return JSONResponse(status_code=404, content={"detail": "Pago no encontrado"})
        
        # Convertir el pago en un diccionario
        pago_con_detalle = {
            "id": pago.id,
            "user_id": pago.user_id,
            "carrera_id": pago.carrera_id,
            "monto": pago.monto,
            "mes": pago.mes,
            "fecha_pago": pago.fecha_pago,
        }
        
        return JSONResponse(status_code=200, content=pago_con_detalle)
    except Exception as e:
        print("Error al obtener el pago:", e)
        return JSONResponse(
            status_code=500, content={"detail": "Error al obtener el pago"}
        )
    
@pago.post("/pagos/add")
def agregar_pago(pago: InputUser):
    try:
        nuevo_pago = Pago(
            user_id=pago.user_id,
            carrera_id=pago.carrera_id,
            monto=pago.monto,
            mes=pago.mes,
            fecha_pago=pago.fecha_pago
        )
        session.add(nuevo_pago)
        session.commit()
        return JSONResponse(status_code=201, content={"detail": "Pago agregado exitosamente"})
    except IntegrityError as e:
        session.rollback()
        print("Error de integridad al agregar el pago:", e)
        return JSONResponse(status_code=400, content={"detail": "Error de integridad al agregar el pago"})
    except Exception as e:
        print("Error al agregar el pago:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al agregar el pago"})
    
@pago.put("/pagos/edit/{id}")
def editar_pago(id: int, pago: InputUser):
    try:
        # Buscar el pago por ID
        pago_existente = session.query(Pago).filter(Pago.id == id).first()
        
        if not pago_existente:
            return JSONResponse(status_code=404, content={"detail": "Pago no encontrado"})
        
        # Actualizar los campos del pago
        if pago.user_id is not None:
            pago_existente.user_id = pago.user_id
        if pago.carrera_id is not None:
            pago_existente.carrera_id = pago.carrera_id
        if pago.monto is not None:
            pago_existente.monto = pago.monto
        if pago.mes is not None:
            pago_existente.mes = pago.mes
        
        session.commit()
        return JSONResponse(status_code=200, content={"detail": "Pago actualizado exitosamente"})
    except Exception as e:
        print("Error al editar el pago:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al editar el pago"})
    
@pago.delete("/pagos/delete/{id}")
def eliminar_pago(id: int):
    try:
        # Buscar el pago por ID
        pago = session.query(Pago).filter(Pago.id == id).first()
        
        if not pago:
            return JSONResponse(status_code=404, content={"detail": "Pago no encontrado"})
        
        session.delete(pago)
        session.commit()
        return JSONResponse(status_code=200, content={"detail": "Pago eliminado exitosamente"})
    except Exception as e:
        print("Error al eliminar el pago:", e)
        return JSONResponse(status_code=500, content={"detail": "Error al eliminar el pago"})
    
    