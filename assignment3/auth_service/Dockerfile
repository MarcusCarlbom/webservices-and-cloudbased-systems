FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8101

CMD ["gunicorn", "--bind", "0.0.0.0:8101", "--workers", "2", "--timeout", "60", "auth_rest_service:app"]
