from fastapi import APIRouter, HTTPException, status, Response, Depends
from pydantic import BaseModel, EmailStr

from services.auth_service import AuthService
from services.erros import ValidationError, NotFoundError
from dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


@router.post('/login')
def login(request: LoginRequest, response: Response):
    service = AuthService()
    try:
        result = service.login(request.email, request.senha)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    token = result["access_token"]
    response.set_cookie(key="access_token", value=token, httponly=True, secure=False, samesite="lax")

    return {"message": "Login realizado", "user": result["user"]}


@router.get('/me')
def me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
