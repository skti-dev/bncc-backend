from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers.api_routes import router as api_router
from config.settings import settings
from connection import test_connection
import time
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from services.log_service import LogService
from services.log_service_async import LogServiceAsync
import traceback
from services.auth_service import decode_token, AuthService
from services.erros import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import HTTPException as FastAPIHTTPException


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# CONFIGURAÇÃO CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "https://enhancing-desired-efforts-reseller.trycloudflare.com/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _write_log_async(log_svc_async: LogServiceAsync | None, sync_svc: LogService, origem: str, resultado: str, endpoint: str | None, detalhes: dict | None):
    if log_svc_async and hasattr(log_svc_async, "log_consumo"):
        try:
            return await log_svc_async.log_consumo(origem_consumo=origem, resultado_consumo=resultado, endpoint=endpoint, detalhes=detalhes)
        except Exception:
            pass
    try:
        return await run_in_threadpool(sync_svc.log_consumo, origem, resultado, endpoint, detalhes)
    except Exception:
        return None


async def _log_preflight(log_svc_async, sync_svc, request: Request, path: str):
    detalhes_pf = {"method": request.method, "path": path, "query": None, "client": request.client.host if request.client else None}
    await _write_log_async(log_svc_async, sync_svc, "middleware", "preflight", path, detalhes_pf)


async def _log_unauthenticated(log_svc_async, sync_svc, request: Request, path: str, query: str, client_host: str):
    detalhes_na = {"method": request.method, "path": path, "query": query, "client": client_host}
    await _write_log_async(log_svc_async, sync_svc, "middleware", "unauthenticated", path + (f"?{query}" if query else ""), detalhes_na)


async def _log_invalid_token(log_svc_async, sync_svc, request: Request, path: str, query: str, client_host: str):
    detalhes_it = {"method": request.method, "path": path, "query": query, "client": client_host}
    await _write_log_async(log_svc_async, sync_svc, "middleware", "invalid_token", path + (f"?{query}" if query else ""), detalhes_it)


async def _log_validation_error(log_svc_async, sync_svc, request: Request, path: str, query: str, client_host: str, validation: str):
    detalhes_val = {"method": request.method, "path": path, "query": query, "client": client_host, "validation": validation}
    await _write_log_async(log_svc_async, sync_svc, "middleware", "validation_error", path + (f"?{query}" if query else ""), detalhes_val)


async def _log_unhandled_exception(log_svc_async, sync_svc, path: str, query: str, exc: Exception):
    detalhes = {"error": "unhandled_exception", "exception": str(exc), "trace": traceback.format_exc()}
    await _write_log_async(log_svc_async, sync_svc, "middleware", "error", path + (f"?{query}" if query else ""), detalhes)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    allow_paths = {"/", "/health", "/auth/login"}
    allow_prefixes = ()

    request.state.user = None

    path = request.url.path
    query = str(request.url.query) if request.url.query else None
    client_host = request.client.host if request.client else None
    sync_log_service = LogService()
    async_log_service = LogServiceAsync()

    # CORS preflight
    if request.method == "OPTIONS":
        response = await call_next(request)
        process_time = time.time() - start_time
        try:
            await _log_preflight(async_log_service, sync_log_service, request, path)
        except Exception:
            pass
        print(f"[REQ] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
        return response

    if not (path in allow_paths or any(path.startswith(p) for p in allow_prefixes)):
        access_token = request.cookies.get("access_token")
        if not access_token:
            await _log_unauthenticated(async_log_service, sync_log_service, request, path, query, client_host)
            return JSONResponse(status_code=401, content={"error": {"code": 401, "message": "Not authenticated"}})
        try:
            payload = decode_token(access_token)
            user_id = payload.get("sub")
            if not user_id:
                await _log_invalid_token(async_log_service, sync_log_service, request, path, query, client_host)
                return JSONResponse(status_code=401, content={"error": {"code": 401, "message": "Invalid token"}})
            service = AuthService()
            user = service.get_user_by_id(user_id)
            request.state.user = user
        except ValidationError as e:
            await _log_validation_error(async_log_service, sync_log_service, request, path, query, client_host, str(e))
            return JSONResponse(status_code=401, content={"error": {"code": 401, "message": str(e)}})
        except Exception as e:
            # Log authentication failure
            detalhes = {"error": "authentication_failed", "exception": str(e), "trace": traceback.format_exc()}
            await _write_log_async(async_log_service, sync_log_service, "middleware", "failure", path, detalhes)
            return JSONResponse(status_code=401, content={"error": {"code": 401, "message": "Authentication failed"}})

    try:
        response = await call_next(request)
    except Exception as exc:
        # Log and re-raise
        try:
            await _log_unhandled_exception(async_log_service, sync_log_service, path, query, exc)
        except Exception:
            pass
        raise

    process_time = time.time() - start_time

    # Build log details
    try:
        user_info = None
        if hasattr(request.state, "user") and request.state.user:
            user = request.state.user
            user_info = {"id": user.get("id") if isinstance(user, dict) else None, "email": user.get("email") if isinstance(user, dict) else None}
    except Exception:
        user_info = None

    detalhes = {"method": request.method, "path": path, "query": query, "client": client_host, "user": user_info, "status_code": getattr(response, "status_code", None), "duration_s": f"{process_time:.3f}"}

    try:
        await _write_log_async(async_log_service, sync_log_service, "api", "success", path + (f"?{query}" if query else ""), detalhes)
    except Exception:
        pass

    print(f"[REQ] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    status = exc.status_code
    if status in (401, 403, 500):
        return JSONResponse(status_code=status, content={"error": {"code": status, "message": exc.detail}})
    return JSONResponse(status_code=status, content={"detail": exc.detail})


@app.exception_handler(FastAPIHTTPException)
async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
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