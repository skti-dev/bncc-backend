from fastapi import APIRouter, HTTPException, Request, Query
from models.questao_model import QuestaoCreate, QuestaoResponse
from services.questao_service import QuestaoService
from services.log_service import LogService
from typing import Optional, Union, List

from models.questao_model import DisciplinaEnum

router = APIRouter(prefix="/questoes", tags=["questoes"])
questao_service = QuestaoService()
log_service = LogService()

questoes_endpoint = "/questoes"

@router.get("/", response_model=Union[List[QuestaoResponse], dict])
async def listar_questoes(
    request: Request,
    page: int = Query(..., ge=1),
    limit: int = Query(10, ge=1, le=20),
    disciplina: Optional[DisciplinaEnum] = Query(None),
):
    """Lista todas as questões"""
    origem = request.client.host
    
    try:
        paginated = questao_service.listar_questoes_paginated(page=page, limit=limit, disciplina=(disciplina.value if disciplina else None))

        total_pages = paginated.get("totalPages", 0)
        if total_pages == 0 or page > total_pages:
            log_service.log_consumo(
                origem_consumo=origem,
                resultado_consumo="sucesso",
                endpoint=questoes_endpoint,
                detalhes=f"page={page} out_of_range total={paginated.get('total',0)}"
            )
            return []

        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=questoes_endpoint,
            detalhes=f"page={page} limit={limit} disciplina={disciplina} total={paginated.get('total',0)}"
        )

        return paginated
    except Exception as e:
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=questoes_endpoint,
            detalhes=str(e)
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{questao_id}", response_model=QuestaoResponse)
async def buscar_questao(questao_id: str, request: Request):
    """Busca uma questão pelo ID"""
    origem = request.client.host
    
    try:
        questao = questao_service.buscar_questao_por_id(questao_id)
        if not questao:
            raise HTTPException(status_code=404, detail="Questão não encontrada")
        
        # Log de sucesso
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=f"{questoes_endpoint}/{questao_id}",
            detalhes=f"Questão encontrada com ID: {questao_id}"
        )

        qr = QuestaoResponse.model_validate(questao)
        return qr.model_dump()
    except HTTPException as he:
        raise he
    except Exception as e:
        # Log de erro
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=f"{questoes_endpoint}/{questao_id}",
            detalhes=str(e)
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adicionar", response_model=dict)
async def adicionar_questao(questao: QuestaoCreate, request: Request):
    """Adiciona uma nova questão"""
    origem = request.client.host
    
    try:
        nova_questao = questao_service.adicionar_questao(questao)

        questao_id = nova_questao.get("id")

        # Log de sucesso
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint=f"{questoes_endpoint}/adicionar",
            detalhes=f"Questão adicionada com ID: {questao_id}"
        )

        return {
            "message": "Questão adicionada com sucesso!",
            "questao_id": questao_id,
            "questao": nova_questao
        }
        
    except Exception as e:
        # Log de erro
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=f"{questoes_endpoint}/adicionar",
            detalhes=str(e)
        )
        
        raise HTTPException(status_code=500, detail=str(e))