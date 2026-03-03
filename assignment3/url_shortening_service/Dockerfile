FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8100

CMD ["gunicorn", "--bind", "0.0.0.0:8100", "--workers", "2", "--timeout", "60", "rest_service:app"]
