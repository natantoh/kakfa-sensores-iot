# kakfa-sensores-iot
# IoT Sensor Monitoring with Kafka and PostgreSQL

This project demonstrates a system for monitoring IoT sensors using Kafka as a message broker and PostgreSQL for data storage.

## Architecture

1. **Producer**: Generates fake sensor data and sends to Kafka topic
2. **Kafka**: Message broker for real-time data streaming
3. **Consumer**: Processes messages from Kafka and stores in PostgreSQL
4. **PostgreSQL**: Database for persistent storage of sensor data

## Setup

1. Install Docker and Docker Compose
2. Clone this repository
3. Create `.env` file if needed (see `.env.example`)

## Running the System

1. Start containers:
   ```bash
   docker-compose up -d
   ```

2. Create database tables (run once):
   ```bash
    python -c "from db.models import create_tables; create_tables()"
   ```
3. Run producer:
 ```bash
    python producer/producer.py
 ```
4. Run consumer:
 ```bash
   python consumer/consumer.py
 ```

## Access Services
  Kafka UI: http://localhost:8080
  PostgreSQL:
  Host: localhost
  Port: 5432
  Database: iotdb
  User: iotuser
  Password: iotpassword

## Como Usar o Sistema
  1. Inicie todos os serviços com `docker-compose up -d`
  2. Crie as tabelas no PostgreSQL executando o comando para criar tabelas
  3. Execute o producer para começar a gerar dados
  4. Execute o consumer para processar e armazenar os dados

  O sistema irá:
  - Gerar dados falsos de sensores IoT (temperatura, umidade, etc.)
  - Enviar esses dados para um tópico Kafka
  - Consumir os dados do Kafka
  - Armazenar os dados no PostgreSQL

Você pode monitorar os dados através do Kafka UI em http://localhost:8080 e consultar os dados armazenados no PostgreSQL.
