from fastapi import APIRouter, HTTPException, Request
from models.questao_model import QuestaoCreate, QuestaoResponse
from services.questao_service import QuestaoService
from services.log_service import LogService

router = APIRouter(prefix="/questoes", tags=["questoes"])
questao_service = QuestaoService()
log_service = LogService()

@router.get("/", response_model=list[QuestaoResponse])
async def listar_questoes(request: Request):
    """Lista todas as questões"""
    origem = request.client.host
    
    try:
        questoes = questao_service.listar_questoes()
        
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="sucesso",
            endpoint="/questoes/",
            detalhes=f"{len(questoes)} questões listadas"
        )
        
        return questoes
    except Exception as e:
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint="/questoes/",
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
            endpoint=f"/questoes/{questao_id}",
            detalhes=f"Questão encontrada com ID: {questao_id}"
        )
        
        return questao
        
    except HTTPException as he:
        raise he
    except Exception as e:
        # Log de erro
        log_service.log_consumo(
            origem_consumo=origem,
            resultado_consumo="erro",
            endpoint=f"/questoes/{questao_id}",
            detalhes=str(e)
        )
        
        raise HTTPException(status_code=500, detail=str(e))

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