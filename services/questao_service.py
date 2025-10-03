from connection import get_collection
from models.questao_model import QuestaoCreate
from bson import ObjectId
from datetime import datetime, timezone
from models.questao_model import QuestaoResponse
from config.settings import settings as app_settings
from services.erros import ServiceError


class QuestaoService:
    def __init__(self):
        self.collection = get_collection(app_settings.QUESTOES_COLLECTION)

    def adicionar_questao(self, questao_data: QuestaoCreate):
        """Adiciona uma nova questão ao banco de dados"""
        try:
            questao_dict = questao_data.model_dump(mode="json")
            
            now_iso = datetime.now(timezone.utc).isoformat()
            questao_dict['created_at'] = now_iso
            questao_dict['updated_at'] = now_iso
            
            result = self.collection.insert_one(questao_dict)
            
            questao_inserida = self.collection.find_one({"_id": result.inserted_id})
            questao_inserida["id"] = str(questao_inserida["_id"])
            
            if "_id" in questao_inserida:
                del questao_inserida["_id"]

            for t in ("created_at", "updated_at"):
                if t in questao_inserida and not isinstance(questao_inserida[t], str):
                    try:
                        questao_inserida[t] = questao_inserida[t].isoformat() + "Z"
                    except Exception:
                        questao_inserida[t] = str(questao_inserida[t])

            qr = QuestaoResponse.model_validate(questao_inserida)
            return qr.model_dump(mode="json")
            
        except Exception as e:
            raise ServiceError(f"Erro ao adicionar questão: {str(e)}")
    
    def buscar_questao_por_id(self, questao_id: str):
        """Busca uma questão pelo ID"""
        try:
            questao = self.collection.find_one({"_id": ObjectId(questao_id)})
            if questao:
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
                return qr.model_dump(mode="json")
            return None
        except Exception as e:
            raise ServiceError(f"Erro ao buscar questão: {str(e)}")
        
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

                qr = QuestaoResponse.model_validate(questao)
                questoes.append(qr.model_dump(mode="json"))
            return questoes
        except Exception as e:
            raise ServiceError(f"Erro ao listar questões: {str(e)}")

    def _build_query(self, disc: str | None) -> dict:
        return {"disciplina": disc} if disc else {}

    def _calc_total_pages(self, total: int, lim: int) -> int:
        return (total + lim - 1) // lim if total > 0 else 0

    def _normalize_and_serialize(self, doc: dict) -> dict:
        doc["id"] = str(doc.get("_id"))
        if "_id" in doc:
            del doc["_id"]

        for t in ("created_at", "updated_at"):
            if t in doc and not isinstance(doc[t], str):
                try:
                    doc[t] = doc[t].isoformat() + "Z"
                except Exception:
                    doc[t] = str(doc[t])

        qr = QuestaoResponse.model_validate(doc)
        return qr.model_dump(mode="json")

    def listar_questoes_paginated(self, page: int, limit: int, disciplina: str | None = None):
        """Lista questões com paginação e filtro opcional por disciplina.

        Retorna um dict: { 'total': int, 'totalPages': int, 'page': int, 'limit': int, 'data': list }
        """

        try:
            if page < 1:
                return {"total": 0, "totalPages": 0, "page": page, "limit": limit, "data": []}

            query = self._build_query(disciplina)
            total = self.collection.count_documents(query)
            total_pages = self._calc_total_pages(total, limit)

            if total_pages > 0 and page > total_pages:
                return {"total": total, "totalPages": total_pages, "page": page, "limit": limit, "data": []}

            skip = (page - 1) * limit
            cursor = self.collection.find(query).skip(skip).limit(limit)

            data = [self._normalize_and_serialize(q) for q in cursor]

            return {
                "total": total,
                "totalPages": total_pages,
                "page": page,
                "limit": limit,
                "hasNext": page < total_pages,
                "hasPrev": page > 1 and total_pages > 0,
                "data": data,
            }
        except Exception as e:
            raise ServiceError(f"Erro ao listar questões paginadas: {str(e)}")