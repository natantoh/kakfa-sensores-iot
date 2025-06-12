# Makefile para facilitar comandos do projeto IoT Kafka Monitoring

# Equivalente a ir em iot-kafka-monitoring e docker-compose down -v. Remove containers e volumes (apaga dados do banco)
down-all-reset:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml down -v

# Sobe todos os containers e reconstrói as imagens, mostrando os logs no terminal
up-all:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml up --build

# Sobe todos os containers em modo detach (background)
up:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml up --build -d

# Para e remove todos os containers, mas mantém os volumes (dados do banco)
down:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml down

# Logs individuais dos serviços
log-kafka:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f kafka

# Logs do Zookeeper, que é usado pelo Kafka
log-zookeeper:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f zookeeper

# Logs do banco de dados PostgreSQL, que armazena os dados dos sensores
log-postgres:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f postgres

# Logs do producer, que envia mensagens para o Kafka
log-producer:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f producer

# Logs do consumer, que consome mensagens do Kafka e as insere no banco de dados
log-consumer:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f consumer

# Logs do Redis, que é usado para cache
log-redis:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f redis

# Mostra os logs de todos os serviços
logs:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f

# Mostra os logs do consumer
logs-consumer:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f consumer

# Mostra os logs do producer
logs-producer:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml logs -f producer

# Entra no shell do banco de dados PostgreSQL, no terminal interativo, \dt lista as tabelas, e comandos SQL podem ser executados com final, ex: select * from sensors;
psql:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata

# Lista as tabelas do banco de dados
list-tables:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "\dt"

# Executa um comando SQL no banco (exemplo: make sql CMD="SELECT * FROM sensors;")
sql:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "$(CMD)"

# Executa um select no banco de dados
select_from:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "SELECT * FROM sensor_events;"

# Checa duplicatas no banco de dados, procurando por readings com o mesmo unique_reading_id
check-duplicates:
	docker-compose -f iot-kafka-monitoring/docker-compose.yml exec postgres psql -U iotuser -d iotdata -c "SELECT unique_reading_id, COUNT(*) FROM sensor_events GROUP BY unique_reading_id HAVING COUNT(*) > 1;"

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

.PHONY: up down reset logs logs-consumer logs-producer psql list-tables sql restart-consumer restart-