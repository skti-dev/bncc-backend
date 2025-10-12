from connection import get_collection
from models.resultado_model import ResultadoCreate, ResultadoResponse
from bson import ObjectId
from datetime import datetime, timezone
from config.settings import settings as app_settings
from services.erros import ServiceError


class ResultadoService:
    def __init__(self):
        self.collection = get_collection(app_settings.RESULTADOS_COLLECTION)

    def salvar_resultado(self, resultado_data: ResultadoCreate):
        """Salva um resultado ao banco de dados"""
        try:
            resultado_dict = resultado_data.model_dump(mode="json")
            
            percentual_acerto = (resultado_data.pontuacao / resultado_data.total_questoes) * 100 if resultado_data.total_questoes > 0 else 0.0
            resultado_dict['percentual_acerto'] = round(percentual_acerto, 2)
            
            now_iso = datetime.now(timezone.utc).isoformat()
            resultado_dict['created_at'] = now_iso
            resultado_dict['updated_at'] = now_iso
            
            result = self.collection.insert_one(resultado_dict)
            
            resultado_inserido = self.collection.find_one({"_id": result.inserted_id})
            if not resultado_inserido:
                raise ServiceError("Erro ao recuperar resultado inserido")
            
            return self._normalize_and_serialize(resultado_inserido)
            
        except Exception as e:
            raise ServiceError(f"Erro ao salvar resultado: {str(e)}")
    
    def buscar_resultado_por_id(self, resultado_id: str):
        """Busca um resultado pelo ID"""
        try:
            resultado = self.collection.find_one({"_id": ObjectId(resultado_id)})
            if resultado:
                return self._normalize_and_serialize(resultado)
            return None
        except Exception as e:
            raise ServiceError(f"Erro ao buscar resultado: {str(e)}")
        
    def listar_resultados(self):
        """Lista todos os resultados"""
        try:
            resultados = []
            for resultado in self.collection.find():
                resultados.append(self._normalize_and_serialize(resultado))
            return resultados
        except Exception as e:
            raise ServiceError(f"Erro ao listar resultados: {str(e)}")

    def _build_query(self, disciplina: str | None, ano: int | None, email: str | None) -> dict:
        """Constrói query de filtro"""
        query = {}
        
        if disciplina:
            query["disciplina"] = disciplina
        
        if ano:
            query["ano"] = ano
            
        if email:
            query["email"] = email
        
        return query

    def _calc_total_pages(self, total: int, limit: int) -> int:
        """Calcula total de páginas"""
        return (total + limit - 1) // limit if total > 0 else 0

    def _normalize_and_serialize(self, doc: dict) -> dict:
        """Normaliza documento do MongoDB e serializa"""
        doc["id"] = str(doc.get("_id"))
        if "_id" in doc:
            del doc["_id"]

        for timestamp_field in ("created_at", "updated_at"):
            if timestamp_field in doc and not isinstance(doc[timestamp_field], str):
                try:
                    doc[timestamp_field] = doc[timestamp_field].isoformat() + "Z"
                except Exception:
                    doc[timestamp_field] = str(doc[timestamp_field])

        resultado_response = ResultadoResponse.model_validate(doc)
        return resultado_response.model_dump(mode="json")

    def listar_resultados_paginated(self, page: int, limit: int, disciplina: str | None = None, ano: int | None = None, email: str | None = None) -> dict:
        """Lista resultados com paginação e filtro opcional por disciplina, ano e email"""
        
        try:
            if page < 1:
                return {"total": 0, "totalPages": 0, "page": page, "limit": limit, "data": []}

            query = self._build_query(disciplina, ano, email)
            
            total = self.collection.count_documents(query)
            total_pages = self._calc_total_pages(total, limit)
            
            if total_pages > 0 and page > total_pages:
                return {"total": total, "totalPages": total_pages, "page": page, "limit": limit, "data": []}

            skip = (page - 1) * limit
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            data = [self._normalize_and_serialize(resultado) for resultado in cursor]

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
            raise ServiceError(f"Erro ao listar resultados paginados: {str(e)}")
