from connection import get_collection
from models.questao_model import QuestaoCreate
from bson import ObjectId
from datetime import datetime

class QuestaoService:
    def __init__(self):
        self.collection = get_collection('questoes')
    
    def adicionar_questao(self, questao_data: QuestaoCreate):
        """Adiciona uma nova questão ao banco de dados"""
        try:
            # Converter para dict
            questao_dict = questao_data.model_dump()
            
            # Adicionar timestamp
            questao_dict['created_at'] = datetime.utcnow()
            questao_dict['updated_at'] = datetime.utcnow()
            
            # Inserir no MongoDB
            result = self.collection.insert_one(questao_dict)
            
            # Retornar o documento inserido
            questao_inserida = self.collection.find_one({"_id": result.inserted_id})
            questao_inserida["_id"] = str(questao_inserida["_id"])
            
            return questao_inserida
            
        except Exception as e:
            raise Exception(f"Erro ao adicionar questão: {str(e)}")
    
    def buscar_questao_por_id(self, questao_id: str):
        """Busca uma questão pelo ID"""
        try:
            questao = self.collection.find_one({"_id": ObjectId(questao_id)})
            if questao:
                questao["_id"] = str(questao["_id"])
            return questao
        except Exception as e:
            raise Exception(f"Erro ao buscar questão: {str(e)}")