from fastapi import APIRouter, HTTPException, Request, Query
from models.resultado_model import ResultadoCreate, ResultadoResponse
from services.resultado_service import ResultadoService
from services.log_service import LogService
from typing import Optional, Union, List

router = APIRouter(prefix="/resultados", tags=["resultados"])
resultado_service = ResultadoService()
log_service = LogService()

resultados_endpoint = "/resultados"

@router.put("/", response_model=dict)
@router.put("", response_model=dict)
async def salvar_resultado(resultado: ResultadoCreate, request: Request):
    """Salva um resultado de prova/exercício"""
    origem = request.client.host if request.client else "unknown"
    
    try:
        novo_resultado = resultado_service.salvar_resultado(resultado)
        resultado_id = novo_resultado.get("id")
        percentual_calculado = novo_resultado.get("percentual_acerto", 0)

        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=resultados_endpoint,
            detalhes=f"Resultado salvo - ID: {resultado_id}, Disciplina: {resultado.disciplina}, Ano: {resultado.ano}, Pontuação: {resultado.pontuacao}/{resultado.total_questoes} ({percentual_calculado}%)"
        )

        return {
            "success": True,
            "message": "Resultado salvo com sucesso!",
            "data": {
                "resultado_id": resultado_id,
                "resultado": novo_resultado
            }
        }
        
    except Exception as e:
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=resultados_endpoint,
            detalhes=f"Erro ao salvar resultado: {str(e)}"
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=Union[List[ResultadoResponse], dict])
@router.get("", response_model=Union[List[ResultadoResponse], dict])  # Aceita sem trailing slash também
async def listar_resultados(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    disciplina: Optional[str] = Query(None),
    ano: Optional[int] = Query(None, ge=1, le=12)
):
    """Lista todos os resultados com paginação"""
    origem = request.client.host if request.client else "unknown"
    
    try:
        paginated = resultado_service.listar_resultados_paginated(
            page=page, 
            limit=limit, 
            disciplina=disciplina, 
            ano=ano
        )

        total_pages = paginated.get("totalPages", 0)
        if total_pages == 0 or page > total_pages:
            log_service.log_consumo(
                origem_consumo=origem,
                resultado_consumo="sucesso",
                endpoint=resultados_endpoint,
                detalhes=f"Listagem resultados - Página {page} fora do range, Total: {paginated.get('total', 0)}, Disciplina: {disciplina}, Ano: {ano}"
            )
            return []

        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=resultados_endpoint,
            detalhes=f"Listagem resultados - Página {page}/{total_pages}, Limit: {limit}, Total: {paginated.get('total', 0)}, Disciplina: {disciplina}, Ano: {ano}"
        )

        return paginated
    except Exception as e:
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=resultados_endpoint,
            detalhes=f"Erro ao listar resultados: {str(e)}"
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{resultado_id}", response_model=ResultadoResponse)
async def buscar_resultado(resultado_id: str, request: Request):
    """Busca um resultado pelo ID"""
    origem = request.client.host if request.client else "unknown"
    
    try:
        resultado = resultado_service.buscar_resultado_por_id(resultado_id)
        if not resultado:
            raise HTTPException(status_code=404, detail="Resultado não encontrado")
        
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=f"{resultados_endpoint}/{resultado_id}",
            detalhes=f"Resultado encontrado - ID: {resultado_id}"
        )

        return resultado
    except HTTPException as he:
        raise he
    except Exception as e:
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=f"{resultados_endpoint}/{resultado_id}",
            detalhes=f"Erro ao buscar resultado: {str(e)}"
        )
        
        raise HTTPException(status_code=500, detail=str(e))
