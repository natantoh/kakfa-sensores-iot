import os

class BaseSettings:
    # Kafka
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
    TOPIC_NAME = os.getenv('TOPIC_NAME', 'iot-sensor-data')
    GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'iot-consumer-group')

    # PostgreSQL
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'iotdata')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'iotuser')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'iotpassword')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

    DB_CONFIG = {
        'dbname': POSTGRES_DB,
        'user': POSTGRES_USER,
        'password': POSTGRES_PASSWORD,
        'host': POSTGRES_HOST,
        'port': POSTGRES_PORT
    }

    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_TTL_SECONDS = int(os.getenv('REDIS_TTL_SECONDS', '3600'))  # Adicionado para centralizar o TTL

class DevSettings(BaseSettings):
    pass

class ProdSettings(BaseSettings):
    # Exemplo: sobrescrever valores para produção
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'prod-kafka:9092')
    # Outros overrides...

# Escolha automática do ambiente
env = os.getenv('ENV', 'dev').lower()
if env == 'prod':
    settings = ProdSettings()
else:
    settings = DevSettings()