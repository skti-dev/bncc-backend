from connection import get_async_collection
from datetime import datetime
from config.settings import settings as app_settings


class LogServiceAsync:
    def __init__(self):
        self.collection = get_async_collection(app_settings.LOG_COLLECTION)

    async def log_consumo(self, origem_consumo: str, resultado_consumo: str, endpoint: str = None, detalhes: dict | None = None):
        """Registra o consumo da API de forma assíncrona"""
        if self.collection is None:
            return None
        try:
            now_iso = datetime.utcnow().isoformat() + "Z"
            detalhes_json = detalhes if isinstance(detalhes, dict) else {"raw": str(detalhes)}
            log_data = {
                "origem_consumo": origem_consumo,
                "resultado_consumo": resultado_consumo,
                "endpoint": endpoint,
                "detalhes": detalhes_json,
                "timestamp": now_iso
            }
            result = await self.collection.insert_one(log_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Erro ao registrar log async: {e}")
            return None

    async def buscar_logs(self, limite: int = 100, skip: int = 0):
        if self.collection is None:
            return []
        try:
            cursor = self.collection.find().sort("timestamp", -1).skip(skip).limit(limite)
            items = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"]) if "_id" in doc else doc.get("id")
                if "_id" in doc:
                    del doc["_id"]
                items.append(doc)
            return items
        except Exception as e:
            print(f"❌ Erro ao buscar logs async: {e}")
            return []
