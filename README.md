# kakfa-sensores-iot
# Monitoramento de dispositivo IOT com Kafa, PostgreSQL e Redis
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
3. **Consumer**: Consome as mensagens do tópico Kafka, processa cada evento, faz deduplicação e persistência.
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
   
## Rodando o sistema
  Para rodar o sistema no windows, é necessário ter o docker instalado ( No meu caso instalei o docker desktop, onde pode-se acompanhar visualmente os containers que sobem entre outros gerenciamentos do docker )

1. Iniciar todos os containers ( Na pasta raíz do projeto )
   ```bash
   docker-compose -f iot-kafka-monitoring/docker-compose.yml up --build
   ```
  O comando acima irá subir todos os containers e começar a rodar. 

2. Lista a tabela criada:
   ```bash
    docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "\dt"
   ```

3. Faz select na tabela:
   ```bash
    docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "SELECT * FROM sensor_events;"
   ```

4. Check Duplicatas na tabela:
   ```bash
    docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "SELECT unique_reading_id, COUNT(*) FROM sensor_events GROUP BY unique_reading_id HAVING COUNT(*) > 1;"
   ```
Neste projeto, tem diversos comandos no makefile que podem ser usados no terminal para análise como um todo. Os comandos mais usados foram disponibilizados no makefile do projeto. 

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

## TESTES
   Os testes foram feito utilizando o framework pytest, para correta execução dos teste, recomenda-se a instalação dos requirements.txt do projeto e test_requirements.txt de teste.

Para este teste, é necessário subir o container do redis, para isso, pode-se usar no terminal: docker-compose -f iot-kafka-monitoring/docker-compose.yml up redis
test_redis_helper
```bash
   pytest -vv iot-kafka-monitoring/tests/test_redis_helper.py
```

test_sensor_event_processor
```bash
   pytest -vv iot-kafka-monitoring/tests/test_sensor_event_processor.py
```

test_sensor_event_repository
```bash
   pytest -vv iot-kafka-monitoring/tests/test_sensor_event_repository.py
```