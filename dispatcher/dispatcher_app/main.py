""" 
🚀 API Gateway (Dispatcher) - Stabil Sürüm 
Yetkilendirme, Akıllı Yönlendirme ve Dashboard Desteği 
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator
import httpx
import os
import redis
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# --- 1. BAĞLANTILAR VE AYARLAR ---
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo-dispatcher:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_database("dispatcher_db")
logs_collection = db.get_collection("traffic_logs")

# Redis bağlantısı (Container ismine dikkat: redis-cache)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis-cache"), 
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
            raise HTTPException(status_code=404, detail=f"Servis tanımlı değil: {service_name}")
        return self._services[service_name]

app = FastAPI(title="API Gateway (Dispatcher)")
Instrumentator().instrument(app).expose(app)
registry = ServiceRegistry()

# --- 2. AUTH MIDDLEWARE (GÜVENLİ GEÇİŞ) ---
async def verify_token(request: Request):
    path = request.url.path
    
    # Şifresiz geçebilecek yollar
    public_paths = ["auth/login", "auth/register", "/dashboard", "/metrics", "/health"]
    if any(p in path for p in public_paths):
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Oturum açmanız gerekiyor (Token eksik)")

    token = auth_header.split(" ")[1]
    
    try:
        # Redis'ten session bilgisini çek
        user_session = redis_client.get(f"token:{token}")
        
        if not user_session:
            raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş oturum")
        
        return json.loads(user_session)
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Yetkilendirme sistemi (Redis) hatası")

# --- 3. LOGLAMA VE DASHBOARD ---
async def log_traffic(service: str, method: str, path: str, status: int):
    await logs_collection.insert_one({
        "service": service,
        "method": method,
        "path": path,
        "status_code": status,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    logs = await logs_collection.find().sort("_id", -1).limit(30).to_list(30)
    rows = "".join([
        f"<tr><td>{l['timestamp']}</td><td><b>{l['service'].upper()}</b></td><td>{l['method']}</td>"
        f"<td style='color: {'#ff4444' if l['status_code']>=400 else '#00c851'}; font-weight:bold;'>{l['status_code']}</td>"
        f"<td>{l['path']}</td></tr>" for l in logs
    ])

    return f"""
    <html><head><title>Monitor</title><style>
    body {{ font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; padding: 40px; }}
    table {{ width: 100%; border-collapse: collapse; background: #1e1e1e; border-radius: 8px; }}
    th, td {{ padding: 15px; border-bottom: 1px solid #333; text-align: left; }}
    th {{ background: #007acc; color: white; }}
    tr:hover {{ background: #2d2d2d; }}
    </style></head><body>
    <h1>🚀 API Gateway Traffic Monitor</h1>
    <table><thead><tr><th>Zaman</th><th>Hedef Servis</th><th>Metot</th><th>Durum</th><th>Yol</th></tr></thead>
    <tbody>{rows}</tbody></table></body></html>
    """

# --- 4. ANA YÖNLENDİRİCİ (DİNAMİK ROUTER) ---
@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_request(service_name: str, path: str, request: Request, user_data: dict = Depends(verify_token)):
    base_url = registry.get_service_url(service_name)
    
    # 💡 KRİTİK: Sondaki '/' işaretini siliyoruz (307 Redirect'i önlemek için)
    clean_path = path.rstrip("/")
    target_url = f"{base_url}/{service_name}/{clean_path}"
    
    print(f"DEBUG: {request.method} isteği -> {target_url}")

    # 💡 KRİTİK: follow_redirects=True sayesinde 307 hataları otomatik çözülür
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as http_client:
        body = await request.body()
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
        
        try:
            response = await http_client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                params=request.query_params
            )
            
            await log_traffic(service_name, request.method, path, response.status_code)
            
            # Yanıt içeriğini JSON olarak dönmeye çalış, olmazsa text dön
            try:
                resp_content = response.json()
            except:
                resp_content = {"detail": response.text}

            return JSONResponse(content=resp_content, status_code=response.status_code)
            
        except httpx.RequestError as exc:
            await log_traffic(service_name, request.method, path, 503)
            print(f"DEBUG: Bağlantı Hatası -> {str(exc)}")
            raise HTTPException(status_code=503, detail=f"Servis ulaşılamıyor: {service_name}")