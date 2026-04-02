FROM python:3.11-slim

# Python'ın /app dizinindeki modülleri (örn: shared) bulabilmesi için
ENV PYTHONPATH=/app

WORKDIR /app

# 1. Bağımlılıkları kopyala ve kur (önbellekleme için ayrı katman)
COPY dispatcher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Ortak 'shared' kütüphanesini kopyala
COPY shared /app/shared

# 3. dispatcher uygulamasının kaynak kodlarını kopyala
COPY dispatcher/. /app/

EXPOSE 8000

CMD ["uvicorn", "dispatcher_app.main:app", "--host", "0.0.0.0", "--port", "8000"]