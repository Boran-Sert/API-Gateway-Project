import os
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from dispatcher_app.core.router_manager import RouteManager
from dispatcher_app.core.authenticator import Authenticator
from shared.logging import setup_logging
from shared.middleware import LoggingMiddleware
from shared.exceptions import (
    ServiceUnavailableException,
    AppException,
    app_exception_handler,
)
from shared.metrics import setup_metrics

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTES_CONFIG = os.path.join(BASE_DIR, "routes.yaml")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
router_manager = RouteManager(ROUTES_CONFIG)
authenticator = Authenticator(AUTH_SERVICE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield


app = FastAPI(title="API Gateway (Dispatcher)", version="1.0.0", lifespan=lifespan)
logger = setup_logging("dispatcher")
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_exception_handler(AppException, app_exception_handler)
setup_metrics(app, "api-gateway")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "dispatcher"}


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def route_request(request: Request, path: str):
    full_path = f"/{path}"
    route = router_manager.get_route(full_path)
    if not route:
        if full_path in ["/docs", "/openapi.json"]:
            return Response(status_code=404, content="Endpoint not found")
        return Response(status_code=404, content="Endpoint not found")
    if route.get("require_auth", False):
        await authenticator.authenticate(request)
    query_params = str(request.query_params)
    target_url = router_manager.build_target_url(route, full_path, query_params)
    client: httpx.AsyncClient = request.app.state.http_client
    headers = dict(request.headers)
    if hasattr(request.state, "user_id"):
        headers["X-User-ID"] = str(request.state.user_id)
        headers["X-User-Email"] = request.state.user_email
        headers["X-User-Role"] = request.state.user_role
    headers.pop("host", None)
    try:
        rp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            timeout=30.0,
        )
    except httpx.RequestError as e:
        service_name = target_url.split("//")[1].split(":")[0]
        logger.error(f"Upstream request failed: {e}")
        raise ServiceUnavailableException(service_name)
    return Response(
        content=rp.content, status_code=rp.status_code, headers=dict(rp.headers)
    )
