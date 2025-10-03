from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers.api_routes import router as api_router
from config.settings import settings
from connection import test_connection
import time

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
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    print(f"[REQ] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    return response

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    print("Starting BCNN Backend API...")
    if test_connection():
        print("Connection to MongoDB established!")
    else:
        print("Failed to connect to MongoDB!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)