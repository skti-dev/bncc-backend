from fastapi import APIRouter, HTTPException, Request
from models.questao_model import QuestaoCreate, QuestaoResponse
from services.questao_service import QuestaoService
from services.log_service import LogService

router = APIRouter(prefix="/questoes", tags=["questoes"])
questao_service = QuestaoService()
log_service = LogService()

@router.post("/adicionar", response_model=dict)
async def adicionar_questao(questao: QuestaoCreate, request: Request):
    """Adiciona uma nova questão"""
    origem = request.client.host
    
    try:
        # Adicionar questão
        nova_questao = questao_service.adicionar_questao(questao)
        
        # Log de sucesso
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint="/questoes/adicionar",
            detalhes=f"Questão adicionada com ID: {nova_questao['_id']}"
        )
        
        return {
            "message": "Questão adicionada com sucesso!",
            "questao_id": nova_questao["_id"],
            "questao": nova_questao
        }
        
    except Exception as e:
        # Log de erro
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint="/questoes/adicionar",
            detalhes=str(e)
        )
        
        raise HTTPException(status_code=500, detail=str(e))