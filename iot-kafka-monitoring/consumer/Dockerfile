FROM python:3.11.9-slim-bookworm

WORKDIR /app

# Instala dependências de sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copia requirements.txt e utils da pasta pai (contexto definido no compose)
COPY requirements.txt .
COPY utils ./utils
COPY config ./config
COPY consumer ./consumer

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "consumer.consumer"]