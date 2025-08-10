FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY knowledge_base/ ./knowledge_base/

RUN mkdir -p uploads

EXPOSE 8000

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]