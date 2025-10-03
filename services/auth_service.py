from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from bson import ObjectId

from connection import get_collection
from config.settings import settings
from services.erros import NotFoundError, ValidationError

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValidationError("Token expirado")
    except jwt.InvalidTokenError:
        raise ValidationError("Token inválido")


class AuthService:
    def __init__(self):
        self.collection = get_collection(settings.USUARIOS_COLLECTION)

    def authenticate_user(self, email: str, password: str) -> dict:
        """Valida credenciais e retorna o documento do usuário (sem senha)."""
        user = self.collection.find_one({"email": email})
        if not user:
            raise NotFoundError("Usuário não encontrado")

        hashed = user.get("senha") or user.get("password")
        if not hashed:
            raise ValidationError("Usuário sem senha cadastrada")

        if not verify_password(password, hashed):
            raise ValidationError("Credenciais inválidas")

        # remove senha before returning
        user["id"] = str(user.get("_id"))
        user.pop("_id", None)
        user.pop("senha", None)
        user.pop("password", None)
        return user

    def login(self, email: str, password: str) -> dict:
        user = self.authenticate_user(email, password)
        token_data = {"sub": user.get("id"), "email": user.get("email")}
        token = create_access_token(token_data)
        return {"access_token": token, "token_type": "bearer", "user": user}

    def get_user_by_id(self, user_id: str) -> dict:
        user = self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise NotFoundError("Usuário não encontrado")
        user["id"] = str(user.get("_id"))
        user.pop("_id", None)
        user.pop("senha", None)
        user.pop("password", None)
        return user
