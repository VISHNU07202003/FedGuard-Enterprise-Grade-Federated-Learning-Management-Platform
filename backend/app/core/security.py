import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.core.config import settings
from app.core.secrets import config_provider

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    from app.core.secrets import get_secret
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    jwt_secret = get_secret("JWT_SECRET")
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
