from fastapi import APIRouter, Query
from services.log_service import LogService
from services.log_service_async import LogServiceAsync
from typing import Optional

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", response_model=list)
async def listar_logs(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), origem: Optional[str] = None, resultado: Optional[str] = None):
    """Lista logs com paginação e filtragem simples"""
    skip = (page - 1) * limit
    async_svc = LogServiceAsync()
    sync_svc = LogService()
    if async_svc.collection is not None:
        items = await async_svc.buscar_logs(limite=limit, skip=skip)
    else:
        items = sync_svc.buscar_logs(limite=limit)

    if origem:
        items = [i for i in items if i.get("origem_consumo") == origem]
    if resultado:
        items = [i for i in items if i.get("resultado_consumo") == resultado]

    return items
