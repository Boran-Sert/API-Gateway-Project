FROM python:3.11-slim

# Python'ın /app dizinindeki modülleri (örn: shared) bulabilmesi için
ENV PYTHONPATH=/app

WORKDIR /app

# 1. Bağımlılıkları kopyala ve kur (önbellekleme için ayrı katman)
COPY auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Ortak 'shared' kütüphanesini kopyala
COPY shared /app/shared

# 3. auth-service uygulamasının kaynak kodlarını kopyala
COPY auth-service/. /app/

EXPOSE 8001

CMD ["uvicorn", "auth_app.main:app", "--host", "0.0.0.0", "--port", "8000"]