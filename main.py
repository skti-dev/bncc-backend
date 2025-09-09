from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers.questao_routes import router as questao_router
from config.settings import settings
from connection import test_connection
import time

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Processar request
    response = await call_next(request)
    
    # Calcular tempo de processamento
    process_time = time.time() - start_time
    
    # Log básico (pode ser expandido)
    print(f"📝 {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    return response

# Incluir routers
app.include_router(questao_router)

# Rota de health check
@app.get("/")
async def health_check():
    """Verifica se a API está funcionando"""
    return {
        "message": "BCNN Backend API está funcionando!",
        "version": settings.API_VERSION,
        "status": "online"
    }

@app.get("/health")
async def detailed_health_check():
    """Verifica saúde da aplicação incluindo MongoDB"""
    mongodb_status = "online" if test_connection() else "offline"
    
    return {
        "api_status": "online",
        "mongodb_status": mongodb_status,
        "version": settings.API_VERSION
    }

# Evento de inicialização
@app.on_event("startup")
async def startup_event():
    print("🚀 Iniciando BCNN Backend API...")
    if test_connection():
        print("✅ Conexão com MongoDB estabelecida!")
    else:
        print("❌ Falha na conexão com MongoDB!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)