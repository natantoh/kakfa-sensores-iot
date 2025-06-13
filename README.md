# kakfa-sensores-iot
# IoT Sensor Monitoring with Kafka and PostgreSQL
## Estrutura do Projeto

```
.
├── .gitignore
├── LICENSE
├── Makefile
├── README.md
└── iot-kafka-monitoring/
    ├── docker-compose.yml
    ├── requirements.txt
    ├── test_requirements.txt
    ├── config/
    │   └── settings.py
    ├── consumer/
    │   ├── consumer.py
    │   ├── Dockerfile
    │   ├── kafka_consumer_manager.py
    │   ├── sensor_event_processor.py
    │   └── sensor_event_repository.py
    ├── producer/
    │   ├── Dockerfile
    │   └── producer.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_redis_helper.py
    │   ├── test_sensor_event_processor.py
    │   └── test_sensor_event_repository.py
    └── utils/
        ├── fake_data_sensor.py
        └── redis_helper.py
```

### Descrição das Pastas e Arquivos

- **.gitignore**: Arquivos e pastas a serem ignorados pelo Git.
- **LICENSE**: Licença do projeto.
- **Makefile**: Atalhos para comandos comuns do projeto (subir containers, rodar testes, etc).
- **README.md**: Documentação principal do projeto.

#### iot-kafka-monitoring/
- **docker-compose.yml**: Orquestra todos os serviços (Kafka, Zookeeper, PostgreSQL, Redis, Producer, Consumer).
- **requirements.txt**: Dependências Python do projeto.
- **test_requirements.txt**: Dependências para rodar os testes automatizados.

##### config/
- **settings.py**: Centraliza as configurações do projeto (Kafka, PostgreSQL, Redis, etc).

##### consumer/
- **consumer.py**: Script principal do consumidor Kafka (processa e armazena eventos).
- **Dockerfile**: Dockerfile para buildar o container do consumer.
- **kafka_consumer_manager.py**: Gerencia a conexão e consumo de mensagens do Kafka.
- **sensor_event_processor.py**: Lógica de processamento dos eventos (deduplicação, persistência, cache).
- **sensor_event_repository.py**: Interação com o banco de dados PostgreSQL.

##### producer/
- **producer.py**: Script principal do produtor Kafka (gera e envia dados fake de sensores).
- **Dockerfile**: Dockerfile para buildar o container do producer.

##### tests/
- **__init__.py**: Torna a pasta um pacote Python.
- **test_redis_helper.py**: Testes para utilitários de Redis.
- **test_sensor_event_processor.py**: Testes para o processamento de eventos do sensor.
- **test_sensor_event_repository.py**: Testes para o repositório de eventos do sensor.

##### utils/
- **fake_data_sensor.py**: Geração de dados fake de sensores IoT.
- **redis_helper.py**: Utilitário para operações de cache e deduplicação no Redis.


## Arquitetura

1. **Producer**: Gera dados falsos do sensor e envia para o tópico Kafka. 
2. **Kafka**: Recebe as mensagens do producer e as disponibiliza imediatamente para consumo contínuo (streaming), permitindo processamento quase em tempo real pelo consumer.
3. **Consumer**: consome as mensagens do tópico Kafka, processa cada evento, faz deduplicação e persistência.
4.  **Redis**: É usado em paralelo ao banco, após o processamento, para marcar leituras como já processadas e armazenar o último valor de cada sensor. PostgreSQL continua sendo o sistema de armazenamento histórico oficial.
5. **PostgreSQL**: Armazena historicamente todos os eventos de sensores processados.

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
                         +--------+---------------+
                         |     Apache Kafka       |
                         |   (Broker + Topic)     |
                         | Topic: iot-sensor-data |
                         +--------+---------------+
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
        | Table: sensor_events   |
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
- TESTE COMO PRIORIDADE

## DockerFile de consumer e producer
Foi mantido uma imagem separada para o consumer e uma para o producer, visando os seguintes benefícios futuros:

- **Responsabilidade única:** Cada serviço tem sua função bem definida e pode evoluir de forma independente.
- **Escalabilidade:** Podemos escalar o producer ou o consumer separadamente, conforme a demanda.
- **Deploy independente:** Atualizações em um serviço não afetam o outro.
- **Boas práticas DevOps:** Facilita CI/CD, troubleshooting e manutenção.
- **Flexibilidade:** Permite usar dependências, variáveis de ambiente e configurações específicas para cada serviço. 

## Makefile
No projeto, utilizamos o makefile para "dar apelidos curtos" para os comandos normalmente usados. Na pasta raíz do projeto, podemos encontrar o arquivo makefile que contém comandos normalmente utilizados neste projeto. Para utilização do makefile, primeiro precisa verificar se o mesmo está instalado, para isso podemos verificar digitando:

 ```bash
   make --version
 ```

Se aparecer a versão, o make já está disponível. Assim pode-se utilizar os comandos make apresentados o makefile do projeto.
Caso não aparecer, precisa ser instalado. Existem várias formas na internet para instalar o makefile, mas, como não é importante para a execução do projeto, essa parte fica a critério do leitor. Podemos copiar diretamente os comandos completos do makefile e jogar no terminal, funcionando da mesma forma como se fosse pelo make.

