from fastapi import APIRouter, HTTPException, status, Response, Depends, Request
from pydantic import BaseModel, EmailStr
from fastapi.concurrency import run_in_threadpool

from services.auth_service import AuthService
from services.erros import ValidationError, NotFoundError
from dependencies.auth import get_current_user
from services.log_service import LogService
from services.log_service_async import LogServiceAsync

router = APIRouter(prefix="/auth", tags=["auth"])

AUTH_LOGIN = "/auth/login"
AUTH_ME = "/auth/me"
AUTH_LOGOUT = "/auth/logout"


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


@router.post('/login')
async def login(payload: LoginRequest, response: Response, request: Request):
    origem = request.client.host if request.client else 'auth'

    sync_log = LogService()
    async_log = LogServiceAsync()

    service = AuthService()
    try:
        result = service.login(payload.email, payload.senha)
    except NotFoundError:
        detalhes = {"email": payload.email, "result": "not_found"}
        try:
            if async_log.collection is not None:
                await async_log.log_consumo(origem_consumo=origem, resultado_consumo='erro', endpoint=AUTH_LOGIN, detalhes=detalhes)
            else:
                await run_in_threadpool(sync_log.log_consumo, origem, 'erro', AUTH_LOGIN, detalhes)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    except ValidationError as e:
        detalhes = {"email": payload.email, "result": "validation_error", "reason": str(e)}
        try:
            if async_log.collection is not None:
                await async_log.log_consumo(origem_consumo=origem, resultado_consumo='erro', endpoint=AUTH_LOGIN, detalhes=detalhes)
            else:
                await run_in_threadpool(sync_log.log_consumo, origem, 'erro', AUTH_LOGIN, detalhes)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    token = result["access_token"]
    response.set_cookie(key="access_token", value=token, httponly=True, secure=False, samesite="none")

    detalhes = {"email": payload.email, "result": "success", "user": result.get("user")}
    try:
        if async_log.collection is not None:
            await async_log.log_consumo(origem_consumo=origem, resultado_consumo='sucesso', endpoint=AUTH_LOGIN, detalhes=detalhes)
        else:
            await run_in_threadpool(sync_log.log_consumo, origem, 'sucesso', AUTH_LOGIN, detalhes)
    except Exception:
        pass

    return {"message": "Login realizado", "user": result["user"]}


@router.get('/me')
async def me(request: Request, current_user: dict = Depends(get_current_user)):
    origem = request.client.host if request.client else 'auth'

    sync_log = LogService()
    async_log = LogServiceAsync()
    detalhes = {"action": "me", "user": current_user}
    try:
        if async_log.collection is not None:
            await async_log.log_consumo(origem_consumo=origem, resultado_consumo='sucesso', endpoint=AUTH_ME, detalhes=detalhes)
        else:
            await run_in_threadpool(sync_log.log_consumo, origem, 'sucesso', AUTH_ME, detalhes)
    except Exception:
        pass

    return {"user": current_user}


@router.post('/logout')
async def logout(request: Request, response: Response):
    origem = request.client.host if request.client else 'auth'
    sync_log = LogService()
    async_log = LogServiceAsync()
    detalhes = {"action": "logout"}
    try:
        if async_log.collection is not None:
            await async_log.log_consumo(origem_consumo=origem, resultado_consumo='sucesso', endpoint=AUTH_LOGOUT, detalhes=detalhes)
        else:
            await run_in_threadpool(sync_log.log_consumo, origem, 'sucesso', AUTH_LOGOUT, detalhes)
    except Exception:
        pass

    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logout realizado"}
