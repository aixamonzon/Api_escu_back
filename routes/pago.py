from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from psycopg2 import IntegrityError
from models.user import session, InputUser, User
from models.pago import Pago, NuevoPago, EditarPago
from sqlalchemy.orm import (
   joinedload,
)
from security.auth import obtener_usuario_actual

pago = APIRouter()

@pago.get("/")
def welcome():
    return "Bienvenido a la ruta de pagos!"

@pago.get("/pagos/all")
def ver_todos_los_pagos(payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede ver todos los pagos")

    pagos = session.query(Pago).options(joinedload(Pago.user)).all()

    return [
        {
            "id": pago.id,
            "monto": str(pago.monto),
            "mes": pago.mes,
            "fecha_pago": str(pago.fecha_pago),
            "carrera_id": pago.carrera_id,
            "user": {
                "id": pago.user.id,
                "username": pago.user.username
            }
        }
        for pago in pagos
    ]
    
@pago.put("/pagos/edit/{id}")
def editar_pago(id: int, datos: EditarPago, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede editar pagos")

    pago = session.query(Pago).filter(Pago.id == id).first()

    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    if datos.monto is not None:
        pago.monto = datos.monto
    if datos.mes is not None:
        pago.mes = datos.mes
    if datos.carrera_id is not None:
        pago.carrera_id = datos.carrera_id

    session.commit()
    return JSONResponse(status_code=200, content={"detail": "Pago actualizado correctamente"})

@pago.get("/pagos/mis_pagos")
def ver_mis_pagos(payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "alumno":
        raise HTTPException(status_code=403, detail="Solo los alumnos pueden ver sus pagos")

    pagos = session.query(Pago).filter(Pago.user_id == payload["sub"]).all()

    return [
        {
            "id": pago.id,
            "monto": str(pago.monto),
            "mes": pago.mes,
            "fecha_pago": str(pago.fecha_pago),
            "carrera_id": pago.carrera_id
        }
        for pago in pagos
    ]
    
@pago.post("/pagos/create")
def crear_pago(pago: NuevoPago, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede registrar pagos")

    # Validación: verificar si ya existe un pago para ese alumno, carrera y mes
    pago_existente = session.query(Pago).filter(
        Pago.user_id == pago.user_id,
        Pago.carrera_id == pago.carrera_id,
        Pago.mes == pago.mes
    ).first()

    if pago_existente:
        raise HTTPException(status_code=400, detail="Ya existe un pago para este alumno en ese mes y carrera")

    try:
        nuevo_pago = Pago(
            user_id=pago.user_id,
            carrera_id=pago.carrera_id,
            monto=pago.monto,
            mes=pago.mes
        )
        session.add(nuevo_pago)
        session.commit()
        return JSONResponse(status_code=201, content={"detail": "Pago registrado correctamente"})
    except Exception as e:
        session.rollback()
        print("Error al registrar pago:", e)
        raise HTTPException(status_code=500, detail="Error interno al registrar el pago")
    
@pago.delete("/pagos/delete/{id}")
def eliminar_pago(id: int, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede eliminar pagos")

    pago = session.query(Pago).filter(Pago.id == id).first()

    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    session.delete(pago)
    session.commit()
    return JSONResponse(status_code=200, content={"detail": "Pago eliminado correctamente"})
    
@pago.get("/pagos/estado_mensual")
def estado_mensual(payload=Depends(obtener_usuario_actual)):
    """
    El alumno puede ver para cada mes si ya pagó o no (solo para el año actual).
    """
    if payload["type"] != "alumno":
        raise HTTPException(status_code=403, detail="Solo alumnos pueden ver su estado de pago mensual")

    from datetime import datetime
    import calendar

    meses = [f"{i:02d}" for i in range(1, 13)]
    pagos = session.query(Pago).filter(Pago.user_id == payload["sub"]).all()
    pagos_realizados = {pago.mes for pago in pagos}

    return [
        {"mes": mes, "estado": "pagado" if mes in pagos_realizados else "pendiente"}
        for mes in meses
    ]    

@pago.get("/pagos/alumno")
def pagos_por_alumno(user_id: int, payload=Depends(obtener_usuario_actual)):
    if payload["type"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede consultar los pagos por alumno")

    pagos = session.query(Pago).filter(Pago.user_id == user_id).all()

    if not pagos:
        return JSONResponse(status_code=404, content={"detail": "El alumno no tiene pagos registrados"})

    return [
        {
            "id": pago.id,
            "monto": str(pago.monto),
            "mes": pago.mes,
            "fecha_pago": str(pago.fecha_pago),
            "carrera_id": pago.carrera_id
        }
        for pago in pagos
    ]