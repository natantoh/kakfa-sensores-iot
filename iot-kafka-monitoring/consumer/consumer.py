from json import loads
from kafka import KafkaConsumer
from psycopg2 import connect
from datetime import datetime
import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import redis_helper

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = 'iot-sensor-data'
GROUP_ID = 'iot-consumer-group'

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'iotdata'),
    'user': os.getenv('POSTGRES_USER', 'iotuser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'iotpassword'),
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': '5432'
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_schema(conn):
    """Cria a tabela única para eventos de sensores"""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_events (
                id SERIAL PRIMARY KEY,
                unique_reading_id VARCHAR(36) NOT NULL UNIQUE,
                sensor_id VARCHAR(36) NOT NULL,
                sensor_type VARCHAR(20) NOT NULL,
                latitude DECIMAL(10, 6),
                longitude DECIMAL(10, 6),
                timestamp TIMESTAMP NOT NULL,
                value DECIMAL(10, 2),
                unit VARCHAR(10),
                status VARCHAR(10),
                battery_level INTEGER
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_events_sensor_id ON sensor_events(sensor_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_events_timestamp ON sensor_events(timestamp)")
        conn.commit()
    logger.info("Schema do banco de dados verificado/criado")

def insert_sensor_event(conn, sensor_data):
    """Insere um evento completo do sensor na tabela sensor_events"""
    with conn.cursor() as cursor:
        timestamp = datetime.fromisoformat(sensor_data['timestamp'])
        cursor.execute("""
            INSERT INTO sensor_events (
                unique_reading_id, sensor_id, sensor_type, latitude, longitude,
                timestamp, value, unit, status, battery_level
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (unique_reading_id) DO NOTHING
        """, (
            sensor_data['unique_reading_id'],
            sensor_data['sensor_id'],
            sensor_data['sensor_type'],
            sensor_data['location']['latitude'],
            sensor_data['location']['longitude'],
            timestamp,
            sensor_data['value'],
            sensor_data['unit'],
            sensor_data['status'],
            sensor_data['battery_level']
        ))
        conn.commit()

def create_kafka_consumer():
    """Cria e retorna um consumidor Kafka"""
    return KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=GROUP_ID,
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )

def main():
    try:
        conn = connect(**DB_CONFIG)
        create_database_schema(conn)
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return

    try:
        consumer = create_kafka_consumer()
    except Exception as e:
        logger.error(f"Erro ao criar consumidor Kafka: {e}")
        conn.close()
        return

    logger.info("Iniciando consumo de mensagens...")

    try:
        for message in consumer:
            sensor_data = message.value
            reading_id = sensor_data.get("unique_reading_id")
            sensor_id = sensor_data.get("sensor_id")

            if not reading_id or not sensor_id:
                logger.warning("Mensagem inválida, ignorando.")
                continue

            if redis_helper.is_duplicate(reading_id):
                logger.info(f"Mensagem duplicada ignorada: {reading_id}")
                continue

            logger.info(f"Mensagem recebida: {sensor_id} - {sensor_data['sensor_type']}")

            try:
                insert_sensor_event(conn, sensor_data)
                redis_helper.mark_as_processed(reading_id)
                redis_helper.cache_last_value(sensor_id, sensor_data)
                logger.info("Dados processados e armazenados com sucesso")
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}")
                conn.rollback()

    except KeyboardInterrupt:
        logger.info("Parando o consumer...")
    finally:
        consumer.close()
        conn.close()

if __name__ == "__main__":
    main()