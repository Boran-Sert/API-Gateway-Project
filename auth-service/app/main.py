from fastapi import FastAPI, Request
from shared.exceptions import AppException, app_exception_handler
from shared.middleware import RequestLoggingMiddleware
from shared.metrics import setup_metrics
from app.api.router import router 

app = FastAPI(title="Auth Service", version="1.0.0")

# Shared Library Entegrasyonu
app.add_exception_handler(AppException, app_exception_handler)
app.add_middleware(RequestLoggingMiddleware)
setup_metrics(app, service_name="auth-service")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth-service"}

app.include_router(router)    
