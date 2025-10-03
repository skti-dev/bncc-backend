from connection import get_collection
from datetime import datetime
from config.settings import settings as app_settings

class LogService:
    def __init__(self):
        self.collection = get_collection(app_settings.LOG_COLLECTION)

    def log_consumo(self, origem_consumo: str, resultado_consumo: str, endpoint: str = None, detalhes: str = None):
        """Registra o consumo da API"""
        try:
            now_iso = datetime.utcnow().isoformat() + "Z"
            log_data = {
                "origem_consumo": origem_consumo,
                "resultado_consumo": resultado_consumo,
                "endpoint": endpoint,
                "detalhes": detalhes,
                "timestamp": now_iso
            }
            
            result = self.collection.insert_one(log_data)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Erro ao registrar log: {e}")
            return None
    
    def buscar_logs(self, limite: int = 100):
        """Busca os logs mais recentes"""
        try:
            logs = list(self.collection.find().sort("timestamp", -1).limit(limite))
            for log in logs:
                log["id"] = str(log["_id"]) if "_id" in log else log.get("id")
                if "_id" in log:
                    del log["_id"]
                if "timestamp" in log and not isinstance(log["timestamp"], str):
                    try:
                        log["timestamp"] = log["timestamp"].isoformat() + "Z"
                    except Exception:
                        log["timestamp"] = str(log["timestamp"])
            return logs
        except Exception as e:
            print(f"❌ Erro ao buscar logs: {e}")
            return []
    
    def buscar_logs_por_origem(self, origem: str, limite: int = 50):
        """Busca logs por origem específica"""
        try:
            logs = list(
                self.collection.find({"origem_consumo": origem})
                .sort("timestamp", -1)
                .limit(limite)
            )
            for log in logs:
                log["id"] = str(log["_id"]) if "_id" in log else log.get("id")
                if "_id" in log:
                    del log["_id"]
                if "timestamp" in log and not isinstance(log["timestamp"], str):
                    try:
                        log["timestamp"] = log["timestamp"].isoformat() + "Z"
                    except Exception:
                        log["timestamp"] = str(log["timestamp"])
            return logs
        except Exception as e:
            print(f"❌ Erro ao buscar logs por origem: {e}")
            return []