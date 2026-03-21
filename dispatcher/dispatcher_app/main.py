""" Sistemin Ana uygulaması - Loglama ve Dashboard Destekli """
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
import httpx
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# --- VERİTABANI BAĞLANTISI (Veri İzolasyonu İsteri) ---
# Dispatcher'ın kendine ait izole NoSQL yapısı [cite: 65]
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo-dispatcher:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_database("dispatcher_db")
logs_collection = db.get_collection("traffic_logs")

class ServiceRegistry:
    """Tüm mikroservislerin adreslerini yöneten sınıf."""
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

app = FastAPI(title="API Gateway (Dispatcher) with Monitoring")
registry = ServiceRegistry()

# --- LOGLAMA FONKSİYONU ---
async def log_traffic(service: str, method: str, path: str, status: int):
    """Tüm trafiği NoSQL veri tabanına kaydeder [cite: 41, 68]"""
    await logs_collection.insert_one({
        "service": service,
        "method": method,
        "path": path,
        "status_code": status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# --- DASHBOARD (Görselleştirme İsteri) ---
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Trafik akışını tablo halinde sunan arayüz [cite: 68, 74]"""
    logs = await logs_collection.find().sort("_id", -1).limit(20).to_list(20)
    
    rows = ""
    for log in logs:
        # Hata durumlarını kırmızı göstererek görselleştirme kalitesini artırıyoruz
        color = "red" if log['status_code'] >= 400 else "green"
        rows += f"""
            <tr>
                <td>{log['timestamp']}</td>
                <td><strong>{log['service']}</strong></td>
                <td>{log['method']}</td>
                <td style="color: {color}; font-weight: bold;">{log['status_code']}</td>
                <td>{log['path']}</td>
            </tr>
        """

    return f"""
    <html>
        <head>
            <title>Dispatcher Traffic Monitor</title>
            <style>
                body {{ font-family: sans-serif; margin: 40px; background: #f4f7f6; }}
                table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #2c3e50; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 API Gateway Traffic Monitor</h1>
                <span>Son 20 İşlem (Canlı)</span>
            </div>
            <table>
                <thead><tr><th>Zaman</th><th>Hedef Servis</th><th>Metot</th><th>Durum Kodu</th><th>Yol</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "dispatcher"}

@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_request(service_name: str, path: str, request: Request):
    """Gelen isteği yönlendirir ve loglar [cite: 39, 47]"""
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
        
        # --- KRİTİK: Her isteği logluyoruz ---
        await log_traffic(service_name, request.method, path, response.status_code)

        return JSONResponse(
            content=response.json() if response.content else None,
            status_code=response.status_code,
            headers=dict(response.headers)
        )