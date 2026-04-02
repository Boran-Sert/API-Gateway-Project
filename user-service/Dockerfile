FROM python:3.11-slim

# Python'ın /app dizinindeki modülleri (örn: shared) bulabilmesi için
ENV PYTHONPATH=/app

WORKDIR /app

# 1. Bağımlılıkları kopyala ve kur (önbellekleme için ayrı katman)
COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Ortak 'shared' kütüphanesini kopyala
COPY shared /app/shared

# 3. user-service uygulamasının kaynak kodlarını kopyala
COPY user-service/. /app/

EXPOSE 8002

CMD ["uvicorn", "user_service_app.main:app", "--host", "0.0.0.0", "--port", "8002"]