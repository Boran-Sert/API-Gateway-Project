FROM python:3.11-slim

ENV PYTHONPATH=/app

WORKDIR /app

COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY user-service/. /app/

EXPOSE 8002

CMD ["uvicorn", "user_service_app.main:app", "--host", "0.0.0.0", "--port", "8002"]