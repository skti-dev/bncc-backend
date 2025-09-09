from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_pass = os.getenv('MONGODB_PASS')
database_name = os.getenv('DATABASE_NAME', 'bncc_database')

uri = f"mongodb+srv://augustotseabra79_db_user:{mongodb_pass}@bncc-cluster.omelecl.mongodb.net/?retryWrites=true&w=majority&appName=BNCC-Cluster"

# Criar cliente MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))

# Exportar o banco de dados
database = client[database_name]

def get_database():
    """Retorna a instância do banco de dados"""
    return database

def get_collection(collection_name: str):
    """Retorna uma coleção específica do banco"""
    return database[collection_name]

def list_databases():
    """Lista todos os databases disponíveis"""
    try:
        databases = client.list_database_names()
        print("📂 Databases disponíveis:")
        for db in databases:
            print(f"  - {db}")
        return databases
    except Exception as e:
        print(f"❌ Erro ao listar databases: {e}")
        return []

def test_connection():
    """Testa a conexão com MongoDB"""
    try:
        client.admin.command('ping')
        print("✅ Pinged your deployment. You successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def close_connection():
    """Fecha a conexão com MongoDB"""
    client.close()

if __name__ == "__main__":
    print("🔌 Testando conexão com MongoDB...")
    if test_connection():
        list_databases()