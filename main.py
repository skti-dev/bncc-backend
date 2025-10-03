from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers.api_routes import router as api_router
from config.settings import settings
from connection import test_connection
import time
from fastapi.responses import JSONResponse
from services.auth_service import decode_token, AuthService
from services.erros import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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
    
    allow_paths = {"/", "/health", "/auth/login"}
    allow_prefixes = ()

    request.state.user = None

    # CORS preflight
    if request.method == "OPTIONS":
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"[REQ] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
        return response

    path = request.url.path

    if not (path in allow_paths or any(path.startswith(p) for p in allow_prefixes)):
        access_token = request.cookies.get("access_token")
        if not access_token:
            return JSONResponse(status_code=401, content={"error": {"code": 401, "message": "Not authenticated"}})
        try:
            payload = decode_token(access_token)
            user_id = payload.get("sub")
            if not user_id:
                return JSONResponse(status_code=401, content={"error": {"code": 401, "message": "Invalid token"}})
            service = AuthService()
            user = service.get_user_by_id(user_id)
            request.state.user = user
        except ValidationError as e:
            return JSONResponse(status_code=401, content={"error": {"code": 401, "message": str(e)}})
        except Exception:
            return JSONResponse(status_code=401, content={"error": {"code": 401, "message": "Authentication failed"}})

    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    print(f"[REQ] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    status = exc.status_code
    if status in (401, 403, 500):
        return JSONResponse(status_code=status, content={"error": {"code": status, "message": exc.detail}})
    return JSONResponse(status_code=status, content={"detail": exc.detail})


@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    status = exc.status_code
    if status in (401, 403, 500):
        return JSONResponse(status_code=status, content={"error": {"code": status, "message": exc.detail}})
    return JSONResponse(status_code=status, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"error": {"code": 500, "message": "Internal Server Error"}})

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