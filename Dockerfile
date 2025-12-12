FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai_observability ./ai_observability
ENV PORT=8000
CMD ["uvicorn", "ai_observability.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
