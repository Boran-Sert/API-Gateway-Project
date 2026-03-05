""" Sistemin Ana uygulaması """
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os

class ServiceRegistry:
    """Tüm mikroservislerin adreslerini yöneten sınıf (Single Responsibility)."""
    def __init__(self):
        self._services = {
            "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
            "users": os.getenv("USER_SERVICE_URL", "http://user-service:8002"),
            "products": os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8003"),
        }
        
    def get_service_url(self, service_name: str) -> str:
        if service_name not in self._services:
            raise HTTPException(status_code=404, detail="Service not found")
        return self._services[service_name]

# Uygulama ve Bağımlılıklar başlatılıyor
app = FastAPI(title="API Gateway (Dispatcher)")
registry = ServiceRegistry()

@app.get("/health")
async def health_check():
    """ Gateway çalışıyor mu kontrol eder """
    return {"status": "ok", "service": "dispatcher"}

@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_request(service_name: str, path: str, request: Request):
    """Gelen isteği yakalar ve ServiceRegistry'den adresi bulup yönlendirir."""
    
    base_url = registry.get_service_url(service_name)
    target_url = f"{base_url}/{service_name}/{path}" if path else f"{base_url}/{service_name}"
    
    async with httpx.AsyncClient() as client:
        body = await request.body()
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            content=body,
            params=request.query_params
        )
        return JSONResponse(
            content=response.json() if response.content else None,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
