from fastapi import APIRouter
from routers.questao_routes import router as questao_router
from routers.auth_routes import router as auth_router
from routers.logs_routes import router as logs_router
from routers.resultado_routes import router as resultado_router
from connection import test_connection
from config.settings import settings

router = APIRouter()

router.include_router(questao_router)
router.include_router(auth_router)
router.include_router(logs_router)
router.include_router(resultado_router)


@router.get("/", tags=["health"])
async def health_check():
    """Verifica se a API está funcionando"""
    return {
        "message": f"{settings.API_TITLE} está funcionando!",
        "version": settings.API_VERSION,
        "status": "online",
    }


@router.get("/health", tags=["health"])
async def detailed_health_check():
    """Verifica saúde da aplicação incluindo MongoDB"""
    mongodb_status = "online" if test_connection() else "offline"
    return {
        "api_status": "online",
        "mongodb_status": mongodb_status,
        "version": settings.API_VERSION,
    }
