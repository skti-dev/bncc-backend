import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGODB_PASS = os.getenv('MONGODB_PASS')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'bcnn_database')
    
    # API
    API_TITLE = "BCNN Backend API"
    API_DESCRIPTION = "API para gerenciamento de questões do BCNN"
    API_VERSION = "1.0.0"
    
    # Logs
    LOG_COLLECTION = "logs_api"
    QUESTOES_COLLECTION = "questoes"

settings = Settings()