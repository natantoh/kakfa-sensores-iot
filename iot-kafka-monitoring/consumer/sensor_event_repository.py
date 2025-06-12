from psycopg2 import connect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SensorEventRepository:
    """
    Responsável por toda a interação com o banco de dados de eventos de sensores,
    incluindo criação de schema e inserção de dados.
    """
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None

    def connect(self):
        """
        Estabelece conexão com o banco de dados e garante que o schema está criado.
        """
        self.conn = connect(**self.db_config)
        self.create_database_schema()

    def create_database_schema(self):
        """
        Cria a tabela e índices necessários para armazenar eventos de sensores, caso não existam.
        """
        with self.conn.cursor() as cursor:
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
            self.conn.commit()
        logger.info("Schema do banco de dados verificado/criado")

    def insert_sensor_event(self, sensor_data):
        """
        Insere um evento de sensor no banco de dados, ignorando duplicatas pelo unique_reading_id.
        """
        with self.conn.cursor() as cursor:
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
            self.conn.commit()

    def close(self):
        """
        Fecha a conexão com o banco de dados, se estiver aberta.
        """
        if self.conn:
            self.conn.close()