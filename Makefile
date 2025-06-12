# Makefile para facilitar comandos do projeto IoT Kafka Monitoring

# Sobe todos os containers em modo detach (background)
up:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml up --build -d

# Para e remove todos os containers, mas mantém os volumes (dados do banco)
down:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml down

# Para, remove containers e volumes (apaga dados do banco)
reset:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml down -v

# Mostra os logs de todos os serviços
logs:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f

# Mostra os logs do consumer
logs-consumer:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f consumer

# Mostra os logs do producer
logs-producer:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f producer

# Entra no shell do banco de dados PostgreSQL
psql:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata

# Lista as tabelas do banco de dados
list-tables:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "\dt"

# Executa um comando SQL no banco (exemplo: make sql CMD="SELECT * FROM sensors;")
sql:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "$(CMD)"

# Reinicia apenas o consumer
restart-consumer:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml restart consumer

# Reinicia apenas o producer
restart-producer:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml restart producer

# Mostra o status dos containers
status:
    docker-compose -f iot-kafka-monitoring/docker-compose.yml ps

# Limpa imagens não utilizadas (opcional)
prune:
    docker system prune -f

.PHONY: up down reset logs logs-consumer logs-producer psql list-tables sql restart-consumer restart-producer status prune