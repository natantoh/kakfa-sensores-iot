# kakfa-sensores-iot
# IoT Sensor Monitoring with Kafka and PostgreSQL

This project demonstrates a system for monitoring IoT sensors using Kafka as a message broker and PostgreSQL for data storage.

## Arquitetura

1. **Producer**: Gera dados falsos do sensor e envia para o tópico Kafka
2. **Kafka**: Message broker for real-time data streaming
3. **Consumer**: Processes messages from Kafka and stores in PostgreSQL
4. **PostgreSQL**: Database for persistent storage of sensor data

      [Producer] --> [Tópico Kafka] --> [Consumer] --> [Banco de Dados]

## Setup

1. Install Docker and Docker Compose
2. Clone this repository
3. Create `.env` file if needed (see `.env.example`)

## Running the System

1. Iniciar os containers:
   ```bash
   docker-compose up -d
   ```

2. Create database tables (run once):
   ```bash
    python -c "from db.models import create_tables; create_tables()"
   ```
3. Rodar o producer:
 ```bash
    python producer/producer.py
 ```
4. Rodar o onsumer:
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
