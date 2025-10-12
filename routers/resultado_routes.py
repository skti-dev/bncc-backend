from fastapi import APIRouter, HTTPException, Request, Query
from models.resultado_model import ResultadoCreate, ResultadoResponse
from services.resultado_service import ResultadoService
from services.log_service_async import LogServiceAsync
from typing import Optional, Union, List

router = APIRouter(prefix="/resultados", tags=["resultados"])
resultado_service = ResultadoService()
log_service = LogServiceAsync()

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

        await log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=resultados_endpoint,
            detalhes={
                "message": "Resultado salvo",
                "resultado_id": resultado_id,
                "email": resultado.email,
                "disciplina": resultado.disciplina,
                "ano": resultado.ano,
                "pontuacao": resultado.pontuacao,
                "total_questoes": resultado.total_questoes,
                "percentual_acerto": percentual_calculado
            }
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
        await log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=resultados_endpoint,
            detalhes={"error": str(e), "message": "Erro ao salvar resultado"}
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=Union[List[ResultadoResponse], dict])
@router.get("", response_model=Union[List[ResultadoResponse], dict])
async def listar_resultados(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    disciplina: Optional[str] = Query(None),
    ano: Optional[int] = Query(None, ge=1, le=12),
    email: Optional[str] = Query(None)
):
    """Lista todos os resultados com paginação"""
    origem = request.client.host if request.client else "unknown"
    
    try:
        paginated = resultado_service.listar_resultados_paginated(
            page=page, 
            limit=limit, 
            disciplina=disciplina, 
            ano=ano,
            email=email
        )

        total_pages = paginated.get("totalPages", 0)
        if total_pages == 0 or page > total_pages:
            await log_service.log_consumo(
                origem_consumo=origem,
                resultado_consumo="sucesso",
                endpoint=resultados_endpoint,
                detalhes={
                    "message": "Página fora do range",
                    "page": page,
                    "total": paginated.get('total', 0),
                    "disciplina": disciplina,
                    "ano": ano,
                    "email": email
                }
            )
            return []

        await log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=resultados_endpoint,
            detalhes={
                "message": "Listagem resultados",
                "page": page,
                "total_pages": total_pages,
                "limit": limit,
                "total": paginated.get('total', 0),
                "disciplina": disciplina,
                "ano": ano,
                "email": email
            }
        )

        return paginated
    except Exception as e:
        await log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=resultados_endpoint,
            detalhes={"error": str(e), "message": "Erro ao listar resultados"}
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
        
        await log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=f"{resultados_endpoint}/{resultado_id}",
            detalhes={"message": "Resultado encontrado", "resultado_id": resultado_id}
        )

        return resultado
    except HTTPException as he:
        raise he
    except Exception as e:
        await log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=f"{resultados_endpoint}/{resultado_id}",
            detalhes={"error": str(e), "message": "Erro ao buscar resultado"}
        )
        
        raise HTTPException(status_code=500, detail=str(e))
