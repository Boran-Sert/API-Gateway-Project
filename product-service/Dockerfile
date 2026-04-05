FROM python:3.11-slim

ENV PYTHONPATH=/app

WORKDIR /app

COPY product-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY product-service/. /app/

EXPOSE 8003

CMD ["uvicorn", "product_service_app.main:app", "--host", "0.0.0.0", "--port", "8003"]