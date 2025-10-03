from connection import get_collection
from models.questao_model import QuestaoCreate
from bson import ObjectId
from datetime import datetime
from models.questao_model import QuestaoResponse
from config.settings import settings as app_settings

class QuestaoService:
    def __init__(self):
        self.collection = get_collection(app_settings.QUESTOES_COLLECTION)

    def adicionar_questao(self, questao_data: QuestaoCreate):
        """Adiciona uma nova questão ao banco de dados"""
        try:
            # Converter para dict
            # usar mode="json" para garantir que enums e outros tipos sejam serializáveis
            questao_dict = questao_data.model_dump(mode="json")
            
            # Adicionar timestamp (usar ISO strings para JSON)
            now_iso = datetime.utcnow().isoformat() + "Z"
            questao_dict['created_at'] = now_iso
            questao_dict['updated_at'] = now_iso
            
            # Inserir no MongoDB
            result = self.collection.insert_one(questao_dict)
            
            # Retornar o documento inserido
            questao_inserida = self.collection.find_one({"_id": result.inserted_id})
            # criar campo id como string para compatibilidade com os Pydantic models
            questao_inserida["id"] = str(questao_inserida["_id"])
            # remover _id cru do documento retornado
            if "_id" in questao_inserida:
                del questao_inserida["_id"]

            # garantir timestamps em ISO strings se vierem como datetimes
            for t in ("created_at", "updated_at"):
                if t in questao_inserida and not isinstance(questao_inserida[t], str):
                    try:
                        questao_inserida[t] = questao_inserida[t].isoformat() + "Z"
                    except Exception:
                        questao_inserida[t] = str(questao_inserida[t])

            # reconstruir via Pydantic e retornar serializado sem alias (apenas 'id')
            qr = QuestaoResponse.model_validate(questao_inserida)
            return qr.model_dump()
            
        except Exception as e:
            raise Exception(f"Erro ao adicionar questão: {str(e)}")
    
    def buscar_questao_por_id(self, questao_id: str):
        """Busca uma questão pelo ID"""
        try:
            questao = self.collection.find_one({"_id": ObjectId(questao_id)})
            if questao:
                # definir id e remover _id antes da validação
                questao["id"] = str(questao["_id"])
                if "_id" in questao:
                    del questao["_id"]
                for t in ("created_at", "updated_at"):
                    if t in questao and not isinstance(questao[t], str):
                        try:
                            questao[t] = questao[t].isoformat() + "Z"
                        except Exception:
                            questao[t] = str(questao[t])
                qr = QuestaoResponse.model_validate(questao)
                return qr.model_dump()
            return None
        except Exception as e:
            raise Exception(f"Erro ao buscar questão: {str(e)}")
        
    def listar_questoes(self):
        """Lista todas as questões"""
        try:
            questoes = []
            for questao in self.collection.find():
                questao["id"] = str(questao["_id"])
                if "_id" in questao:
                    del questao["_id"]
                for t in ("created_at", "updated_at"):
                    if t in questao and not isinstance(questao[t], str):
                        try:
                            questao[t] = questao[t].isoformat() + "Z"
                        except Exception:
                            questao[t] = str(questao[t])
                # reconstruir e serializar
                qr = QuestaoResponse.model_validate(questao)
                questoes.append(qr.model_dump())
            return questoes
        except Exception as e:
            raise Exception(f"Erro ao listar questões: {str(e)}")