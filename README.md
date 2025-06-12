# kakfa-sensores-iot
# IoT Sensor Monitoring with Kafka and PostgreSQL
## Estrutura do Projeto

```
kakfa-sensores-iot/
│
├── iot-kafka-monitoring/
│   ├── docker-compose.yml
│   ├── requirements.txt
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── consumer/
│   │   ├── consumer.py
│   │   └── Dockerfile
│   │
│   ├── db/
│   │
│   ├── producer/
│   │   ├── producer.py
│   │   └── Dockerfile
│   │
│   └── utils/
│       └── fake_data_sensor.py
│
├── .gitignore
├── LICENSE
└── README.md
```
## Descrição

- **docker-compose.yml**: Orquestra todos os serviços (Kafka, Zookeeper, PostgreSQL, Producer, Consumer).
- **requirements.txt**: Dependências Python compartilhadas por Producer e Consumer.
- **config/**: Configurações auxiliares do projeto.
- **consumer/**: Código e Dockerfile do consumidor Kafka (salva dados no PostgreSQL).
- **producer/**: Código e Dockerfile do produtor Kafka (gera dados fake de sensores).
- **db/**: (Opcional) Scripts ou arquivos relacionados ao banco de dados.
- **utils/**: Utilitários, como gerador de dados fake para sensores.
- **.gitignore**: Arquivos e pastas ignorados pelo Git.
- **LICENSE**: Licença do projeto.
- **README.md**: Documentação do projeto.

## Arquitetura

1. **Producer**: Gera dados falsos do sensor e envia para o tópico Kafka. 
2. **Kafka**: Message broker for real-time data streaming
3. **Consumer**: Processes messages from Kafka and stores in PostgreSQL
4. **PostgreSQL**: Database for persistent storage of sensor data
5.  **Redis**: O redis é usado em paralelo ao banco, após o processamento, para marcar leituras como já processadas e armazenar o último valor de cada sensor. PostgreSQL continua sendo o sistema de armazenamento histórico oficial.

      [Producer] --> [Kafka Topic] --> [Consumer] --> [Redis (cache + deduplicação)] + [PostgreSQL (persistência)]

                        +-------------------+
                        |   Sensor (fake)   |
                        |   Producer.py     |
                        |-------------------|
                        | Faker gera dados  |
                        | UUID, tipo, valor |
                        +---------+---------+
                                  |
                         Kafka Producer envia JSON
                                  |
                                  v
                         +--------+--------+
                         |     Apache Kafka |
                         |   (Broker + Topic)  |
                         | Topic: iot-sensor-data |
                         +--------+--------+
                                  |
                +----------------+------------------+
                |                                   |
                v                                   v
      +---------+---------+              (outros consumers, se quiser)
      |     Consumer.py    |
      |--------------------|
      | KafkaConsumer escuta |
      | o tópico Kafka       |
      +---------+-----------+
                |
                | Verifica se o `unique_reading_id`
                | já foi processado em Redis:
                |  → Se sim: ignora (deduplicação)
                |  → Se não:
                |      - processa
                |      - salva no banco
                |      - cacheia último valor
                v
        +--------------------+
        |       Redis        |
        |--------------------|
        | reading:<uuid>     |  ← deduplicação com TTL
        | last:<sensor_id>   |  ← cache do último valor
        +--------------------+

                |
                v
        +------------------------+
        |     PostgreSQL         |
        |------------------------|
        | Table: sensors         |
        | Table: sensor_readings |
        +------------------------+
   
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

ADICIONAR:
- REDIS
- MONITORAMENTO
- QT DE MSG PROCESSADA
- TRATAMENTO DE MSG

## Realizando a configuração local - Para teste sem o docker
- Baixar e instalar o PostgreSQL https://www.postgresql.org/download/windows/
- Configurar com a porta 5432 ( Padrão )
- Ir na pesquisa do windows digitar psql
  No terminal **psql**, quando ele pedir as informações, preencher:

  - **Server/host:**   localhost
  - **Database:**  iotdata
  - **Port:**  5432
  - **Username:**  iotuser
  - **Password:**  iotpassword

Esses dados são os mesmos que você configuramos no arquivo consumer.py. Depois de preencher, você estará conectado ao seu banco PostgreSQL local e poderá executar comandos SQL normalmente!

## DockerFile de consumer e producer
Foi mantido uma imagem separada para o consumer e uma para o producer, visando os seguintes benefícios futuros:

- **Responsabilidade única:** Cada serviço tem sua função bem definida e pode evoluir de forma independente.
- **Escalabilidade:** Podemos escalar o producer ou o consumer separadamente, conforme a demanda.
- **Deploy independente:** Atualizações em um serviço não afetam o outro.
- **Boas práticas DevOps:** Facilita CI/CD, troubleshooting e manutenção.
- **Flexibilidade:** Permite usar dependências, variáveis de ambiente e configurações específicas para cada serviço. 

