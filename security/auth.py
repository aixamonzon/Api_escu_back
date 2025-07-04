from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
import pytz

SECRET_KEY = "w8iK2xXcq38v!@#ZmuP0qLzJ7hA!9fdR" # Clave secreta para firmar el JWT
ALGORITHM = "HS256" # Algoritmo de firma del JWT
TIMEZONE = pytz.timezone("America/Argentina/Buenos_Aires") # Zona horaria configurada para la aplicación

security = HTTPBearer(auto_error=False) # Seguridad HTTP Bearer para manejar tokens JWT

def crear_token(data, expires_delta: int = 60):
    """
    Crea un JWT con expiración (en minutos) y zona horaria configurada.
    """
    ahora = datetime.now(TIMEZONE) # Obtiene la hora actual en la zona horaria configurada
    exp = ahora + timedelta(minutes=expires_delta) # Tiempo de expiración del token

    payload = {
        "sub": str (data.id), # ID del usuario
        "username": data.username, # Nombre de usuario
        "type": data.user_detail.type, # Tipo de usuario (por ejemplo, admin, alumno, etc.)
        "iat": ahora, # Tiempo de emisión del token
        "exp": exp # Tiempo de expiración del token
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token if isinstance(token, str) else token.decode("utf-8") # Asegura que el token sea una cadena de texto

def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica que el header Authorization exista y tenga esquema Bearer,
    retorna solo el token (string) para decodificar.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization header must start with 'Bearer'")
    return credentials.credentials

def verificar_token(headers):
    """
    Verifica y decodifica el JWT. Lanza excepciones si es inválido o expiró.
    """
    if headers["authorization"]:
      token = headers["authorization"].split(" ")[1]
      try:
          payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
          return payload
      except jwt.ExpiredSignatureError:
         return {"success": False, "message": "Token expired!"}
      except jwt.InvalidSignatureError:
         return {"success": False, "message": "Token: signature error!"}
      except jwt.DecodeError as e:
         return {"success": False, "message": "Invalid token!"}
      except Exception as e:
         return {"success": False, "message": "Token: unknown error!"}

def obtener_usuario_actual(token: str = Depends(verify_bearer_token)):
    """
    Decodifica el JWT y retorna el payload con la info del usuario.
    Lanza HTTPException si el token es inválido o expiró.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        print(f"Token inválido, error: {e}")
        raise HTTPException(status_code=401, detail="Token inválido")