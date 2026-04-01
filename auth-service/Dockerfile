FROM python:3.11-slim

WORKDIR /app

# 1. requirements.txt dosyasını ana dizinden auth-service içine bakarak kopyala
COPY auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY auth-service /app

EXPOSE 8001

CMD ["uvicorn", "auth_app.main:app", "--host", "0.0.0.0", "--port", "8001"]