from fastapi import Depends
from security.auth import obtener_usuario_actual

def solo_admin(user_data=Depends(obtener_usuario_actual)): # Dependencia para verificar si el usuario es administrador
    if user_data.get("type") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    return user_data 


def solo_alumno(user_data=Depends(obtener_usuario_actual)): # Dependencia para verificar si el usuario es alumno
    if user_data.get("type") != "alumno":
        raise HTTPException(status_code=403, detail="Solo accesible para alumnos")
    return user_data