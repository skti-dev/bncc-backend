import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGODB_PASS = os.getenv('MONGODB_PASS')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'appDB')
    MONGODB_USER = os.getenv('MONGODB_USER', 'appLink')
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'db-pi-v.b1go26j.mongodb.net')
    
    # API
    API_TITLE = "BCNN Backend API"
    API_DESCRIPTION = "API para gerenciamento de questões do BCNN"
    API_VERSION = "1.0.0"
    
    # Logs
    LOG_COLLECTION = "LOGS"
    QUESTOES_COLLECTION = "QUESTOES"

settings = Settings()