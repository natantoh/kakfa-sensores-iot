FROM python:3.11.9-slim-bookworm

WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "producer.py"]