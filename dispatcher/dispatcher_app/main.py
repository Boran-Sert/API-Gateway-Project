""" Sistemin Ana uygulaması - Loglama, Dashboard ve Merkezi Yetkilendirme Destekli """
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
import httpx
import os
import redis
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# --- VERİTABANI BAĞLANTILARI ---
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo-dispatcher:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_database("dispatcher_db")
logs_collection = db.get_collection("traffic_logs")

# Redis Bağlantısı (Merkezi Yetkilendirme için)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"), 
    port=int(os.getenv("REDIS_PORT", 6379)), 
    decode_responses=True
)

class ServiceRegistry:
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

app = FastAPI(title="API Gateway (Dispatcher) with Auth & Monitoring")
registry = ServiceRegistry()

# --- AUTH MIDDLEWARE (Faz 8.1) ---
async def verify_token(request: Request):
    """Her istekte token'ı Redis üzerinden doğrular"""
    # Halka açık yolları muaf tutuyoruz
    if request.url.path in ["/health", "/dashboard", "/api/auth/login", "/api/auth/register"]:
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Erişim reddedildi: Token bulunamadı")

    token = auth_header.split(" ")[1]
    user_session = redis_client.get(f"token:{token}")
    
    if not user_session:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş oturum")
    
    return json.loads(user_session)

# --- LOGLAMA VE DASHBOARD FONKSİYONLARI ---
async def log_traffic(service: str, method: str, path: str, status: int):
    await logs_collection.insert_one({
        "service": service,
        "method": method,
        "path": path,
        "status_code": status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    logs = await logs_collection.find().sort("_id", -1).limit(20).to_list(20)
    rows = ""
    for log in logs:
        color = "red" if log['status_code'] >= 400 else "green"
        rows += f"""<tr><td>{log['timestamp']}</td><td><strong>{log['service']}</strong></td><td>{log['method']}</td><td style="color: {color}; font-weight: bold;">{log['status_code']}</td><td>{log['path']}</td></tr>"""

    return f"<html><head><title>Monitor</title><style>body {{ font-family: sans-serif; margin: 40px; background: #f4f7f6; }} table {{ width: 100%; border-collapse: collapse; background: white; }} th, td {{ padding: 12px; border-bottom: 1px solid #ddd; }} th {{ background: #2c3e50; color: white; }}</style></head><body><h1>🚀 API Gateway Traffic Monitor</h1><table><thead><tr><th>Zaman</th><th>Hedef Servis</th><th>Metot</th><th>Durum Kodu</th><th>Yol</th></tr></thead><tbody>{rows}</tbody></table></body></html>"

@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_request(service_name: str, path: str, request: Request, user_data: dict = Depends(verify_token)):
    """Gelen isteği yetkilendirir, yönlendirir ve loglar"""
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
        
        await log_traffic(service_name, request.method, path, response.status_code)
        return JSONResponse(content=response.json() if response.content else None, status_code=response.status_code, headers=dict(response.headers))