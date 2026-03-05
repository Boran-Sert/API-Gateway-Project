""" Sistemin Ana uygulaması """
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI(title = "API Gateaway (Dispatcher)")

# Servis URL leri dockerdan veya ortam değişkenleriden alınıyor

SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"), 
    "users": os.getenv("USER_SERVICE_URL", "http://user-service:8002"),
    "products": os.getenv("PRODUCT_SERVICE_URL","http://product-service:8003")
}

@app.get("/health")
async def health_check():
    """ Gateway çalışıyor mu kontrol eder """
    return {"status": "ok", "service": "dispatcher"}

@app.api_route("/api/{service_name}/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def route_request(service_name: str, path: str, request: Request):
    """ Gelen istekleri yönlendirir """
    if service_name not in SERVICES:
        # Eğer olmayan servis isternirse 404 döner
        raise HTTPException(status_code = 404, detail= "Servis bulunamadı")

    # Hedef URL oluştur
    # Hedef URL oluştur ('/api/users/profile' -> 'profile' path olur, '/api/users' için path boştur)
    # Target URL'ye her zaman service_name (örn: /users) eklenir. Test: http://user-service:8002/users
    target_url = f"{SERVICES[service_name]}/{service_name}/{path}" if path else f"{SERVICES[service_name]}/{service_name}"


    # HTTP isteği ile trafik oluştur
    async with httpx.AsyncClient() as client:

        # Gelen body oku
        body = await request.body()

        # İstek hedef servise iletirilir
        response = await client.request(
            method = request.method,
            url = target_url,
            headers = dict(request.headers),
            content = body,
            params = request.query_params
        )

        return JSONResponse(
            content=response.json() if response.content else None,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
