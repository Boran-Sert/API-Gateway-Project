import os
import httpx
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager

from shared.logging import setup_logging
from shared.middleware import LoggingMiddleware
from shared.metrics import setup_metrics
from shared.exceptions import ServiceUnavailableException, UnauthorizedException, AppException, app_exception_handler

# --- Service URLs from Environment ---
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")

# --- Lifespan for HTTPX client ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create a single, reusable HTTP client for the application's lifespan
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield

# --- FastAPI App Setup ---
app = FastAPI(
    title="API Gateway (Dispatcher)",
    version="1.0.0",
    lifespan=lifespan
)

logger = setup_logging("dispatcher")
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_exception_handler(AppException, app_exception_handler)
setup_metrics(app, "dispatcher")

# --- Authentication Middleware ---
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    public_paths = ["/api/auth/login", "/api/auth/register", "/docs", "/openapi.json", "/health", "/metrics"]
    if any(request.url.path.startswith(p) for p in public_paths):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise UnauthorizedException("Authorization header missing")

    try:
        client: httpx.AsyncClient = request.app.state.http_client
        validate_url = f"{AUTH_SERVICE_URL}/auth/validate"
        headers = {"Authorization": auth_header}
        
        resp = await client.post(validate_url, headers=headers)
        resp.raise_for_status()
        
        user_data = resp.json()
        
        # Add user info to request state for the routing function to use
        request.state.user_id = user_data.get("user_id")
        request.state.user_email = user_data.get("email")
        request.state.user_role = user_data.get("role")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise UnauthorizedException()
        else:
            logger.error(f"Auth service validation error: {e.response.text}")
            raise ServiceUnavailableException("Auth Service")
    except httpx.RequestError:
        raise ServiceUnavailableException("Auth Service")

    return await call_next(request)


# --- Dynamic Routing Logic ---
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_request(request: Request, path: str):
    client: httpx.AsyncClient = request.app.state.http_client

    target_url = None
    if path.startswith("auth/"):
        target_url = f"{AUTH_SERVICE_URL}/{path}"
    elif path.startswith("products"):
        target_url = f"{PRODUCT_SERVICE_URL}/{path}"
    elif path.startswith("users/"):
        target_url = f"{USER_SERVICE_URL}/{path}"

    if not target_url:
        return Response(status_code=404, content="Endpoint not found")

    headers = dict(request.headers)
    if hasattr(request.state, 'user_id'):
        headers["X-User-ID"] = request.state.user_id
        headers["X-User-Email"] = request.state.user_email
        headers["X-User-Role"] = request.state.user_role
    
    headers.pop("host", None)

    try:
        rp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
            timeout=30.0,
        )
    except httpx.RequestError:
        service_name = target_url.split('//')[1].split(':')[0]
        raise ServiceUnavailableException(service_name)

    return Response(content=rp.content, status_code=rp.status_code, headers=dict(rp.headers))

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "dispatcher"}