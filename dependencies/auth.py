from fastapi import Cookie, HTTPException, status, Request

from services.auth_service import decode_token, AuthService
from services.erros import ValidationError, NotFoundError


def get_current_user(request: Request, access_token: str | None = Cookie(default=None)):
    if hasattr(request.state, 'user') and request.state.user is not None:
        return request.state.user

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_token(access_token)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    service = AuthService()
    try:
        user = service.get_user_by_id(user_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    return user
