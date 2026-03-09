# 1. Python imajını kullan
FROM python:3.11-slim

# 2. Çalışma dizinini ayarla
WORKDIR /app

# 3. Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Tüm kodları kopyala
COPY . .

# 5. Uygulamayı başlat (Boran'ın portu 8002'ydi)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]