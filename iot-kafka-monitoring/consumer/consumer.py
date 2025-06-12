from json import loads
from kafka import KafkaConsumer
from psycopg2 import connect, extras
from datetime import datetime
import logging
import os

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = 'iot-sensor-data'
GROUP_ID = 'iot-consumer-group'

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'iotdata'),
    'user': os.getenv('POSTGRES_USER', 'iotuser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'iotpassword'),
    'host': os.getenv('POSTGRES_HOST', 'postgres'),  # <- deve ser 'postgres'
    'port': '5432'
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_schema(conn):
    """Cria as tabelas necessárias no banco de dados"""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensors (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(36) NOT NULL,
                sensor_type VARCHAR(20) NOT NULL,
                latitude DECIMAL(10, 6),
                longitude DECIMAL(10, 6),
                status VARCHAR(10),
                battery_level INTEGER,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                UNIQUE(sensor_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(36) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                value DECIMAL(10, 2),
                unit VARCHAR(10),
                FOREIGN KEY (sensor_id) REFERENCES sensors (sensor_id)
            )
        """)
        
        # Índices para melhorar performance de consultas
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_id ON sensor_readings(sensor_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp)")
        
        conn.commit()
    logger.info("Schema do banco de dados verificado/criado")

def update_or_insert_sensor(conn, sensor_data):
    """Atualiza ou insere informações do sensor na tabela sensors"""
    with conn.cursor() as cursor:
        timestamp = datetime.fromisoformat(sensor_data['timestamp'])
        
        cursor.execute("""
            INSERT INTO sensors (sensor_id, sensor_type, latitude, longitude, status, battery_level, first_seen, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sensor_id) DO UPDATE SET
                status = EXCLUDED.status,
                battery_level = EXCLUDED.battery_level,
                last_seen = EXCLUDED.last_seen
            RETURNING id
        """, (
            sensor_data['sensor_id'],
            sensor_data['sensor_type'],
            sensor_data['location']['latitude'],
            sensor_data['location']['longitude'],
            sensor_data['status'],
            sensor_data['battery_level'],
            timestamp,
            timestamp
        ))
        
        conn.commit()

def insert_sensor_reading(conn, sensor_data):
    """Insere uma nova leitura do sensor na tabela sensor_readings"""
    with conn.cursor() as cursor:
        timestamp = datetime.fromisoformat(sensor_data['timestamp'])
        
        cursor.execute("""
            INSERT INTO sensor_readings (sensor_id, timestamp, value, unit)
            VALUES (%s, %s, %s, %s)
        """, (
            sensor_data['sensor_id'],
            timestamp,
            sensor_data['value'],
            sensor_data['unit']
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
    # Conecta ao banco de dados
    try:
        conn = connect(**DB_CONFIG)
        create_database_schema(conn)
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return
    
    # Cria o consumidor Kafka
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
            logger.info(f"Mensagem recebida: {sensor_data['sensor_id']} - {sensor_data['sensor_type']}")
            
            try:
                # Atualiza/insere informações do sensor
                update_or_insert_sensor(conn, sensor_data)
                
                # Insere a leitura do sensor
                insert_sensor_reading(conn, sensor_data)
                
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