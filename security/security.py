from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Contexto de cifrado para contraseñas

def hash_password(plain_password: str) -> str:  # Cifra una contraseña en texto plano
    return pwd_context.hash(plain_password)

def verificar_password(plain_password: str, hashed_password: str) -> bool: # Verifica si una contraseña en texto plano coincide con una contraseña cifrada
    return pwd_context.verify(plain_password, hashed_password)